#!/usr/bin/env python3
"""Reusable browser validation harness for GridFlow map-review workflows.

Runs a baseline review suite against one or more jobs and, optionally, layers
on task-specific checklists. Designed to be invoked after any feature task,
not only the C2E2 popup work that motivated it.

Browser automation uses Selenium WebDriver (Chrome). Selenium Manager
(bundled with Selenium 4.10+) resolves the matching chromedriver
automatically, so no separate driver install is required.

Outputs land under validation_runs/<UTC-timestamp>/:
  - validation_report.md
  - console_log.txt
  - failures.json
  - screenshots/  (only failures, unless --evidence-screenshot is passed)
"""

from __future__ import annotations

import argparse
import contextlib
import dataclasses
import json
import re
import socket
import sys
import threading
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

import yaml
from werkzeug.serving import make_server

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))
PROJECTS_ROOT = REPO_ROOT / "uploads" / "projects"
JOBS_ROOT = REPO_ROOT / "uploads" / "jobs"
VALIDATION_ROOT = REPO_ROOT / "validation_runs"


@dataclasses.dataclass(frozen=True)
class JobTarget:
    requested: str
    label: str
    kind: str
    view_path: str
    data_path: str
    source_path: Path


@dataclasses.dataclass
class CheckResult:
    job: str
    check_id: str
    description: str
    status: str
    message: str = ""
    screenshot: str | None = None


# ---------------------------------------------------------------------------
# Job target resolution
# ---------------------------------------------------------------------------


def _slug(value: str) -> str:
    return re.sub(r"[^A-Za-z0-9_.-]+", "_", value).strip("_") or "job"


def _read_json(path: Path) -> dict[str, Any]:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}


def _project_file_target(project_id: str, file_id: str, requested: str) -> JobTarget:
    file_dir = PROJECTS_ROOT / project_id / "files" / file_id
    if not file_dir.exists():
        raise ValueError(f"Project file not found: {project_id}/{file_id}")
    label = f"{project_id}/{file_id}"
    return JobTarget(
        requested=requested,
        label=label,
        kind="project_file",
        view_path=f"/map/view/project/{project_id}/{file_id}",
        data_path=f"/map/data/project/{project_id}/{file_id}",
        source_path=file_dir,
    )


def _legacy_job_target(job_id: str, requested: str) -> JobTarget:
    job_dir = JOBS_ROOT / job_id
    if not job_dir.exists():
        raise ValueError(f"Legacy job not found: {job_id}")
    return JobTarget(
        requested=requested,
        label=job_id,
        kind="legacy_job",
        view_path=f"/map/view/{job_id}",
        data_path=f"/map/data/{job_id}",
        source_path=job_dir,
    )


def _first_file_for_project(project_id: str, requested: str) -> JobTarget:
    project_dir = PROJECTS_ROOT / project_id
    files_dir = project_dir / "files"
    if not files_dir.exists():
        raise ValueError(f"Project not found or has no files: {project_id}")
    file_ids = sorted(path.name for path in files_dir.iterdir() if path.is_dir())
    if not file_ids:
        raise ValueError(f"Project has no map files: {project_id}")
    return _project_file_target(project_id, file_ids[0], requested)


def _project_search_text(project_dir: Path) -> str:
    parts: list[str] = []
    project = _read_json(project_dir / "project.json")
    parts.extend(str(project.get(key) or "") for key in ("project_id", "name", "description"))
    for file_entry in project.get("files") or []:
        if isinstance(file_entry, dict):
            parts.append(str(file_entry.get("filename") or ""))
            intake = file_entry.get("intake") or {}
            if isinstance(intake, dict):
                parts.extend(str(value or "") for value in intake.values())
    for meta_path in sorted((project_dir / "files").glob("*/meta.json")):
        meta = _read_json(meta_path)
        parts.extend(str(meta.get(key) or "") for key in ("filename", "job_id"))
        intake = meta.get("intake") or {}
        if isinstance(intake, dict):
            parts.extend(str(value or "") for value in intake.values())
    return "\n".join(parts).lower()


