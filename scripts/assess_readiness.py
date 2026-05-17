#!/usr/bin/env python3
# ruff: noqa: E402
"""Run conservative Stage 6E design-readiness assessment."""

from __future__ import annotations

import argparse
import sys
from collections import Counter
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from gridflow.readiness import ReadinessAssessor


def _render_report(results: list, survey_root: str, trace_path: str) -> str:
    lines: list[str] = []
    lines.append("# P_LOCAL_002 Readiness Report\n")
    lines.append(f"**Survey root:** `{survey_root}`")
    lines.append(f"**Trace source:** `{trace_path}`\n")
    lines.append("| Pole | Support | Readiness | Status | Confidence | Blockers | Warnings |")
    lines.append("| --- | --- | --- | --- | --- | --- | --- |")
    for result in results:
        blockers = "; ".join(result.readiness_blockers) if result.readiness_blockers else "None"
        warnings = "; ".join(result.readiness_warnings) if result.readiness_warnings else "-"
        lines.append(
            f"| {result.pole_id} | {result.support_no or '-'} | "
            f"{str(result.design_ready).lower()} | {result.readiness_status} | "
            f"{result.readiness_confidence} | {blockers} | {warnings} |"
        )

    counts = Counter(result.readiness_status for result in results)
    ready = [result.pole_id for result in results if result.readiness_status == "ready"]
    review = [result.pole_id for result in results if result.readiness_status == "review_required"]
    not_ready = [result.pole_id for result in results if result.readiness_status == "not_ready"]
    insufficient = [
        result.pole_id for result in results if result.readiness_status == "insufficient_evidence"
    ]

    lines.append("\n## Summary\n")
    lines.append(f"- ready (design_ready=true): {counts.get('ready', 0)}")
    lines.append(
        f"- review_required: {counts.get('review_required', 0)}"
        + (f" ({', '.join(review)})" if review else "")
    )
    lines.append(
        f"- not_ready: {counts.get('not_ready', 0)}"
        + (f" ({', '.join(not_ready)})" if not_ready else "")
    )
    lines.append(
        f"- insufficient_evidence: {counts.get('insufficient_evidence', 0)}"
        + (f" ({', '.join(insufficient)})" if insufficient else "")
    )
    if ready:
        lines.append(f"- design_ready poles: {', '.join(ready)}")
    lines.append(
        "- conductor_spec_missing remains unchanged by this assessment; "
        "route-level conductor evidence does not clear it."
    )
    return "\n".join(lines) + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Stage 6E conservative design-readiness assessor.")
    parser.add_argument(
        "--survey", required=True, help="Survey root (e.g. real_pilot_data/P_LOCAL_002)"
    )
    parser.add_argument("--trace", required=True, help="ENWL trace GeoJSON file path")
    parser.add_argument("--output", required=True, help="Output markdown report path")
    args = parser.parse_args(argv)

    assessor = ReadinessAssessor()
    results = assessor.assess_survey(args.survey, args.trace)
    report = _render_report(results, args.survey, args.trace)

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(report, encoding="utf-8")
    print(report)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
