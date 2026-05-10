#!/usr/bin/env python3
"""Worker startup safety check for GridFlow.

Performs every mandatory pre-task check from AI_CONTROL/41 before a worker
begins coding.  Exits non-zero on any blocking failure so automation can
refuse to proceed.

Exit codes:
  0  All checks pass — safe to start work.
  1  One or more blocking failures — do NOT start work.
  2  Warnings only — proceed with caution, but not blocked.
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
PROJECT_BOARD_PATH = AI_CONTROL_DIR / "00_PROJECT_BOARD.md"
HANDOFF_PATH = AI_CONTROL_DIR / "05_HANDOFF.md"

_BLOCKING = "BLOCK"
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


def check_git_working_tree() -> tuple[str, str]:
    """Working tree must be clean before starting a task."""
    _, stdout, _ = _run(["git", "status", "--short"])
    if not stdout:
        return _OK, "Working tree is clean."
    ai_control_dirty = [ln for ln in stdout.splitlines() if "AI_CONTROL/" in ln]
    if ai_control_dirty:
        return (
            _BLOCKING,
            f"AI_CONTROL files are modified: {', '.join(ai_control_dirty)}. "
            "Run `git restore` or commit before starting a new task.",
        )
    return (
        _WARNING,
        f"Working tree has uncommitted changes:\n{stdout}\n"
        "Ensure these belong to this task before proceeding.",
    )


def check_branch_name(expected_branch: str | None) -> tuple[str, str]:
    """Active git branch must match the task's assigned branch."""
    _, branch, _ = _run(["git", "branch", "--show-current"])
    if not branch:
        return _BLOCKING, "Cannot determine current git branch."
    if expected_branch and branch != expected_branch:
        return (
            _BLOCKING,
            f"On branch `{branch}` but task requires `{expected_branch}`. "
            "Switch branches before starting.",
        )
    if not expected_branch:
        return _WARNING, f"No expected branch specified; currently on `{branch}`."
    return _OK, f"Branch `{branch}` matches expected branch."


def check_master_baseline() -> tuple[str, str]:
    """Record the master HEAD SHA so it's captured at task start."""
    _, master_sha, _ = _run(["git", "rev-parse", "origin/master"])
    if not master_sha:
        _, master_sha, _ = _run(["git", "rev-parse", "master"])
    if not master_sha:
        return _WARNING, "Cannot resolve master HEAD SHA."
    return _OK, f"Master baseline: {master_sha[:12]}"


def check_branch_freshness() -> tuple[str, str]:
    """Warn if the current branch is significantly behind origin/master."""
    _, stdout, _ = _run(["git", "rev-list", "--left-right", "--count", "origin/master...HEAD"])
    if not stdout or "\t" not in stdout:
        return _WARNING, "Cannot determine branch freshness (no remote or new branch)."
    behind, ahead = stdout.split("\t", 1)
    try:
        behind_n = int(behind.strip())
        ahead_n = int(ahead.strip())
    except ValueError:
        return _WARNING, "Cannot parse branch commit counts."
    if behind_n > 20:
        return (
            _WARNING,
            f"Branch is {behind_n} commits behind origin/master "
            f"(and {ahead_n} ahead). Consider rebasing before heavy work.",
        )
    return _OK, f"Branch is {behind_n} behind / {ahead_n} ahead of origin/master."


def check_no_parallel_active_task(expected_task: str | None) -> tuple[str, str]:
    """Detect if a different task is already marked active in the project board."""
    board_text = _read(PROJECT_BOARD_PATH)
    start = board_text.find("<!-- PROJECT_CONTROL:ACTIVE_TASK_START -->")
    end = board_text.find("<!-- PROJECT_CONTROL:ACTIVE_TASK_END -->")
    if start == -1 or end == -1:
        return _WARNING, "No active-task marker found in project board."
    section = board_text[start:end]
    task_match = re.search(r"^- Task:\s*(.+)$", section, re.MULTILINE)
    board_task = task_match.group(1).strip() if task_match else ""
    owner_match = re.search(r"^- Owner:\s*(.+)$", section, re.MULTILINE)
    board_owner = owner_match.group(1).strip() if owner_match else ""
    if expected_task and board_task and board_task != expected_task:
        return (
            _BLOCKING,
            f"Project board shows a different active task: '{board_task}' (owner: {board_owner}). "
            f"Expected: '{expected_task}'. Confirm coordination before starting.",
        )
    return _OK, f"Active task: '{board_task}' (owner: {board_owner})."


