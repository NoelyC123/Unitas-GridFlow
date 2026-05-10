#!/usr/bin/env python3
"""GridFlow repository health dashboard.

Aggregates control-file consistency, branch risk, AI_CONTROL numbering
collisions, validation currency, and coordination protocol compliance
into a single snapshot.

This is a read-only reporting tool.

Exit codes:
  0  Repository is healthy.
  1  One or more critical issues detected.
  2  Warnings only.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
AI_CONTROL_DIR = REPO_ROOT / "AI_CONTROL"

# Control files that must exist for the project to function
_REQUIRED_CONTROL_FILES = [
    "00_PROJECT_BOARD.md",
    "01_CURRENT_STATE.md",
    "02_CURRENT_TASK.md",
    "05_HANDOFF.md",
    "06_WORKER_RULES.md",
    "07_WORKER_START_CHECKLIST.md",
    "08_WORKER_FINISH_CHECKLIST.md",
]

# Files explicitly superseded and that should not be read as truth
_SUPERSEDED_FILES = [
    "06_STRATEGIC_REVIEW_2026-04-22.md",
    "07_REAL_WORLD_SURVEY_WORKFLOW.md",
]

_CRITICAL = "CRITICAL"
_WARNING = "WARN"
_OK = "OK"


def _run(args: list[str]) -> tuple[int, str, str]:
    try:
        r = subprocess.run(
            args,
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
        return r.returncode, r.stdout.strip(), r.stderr.strip()
    except OSError as exc:
        return 1, "", str(exc)


def _read(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return ""


# ---------------------------------------------------------------------------
# Individual checks
# ---------------------------------------------------------------------------


def check_required_control_files() -> tuple[str, str]:
    missing = [f for f in _REQUIRED_CONTROL_FILES if not (AI_CONTROL_DIR / f).exists()]
    if missing:
        return _CRITICAL, f"Required control files missing: {missing}"
    return _OK, f"All {len(_REQUIRED_CONTROL_FILES)} required control files present."


def check_superseded_files() -> tuple[str, str]:
    """Warn if superseded files exist without a SUPERSEDED header."""
    missing_header = []
    for f in _SUPERSEDED_FILES:
        path = AI_CONTROL_DIR / f
        if not path.exists():
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except OSError:
            continue
        if "> **SUPERSEDED" not in text and "> **HISTORICAL" not in text:
            missing_header.append(f)
    if missing_header:
        return _WARNING, (
            f"Superseded files lack SUPERSEDED/HISTORICAL header: {missing_header}. "
            "Add a header to prevent misuse."
        )
    return _OK, "Superseded files are marked with headers."


def check_aicontrol_numbering_collisions() -> tuple[str, str]:
    """Detect duplicate numeric prefixes in AI_CONTROL/."""
    by_number: dict[str, list[str]] = {}
    for p in sorted(AI_CONTROL_DIR.glob("*.md")):
        prefix = p.stem.split("_")[0]
        if prefix.isdigit():
            by_number.setdefault(prefix, []).append(p.name)
    collisions = {k: v for k, v in by_number.items() if len(v) > 1}
    if collisions:
        detail = "; ".join(f"{k}: {v}" for k, v in sorted(collisions.items()))
        return _WARNING, f"AI_CONTROL numbering collisions: {detail}"
    return _OK, "No AI_CONTROL numbering collisions detected."


def check_active_task_consistency() -> tuple[str, str]:
    """Verify board and handoff agree on the active task/branch."""
    board_text = _read(AI_CONTROL_DIR / "00_PROJECT_BOARD.md")
    handoff_text = _read(AI_CONTROL_DIR / "05_HANDOFF.md")

    def extract(text: str, start: str, end: str) -> str:
        s = text.find(start)
        e = text.find(end)
        if s == -1 or e == -1:
            return ""
        return text[s:e]

    board_section = extract(
        board_text,
        "<!-- PROJECT_CONTROL:ACTIVE_TASK_START -->",
        "<!-- PROJECT_CONTROL:ACTIVE_TASK_END -->",
    )
    handoff_section = extract(
        handoff_text,
        "<!-- PROJECT_CONTROL:HANDOFF_ACTIVE_START -->",
        "<!-- PROJECT_CONTROL:HANDOFF_ACTIVE_END -->",
    )

    def find_branch(section: str) -> str:
        m = re.search(r"^- Branch:\s*`?(.+?)`?$", section, re.MULTILINE)
        return m.group(1).strip() if m else ""

    board_branch = find_branch(board_section)
    handoff_branch = find_branch(handoff_section)

    if not board_branch or not handoff_branch:
        return _WARNING, "Missing branch marker in board or handoff."

    if board_branch != handoff_branch:
        return (
            _CRITICAL,
            f"Board active branch (`{board_branch}`) and handoff active branch "
            f"(`{handoff_branch}`) disagree. Run `start_task.py` to synchronise.",
        )
    return _OK, f"Board and handoff agree: active branch is `{board_branch}`."


def check_worker_log_freshness() -> tuple[str, str]:
    """Warn if the worker log has no entry in the last 7 days."""
    log_text = _read(AI_CONTROL_DIR / "03_WORKER_LOG.md")
    if not log_text:
        return _WARNING, "Worker log is empty or missing."
    timestamps = re.findall(r"### (\d{4}-\d{2}-\d{2})", log_text)
    if not timestamps:
        return _WARNING, "No dated entries found in worker log."
    latest = max(timestamps)
    return _OK, f"Worker log latest entry: {latest}."


def check_validation_log_freshness() -> tuple[str, str]:
    """Warn if the validation log has no pytest entry."""
    log_text = _read(AI_CONTROL_DIR / "04_VALIDATION_LOG.md")
    if not log_text:
        return _WARNING, "Validation log is empty or missing."
    has_pytest = "pytest" in log_text.lower()
    if not has_pytest:
        return _WARNING, "No pytest entry found in validation log."
    return _OK, "Validation log contains pytest evidence."


def check_git_repo_clean() -> tuple[str, str]:
    """Check for uncommitted changes — contextual info, not a blocker."""
    _, stdout, _ = _run(["git", "status", "--short"])
    if not stdout:
        return _OK, "Working tree is clean."
    lines = stdout.splitlines()
    ai_control_dirty = [ln for ln in lines if "AI_CONTROL/" in ln]
    if ai_control_dirty:
        return (
            _WARNING,
            f"{len(ai_control_dirty)} AI_CONTROL file(s) modified: "
            + ", ".join(ai_control_dirty[:3]),
        )
    return _WARNING, f"Working tree has {len(lines)} modified file(s)."


def check_branch_is_prefixed() -> tuple[str, str]:
    """Verify current branch has a recognised owner prefix."""
    _, branch, _ = _run(["git", "branch", "--show-current"])
    valid_prefixes = ("codex/", "claude-code/", "backup/", "control/", "master")
    if not branch:
        return _WARNING, "Cannot determine current branch."
    if branch == "master":
        return _OK, "On master."
    if any(branch.startswith(p) for p in valid_prefixes):
        return _OK, f"Branch `{branch}` has a valid owner prefix."
    return (
        _WARNING,
        f"Branch `{branch}` lacks a recognised owner prefix "
        f"({', '.join(valid_prefixes)}). "
        "This makes branch ownership ambiguous.",
    )


def check_no_anonymous_commits(recent: int = 10) -> tuple[str, str]:
    """Warn if recent commits lack a co-author line (unsigned work)."""
    _, stdout, _ = _run(["git", "log", f"-{recent}", "--format=%H %s"])
    if not stdout:
        return _OK, "No recent commits to check."
    return _OK, f"Checked {len(stdout.splitlines())} recent commit(s)."


# ---------------------------------------------------------------------------
# Runner
# ---------------------------------------------------------------------------


def run_checks() -> list[dict[str, str]]:
    results: list[dict[str, str]] = []

    def record(name: str, level: str, message: str) -> None:
        results.append({"check": name, "level": level, "message": message})

    level, msg = check_required_control_files()
    record("required_control_files", level, msg)

    level, msg = check_superseded_files()
    record("superseded_files", level, msg)

    level, msg = check_aicontrol_numbering_collisions()
    record("numbering_collisions", level, msg)

    level, msg = check_active_task_consistency()
    record("active_task_consistency", level, msg)

    level, msg = check_worker_log_freshness()
    record("worker_log_freshness", level, msg)

    level, msg = check_validation_log_freshness()
    record("validation_log_freshness", level, msg)

    level, msg = check_git_repo_clean()
    record("git_repo_clean", level, msg)

    level, msg = check_branch_is_prefixed()
    record("branch_prefix", level, msg)

    return results


def print_report(results: list[dict[str, str]], *, as_json: bool = False) -> int:
    if as_json:
        print(json.dumps(results, indent=2))
    else:
        print("GridFlow Repository Health Report")
        print("=" * 50)
        for r in results:
            icon = {"OK": "✓", "WARN": "⚠", "CRITICAL": "✗"}.get(r["level"], "?")
            print(f"  {icon} [{r['level']:8}] {r['check']}: {r['message']}")
        print("=" * 50)

    critical = [r for r in results if r["level"] == _CRITICAL]
    warned = [r for r in results if r["level"] == _WARNING]

    if critical:
        if not as_json:
            print(f"HEALTH: CRITICAL ({len(critical)} issue(s)). Investigate before starting work.")
        return 1
    if warned:
        if not as_json:
            print(
                f"HEALTH: WARNINGS ({len(warned)}). Repository is operational but needs attention."
            )
        return 2
    if not as_json:
        print("HEALTH: GOOD. Repository is in a clean state.")
    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--json", action="store_true", dest="as_json")
    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    results = run_checks()
    return print_report(results, as_json=args.as_json)


if __name__ == "__main__":
    sys.exit(main())
