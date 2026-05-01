# app/routes/map_preview.py
from __future__ import annotations

import json
from pathlib import Path

from flask import Blueprint, jsonify, render_template

from app.asset_classifier import classify_asset_type, get_popup_type_label
from app.qa_engine import classify_height_confidence, classify_source_confidence

map_preview_bp = Blueprint("map_preview", __name__)

PROJECT_ROOT = Path(__file__).resolve().parents[2]
JOBS_ROOT = PROJECT_ROOT / "uploads" / "jobs"
PROJECTS_ROOT = PROJECT_ROOT / "uploads" / "projects"

POPUP_DATA_FIELDS = {
    "height_source": None,
    "height_confidence": {},
    "pole_class": None,
    "condition": None,
    "lean_direction": None,
    "lean_severity": None,
    "defect_type": None,
    "foundation_type": None,
    "voltage": None,
    "conductor_type": None,
    "phase_count": None,
    "equipment": [],
    "equipment_rating": None,
    "surveyor": None,
    "survey_date": None,
    "gnss_accuracy": None,
    "source_confidence": "legacy map data",
    "source_confidence_detail": {},
    "capture_method": None,
    "primary_type": None,
    "infrastructure_owner": None,
    "asset_subtype": None,
    "is_structural_pole": None,
    "is_electric_network": None,
    "classification_confidence": None,
    "classification_warnings": [],
    "classification_basis": None,
    "popup_type_label": None,
    "photo_links": [],
    "has_full_pole_photo": False,
    "has_pole_top_photo": False,
    "has_defect_photo": False,
    "photo_count": 0,
    "elevation": None,
    "year_installed": None,
    "circuit_id": None,
    "stay_present": None,
    "stay_type": None,
    "stay_bearing": None,
    "stay_configuration": None,
    "anchor_details": None,
    "linked_pole_id": None,
    "route_deviation_deg": None,
    "action_required": None,
    "access_constraint": None,
    "clearance_measured": None,
    "distance_from_route_m": None,
}


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


def _infer_voltage(props: dict, metadata: dict) -> str | None:
    st = str(props.get("structure_type") or "").lower()
    rulepack = str(metadata.get("rulepack_id") or "")
    if "11" in st:
        return "11kV"
    if "33" in st:
        return "33kV"
    if "lv" in st:
        return "LV"
    if "11kv" in rulepack.lower() or "11kv" in rulepack.replace("_", "").lower():
        return "11kV"
    return None


def _enrich_popup_data_model(data: dict) -> dict:
    """Backfill C2-2 display fields for previously generated map_data.json files."""
    if not isinstance(data, dict):
        return data
    metadata = data.get("metadata") if isinstance(data.get("metadata"), dict) else {}
    for feature in data.get("features") or []:
        props = feature.get("properties") if isinstance(feature, dict) else None
        if not isinstance(props, dict):
            continue
        for field, default in POPUP_DATA_FIELDS.items():
            if field not in props:
                props[field] = list(default) if isinstance(default, list) else default
        classification = classify_asset_type(props)
        if not props.get("primary_type"):
            props["primary_type"] = classification.get("primary_type")
            props["infrastructure_owner"] = classification.get("infrastructure_owner")
            props["asset_subtype"] = classification.get("subtype")
            props["is_structural_pole"] = bool(classification.get("is_structural_pole"))
            props["is_electric_network"] = bool(classification.get("is_electric_network"))
            props["classification_confidence"] = classification.get("classification_confidence")
            props["classification_warnings"] = classification.get("warnings", [])
            props["classification_basis"] = classification.get("classification_basis")
            props["popup_type_label"] = get_popup_type_label(classification)
        if props.get("primary_type") == "third_party_infrastructure":
            props["record_role"] = "third_party"
            props["asset_intent"] = "third_party_not_network"
        if not props.get("height_confidence"):
            props["height_confidence"] = classify_height_confidence(props)
        if not props.get("source_confidence_detail"):
            props["source_confidence_detail"] = classify_source_confidence(props)
        if not props.get("voltage"):
            props["voltage"] = _infer_voltage(props, metadata)
        if props.get("photo_links") and not props.get("photo_count"):
            props["photo_count"] = len(props.get("photo_links") or [])
    return data


def _enrich_with_design_chain_spans(data: dict, seq_path: Path) -> dict:
    """Attach span overlay data without requiring old map_data.json files to be regenerated."""
    if not isinstance(data, dict):
        return data
    if "design_chain_spans" in data:
        return _enrich_popup_data_model(data)
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
    return _enrich_popup_data_model(data)


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
