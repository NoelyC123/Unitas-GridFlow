"""Tests for workspace Flask routes — follows map_preview test pattern."""

import json

import pytest

from app import create_app
from app.routes import workspace as workspace_module


def _make_dataset_json(poles_data: list[dict]) -> dict:
    return {
        "baseline_source": "test.csv",
        "field_source": "/test/field",
        "merge_date": "2026-05-14",
        "total_poles_baseline": len(poles_data),
        "total_poles_field": len(poles_data),
        "total_matched": len(poles_data),
        "poles": poles_data,
        "unmatched_baseline": [],
        "unmatched_field": [],
    }


@pytest.fixture
def setup_workspace_job(tmp_path, monkeypatch):
    """Create a temp JOBS_ROOT and write a test job."""
    jobs_root = tmp_path / "jobs"
    jobs_root.mkdir(parents=True)

    job_id = "WS_TEST_001"
    job_dir = jobs_root / job_id
    job_dir.mkdir()

    poles = [
        {
            "support_no": "903203",
            "design_ready": False,
            "design_blocked": True,
            "match_confidence": "HIGH",
            "field_photo_count": 5,
            "notes_content": "Support No: 903203",
            "special_flags": [],
            "voltage_verification_required": True,
            "conductor_verification_required": True,
            "pole_class_verification_required": True,
            "condition_verification_required": False,
            "identity_verification_required": False,
            "equipment_conflict_flag": False,
            "designer_actions": [
                "Obtain DNO-certified voltage specification",
                "Obtain DNO conductor specification",
            ],
        }
    ]
    (job_dir / "04_merged_dataset.json").write_text(
        json.dumps(_make_dataset_json(poles)), encoding="utf-8"
    )

    monkeypatch.setattr(workspace_module, "JOBS_ROOT", jobs_root)
    return job_id


def test_workspace_view_route_renders(setup_workspace_job):
    """GET /workspace/view/<job_id> returns 200 with pole table."""
    app = create_app()
    client = app.test_client()

    res = client.get(f"/workspace/view/{setup_workspace_job}")
    assert res.status_code == 200

    body = res.data.decode()
    assert "Review Workspace" in body
    assert "903203" in body


def test_workspace_view_statistics_panel(setup_workspace_job):
    """Statistics panel values are present in response."""
    app = create_app()
    client = app.test_client()

    res = client.get(f"/workspace/view/{setup_workspace_job}")
    body = res.data.decode()

    # Total poles = 1, design_blocked = 1
    assert "Total Poles" in body
    assert "Design Blocked" in body


def test_workspace_view_filter_design_ready(setup_workspace_job):
    """Filter design_ready=true returns empty table (job has no ready poles)."""
    app = create_app()
    client = app.test_client()

    res = client.get(f"/workspace/view/{setup_workspace_job}?design_ready=true")
    assert res.status_code == 200

    body = res.data.decode()
    assert "No poles match the current filters" in body


def test_workspace_view_filter_design_blocked(setup_workspace_job):
    """Filter design_ready=false returns the blocked pole."""
    app = create_app()
    client = app.test_client()

    res = client.get(f"/workspace/view/{setup_workspace_job}?design_ready=false")
    assert res.status_code == 200
    assert b"903203" in res.data


def test_pole_detail_route_renders(setup_workspace_job):
    """GET /workspace/pole/<job_id>/<support_no> returns pole detail."""
    app = create_app()
    client = app.test_client()

    res = client.get(f"/workspace/pole/{setup_workspace_job}/903203")
    assert res.status_code == 200

    body = res.data.decode()
    assert "Pole 903203" in body
    assert "Design Blocked" in body


def test_pole_detail_shows_designer_actions(setup_workspace_job):
    """Pole detail renders the designer_actions list."""
    app = create_app()
    client = app.test_client()

    res = client.get(f"/workspace/pole/{setup_workspace_job}/903203")
    body = res.data.decode()

    assert "Obtain DNO-certified voltage specification" in body
    assert "Required Actions Before Design" in body


def test_pole_detail_not_found(setup_workspace_job):
    """Requesting an unknown support_no returns 404."""
    app = create_app()
    client = app.test_client()

    res = client.get(f"/workspace/pole/{setup_workspace_job}/UNKNOWN_99")
    assert res.status_code == 404


def test_workspace_job_not_found():
    """Requesting a non-existent job returns 404."""
    app = create_app()
    client = app.test_client()

    res = client.get("/workspace/view/NONEXISTENT_JOB_XYZ")
    assert res.status_code == 404
