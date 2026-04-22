from __future__ import annotations

import json
from pathlib import Path

from app import create_app
from app.routes import api_intake, api_jobs, pdf_reports


def _write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
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


def test_import_finalize_returns_success_for_valid_job(tmp_path, monkeypatch) -> None:
    jobs_root = tmp_path / "jobs"
    job_dir = jobs_root / "J50005"
    job_dir.mkdir(parents=True)

    csv_path = job_dir / "mock_survey.csv"
    csv_path.write_text(
        "\n".join(
            [
                "asset_id,structure_type,height_m,material,location_name,easting,northing,latitude,longitude",
                "P-1001,Wood Pole,11.0,Wood,Dalton Road Junction,352841,503122,54.5210,-3.0140",
                "P-1002,Wood Pole,7.5,Wood,Back Lane Farm,352910,503088,54.5183,-3.0121",
                "P-1003,Steel Pole,28.0,Steel,Moorside Substation,352975,503200,54.5291,-3.0098",
                "P-1004,Wood Pole,12.5,,Hartley Bridge,353041,503155,54.5246,-3.0075",
                (
                    "P-1001,Wood Pole,13.0,Wood,"
                    "Dalton Road Junction North,353100,503170,54.5261,-3.0052"
                ),
            ]
        ),
        encoding="utf-8",
    )

    _write_json(
        job_dir / "meta.json",
        {
            "job_id": "J50005",
            "uploaded_path": str(csv_path),
            "filename": "mock_survey.csv",
            "status": "uploaded",
        },
    )

    monkeypatch.setattr(api_intake, "_jobs_root", lambda: jobs_root)

    app = create_app()
    client = app.test_client()

    response = client.post("/api/import/J50005", json={"dno": "SPEN_11kV"})

    assert response.status_code == 200
    data = response.get_json()

    assert data["ok"] is True
    assert data["job_id"] == "J50005"
    assert data["rulepack_id"] == "SPEN_11kV"
    assert data["issue_count"] == 11

    updated_meta = json.loads((job_dir / "meta.json").read_text(encoding="utf-8"))
    assert updated_meta["status"] == "complete"
    assert updated_meta["auto_normalized"] is True

    issues_csv = job_dir / "issues.csv"
    map_data_json = job_dir / "map_data.json"

    assert issues_csv.exists()
    assert map_data_json.exists()


def test_import_finalize_returns_500_when_uploaded_path_missing(tmp_path, monkeypatch) -> None:
    jobs_root = tmp_path / "jobs"
    job_dir = jobs_root / "J50006"
    job_dir.mkdir(parents=True)

    _write_json(
        job_dir / "meta.json",
        {
            "job_id": "J50006",
            "status": "uploaded",
        },
    )

    monkeypatch.setattr(api_intake, "_jobs_root", lambda: jobs_root)

    app = create_app()
    client = app.test_client()

    response = client.post("/api/import/J50006", json={"dno": "SPEN_11kV"})

    assert response.status_code == 500
    data = response.get_json()

    assert data["ok"] is False
    assert data["job_id"] == "J50006"
    assert "No uploaded file path recorded in meta.json" in data["error"]

    updated_meta = json.loads((job_dir / "meta.json").read_text(encoding="utf-8"))
    assert updated_meta["status"] == "error"


def test_import_finalize_handles_raw_controller_dump(tmp_path, monkeypatch) -> None:
    jobs_root = tmp_path / "jobs"
    job_dir = jobs_root / "J50099"
    job_dir.mkdir(parents=True)

    # Minimal raw controller dump matching 28-14 513 (2).csv format.
    # Coordinates are TM65 Irish Grid (Strabane area, Northern Ireland).
    raw_dump = (
        "Job:28-14 513,Version:24.00,Units:Metres\n"
        "PRS485572899536,219497.298,413575.610,118.985,\n"
        "1,242186.075,402362.807,99.505,Angle,Angle:STRING,1,"
        "Angle:TAG,5,Angle:REMARK,convert to tee\n"
        "2,242218.756,402321.523,97.200,Pol,Pol:HEIGHT,6.1,Pol:REMARK,new term pole pos\n"
        "3,242245.112,402276.834,95.800,Hedge,Hedge:STRING,2,Hedge:TAG,3\n"
    )
    csv_path = job_dir / "28-14_513.csv"
    csv_path.write_text(raw_dump, encoding="utf-8")

    _write_json(
        job_dir / "meta.json",
        {
            "job_id": "J50099",
            "uploaded_path": str(csv_path),
            "filename": "28-14_513.csv",
            "status": "uploaded",
        },
    )

    monkeypatch.setattr(api_intake, "_jobs_root", lambda: jobs_root)

    app = create_app()
    client = app.test_client()

    response = client.post("/api/import/J50099", json={"dno": "NIE_11kV"})

    assert response.status_code == 200
    data = response.get_json()

    assert data["ok"] is True
    assert data["file_type"] == "controller"
    assert data["auto_normalized"] is True

    completeness = data["completeness"]
    assert completeness["total_records"] == 3
    assert completeness["fields"]["height"]["present"] == 1  # only Pol has HEIGHT attribute
    assert completeness["fields"]["location"]["present"] == 2  # Angle and Pol have REMARK

    assert "feature_codes_found" in completeness
    assert set(completeness["feature_codes_found"]) == {"Angle", "Pol", "Hedge"}

    assert (job_dir / "issues.csv").exists()
    assert (job_dir / "map_data.json").exists()

    updated_meta = json.loads((job_dir / "meta.json").read_text(encoding="utf-8"))
    assert updated_meta["status"] == "complete"
    assert updated_meta["file_type"] == "controller"


def test_import_finalize_returns_500_when_csv_file_missing(tmp_path, monkeypatch) -> None:
    jobs_root = tmp_path / "jobs"
    job_dir = jobs_root / "J50007"
    job_dir.mkdir(parents=True)

    missing_csv_path = job_dir / "missing.csv"

    _write_json(
        job_dir / "meta.json",
        {
            "job_id": "J50007",
            "uploaded_path": str(missing_csv_path),
            "filename": "missing.csv",
            "status": "uploaded",
        },
    )

    monkeypatch.setattr(api_intake, "_jobs_root", lambda: jobs_root)

    app = create_app()
    client = app.test_client()

    response = client.post("/api/import/J50007", json={"dno": "SPEN_11kV"})

    assert response.status_code == 500
    data = response.get_json()

    assert data["ok"] is False
    assert data["job_id"] == "J50007"
    assert "Uploaded CSV not found" in data["error"]

    updated_meta = json.loads((job_dir / "meta.json").read_text(encoding="utf-8"))
    assert updated_meta["status"] == "error"
