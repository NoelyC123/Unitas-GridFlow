#!/usr/bin/env python3
"""Record the start of a GridFlow control-layer task."""

from __future__ import annotations

import argparse
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
AI_CONTROL_DIR = REPO_ROOT / "AI_CONTROL"
PROJECT_BOARD_PATH = AI_CONTROL_DIR / "00_PROJECT_BOARD.md"
WORKER_LOG_PATH = AI_CONTROL_DIR / "03_WORKER_LOG.md"
HANDOFF_PATH = AI_CONTROL_DIR / "05_HANDOFF.md"


def _git_ai_control_dirty() -> list[str]:
    """Return lines from git status that touch AI_CONTROL files."""
    try:
        result = subprocess.run(
            ["git", "status", "--short"],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
    except OSError:
        return []
    return [line for line in result.stdout.splitlines() if "AI_CONTROL/" in line]


def refuse_if_dirty_control_files() -> None:
    """Abort with a clear message if AI_CONTROL files have uncommitted edits.

    Prevents a new agent from inheriting a previous agent's in-progress
    control-file edits and accidentally committing them under the wrong task.
    (See AI_CONTROL/41_WORKER_COORDINATION_RISK_REVIEW.md, Incident 1.)
    """
    dirty = _git_ai_control_dirty()
    if dirty:
        lines = "\n".join(f"  {line}" for line in dirty)
        print(
            "ERROR: AI_CONTROL files have uncommitted changes:\n"
            f"{lines}\n\n"
            "Run `git restore AI_CONTROL/` or commit those changes before "
            "starting a new task.  This check prevents stale control-file "
            "edits from being attributed to the wrong task.",
            file=sys.stderr,
        )
        sys.exit(1)


def utc_timestamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _ensure_parent(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)


def append_worker_log(
    *,
    worker: str,
    branch: str,
    action: str,
    files: str = "n/a",
    validation: str = "pending",
    next_action: str = "n/a",
    timestamp: str | None = None,
) -> None:
    ts = timestamp or utc_timestamp()
    _ensure_parent(WORKER_LOG_PATH)
    if not WORKER_LOG_PATH.exists():
        WORKER_LOG_PATH.write_text("# GridFlow Worker Log\n\n## Log\n", encoding="utf-8")
    with WORKER_LOG_PATH.open("a", encoding="utf-8") as handle:
        handle.write(
            f"\n### {ts}\n\n"
            f"- Worker: {worker}\n"
            f"- Branch: `{branch}`\n"
            f"- Action: {action}\n"
            f"- Files changed: {files}\n"
            f"- Validation state: {validation}\n"
            f"- Next action: {next_action}\n"
        )


def replace_marked_section(
    path: Path,
    start_marker: str,
    end_marker: str,
    replacement: str,
) -> None:
    _ensure_parent(path)
    original = path.read_text(encoding="utf-8") if path.exists() else ""
    start = original.find(start_marker)
    end = original.find(end_marker)
    if start == -1 or end == -1 or end < start:
        text = original.rstrip() + f"\n\n{start_marker}\n{replacement.rstrip()}\n{end_marker}\n"
    else:
        end += len(end_marker)
        text = (
            original[:start]
            + f"{start_marker}\n{replacement.rstrip()}\n{end_marker}"
            + original[end:]
        )
    path.write_text(text, encoding="utf-8")


def update_handoff(
    *,
    task: str,
    owner: str,
    branch: str,
    status: str,
    summary: str,
    timestamp: str,
) -> None:
    replacement = (
        f"- Task: {task}\n"
        f"- Owner: {owner}\n"
        f"- Branch: `{branch}`\n"
        f"- Status: {status}\n"
        f"- Summary: {summary or 'n/a'}\n"
        f"- Updated: {timestamp}"
    )
    replace_marked_section(
        HANDOFF_PATH,
        "<!-- PROJECT_CONTROL:HANDOFF_ACTIVE_START -->",
        "<!-- PROJECT_CONTROL:HANDOFF_ACTIVE_END -->",
        replacement,
    )


def update_project_board(
    *,
    task: str,
    owner: str,
    branch: str,
    status: str,
    summary: str,
) -> None:
    replacement = (
        f"- Task: {task}\n"
        f"- Branch: `{branch}`\n"
        f"- Owner: {owner}\n"
        f"- Status: {status}\n"
        f"- Summary: {summary or 'n/a'}"
    )
    replace_marked_section(
        PROJECT_BOARD_PATH,
        "<!-- PROJECT_CONTROL:ACTIVE_TASK_START -->",
        "<!-- PROJECT_CONTROL:ACTIVE_TASK_END -->",
        replacement,
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--task", required=True)
    parser.add_argument("--owner", required=True)
    parser.add_argument("--branch", required=True)
    parser.add_argument("--status", default="in_progress")
    parser.add_argument("--summary", default="")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    refuse_if_dirty_control_files()
    ts = utc_timestamp()
    append_worker_log(
        worker=args.owner,
        branch=args.branch,
        action=f"Started task: {args.task}. {args.summary}".strip(),
        files="control files pending",
        validation="pending",
        next_action="implement task and validate",
        timestamp=ts,
    )
    update_handoff(
        task=args.task,
        owner=args.owner,
        branch=args.branch,
        status=args.status,
        summary=args.summary,
        timestamp=ts,
    )
    update_project_board(
        task=args.task,
        owner=args.owner,
        branch=args.branch,
        status=args.status,
        summary=args.summary,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
