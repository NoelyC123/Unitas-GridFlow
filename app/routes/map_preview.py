# app/routes/map_preview.py
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from flask import Blueprint, jsonify, render_template

from app.asset_classifier import classify_asset_type, get_popup_type_label
from app.cable_generator import attach_cable_features_to_collection
from app.context_crossing import enrich_context_crossing_records
from app.duplicate_detection import apply_duplicate_detection
from app.electrical_schema import (
    merge_electrical_fields_into_props,
    merge_equipment_fields_into_props,
    strip_network_electrical_from_point_props,
)
from app.field_ownership import (
    finalize_field_ownership_metadata,
    point_map_electrical_violations,
    validate_map_feature_collection_field_ownership,
)
from app.geometry_pipeline import normalize_geometry_for_span_generation
from app.pole_field_schema import (
    enrich_pole_support_props,
    popup_priority_field_catalog,
    popup_schema_contract,
)
from app.qa_engine import classify_height_confidence, classify_source_confidence, parse_attachments
from app.replacement_pairs import enrich_replacement_pair_intelligence
from app.span_generator import attach_span_features_to_collection
from app.survey_connectivity import merge_connectivity_into_props, merge_survey_metadata_into_props

map_preview_bp = Blueprint("map_preview", __name__)

PROJECT_ROOT = Path(__file__).resolve().parents[2]
JOBS_ROOT = PROJECT_ROOT / "uploads" / "jobs"
PROJECTS_ROOT = PROJECT_ROOT / "uploads" / "projects"


POPUP_DATA_FIELDS: dict[str, Any] = {
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
    "third_party_attachments": None,
    "attachments_detail": {},
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
    "stay_types": [],
    "stay_evidence_status": None,
    "nearest_stay_distance_m": None,
    "nearest_stay_point_id": None,
    "stay_bearing": None,
    "stay_configuration": None,
    "anchor_details": None,
    "linked_pole_id": None,
    "route_deviation_deg": None,
    "action_required": None,
    "access_constraint": None,
    "wayleave_notes": None,
    "clearance_measured": None,
    "distance_from_route_m": None,
    "voltage_detail": {},
    "is_overhead": True,
    "is_underground": False,
    "conductor_detail": {},
    "conductor_type_normalized": None,
    "conductor_size": None,
    "conductor_size_description": None,
    "phase_detail": {},
    "cable_type": None,
    "cable_detail": {},
    "cable_size": None,
    "cores_phases": None,
    "equipment_categories": [],
    "equipment_primary_category": None,
    "equipment_type_detail": {},
    "equipment_kva": None,
    "equipment_kva_label": None,
    "equipment_voltage_ratio": None,
    "pole_top_arrangement": None,
    "pole_top_detail": {},
    "insulator_type": None,
    "crossarm_configuration": None,
    "earthing_status": None,
    "asset_plate_id": None,
    "equipment_mounting": None,
    "from_support_id": None,
    "to_support_id": None,
    "parent_support_id": None,
    "parent_structure_id": None,
    "cable_from_asset_id": None,
    "cable_to_asset_id": None,
    "connectivity_parent_pole": None,
    "survey_job_ref": None,
    "equipment_used": None,
    "survey_limitations": None,
    "gnss_fix_type": None,
    "horizontal_accuracy_m": None,
    "vertical_accuracy_m": None,
    "gnss_accuracy_summary": None,
    "capture_method_key": None,
    "capture_method_label": None,
    "burial_depth_m": None,
    "ducting_type": None,
    "point_id": None,
    "material": None,
    "species": None,
    "treatment": None,
    "decay_location": None,
    "decay_severity": None,
    "measured_height_m": None,
    "proposed_height_m": None,
    "specification": None,
    "specification_source": None,
    "purpose": None,
    "unresolved_decisions": [],
    "qa_status": None,
    "review_category": None,
    "design_impact": None,
    "lifecycle_state": None,
    "replacement_status": None,
    "linked_support_id": None,
    "parent_pole_id": None,
    "support_schema_role": None,
}


