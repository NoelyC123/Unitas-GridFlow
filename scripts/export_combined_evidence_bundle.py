#!/usr/bin/env python3
# ruff: noqa: E402
"""Export combined evidence records for selected poles."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from gridflow.evidence_combiner import DESIGN_READINESS_CAUTION, combine_pole_evidence


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Export a JSON combined-evidence bundle for selected P_LOCAL poles."
    )
    parser.add_argument(
        "--survey", required=True, help="Survey root, e.g. real_pilot_data/P_LOCAL_002"
    )
    parser.add_argument("--trace", required=True, help="ENWL trace GeoJSON path")
    parser.add_argument("--poles", nargs="+", required=True, help="Pole folder names to export")
    parser.add_argument("--output-dir", required=True, help="Directory to write bundle files")
    args = parser.parse_args(argv)

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    records = []
    for pole in args.poles:
        record = combine_pole_evidence(args.survey, pole, args.trace)
        records.append(record)
        output_path = output_dir / f"{pole}_combined_evidence.json"
        output_path.write_text(
            json.dumps(record, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
        )

    summary = build_bundle_summary(records, args.survey, args.trace)
    summary_path = output_dir / "bundle_summary.md"
    summary_path.write_text(summary, encoding="utf-8")

    print(f"Exported {len(records)} combined evidence records to {output_dir}")
    for record in records:
        print(
            f"- {record['pole_id']}: support {record.get('support_no') or '-'}, "
            f"Level 2 equipment {len(record['direct_equipment_records'])}, "
            f"Level 3 conductors {len(record['route_conductor_evidence'])}"
        )
    print(f"Summary: {summary_path}")
    print(DESIGN_READINESS_CAUTION)
    return 0


def build_bundle_summary(records: list[dict], survey: str, trace: str) -> str:
    lines = [
        "# Combined Evidence Bundle Summary",
        "",
        f"**Survey:** `{survey}`",
        f"**Trace:** `{trace}`",
        "",
        "| Pole | Support | Pole FID | Level 2 Equipment | Level 3 Conductors | Level 4 Context |",
        "|---|---|---|---:|---:|---:|",
    ]
    for record in records:
        lines.append(
            "| "
            f"{record['pole_id']} | "
            f"{record.get('support_no') or '-'} | "
            f"{record.get('pole_fid') or '-'} | "
            f"{len(record['direct_equipment_records'])} | "
            f"{len(record['route_conductor_evidence'])} | "
            f"{len(record['nearby_context'])} |"
        )
    lines.extend(["", f"**Design-readiness caution:** {DESIGN_READINESS_CAUTION}", ""])
    return "\n".join(lines)


if __name__ == "__main__":
    raise SystemExit(main())
