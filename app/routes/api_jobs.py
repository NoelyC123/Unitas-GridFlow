# app/routes/api_jobs.py
from __future__ import annotations

import json
from pathlib import Path

from flask import Blueprint, jsonify

from gridflow.workspace import ReviewDataProvider
from gridflow.workspace.readiness_adapter import load_job_readiness_summary
from gridflow.workspace.review_data_provider import _evidence_quality

api_jobs_bp = Blueprint("api_jobs", __name__)

PROJECT_ROOT = Path(__file__).resolve().parents[2]
JOBS_ROOT = PROJECT_ROOT / "uploads" / "jobs"


def _load_meta(meta_path: Path) -> dict | None:
    try:
        return json.loads(meta_path.read_text(encoding="utf-8"))
    except Exception:
        return None


def _job_summary(job_dir: Path) -> dict:
    summary = {
        "workspace_ready": False,
        "readiness_summary": None,
        "evidence_quality_indicator": "RED",
        "photo_count_total": 0,
        "last_assessed_date": None,
        "export_ready": False,
    }
    merged_path = job_dir / "04_merged_dataset.json"
    if not merged_path.exists():
        return summary
    try:
        provider = ReviewDataProvider(job_dir)
        provider.load_job()
        poles = provider.get_poles()
        readiness = load_job_readiness_summary(job_dir, poles)
        evidence_levels = [_evidence_quality(pole) for pole in poles]
        photo_count_total = sum(int(getattr(pole, "field_photo_count", 0) or 0) for pole in poles)
        readiness_path = job_dir / "06_readiness_assessment.json"
        last_assessed = None
        if readiness_path.exists():
            last_assessed = readiness_path.stat().st_mtime

        if evidence_levels and all(level == "HIGH" for level in evidence_levels):
            indicator = "GREEN"
        elif evidence_levels and all(level in {"LOW", "NONE"} for level in evidence_levels):
            indicator = "RED"
        else:
            indicator = "AMBER"

        summary.update(
            {
                "workspace_ready": True,
                "readiness_summary": {
                    "ready": readiness.ready_count,
                    "review": readiness.review_count,
                    "not_ready": readiness.not_ready_count,
                    "insufficient": readiness.insufficient_count,
                    "source": readiness.source,
                },
                "evidence_quality_indicator": indicator,
                "photo_count_total": photo_count_total,
                "last_assessed_date": last_assessed,
                "export_ready": True,
            }
        )
    except Exception:
        return summary
    return summary


@api_jobs_bp.get("/")
def list_jobs():
    jobs = []

    if JOBS_ROOT.exists():
        for meta_path in sorted(JOBS_ROOT.glob("*/meta.json")):
            meta = _load_meta(meta_path)
            if meta:
                jobs.append({**meta, **_job_summary(meta_path.parent)})

    return jsonify({"jobs": jobs})


@api_jobs_bp.get("/<job_id>/status")
def job_status(job_id: str):
    meta_path = JOBS_ROOT / job_id / "meta.json"

    if not meta_path.exists():
        return jsonify({"job_id": job_id, "status": "pending"})

    meta = _load_meta(meta_path)
    if not meta:
        return jsonify({"job_id": job_id, "status": "error", "error": "Invalid meta.json"}), 500

    return jsonify(meta)