def _empty_feature_collection(job_id: str) -> dict[str, Any]:
    return {
        "type": "FeatureCollection",
        "features": [],
        "design_chain_spans": [],
        "span_features": [],
        "cable_features": [],
        "metadata": {
            "job_id": job_id,
            "rulepack_id": "SPEN_11kV",
            "auto_normalized": False,
            "pole_count": 0,
            "pass_count": 0,
            "warn_count": 0,
            "fail_count": 0,
            "design_chain_span_count": 0,
            "popup_priority_field_catalog": popup_priority_field_catalog(),
            "popup_schema_contract": popup_schema_contract(),
        },
    }


def _safe_float(value: object) -> float | None:
    try:
        if value is None or value == "":
            return None
        return float(value)
    except (TypeError, ValueError):
        return None


def _build_design_chain_spans(seq: dict[str, Any]) -> list[dict[str, Any]]:
    chain = seq.get("chain") or []
    spans: list[dict[str, Any]] = []

    for index in range(len(chain) - 1):
        start = chain[index] or {}
        end = chain[index + 1] or {}

        start_lat = _safe_float(start.get("lat"))
        start_lon = _safe_float(start.get("lon"))
        end_lat = _safe_float(end.get("lat"))
        end_lon = _safe_float(end.get("lon"))

        if None in (start_lat, start_lon, end_lat, end_lon):
            continue

        spans.append(
            {
                "from_point_id": start.get("point_id"),
                "to_point_id": end.get("point_id"),
                "from_design_pole_no": start.get("design_pole_number"),
                "to_design_pole_no": end.get("design_pole_number"),
                "section_id": start.get("section_id"),
                "distance_m": _safe_float(start.get("span_to_next_m")),
                "coordinates": [[start_lat, start_lon], [end_lat, end_lon]],
            }
        )

    return spans


def _load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}
    return payload if isinstance(payload, dict) else {}


def _copy_default(default: Any) -> Any:
    if isinstance(default, list):
        return list(default)
    if isinstance(default, dict):
        return dict(default)
    return default


def _ensure_metadata_contract(data: dict[str, Any]) -> dict[str, Any]:
    metadata = data.setdefault("metadata", {})
    if not isinstance(metadata, dict):
        metadata = {}
        data["metadata"] = metadata

    metadata.setdefault("popup_priority_field_catalog", popup_priority_field_catalog())
    metadata.setdefault("popup_schema_contract", popup_schema_contract())
    metadata.setdefault("design_chain_span_count", len(data.get("design_chain_spans") or []))
    return metadata


def _backfill_popup_fields(props: dict[str, Any]) -> None:
    for field, default in POPUP_DATA_FIELDS.items():
        if field not in props:
            props[field] = _copy_default(default)


def _enrich_point_feature(feature: dict[str, Any]) -> int:
    props = feature.setdefault("properties", {})
    if not isinstance(props, dict):
        props = {}
        feature["properties"] = props

    _backfill_popup_fields(props)

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

    if not props.get("attachments_detail"):
        props["attachments_detail"] = parse_attachments(props)

    point_leaks = len(point_map_electrical_violations(props))

    strip_network_electrical_from_point_props(props)
    merge_equipment_fields_into_props(props)
    merge_connectivity_into_props(props)
    merge_survey_metadata_into_props(props)
    enrich_pole_support_props(props)

    if props.get("photo_links") and not props.get("photo_count"):
        props["photo_count"] = len(props.get("photo_links") or [])

    return point_leaks


