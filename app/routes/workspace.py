"""
Review Workspace Routes

Web UI for browsing and filtering merged pole data produced by the GridFlow pipeline.
"""

import json
import logging
from pathlib import Path

from flask import Blueprint, render_template, request

from gridflow.workspace import ReviewDataProvider
from gridflow.workspace.review_data_provider import _evidence_quality

logger = logging.getLogger(__name__)

workspace_bp = Blueprint("workspace", __name__, url_prefix="/workspace")

PROJECT_ROOT = Path(__file__).resolve().parents[2]
JOBS_ROOT = PROJECT_ROOT / "uploads" / "jobs"


def _available_jobs(limit: int = 10) -> list[str]:
    """Return job folders that can be offered in workspace error pages."""
    if not JOBS_ROOT.exists():
        return []
    return sorted(d.name for d in JOBS_ROOT.iterdir() if d.is_dir() and not d.name.startswith("."))[
        :limit
    ]


def _pipeline_run_timestamp(job_dir: Path) -> str:
    """Read the latest pipeline run id/date for display in the workspace header."""
    candidates = []
    direct_summary = job_dir / "pipeline_summary.json"
    if direct_summary.exists():
        candidates.append(direct_summary)
    candidates.extend(sorted(job_dir.glob("pipeline_run_*/pipeline_summary.json"), reverse=True))

    for summary_path in candidates:
        try:
            with open(summary_path, encoding="utf-8") as f:
                summary = json.load(f)
            return summary.get("run_id") or summary.get("run_date") or "Unknown"
        except Exception:
            logger.warning("Could not read pipeline summary: %s", summary_path)
    return "Unknown"


@workspace_bp.route("/view/<job_id>")
def view_job(job_id: str):
    """Display review workspace for a job."""
    try:
        job_dir = JOBS_ROOT / job_id
        provider = ReviewDataProvider(job_dir)
        provider.load_job()
        run_timestamp = _pipeline_run_timestamp(job_dir)

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
            run_timestamp=run_timestamp,
        )

    except FileNotFoundError as e:
        logger.error("Job not found: %s — %s", job_id, e)
        return (
            render_template(
                "workspace/error_job_not_found.html",
                job_id=job_id,
                available_jobs=_available_jobs(),
            ),
            404,
        )

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
            all_poles = provider.get_poles()
            return (
                render_template(
                    "workspace/error_pole_not_found.html",
                    job_id=job_id,
                    support_number=support_no,
                    available_poles=[p.support_no for p in all_poles[:20]],
                ),
                404,
            )

        evidence_quality = _evidence_quality(pole)

        return render_template(
            "workspace/pole_detail.html",
            job_id=job_id,
            pole=pole,
            evidence_quality=evidence_quality,
        )

    except FileNotFoundError as e:
        logger.error("Job not found: %s — %s", job_id, e)
        return (
            render_template(
                "workspace/error_job_not_found.html",
                job_id=job_id,
                available_jobs=_available_jobs(),
            ),
            404,
        )

    except Exception as e:
        logger.error("Error loading pole %s: %s", support_no, e, exc_info=True)
        return f"Error loading pole: {e}", 500
