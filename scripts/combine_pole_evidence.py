#!/usr/bin/env python3
# ruff: noqa: E402
"""Combine a surveyed pole folder with ENWL trace evidence."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from gridflow.evidence_combiner import combine_pole_evidence


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Combine pole_notes.md, survey folder provenance, and ENWL trace "
            "GeoJSON into one conservative evidence record."
        )
    )
    parser.add_argument(
        "--survey", required=True, help="Survey root, e.g. real_pilot_data/P_LOCAL_002"
    )
    parser.add_argument("--pole", required=True, help="Pole folder name, e.g. 05_SUPPORT_900344")
    parser.add_argument("--trace", required=True, help="ENWL trace GeoJSON path")
    parser.add_argument("--output", help="Optional JSON output path")
    args = parser.parse_args(argv)

    record = combine_pole_evidence(args.survey, args.pole, args.trace)
    payload = json.dumps(record, indent=2, ensure_ascii=False)
    print(payload)

    if args.output:
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(payload + "\n", encoding="utf-8")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
