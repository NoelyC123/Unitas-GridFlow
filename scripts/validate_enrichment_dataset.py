#!/usr/bin/env python3
"""
Validate ENWL enrichment dataset structure and evidence requirements.

This script validates that each pole folder in the enrichment dataset contains:
- Minimum 3 field photos
- At least 1 map screenshot
- At least 1 notes file

It also validates folder naming pattern and checks for duplicate support numbers.
"""

import sys
from argparse import ArgumentParser
from pathlib import Path
from typing import Dict, Tuple


def extract_support_number(folder_name: str) -> str:
    """Extract support number from folder name pattern NN_SUPPORT_XXXXXX*"""
    parts = folder_name.split("_")
    if len(parts) >= 3 and parts[1].upper() == "SUPPORT":
        return "_".join(parts[2:])  # Everything after SUPPORT
    return None


def validate_folder_naming(folder_name: str) -> bool:
    """Validate folder follows pattern NN_SUPPORT_XXXXXX*"""
    parts = folder_name.split("_")
    if len(parts) < 3:
        return False
    if not parts[0].isdigit() or len(parts[0]) != 2:
        return False
    if parts[1].upper() != "SUPPORT":
        return False
    return True


def count_file_type(folder_path: Path, extensions: Tuple[str, ...]) -> int:
    """Count files with given extensions in folder (non-recursive)"""
    count = 0
    for ext in extensions:
        count += len(list(folder_path.glob(f"*{ext}")))
    return count


def validate_dataset(dataset_path: Path) -> Dict:
    """
    Validate enrichment dataset structure.

    Returns dict with validation results.
    """
    results = {
        "total_poles": 0,
        "poles_with_sufficient_photos": 0,
        "poles_with_map_screenshot": 0,
        "poles_with_notes": 0,
        "poles_with_all_requirements": 0,
        "poles_missing_photos": [],
        "poles_missing_screenshots": [],
        "poles_missing_notes": [],
        "naming_pattern_violations": [],
        "duplicate_support_numbers": [],
        "all_support_numbers": [],
    }

    if not dataset_path.exists():
        return {"error": f"Dataset path does not exist: {dataset_path}"}

    # Find all pole folders
    pole_folders = sorted([f for f in dataset_path.iterdir() if f.is_dir()])
    results["total_poles"] = len(pole_folders)

    support_number_counts = {}

    for pole_folder in pole_folders:
        folder_name = pole_folder.name

        # Validate naming pattern
        if not validate_folder_naming(folder_name):
            results["naming_pattern_violations"].append(folder_name)
            continue

        # Extract support number
        support_no = extract_support_number(folder_name)
        if support_no:
            results["all_support_numbers"].append((folder_name, support_no))
            support_number_counts[support_no] = support_number_counts.get(support_no, 0) + 1

        # Count photos (check root and field_photos/ subdirectory)
        photo_count = count_file_type(
            pole_folder, (".jpg", ".jpeg", ".heic", ".png", ".JPG", ".JPEG", ".HEIC", ".PNG")
        )
        field_photos_dir = pole_folder / "field_photos"
        if field_photos_dir.exists():
            photo_count += count_file_type(
                field_photos_dir,
                (".jpg", ".jpeg", ".heic", ".png", ".JPG", ".JPEG", ".HEIC", ".PNG"),
            )

        # Count screenshots (common screenshot naming)
        screenshot_count = count_file_type(
            pole_folder, (".png", ".jpg", ".jpeg", ".PNG", ".JPG", ".JPEG")
        )
        # More specific: look for "screenshot" or "map" in filenames
        screenshot_count = len(list(pole_folder.glob("*screenshot*"))) + len(
            list(pole_folder.glob("*map*"))
        )
        if screenshot_count == 0:
            screenshot_count = len(list(pole_folder.glob("*.png"))) + len(
                list(pole_folder.glob("*.PNG"))
            )

        # Count notes files (check root and notes/ subdirectory)
        notes_count = count_file_type(pole_folder, (".txt", ".md", ".TXT", ".MD"))
        notes_dir = pole_folder / "notes"
        if notes_dir.exists():
            notes_count += len(list(notes_dir.glob("*.txt"))) + len(list(notes_dir.glob("*.TXT")))

        # Track compliance
        has_sufficient_photos = photo_count >= 3
        has_map_screenshot = screenshot_count >= 1
        has_notes = notes_count >= 1

        if has_sufficient_photos:
            results["poles_with_sufficient_photos"] += 1
        else:
            results["poles_missing_photos"].append((folder_name, photo_count))

        if has_map_screenshot:
            results["poles_with_map_screenshot"] += 1
        else:
            results["poles_missing_screenshots"].append((folder_name, screenshot_count))

        if has_notes:
            results["poles_with_notes"] += 1
        else:
            results["poles_missing_notes"].append((folder_name, notes_count))

        if has_sufficient_photos and has_map_screenshot and has_notes:
            results["poles_with_all_requirements"] += 1

    # Check for duplicate support numbers
    for support_no, count in support_number_counts.items():
        if count > 1:
            # Find folders with this support number
            folders = [f[0] for f in results["all_support_numbers"] if f[1] == support_no]
            results["duplicate_support_numbers"].append(
                {
                    "support_no": support_no,
                    "count": count,
                    "folders": folders,
                }
            )

    return results


