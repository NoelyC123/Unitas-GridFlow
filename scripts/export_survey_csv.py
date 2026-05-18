#!/usr/bin/env python3
# ruff: noqa: E402
"""Export survey evidence CSV."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from gridflow.exports import SurveyCSVExporter
from gridflow.exports.excel_exporter import POLES_COLUMNS


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Export survey evidence to CSV.")
    parser.add_argument("--survey", required=True, help="Survey root")
    parser.add_argument("--trace", required=True, help="ENWL trace GeoJSON path")
    parser.add_argument("--output", required=True, help="Output CSV path")
    args = parser.parse_args(argv)

    bundle = SurveyCSVExporter().export(args.survey, args.trace, args.output)
    print(f"Export complete: {args.output}")
    print(f"Poles: {bundle.total_poles}")
    print(f"Columns: {len(POLES_COLUMNS)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
