"""
Review Workspace Routes

Web UI for browsing and filtering merged pole data produced by the GridFlow pipeline.
"""

import json
import logging
from pathlib import Path
from types import SimpleNamespace

from flask import Blueprint, current_app, render_template, request

from gridflow.conflict_detector import ConflictDetector
from gridflow.evidence_combiner import combine_pole_evidence, link_pole
from gridflow.photos import load_pole_photos
from gridflow.readiness import ReadinessAssessor
from gridflow.timeline import EvidenceTimelineBuilder
from gridflow.workspace import ReviewDataProvider
from gridflow.workspace.enwl_evidence_adapter import (
    load_enwl_pole_evidence,
    load_enwl_trace_summary,
)
from gridflow.workspace.filter_engine import PoleFilterEngine
from gridflow.workspace.readiness_adapter import (
    load_job_readiness_summary,
    load_pole_readiness,
)
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


def _survey_id_from_job(job_dir: Path) -> str | None:
    """Derive survey folder id from merged dataset field_source."""
    merged_path = job_dir / "04_merged_dataset.json"
    if not merged_path.exists():
        return None
    try:
        with open(merged_path, encoding="utf-8") as f:
            data = json.load(f)
        field_source = data.get("field_source") or ""
        field_path = Path(field_source)
        if field_path.name == "enwl_enrichment_clean" and field_path.parent.name:
            return field_path.parent.name
        if field_path.name:
            return field_path.name
    except Exception:
        logger.warning("Could not derive survey_id from %s", merged_path)
    return None


def _survey_root_from_job(job_dir: Path, survey_id: str | None) -> Path | None:
    if not survey_id:
        return None
    root = Path(current_app.config.get("REAL_PILOT_DATA_ROOT", ""))
    if not root:
        return None
    survey_root = root / survey_id
    return survey_root if survey_root.exists() else None


def _trace_path_for_survey(survey_root: Path | None) -> Path | None:
    if survey_root is None:
        return None
    trace_dir = survey_root / "enwl_trace"
    if not trace_dir.exists():
        return None
    matches = sorted(trace_dir.glob("*.geojson"))
    return matches[0] if matches else None


def _to_mapping(value) -> dict:
    if value is None:
        return {}
    if isinstance(value, dict):
        return dict(value)
    if hasattr(value, "to_dict") and callable(value.to_dict):
        return dict(value.to_dict())
    if hasattr(value, "__dict__"):
        return dict(vars(value))
    return {}


