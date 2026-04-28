# app/routes/map_preview.py
from __future__ import annotations

import json
from pathlib import Path

from flask import Blueprint, jsonify, render_template

map_preview_bp = Blueprint("map_preview", __name__)

PROJECT_ROOT = Path(__file__).resolve().parents[2]
JOBS_ROOT = PROJECT_ROOT / "uploads" / "jobs"
PROJECTS_ROOT = PROJECT_ROOT / "uploads" / "projects"


def _empty_feature_collection(job_id: str) -> dict:
    return {
        "type": "FeatureCollection",
        "features": [],
        "design_chain_spans": [],
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


def _safe_float(value: object) -> float | None:
    try:
        if value is None or value == "":
            return None
        return float(value)
    except (TypeError, ValueError):
        return None


def _build_design_chain_spans(seq: dict) -> list[dict]:
    """Build a lightweight Leaflet-friendly span overlay from sequenced route data."""
    chain = seq.get("chain") or []
    spans: list[dict] = []

    for index in range(len(chain) - 1):
        start = chain[index] or {}
        end = chain[index + 1] or {}
        start_lat = _safe_float(start.get("lat"))
        start_lon = _safe_float(start.get("lon"))
        end_lat = _safe_float(end.get("lat"))
        end_lon = _safe_float(end.get("lon"))

        if None in (start_lat, start_lon, end_lat, end_lon):
            continue

        distance_m = _safe_float(start.get("span_to_next_m"))
        spans.append(
            {
                "from_point_id": start.get("point_id"),
                "to_point_id": end.get("point_id"),
                "from_design_pole_no": start.get("design_pole_number"),
                "to_design_pole_no": end.get("design_pole_number"),
                "section_id": start.get("section_id"),
                "distance_m": distance_m,
                "coordinates": [[start_lat, start_lon], [end_lat, end_lon]],
            }
        )

    return spans


def _enrich_with_design_chain_spans(data: dict, seq_path: Path) -> dict:
    """Attach span overlay data without requiring old map_data.json files to be regenerated."""
    if not isinstance(data, dict):
        return data
    if "design_chain_spans" in data:
        return data
    spans: list[dict] = []
    if seq_path.exists():
        try:
            seq = json.loads(seq_path.read_text(encoding="utf-8"))
            if seq.get("status") == "ok":
                spans = _build_design_chain_spans(seq)
        except Exception:
            spans = []
    data["design_chain_spans"] = spans
    metadata = data.setdefault("metadata", {})
    if isinstance(metadata, dict):
        metadata["design_chain_span_count"] = len(spans)
    return data


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
    sequence_summary: dict = {}
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
            sequence_summary = meta.get("sequence_summary") or {}
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
        sequence_summary=sequence_summary,
    )


@map_preview_bp.get("/data/<job_id>")
def map_data(job_id: str):
    map_path = JOBS_ROOT / job_id / "map_data.json"
    seq_path = JOBS_ROOT / job_id / "sequenced_route.json"

    if not map_path.exists():
        return jsonify(_empty_feature_collection(job_id))

    try:
        data = json.loads(map_path.read_text(encoding="utf-8"))
        data = _enrich_with_design_chain_spans(data, seq_path)
        return jsonify(data)
    except Exception:
        return jsonify(_empty_feature_collection(job_id))


def _load_file_meta(file_dir: Path) -> dict:
    meta_path = file_dir / "meta.json"
    if not meta_path.exists():
        return {}
    try:
        return json.loads(meta_path.read_text(encoding="utf-8"))
    except Exception:
        return {}


@map_preview_bp.get("/view/project/<project_id>/<file_id>")
def project_map_view(project_id: str, file_id: str):
    file_dir = PROJECTS_ROOT / project_id / "files" / file_id
    meta = _load_file_meta(file_dir)
    display_id = f"{project_id}/{file_id}"
    return render_template(
        "map_viewer.html",
        job_id=display_id,
        map_data_url=f"/map/data/project/{project_id}/{file_id}",
        project_id=project_id,
        file_id=file_id,
        completeness=meta.get("completeness") or {},
        design_readiness=meta.get("design_readiness") or {},
        circuit_summary=meta.get("circuit_summary") or {},
        top_design_risks=meta.get("top_design_risks") or [],
        replacement_narratives=meta.get("replacement_narratives") or [],
        recommended_actions=meta.get("recommended_actions") or [],
        evidence_gates=meta.get("evidence_gates") or [],
        sequence_summary=meta.get("sequence_summary") or {},
        d2d_url=f"/d2d/export/project/{project_id}/{file_id}",
        d2d_interleaved_url=f"/d2d/interleaved/project/{project_id}/{file_id}",
        pdf_url=f"/pdf/qa/project/{project_id}/{file_id}",
        back_url=f"/project/{project_id}",
    )


@map_preview_bp.get("/data/project/<project_id>/<file_id>")
def project_map_data(project_id: str, file_id: str):
    display_id = f"{project_id}/{file_id}"
    file_dir = PROJECTS_ROOT / project_id / "files" / file_id
    map_path = file_dir / "map_data.json"
    seq_path = file_dir / "sequenced_route.json"
    if not map_path.exists():
        return jsonify(_empty_feature_collection(display_id))
    try:
        data = json.loads(map_path.read_text(encoding="utf-8"))
        data = _enrich_with_design_chain_spans(data, seq_path)
        return jsonify(data)
    except Exception:
        return jsonify(_empty_feature_collection(display_id))
