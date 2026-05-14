#!/usr/bin/env python3
"""
Pre-Flight Check for Designer Review Session — Stage 5G

Verifies a registered GridFlow job is ready for a designer walk-through:
  1. Job directory and all expected files exist
  2. meta.json is valid and contains the correct job_id
  3. Flask routes return 200 (skipped gracefully if Flask is not running)

Usage:
    python scripts/preflight_designer_review.py <job_id>

Example:
    python scripts/preflight_designer_review.py P_LOCAL_DESIGNER_REVIEW
"""

import json
import sys
from pathlib import Path
from typing import List, Tuple

EXPECTED_FILES = [
    "meta.json",
    "pipeline_summary.json",
    "00_pilot_output_pack_index.md",
    "04_merged_dataset.json",
    "05_qa_report.md",
    "06_dno_data_request.md",
    "07_design_readiness_summary.md",
    "08_match_confidence_analysis.md",
    "09_verification_flags_breakdown.md",
    "10_evidence_provenance_log.md",
]

ROUTES_TO_CHECK = [
    "/workspace/view/{job_id}",
    "/map/overlay/{job_id}",
    "/map/overlay/data/{job_id}",
    "/map/view/{job_id}",
    "/feedback/{job_id}",
]


def check_job_directory(job_id: str) -> Tuple[bool, List[str]]:
    """Check that job directory and all expected files exist."""
    issues: List[str] = []
    job_dir = Path("uploads/jobs") / job_id

    if not job_dir.exists():
        issues.append(
            f"Job directory missing: {job_dir}\n"
            f"  Fix: python scripts/run_pipeline.py ... --register --job-id {job_id}"
        )
        return False, issues

    for filename in EXPECTED_FILES:
        if not (job_dir / filename).exists():
            issues.append(f"Missing file: {filename}")

    return len(issues) == 0, issues


def check_meta_json(job_id: str) -> Tuple[bool, List[str]]:
    """Check that meta.json is valid JSON and contains the expected job_id."""
    issues: List[str] = []
    meta_path = Path("uploads/jobs") / job_id / "meta.json"

    if not meta_path.exists():
        issues.append(f"meta.json not found at {meta_path}")
        return False, issues

    try:
        meta = json.loads(meta_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        issues.append(f"meta.json is not valid JSON: {exc}")
        return False, issues

    if meta.get("job_id") != job_id:
        issues.append(f"meta.json job_id mismatch: expected '{job_id}', got '{meta.get('job_id')}'")

    if "registered_at" not in meta:
        issues.append("meta.json missing 'registered_at' field")

    return len(issues) == 0, issues


def check_flask_routes(
    job_id: str, base_url: str = "http://127.0.0.1:5000"
) -> Tuple[bool, List[str]]:
    """Check that Flask routes return 200. Returns gracefully if Flask is not running."""
    import urllib.error
    import urllib.request

    issues: List[str] = []
    flask_running = False

    for route_template in ROUTES_TO_CHECK:
        url = base_url + route_template.format(job_id=job_id)
        try:
            req = urllib.request.Request(url, headers={"Accept": "text/html"})
            with urllib.request.urlopen(req, timeout=3) as resp:
                flask_running = True
                if resp.status != 200:
                    issues.append(f"Route returned {resp.status}: {url}")
        except urllib.error.URLError as exc:
            reason = str(getattr(exc, "reason", exc))
            if "Connection refused" in reason or "Connection reset" in reason:
                if not flask_running:
                    issues.append(
                        f"Flask is not running at {base_url}\n"
                        f"  Fix: export FLASK_APP=run.py && flask run"
                    )
                    return False, issues
            else:
                issues.append(f"Route error: {url} ({exc})")
        except Exception as exc:
            issues.append(f"Route check failed: {url} ({exc})")

    return len(issues) == 0, issues


def main() -> int:
    if len(sys.argv) < 2:
        print("Usage: python scripts/preflight_designer_review.py <job_id>")
        print()
        print("Example:")
        print("  python scripts/preflight_designer_review.py P_LOCAL_DESIGNER_REVIEW")
        return 1

    job_id = sys.argv[1]
    width = 66

    print(f"{'=' * width}")
    print("  GridFlow Designer Review — Pre-Flight Check")
    print(f"  Job ID: {job_id}")
    print(f"{'=' * width}")
    print()

    all_passed = True

    # Check 1: directory and files
    print("[1/3] Checking job directory and expected files...")
    ok, issues = check_job_directory(job_id)
    if ok:
        print(f"      OK  All {len(EXPECTED_FILES)} expected files present")
    else:
        all_passed = False
        for issue in issues:
            print(f"      FAIL  {issue}")
    print()

    # Check 2: meta.json
    print("[2/3] Validating meta.json...")
    ok, issues = check_meta_json(job_id)
    if ok:
        print("      OK  meta.json is valid and contains correct job_id")
    else:
        all_passed = False
        for issue in issues:
            print(f"      FAIL  {issue}")
    print()

    # Check 3: Flask routes (optional — warn only)
    print("[3/3] Checking Flask routes (skipped gracefully if Flask not running)...")
    ok, issues = check_flask_routes(job_id)
    if ok:
        print(f"      OK  All {len(ROUTES_TO_CHECK)} routes return 200")
    else:
        for issue in issues:
            print(f"      WARN  {issue}")
    print()

    print("-" * width)
    if all_passed:
        print("PRE-FLIGHT PASS — Ready for designer review session")
        print()
        print("One-pager (open in browser):")
        print("  open AI_CONTROL/115_DESIGNER_ONE_PAGER.html")
        print()
        print("Review routes:")
        for route in ROUTES_TO_CHECK:
            print(f"  http://127.0.0.1:5000{route.format(job_id=job_id)}")
        return 0
    else:
        print("PRE-FLIGHT FAIL — Fix issues above before the review session")
        return 1


if __name__ == "__main__":
    sys.exit(main())
