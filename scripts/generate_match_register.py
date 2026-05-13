#!/usr/bin/env python3
"""
Generate baseline-field match register from enrichment dataset.

Reads pole folders from enwl_enrichment_clean and creates a CSV register
with automated initial match confidence scoring.
"""

import csv
import sys
from argparse import ArgumentParser
from pathlib import Path
from typing import Dict, List, Tuple


def extract_support_number(folder_name: str) -> str:
    """Extract support number from folder name pattern NN_SUPPORT_XXXXXX*"""
    parts = folder_name.split("_")
    if len(parts) >= 3 and parts[1].upper() == "SUPPORT":
        return parts[2]  # Just the support number part
    return None


def count_files_in_dir(directory: Path, extensions: Tuple[str, ...]) -> int:
    """Count files with given extensions in directory"""
    if not directory.exists():
        return 0
    count = 0
    for ext in extensions:
        count += len(list(directory.glob(f"*{ext}")))
    return count


def has_files_in_dir(directory: Path, extensions: Tuple[str, ...]) -> bool:
    """Check if directory has any files with given extensions"""
    return count_files_in_dir(directory, extensions) > 0


def determine_match_confidence(photo_count: int, screenshot_count: int, notes_present: bool) -> str:
    """Determine match confidence based on evidence"""
    requirements_met = sum([photo_count >= 3, screenshot_count >= 1, notes_present])

    if requirements_met == 3:
        return "HIGH"
    elif requirements_met == 2:
        return "MEDIUM"
    else:
        return "LOW"


def determine_map_popup_present(folder_name: str) -> str:
    """Determine if map popup is present based on folder name"""
    if "NO_POLE_POPUP" in folder_name.upper():
        return "uncertain"
    return "yes"


def process_dataset(dataset_path: Path) -> List[Dict]:
    """Process enrichment dataset and return list of match records"""
    records = []

    if not dataset_path.exists():
        print(f"ERROR: Dataset path does not exist: {dataset_path}")
        sys.exit(1)

    # Find all pole folders
    pole_folders = sorted(
        [f for f in dataset_path.iterdir() if f.is_dir() and not f.name.startswith(".")]
    )

    for pole_folder in pole_folders:
        folder_name = pole_folder.name

        # Extract support number
        support_no = extract_support_number(folder_name)
        if not support_no:
            continue

        # Count evidence
        field_photos_dir = pole_folder / "field_photos"
        photo_count = count_files_in_dir(
            field_photos_dir, (".jpg", ".jpeg", ".heic", ".JPG", ".JPEG", ".HEIC")
        )

        map_screenshots_dir = pole_folder / "map_screenshots"
        screenshot_count = count_files_in_dir(
            map_screenshots_dir, (".png", ".jpg", ".jpeg", ".PNG", ".JPG", ".JPEG")
        )

        notes_dir = pole_folder / "notes"
        notes_present = has_files_in_dir(notes_dir, (".txt", ".TXT"))

        # Determine confidence
        match_confidence = determine_match_confidence(photo_count, screenshot_count, notes_present)

        # Determine map popup
        map_popup_present = determine_map_popup_present(folder_name)

        # Determine review required
        review_required = "yes" if match_confidence in ["MEDIUM", "LOW"] else "no"

        # Build record
        record = {
            "support_no": support_no,
            "pole_folder": folder_name,
            "field_photo_count": photo_count,
            "map_screenshot_count": screenshot_count,
            "notes_present": "yes" if notes_present else "no",
            "match_confidence": match_confidence,
            "identity_verified": "",
            "top_visible": "",
            "base_visible": "",
            "warning_sign_visible": "",
            "equipment_match": "",
            "map_popup_present": map_popup_present,
            "review_required": review_required,
        }
        records.append(record)

    return records


def write_csv(records: List[Dict], output_path: Path) -> None:
    """Write records to CSV file"""
    fieldnames = [
        "support_no",
        "pole_folder",
        "field_photo_count",
        "map_screenshot_count",
        "notes_present",
        "match_confidence",
        "identity_verified",
        "top_visible",
        "base_visible",
        "warning_sign_visible",
        "equipment_match",
        "map_popup_present",
        "review_required",
    ]

    # Ensure output directory exists
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, "w", newline="") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(records)


def print_summary(records: List[Dict], output_path: Path) -> None:
    """Print validation summary"""
    high_count = sum(1 for r in records if r["match_confidence"] == "HIGH")
    medium_count = sum(1 for r in records if r["match_confidence"] == "MEDIUM")
    low_count = sum(1 for r in records if r["match_confidence"] == "LOW")
    review_count = sum(1 for r in records if r["review_required"] == "yes")

    print("\n" + "=" * 70)
    print("MATCH REGISTER GENERATION SUMMARY")
    print("=" * 70)

    print(f"\n{'PROCESSING RESULTS':-^70}")
    print(f"Total poles processed: {len(records)}")

    print(f"\n{'CONFIDENCE DISTRIBUTION':-^70}")
    print(f"HIGH confidence (ready for immediate use): {high_count}")
    print(f"MEDIUM confidence (needs 1 item verified): {medium_count}")
    print(f"LOW confidence (needs 2+ items verified): {low_count}")

    print(f"\n{'REVIEW REQUIREMENTS':-^70}")
    print(f"Poles requiring manual review: {review_count}/{len(records)}")

    print(f"\n{'OUTPUT':-^70}")
    print(f"Match register saved to: {output_path}")

    print("=" * 70 + "\n")


def main():
    parser = ArgumentParser(
        description="Generate baseline-field match register from enrichment dataset"
    )
    parser.add_argument(
        "--dataset-path",
        default="real_pilot_data/P_LOCAL_001/enwl_enrichment_clean",
        help="Path to enrichment dataset (default: real_pilot_data/P_LOCAL_001/enwl_enrichment_clean)",
    )

    args = parser.parse_args()
    dataset_path = Path(args.dataset_path)

    # Process dataset
    records = process_dataset(dataset_path)

    # Default output path
    output_path = Path("real_pilot_data/P_LOCAL_001/baseline_field_match_register.csv")

    # Write CSV
    write_csv(records, output_path)

    # Print summary
    print_summary(records, output_path)


if __name__ == "__main__":
    main()
