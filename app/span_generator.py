"""GeoJSON span (LineString) generation for circuit electrical display.

Phase 3A: electrical enrichment belongs on spans (segment between sequenced poles),
not duplicated on pole points. Coordinates follow GeoJSON order: [lon, lat].
"""

from __future__ import annotations

import math
from typing import Any

from app.electrical_schema import merge_electrical_fields_into_props
from app.qa_engine import infer_display_network_fields

EARTH_RADIUS_M = 6371000.0


def haversine_distance_m(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Great-circle distance in metres between two WGS84 points."""
    rlat1 = math.radians(lat1)
    rlat2 = math.radians(lat2)
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat / 2) ** 2 + math.cos(rlat1) * math.cos(rlat2) * math.sin(dlon / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(max(0.0, 1.0 - a)))
    return round(EARTH_RADIUS_M * c, 1)


def _safe_float(v: Any) -> float | None:
    try:
        if v is None or v == "":
            return None
        x = float(v)
        if math.isnan(x) or math.isinf(x):
            return None
        return x
    except (TypeError, ValueError):
        return None


def _norm_id(v: Any) -> str | None:
    if v is None:
        return None
    s = str(v).strip()
    return s or None


def index_point_features_by_pole_id(features: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    """Map pole_id string -> feature properties (live dict reference)."""
    out: dict[str, dict[str, Any]] = {}
    for feat in features:
        if not isinstance(feat, dict) or feat.get("type") != "Feature":
            continue
        geom = feat.get("geometry")
        if not isinstance(geom, dict) or geom.get("type") != "Point":
            continue
        props = feat.get("properties")
        if not isinstance(props, dict):
            continue
        pid = _norm_id(props.get("pole_id"))
        if pid:
            out[pid] = props
    return out


def coalesce_electrical_source(
    from_props: dict[str, Any],
    to_props: dict[str, Any],
    rulepack_id: str | None,
) -> dict[str, Any]:
    """Merge CSV/network electrical fields from span endpoints (prefer from, then to)."""

    def pick(key: str, a: dict[str, Any], b: dict[str, Any]) -> Any:
        va = a.get(key)
        vb = b.get(key)
        if va not in (None, ""):
            return va
        if vb not in (None, ""):
            return vb
        return None

    # infer_display_network_fields expects row-like dicts
    from_nf = infer_display_network_fields(from_props, rulepack_id)
    to_nf = infer_display_network_fields(to_props, rulepack_id)

    merged: dict[str, Any] = {}
    for key in (
        "voltage",
        "conductor_type",
        "conductor_size",
        "cable_type",
        "route_type",
        "phase_count",
    ):
        merged[key] = pick(key, from_nf, to_nf) or pick(
            key,
            from_props,
            to_props,
        )
    merged["line_voltage"] = merged.get("voltage")
    merged["conductor"] = merged.get("conductor_type")
    merged["phases"] = merged.get("phase_count")
    merged["cores_phases"] = pick("cores_phases", from_props, to_props)
    return merged


def build_span_feature(
    from_pid: str,
    to_pid: str,
    from_lon: float,
    from_lat: float,
    to_lon: float,
    to_lat: float,
    from_props: dict[str, Any],
    to_props: dict[str, Any],
    *,
    rulepack_id: str | None,
    distance_m: float | None,
    section_id: Any = None,
    from_design_pole_no: Any = None,
    to_design_pole_no: Any = None,
    span_index: int = 0,
) -> dict[str, Any]:
    """One GeoJSON Feature: LineString + enriched electrical properties."""

    dist = distance_m
    if dist is None:
        dist = haversine_distance_m(from_lat, from_lon, to_lat, to_lon)

    base = coalesce_electrical_source(from_props, to_props, rulepack_id)
    base["from_point_id"] = from_pid
    base["to_point_id"] = to_pid
    base["from_design_pole_no"] = from_design_pole_no
    base["to_design_pole_no"] = to_design_pole_no
    base["section_id"] = section_id
    base["distance_m"] = dist
    base["span_index"] = span_index
    base["feature_type"] = "circuit_span"

    merge_electrical_fields_into_props(base)

    return {
        "type": "Feature",
        "geometry": {
            "type": "LineString",
            "coordinates": [[from_lon, from_lat], [to_lon, to_lat]],
        },
        "properties": base,
    }


def generate_span_features_geojson(
    point_features: list[dict[str, Any]],
    sequence_payload: dict[str, Any] | None,
    metadata: dict[str, Any] | None = None,
) -> list[dict[str, Any]]:
    """Build span LineString features from point GeoJSON + sequenced_route chain."""

    meta = metadata or {}
    rulepack_id = meta.get("rulepack_id")

    if not sequence_payload or sequence_payload.get("status") != "ok":
        return []

    chain = sequence_payload.get("chain") or []
    if len(chain) < 2:
        return []

    by_pole = index_point_features_by_pole_id(point_features)
    spans: list[dict[str, Any]] = []

    for index in range(len(chain) - 1):
        a = chain[index] or {}
        b = chain[index + 1] or {}
        from_pid = _norm_id(a.get("point_id"))
        to_pid = _norm_id(b.get("point_id"))
        if not from_pid or not to_pid:
            continue

        from_lat = _safe_float(a.get("lat"))
        from_lon = _safe_float(a.get("lon"))
        to_lat = _safe_float(b.get("lat"))
        to_lon = _safe_float(b.get("lon"))
        if None in (from_lat, from_lon, to_lat, to_lon):
            continue

        from_props = by_pole.get(from_pid, {})
        to_props = by_pole.get(to_pid, {})

        dist = _safe_float(a.get("span_to_next_m"))
        spans.append(
            build_span_feature(
                from_pid,
                to_pid,
                from_lon,
                from_lat,
                to_lon,
                to_lat,
                from_props,
                to_props,
                rulepack_id=rulepack_id,
                distance_m=dist,
                section_id=a.get("section_id"),
                from_design_pole_no=a.get("design_pole_number"),
                to_design_pole_no=b.get("design_pole_number"),
                span_index=len(spans),
            )
        )

    return spans


def attach_span_features_to_collection(
    collection: dict[str, Any], sequence_payload: dict[str, Any]
) -> None:
    """Mutates a FeatureCollection dict in place: sets ``span_features`` and metadata count."""

    feats = collection.get("features")
    if not isinstance(feats, list):
        feats = []
    meta = collection.get("metadata")
    if not isinstance(meta, dict):
        meta = {}
        collection["metadata"] = meta

    span_features = generate_span_features_geojson(feats, sequence_payload, meta)
    collection["span_features"] = span_features
    meta["span_feature_count"] = len(span_features)
