"""
Review Workspace Routes

Web UI for browsing and filtering merged pole data produced by the GridFlow pipeline.
"""

import logging
from pathlib import Path

from flask import Blueprint, render_template, request

from gridflow.workspace import ReviewDataProvider
from gridflow.workspace.review_data_provider import _evidence_quality

logger = logging.getLogger(__name__)

workspace_bp = Blueprint("workspace", __name__, url_prefix="/workspace")

PROJECT_ROOT = Path(__file__).resolve().parents[2]
JOBS_ROOT = PROJECT_ROOT / "uploads" / "jobs"


@workspace_bp.route("/view/<job_id>")
def view_job(job_id: str):
    """Display review workspace for a job."""
    try:
        job_dir = JOBS_ROOT / job_id
        provider = ReviewDataProvider(job_dir)
        provider.load_job()

        filters: dict = {}
        if request.args.get("design_ready") in ("true", "false"):
            filters["design_ready"] = request.args.get("design_ready") == "true"
        if request.args.get("evidence_quality"):
            filters["evidence_quality"] = request.args.get("evidence_quality")
        if request.args.get("match_confidence"):
            filters["match_confidence"] = request.args.get("match_confidence")
        if request.args.get("has_flags") == "true":
            filters["has_flags"] = True

        poles = provider.get_poles(filters)
        stats = provider.get_statistics()

        # Attach derived evidence quality to each pole for the template
        poles_with_eq = [(p, _evidence_quality(p)) for p in poles]

        return render_template(
            "workspace/review_workspace.html",
            job_id=job_id,
            poles_with_eq=poles_with_eq,
            stats=stats,
            active_filters=filters,
        )

    except FileNotFoundError as e:
        logger.error("Job not found: %s — %s", job_id, e)
        return f"Job not found: {job_id}", 404

    except Exception as e:
        logger.error("Error loading workspace for %s: %s", job_id, e, exc_info=True)
        return f"Error loading workspace: {e}", 500


@workspace_bp.route("/pole/<job_id>/<support_no>")
def view_pole(job_id: str, support_no: str):
    """Display detailed view for a single pole."""
    try:
        job_dir = JOBS_ROOT / job_id
        provider = ReviewDataProvider(job_dir)
        provider.load_job()

        pole = provider.get_pole_details(support_no)
        if pole is None:
            return f"Pole not found: {support_no}", 404

        evidence_quality = _evidence_quality(pole)

        return render_template(
            "workspace/pole_detail.html",
            job_id=job_id,
            pole=pole,
            evidence_quality=evidence_quality,
        )

    except FileNotFoundError as e:
        logger.error("Job not found: %s — %s", job_id, e)
        return f"Job not found: {job_id}", 404

    except Exception as e:
        logger.error("Error loading pole %s: %s", support_no, e, exc_info=True)
        return f"Error loading pole: {e}", 500
