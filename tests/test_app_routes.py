from __future__ import annotations

import json
from pathlib import Path

from app import create_app
from app.routes import api_jobs, pdf_reports


def _write_json(path: Path, payload: dict) -> None:
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def test_health_full_returns_expected_payload() -> None:
    app = create_app()
    client = app.test_client()

    response = client.get("/health/full")

    assert response.status_code == 200
    data = response.get_json()

    assert data["ok"] is True
    assert data["service"] == "unitas-gridflow"
    assert data["status"] == "healthy"
    assert data["version"] == "dev"


def test_api_jobs_list_returns_saved_job_metadata(tmp_path, monkeypatch) -> None:
    jobs_root = tmp_path / "jobs"
    job_dir = jobs_root / "J10001"
    job_dir.mkdir(parents=True)

    _write_json(
        job_dir / "meta.json",
        {
            "job_id": "J10001",
            "status": "complete",
            "rulepack_id": "SPEN_11kV",
            "pole_count": 5,
            "issue_count": 4,
            "pass_count": 1,
            "warn_count": 0,
            "fail_count": 4,
            "filename": "mock_survey.csv",
            "auto_normalized": True,
        },
    )

    monkeypatch.setattr(api_jobs, "JOBS_ROOT", jobs_root)

    app = create_app()
    client = app.test_client()

    response = client.get("/api/jobs/")

    assert response.status_code == 200
    data = response.get_json()

    assert "jobs" in data
    assert len(data["jobs"]) == 1
    assert data["jobs"][0]["job_id"] == "J10001"
    assert data["jobs"][0]["status"] == "complete"
    assert data["jobs"][0]["rulepack_id"] == "SPEN_11kV"


def test_api_job_status_returns_pending_for_missing_job(tmp_path, monkeypatch) -> None:
    jobs_root = tmp_path / "jobs"
    jobs_root.mkdir(parents=True)

    monkeypatch.setattr(api_jobs, "JOBS_ROOT", jobs_root)

    app = create_app()
    client = app.test_client()

    response = client.get("/api/jobs/J99999/status")

    assert response.status_code == 200
    data = response.get_json()

    assert data["job_id"] == "J99999"
    assert data["status"] == "pending"


def test_api_job_status_returns_error_for_invalid_meta(tmp_path, monkeypatch) -> None:
    jobs_root = tmp_path / "jobs"
    job_dir = jobs_root / "J20002"
    job_dir.mkdir(parents=True)

    (job_dir / "meta.json").write_text("{not valid json", encoding="utf-8")

    monkeypatch.setattr(api_jobs, "JOBS_ROOT", jobs_root)

    app = create_app()
    client = app.test_client()

    response = client.get("/api/jobs/J20002/status")

    assert response.status_code == 500
    data = response.get_json()

    assert data["job_id"] == "J20002"
    assert data["status"] == "error"
    assert "Invalid meta.json" in data["error"]


def test_pdf_route_returns_pdf_for_valid_job(tmp_path, monkeypatch) -> None:
    jobs_root = tmp_path / "jobs"
    job_dir = jobs_root / "J30003"
    job_dir.mkdir(parents=True)

    _write_json(
        job_dir / "meta.json",
        {
            "job_id": "J30003",
            "status": "complete",
            "rulepack_id": "SPEN_11kV",
            "auto_normalized": True,
            "pole_count": 5,
            "issue_count": 2,
        },
    )

    (job_dir / "issues.csv").write_text(
        "Issue,Row\n\"Duplicate value in 'pole_id': P-1001\",\"{'pole_id': 'P-1001'}\"\n",
        encoding="utf-8",
    )

    monkeypatch.setattr(pdf_reports, "JOBS_ROOT", jobs_root)

    app = create_app()
    client = app.test_client()

    response = client.get("/pdf/qa/J30003")

    assert response.status_code == 200
    assert response.mimetype == "application/pdf"
    assert response.data.startswith(b"%PDF")


def test_pdf_route_returns_404_for_missing_job(tmp_path, monkeypatch) -> None:
    jobs_root = tmp_path / "jobs"
    jobs_root.mkdir(parents=True)

    monkeypatch.setattr(pdf_reports, "JOBS_ROOT", jobs_root)

    app = create_app()
    client = app.test_client()

    response = client.get("/pdf/qa/J40400")

    assert response.status_code == 404
