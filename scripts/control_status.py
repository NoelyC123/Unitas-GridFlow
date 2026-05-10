#!/usr/bin/env python3
"""Print a concise GridFlow project control snapshot for workers."""

from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
AI_CONTROL_DIR = REPO_ROOT / "AI_CONTROL"
PROJECT_BOARD_PATH = AI_CONTROL_DIR / "00_PROJECT_BOARD.md"
HANDOFF_PATH = AI_CONTROL_DIR / "05_HANDOFF.md"
VALIDATION_LOG_PATH = AI_CONTROL_DIR / "04_VALIDATION_LOG.md"
WORKER_RULES_PATH = AI_CONTROL_DIR / "06_WORKER_RULES.md"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true", dest="as_json")
    return parser


def read_text(path: Path) -> str | None:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return None


def run_git_command(args: list[str]) -> str | None:
    try:
        result = subprocess.run(
            args,
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
    except OSError:
        return None
    if result.returncode != 0:
        return None
    return result.stdout.strip()


def get_git_branch() -> str:
    return run_git_command(["git", "branch", "--show-current"]) or "unknown"


def get_git_status() -> tuple[str, list[str], bool]:
    output = run_git_command(["git", "status", "--short"])
    if output is None:
        return "unknown", [], False
    if not output:
        return "clean", [], False
    lines = [line.strip() for line in output.splitlines() if line.strip()]
    summary = "; ".join(lines[:5])
    if len(lines) > 5:
        summary += "; ..."
    return summary, lines, True


def extract_marked_section(text: str | None, start_marker: str, end_marker: str) -> str | None:
    if not text:
        return None
    start = text.find(start_marker)
    end = text.find(end_marker)
    if start == -1 or end == -1 or end < start:
        return None
    start += len(start_marker)
    return text[start:end].strip()


def extract_heading_section(text: str | None, heading: str) -> str | None:
    if not text:
        return None
    lines = text.splitlines()
    capture: list[str] = []
    in_section = False
    for line in lines:
        if line.strip() == heading:
            in_section = True
            continue
        if in_section and line.startswith("## "):
            break
        if in_section:
            capture.append(line)
    section = "\n".join(capture).strip()
    return section or None


def parse_bullets(section: str | None) -> dict[str, str]:
    data: dict[str, str] = {}
    if not section:
        return data
    for raw_line in section.splitlines():
        line = raw_line.strip()
        if not line.startswith("- ") or ":" not in line:
            continue
        key, value = line[2:].split(":", 1)
        data[key.strip().lower().replace(" ", "_")] = value.strip()
    return data


def summarize_text(section: str | None, *, max_lines: int = 3) -> str:
    if not section:
        return "missing"
    lines = [line.strip() for line in section.splitlines() if line.strip()]
    if not lines:
        return "missing"
    summary = " | ".join(lines[:max_lines])
    return summary


def extract_latest_entry(text: str | None) -> str | None:
    if not text:
        return None
    chunks = text.split("\n### ")
    if len(chunks) < 2:
        return None
    entry = chunks[-1].strip()
    if not entry.startswith("### "):
        entry = f"### {entry}"
    return entry


def summarize_entry(entry: str | None) -> str:
    if not entry:
        return "missing"
    lines = [line.strip() for line in entry.splitlines() if line.strip()]
    if not lines:
        return "missing"
    heading = lines[0].removeprefix("### ").strip()
    bullets = [line[2:].strip() for line in lines[1:] if line.startswith("- ")]
    if not bullets:
        return heading
    return f"{heading} | " + " | ".join(bullets[:4])


def collect_status() -> dict[str, object]:
    board_text = read_text(PROJECT_BOARD_PATH)
    handoff_text = read_text(HANDOFF_PATH)
    validation_text = read_text(VALIDATION_LOG_PATH)
    rules_text = read_text(WORKER_RULES_PATH)

    branch = get_git_branch()
    git_status_summary, git_status_lines, is_dirty = get_git_status()

    stable_section = extract_heading_section(board_text, "## Current stable milestone")
    handoff_summary_section = extract_heading_section(handoff_text, "## Summary")
    worker_rules_section = extract_heading_section(rules_text, "## Required Reading")
    active_task_section = extract_marked_section(
        board_text,
        "<!-- PROJECT_CONTROL:ACTIVE_TASK_START -->",
        "<!-- PROJECT_CONTROL:ACTIVE_TASK_END -->",
    ) or extract_marked_section(
        handoff_text,
        "<!-- PROJECT_CONTROL:HANDOFF_ACTIVE_START -->",
        "<!-- PROJECT_CONTROL:HANDOFF_ACTIVE_END -->",
    )
    latest_validation_entry = extract_latest_entry(validation_text)

    missing_files = [
        str(path.relative_to(REPO_ROOT))
        for path, text in [
            (PROJECT_BOARD_PATH, board_text),
            (HANDOFF_PATH, handoff_text),
            (VALIDATION_LOG_PATH, validation_text),
            (WORKER_RULES_PATH, rules_text),
        ]
        if text is None
    ]

    warnings: list[str] = []
    if is_dirty:
        warnings.append("working tree is dirty")
    if branch == "unknown":
        warnings.append("git branch unknown")
    if git_status_summary == "unknown":
        warnings.append("git status unavailable")
    if missing_files:
        warnings.append("missing control files: " + ", ".join(missing_files))

    return {
        "branch": branch,
        "git_status": git_status_summary,
        "git_status_lines": git_status_lines,
        "stable_milestone": summarize_text(stable_section, max_lines=3),
        "active_task": parse_bullets(active_task_section)
        or {"summary": summarize_text(active_task_section, max_lines=5)},
        "handoff": summarize_text(handoff_summary_section, max_lines=4),
        "latest_validation": summarize_entry(latest_validation_entry),
        "worker_rules": summarize_text(worker_rules_section, max_lines=4),
        "warnings": warnings,
    }


def print_text_report(status: dict[str, object]) -> None:
    active_task = status["active_task"]
    if isinstance(active_task, dict):
        task_summary = " | ".join(f"{key}={value}" for key, value in active_task.items() if value)
    else:
        task_summary = str(active_task)

    warnings = status["warnings"]
    warning_text = "; ".join(warnings) if warnings else "none"

    print("GridFlow Project Control Status")
    print(f"- Git branch: {status['branch']}")
    print(f"- Git status: {status['git_status']}")
    print(f"- Stable milestone: {status['stable_milestone']}")
    print(f"- Active task: {task_summary}")
    print(f"- Handoff summary: {status['handoff']}")
    print(f"- Latest validation: {status['latest_validation']}")
    print(f"- Worker rules reminder: {status['worker_rules']}")
    print(f"- Warnings: {warning_text}")


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    status = collect_status()
    if args.as_json:
        print(json.dumps(status, indent=2, sort_keys=True))
    else:
        print_text_report(status)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
