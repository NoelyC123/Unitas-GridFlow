"""
Designer Feedback Capture Route — Stage 5G

Live in-workspace feedback form for designer review sessions.
Saves answers to uploads/jobs/<job_id>/feedback.json.
"""

from __future__ import annotations

import json
import logging
from datetime import datetime
from pathlib import Path

from flask import Blueprint, render_template, request

logger = logging.getLogger(__name__)

feedback_bp = Blueprint("feedback", __name__, url_prefix="/feedback")

PROJECT_ROOT = Path(__file__).resolve().parents[2]
JOBS_ROOT = PROJECT_ROOT / "uploads" / "jobs"

REVIEW_QUESTIONS = [
    {
        "id": "q1_what_gridflow_does",
        "label": "1. After reviewing this, can you explain in your own words what GridFlow does?",
        "type": "textarea",
        "required": True,
    },
    {
        "id": "q2_blockers_make_sense",
        "label": "2. Does 0/10 design-ready make sense once you see the missing DNO data?",
        "type": "radio",
        "options": ["Yes, makes complete sense", "Mostly", "Confusing", "No, looks wrong"],
        "required": True,
    },
    {
        "id": "q3_dno_request_clarity",
        "label": "3. Is it clear what data must be requested from the DNO?",
        "type": "radio",
        "options": ["Crystal clear", "Mostly clear", "Some gaps", "Not clear"],
        "required": True,
    },
    {
        "id": "q4_time_savings",
        "label": "4. Would this save time compared with your current workflow?",
        "type": "radio",
        "options": ["Significant savings", "Some savings", "Not sure", "No savings"],
        "required": True,
    },
    {
        "id": "q5_trust_in_blockers",
        "label": "5. Do you trust the blockers, or would you challenge any of them?",
        "type": "textarea",
        "required": True,
    },
    {
        "id": "q6_match_confidence",
        "label": "6. Is match confidence understandable and useful?",
        "type": "radio",
        "options": ["Yes, very useful", "Somewhat useful", "Confusing", "Not useful"],
        "required": True,
    },
    {
        "id": "q7_map_overlay",
        "label": "7. Is the map overlay useful?",
        "type": "radio",
        "options": ["Yes, very useful", "Somewhat useful", "Confusing", "Not useful"],
        "required": True,
    },
    {
        "id": "q8_photo_priority",
        "label": "8. How important is photo/evidence integration before you'd use this on a real job?",
        "type": "radio",
        "options": ["Critical blocker", "High priority", "Nice to have", "Not important"],
        "required": True,
    },
    {
        "id": "q9_use_blockers",
        "label": "9. What would stop you from using GridFlow on a real project right now?",
        "type": "textarea",
        "required": True,
    },
    {
        "id": "q10_first_change",
        "label": "10. If you could change one thing first, what would it be?",
        "type": "textarea",
        "required": True,
    },
]


def _get_job_dir(job_id: str) -> Path:
    return JOBS_ROOT / job_id


@feedback_bp.route("/<job_id>", methods=["GET"])
def feedback_form(job_id: str):
    """Display the feedback form for a registered job."""
    job_dir = _get_job_dir(job_id)

    if not job_dir.exists():
        return render_template(
            "feedback_form.html",
            error=f"Job not found: {job_id}",
            job_id=job_id,
            questions=[],
            existing_feedback=None,
        ), 404

    existing = None
    feedback_path = job_dir / "feedback.json"
    if feedback_path.exists():
        try:
            existing = json.loads(feedback_path.read_text(encoding="utf-8"))
        except Exception as exc:
            logger.warning("Could not load existing feedback for %s: %s", job_id, exc)

    return render_template(
        "feedback_form.html",
        job_id=job_id,
        questions=REVIEW_QUESTIONS,
        existing_feedback=existing,
        error=None,
    )


@feedback_bp.route("/<job_id>/submit", methods=["POST"])
def feedback_submit(job_id: str):
    """Save designer feedback to uploads/jobs/<job_id>/feedback.json."""
    job_dir = _get_job_dir(job_id)

    if not job_dir.exists():
        return f"Job not found: {job_id}", 404

    answers = {
        q["id"]: {
            "question": q["label"],
            "answer": request.form.get(q["id"], "").strip(),
        }
        for q in REVIEW_QUESTIONS
    }

    feedback = {
        "job_id": job_id,
        "submitted_at": datetime.now().isoformat(),
        "designer_name": request.form.get("designer_name", "").strip() or "Anonymous",
        "designer_role": request.form.get("designer_role", "").strip() or "",
        "answers": answers,
        "additional_notes": request.form.get("additional_notes", "").strip(),
    }

    feedback_path = job_dir / "feedback.json"
    if feedback_path.exists():
        try:
            existing = json.loads(feedback_path.read_text(encoding="utf-8"))
            if isinstance(existing, list):
                existing.append(feedback)
                all_feedback = existing
            else:
                all_feedback = [existing, feedback]
        except Exception:
            all_feedback = [feedback]
    else:
        all_feedback = [feedback]

    feedback_path.write_text(json.dumps(all_feedback, indent=2), encoding="utf-8")
    logger.info("Saved feedback for job %s → %s", job_id, feedback_path)

    return render_template(
        "feedback_thanks.html",
        job_id=job_id,
        feedback=feedback,
    )
