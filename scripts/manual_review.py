#!/usr/bin/env python3
"""Reusable browser validation harness for GridFlow map-review workflows."""

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

from werkzeug.serving import make_server

REPO_ROOT = Path(__file__).resolve().parents[1]
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

    # Prefer the latest project identifier when several historical validation copies exist.
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


def _parse_scalar(value: str) -> Any:
    value = value.strip()
    if value in {"", "null", "None", "~"}:
        return None
    if value in {"true", "True"}:
        return True
    if value in {"false", "False"}:
        return False
    if (value.startswith('"') and value.endswith('"')) or (
        value.startswith("'") and value.endswith("'")
    ):
        return value[1:-1]
    if re.fullmatch(r"-?\d+", value):
        return int(value)
    return value


def _strip_yaml_comment(raw: str) -> str:
    in_single = False
    in_double = False
    for idx, char in enumerate(raw):
        if char == "'" and not in_double:
            in_single = not in_single
        elif char == '"' and not in_single:
            in_double = not in_double
        elif char == "#" and not in_single and not in_double:
            if idx == 0 or raw[idx - 1].isspace():
                return raw[:idx].rstrip()
    return raw.rstrip()


def load_simple_yaml(path: Path) -> dict[str, Any]:
    """Parse the small checklist YAML subset used by this harness."""

    data: dict[str, Any] = {}
    current_list_name: str | None = None
    current_item: dict[str, Any] | None = None
    current_sublist: str | None = None

    for raw in path.read_text(encoding="utf-8").splitlines():
        line = _strip_yaml_comment(raw)
        if not line.strip():
            continue
        indent = len(line) - len(line.lstrip(" "))
        text = line.strip()

        if indent == 0:
            current_item = None
            current_sublist = None
            if text.endswith(":"):
                key = text[:-1]
                data[key] = []
                current_list_name = key
            else:
                key, _, value = text.partition(":")
                data[key.strip()] = _parse_scalar(value)
                current_list_name = None
            continue

        if indent == 2 and text.startswith("- "):
            if current_list_name is None:
                raise ValueError(f"List item outside a list in {path}: {raw}")
            item_text = text[2:].strip()
            current_item = {}
            current_sublist = None
            data.setdefault(current_list_name, []).append(current_item)
            if item_text:
                key, _, value = item_text.partition(":")
                current_item[key.strip()] = _parse_scalar(value)
            continue

        if indent == 4 and current_item is not None:
            key, _, value = text.partition(":")
            key = key.strip()
            if value.strip():
                current_item[key] = _parse_scalar(value)
                current_sublist = None
            else:
                current_item[key] = []
                current_sublist = key
            continue

        if indent == 6 and text.startswith("- ") and current_item is not None and current_sublist:
            current_item[current_sublist].append(_parse_scalar(text[2:]))
            continue

        raise ValueError(f"Unsupported checklist YAML line in {path}: {raw}")

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
        self.results: list[CheckResult] = []
        self.console_entries: list[str] = []
        self.console_errors_by_job: dict[str, list[str]] = {}

    def _log_console(self, job: JobTarget, kind: str, message: str) -> None:
        entry = f"[{job.label}] {kind}: {message}"
        self.console_entries.append(entry)
        if kind in {"console.error", "pageerror"}:
            self.console_errors_by_job.setdefault(job.label, []).append(entry)

    def _screenshot(self, page: Any, job: JobTarget, check_id: str) -> str:
        self.screenshots_dir.mkdir(parents=True, exist_ok=True)
        path = self.screenshots_dir / f"{_slug(job.label)}__{_slug(check_id)}.png"
        page.screenshot(path=str(path), full_page=True)
        return str(path.relative_to(self.run_dir))

    def _record(
        self,
        page: Any,
        job: JobTarget,
        check_id: str,
        description: str,
        fn: Callable[[], str | None],
    ) -> None:
        try:
            message = fn() or ""
            screenshot = self._screenshot(page, job, check_id) if self.evidence_screenshot else None
            self.results.append(
                CheckResult(job.label, check_id, description, "pass", message, screenshot)
            )
        except Exception as exc:  # noqa: BLE001 - every check should continue the run
            screenshot = self._screenshot(page, job, check_id)
            self.results.append(
                CheckResult(job.label, check_id, description, "fail", str(exc), screenshot)
            )

    def _wait_map_ready(self, page: Any) -> None:
        page.wait_for_selector("#map", state="visible", timeout=self.timeout_ms)
        page.wait_for_function(
            """
            () => {
              const viewer = window.gridflowMapViewer;
              const rulepack = document.querySelector('#rulepack-badge')?.textContent || '';
              return Boolean(
                viewer
                && viewer.map
                && viewer._mapMeta
                && rulepack
                && rulepack !== 'Loading…'
                && (
                  viewer.featureData.length > 0
                  || viewer._spanLineRefs.length > 0
                  || Number(viewer._mapMeta.pole_count || 0) === 0
                )
              );
            }
            """,
            timeout=self.timeout_ms,
        )

    def _open_first_popup(self, page: Any) -> str:
        return page.evaluate(
            """
            () => {
              const viewer = window.gridflowMapViewer;
              if (!viewer) throw new Error('MapViewer hook unavailable');
              const feature = (viewer.featureData || []).find((item) => item.marker);
              if (!feature) throw new Error('No marker feature available for popup check');
              feature.marker.openPopup();
              const el = document.querySelector('.leaflet-popup-content');
              if (!el) throw new Error('Popup did not open');
              return el.innerText || el.textContent || '';
            }
            """
        )

    def _baseline_checks(self, page: Any, job: JobTarget) -> None:
        self._record(
            page,
            job,
            "app_loads",
            "App loads",
            lambda: (
                page.goto(f"{self.base_url}{job.view_path}", wait_until="domcontentloaded"),
                page.wait_for_selector("#map", state="visible", timeout=self.timeout_ms),
                "map shell visible",
            )[-1],
        )
        self._record(
            page,
            job,
            "target_map_loads",
            "Target job/map loads",
            lambda: (self._wait_map_ready(page), f"{job.data_path} ready")[-1],
        )
        self._record(
            page,
            job,
            "review_navigation_works",
            "Review navigation works",
            lambda: page.evaluate(
                """
                () => {
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
                }
                """
            ),
        )
        self._record(
            page,
            job,
            "next_previous_works",
            "Next / Previous works",
            lambda: page.evaluate(
                """
                () => {
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
                }
                """
            ),
        )
        self._record(
            page,
            job,
            "route_highlight_works",
            "Route highlight works",
            lambda: page.evaluate(
                """
                () => {
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
                }
                """
            ),
        )
        self._record(
            page,
            job,
            "release_map_works",
            "Release Map works",
            lambda: page.evaluate(
                """
                () => {
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
                }
                """
            ),
        )
        self._record(
            page,
            job,
            "planner_awareness_toggle_works",
            "Planner Awareness toggle works",
            lambda: page.evaluate(
                """
                () => {
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
                }
                """
            ),
        )
        self._record(
            page,
            job,
            "popups_open_without_crashing",
            "Popups open without crashing",
            lambda: self._open_first_popup(page)[:120],
        )
        self._record(
            page,
            job,
            "popup_remains_readable",
            "Popup remains readable",
            lambda: page.evaluate(
                """
                () => {
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
                }
                """
            ),
        )
        self._record(
            page,
            job,
            "console_clean",
            "Console clean",
            lambda: (
                (_ for _ in ()).throw(
                    AssertionError(
                        "; ".join(self.console_errors_by_job.get(job.label, [])[-8:])
                        or "Console errors recorded"
                    )
                )
                if self.console_errors_by_job.get(job.label)
                else "no console errors"
            ),
        )

    def _run_checklist_check(self, page: Any, job: JobTarget, check: dict[str, Any]) -> None:
        check_type = str(check["type"])
        check_id = str(check["id"])
        description = str(check.get("description") or check_id)

        def run() -> str | None:
            if check_type == "selector_visible":
                selector = str(check["selector"])
                page.wait_for_selector(selector, state="visible", timeout=self.timeout_ms)
                return selector
            if check_type == "text_present":
                text = str(check["text"])
                page.get_by_text(text).first.wait_for(state="visible", timeout=self.timeout_ms)
                return text
            if check_type == "popup_text_contains":
                text = self._open_first_popup(page)
                missing = [str(item) for item in check.get("contains", []) if str(item) not in text]
                if missing:
                    raise AssertionError(f"Popup missing expected text: {', '.join(missing)}")
                return f"{len(check.get('contains', []))} popup text assertions"
            if check_type == "click_selector":
                selector = str(check["selector"])
                page.locator(selector).first.click(timeout=self.timeout_ms)
                if check.get("expect_selector"):
                    page.wait_for_selector(
                        str(check["expect_selector"]), state="visible", timeout=self.timeout_ms
                    )
                if check.get("expect_text"):
                    page.get_by_text(str(check["expect_text"])).first.wait_for(
                        state="visible", timeout=self.timeout_ms
                    )
                return selector
            if check_type == "route_highlight_active":
                return page.evaluate(
                    """
                    () => {
                      const viewer = window.gridflowMapViewer;
                      const ref = (viewer._spanLineRefs || [])[0];
                      if (!ref) throw new Error('No route span available');
                      viewer.clearSpanRouteHighlight();
                      viewer.handleDirectSpanClick(ref);
                      if (!document.querySelector('.gf-route-highlight')) {
                        throw new Error('Route highlight class missing');
                      }
                      return 'route highlighted';
                    }
                    """
                )
            if check_type == "planner_awareness_visible":
                return page.evaluate(
                    """
                    () => {
                      const viewer = window.gridflowMapViewer;
                      if (!viewer._awarenessMarkerRefs?.length) {
                        throw new Error('No planner awareness markers available');
                      }
                      return `${viewer._awarenessMarkerRefs.length} awareness marker(s)`;
                    }
                    """
                )
            raise ValueError(f"Unsupported checklist check type: {check_type}")

        self._record(page, job, check_id, description, run)

    def run_job(self, browser: Any, job: JobTarget, checklist_checks: list[dict[str, Any]]) -> None:
        context = browser.new_context(viewport={"width": 1440, "height": 1000})
        page = context.new_page()
        page.on("console", lambda msg: self._log_console(job, f"console.{msg.type}", msg.text))
        page.on("pageerror", lambda exc: self._log_console(job, "pageerror", str(exc)))
        try:
            self._baseline_checks(page, job)
            for check in checklist_checks:
                self._run_checklist_check(page, job, check)
            if self.overview_screenshot:
                self._screenshot(page, job, "final_overview")
        finally:
            context.close()

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
            from playwright.sync_api import sync_playwright
        except ImportError:
            print(
                "Playwright is required for browser validation. Install with:\n"
                "  python3 -m pip install playwright\n"
                "  python3 -m playwright install chromium",
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
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch()
            try:
                for job in jobs:
                    runner.run_job(browser, job, checklist_checks)
            finally:
                browser.close()
        runner.write_outputs(jobs, checklist_paths)
        failures = [result for result in runner.results if result.status == "fail"]
        print(f"Validation report: {run_dir / 'validation_report.md'}")
        return 1 if failures else 0
    finally:
        if server is not None:
            server.shutdown()


if __name__ == "__main__":
    raise SystemExit(main())
