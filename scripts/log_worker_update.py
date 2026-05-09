#!/usr/bin/env python3
"""Append a GridFlow worker progress update."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
AI_CONTROL_DIR = REPO_ROOT / "AI_CONTROL"
WORKER_LOG_PATH = AI_CONTROL_DIR / "03_WORKER_LOG.md"


def utc_timestamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def append_update(
    *,
    worker: str,
    branch: str,
    summary: str,
    files: str = "n/a",
    validation: str = "not run",
    next_action: str = "n/a",
    timestamp: str | None = None,
) -> None:
    ts = timestamp or utc_timestamp()
    WORKER_LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    if not WORKER_LOG_PATH.exists():
        WORKER_LOG_PATH.write_text("# GridFlow Worker Log\n\n## Log\n", encoding="utf-8")
    with WORKER_LOG_PATH.open("a", encoding="utf-8") as handle:
        handle.write(
            f"\n### {ts}\n\n"
            f"- Worker: {worker}\n"
            f"- Branch: `{branch}`\n"
            f"- Action: {summary}\n"
            f"- Files changed: {files}\n"
            f"- Validation state: {validation}\n"
            f"- Next action: {next_action}\n"
        )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--worker", required=True)
    parser.add_argument("--branch", required=True)
    parser.add_argument("--summary", required=True)
    parser.add_argument("--files", default="n/a")
    parser.add_argument("--validation", default="not run")
    parser.add_argument("--next-action", default="n/a")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    append_update(
        worker=args.worker,
        branch=args.branch,
        summary=args.summary,
        files=args.files,
        validation=args.validation,
        next_action=args.next_action,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
