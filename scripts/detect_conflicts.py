#!/usr/bin/env python3
# ruff: noqa: E402
"""Detect read-only Stage 6D evidence conflicts across a survey."""

from __future__ import annotations

import argparse
import sys
from collections import Counter
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from gridflow.conflict_detector import ConflictDetector


def _build_report(conflicts_by_pole: dict[str, list], survey: str, trace: str) -> str:
    all_conflicts = [c for items in conflicts_by_pole.values() for c in items]
    sev_counts = Counter(c.severity for c in all_conflicts)
    poles_with_conflicts = sum(1 for _, items in conflicts_by_pole.items() if items)

    lines: list[str] = []
    lines.append("# P_LOCAL_002 Conflict Detection Report\n")
    lines.append(f"**Survey root:** `{survey}`")
    lines.append(f"**Trace source:** `{trace}`\n")
    lines.append("## Summary")
    lines.append(f"- Total poles analyzed: {len(conflicts_by_pole)}")
    lines.append(f"- Poles with conflicts: {poles_with_conflicts}")
    lines.append(f"- CRITICAL conflicts: {sev_counts.get('CRITICAL', 0)}")
    lines.append(f"- WARNING conflicts: {sev_counts.get('WARNING', 0)}")
    lines.append(f"- INFO conflicts: {sev_counts.get('INFO', 0)}\n")

    lines.append("## Conflicts by Pole\n")
    for pole in sorted(conflicts_by_pole, key=_pole_sort_key):
        pole_conflicts = conflicts_by_pole[pole]
        support = pole.split("_SUPPORT_", 1)[1] if "_SUPPORT_" in pole else "UNKNOWN"
        lines.append(f"### Pole {pole.split('_', 1)[0]} ({support})")
        if not pole_conflicts:
            lines.append("- No conflicts detected\n")
            continue
        for c in pole_conflicts:
            lines.append(f"- **{c.severity}**: {c.conflict_type}")
            if c.field_value is not None:
                lines.append(f"  - Field: `{c.field_value}`")
            if c.enwl_value is not None:
                lines.append(f"  - ENWL: `{c.enwl_value}`")
            if c.trace_value is not None:
                lines.append(f"  - Trace: `{c.trace_value}`")
            lines.append(f"  - Description: {c.description}")
            lines.append(f"  - Action: {c.recommended_action}")
        lines.append("")

    lines.append("## Recommended Actions")
    lines.append("1. CRITICAL conflicts must be resolved before design")
    lines.append("2. WARNING conflicts should be verified with field photos")
    lines.append("3. INFO conflicts are evidence gaps, not errors")
    return "\n".join(lines) + "\n"


def _pole_sort_key(pole_id: str) -> tuple[int, str]:
    prefix = pole_id.split("_", 1)[0]
    return (int(prefix) if prefix.isdigit() else 999, pole_id)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Stage 6D three-source conflict detection.")
    parser.add_argument(
        "--survey", required=True, help="Survey root (e.g. real_pilot_data/P_LOCAL_002)"
    )
    parser.add_argument("--trace", required=True, help="ENWL trace GeoJSON file path")
    parser.add_argument("--output", required=True, help="Output markdown report path")
    args = parser.parse_args(argv)

    detector = ConflictDetector()
    conflicts = detector.detect_survey(args.survey, args.trace)
    report = _build_report(conflicts, args.survey, args.trace)

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(report, encoding="utf-8")
    print(report)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
