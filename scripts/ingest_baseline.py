#!/usr/bin/env python3
"""
Stage 4C.1 Baseline Ingestion CLI

Parse, validate, and normalize DNO/Trimble baseline CSV exports.
"""

import json
import logging
import sys
from argparse import ArgumentParser
from datetime import datetime
from pathlib import Path

from gridflow.baseline import (
    CoordinateTransformer,
    CSVParser,
    RouteReconstructor,
    SchemaValidator,
    SupportNumberNormalizer,
)

# Set up logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def parse_arguments():
    """Parse command line arguments."""
    parser = ArgumentParser(
        description="Stage 4C.1 Baseline Ingestion Engine",
        epilog="Example: python scripts/ingest_baseline.py --input baseline.csv --output baseline.json --validate --transform-coords",
    )

    parser.add_argument("--input", required=True, type=Path, help="Path to baseline CSV file")

    parser.add_argument(
        "--format",
        choices=["ENWL", "TRIMBLE", "GENERIC", "AUTO"],
        default="AUTO",
        help="Format hint for CSV parsing (default: AUTO-detect)",
    )

    parser.add_argument(
        "--output", required=True, type=Path, help="Output path for processed baseline JSON"
    )

    parser.add_argument("--validate", action="store_true", help="Run schema validation")

    parser.add_argument("--transform-coords", action="store_true", help="Add WGS84 coordinates")

    parser.add_argument(
        "--reconstruct-routes", action="store_true", help="Infer pole sequences from coordinates"
    )

    parser.add_argument(
        "--normalize-support-numbers", action="store_true", help="Normalize support numbers"
    )

    parser.add_argument(
        "--strict", action="store_true", help="Fail on validation errors (default: warn only)"
    )

    parser.add_argument("--report", type=Path, help="Generate validation report (markdown)")

    parser.add_argument(
        "--log-level",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        default="INFO",
        help="Logging level",
    )

    return parser.parse_args()


def main():
    """Main CLI entry point."""
    args = parse_arguments()

    # Set logging level
    logging.getLogger().setLevel(getattr(logging, args.log_level))

    logger.info("Starting baseline ingestion")
    logger.info(f"Input: {args.input}")
    logger.info(f"Output: {args.output}")

    try:
        # Parse CSV
        logger.info("Parsing CSV...")
        parser = CSVParser()
        format_hint = None if args.format == "AUTO" else args.format
        dataset = parser.parse(args.input, format_hint=format_hint)
        logger.info(f"Parsed {dataset.pole_count} poles")

        # Normalize support numbers
        if args.normalize_support_numbers:
            logger.info("Normalizing support numbers...")
            normalizer = SupportNumberNormalizer()
            for pole in dataset.poles:
                if pole.support_no:
                    pole.support_no = normalizer.normalize(pole.support_no)

        # Transform coordinates
        if args.transform_coords:
            logger.info("Transforming coordinates to WGS84...")
            try:
                transformer = CoordinateTransformer()
                dataset = transformer.transform_dataset(dataset)
                logger.info(f"Transformed {dataset.pole_count} poles")
            except ImportError:
                logger.warning("pyproj not available, skipping coordinate transformation")

        # Reconstruct routes
        if args.reconstruct_routes:
            logger.info("Reconstructing routes...")
            reconstructor = RouteReconstructor()
            dataset = reconstructor.reconstruct_sequences(dataset)
            logger.info(f"Reconstructed routes for {dataset.pole_count} poles")

        # Validate
        if args.validate:
            logger.info("Validating dataset...")
            validator = SchemaValidator()
            validation_report = validator.validate_dataset(dataset)
            dataset.validation_report = validation_report

            logger.info(
                f"Validation: {validation_report.valid_poles} valid, {validation_report.error_count} errors, {validation_report.warning_count} warnings"
            )

            # Fail if errors and strict mode
            if not validation_report.is_valid and args.strict:
                logger.error("Validation failed (strict mode)")
                return 1

            # Generate markdown report
            if args.report:
                logger.info(f"Writing validation report to {args.report}")
                _write_validation_report(validation_report, args.report)

        # Write output JSON
        logger.info(f"Writing output to {args.output}")
        _write_output_json(dataset, args.output)

        logger.info("Baseline ingestion complete")
        return 0

    except Exception as e:
        logger.error(f"Error during ingestion: {e}", exc_info=True)
        return 1


def _write_output_json(dataset, output_path: Path):
    """Write dataset to JSON file."""
    output_path.parent.mkdir(parents=True, exist_ok=True)

    output_data = {
        "metadata": {
            "source_file": str(dataset.metadata.get("source_file", "")),
            "format_detected": dataset.metadata.get("format", "UNKNOWN"),
            "ingestion_date": datetime.now().isoformat(),
            "total_poles": dataset.pole_count,
            "has_coordinates": dataset.has_coordinates,
            "has_wgs84": dataset.has_wgs84,
            "has_routes": dataset.has_routes,
            "has_sequences": dataset.has_sequences,
        },
        "poles": [pole.model_dump(exclude_none=False) for pole in dataset.poles],
        "validation_report": None,
    }

    if dataset.validation_report:
        output_data["metadata"]["valid_poles"] = dataset.validation_report.valid_poles
        output_data["metadata"]["validation_errors"] = dataset.validation_report.error_count
        output_data["metadata"]["validation_warnings"] = dataset.validation_report.warning_count
        output_data["validation_report"] = dataset.validation_report.model_dump()

    with open(output_path, "w") as f:
        json.dump(output_data, f, indent=2, default=str)


def _write_validation_report(validation_report, report_path: Path):
    """Write validation report as markdown."""
    report_path.parent.mkdir(parents=True, exist_ok=True)

    lines = []
    lines.append("# Baseline Validation Report")
    lines.append("")
    lines.append("## Summary")
    lines.append(f"- **Total Poles**: {validation_report.total_poles}")
    lines.append(f"- **Valid Poles**: {validation_report.valid_poles}")
    lines.append(f"- **Valid with Warnings**: {validation_report.valid_with_warnings}")
    lines.append(f"- **Errors**: {validation_report.error_count}")
    lines.append(f"- **Warnings**: {validation_report.warning_count}")
    lines.append(f"- **Status**: {'✅ PASS' if validation_report.is_valid else '❌ FAIL'}")
    lines.append("")

    if validation_report.errors:
        lines.append("## Errors")
        for error in validation_report.errors:
            lines.append(f"- {error}")
        lines.append("")

    if validation_report.warnings:
        lines.append("## Warnings")
        for warning in validation_report.warnings:
            lines.append(f"- {warning}")
        lines.append("")

    if validation_report.issues:
        lines.append("## Issues by Pole")
        lines.append("")
        lines.append("| Pole ID | Field | Issue | Severity | Message |")
        lines.append("|---------|-------|-------|----------|---------|")
        for issue in validation_report.issues:
            lines.append(
                f"| {issue.pole_id} | {issue.field} | {issue.issue_type} | {issue.severity} | {issue.message} |"
            )
        lines.append("")

    with open(report_path, "w") as f:
        f.write("\n".join(lines))


if __name__ == "__main__":
    sys.exit(main())
