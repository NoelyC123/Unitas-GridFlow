#!/usr/bin/env python3
"""Stage 4C.3 Matching Engine CLI."""

import json
import logging
import sys
from argparse import ArgumentParser
from datetime import datetime
from pathlib import Path

from gridflow.baseline.models import BaselineDataset
from gridflow.field.models import FieldDataset
from gridflow.matching import ConfidenceScorer, RegisterBuilder, SupportNumberMatcher

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


def parse_args():
    parser = ArgumentParser(description="Stage 4C.3 Matching Engine")
    parser.add_argument("--baseline", required=True, type=Path)
    parser.add_argument("--field", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--csv", action="store_true")
    parser.add_argument("--report", type=Path)
    parser.add_argument(
        "--log-level", choices=["DEBUG", "INFO", "WARNING", "ERROR"], default="INFO"
    )
    return parser.parse_args()


def _load_baseline(path: Path) -> BaselineDataset:
    with open(path) as f:
        data = json.load(f)
    from gridflow.baseline.models import BaselinePole

    poles = [BaselinePole(**p) for p in data.get("poles", [])]
    return BaselineDataset(poles=poles, metadata=data.get("metadata", {}))


def _load_field(path: Path) -> FieldDataset:
    with open(path) as f:
        data = json.load(f)
    from gridflow.field.models import FieldPole

    poles = [FieldPole(**p) for p in data.get("poles", [])]
    return FieldDataset(
        dataset_path=data.get("metadata", {}).get("source_path", ""),
        scan_date=data.get("metadata", {}).get("scan_date", ""),
        total_poles=len(poles),
        poles=poles,
        evidence_summary=data.get("evidence_summary", {}),
    )


def main():
    args = parse_args()
    logging.getLogger().setLevel(getattr(logging, args.log_level))

    try:
        logger.info("Loading baseline: %s", args.baseline)
        baseline = _load_baseline(args.baseline)
        logger.info("Loaded %d baseline poles", baseline.pole_count)

        logger.info("Loading field evidence: %s", args.field)
        field = _load_field(args.field)
        logger.info("Loaded %d field poles", field.total_poles)

        # Match
        logger.info("Running support number matching...")
        matcher = SupportNumberMatcher()
        match_results = matcher.match(baseline, field)

        # Score confidence
        logger.info("Scoring confidence...")
        scorer = ConfidenceScorer()
        b_by_id = {p.pole_id: p for p in baseline.poles}
        f_by_folder = {p.folder_name: p for p in field.poles}
        for mr in match_results:
            bp = b_by_id.get(mr.baseline_pole_id)
            fp = f_by_folder.get(mr.field_folder or "")
            if bp:
                scorer.score(mr, bp, fp)

        # Build register
        builder = RegisterBuilder()
        register = builder.build(match_results, baseline, field)

        logger.info(
            "Register: %d matched, match rate %.1f%%",
            register.matched,
            register.match_rate,
        )

        # Write JSON output
        args.output.parent.mkdir(parents=True, exist_ok=True)
        output_data = {
            "metadata": {
                "generated_at": datetime.now().isoformat(),
                "baseline_source": str(args.baseline),
                "field_source": str(args.field),
                "baseline_total": register.baseline_total,
                "field_total": register.field_total,
                "matched": register.matched,
                "match_rate": register.match_rate,
                "high_confidence": register.high_confidence,
                "medium_confidence": register.medium_confidence,
                "low_confidence": register.low_confidence,
            },
            "entries": [e.model_dump() for e in register.entries],
        }
        with open(args.output, "w") as f:
            json.dump(output_data, f, indent=2, default=str)
        logger.info("Output written to %s", args.output)

        # Optional CSV
        if args.csv:
            csv_path = args.output.with_suffix(".csv")
            builder.export_csv(register, csv_path)

        # Optional report
        if args.report:
            _write_report(register, args.report)

        return 0

    except Exception as e:
        logger.error("Matching failed: %s", e, exc_info=True)
        return 1


def _write_report(register, report_path: Path):
    report_path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# Stage 4C.3 Match Register Report",
        "",
        "## Summary",
        f"- **Baseline Poles**: {register.baseline_total}",
        f"- **Field Poles**: {register.field_total}",
        f"- **Matched**: {register.matched}",
        f"- **Match Rate**: {register.match_rate:.1f}%",
        f"- **HIGH Confidence**: {register.high_confidence}",
        f"- **MEDIUM Confidence**: {register.medium_confidence}",
        f"- **LOW Confidence**: {register.low_confidence}",
        "",
        "## Match Entries",
        "",
        "| Support No | Baseline ID | Field Folder | Confidence | Type | Flags |",
        "|-----------|-------------|--------------|------------|------|-------|",
    ]
    for entry in register.entries:
        flags = "|".join(entry.conflict_flags) if entry.conflict_flags else "-"
        lines.append(
            f"| {entry.support_no} | {entry.baseline_pole_id or '-'} "
            f"| {entry.field_folder or '-'} | {entry.match_confidence} "
            f"| {entry.match_type} | {flags} |"
        )
    with open(report_path, "w") as f:
        f.write("\n".join(lines))
    logger.info("Report written to %s", report_path)


if __name__ == "__main__":
    sys.exit(main())
