"""Phase 3D — electrical field ownership for map FeatureCollections.

Survey **Points** (poles, stays, context, third-party) must not carry line network
electrical attributes in the map API response. Those values are coalesced onto
**span_features** and **cable_features** LineStrings only.

See ``FIELD_OWNERSHIP_MATRIX`` and ``validate_map_feature_collection_field_ownership``.
"""

from __future__ import annotations

from typing import Any

from app.electrical_schema import (
    POINT_ALL_FORBIDDEN_ELECTRICAL_KEYS,
    POINT_ELECTRICAL_POPUP_KEYS,
    strip_network_electrical_from_point_props,
)

FIELD_OWNERSHIP_MATRIX: dict[str, Any] = {
    "policy_version": 2,
    "policy_name": "network_electrical_on_spans_and_cables_only",
    "survey_point": {
        "geometry_types": frozenset({"Point"}),
        "roles": ("pole", "stay", "anchor", "context", "third_party", "other"),
        "forbidden_electrical_keys": POINT_ALL_FORBIDDEN_ELECTRICAL_KEYS,
        "notes": (
            "No voltage/conductor/phase/cable enriched display on Points; "
            "use span_features / cable_features for circuit electrical data."
        ),
    },
    "span_linestring": {
        "storage": "span_features[]",
        "geometry_types": frozenset({"LineString"}),
        "owns_network_electrical": POINT_ALL_FORBIDDEN_ELECTRICAL_KEYS,
    },
    "cable_linestring": {
        "storage": "cable_features[]",
        "geometry_types": frozenset({"LineString"}),
        "owns_network_electrical": POINT_ALL_FORBIDDEN_ELECTRICAL_KEYS,
    },
}


def _is_significant_value(value: Any) -> bool:
    if value is None or value == "":
        return False
    if isinstance(value, dict) and len(value) == 0:
        return False
    return True


def point_enriched_electrical_leaks(props: dict[str, Any]) -> list[str]:
    """Pre-strip: enriched-display keys that must move to spans/cables."""
    out: list[str] = []
    for k in POINT_ELECTRICAL_POPUP_KEYS:
        if k in props and _is_significant_value(props.get(k)):
            out.append(k)
    return out


def point_map_electrical_violations(props: dict[str, Any]) -> list[str]:
    """Any forbidden electrical key present with a significant value (pre- or post-strip check)."""
    out: list[str] = []
    for k in POINT_ALL_FORBIDDEN_ELECTRICAL_KEYS:
        if k in props and _is_significant_value(props.get(k)):
            out.append(k)
    return out


def strip_enriched_electrical_from_point_props(props: dict[str, Any]) -> None:
    """Backward-compatible alias for tests; prefer ``strip_network_electrical_from_point_props``."""
    strip_network_electrical_from_point_props(props)


def validate_map_feature_collection_field_ownership(data: dict[str, Any]) -> list[str]:
    """Validate Point features after enrichment: no forbidden electrical keys."""
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
        for key in point_map_electrical_violations(props):
            violations.append(f"point pole_id={pid!r} has forbidden electrical key {key!r}")
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
        "policy_version": 2,
        "policy": "network_electrical_on_spans_and_cables_only",
        "point_electrical_keys_found_pre_strip": point_leak_total,
        "point_features": point_count,
        "span_features": span_n,
        "cable_features": cab_n,
        "enriched_spans_merged": span_n,
        "enriched_cables_merged": cab_n,
        "post_enrichment_violation_count": len(viol),
        "post_enrichment_clean": len(viol) == 0,
    }