def _enrich_popup_data_model(data: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(data, dict):
        return data

    data.setdefault("features", [])
    data.setdefault("span_features", [])
    data.setdefault("cable_features", [])
    data.setdefault("design_chain_spans", [])

    _ensure_metadata_contract(data)

    point_leak_total = 0
    for feature in data.get("features") or []:
        if not isinstance(feature, dict) or feature.get("type") != "Feature":
            continue

        geometry = feature.get("geometry")
        if not isinstance(geometry, dict) or geometry.get("type") != "Point":
            continue

        point_leak_total += _enrich_point_feature(feature)

    for span_feature in data.get("span_features") or []:
        if not isinstance(span_feature, dict):
            continue
        props = span_feature.get("properties")
        if isinstance(props, dict):
            merge_electrical_fields_into_props(props)

    for cable_feature in data.get("cable_features") or []:
        if not isinstance(cable_feature, dict):
            continue
        props = cable_feature.get("properties")
        if isinstance(props, dict):
            merge_electrical_fields_into_props(props)

    enrich_context_crossing_records(data)
    enrich_replacement_pair_intelligence(data)

    apply_duplicate_detection(data.get("features") or [])

    post_violations = validate_map_feature_collection_field_ownership(data)
    finalize_field_ownership_metadata(
        data,
        point_leak_total=point_leak_total,
        post_enrichment_violations=post_violations,
    )

    _ensure_metadata_contract(data)
    return data


def _enrich_with_design_chain_spans(data: dict[str, Any], seq_path: Path) -> dict[str, Any]:
    if not isinstance(data, dict):
        return _empty_feature_collection("unknown")

    data.setdefault("features", [])
    data.setdefault("span_features", [])
    data.setdefault("cable_features", [])
    data.setdefault("design_chain_spans", [])

    seq_payload = _load_json(seq_path)

    try:
        cleaned = normalize_geometry_for_span_generation(data.get("features") or [], seq_payload)
        cleaned_seq = getattr(cleaned, "sequence_payload", None) or seq_payload
    except Exception:
        cleaned_seq = seq_payload

    attach_span_features_to_collection(data, cleaned_seq)
    attach_cable_features_to_collection(data)

    spans = _build_design_chain_spans(cleaned_seq)
    data["design_chain_spans"] = spans

    metadata = _ensure_metadata_contract(data)
    metadata["design_chain_span_count"] = len(spans)

    return _enrich_popup_data_model(data)


def _template_context_from_meta(meta: dict[str, Any]) -> dict[str, Any]:
    return {
        "completeness": meta.get("completeness") or {},
        "design_readiness": meta.get("design_readiness") or {},
        "circuit_summary": meta.get("circuit_summary") or {},
        "top_design_risks": meta.get("top_design_risks") or [],
        "replacement_narratives": meta.get("replacement_narratives") or [],
        "recommended_actions": meta.get("recommended_actions") or [],
        "evidence_gates": meta.get("evidence_gates") or [],
        "sequence_summary": meta.get("sequence_summary") or {},
    }


@map_preview_bp.get("/view/<job_id>")
def map_view(job_id: str):
    meta = _load_json(JOBS_ROOT / job_id / "meta.json")
    return render_template(
        "map_viewer.html",
        job_id=job_id,
        **_template_context_from_meta(meta),
    )


@map_preview_bp.get("/data/<job_id>")
def map_data(job_id: str):
    map_path = JOBS_ROOT / job_id / "map_data.json"
    seq_path = JOBS_ROOT / job_id / "sequenced_route.json"

    if not map_path.exists():
        return jsonify(_empty_feature_collection(job_id))

    try:
        data = _load_json(map_path)
        if not data:
            return jsonify(_empty_feature_collection(job_id))
        return jsonify(_enrich_with_design_chain_spans(data, seq_path))
    except Exception:
        return jsonify(_empty_feature_collection(job_id))


@map_preview_bp.get("/view/project/<project_id>/<file_id>")
def project_map_view(project_id: str, file_id: str):
    file_dir = PROJECTS_ROOT / project_id / "files" / file_id
    meta = _load_json(file_dir / "meta.json")
    display_id = f"{project_id}/{file_id}"

    return render_template(
        "map_viewer.html",
        job_id=display_id,
        map_data_url=f"/map/data/project/{project_id}/{file_id}",
        project_id=project_id,
        file_id=file_id,
        d2d_url=f"/d2d/export/project/{project_id}/{file_id}",
        d2d_interleaved_url=f"/d2d/interleaved/project/{project_id}/{file_id}",
        pdf_url=f"/pdf/qa/project/{project_id}/{file_id}",
        back_url=f"/project/{project_id}",
        **_template_context_from_meta(meta),
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
        data = _load_json(map_path)
        if not data:
            return jsonify(_empty_feature_collection(display_id))
        return jsonify(_enrich_with_design_chain_spans(data, seq_path))
    except Exception:
        return jsonify(_empty_feature_collection(display_id))
