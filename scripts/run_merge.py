#!/usr/bin/env python3
"""Stage 4C.4 Merge Engine CLI."""

import json
import logging
import sys
from argparse import ArgumentParser
from pathlib import Path

from gridflow.baseline.models import BaselineDataset, BaselinePole
from gridflow.field.models import FieldDataset, FieldPole
from gridflow.matching.models import MatchRegister, MatchRegisterEntry
from gridflow.merge import DataMerger, QAReportGenerator

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


def parse_args():
    p = ArgumentParser(description="Stage 4C.4 Merge Engine")
    p.add_argument("--baseline", required=True, type=Path)
    p.add_argument("--field", required=True, type=Path)
    p.add_argument("--register", required=True, type=Path)
    p.add_argument("--output", required=True, type=Path)
    p.add_argument("--report", type=Path)
    p.add_argument("--csv", type=Path)
    p.add_argument(
        "--log-level", choices=["DEBUG", "INFO", "WARNING", "ERROR"], default="INFO"
    )
    return p.parse_args()


def _load_baseline(path: Path) -> BaselineDataset:
    with open(path) as f:
        data = json.load(f)
    poles = [BaselinePole(**p) for p in data.get("poles", [])]
    return BaselineDataset(poles=poles, metadata=data.get("metadata", {}))


def _load_field(path: Path) -> FieldDataset:
    with open(path) as f:
        data = json.load(f)
    poles = [FieldPole(**p) for p in data.get("poles", [])]
    return FieldDataset(
        dataset_path=data.get("metadata", {}).get("source_path", ""),
        scan_date=data.get("metadata", {}).get("scan_date", ""),
        total_poles=len(poles),
        poles=poles,
        evidence_summary=data.get("evidence_summary", {}),
    )


def _load_register(path: Path) -> MatchRegister:
    with open(path) as f:
        data = json.load(f)
    entries = [MatchRegisterEntry(**e) for e in data.get("entries", [])]
    meta = data.get("metadata", {})
    return MatchRegister(
        baseline_total=meta.get("baseline_total", len(entries)),
        field_total=meta.get("field_total", 0),
        matched=meta.get("matched", 0),
        match_rate=meta.get("match_rate", 0.0),
        entries=entries,
    )


def main():
    args = parse_args()
    logging.getLogger().setLevel(getattr(logging, args.log_level))

    try:
        logger.info("Loading baseline: %s", args.baseline)
        baseline = _load_baseline(args.baseline)

        logger.info("Loading field evidence: %s", args.field)
        field = _load_field(args.field)

        logger.info("Loading match register: %s", args.register)
        register = _load_register(args.register)

        logger.info("Running merge...")
        merger = DataMerger()
        dataset = merger.merge(baseline, field, register)

        logger.info(
            "Merged: %d poles, %d design_ready, %d design_blocked",
            dataset.total_matched,
            dataset.design_ready_count,
            dataset.design_blocked_count,
        )

        # Write JSON output
        args.output.parent.mkdir(parents=True, exist_ok=True)
        with open(args.output, "w") as f:
            json.dump(dataset.model_dump(), f, indent=2, default=str)
        logger.info("Merged dataset written to %s", args.output)

        # QA report
        reporter = QAReportGenerator()
        if args.report:
            report_md = reporter.generate(dataset)
            args.report.parent.mkdir(parents=True, exist_ok=True)
            with open(args.report, "w") as f:
                f.write(report_md)
            logger.info("QA report written to %s", args.report)

        # CSV
        if args.csv:
            reporter.export_csv(dataset, args.csv)

        # Console summary
        print("\n" + "=" * 60)
        print("MERGE SUMMARY")
        print("=" * 60)
        print(f"Total merged poles:  {dataset.total_matched}")
        print(f"Design ready:        {dataset.design_ready_count}")
        print(f"Design blocked:      {dataset.design_blocked_count}")
        print(f"Review required:     {dataset.review_required_count}")
        print(f"HIGH confidence:     {dataset.high_confidence_count}")
        print(f"MEDIUM confidence:   {dataset.medium_confidence_count}")
        print(f"LOW confidence:      {dataset.low_confidence_count}")
        print("=" * 60)

        return 0

    except Exception as e:
        logger.error("Merge failed: %s", e, exc_info=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())
