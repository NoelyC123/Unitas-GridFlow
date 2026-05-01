"""Phase 3D — electrical *display* field ownership for map FeatureCollections.

Enriched D2-A electrical presentation (voltage_detail, conductor_detail, etc.)
belongs on **span** and **underground cable** LineStrings, not on pole Points.

Raw CSV echoes (``voltage``, ``conductor_type``, …) may remain on points for
coalescing into spans / cables; those are not stripped here.
"""

from __future__ import annotations

from typing import Any

from app.electrical_schema import (
    POINT_ELECTRICAL_POPUP_KEYS,
    strip_electrical_fields_from_point_props,
)


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


def finalize_field_ownership_metadata(
    data: dict[str, Any],
    *,
    point_leak_total: int,
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
    meta["field_ownership_3d"] = {
        "policy_version": 1,
        "policy": "enriched_electrical_display_on_spans_and_cables_only",
        "point_enriched_electrical_keys_found_pre_strip": point_leak_total,
        "point_features": point_count,
        "span_features": span_n,
        "cable_features": cab_n,
        "enriched_spans_merged": span_n,
        "enriched_cables_merged": cab_n,
    }
