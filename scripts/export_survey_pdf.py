#!/usr/bin/env python3
# ruff: noqa: E402
"""Export survey evidence PDF."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from gridflow.exports import SurveyPDFExporter


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Export survey evidence to PDF.")
    parser.add_argument("--survey", required=True, help="Survey root")
    parser.add_argument("--trace", required=True, help="ENWL trace GeoJSON path")
    parser.add_argument("--output", required=True, help="Output .pdf path")
    args = parser.parse_args(argv)

    bundle = SurveyPDFExporter().export(args.survey, args.trace, args.output)
    print(f"Export complete: {args.output}")
    print(f"Poles: {bundle.total_poles}")
    print("Pages: 2+")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