def _search_project_alias(alias: str) -> JobTarget:
    exact_aliases = {
        "gordon": ("P010", "F001"),
        "bellsprings": ("P008", "F001"),
    }
    if alias.lower() in exact_aliases:
        project_id, file_id = exact_aliases[alias.lower()]
        if (PROJECTS_ROOT / project_id / "files" / file_id).exists():
            return _project_file_target(project_id, file_id, alias)

    matches: list[Path] = []
    needle = alias.lower()
    for project_dir in sorted(PROJECTS_ROOT.glob("P*")):
        if project_dir.is_dir() and needle in _project_search_text(project_dir):
            matches.append(project_dir)
    if not matches:
        raise ValueError(f"No project/job alias matched: {alias}")

    return _first_file_for_project(matches[-1].name, alias)


def resolve_job_target(value: str) -> JobTarget:
    value = value.strip()
    if not value:
        raise ValueError("Empty job argument")
    if "/" in value:
        project_id, file_id = value.split("/", 1)
        return _project_file_target(project_id, file_id, value)
    if re.fullmatch(r"P\d{3}", value, flags=re.IGNORECASE):
        return _first_file_for_project(value.upper(), value)
    if re.fullmatch(r"J[\w-]+", value, flags=re.IGNORECASE):
        return _legacy_job_target(value.upper(), value)
    return _search_project_alias(value)


# ---------------------------------------------------------------------------
# Checklist loading
# ---------------------------------------------------------------------------


