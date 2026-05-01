"""Phase 3D — electrical *display* field ownership for map FeatureCollections.

Enriched D2-A electrical presentation (voltage_detail, conductor_detail, etc.)
belongs on **span** and **underground cable** LineStrings, not on pole Points.

Raw CSV echoes (``voltage``, ``conductor_type``, …) may remain on points for
coalescing into spans / cables; those are not stripped here.

See ``FIELD_OWNERSHIP_MATRIX`` for the machine-readable ownership contract
enforced by ``validate_map_feature_collection_field_ownership``.
"""

from __future__ import annotations

from typing import Any

from app.electrical_schema import (
    POINT_ELECTRICAL_POPUP_KEYS,
    strip_electrical_fields_from_point_props,
)

# Phase 3D — canonical ownership (aligned with PHASE_3_MASTER_ROADMAP § field ownership).
POINT_RAW_NETWORK_ECHO_FIELDS: frozenset[str] = frozenset(
    {
        "voltage",
        "line_voltage",
        "conductor_type",
        "conductor",
        "phase_count",
        "phases",
        "circuit_id",
    }
)

FIELD_OWNERSHIP_MATRIX: dict[str, Any] = {
    "policy_version": 1,
    "policy_name": "enriched_electrical_display_on_spans_and_cables_only",
    "point": {
        "geometry_types": frozenset({"Point"}),
        "forbidden_enriched_electrical_keys": POINT_ELECTRICAL_POPUP_KEYS,
        "allowed_raw_network_echo_fields": POINT_RAW_NETWORK_ECHO_FIELDS,
        "notes": (
            "Poles carry structure/survey/raw network echoes; "
            "enriched electrical display is stripped before map response."
        ),
    },
    "span_linestring": {
        "storage": "span_features[]",
        "geometry_types": frozenset({"LineString"}),
        "owns_enriched_electrical_display": POINT_ELECTRICAL_POPUP_KEYS,
        "notes": "Overhead span coalesces endpoint echoes into enriched props here.",
    },
    "underground_cable_linestring": {
        "storage": "cable_features[]",
        "geometry_types": frozenset({"LineString"}),
        "owns_enriched_electrical_display": POINT_ELECTRICAL_POPUP_KEYS,
        "notes": "UG cable segments carry routing + enriched electrical display.",
    },
}


def _is_significant_enriched_value(value: Any) -> bool:
    if value is None or value == "":
        return False
    if isinstance(value, dict) and len(value) == 0:
        return False
    return True


def point_enriched_electrical_leaks(props: dict[str, Any]) -> list[str]:
    """Return POINT keys that should not be on a pole after enrichment (pre-strip)."""
    out: list[str] = []
    for k in POINT_ELECTRICAL_POPUP_KEYS:
        if k in props and _is_significant_enriched_value(props.get(k)):
            out.append(k)
    return out


def strip_enriched_electrical_from_point_props(props: dict[str, Any]) -> None:
    """Remove enriched electrical display keys from a Point feature (alias)."""
    strip_electrical_fields_from_point_props(props)


def validate_map_feature_collection_field_ownership(data: dict[str, Any]) -> list[str]:
    """Return human-readable violations: Point features must not carry enriched electrical display.

    Call **after** map enrichment (strip + span/cable merge). Empty list means Phase 3D clean.
    """
    violations: list[str] = []
    feats = data.get("features") or []
    if not isinstance(feats, list):
        return ["features is not a list"]
    for idx, feat in enumerate(feats):
        if not isinstance(feat, dict) or feat.get("type") != "Feature":
            continue
        geom = feat.get("geometry")
        if not isinstance(geom, dict) or geom.get("type") != "Point":
            continue
        props = feat.get("properties")
        if not isinstance(props, dict):
            continue
        pid = props.get("pole_id") or props.get("point_id") or idx
        for key in point_enriched_electrical_leaks(props):
            violations.append(f"point pole_id={pid!r} has forbidden enriched key {key!r}")
    return violations


def finalize_field_ownership_metadata(
    data: dict[str, Any],
    *,
    point_leak_total: int,
    post_enrichment_violations: list[str] | None = None,
) -> None:
    """Write Phase 3D audit block under ``metadata`` (mutates ``data``)."""
    meta = data.setdefault("metadata", {})
    if not isinstance(meta, dict):
        return
    span_n = (
        len(data.get("span_features") or []) if isinstance(data.get("span_features"), list) else 0
    )
    cab_n = (
        len(data.get("cable_features") or []) if isinstance(data.get("cable_features"), list) else 0
    )
    pts = data.get("features") or []
    point_count = sum(
        1
        for f in pts
        if isinstance(f, dict)
        and f.get("type") == "Feature"
        and isinstance(f.get("geometry"), dict)
        and f["geometry"].get("type") == "Point"
    )
    viol = post_enrichment_violations if post_enrichment_violations is not None else []
    meta["field_ownership_3d"] = {
        "policy_version": 1,
        "policy": "enriched_electrical_display_on_spans_and_cables_only",
        "point_enriched_electrical_keys_found_pre_strip": point_leak_total,
        "point_features": point_count,
        "span_features": span_n,
        "cable_features": cab_n,
        "enriched_spans_merged": span_n,
        "enriched_cables_merged": cab_n,
        "post_enrichment_violation_count": len(viol),
        "post_enrichment_clean": len(viol) == 0,
    }
