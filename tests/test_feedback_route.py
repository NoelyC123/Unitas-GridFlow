"""Tests for the Stage 5G designer feedback route."""

from __future__ import annotations

import json
import shutil
from pathlib import Path

import pytest

from app import create_app
from app.routes import feedback as feedback_module

PROJECT_ROOT = Path(__file__).resolve().parents[1]
JOBS_ROOT = PROJECT_ROOT / "uploads" / "jobs"


@pytest.fixture
def feedback_client(monkeypatch):
    """Test client with JOBS_ROOT pointing to the real uploads/jobs directory."""
    monkeypatch.setattr(feedback_module, "JOBS_ROOT", JOBS_ROOT)
    return create_app().test_client()


@pytest.fixture
def feedback_test_job(monkeypatch):
    """Create a minimal registered job directory and clean it up after the test."""
    monkeypatch.setattr(feedback_module, "JOBS_ROOT", JOBS_ROOT)
    job_id = "FEEDBACK_TEST_JOB"
    job_dir = JOBS_ROOT / job_id
    job_dir.mkdir(parents=True, exist_ok=True)
    (job_dir / "meta.json").write_text(json.dumps({"job_id": job_id}), encoding="utf-8")
    try:
        yield job_id
    finally:
        if job_dir.exists():
            shutil.rmtree(job_dir)


def _full_form_data(designer_name: str = "Test Designer") -> dict:
    """Return a complete valid form submission."""
    return {
        "designer_name": designer_name,
        "designer_role": "OHL Designer",
        "q1_what_gridflow_does": "Reconciles survey data with DNO records",
        "q2_blockers_make_sense": "Yes, makes complete sense",
        "q3_dno_request_clarity": "Crystal clear",
        "q4_time_savings": "Significant savings",
        "q5_trust_in_blockers": "I trust them",
        "q6_match_confidence": "Yes, very useful",
        "q7_map_overlay": "Yes, very useful",
        "q8_photo_priority": "High priority",
        "q9_use_blockers": "Nothing at this stage",
        "q10_first_change": "Photo integration",
        "additional_notes": "Looks promising",
    }


def test_feedback_form_renders(feedback_client, feedback_test_job):
    """GET /feedback/<job_id> returns 200 with the form."""
    response = feedback_client.get(f"/feedback/{feedback_test_job}")
    assert response.status_code == 200
    assert b"Designer Feedback" in response.data
    assert feedback_test_job.encode() in response.data


def test_feedback_form_404_for_unknown_job(feedback_client, monkeypatch):
    """GET /feedback/<unknown> returns 404."""
    monkeypatch.setattr(feedback_module, "JOBS_ROOT", JOBS_ROOT)
    response = feedback_client.get("/feedback/NONEXISTENT_JOB_XYZ_999")
    assert response.status_code == 404


def test_feedback_submit_saves_json(feedback_client, feedback_test_job):
    """POST /feedback/<job_id>/submit saves feedback.json with all answers."""
    response = feedback_client.post(
        f"/feedback/{feedback_test_job}/submit",
        data=_full_form_data(),
    )
    assert response.status_code == 200
    assert b"Feedback Received" in response.data

    feedback_path = JOBS_ROOT / feedback_test_job / "feedback.json"
    assert feedback_path.exists()

    saved = json.loads(feedback_path.read_text(encoding="utf-8"))
    assert isinstance(saved, list)
    assert len(saved) == 1
    entry = saved[0]
    assert entry["designer_name"] == "Test Designer"
    assert (
        entry["answers"]["q1_what_gridflow_does"]["answer"]
        == "Reconciles survey data with DNO records"
    )
    assert entry["additional_notes"] == "Looks promising"
    assert "submitted_at" in entry
    assert entry["job_id"] == feedback_test_job


def test_feedback_submit_appends_existing(feedback_client, feedback_test_job):
    """Second submission appends to feedback.json rather than overwriting."""
    feedback_client.post(
        f"/feedback/{feedback_test_job}/submit",
        data=_full_form_data("Designer One"),
    )
    feedback_client.post(
        f"/feedback/{feedback_test_job}/submit",
        data=_full_form_data("Designer Two"),
    )

    saved = json.loads(
        (JOBS_ROOT / feedback_test_job / "feedback.json").read_text(encoding="utf-8")
    )
    assert len(saved) == 2
    assert saved[0]["designer_name"] == "Designer One"
    assert saved[1]["designer_name"] == "Designer Two"


def test_feedback_submit_404_for_unknown_job(feedback_client, monkeypatch):
    """POST to an unknown job returns 404."""
    monkeypatch.setattr(feedback_module, "JOBS_ROOT", JOBS_ROOT)
    response = feedback_client.post(
        "/feedback/NONEXISTENT/submit",
        data={"designer_name": "Test"},
    )
    assert response.status_code == 404


def test_feedback_form_shows_existing_warning(feedback_client, feedback_test_job):
    """GET shows 'already submitted' note when feedback.json already exists."""
    feedback_path = JOBS_ROOT / feedback_test_job / "feedback.json"
    feedback_path.write_text(json.dumps([{"designer_name": "Previous"}]), encoding="utf-8")

    response = feedback_client.get(f"/feedback/{feedback_test_job}")
    assert response.status_code == 200
    assert b"already been submitted" in response.data


def test_feedback_submit_anonymous_when_name_omitted(feedback_client, feedback_test_job):
    """Submitting without a name stores 'Anonymous'."""
    data = _full_form_data()
    data["designer_name"] = ""
    feedback_client.post(f"/feedback/{feedback_test_job}/submit", data=data)

    saved = json.loads(
        (JOBS_ROOT / feedback_test_job / "feedback.json").read_text(encoding="utf-8")
    )
    assert saved[0]["designer_name"] == "Anonymous"


def test_feedback_thanks_links_back_to_workspace(feedback_client, feedback_test_job):
    """Thanks page includes a link back to the workspace."""
    response = feedback_client.post(
        f"/feedback/{feedback_test_job}/submit",
        data=_full_form_data(),
    )
    assert b"/workspace/view/" in response.data
    assert feedback_test_job.encode() in response.data
