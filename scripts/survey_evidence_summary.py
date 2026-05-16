#!/usr/bin/env python3
# ruff: noqa: E402
"""Print a conservative all-poles evidence summary for a survey."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from gridflow.evidence_combiner import DESIGN_READINESS_CAUTION, combine_pole_evidence

CHECK = "✓"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Summarise combined evidence quality for all pole folders in a survey."
    )
    parser.add_argument(
        "--survey", required=True, help="Survey root, e.g. real_pilot_data/P_LOCAL_002"
    )
    parser.add_argument("--trace", required=True, help="ENWL trace GeoJSON path")
    args = parser.parse_args(argv)

    records = collect_survey_records(Path(args.survey), Path(args.trace))
    print_summary(records)
    return 0


def collect_survey_records(survey_root: Path, trace_path: Path) -> list[dict]:
    pole_root = survey_root / "enwl_enrichment_clean"
    if not pole_root.exists():
        raise FileNotFoundError(f"Survey evidence folder not found: {pole_root}")

    pole_folders = sorted(
        [path.name for path in pole_root.iterdir() if path.is_dir() and "_SUPPORT_" in path.name],
        key=_pole_sort_key,
    )
    records = []
    for pole_folder in pole_folders:
        records.append(combine_pole_evidence(survey_root, pole_folder, trace_path))
    return records


def print_summary(records: list[dict]) -> None:
    print("# Survey Evidence Summary")
    print()
    print(
        "| Pole | Support | FID | Level 1 | Level 2 Equipment | "
        "Level 3 Conductors | Level 4 Context | Evidence Quality |"
    )
    print(
        "|------|---------|-----|---------|-------------------|--------------------|-----------------|-----------------|"
    )

    for record in records:
        print(
            "| "
            f"{_pole_index(record['pole_id'])} | "
            f"{record.get('support_no') or '-'} | "
            f"{record.get('pole_fid') or '-'} | "
            f"{CHECK if has_level1(record) else 'Missing'} | "
            f"{equipment_summary(record['direct_equipment_records'])} | "
            f"{count_summary(record['route_conductor_evidence'], 'record')} | "
            f"{count_summary(record['nearby_context'], 'record')} | "
            f"{evidence_quality(record)} |"
        )

    print()
    print(f"Total poles processed: {len(records)}")
    print(
        f"Poles with direct equipment links (Level 2): {sum(bool(r['direct_equipment_records']) for r in records)}"
    )
    print(
        f"Poles with route conductor evidence (Level 3): {sum(bool(r['route_conductor_evidence']) for r in records)}"
    )
    print(
        f"Poles with no ENWL evidence beyond identity: {sum(no_enwl_relationship_evidence(r) for r in records)}"
    )
    print(f"GREEN poles: {', '.join(quality_poles(records, 'GREEN')) or 'None'}")
    print(f"AMBER poles: {', '.join(quality_poles(records, 'AMBER')) or 'None'}")
    print(f"RED poles: {', '.join(quality_poles(records, 'RED')) or 'None'}")
    print()
    print(f"Design-readiness caution: {DESIGN_READINESS_CAUTION}")


def evidence_quality(record: dict) -> str:
    if not has_level1(record):
        return "RED"
    if record["direct_equipment_records"]:
        return "GREEN"
    return "AMBER"


def has_level1(record: dict) -> bool:
    return bool(record.get("support_no") and record.get("pole_fid") and record.get("spn"))


def equipment_summary(records: list[dict]) -> str:
    if not records:
        return "None"
    labels = []
    for record in records:
        labels.append(f"{equipment_label(record)} (FID {record.get('fid') or '-'})")
    return "; ".join(labels)


def equipment_label(record: dict) -> str:
    text = " ".join(
        str(value or "")
        for value in (record.get("feature_type"), record.get("spn"), record.get("source_section"))
    ).lower()
    if "fault section" in text or "fsl" in text or "fuse" in text:
        return "FSL switch"
    if "fault making" in text or "abs" in text or "isolator" in text:
        return "ABS switch"
    if "transformer" in text:
        return "Transformer"
    if "link" in text:
        return "HV link"
    return record.get("feature_type") or "Equipment"


def count_summary(records: list[dict], noun: str) -> str:
    count = len(records)
    if count == 0:
        return "None"
    suffix = noun if count == 1 else f"{noun}s"
    return f"{count} {suffix}"


def no_enwl_relationship_evidence(record: dict) -> bool:
    return not (
        record["direct_equipment_records"]
        or record["route_conductor_evidence"]
        or record["nearby_context"]
    )


def quality_poles(records: list[dict], quality: str) -> list[str]:
    return [record["pole_id"] for record in records if evidence_quality(record) == quality]


def _pole_index(pole_id: str) -> str:
    return pole_id.split("_", 1)[0]


def _pole_sort_key(pole_id: str) -> tuple[int, str]:
    prefix = _pole_index(pole_id)
    return (int(prefix) if prefix.isdigit() else 999, pole_id)


if __name__ == "__main__":
    raise SystemExit(main())
