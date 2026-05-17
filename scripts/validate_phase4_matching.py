#!/usr/bin/env python3
"""Validate Phase 4 field-to-baseline matching for P_LOCAL_002-style datasets."""

from __future__ import annotations

import argparse
import csv
import json
import sys
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_BASELINE = (
    REPO_ROOT / "real_pilot_data" / "P_LOCAL_002" / "csv" / "P_LOCAL_002_baseline.csv"
)
DEFAULT_FIELD_DIR = REPO_ROOT / "real_pilot_data" / "P_LOCAL_002" / "enwl_enrichment_clean"
DEFAULT_OUTPUT = REPO_ROOT / "validation_runs" / "P_LOCAL_002_phase4_validation.json"
IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".heic", ".heif"}


@dataclass
class PoleValidationResult:
    pole_id: str
    baseline_voltage: str
    folder_name: str | None
    matched: bool
    evidence_complete: bool
    field_photo_count: int
    enwl_screenshot_count: int
    map_screenshot_count: int
    note_file_count: int
    flags: list[str]


def load_baseline(csv_path: Path) -> list[dict[str, str]]:
    if not csv_path.exists():
        raise FileNotFoundError(f"Baseline CSV not found: {csv_path}")

    with csv_path.open("r", newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        rows = list(reader)

    if not rows:
        raise ValueError(f"Baseline CSV is empty: {csv_path}")

    required = {"pole_id", "voltage"}
    missing = required.difference(reader.fieldnames or [])
    if missing:
        raise ValueError(f"Baseline CSV missing columns: {', '.join(sorted(missing))}")

    return rows


def count_files(folder: Path) -> int:
    if not folder.exists():
        return 0
    return sum(1 for p in folder.iterdir() if p.is_file() and p.suffix.lower() in IMAGE_EXTENSIONS)


def count_note_files(folder: Path) -> int:
    if not folder.exists():
        return 0
    return sum(1 for p in folder.iterdir() if p.is_file())


def build_field_index(field_root: Path) -> dict[str, Path]:
    if not field_root.exists():
        raise FileNotFoundError(f"Field evidence directory not found: {field_root}")

    index: dict[str, Path] = {}
    for child in sorted(field_root.iterdir()):
        if not child.is_dir():
            continue
        parts = child.name.split("SUPPORT_", 1)
        if len(parts) != 2:
            continue
        support_suffix = parts[1]
        pole_id = support_suffix.split("_", 1)[0].strip()
        if pole_id:
            index[pole_id] = child
    return index


def validate_pole(
    baseline_row: dict[str, str], field_index: dict[str, Path]
) -> PoleValidationResult:
    pole_id = str(baseline_row.get("pole_id", "")).strip()
    voltage = str(baseline_row.get("voltage", "")).strip()
    folder = field_index.get(pole_id)
    flags: list[str] = []

    if folder is None:
        flags.append("FIELD_FOLDER_MISSING")
        return PoleValidationResult(
            pole_id=pole_id,
            baseline_voltage=voltage,
            folder_name=None,
            matched=False,
            evidence_complete=False,
            field_photo_count=0,
            enwl_screenshot_count=0,
            map_screenshot_count=0,
            note_file_count=0,
            flags=flags,
        )

    field_photo_count = count_files(folder / "field_photos")
    enwl_screenshot_count = count_files(folder / "enwl_screenshots")
    map_screenshot_count = count_files(folder / "map_screenshots")
    note_file_count = count_note_files(folder / "notes")

    if field_photo_count == 0:
        flags.append("FIELD_PHOTOS_MISSING")
    if enwl_screenshot_count == 0:
        flags.append("ENWL_SCREENSHOTS_MISSING")
    if map_screenshot_count == 0:
        flags.append("MAP_SCREENSHOTS_MISSING")
    if note_file_count == 0:
        flags.append("NOTES_MISSING")

    evidence_complete = field_photo_count > 0 and enwl_screenshot_count > 0

    return PoleValidationResult(
        pole_id=pole_id,
        baseline_voltage=voltage,
        folder_name=folder.name,
        matched=True,
        evidence_complete=evidence_complete,
        field_photo_count=field_photo_count,
        enwl_screenshot_count=enwl_screenshot_count,
        map_screenshot_count=map_screenshot_count,
        note_file_count=note_file_count,
        flags=flags,
    )


def relative_to_repo(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(REPO_ROOT))
    except ValueError:
        return str(path.resolve())


def write_results(
    output_path: Path,
    *,
    baseline_csv: Path,
    field_root: Path,
    results: list[PoleValidationResult],
    match_rate: float,
) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    payload: dict[str, Any] = {
        "generated_at_utc": datetime.now(UTC).isoformat(),
        "baseline_csv": relative_to_repo(baseline_csv),
        "field_evidence_dir": relative_to_repo(field_root),
        "total_poles": len(results),
        "matched_poles": sum(1 for result in results if result.matched),
        "complete_evidence_poles": sum(1 for result in results if result.evidence_complete),
        "match_rate_percent": round(match_rate, 2),
        "results": [asdict(result) for result in results],
    }
    output_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def print_results(
    results: list[PoleValidationResult], match_rate: float, output_path: Path
) -> None:
    print("=" * 72)
    print("PHASE 4 FIELD-TO-BASELINE MATCHING VALIDATION")
    print("=" * 72)
    for result in results:
        status = "MATCHED" if result.matched else "MISSING"
        completeness = "COMPLETE" if result.evidence_complete else "INCOMPLETE"
        print(
            f"{result.pole_id:8s}  {status:7s}  {completeness:10s}  "
            f"photos={result.field_photo_count:2d}  "
            f"enwl={result.enwl_screenshot_count:2d}  "
            f"maps={result.map_screenshot_count:2d}  "
            f"notes={result.note_file_count:2d}"
        )
        if result.flags:
            print(f"           flags: {', '.join(result.flags)}")
        elif not result.evidence_complete:
            print("           flags: evidence incomplete")
    print("-" * 72)
    matched = sum(1 for result in results if result.matched)
    total = len(results)
    print(f"Matched poles: {matched}/{total}")
    print(f"Match rate: {match_rate:.2f}%")
    print(f"JSON results: {output_path}")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate Phase 4 field-to-baseline matching for baseline CSV vs field evidence."
    )
    parser.add_argument(
        "--baseline-csv",
        default=str(DEFAULT_BASELINE),
        help="Path to baseline CSV (default: P_LOCAL_002 baseline CSV).",
    )
    parser.add_argument(
        "--field-evidence-dir",
        default=str(DEFAULT_FIELD_DIR),
        help="Path to field evidence root folder (default: P_LOCAL_002 enwl_enrichment_clean).",
    )
    parser.add_argument(
        "--output",
        default=str(DEFAULT_OUTPUT),
        help="Path to JSON output file (default: validation_runs/P_LOCAL_002_phase4_validation.json).",
    )
    args = parser.parse_args()

    baseline_csv = Path(args.baseline_csv)
    field_root = Path(args.field_evidence_dir)
    output_path = Path(args.output)

    try:
        baseline_rows = load_baseline(baseline_csv)
        field_index = build_field_index(field_root)
        results = [validate_pole(row, field_index) for row in baseline_rows]
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    matched_poles = sum(1 for result in results if result.matched)
    total_poles = len(results)
    match_rate = (matched_poles / total_poles * 100.0) if total_poles else 0.0

    write_results(
        output_path,
        baseline_csv=baseline_csv,
        field_root=field_root,
        results=results,
        match_rate=match_rate,
    )
    print_results(results, match_rate, output_path)

    # Requested for automation: return the integer match rate as process exit code.
    return int(round(match_rate))


if __name__ == "__main__":
    sys.exit(main())
