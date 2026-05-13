#!/usr/bin/env python3
"""
Generate final Stage 4B verdict document.

Reads match register CSV, calculates statistics, and populates
the Stage 4B verdict template with actual data.
"""

import csv
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List


def load_register(csv_path: Path) -> List[Dict]:
    """Load match register CSV"""
    if not csv_path.exists():
        print(f"ERROR: Match register not found: {csv_path}")
        sys.exit(1)

    records = []
    with open(csv_path, "r") as f:
        reader = csv.DictReader(f)
        for row in reader:
            records.append(row)

    return records


def calculate_statistics(records: List[Dict]) -> Dict:
    """Calculate match rate statistics"""
    total = len(records)

    if total == 0:
        print("ERROR: No records found in match register")
        sys.exit(1)

    high_count = sum(1 for r in records if r["match_confidence"] == "HIGH")
    medium_count = sum(1 for r in records if r["match_confidence"] == "MEDIUM")
    low_count = sum(1 for r in records if r["match_confidence"] == "LOW")

    match_rate = ((high_count + medium_count) / total * 100) if total > 0 else 0

    # Count evidence
    review_required = sum(1 for r in records if r.get("review_required") == "yes")
    map_popup_present = sum(1 for r in records if r.get("map_popup_present") == "yes")

    # Count total photos and screenshots
    total_photos = sum(int(r.get("field_photo_count", 0)) for r in records)
    total_screenshots = sum(int(r.get("map_screenshot_count", 0)) for r in records)

    photo_counts = [int(r.get("field_photo_count", 0)) for r in records]
    screenshot_counts = [int(r.get("map_screenshot_count", 0)) for r in records]

    avg_photos = total_photos / total if total > 0 else 0
    avg_screenshots = total_screenshots / total if total > 0 else 0

    return {
        "total": total,
        "high_count": high_count,
        "medium_count": medium_count,
        "low_count": low_count,
        "high_pct": (high_count / total * 100) if total > 0 else 0,
        "medium_pct": (medium_count / total * 100) if total > 0 else 0,
        "low_pct": (low_count / total * 100) if total > 0 else 0,
        "match_rate": match_rate,
        "review_required": review_required,
        "map_popup_present": map_popup_present,
        "total_photos": total_photos,
        "total_screenshots": total_screenshots,
        "avg_photos": avg_photos,
        "avg_screenshots": avg_screenshots,
        "min_photos": min(photo_counts) if photo_counts else 0,
        "max_photos": max(photo_counts) if photo_counts else 0,
        "min_screenshots": min(screenshot_counts) if screenshot_counts else 0,
        "max_screenshots": max(screenshot_counts) if screenshot_counts else 0,
    }


def determine_verdict(match_rate: float) -> str:
    """Determine verdict based on match rate"""
    if match_rate >= 80:
        return "GO"
    elif match_rate >= 70:
        return "CONDITIONAL GO"
    else:
        return "NO-GO"


def determine_status(match_rate: float) -> str:
    """Determine status text"""
    if match_rate >= 80:
        return "PASS"
    elif match_rate >= 70:
        return "CONDITIONAL PASS"
    else:
        return "FAIL"


def load_template(template_path: Path) -> str:
    """Load verdict template"""
    if not template_path.exists():
        print(f"ERROR: Template not found: {template_path}")
        sys.exit(1)

    with open(template_path, "r") as f:
        return f.read()