def load_simple_yaml(path: Path) -> dict[str, Any]:
    """Load a checklist YAML file via PyYAML (kept as a named helper for tests)."""

    with path.open("r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle) or {}
    if not isinstance(data, dict):
        raise ValueError(f"Checklist root must be a mapping: {path}")
    return data


def load_checklist(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        raise ValueError(f"Checklist not found: {path}")
    if path.suffix.lower() == ".json":
        payload = json.loads(path.read_text(encoding="utf-8"))
    else:
        payload = load_simple_yaml(path)
    checks = payload.get("checks")
    if not isinstance(checks, list):
        raise ValueError(f"Checklist must contain a checks list: {path}")
    for check in checks:
        if not isinstance(check, dict) or not check.get("id") or not check.get("type"):
            raise ValueError(f"Each checklist item needs id and type: {path}")
    return checks


# ---------------------------------------------------------------------------
# Local Flask server (so the harness is self-contained)
# ---------------------------------------------------------------------------


class FlaskServerThread(threading.Thread):
    def __init__(self, host: str, port: int) -> None:
        super().__init__(daemon=True)
        from app import create_app

        self.server = make_server(host, port, create_app(), threaded=True)

    def run(self) -> None:
        self.server.serve_forever()

    def shutdown(self) -> None:
        self.server.shutdown()


def _free_port() -> int:
    with contextlib.closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as sock:
        sock.bind(("127.0.0.1", 0))
        return int(sock.getsockname()[1])


def _start_server() -> tuple[str, FlaskServerThread]:
    port = _free_port()
    server = FlaskServerThread("127.0.0.1", port)
    server.start()
    return f"http://127.0.0.1:{port}", server


# ---------------------------------------------------------------------------
# Selenium runner
# ---------------------------------------------------------------------------


def _eval_wrap(body: str) -> str:
    """Wrap an arrow-style JS body for Selenium's execute_script."""
    return f"return (() => {{ {body} }})();"


def _xpath_literal(value: str) -> str:
    if "'" not in value:
        return f"'{value}'"
    if '"' not in value:
        return f'"{value}"'
    parts = value.split("'")
    pieces: list[str] = []
    for index, part in enumerate(parts):
        if part:
            pieces.append(f"'{part}'")
        if index < len(parts) - 1:
            pieces.append('"\'"')
    return "concat(" + ", ".join(pieces) + ")"


class ManualReviewRunner:
    def __init__(
        self,
        *,
        base_url: str,
        run_dir: Path,
        evidence_screenshot: bool,
        overview_screenshot: bool,
        timeout_ms: int,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.run_dir = run_dir
        self.screenshots_dir = run_dir / "screenshots"
        self.evidence_screenshot = evidence_screenshot
        self.overview_screenshot = overview_screenshot
        self.timeout_ms = timeout_ms
        self.timeout_s = max(1, int(timeout_ms / 1000))
        self.results: list[CheckResult] = []
        self.console_entries: list[str] = []
        self.console_errors_by_job: dict[str, list[str]] = {}

    # -- console -----------------------------------------------------------

    # Browser-log noise that is not a real app failure. The favicon 404 is
    # emitted by Chrome for any site without a favicon and would otherwise
    # mask the genuine JS errors we care about.
    _CONSOLE_NOISE = ("/favicon.ico - Failed to load resource",)

    def _drain_console(self, driver: Any, job: JobTarget) -> None:
        try:
            entries = driver.get_log("browser")
        except Exception:
            entries = []
        for entry in entries:
            level = str(entry.get("level") or "INFO")
            message = str(entry.get("message") or "").replace("\n", " ")
            line = f"[{job.label}] {level}: {message}"
            self.console_entries.append(line)
            if level in {"SEVERE", "ERROR"} and not any(
                token in message for token in self._CONSOLE_NOISE
            ):
                self.console_errors_by_job.setdefault(job.label, []).append(line)

    # -- screenshots -------------------------------------------------------

    def _screenshot(self, driver: Any, job: JobTarget, check_id: str) -> str:
        self.screenshots_dir.mkdir(parents=True, exist_ok=True)
        path = self.screenshots_dir / f"{_slug(job.label)}__{_slug(check_id)}.png"
        try:
            driver.save_screenshot(str(path))
        except Exception:
            return ""
        return str(path.relative_to(self.run_dir))

    # -- recording ---------------------------------------------------------

    def _record(
        self,
        driver: Any,
        job: JobTarget,
        check_id: str,
        description: str,
        fn: Callable[[], str | None],
    ) -> None:
        try:
            message = fn() or ""
            self._drain_console(driver, job)
            screenshot = (
                self._screenshot(driver, job, check_id) if self.evidence_screenshot else None
            )
            self.results.append(
                CheckResult(job.label, check_id, description, "pass", message, screenshot)
            )
        except Exception as exc:  # noqa: BLE001 - keep running across failures
            self._drain_console(driver, job)
            screenshot = self._screenshot(driver, job, check_id)
            self.results.append(
                CheckResult(job.label, check_id, description, "fail", str(exc), screenshot)
            )

    # -- waits / helpers ---------------------------------------------------

    def _wait_visible(self, driver: Any, selector: str) -> None:
        from selenium.webdriver.common.by import By
        from selenium.webdriver.support import expected_conditions as EC
        from selenium.webdriver.support.ui import WebDriverWait

        WebDriverWait(driver, self.timeout_s).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, selector))
        )

    def _wait_text_visible(self, driver: Any, text: str) -> None:
        from selenium.webdriver.common.by import By
        from selenium.webdriver.support import expected_conditions as EC
        from selenium.webdriver.support.ui import WebDriverWait

        xpath = (
            f"//*[not(self::script) and not(self::style) "
            f"and contains(normalize-space(.), {_xpath_literal(text)})]"
        )
        WebDriverWait(driver, self.timeout_s).until(
            EC.visibility_of_element_located((By.XPATH, xpath))
        )

    def _wait_for_js(self, driver: Any, body: str) -> None:
        from selenium.webdriver.support.ui import WebDriverWait

        script = _eval_wrap(body)
        WebDriverWait(driver, self.timeout_s).until(lambda d: bool(d.execute_script(script)))

    def _wait_map_ready(self, driver: Any) -> None:
        self._wait_visible(driver, "#map")
        self._wait_for_js(
            driver,
            """
            const viewer = window.gridflowMapViewer;
            const rulepack = document.querySelector('#rulepack-badge')?.textContent || '';
            return Boolean(
              viewer
              && viewer.map
              && viewer._mapMeta
              && rulepack
              && rulepack !== 'Loading…'
              && (
                (viewer.featureData || []).length > 0
                || (viewer._spanLineRefs || []).length > 0
                || Number(viewer._mapMeta.pole_count || 0) === 0
              )
            );
            """,
        )

    def _open_first_popup(self, driver: Any) -> str:
        return driver.execute_script(
            _eval_wrap(
                """
                const viewer = window.gridflowMapViewer;
                if (!viewer) throw new Error('MapViewer hook unavailable');
                const feature = (viewer.featureData || []).find((item) => item.marker);
                if (!feature) throw new Error('No marker feature available for popup check');
                feature.marker.openPopup();
                const el = document.querySelector('.leaflet-popup-content');
                if (!el) throw new Error('Popup did not open');
                return el.innerText || el.textContent || '';
                """
            )
        )

    def _open_first_c2e2_support_popup(self, driver: Any) -> str:
        return driver.execute_script(
            _eval_wrap(
                """
                const viewer = window.gridflowMapViewer;
                if (!viewer) throw new Error('MapViewer hook unavailable');
                const feature = (viewer.featureData || []).find((item) => {
                  const kind = viewer.popupAssetKind(item.props || {});
                  return ['existing', 'angle', 'proposed'].includes(kind) && item.marker;
                });
                if (!feature) throw new Error('No C2E2 support marker available for popup check');
                feature.marker.openPopup();
                const popup = feature.marker.getPopup && feature.marker.getPopup();
                const content = popup && popup.getContent ? popup.getContent() : '';
                if (!content) throw new Error('C2E2 support popup content unavailable');
                return String(content);
                """
            )
        )

    # -- baseline checks ---------------------------------------------------

    def _baseline_checks(self, driver: Any, job: JobTarget) -> None:
        url = f"{self.base_url}{job.view_path}"

        def app_loads() -> str:
            driver.get(url)
            self._wait_visible(driver, "#map")
            return "map shell visible"

        self._record(driver, job, "app_loads", "App loads", app_loads)

        def target_map_loads() -> str:
            self._wait_map_ready(driver)
            return f"{job.data_path} ready"

        self._record(driver, job, "target_map_loads", "Target job/map loads", target_map_loads)

        self._record(
            driver,
            job,
            "review_navigation_works",
            "Review navigation works",
            lambda: driver.execute_script(
                _eval_wrap(
                    """
                    const viewer = window.gridflowMapViewer;
                    viewer.buildReviewNavigationTargets();
                    const groups = ['blockers', 'review', 'gaps', 'awareness'];
                    const group = groups.find(
                      (name) => (viewer._reviewNavigationTargets[name] || []).length > 0,
                    );
                    if (!group) throw new Error('No review navigation targets available');
                    viewer.selectReviewNavigationGroup(group);
                    if (viewer._activeReviewTargetGroup !== group) {
                      throw new Error('Review group did not activate');
                    }
                    return `${group} selected`;
                    """
                )
            ),
        )

        self._record(
            driver,
            job,
            "next_previous_works",
            "Next / Previous works",
            lambda: driver.execute_script(
                _eval_wrap(
                    """
                    const viewer = window.gridflowMapViewer;
                    if (!viewer._activeReviewTargetGroup) {
                      viewer.buildReviewNavigationTargets();
                      const group = ['blockers', 'review', 'gaps', 'awareness']
                        .find((name) => (viewer._reviewNavigationTargets[name] || []).length > 0);
                      if (!group) throw new Error('No active review target group');
                      viewer.selectReviewNavigationGroup(group);
                    }
                    viewer.focusNextReviewTarget();
                    const afterNext = viewer._activeReviewTargetIndex;
                    viewer.focusPreviousReviewTarget();
                    if (viewer._activeReviewTargetIndex < 0) {
                      throw new Error('Previous left no active target');
                    }
                    return [
                      `next index ${afterNext}`,
                      `previous index ${viewer._activeReviewTargetIndex}`,
                    ].join(', ');
                    """
                )
            ),
        )

        self._record(
            driver,
            job,
            "route_highlight_works",
            "Route highlight works",
            lambda: driver.execute_script(
                _eval_wrap(
                    """
                    const viewer = window.gridflowMapViewer;
                    const ref = (viewer._spanLineRefs || [])[0];
                    if (!ref) throw new Error('No route span available');
                    viewer.clearSpanRouteHighlight();
                    viewer.handleDirectSpanClick(ref);
                    const highlighted = document.querySelectorAll('.gf-route-highlight').length;
                    if (viewer._activeRouteGroupIndex == null || highlighted < 1) {
                      throw new Error('Route highlight did not activate');
                    }
                    return `${highlighted} highlighted span element(s)`;
                    """
                )
            ),
        )

        self._record(
            driver,
            job,
            "release_map_works",
            "Release Map works",
            lambda: driver.execute_script(
                _eval_wrap(
                    """
                    const viewer = window.gridflowMapViewer;
                    viewer.buildReviewNavigationTargets();
                    const group = ['blockers', 'review', 'gaps', 'awareness']
                      .find((name) => (viewer._reviewNavigationTargets[name] || []).length > 0);
                    if (!group) throw new Error('No review target available to release');
                    viewer.selectReviewNavigationGroup(group);
                    viewer.releaseReviewNavigationMap();
                    if (viewer._reviewNavigationLocked !== false) {
                      throw new Error('Map was not released');
                    }
                    const note = document.querySelector('#review-map-unlocked-note');
                    if (!note || note.style.display === 'none') {
                      throw new Error('Release note not visible');
                    }
                    return 'map released';
                    """
                )
            ),
        )

        self._record(
            driver,
            job,
            "planner_awareness_toggle_works",
            "Planner Awareness toggle works",
            lambda: driver.execute_script(
                _eval_wrap(
                    """
                    const viewer = window.gridflowMapViewer;
                    const input = document.querySelector('input[data-layer="plannerAwareness"]');
                    if (!input) throw new Error('Planner awareness toggle missing');
                    if (input.disabled) throw new Error('Planner awareness toggle disabled');
                    input.checked = false;
                    input.dispatchEvent(new Event('change', { bubbles: true }));
                    if (viewer.layerState.plannerAwareness !== false) {
                      throw new Error('Toggle off not applied');
                    }
                    input.checked = true;
                    input.dispatchEvent(new Event('change', { bubbles: true }));
                    if (viewer.layerState.plannerAwareness !== true) {
                      throw new Error('Toggle on not applied');
                    }
                    return 'toggle cycled off/on';
                    """
                )
            ),
        )

        self._record(
            driver,
            job,
            "popups_open_without_crashing",
            "Popups open without crashing",
            lambda: (self._open_first_popup(driver) or "")[:120],
        )

        self._record(
            driver,
            job,
            "popup_remains_readable",
            "Popup remains readable",
            lambda: driver.execute_script(
                _eval_wrap(
                    """
                    const el = document.querySelector('.leaflet-popup-content');
                    if (!el) throw new Error('No open popup to inspect');
                    const rect = el.getBoundingClientRect();
                    const text = (el.innerText || '').trim();
                    if (text.length < 20) throw new Error('Popup content is too sparse');
                    if (rect.width > window.innerWidth || rect.height > window.innerHeight) {
                      throw new Error(`Popup exceeds viewport: ${rect.width}x${rect.height}`);
                    }
                    const style = window.getComputedStyle(el);
                    if (style.overflowY !== 'auto' && style.overflowY !== 'scroll') {
                      throw new Error(`Popup overflow is not scrollable: ${style.overflowY}`);
                    }
                    return `popup ${Math.round(rect.width)}x${Math.round(rect.height)}`;
                    """
                )
            ),
        )

        def console_clean() -> str:
            self._drain_console(driver, job)
            errors = self.console_errors_by_job.get(job.label, [])
            if errors:
                raise AssertionError("; ".join(errors[-8:]))
            return "no console errors"

        self._record(driver, job, "console_clean", "Console clean", console_clean)

    # -- checklist checks --------------------------------------------------

    def _run_checklist_check(self, driver: Any, job: JobTarget, check: dict[str, Any]) -> None:
        check_type = str(check["type"])
        check_id = str(check["id"])
        description = str(check.get("description") or check_id)

        def run() -> str | None:
            if check_type == "selector_visible":
                selector = str(check["selector"])
                self._wait_visible(driver, selector)
                return selector
            if check_type == "text_present":
                text = str(check["text"])
                self._wait_text_visible(driver, text)
                return text
            if check_type == "popup_text_contains":
                text = self._open_first_popup(driver) or ""
                missing = [str(item) for item in check.get("contains", []) if str(item) not in text]
                if missing:
                    raise AssertionError(f"Popup missing expected text: {', '.join(missing)}")
                return f"{len(check.get('contains', []))} popup text assertions"
            if check_type == "c2e2_support_popup_text_contains":
                text = self._open_first_c2e2_support_popup(driver) or ""
                missing = [str(item) for item in check.get("contains", []) if str(item) not in text]
                if missing:
                    raise AssertionError(
                        f"C2E2 support popup missing expected text: {', '.join(missing)}"
                    )
                return f"{len(check.get('contains', []))} C2E2 popup text assertions"
            if check_type == "click_selector":
                from selenium.webdriver.common.by import By

                selector = str(check["selector"])
                self._wait_visible(driver, selector)
                driver.find_element(By.CSS_SELECTOR, selector).click()
                if check.get("expect_selector"):
                    self._wait_visible(driver, str(check["expect_selector"]))
                if check.get("expect_text"):
                    self._wait_text_visible(driver, str(check["expect_text"]))
                return selector
            if check_type == "route_highlight_active":
                return driver.execute_script(
                    _eval_wrap(
                        """
                        const viewer = window.gridflowMapViewer;
                        const ref = (viewer._spanLineRefs || [])[0];
                        if (!ref) throw new Error('No route span available');
                        viewer.clearSpanRouteHighlight();
                        viewer.handleDirectSpanClick(ref);
                        if (!document.querySelector('.gf-route-highlight')) {
                          throw new Error('Route highlight class missing');
                        }
                        return 'route highlighted';
                        """
                    )
                )
            if check_type == "review_focus_category_active":
                category = str(check["category"])
                return driver.execute_script(
                    _eval_wrap(
                        f"""
                        const viewer = window.gridflowMapViewer;
                        if (!viewer) throw new Error('MapViewer hook unavailable');
                        if (typeof viewer.activateReviewFocusMode !== 'function') {{
                          throw new Error('Review focus mode is unavailable');
                        }}
                        viewer.activateReviewFocusMode({category!r});
                        const targets = viewer.getFocusTargetsForCategory({category!r});
                        if (!targets.length) {{
                          throw new Error(`No review focus targets for {category}`);
                        }}
                        if (viewer.activeFocusCategory !== {category!r}) {{
                          throw new Error('Review focus category did not activate');
                        }}
                        const focused = document.querySelectorAll('.gf-focus-target').length;
                        if (focused < 1) {{
                          throw new Error('No focused map targets were styled');
                        }}
                        return `${{targets.length}} {category} focus target(s)`;
                        """
                    )
                )
            if check_type == "lifecycle_focus_active":
                mode = str(check.get("mode") or "replacement-pairs")
                return driver.execute_script(
                    _eval_wrap(
                        f"""
                        const viewer = window.gridflowMapViewer;
                        if (!viewer) throw new Error('MapViewer hook unavailable');
                        if (typeof viewer.activateLifecycleFocusMode !== 'function') {{
                          throw new Error('Lifecycle focus mode is unavailable');
                        }}
                        viewer.activateLifecycleFocusMode({mode!r});
                        const targets = viewer.getLifecycleFocusTargets({mode!r});
                        const count = (
                          (targets.features || []).length
                          + (targets.connectors || []).length
                        );
                        if (!count) {{
                          return `no {mode} lifecycle targets in this job`;
                        }}
                        if (viewer.activeLifecycleFocusMode !== {mode!r}) {{
                          throw new Error('Lifecycle focus mode did not activate');
                        }}
                        const focused = document.querySelectorAll(
                          '.gf-lifecycle-pair-highlight',
                        ).length;
                        if (focused < 1) {{
                          throw new Error('No lifecycle map targets were styled');
                        }}
                        return `${{count}} {mode} lifecycle focus target(s)`;
                        """
                    )
                )
            if check_type == "planner_awareness_visible":
                return driver.execute_script(
                    _eval_wrap(
                        """
                        const viewer = window.gridflowMapViewer;
                        if (!(viewer._awarenessMarkerRefs || []).length) {
                          throw new Error('No planner awareness markers available');
                        }
                        return `${viewer._awarenessMarkerRefs.length} awareness marker(s)`;
                        """
                    )
                )
            raise ValueError(f"Unsupported checklist check type: {check_type}")

        self._record(driver, job, check_id, description, run)

    # -- per-job orchestration --------------------------------------------

    def run_job(self, job: JobTarget, checklist_checks: list[dict[str, Any]]) -> None:
        driver = _build_driver()
        try:
            self._baseline_checks(driver, job)
            for check in checklist_checks:
                self._run_checklist_check(driver, job, check)
            if self.overview_screenshot:
                self._screenshot(driver, job, "final_overview")
            self._drain_console(driver, job)
        finally:
            with contextlib.suppress(Exception):
                driver.quit()

    # -- output writers ----------------------------------------------------

    def write_outputs(self, jobs: list[JobTarget], checklist_paths: list[Path]) -> None:
        self.run_dir.mkdir(parents=True, exist_ok=True)
        (self.run_dir / "console_log.txt").write_text(
            "\n".join(self.console_entries) + ("\n" if self.console_entries else ""),
            encoding="utf-8",
        )
        failures = [
            dataclasses.asdict(result) for result in self.results if result.status == "fail"
        ]
        (self.run_dir / "failures.json").write_text(
            json.dumps(failures, indent=2), encoding="utf-8"
        )

        passed = sum(1 for result in self.results if result.status == "pass")
        failed = sum(1 for result in self.results if result.status == "fail")
        lines = [
            "# GridFlow Manual Review Validation Report",
            "",
            f"- Run: `{self.run_dir.name}`",
            f"- Base URL: `{self.base_url}`",
            f"- Jobs: {', '.join(f'`{job.label}`' for job in jobs)}",
            f"- Checklists: {', '.join(f'`{path}`' for path in checklist_paths) or 'none'}",
            f"- Result: {passed} passed, {failed} failed",
            "",
            "| Job | Check | Status | Message | Screenshot |",
            "| --- | --- | --- | --- | --- |",
        ]
        for result in self.results:
            screenshot = f"`{result.screenshot}`" if result.screenshot else ""
            message = result.message.replace("\n", " ")[:240]
            lines.append(
                f"| `{result.job}` | `{result.check_id}` | {result.status.upper()} | "
                f"{message} | {screenshot} |"
            )
        (self.run_dir / "validation_report.md").write_text(
            "\n".join(lines) + "\n", encoding="utf-8"
        )