def check_handoff_marker(expected_branch: str | None) -> tuple[str, str]:
    """Detect if the handoff active-task block points to a different branch."""
    handoff_text = _read(HANDOFF_PATH)
    start = handoff_text.find("<!-- PROJECT_CONTROL:HANDOFF_ACTIVE_START -->")
    end = handoff_text.find("<!-- PROJECT_CONTROL:HANDOFF_ACTIVE_END -->")
    if start == -1 or end == -1:
        return _WARNING, "No active marker in handoff file."
    section = handoff_text[start:end]
    branch_match = re.search(r"^- Branch:\s*`?(.+?)`?$", section, re.MULTILINE)
    handoff_branch = branch_match.group(1).strip() if branch_match else ""
    if expected_branch and handoff_branch and handoff_branch != expected_branch:
        return (
            _WARNING,
            f"Handoff file points to branch `{handoff_branch}` "
            f"but this task uses `{expected_branch}`. "
            "Run `start_task.py` to update the handoff.",
        )
    return _OK, f"Handoff branch: `{handoff_branch}`."


def check_no_branch_name_collision(branch: str | None) -> tuple[str, str]:
    """Confirm the task branch does not already exist on a different SHA."""
    if not branch:
        return _WARNING, "No branch name provided; skipping collision check."
    _, _, current = _run(["git", "branch", "--show-current"])
    _, stdout, _ = _run(["git", "branch", "-a"])
    existing = [ln.strip().lstrip("* ").removeprefix("remotes/") for ln in stdout.splitlines()]
    if branch in existing:
        return _OK, f"Branch `{branch}` exists (current — expected)."
    collisions = [e for e in existing if e != branch and Path(e).name == Path(branch).name]
    if collisions:
        return (
            _WARNING,
            f"Similar branch names exist: {collisions}. Confirm there is no scope overlap.",
        )
    return _OK, f"Branch name `{branch}` is unique."


def check_aicontrol_slot_free(slot_number: str | None) -> tuple[str, str]:
    """Confirm the chosen AI_CONTROL doc number slot is not already taken."""
    if not slot_number:
        return _OK, "No AI_CONTROL slot check requested."
    matches = list(AI_CONTROL_DIR.glob(f"{slot_number}_*.md"))
    if matches:
        names = [m.name for m in matches]
        return (
            _BLOCKING,
            f"AI_CONTROL slot {slot_number} is already occupied by: {names}. "
            "Choose a different number or use a namespace prefix.",
        )
    return _OK, f"AI_CONTROL slot {slot_number} is free."


def check_map_viewer_untouched(forbid_map_viewer: bool) -> tuple[str, str]:
    """Verify map-viewer.js has not been modified if this task forbids it."""
    if not forbid_map_viewer:
        return _OK, "map-viewer guard not requested."
    _, stdout, _ = _run(["git", "diff", "master", "--", "app/static/js/map-viewer.js"])
    if stdout and stdout.strip():
        lines = len(stdout.splitlines())
        return (
            _BLOCKING,
            f"app/static/js/map-viewer.js has {lines} diff lines vs master "
            "but this task must not change it. Restore before proceeding.",
        )
    return _OK, "app/static/js/map-viewer.js is unchanged vs master."


# ---------------------------------------------------------------------------
# Runner
# ---------------------------------------------------------------------------


