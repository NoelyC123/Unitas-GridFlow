#!/usr/bin/env python3
"""Append a GridFlow validation run entry."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
AI_CONTROL_DIR = REPO_ROOT / "AI_CONTROL"
VALIDATION_LOG_PATH = AI_CONTROL_DIR / "04_VALIDATION_LOG.md"
WORKER_LOG_PATH = AI_CONTROL_DIR / "03_WORKER_LOG.md"


def utc_timestamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _jobs_text(jobs: list[str] | None) -> str:
    if not jobs:
        return "n/a"
    return ", ".join(f"`{job}`" for job in jobs)


def append_validation(
    *,
    branch: str,
    status: str,
    command: str,
    commit: str = "unknown",
    jobs: list[str] | None = None,
    report: str = "n/a",
    failures: str = "not recorded",
    notes: str = "",
    timestamp: str | None = None,
) -> None:
    ts = timestamp or utc_timestamp()
    VALIDATION_LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    if not VALIDATION_LOG_PATH.exists():
        VALIDATION_LOG_PATH.write_text(
            "# GridFlow Validation Log\n\n## Validation Runs\n",
            encoding="utf-8",
        )

    verdict = "pass" if status.lower() == "pass" else status
    with VALIDATION_LOG_PATH.open("a", encoding="utf-8") as handle:
        handle.write(
            f"\n### {ts}\n\n"
            f"- Branch: `{branch}`\n"
            f"- Commit: `{commit}`\n"
            f"- Jobs tested: {_jobs_text(jobs)}\n"
            f"- Command run: `{command}`\n"
            f"- validation_runs report path: `{report}`\n"
            f"- failures.json status: {failures}\n"
            f"- Screenshots required: {'yes' if report != 'n/a' else 'no'}\n"
            f"- Verdict: {verdict}\n"
        )
        if notes:
            handle.write(f"- Notes: {notes}\n")

    WORKER_LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    if not WORKER_LOG_PATH.exists():
        WORKER_LOG_PATH.write_text("# GridFlow Worker Log\n\n## Log\n", encoding="utf-8")
    with WORKER_LOG_PATH.open("a", encoding="utf-8") as handle:
        handle.write(
            f"\n### {ts}\n\n"
            "- Worker: validation\n"
            f"- Branch: `{branch}`\n"
            f"- Action: Recorded validation run with status `{status}`.\n"
            f"- Files changed: AI_CONTROL/04_VALIDATION_LOG.md\n"
            f"- Validation state: {verdict}\n"
            "- Next action: update handoff or proceed to review\n"
        )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--branch", required=True)
    parser.add_argument("--status", required=True)
    parser.add_argument("--command", required=True)
    parser.add_argument("--commit", default="unknown")
    parser.add_argument("--jobs", nargs="*", default=None)
    parser.add_argument("--report", default="n/a")
    parser.add_argument("--failures", default="not recorded")
    parser.add_argument("--notes", default="")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    append_validation(
        branch=args.branch,
        status=args.status,
        command=args.command,
        commit=args.commit,
        jobs=args.jobs,
        report=args.report,
        failures=args.failures,
        notes=args.notes,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
