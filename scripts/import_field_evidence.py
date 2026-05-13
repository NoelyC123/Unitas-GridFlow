#!/usr/bin/env python3
"""Stage 4C.2 Field Evidence Importer CLI."""

import json
import logging
import sys
from argparse import ArgumentParser
from datetime import datetime
from pathlib import Path

from gridflow.field import (
    EvidenceQualityScorer,
    FieldDatasetValidator,
    FolderScanner,
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


def parse_args():
    parser = ArgumentParser(description="Stage 4C.2 Field Evidence Importer")
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--validate", action="store_true")
    parser.add_argument("--score", action="store_true")
    parser.add_argument("--report", type=Path)
    parser.add_argument(
        "--log-level", choices=["DEBUG", "INFO", "WARNING", "ERROR"], default="INFO"
    )
    return parser.parse_args()


def main():
    args = parse_args()
    logging.getLogger().setLevel(getattr(logging, args.log_level))

    try:
        logger.info("Scanning field evidence: %s", args.input)
        scanner = FolderScanner()
        dataset = scanner.scan(args.input)
        logger.info("Scanned %d poles", dataset.total_poles)

        if args.score:
            logger.info("Scoring evidence quality...")
            scorer = EvidenceQualityScorer()
            dataset = scorer.score_dataset(dataset)

        validation_report = None
        if args.validate:
            logger.info("Validating dataset...")
            validator = FieldDatasetValidator()
            validation_report = validator.validate(dataset)
            logger.info(
                "Validation: %d valid, %d errors, %d warnings",
                validation_report.valid_poles,
                validation_report.error_count,
                validation_report.warning_count,
            )

        # Write output JSON
        args.output.parent.mkdir(parents=True, exist_ok=True)
        output_data = {
            "metadata": {
                "source_path": str(dataset.dataset_path),
                "scan_date": dataset.scan_date,
                "generated_at": datetime.now().isoformat(),
                "total_poles": dataset.total_poles,
            },
            "poles": [p.model_dump() for p in dataset.poles],
            "evidence_summary": dataset.evidence_summary,
            "validation_report": validation_report.model_dump() if validation_report else None,
        }

        with open(args.output, "w") as f:
            json.dump(output_data, f, indent=2, default=str)
        logger.info("Output written to %s", args.output)

        # Optional markdown report
        if args.report:
            _write_report(dataset, validation_report, args.report)

        return 0

    except Exception as e:
        logger.error("Import failed: %s", e, exc_info=True)
        return 1


def _write_report(dataset, validation_report, report_path: Path):
    report_path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# Stage 4C.2 Field Evidence Import Report",
        "",
        "## Summary",
        f"- **Total Poles**: {dataset.total_poles}",
        f"- **Scan Date**: {dataset.scan_date}",
        "",
        "## Evidence Quality",
        f"- HIGH: {dataset.evidence_summary.get('high', 0)}",
        f"- MEDIUM: {dataset.evidence_summary.get('medium', 0)}",
        f"- LOW: {dataset.evidence_summary.get('low', 0)}",
        "",
        "## Poles",
        "",
        "| # | Folder | Support No | Quality | Photos | Screenshots | Flags |",
        "|---|--------|-----------|---------|--------|-------------|-------|",
    ]

    for pole in dataset.poles:
        flags = ", ".join(pole.special_flags) if pole.special_flags else "-"
        lines.append(
            f"| {pole.sequence_no or '-'} | {pole.folder_name} | {pole.support_no} "
            f"| {pole.evidence_quality} | {pole.field_photo_count} "
            f"| {pole.map_screenshot_count} | {flags} |"
        )

    if validation_report and validation_report.issues:
        lines += [
            "",
            "## Validation Issues",
            "| Pole | Field | Issue | Severity |",
            "|------|-------|-------|----------|",
        ]
        for issue in validation_report.issues:
            lines.append(
                f"| {issue.pole_id} | {issue.field} | {issue.message} | {issue.severity} |"
            )

    with open(report_path, "w") as f:
        f.write("\n".join(lines))
    logger.info("Report written to %s", report_path)


if __name__ == "__main__":
    sys.exit(main())