_ALL_CHECKS = [
    "git_working_tree",
    "branch_name",
    "master_baseline",
    "branch_freshness",
    "parallel_active_task",
    "handoff_marker",
    "branch_collision",
    "aicontrol_slot",
    "map_viewer",
]


def run_checks(
    *,
    expected_branch: str | None = None,
    expected_task: str | None = None,
    aicontrol_slot: str | None = None,
    forbid_map_viewer: bool = False,
    checks: list[str] | None = None,
) -> list[dict[str, str]]:
    active = set(checks) if checks else set(_ALL_CHECKS)
    results: list[dict[str, str]] = []

    def record(name: str, level: str, message: str) -> None:
        results.append({"check": name, "level": level, "message": message})

    if "git_working_tree" in active:
        level, msg = check_git_working_tree()
        record("git_working_tree", level, msg)

    if "branch_name" in active:
        level, msg = check_branch_name(expected_branch)
        record("branch_name", level, msg)

    if "master_baseline" in active:
        level, msg = check_master_baseline()
        record("master_baseline", level, msg)

    if "branch_freshness" in active:
        level, msg = check_branch_freshness()
        record("branch_freshness", level, msg)

    if "parallel_active_task" in active:
        level, msg = check_no_parallel_active_task(expected_task)
        record("parallel_active_task", level, msg)

    if "handoff_marker" in active:
        level, msg = check_handoff_marker(expected_branch)
        record("handoff_marker", level, msg)

    if "branch_collision" in active:
        level, msg = check_no_branch_name_collision(expected_branch)
        record("branch_collision", level, msg)

    if "aicontrol_slot" in active:
        level, msg = check_aicontrol_slot_free(aicontrol_slot)
        record("aicontrol_slot", level, msg)

    if "map_viewer" in active:
        level, msg = check_map_viewer_untouched(forbid_map_viewer)
        record("map_viewer", level, msg)

    return results


def print_report(results: list[dict[str, str]], *, as_json: bool = False) -> int:
    if as_json:
        print(json.dumps(results, indent=2))
    else:
        print("GridFlow Worker Safety Check")
        print("=" * 40)
        for r in results:
            icon = {"OK": "✓", "WARN": "⚠", "BLOCK": "✗"}.get(r["level"], "?")
            print(f"  {icon} [{r['level']:5}] {r['check']}: {r['message']}")
        print("=" * 40)

    blocked = [r for r in results if r["level"] == _BLOCKING]
    warned = [r for r in results if r["level"] == _WARNING]
    if blocked:
        if not as_json:
            print(f"RESULT: BLOCKED ({len(blocked)} blocking failure(s)). Do NOT start work.")
        return 1
    if warned:
        if not as_json:
            print(f"RESULT: WARNINGS ({len(warned)} warning(s)). Proceed with caution.")
        return 2
    if not as_json:
        print("RESULT: ALL CHECKS PASS. Safe to begin work.")
    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--branch", help="Expected branch name for this task.")
    p.add_argument("--task", help="Expected active task name.")
    p.add_argument(
        "--aicontrol-slot",
        dest="aicontrol_slot",
        help="AI_CONTROL numeric slot to verify is free (e.g. '43').",
    )
    p.add_argument(
        "--forbid-map-viewer",
        action="store_true",
        dest="forbid_map_viewer",
        help="Fail if app/static/js/map-viewer.js differs from master.",
    )
    p.add_argument(
        "--checks",
        nargs="*",
        choices=_ALL_CHECKS,
        help="Run only these checks (default: all).",
    )
    p.add_argument("--json", action="store_true", dest="as_json")
    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    results = run_checks(
        expected_branch=args.branch,
        expected_task=args.task,
        aicontrol_slot=args.aicontrol_slot,
        forbid_map_viewer=args.forbid_map_viewer,
        checks=args.checks,
    )
    return print_report(results, as_json=args.as_json)


if __name__ == "__main__":
    sys.exit(main())
