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
            "pass_count": 0,
            "warn_count": 0,
            "fail_count": 0,
        },
    }


@map_preview_bp.get("/view/<job_id>")
def map_view(job_id: str):
    meta_path = JOBS_ROOT / job_id / "meta.json"
    completeness: dict = {}
    design_readiness: dict = {}
    circuit_summary: dict = {}
    top_design_risks: list = []
    replacement_narratives: list = []
    recommended_actions: list = []
    evidence_gates: list = []
    if meta_path.exists():
        try:
            meta = json.loads(meta_path.read_text(encoding="utf-8"))
            completeness = meta.get("completeness") or {}
            design_readiness = meta.get("design_readiness") or {}
            circuit_summary = meta.get("circuit_summary") or {}
            top_design_risks = meta.get("top_design_risks") or []
            replacement_narratives = meta.get("replacement_narratives") or []
            recommended_actions = meta.get("recommended_actions") or []
            evidence_gates = meta.get("evidence_gates") or []
        except Exception:
            pass
    return render_template(
        "map_viewer.html",
        job_id=job_id,
        completeness=completeness,
        design_readiness=design_readiness,
        circuit_summary=circuit_summary,
        top_design_risks=top_design_risks,
        replacement_narratives=replacement_narratives,
        recommended_actions=recommended_actions,
        evidence_gates=evidence_gates,
    )


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