@workspace_bp.route("/view/<job_id>")
def view_job(job_id: str):
    """Display review workspace for a job."""
    try:
        job_dir = JOBS_ROOT / job_id
        provider = ReviewDataProvider(job_dir)
        provider.load_job()
        run_timestamp = _pipeline_run_timestamp(job_dir)

        legacy_filters: dict = {}
        if request.args.get("design_ready") in ("true", "false"):
            legacy_filters["design_ready"] = request.args.get("design_ready") == "true"
        if request.args.get("evidence_quality"):
            legacy_filters["evidence_quality"] = request.args.get("evidence_quality")
        if request.args.get("match_confidence"):
            legacy_filters["match_confidence"] = request.args.get("match_confidence")
        if request.args.get("has_flags") == "true":
            legacy_filters["has_flags"] = True

        all_poles = provider.get_poles(legacy_filters)
        stats = provider.get_statistics()

        # Stage 7E: apply search/filter/sort
        search_query = request.args.get("q", "").strip() or None
        status_filter = request.args.get("status") or None
        confidence_filter = request.args.get("confidence") or None
        photos_param = request.args.get("photos")
        has_photos = True if photos_param == "yes" else (False if photos_param == "no" else None)
        conflicts_param = request.args.get("conflicts")
        has_conflicts = (
            True if conflicts_param == "yes" else (False if conflicts_param == "no" else None)
        )
        sort_by = request.args.get("sort") or None

        engine = PoleFilterEngine()
        poles = engine.filter(
            all_poles,
            query=search_query,
            status=status_filter,
            confidence=confidence_filter,
            has_photos=has_photos,
            has_conflicts=has_conflicts,
            sort_by=sort_by,
        )

        active_filters = {
            **legacy_filters,
            "q": search_query,
            "status": status_filter,
            "confidence": confidence_filter,
            "photos": photos_param,
            "conflicts": conflicts_param,
            "sort": sort_by,
        }

        poles_with_eq = [(p, _evidence_quality(p)) for p in poles]

        enwl_summary = load_enwl_trace_summary(job_dir)
        readiness_summary = load_job_readiness_summary(job_dir, all_poles)

        return render_template(
            "workspace/review_workspace.html",
            job_id=job_id,
            poles_with_eq=poles_with_eq,
            total_poles=len(all_poles),
            stats=stats,
            active_filters=active_filters,
            run_timestamp=run_timestamp,
            enwl_summary=enwl_summary,
            readiness_summary=readiness_summary,
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
        survey_id = _survey_id_from_job(job_dir)
        survey_root = _survey_root_from_job(job_dir, survey_id)
        trace_path = _trace_path_for_survey(survey_root)
        photo_set = (
            load_pole_photos(survey_root / "enwl_enrichment_clean" / (pole.folder_name or ""))
            if pole.folder_name and survey_root
            else None
        )
        photos_by_type = (
            {
                photo_type: [
                    photo for photo in photo_set.photo_files if photo.photo_type == photo_type
                ]
                for photo_type in [
                    "full_pole",
                    "pole_top",
                    "pole_base",
                    "equipment",
                    "span",
                    "context",
                    "unknown",
                ]
            }
            if photo_set
            else {}
        )
        pole_view = SimpleNamespace(
            **pole.model_dump(),
            photo_count=photo_set.photo_count if photo_set else pole.field_photo_count,
            photos_by_type=photos_by_type,
            pole_folder=pole.folder_name,
        )
        enwl_evidence = load_enwl_pole_evidence(
            job_dir=job_dir,
            pole_folder_name=pole.folder_name,
            notes_content=pole.notes_content,
        )
        pole_readiness = load_pole_readiness(job_dir, pole)
        readiness_payload = _to_mapping(pole_readiness)
        timeline = EvidenceTimelineBuilder().build(
            pole.folder_name or support_no,
            {
                "pole_id": pole.folder_name or support_no,
                "support_no": pole.support_no,
                "photo_count": photo_set.photo_count if photo_set else pole.field_photo_count,
                "contributing_files": {
                    "pole_folder": str(
                        survey_root / "enwl_enrichment_clean" / (pole.folder_name or "")
                    )
                    if survey_root and pole.folder_name
                    else "",
                    "pole_notes": str(
                        survey_root
                        / "enwl_enrichment_clean"
                        / (pole.folder_name or "")
                        / "notes"
                        / "pole_notes.md"
                    )
                    if survey_root and pole.folder_name
                    else "",
                    "field_photos": str(
                        survey_root
                        / "enwl_enrichment_clean"
                        / (pole.folder_name or "")
                        / "field_photos"
                    )
                    if survey_root and pole.folder_name
                    else "",
                },
                "linking": {},
                "readiness": {
                    **readiness_payload,
                    "assessment_timestamp": _pipeline_run_timestamp(job_dir),
                },
                "conflicts": [],
            },
        )
        if survey_root and trace_path and pole.folder_name:
            try:
                combined = combine_pole_evidence(survey_root, pole.folder_name, trace_path)
                linking = link_pole(survey_root, pole.folder_name, trace_path)
                conflicts = ConflictDetector().detect_pole(
                    survey_root, pole.folder_name, trace_path
                )
                readiness = ReadinessAssessor().assess_from_records(combined, linking, conflicts)
                timeline = EvidenceTimelineBuilder().build(
                    pole.folder_name,
                    {
                        **combined,
                        "linking": linking.to_dict(),
                        "readiness": {
                            **readiness.to_dict(),
                            "assessment_timestamp": _pipeline_run_timestamp(job_dir),
                        },
                        "conflicts": [conflict.to_dict() for conflict in conflicts],
                    },
                )
            except Exception:
                logger.warning(
                    "Could not build evidence timeline for %s/%s",
                    job_id,
                    pole.folder_name,
                    exc_info=True,
                )
        pole_view.timeline = timeline

        return render_template(
            "workspace/pole_detail.html",
            job_id=job_id,
            pole=pole_view,
            evidence_quality=evidence_quality,
            enwl_evidence=enwl_evidence,
            pole_readiness=pole_readiness,
            survey_id=survey_id,
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
