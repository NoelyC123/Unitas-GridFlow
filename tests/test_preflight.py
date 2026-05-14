"""Tests for scripts/preflight_designer_review.py — Stage 5G."""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[1]
JOBS_ROOT = PROJECT_ROOT / "uploads" / "jobs"

PREFLIGHT_SCRIPT = str(PROJECT_ROOT / "scripts" / "preflight_designer_review.py")

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


@pytest.fixture
def preflight_test_job():
    """Create a complete registered job and remove it after the test."""
    job_id = "PREFLIGHT_TEST_JOB"
    job_dir = JOBS_ROOT / job_id
    if job_dir.exists():
        shutil.rmtree(job_dir)
    job_dir.mkdir(parents=True)

    (job_dir / "meta.json").write_text(
        json.dumps(
            {
                "job_id": job_id,
                "registered_at": "2026-05-14T12:00:00",
                "source": "test",
            }
        ),
        encoding="utf-8",
    )
    (job_dir / "pipeline_summary.json").write_text("{}", encoding="utf-8")
    for filename in EXPECTED_FILES:
        if filename not in ("meta.json", "pipeline_summary.json"):
            (job_dir / filename).write_text("test content", encoding="utf-8")

    try:
        yield job_id
    finally:
        if job_dir.exists():
            shutil.rmtree(job_dir)


def _run_preflight(job_id: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, PREFLIGHT_SCRIPT, job_id],
        capture_output=True,
        text=True,
        timeout=15,
        cwd=str(PROJECT_ROOT),
    )


def test_preflight_passes_for_valid_job(preflight_test_job):
    """Preflight reports all file checks OK for a fully-populated job directory."""
    result = _run_preflight(preflight_test_job)
    # File checks must pass — Flask check may fail (warning only)
    assert "All" in result.stdout and "expected files present" in result.stdout
    assert "meta.json is valid" in result.stdout
    # Exit 0 if all non-Flask checks pass (Flask may not be running in CI)
    assert result.returncode in (0, 1)


def test_preflight_fails_for_missing_job():
    """Preflight exits non-zero when the job directory does not exist."""
    result = _run_preflight("NONEXISTENT_JOB_PREFLIGHT_XYZ")
    assert result.returncode != 0
    assert "missing" in result.stdout.lower() or "fail" in result.stdout.lower()


def test_preflight_requires_job_id_argument():
    """Preflight prints usage and exits non-zero when called with no arguments."""
    result = subprocess.run(
        [sys.executable, PREFLIGHT_SCRIPT],
        capture_output=True,
        text=True,
        timeout=10,
        cwd=str(PROJECT_ROOT),
    )
    assert result.returncode != 0
    assert "Usage" in result.stdout or "usage" in result.stdout.lower()


def test_preflight_detects_missing_file(preflight_test_job):
    """Preflight reports a missing file when one expected file is removed."""
    target = JOBS_ROOT / preflight_test_job / "06_dno_data_request.md"
    target.unlink()

    result = _run_preflight(preflight_test_job)
    assert result.returncode != 0
    assert "06_dno_data_request.md" in result.stdout or "Missing" in result.stdout


def test_preflight_detects_meta_job_id_mismatch(preflight_test_job):
    """Preflight flags when meta.json contains a different job_id."""
    meta_path = JOBS_ROOT / preflight_test_job / "meta.json"
    meta_path.write_text(
        json.dumps({"job_id": "WRONG_JOB_ID", "registered_at": "2026-01-01"}),
        encoding="utf-8",
    )

    result = _run_preflight(preflight_test_job)
    assert result.returncode != 0
    assert "mismatch" in result.stdout.lower() or "fail" in result.stdout.lower()