# ---------------------------------------------------------------------------
# Selenium driver factory
# ---------------------------------------------------------------------------


def _build_driver() -> Any:
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.chrome.service import Service

    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1440,1000")
    # browser-log capture requires the goog:loggingPrefs capability
    options.set_capability("goog:loggingPrefs", {"browser": "ALL"})

    # Selenium Manager (built into selenium>=4.10) auto-resolves chromedriver
    return webdriver.Chrome(service=Service(), options=options)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def _build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--jobs", nargs="+", required=True, help="Project files, projects, legacy jobs, or aliases"
    )
    parser.add_argument(
        "--suite", default="baseline", choices=["baseline"], help="Validation suite to run"
    )
    parser.add_argument(
        "--checklist", action="append", default=[], help="Optional YAML/JSON checklist path"
    )
    parser.add_argument(
        "--base-url", help="Existing GridFlow base URL; otherwise a local server is started"
    )
    parser.add_argument(
        "--evidence-screenshot",
        action="store_true",
        help="Capture screenshots for passed checks too",
    )
    parser.add_argument(
        "--overview-screenshot",
        action="store_true",
        help="Capture one final overview screenshot per job",
    )
    parser.add_argument("--timeout-ms", type=int, default=15_000)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _build_arg_parser().parse_args(argv)
    run_id = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    run_dir = VALIDATION_ROOT / run_id

    try:
        jobs = [resolve_job_target(job) for job in args.jobs]
        checklist_paths = [Path(path) for path in args.checklist]
        checklist_checks = [check for path in checklist_paths for check in load_checklist(path)]
    except Exception as exc:
        print(f"manual_review setup failed: {exc}", file=sys.stderr)
        return 2

    server: FlaskServerThread | None = None
    base_url = args.base_url
    if not base_url:
        base_url, server = _start_server()

    try:
        try:
            from selenium import webdriver  # noqa: F401  (import-time check)
        except ImportError:
            print(
                "Selenium is required for browser validation. Install with:\n"
                "  python3 -m pip install selenium pyyaml",
                file=sys.stderr,
            )
            return 2

        runner = ManualReviewRunner(
            base_url=base_url,
            run_dir=run_dir,
            evidence_screenshot=args.evidence_screenshot,
            overview_screenshot=args.overview_screenshot,
            timeout_ms=args.timeout_ms,
        )
        for job in jobs:
            runner.run_job(job, checklist_checks)
        runner.write_outputs(jobs, checklist_paths)
        failures = [result for result in runner.results if result.status == "fail"]
        print(f"Validation report: {run_dir / 'validation_report.md'}")
        return 1 if failures else 0
    finally:
        if server is not None:
            server.shutdown()


if __name__ == "__main__":
    raise SystemExit(main())
