# app/routes/map_preview.py
from __future__ import annotations

import json
from pathlib import Path

from flask import Blueprint, jsonify, render_template

map_preview_bp = Blueprint("map_preview", __name__)

PROJECT_ROOT = Path(__file__).resolve().parents[2]
JOBS_ROOT = PROJECT_ROOT / "uploads" / "jobs"


def _empty_feature_collection(job_id: str) -> dict:
    return {
        "type": "FeatureCollection",
        "features": [],
        "metadata": {
            "job_id": job_id,
            "rulepack_id": "SPEN_11kV",
            "auto_normalized": False,
            "pole_count": 0,
            "span_count": 0,
            "pass_count": 0,
            "warn_count": 0,
            "fail_count": 0,
        },
    }


@map_preview_bp.get("/view/<job_id>")
def map_view(job_id: str):
    return render_template("map_viewer.html", job_id=job_id)


@map_preview_bp.get("/data/<job_id>")
def map_data(job_id: str):
    map_path = JOBS_ROOT / job_id / "map_data.json"

    if not map_path.exists():
        return jsonify(_empty_feature_collection(job_id))

    try:
        data = json.loads(map_path.read_text(encoding="utf-8"))
        return jsonify(data)
    except Exception:
        return jsonify(_empty_feature_collection(job_id))
