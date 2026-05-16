#!/usr/bin/env python3
# ruff: noqa: E402
"""Generate a formal Stage 6C pole-to-ENWL linking report."""

from __future__ import annotations

import argparse
import sys
from collections import Counter
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from gridflow.evidence_combiner import link_survey


def _equipment_summary(result) -> str:
    if not result.direct_equipment_fids:
        return "None"
    return ", ".join(f"FID {fid}" for fid in result.direct_equipment_fids)


def _report_markdown(results: list, survey_root: str, trace_path: str) -> str:
    lines: list[str] = []
    lines.append("# P_LOCAL_002 Linking Report (Stage 6C)\n")
    lines.append(f"**Survey root:** `{survey_root}`")
    lines.append(f"**Trace source:** `{trace_path}`\n")
    lines.append("| Pole | Support | FID | Linking Method | Confidence | Equipment Links | Notes |")
    lines.append("| --- | --- | --- | --- | --- | --- | --- |")
    for result in results:
        notes = result.notes if result.notes else "-"
        lines.append(
            f"| {result.pole_id} | {result.support_no or '-'} | {result.pole_fid or '-'} | "
            f"{result.linking_method} | {result.confidence} | {_equipment_summary(result)} | "
            f"{notes} |"
        )

    counts = Counter(result.confidence for result in results)
    manual_required = sum(1 for result in results if result.manual_confirmation_required)

    lines.append("\n## Summary\n")
    lines.append(f"- Total poles: {len(results)}")
    lines.append(f"- HIGH confidence: {counts.get('HIGH', 0)}")
    lines.append(f"- MEDIUM confidence: {counts.get('MEDIUM', 0)}")
    lines.append(f"- LOW confidence: {counts.get('LOW', 0)}")
    lines.append(f"- Manual confirmation required: {manual_required}\n")
    lines.append(
        "**Design-readiness caution:** This linking output is evidence provenance only. "
        "It does not set `design_ready=True`, does not clear `conductor_spec_missing`, "
        "and does not treat GPS proximity as sole confirmed linkage."
    )
    return "\n".join(lines) + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Link all survey poles to ENWL records using Stage 6C priority rules."
    )
    parser.add_argument(
        "--survey", required=True, help="Survey root (e.g. real_pilot_data/P_LOCAL_002)"
    )
    parser.add_argument("--trace", required=True, help="ENWL trace GeoJSON path")
    parser.add_argument("--output", required=True, help="Output markdown report path")
    args = parser.parse_args(argv)

    results = link_survey(args.survey, args.trace)
    report = _report_markdown(results, args.survey, args.trace)

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(report, encoding="utf-8")
    print(report)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
