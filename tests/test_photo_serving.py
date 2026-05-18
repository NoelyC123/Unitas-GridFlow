from __future__ import annotations

import json
from pathlib import Path

from app import create_app
from app.routes import workspace as workspace_module


def _client_with_root(tmp_path: Path):
    app = create_app()
    app.config["TESTING"] = True
    app.config["REAL_PILOT_DATA_ROOT"] = str(tmp_path)
    return app, app.test_client()


def _make_photo_tree(
    root: Path,
    *,
    survey_id: str = "P_LOCAL_002",
    pole_id: str = "05_SUPPORT_900344",
    filename: str = "IMG_0903.JPG",
) -> Path:
    photo_dir = root / survey_id / "enwl_enrichment_clean" / pole_id / "field_photos"
    photo_dir.mkdir(parents=True, exist_ok=True)
    photo_path = photo_dir / filename
    photo_path.write_bytes(b"fake-image")
    return photo_path


def test_valid_photo_path_returns_200(tmp_path):
    _make_photo_tree(tmp_path)
    app, client = _client_with_root(tmp_path)

    response = client.get("/api/photos/P_LOCAL_002/05_SUPPORT_900344/IMG_0903.JPG")
    assert response.status_code == 200
    assert response.data == b"fake-image"


def test_invalid_survey_id_returns_404(tmp_path):
    _make_photo_tree(tmp_path)
    app, client = _client_with_root(tmp_path)

    response = client.get("/api/photos/../../etc/05_SUPPORT_900344/IMG_0903.JPG")
    assert response.status_code == 404


def test_invalid_pole_id_returns_404(tmp_path):
    _make_photo_tree(tmp_path)
    app, client = _client_with_root(tmp_path)

    response = client.get("/api/photos/P_LOCAL_002/../bad/IMG_0903.JPG")
    assert response.status_code == 404


def test_invalid_filename_extension_returns_404(tmp_path):
    _make_photo_tree(tmp_path)
    app, client = _client_with_root(tmp_path)

    response = client.get("/api/photos/P_LOCAL_002/05_SUPPORT_900344/IMG_0903.gif")
    assert response.status_code == 404


def test_missing_file_returns_404(tmp_path):
    _make_photo_tree(tmp_path)
    app, client = _client_with_root(tmp_path)

    response = client.get("/api/photos/P_LOCAL_002/05_SUPPORT_900344/MISSING.JPG")
    assert response.status_code == 404


def test_path_traversal_in_filename_returns_404(tmp_path):
    _make_photo_tree(tmp_path)
    app, client = _client_with_root(tmp_path)

    response = client.get("/api/photos/P_LOCAL_002/05_SUPPORT_900344/../../secret.JPG")
    assert response.status_code == 404


def test_filename_with_spaces_returns_404(tmp_path):
    _make_photo_tree(tmp_path, filename="IMG_0903 space.JPG")
    app, client = _client_with_root(tmp_path)

    response = client.get("/api/photos/P_LOCAL_002/05_SUPPORT_900344/IMG_0903%20space.JPG")
    assert response.status_code == 404


def test_blueprint_registered_correctly():
    app = create_app()
    rules = {rule.rule for rule in app.url_map.iter_rules()}
    assert "/api/photos/<survey_id>/<pole_id>/<filename>" in rules


def test_workspace_pole_detail_renders_photo_urls(tmp_path, monkeypatch):
    _make_photo_tree(tmp_path)

    jobs_root = tmp_path / "jobs"
    jobs_root.mkdir()
    job_dir = jobs_root / "WS_PHOTO_JOB"
    job_dir.mkdir()
    (job_dir / "04_merged_dataset.json").write_text(
        json.dumps(
            {
                "baseline_source": "test.csv",
                "field_source": "real_pilot_data/P_LOCAL_002/enwl_enrichment_clean",
                "merge_date": "2026-05-18",
                "total_poles_baseline": 1,
                "total_poles_field": 1,
                "total_matched": 1,
                "poles": [
                    {
                        "support_no": "900344",
                        "folder_name": "05_SUPPORT_900344",
                        "field_photo_count": 1,
                        "design_ready": False,
                        "design_blocked": True,
                        "match_confidence": "HIGH",
                        "notes_content": "Support No: 900344",
                        "special_flags": [],
                        "voltage_verification_required": False,
                        "conductor_verification_required": False,
                        "pole_class_verification_required": False,
                        "condition_verification_required": False,
                        "identity_verification_required": False,
                        "equipment_conflict_flag": False,
                        "designer_actions": [],
                    }
                ],
                "unmatched_baseline": [],
                "unmatched_field": [],
            }
        ),
        encoding="utf-8",
    )

    monkeypatch.setattr(workspace_module, "JOBS_ROOT", jobs_root)
    app = create_app()
    app.config["TESTING"] = True
    app.config["REAL_PILOT_DATA_ROOT"] = str(tmp_path)
    client = app.test_client()

    response = client.get("/workspace/pole/WS_PHOTO_JOB/900344")
    assert response.status_code == 200
    body = response.data.decode()
    assert "Field Photos" in body
    assert "/api/photos/P_LOCAL_002/05_SUPPORT_900344/IMG_0903.JPG" in body
