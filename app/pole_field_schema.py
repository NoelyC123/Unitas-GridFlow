"""Phase 3E — pole / support field groups: universal + role-specific presentation keys.

Canonical names align with PHASE_3_MASTER_ROADMAP § Pole/support redesign. Intake may still
use legacy keys (``pole_id``, ``height``, …); map enrichment copies into these slots
when missing.
"""

from __future__ import annotations

from typing import Any

# Universal map-point fields (identity, capture, QA) — documentation / validation sets.
UNIVERSAL_POINT_FIELDS: frozenset[str] = frozenset(
    {
        "pole_id",
        "point_id",
        "structure_type",
        "primary_type",
        "record_role",
        "asset_intent",
        "popup_type_label",
        "lat",
        "lon",
        "easting",
        "northing",
        "elevation",
        "crs",
        "circuit_id",
        "surveyor",
        "survey_date",
        "gnss_accuracy",
        "horizontal_accuracy_m",
        "vertical_accuracy_m",
        "gnss_fix_type",
        "capture_method",
        "capture_method_label",
        "survey_job_ref",
        "source_confidence",
        "source_confidence_detail",
        "height_confidence",
        "photo_links",
        "photo_count",
        "qa_status",
        "review_category",
        "design_impact",
        "lifecycle_state",
        "replacement_status",
        "linked_support_id",
    }
)

EXISTING_POLE_FIELDS: frozenset[str] = frozenset(
    {
        "measured_height_m",
        "height_source",
        "pole_class",
        "material",
        "species",
        "treatment",
        "year_installed",
        "condition",
        "defect_type",
        "decay_location",
        "decay_severity",
        "lean_direction",
        "lean_severity",
        "foundation_type",
        "access_constraint",
    }
)

PROPOSED_POLE_FIELDS: frozenset[str] = frozenset(
    {
        "proposed_height_m",
        "specification",
        "specification_source",
        "purpose",
        "unresolved_decisions",
        "pole_class",
        "material",
    }
)

ANGLE_POLE_FIELDS: frozenset[str] = frozenset(
    {
        "route_deviation_deg",
        "stay_present",
        "stay_type",
        "stay_bearing",
        "stay_configuration",
        "stay_evidence_status",
        "nearest_stay_distance_m",
    }
)

STAY_ANCHOR_FIELDS: frozenset[str] = frozenset(
    {
        "parent_support_id",
        "parent_pole_id",
        "stay_type",
        "stay_bearing",
        "anchor_details",
        "linked_pole_id",
    }
)


def _norm_st(props: dict[str, Any]) -> str:
    return str(props.get("structure_type") or "").strip().lower()


def _norm_role(props: dict[str, Any]) -> str:
    return str(props.get("record_role") or "").strip().lower()


def infer_support_schema_role(props: dict[str, Any]) -> str:
    """Return ``existing`` | ``proposed`` | ``angle`` | ``stay`` | ``context`` | ``third_party``."""
    if str(props.get("primary_type") or "") == "third_party_infrastructure":
        return "third_party"
    role = _norm_role(props)
    if role == "context":
        return "context"
    st = _norm_st(props)
    intent = str(props.get("asset_intent") or "").lower()
    if role == "anchor" or "stay" in st or "anchor" in st:
        return "stay"
    if "angle" in st:
        return "angle"
    if "prpole" in st or st == "pol" or "proposed" in intent:
        return "proposed"
    if "expole" in st or "existing" in intent:
        return "existing"
    if props.get("being_replaced_by") or props.get("replacing"):
        return "existing" if "expole" in st else "proposed"
    return "existing"


def field_groups_for_role(role: str) -> list[frozenset[str]]:
    """Ordered field group sets for the given support role."""
    u = UNIVERSAL_POINT_FIELDS
    if role == "stay":
        return [u, STAY_ANCHOR_FIELDS]
    if role == "angle":
        return [u, EXISTING_POLE_FIELDS, ANGLE_POLE_FIELDS]
    if role == "proposed":
        return [u, PROPOSED_POLE_FIELDS]
    if role in ("context", "third_party"):
        return [u]
    return [u, EXISTING_POLE_FIELDS]


def _coerce_float(val: Any) -> float | None:
    if val is None or val == "":
        return None
    try:
        return float(val)
    except (TypeError, ValueError):
        return None


def enrich_pole_support_props(props: dict[str, Any]) -> None:
    """Derive Phase 3E canonical pole/support keys (mutates ``props``)."""
    pid = props.get("pole_id")
    if pid is not None and props.get("point_id") in (None, ""):
        props["point_id"] = pid

    role = infer_support_schema_role(props)

    h = _coerce_float(props.get("height"))
    if role == "proposed":
        if h is not None and props.get("proposed_height_m") in (None, ""):
            props["proposed_height_m"] = h
    else:
        if h is not None and props.get("measured_height_m") in (None, ""):
            props["measured_height_m"] = h

    if props.get("parent_support_id") and not props.get("parent_pole_id"):
        props["parent_pole_id"] = props.get("parent_support_id")

    bb = props.get("being_replaced_by")
    rp = props.get("replacing")
    if bb:
        props["replacement_status"] = "being_replaced"
        props["linked_support_id"] = bb
    elif rp:
        props["replacement_status"] = "replacing_existing"
        props["linked_support_id"] = rp
    elif props.get("replacement_status") in (None, ""):
        props["replacement_status"] = "independent"

    lc = str(props.get("lifecycle_state") or "").strip().lower()
    if lc and props.get("purpose") in (None, ""):
        if "replac" in lc and bb:
            props["purpose"] = f"Replacement lifecycle: {lc}"

    if not isinstance(props.get("unresolved_decisions"), list):
        props["unresolved_decisions"] = []
    ud = props["unresolved_decisions"]
    if len(ud) == 0:
        auto: list[str] = []
        if role == "proposed" and not props.get("height"):
            auto.append("design_height_to_confirm")
        if role == "angle" and props.get("stay_evidence_status") == "missing":
            auto.append("stay_evidence_required")
        if role == "existing" and not props.get("height_source"):
            auto.append("height_source_to_confirm")
        if auto:
            props["unresolved_decisions"] = auto

    props["support_schema_role"] = role


def validate_support_field_coverage(props: dict[str, Any]) -> list[str]:
    """Return human-readable gaps for test / QA (not a rulepack verdict)."""
    role = str(props.get("support_schema_role") or infer_support_schema_role(props))
    notes: list[str] = []
    if role == "existing":
        if props.get("measured_height_m") in (None, "") and props.get("height") in (None, ""):
            notes.append("existing_pole_height_missing")
    if role == "proposed":
        if props.get("proposed_height_m") in (None, "") and props.get("height") in (None, ""):
            notes.append("proposed_height_missing")
    if role == "stay" and not props.get("parent_pole_id") and not props.get("parent_support_id"):
        notes.append("stay_parent_missing")
    return notes
