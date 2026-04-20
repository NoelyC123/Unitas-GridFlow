# app/routes/api_jobs.py
from __future__ import annotations

import json
from pathlib import Path

from flask import Blueprint, jsonify

api_jobs_bp = Blueprint("api_jobs", __name__)

PROJECT_ROOT = Path(__file__).resolve().parents[2]
JOBS_ROOT = PROJECT_ROOT / "uploads" / "jobs"


def _load_meta(meta_path: Path) -> dict | None:
    try:
        return json.loads(meta_path.read_text(encoding="utf-8"))
    except Exception:
        return None


@api_jobs_bp.get("/")
def list_jobs():
    jobs = []

    if JOBS_ROOT.exists():
        for meta_path in sorted(JOBS_ROOT.glob("*/meta.json")):
            meta = _load_meta(meta_path)
            if meta:
                jobs.append(meta)

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