def print_report(results: Dict) -> None:
    """Print formatted validation report."""
    print("\n" + "=" * 70)
    print("ENWL ENRICHMENT DATASET VALIDATION REPORT")
    print("=" * 70)

    if "error" in results:
        print(f"\nERROR: {results['error']}")
        return

    total = results["total_poles"]
    compliant = results["poles_with_all_requirements"]

    # Dataset overview
    print(f"\n{'DATASET OVERVIEW':-^70}")
    print(f"Total poles found: {total}")
    print(f"Poles meeting ALL requirements: {compliant}/{total}")
    if total > 0:
        compliance_pct = (compliant / total) * 100
        print(f"Overall compliance: {compliance_pct:.1f}%")

    # Evidence breakdown
    print(f"\n{'EVIDENCE REQUIREMENTS':-^70}")
    print(f"Poles with 3+ field photos: {results['poles_with_sufficient_photos']}/{total}")
    print(f"Poles with 1+ map screenshot: {results['poles_with_map_screenshot']}/{total}")
    print(f"Poles with 1+ notes file: {results['poles_with_notes']}/{total}")

    # Naming validation
    print(f"\n{'NAMING PATTERN VALIDATION':-^70}")
    if results["naming_pattern_violations"]:
        print("Folders NOT following NN_SUPPORT_XXXXXX* pattern:")
        for folder in results["naming_pattern_violations"]:
            print(f"  - {folder}")
    else:
        print("✓ All folders follow naming pattern NN_SUPPORT_XXXXXX*")

    # Duplicates
    print(f"\n{'DUPLICATE SUPPORT NUMBERS':-^70}")
    if results["duplicate_support_numbers"]:
        print(
            f"WARNING: Found {len(results['duplicate_support_numbers'])} duplicate support number(s):"
        )
        for dup in results["duplicate_support_numbers"]:
            print(f"  Support {dup['support_no']} appears {dup['count']} times in:")
            for folder in dup["folders"]:
                print(f"    - {folder}")
    else:
        print("✓ No duplicate support numbers detected")

    # Missing evidence details
    if results["poles_missing_photos"]:
        print(f"\n{'POLES MISSING SUFFICIENT PHOTOS':-^70}")
        for folder, count in results["poles_missing_photos"]:
            print(f"  {folder}: {count} photos (need 3+)")

    if results["poles_missing_screenshots"]:
        print(f"\n{'POLES MISSING MAP SCREENSHOTS':-^70}")
        for folder, count in results["poles_missing_screenshots"]:
            print(f"  {folder}: {count} screenshot(s) (need 1+)")

    if results["poles_missing_notes"]:
        print(f"\n{'POLES MISSING NOTES':-^70}")
        for folder, count in results["poles_missing_notes"]:
            print(f"  {folder}: {count} note file(s) (need 1+)")

    # Summary
    print(f"\n{'VALIDATION SUMMARY':-^70}")
    issues = (
        len(results["poles_missing_photos"])
        + len(results["poles_missing_screenshots"])
        + len(results["poles_missing_notes"])
        + len(results["naming_pattern_violations"])
        + len(results["duplicate_support_numbers"])
    )

    if issues == 0:
        print("✓ Dataset validation PASSED - all requirements met")
    else:
        print(f"✗ Dataset validation found {issues} issue(s)")

    print("=" * 70 + "\n")


def main():
    parser = ArgumentParser(description="Validate ENWL enrichment dataset structure")
    parser.add_argument(
        "dataset_path",
        nargs="?",
        default="real_pilot_data/P_LOCAL_001/enwl_enrichment_clean",
        help="Path to enrichment dataset (default: real_pilot_data/P_LOCAL_001/enwl_enrichment_clean)",
    )

    args = parser.parse_args()
    dataset_path = Path(args.dataset_path)

    results = validate_dataset(dataset_path)
    print_report(results)

    # Exit with appropriate code
    if "error" in results:
        sys.exit(1)
    elif (
        results.get("poles_with_all_requirements", 0) == results.get("total_poles", 0)
        and results["total_poles"] > 0
    ):
        sys.exit(0)  # All poles compliant
    else:
        sys.exit(1)  # Some issues found


if __name__ == "__main__":
    main()
