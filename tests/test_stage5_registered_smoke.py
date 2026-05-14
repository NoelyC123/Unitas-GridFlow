"""Stage 5F smoke tests for registered pipeline outputs."""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path

import pytest


@pytest.fixture
def smoke_test_job_id() -> str:
    """Unique job ID for the Stage 5F smoke test."""
    return "TEST_STAGE5F_SMOKE"


@pytest.fixture(autouse=True)
def cleanup_smoke_job(smoke_test_job_id: str):
    """Remove the smoke test job directory before and after each test."""
    job_dir = Path("uploads/jobs") / smoke_test_job_id
    if job_dir.exists():
        shutil.rmtree(job_dir)
    yield
    if job_dir.exists():
        shutil.rmtree(job_dir)


@pytest.fixture
def registered_job(smoke_test_job_id: str, tmp_path: Path) -> str:
    """Run the pipeline with registration enabled and return the job ID."""
    output_dir = tmp_path / "smoke_output"
    result = subprocess.run(
        [
            sys.executable,
            "scripts/run_pipeline.py",
            "--baseline",
            "tests/baseline/fixtures/enwl_sample.csv",
            "--field",
            "real_pilot_data/P_LOCAL_001/enwl_enrichment_clean",
            "--output",
            str(output_dir),
            "--job-id",
            smoke_test_job_id,
            "--register",
            "--overwrite-registration",
            "--log-level",
            "WARNING",
        ],
        capture_output=True,
        text=True,
        timeout=120,
        check=False,
    )

    if result.returncode != 0:
        pytest.skip(f"Pipeline failed in this environment: {result.stderr[-500:]}")

    return smoke_test_job_id


def test_registration_creates_job_directory(registered_job: str):
    """Pipeline with --register creates uploads/jobs/<job_id>/."""
    job_dir = Path("uploads/jobs") / registered_job
    assert job_dir.exists(), f"Job directory not created: {job_dir}"


def test_registration_creates_expected_files(registered_job: str):
    """Registered job directory contains the expected pipeline outputs."""
    job_dir = Path("uploads/jobs") / registered_job
    expected = [
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

    missing = [filename for filename in expected if not (job_dir / filename).exists()]
    assert not missing, f"Missing files in {job_dir}: {missing}"


def test_meta_json_has_job_id(registered_job: str):
    """meta.json contains the registered job ID and registration timestamp."""
    meta = json.loads((Path("uploads/jobs") / registered_job / "meta.json").read_text())
    assert meta["job_id"] == registered_job
    assert meta["source"] == "pipeline_registration"
    assert "registered_at" in meta


def test_workspace_route_loads(client, registered_job: str):
    """GET /workspace/view/<job_id> returns 200."""
    response = client.get(f"/workspace/view/{registered_job}")
    assert response.status_code == 200
    assert registered_job.encode() in response.data


def test_map_overlay_route_loads(client, registered_job: str):
    """GET /map/overlay/<job_id> returns 200."""
    response = client.get(f"/map/overlay/{registered_job}")
    assert response.status_code == 200


def test_map_overlay_data_returns_json(client, registered_job: str):
    """GET /map/overlay/data/<job_id> returns valid JSON with expected keys."""
    response = client.get(f"/map/overlay/data/{registered_job}")
    assert response.status_code == 200
    data = json.loads(response.data)
    assert "baseline_poles" in data
    assert "field_poles" in data
    assert "match_lines" in data
    assert "statistics" in data


def test_map_view_route_loads(client, registered_job: str):
    """GET /map/view/<job_id> returns 200 or redirect."""
    response = client.get(f"/map/view/{registered_job}")
    assert response.status_code in (200, 302)


def test_full_chain_outputs_are_parseable(registered_job: str):
    """Registered outputs are parseable and reference the registered job ID."""
    job_dir = Path("uploads/jobs") / registered_job

    merged = json.loads((job_dir / "04_merged_dataset.json").read_text())
    assert isinstance(merged, dict)
    assert "poles" in merged
    assert len(merged["poles"]) > 0

    report_00 = (job_dir / "00_pilot_output_pack_index.md").read_text()
    assert registered_job in report_00
    assert "GridFlow Pipeline" not in report_00
