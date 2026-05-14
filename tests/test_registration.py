"""Tests for GridFlow pipeline output registration."""

from __future__ import annotations

import json
import time
from pathlib import Path

import pytest

from gridflow.registration import (
    generate_job_id,
    print_registration_summary,
    register_pipeline_output,
)


def test_generate_job_id_format():
    """Job ID should match the gridflow_YYYYMMDD_HHMMSS pattern."""
    job_id = generate_job_id()
    assert job_id.startswith("gridflow_")
    assert len(job_id) == len("gridflow_20260514_120000")


def test_generate_job_id_unique():
    """Two generated job IDs should differ when generated in separate seconds."""
    id1 = generate_job_id()
    time.sleep(1.1)
    id2 = generate_job_id()
    assert id1 != id2


def test_register_copies_files(tmp_path: Path):
    """Registration copies all files from the pipeline run directory."""
    run_dir = tmp_path / "pipeline_run_20260514_120000"
    run_dir.mkdir()
    (run_dir / "04_merged_dataset.json").write_text("[]", encoding="utf-8")
    (run_dir / "00_pilot_output_pack_index.md").write_text("# Test", encoding="utf-8")

    jobs_root = tmp_path / "uploads" / "jobs"

    job_dir = register_pipeline_output(
        pipeline_run_dir=run_dir,
        job_id="TEST_JOB_001",
        jobs_root=jobs_root,
    )

    assert job_dir.exists()
    assert (job_dir / "04_merged_dataset.json").exists()
    assert (job_dir / "00_pilot_output_pack_index.md").exists()


def test_register_writes_meta_json(tmp_path: Path):
    """Registration writes meta.json with job ID and registration metadata."""
    run_dir = tmp_path / "pipeline_run_test"
    run_dir.mkdir()
    (run_dir / "pipeline_summary.json").write_text("{}", encoding="utf-8")

    job_dir = register_pipeline_output(
        pipeline_run_dir=run_dir,
        job_id="META_TEST",
        jobs_root=tmp_path / "uploads" / "jobs",
    )

    meta = json.loads((job_dir / "meta.json").read_text(encoding="utf-8"))
    assert meta["job_id"] == "META_TEST"
    assert meta["source"] == "pipeline_registration"
    assert "registered_at" in meta
    assert meta["pipeline_run_dir"] == str(run_dir)


def test_register_existing_job_without_overwrite_raises(tmp_path: Path):
    """Registration does not silently overwrite an existing job directory."""
    run_dir = tmp_path / "pipeline_run_test"
    run_dir.mkdir()
    (run_dir / "04_merged_dataset.json").write_text('[{"new": true}]', encoding="utf-8")

    jobs_root = tmp_path / "uploads" / "jobs"
    existing_job_dir = jobs_root / "OVERWRITE_TEST"
    existing_job_dir.mkdir(parents=True)
    (existing_job_dir / "old_file.txt").write_text("old content", encoding="utf-8")

    with pytest.raises(FileExistsError, match="Use --overwrite-registration"):
        register_pipeline_output(
            pipeline_run_dir=run_dir,
            job_id="OVERWRITE_TEST",
            jobs_root=jobs_root,
        )

    assert (existing_job_dir / "old_file.txt").exists()


def test_register_existing_job_with_overwrite_replaces_directory(tmp_path: Path):
    """Registration replaces an existing job directory only when overwrite is true."""
    run_dir = tmp_path / "pipeline_run_test"
    run_dir.mkdir()
    (run_dir / "04_merged_dataset.json").write_text('[{"new": true}]', encoding="utf-8")

    jobs_root = tmp_path / "uploads" / "jobs"
    existing_job_dir = jobs_root / "OVERWRITE_TEST"
    existing_job_dir.mkdir(parents=True)
    (existing_job_dir / "old_file.txt").write_text("old content", encoding="utf-8")

    job_dir = register_pipeline_output(
        pipeline_run_dir=run_dir,
        job_id="OVERWRITE_TEST",
        jobs_root=jobs_root,
        overwrite=True,
    )

    assert job_dir == existing_job_dir
    assert not (job_dir / "old_file.txt").exists()
    assert (job_dir / "04_merged_dataset.json").exists()


def test_register_sanitises_job_id(tmp_path: Path):
    """Job IDs with invalid path characters are sanitised."""
    run_dir = tmp_path / "pipeline_run_test"
    run_dir.mkdir()
    (run_dir / "test.json").write_text("{}", encoding="utf-8")

    job_dir = register_pipeline_output(
        pipeline_run_dir=run_dir,
        job_id="job/with/slashes",
        jobs_root=tmp_path / "uploads" / "jobs",
    )

    assert job_dir.name == "job_with_slashes"
    assert job_dir.exists()


def test_register_raises_if_run_dir_missing(tmp_path: Path):
    """Registration raises FileNotFoundError if the run directory does not exist."""
    with pytest.raises(FileNotFoundError):
        register_pipeline_output(
            pipeline_run_dir=tmp_path / "nonexistent",
            job_id="FAIL_TEST",
            jobs_root=tmp_path / "uploads" / "jobs",
        )


def test_register_raises_if_job_id_empty(tmp_path: Path):
    """Registration raises ValueError if the job ID is empty."""
    run_dir = tmp_path / "run"
    run_dir.mkdir()

    with pytest.raises(ValueError):
        register_pipeline_output(
            pipeline_run_dir=run_dir,
            job_id="",
            jobs_root=tmp_path / "uploads" / "jobs",
        )


def test_print_registration_summary_lists_web_routes(capsys, tmp_path: Path):
    """The registration summary prints the expected workspace and map URLs."""
    print_registration_summary("PRINT_TEST", tmp_path / "uploads" / "jobs" / "PRINT_TEST")

    output = capsys.readouterr().out
    assert "Registered as job: PRINT_TEST" in output
    assert "http://127.0.0.1:5000/workspace/view/PRINT_TEST" in output
    assert "http://127.0.0.1:5000/map/overlay/PRINT_TEST" in output
    assert "http://127.0.0.1:5000/map/view/PRINT_TEST" in output