def populate_template(template: str, stats: Dict) -> str:
    """Populate template placeholders with actual data"""
    now = datetime.now()
    today = now.strftime("%Y-%m-%d")
    now_full = now.strftime("%Y-%m-%d %H:%M")

    verdict = determine_verdict(stats["match_rate"])
    status = determine_status(stats["match_rate"])

    result = template

    # Replace basic counts (handle multiple [X] carefully in order of specificity)
    replacements = {
        "- **Total Poles**: [X]": f"- **Total Poles**: {stats['total']}",
        "- **Match Rate**: [XX.X%]": f"- **Match Rate**: {stats['match_rate']:.1f}%",
        "- **Verdict**: [GO / CONDITIONAL GO / NO-GO]": f"- **Verdict**: {verdict}",
        "- **Analysis Date**: [YYYY-MM-DD]": f"- **Analysis Date**: {today}",
        "- **HIGH confidence**: [X] poles ([XX.X%])": f"- **HIGH confidence**: {stats['high_count']} poles ({stats['high_pct']:.1f}%)",
        "- **MEDIUM confidence**: [X] poles ([XX.X%])": f"- **MEDIUM confidence**: {stats['medium_count']} poles ({stats['medium_pct']:.1f}%)",
        "- **LOW confidence**: [X] poles ([XX.X%])": f"- **LOW confidence**: {stats['low_count']} poles ({stats['low_pct']:.1f}%)",
        "= ([X] + [X]) / [X] * 100%": f"= ({stats['high_count']} + {stats['medium_count']}) / {stats['total']} * 100%",
        "= [XX.X%]": f"= {stats['match_rate']:.1f}%",
        "- **Target**: ≥80% match rate\n- **Actual**: [XX.X%]\n- **Status**: [PASS / CONDITIONAL PASS / FAIL]": f"- **Target**: ≥80% match rate\n- **Actual**: {stats['match_rate']:.1f}%\n- **Status**: {status}",
        "- **Field photos**: [X] total (avg [X] per pole, range [X-X])": f"- **Field photos**: {stats['total_photos']} total (avg {stats['avg_photos']:.1f} per pole, range {stats['min_photos']}-{stats['max_photos']})",
        "- **Map screenshots**: [X] total (avg [X] per pole, range [X-X])": f"- **Map screenshots**: {stats['total_screenshots']} total (avg {stats['avg_screenshots']:.1f} per pole, range {stats['min_screenshots']}-{stats['max_screenshots']})",
        "- **Map popup present**: [X/X] poles": f"- **Map popup present**: {stats['map_popup_present']}/{stats['total']} poles",
        "- **Date**: [YYYY-MM-DD HH:MM]": f"- **Date**: {now_full}",
        "- **Next Phase**: [Stage 4C / Phase 4 Pilot / Revision]": "- **Next Phase**: Stage 4C",
    }

    for pattern, replacement in replacements.items():
        result = result.replace(pattern, replacement)

    # Replace remaining individual placeholders in verdict justification
    result = result.replace("[XX.X%]", f"{stats['match_rate']:.1f}%")
    result = result.replace("[X/X]", f"{stats['high_count']}/{stats['total']}")
    result = result.replace("[XX%]", f"{stats['high_pct']:.1f}%")

    # Remove non-matching conditional sections
    result = remove_conditional_sections(result, verdict)

    # Handle remaining date replacements
    result = result.replace("[YYYY-MM-DD]", today)

    return result


def remove_conditional_sections(text: str, verdict: str) -> str:
    """Remove non-matching conditional verdict sections"""
    lines = text.split("\n")
    result = []
    skip_until_next_section = False
    remove_sections = []

    # Determine which sections to remove (both formats)
    if verdict == "GO":
        remove_sections = [
            "### If Match Rate 70-79%",
            "### If Match Rate <70%",
            "### If CONDITIONAL PASS:",
            "### If FAIL:",
        ]
    elif verdict == "CONDITIONAL GO":
        remove_sections = [
            "### If Match Rate ≥80%",
            "### If Match Rate <70%",
            "### If PASS:",
            "### If FAIL:",
        ]
    else:  # NO-GO
        remove_sections = [
            "### If Match Rate ≥80%",
            "### If Match Rate 70-79%",
            "### If PASS:",
            "### If CONDITIONAL PASS:",
        ]

    i = 0
    while i < len(lines):
        line = lines[i]

        # Check if this line starts a section to remove
        should_remove = False
        for remove_section in remove_sections:
            if remove_section in line:
                should_remove = True
                break

        if should_remove:
            skip_until_next_section = True
            i += 1
            continue

        # Check if this line starts a new section (and we're skipping)
        if skip_until_next_section:
            if line.startswith("###") or line.startswith("##"):
                skip_until_next_section = False

        # Add line if not skipping
        if not skip_until_next_section:
            result.append(line)

        i += 1

    return "\n".join(result)


def main():
    # Paths
    register_path = Path("real_pilot_data/P_LOCAL_001/baseline_field_match_register.csv")
    template_path = Path("AI_CONTROL/101_STAGE4B_VERDICT_TEMPLATE.md")
    output_path = Path("AI_CONTROL/101_STAGE4B_VERDICT.md")

    # Load and analyze
    print("Loading match register...")
    records = load_register(register_path)
    stats = calculate_statistics(records)

    # Load template
    print("Loading template...")
    template = load_template(template_path)

    # Populate
    print("Populating template...")
    verdict_doc = populate_template(template, stats)

    # Save
    print(f"Saving verdict to {output_path}...")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w") as f:
        f.write(verdict_doc)

    # Summary
    verdict = determine_verdict(stats["match_rate"])
    print("\n" + "=" * 70)
    print("STAGE 4B VERDICT GENERATED")
    print("=" * 70)
    print("Dataset: P_LOCAL_001 (10 poles)")
    print(f"Match Rate: {stats['match_rate']:.1f}%")
    print(f"Verdict: {verdict}")
    print(f"Output: {output_path}")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    main()
