#!/usr/bin/env python3
"""
Calculate Stage 4B match rate from baseline-field match register.

Reads the match register CSV and generates a summary report
with verdict on Stage 4C authorization readiness.
"""

import csv
import sys
from argparse import ArgumentParser
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple


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

    identity_verified = sum(1 for r in records if r.get("identity_verified", "").strip())
    review_required = sum(1 for r in records if r.get("review_required") == "yes")
    map_popup_present = sum(1 for r in records if r.get("map_popup_present") == "yes")

    return {
        "total": total,
        "high_count": high_count,
        "medium_count": medium_count,
        "low_count": low_count,
        "high_pct": (high_count / total * 100) if total > 0 else 0,
        "medium_pct": (medium_count / total * 100) if total > 0 else 0,
        "low_pct": (low_count / total * 100) if total > 0 else 0,
        "match_rate": match_rate,
        "identity_verified": identity_verified,
        "review_required": review_required,
        "map_popup_present": map_popup_present,
    }


def determine_verdict(match_rate: float) -> Tuple[str, str]:
    """Determine verdict and recommendation based on match rate"""
    if match_rate >= 80:
        status = "PASS"
        verdict = """✅ PASS - Stage 4B validation successful
Match rate exceeds acceptance threshold.
Baseline-to-field correlation methodology validated.
Recommendation: Authorize Stage 4C runtime implementation."""
    elif match_rate >= 70:
        status = "CONDITIONAL PASS"
        verdict = """⚠️ CONDITIONAL PASS - Refinement recommended
Match rate acceptable but below optimal.
Recommendation: Review MEDIUM/LOW confidence poles, then re-evaluate."""
    else:
        status = "FAIL"
        verdict = """❌ FAIL - Significant matching issues
Match rate below acceptance threshold.
Recommendation: Root cause analysis required before Stage 4C."""

    return status, verdict


def format_report(stats: Dict, records: List[Dict], detailed: bool = False) -> str:
    """Format report as string"""
    status, verdict = determine_verdict(stats["match_rate"])

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    report = "=" * 70 + "\n"
    report += "STAGE 4B MATCH RATE ANALYSIS\n"
    report += "Dataset: P_LOCAL_001 ENWL Enrichment Clean\n"
    report += f"Analysis Date: {now}\n"
    report += f"Total Poles: {stats['total']}\n"

    report += "-" * 70 + "\n"
    report += "CONFIDENCE DISTRIBUTION\n"
    report += "-" * 70 + "\n"
    report += f"HIGH confidence:   {stats['high_count']:2d} poles ({stats['high_pct']:5.1f}%)\n"
    report += f"MEDIUM confidence: {stats['medium_count']:2d} poles ({stats['medium_pct']:5.1f}%)\n"
    report += f"LOW confidence:    {stats['low_count']:2d} poles ({stats['low_pct']:5.1f}%)\n"

    report += "\n"
    report += "-" * 70 + "\n"
    report += "MATCH RATE\n"
    report += "-" * 70 + "\n"
    report += f"Overall Match Rate: {stats['match_rate']:5.1f}%\n"
    report += "(HIGH + MEDIUM confidence matches)\n"
    report += "Acceptance Threshold: ≥80%\n"
    report += f"Status: {status}\n"

    report += "\n"
    report += "-" * 70 + "\n"
    report += "EVIDENCE QUALITY\n"
    report += "-" * 70 + "\n"
    report += f"Poles with map popup: {stats['map_popup_present']}/{stats['total']}\n"
    report += f"Poles requiring review: {stats['review_required']}/{stats['total']}\n"

    report += "\n"
    report += "-" * 70 + "\n"
    report += "VERDICT\n"
    report += "-" * 70 + "\n"
    report += verdict + "\n"

    # Optional detailed breakdown
    if detailed:
        report += "\n"
        report += "=" * 70 + "\n"
        report += "PER-POLE BREAKDOWN\n"
        report += "=" * 70 + "\n"
        for record in records:
            report += f"{record['support_no']:6s} {record['pole_folder']:40s} {record['match_confidence']:6s}\n"

    report += "=" * 70 + "\n"

    return report


def write_report(report: str, output_path: Path) -> None:
    """Write report to file"""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w") as f:
        f.write(report)


def write_csv_summary(stats: Dict, output_path: Path) -> None:
    """Write summary statistics as CSV"""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Metric", "Value"])
        writer.writerow(["Total Poles", stats["total"]])
        writer.writerow(["HIGH Confidence", stats["high_count"]])
        writer.writerow(["HIGH Confidence %", f"{stats['high_pct']:.1f}%"])
        writer.writerow(["MEDIUM Confidence", stats["medium_count"]])
        writer.writerow(["MEDIUM Confidence %", f"{stats['medium_pct']:.1f}%"])
        writer.writerow(["LOW Confidence", stats["low_count"]])
        writer.writerow(["LOW Confidence %", f"{stats['low_pct']:.1f}%"])
        writer.writerow(["Match Rate %", f"{stats['match_rate']:.1f}%"])
        writer.writerow(["Map Popup Present", stats["map_popup_present"]])
        writer.writerow(["Requiring Review", stats["review_required"]])


def main():
    parser = ArgumentParser(description="Calculate Stage 4B match rate and generate verdict")
    parser.add_argument(
        "--register-path",
        default="real_pilot_data/P_LOCAL_001/baseline_field_match_register.csv",
        help="Path to match register CSV",
    )
    parser.add_argument(
        "--detailed",
        action="store_true",
        help="Show per-pole breakdown",
    )
    parser.add_argument(
        "--csv",
        action="store_true",
        help="Also output summary statistics as CSV",
    )

    args = parser.parse_args()

    # Load and analyze
    register_path = Path(args.register_path)
    records = load_register(register_path)
    stats = calculate_statistics(records)

    # Generate report
    report = format_report(stats, records, detailed=args.detailed)
    print(report)

    # Save report
    output_path = Path("real_pilot_data/P_LOCAL_001/stage4b_match_rate_report.txt")
    write_report(report, output_path)
    print(f"Report saved to: {output_path}")

    # Optional CSV output
    if args.csv:
        csv_path = Path("real_pilot_data/P_LOCAL_001/stage4b_match_rate_summary.csv")
        write_csv_summary(stats, csv_path)
        print(f"CSV summary saved to: {csv_path}")


if __name__ == "__main__":
    main()
