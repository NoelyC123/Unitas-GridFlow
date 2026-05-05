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

# Context / crossing-related structure_type tokens
# (aligned with map-viewer.js CONTEXT_FEATURE_CODES).
_HIGH_CLEARANCE_CROSSING_HINTS = frozenset(
    ("road", "track", "xing", "pline", "btxing", "lvxing", "hvxing")
)
_MEDIUM_CROSSING_HINTS = frozenset(("wall", "fence", "gate", "hedge", "tree", "post", "stream"))

_SPAN_CROSSING_BUFFER_HIGH_M = 40.0
_SPAN_CROSSING_BUFFER_MEDIUM_M = 28.0
_SPAN_CROSSING_BUFFER_LOW_M = 18.0


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


def _planar_xy_m(lat: float, lon: float, ref_lat: float, ref_lon: float) -> tuple[float, float]:
    """Local tangent-plane metres (adequate for span-scale distances in UK)."""
    r = math.radians(ref_lat)
    x = (lon - ref_lon) * 111_320.0 * math.cos(r)
    y = (lat - ref_lat) * 110_540.0
    return x, y


def distance_point_to_segment_m(
    lat_p: float,
    lon_p: float,
    lat_a: float,
    lon_a: float,
    lat_b: float,
    lon_b: float,
) -> float:
    """Shortest distance in metres from point P to segment A–B."""
    ref_lat = (lat_a + lat_b + lat_p) / 3.0
    ref_lon = (lon_a + lon_b + lon_p) / 3.0
    px, py = _planar_xy_m(lat_p, lon_p, ref_lat, ref_lon)
    ax, ay = _planar_xy_m(lat_a, lon_a, ref_lat, ref_lon)
    bx, by = _planar_xy_m(lat_b, lon_b, ref_lat, ref_lon)
    abx, aby = bx - ax, by - ay
    apx, apy = px - ax, py - ay
    ab2 = abx * abx + aby * aby
    if ab2 < 1e-9:
        return round(math.hypot(apx, apy), 1)
    t = max(0.0, min(1.0, (apx * abx + apy * aby) / ab2))
    cx, cy = ax + t * abx, ay + t * aby
    return round(math.hypot(px - cx, py - cy), 1)


def _structure_type_lower(props: dict[str, Any]) -> str:
    return str(props.get("structure_type") or "").strip().lower()


def _is_route_context_point(props: dict[str, Any]) -> bool:
    role = str(props.get("record_role") or "").strip().lower()
    if role == "context":
        return True
    st = _structure_type_lower(props)
    if not st:
        return False
    for hint in _HIGH_CLEARANCE_CROSSING_HINTS | _MEDIUM_CROSSING_HINTS:
        if hint in st:
            return True
    if st in (
        "hedge",
        "tree",
        "wall",
        "fence",
        "post",
        "gate",
        "road",
        "track",
        "stream",
        "btxing",
        "lvxing",
        "hvxing",
        "11xing",
        "33xing",
    ):
        return True
    if len(st) <= 6 and st.isalpha():
        _short = {"HEDGE", "TREE", "WALL", "FENCE", "POST", "GATE", "ROAD", "TRACK", "STREAM"}
        if st.upper() in _short:
            return True
    return False


def _crossing_tier_for_structure(st_lower: str) -> str | None:
    if not st_lower:
        return None
    if any(h in st_lower for h in _HIGH_CLEARANCE_CROSSING_HINTS):
        return "high"
    if any(h in st_lower for h in _MEDIUM_CROSSING_HINTS):
        return "medium"
    if st_lower in ("post", "11xing", "33xing"):
        return "medium"
    return "low"


def _iter_context_points(point_features: list[dict[str, Any]]) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for feat in point_features:
        if not isinstance(feat, dict) or feat.get("type") != "Feature":
            continue
        geom = feat.get("geometry")
        if not isinstance(geom, dict) or geom.get("type") != "Point":
            continue
        coords = geom.get("coordinates") or []
        if len(coords) < 2:
            continue
        lon, lat = _safe_float(coords[0]), _safe_float(coords[1])
        if lat is None or lon is None:
            continue
        props = feat.get("properties")
        if not isinstance(props, dict):
            continue
        if not _is_route_context_point(props):
            continue
        pid = (
            _norm_id(props.get("pole_id"))
            or _norm_id(props.get("id"))
            or _norm_id(props.get("name"))
        )
        st = str(props.get("structure_type") or "").strip()
        out.append(
            {
                "pole_id": pid or "",
                "lat": lat,
                "lon": lon,
                "structure_type": st,
                "structure_type_lower": st.lower(),
            }
        )
    return out


def line_segment_crossing_profile(
    from_lat: float,
    from_lon: float,
    to_lat: float,
    to_lon: float,
    point_features: list[dict[str, Any]],
) -> tuple[list[dict[str, Any]], str]:
    """Crossing / route context near a line segment (OHL span or underground cable)."""
    return _hits_for_span(from_lat, from_lon, to_lat, to_lon, _iter_context_points(point_features))


def _hits_for_span(
    from_lat: float,
    from_lon: float,
    to_lat: float,
    to_lon: float,
    context_points: list[dict[str, Any]],
) -> tuple[list[dict[str, Any]], str]:
    """Return crossing hits (sorted by distance) and aggregate crossing_risk_level."""
    hits: list[dict[str, Any]] = []
    for ctx in context_points:
        d = distance_point_to_segment_m(ctx["lat"], ctx["lon"], from_lat, from_lon, to_lat, to_lon)
        tier_token = _crossing_tier_for_structure(ctx["structure_type_lower"])
        if tier_token is None:
            continue
        if tier_token == "high" and d > _SPAN_CROSSING_BUFFER_HIGH_M:
            continue
        if tier_token == "medium" and d > _SPAN_CROSSING_BUFFER_MEDIUM_M:
            continue
        if tier_token == "low" and d > _SPAN_CROSSING_BUFFER_LOW_M:
            continue
        hits.append(
            {
                "point_id": ctx.get("pole_id") or "",
                "structure_type": ctx.get("structure_type") or "",
                "distance_m": d,
                "crossing_tier": tier_token,
            }
        )

    hits.sort(key=lambda h: (h["distance_m"], h["structure_type"]))
    level = "none"
    for h in hits:
        t = h.get("crossing_tier") or "low"
        if t == "high":
            level = "high"
            break
        if t == "medium":
            level = "medium"
        elif t == "low" and level == "none":
            level = "low"
    return hits, level


def derive_designer_actions_for_span(props: dict[str, Any]) -> list[str]:
    """Suggested office actions from span enrichment (advisory, not rulepack verdict)."""
    actions: list[str] = []
    risk = str(props.get("crossing_risk_level") or "none").lower()
    if risk == "high":
        actions.append(
            "Confirm statutory clearance and crossing profile for this span — "
            "road/track/utility crossing context within survey corridor.",
        )
    elif risk == "medium":
        actions.append(
            "Review obstruction / access constraints along this span — fence, wall, watercourse, "
            "or vegetation context near the conductor path.",
        )
    elif risk == "low":
        actions.append(
            "Spot-check route context near this span against field notes or photos.",
        )

    vd = props.get("voltage_detail")
    if isinstance(vd, dict) and len(vd) == 0:
        vd = None
    vac = props.get("voltage") or props.get("line_voltage") or vd
    if not vac and not props.get("is_underground"):
        actions.append("Confirm line voltage / circuit identity for this span segment.")

    ct = props.get("conductor_type") or props.get("conductor")
    if not ct and not props.get("is_underground"):
        actions.append("Confirm conductor type and size for sag / tension design on this span.")

    ph = props.get("phase_count") or props.get("phases")
    if not ph and not props.get("is_underground"):
        actions.append("Confirm phase configuration for electrical loading on this span.")

    dist = props.get("distance_m")
    try:
        dm = float(dist) if dist is not None else None
    except (TypeError, ValueError):
        dm = None
    if dm is not None and dm > 280:
        actions.append(
            "Long span — verify conductor choice and structure strength; "
            "confirm no intermediate support omitted.",
        )
    if dm is not None and dm < 12:
        actions.append("Very short span — verify adjacent structure IDs and survey sequence.")

    seen: set[str] = set()
    uniq: list[str] = []
    for a in actions:
        if a not in seen:
            seen.add(a)
            uniq.append(a)
    return uniq


def enrich_spans_phase3b(
    spans: list[dict[str, Any]],
    point_features: list[dict[str, Any]],
) -> None:
    """Add sequence, crossing-risk hits, and designer actions to span props (in place)."""

    total = len(spans)
    ctx_pts = _iter_context_points(point_features)

    for i, feat in enumerate(spans):
        if not isinstance(feat, dict):
            continue
        props = feat.get("properties")
        if not isinstance(props, dict):
            continue
        geom = feat.get("geometry")
        coords: list[Any] = []
        if isinstance(geom, dict) and geom.get("type") == "LineString":
            coords = geom.get("coordinates") or []

        from_lat = from_lon = to_lat = to_lon = None
        if len(coords) >= 2 and isinstance(coords[0], list) and isinstance(coords[-1], list):
            from_lon, from_lat = _safe_float(coords[0][0]), _safe_float(coords[0][1])
            to_lon, to_lat = _safe_float(coords[-1][0]), _safe_float(coords[-1][1])

        hits: list[dict[str, Any]] = []
        level = "none"
        if None not in (from_lat, from_lon, to_lat, to_lon):
            hits, level = _hits_for_span(from_lat, from_lon, to_lat, to_lon, ctx_pts)

        props["span_total"] = total
        props["span_sequence_label"] = f"{i + 1} of {total}" if total else "—"
        if i > 0:
            prev_p = spans[i - 1].get("properties") if isinstance(spans[i - 1], dict) else None
            if isinstance(prev_p, dict):
                props["previous_span"] = {
                    "from_point_id": prev_p.get("from_point_id"),
                    "to_point_id": prev_p.get("to_point_id"),
                    "span_index": prev_p.get("span_index"),
                }
        if i < total - 1:
            next_p = spans[i + 1].get("properties") if isinstance(spans[i + 1], dict) else None
            if isinstance(next_p, dict):
                props["next_span"] = {
                    "from_point_id": next_p.get("from_point_id"),
                    "to_point_id": next_p.get("to_point_id"),
                    "span_index": next_p.get("span_index"),
                }

        props["crossing_hits_survey"] = hits
        props["crossing_risk_level"] = level
        props["designer_suggested_actions"] = derive_designer_actions_for_span(props)


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


_SPAN_INVALID_THRESHOLD_M = 5.0
_SPAN_SUSPECT_THRESHOLD_M = 8.0


def classify_span_validity(distance_m: float | None) -> dict[str, Any]:
    """Classify a span as invalid/suspect/valid based on distance_m only."""
    if distance_m is None or distance_m < _SPAN_INVALID_THRESHOLD_M:
        return {
            "span_validity": "invalid",
            "design_usable": False,
            "clearance_check_allowed": False,
        }
    if distance_m <= _SPAN_SUSPECT_THRESHOLD_M:
        return {"span_validity": "suspect", "design_usable": True, "clearance_check_allowed": True}
    return {"span_validity": "valid", "design_usable": True, "clearance_check_allowed": True}


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
    base.update(classify_span_validity(dist))
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


def annotate_geometry_issue_clusters(spans: list[dict[str, Any]]) -> None:
    """Annotate consecutive invalid/suspect spans as geometry issue clusters.

    Mutates span properties in-place. Adds:
    - geometry_issue_cluster (bool)
    - cluster_size (int | None)

    Clustering is strictly consecutive: a valid span breaks the current cluster.
    """
    _CLUSTER_STATUSES = frozenset(("invalid", "suspect"))

    current_cluster: list[dict[str, Any]] = []

    def _flush(cluster: list[dict[str, Any]]) -> None:
        size = len(cluster)
        for span in cluster:
            props = span.setdefault("properties", {})
            props["geometry_issue_cluster"] = True
            props["cluster_size"] = size

    for span in spans:
        props = span.get("properties") or {}
        validity = props.get("span_validity")
        if validity in _CLUSTER_STATUSES:
            current_cluster.append(span)
        else:
            if current_cluster:
                _flush(current_cluster)
                current_cluster = []
            span.setdefault("properties", {})["geometry_issue_cluster"] = False
            span["properties"]["cluster_size"] = None

    if current_cluster:
        _flush(current_cluster)


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

    if spans:
        enrich_spans_phase3b(spans, point_features)
        annotate_geometry_issue_clusters(spans)
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
    high = med = low = 0
    invalid_count = suspect_count = 0
    for sf in span_features:
        sp = sf.get("properties") if isinstance(sf, dict) else None
        if not isinstance(sp, dict):
            continue
        r = str(sp.get("crossing_risk_level") or "").lower()
        if r == "high":
            high += 1
        elif r == "medium":
            med += 1
        elif r == "low":
            low += 1
        v = sp.get("span_validity")
        if v == "invalid":
            invalid_count += 1
        elif v == "suspect":
            suspect_count += 1
    meta["span_crossing_high_count"] = high
    meta["span_crossing_medium_count"] = med
    meta["span_crossing_low_count"] = low
    if invalid_count > 0:
        meta["geometry_trust"] = "LOW"
    elif suspect_count >= 3:
        meta["geometry_trust"] = "MEDIUM"
    else:
        meta["geometry_trust"] = "HIGH"
    # Map viewer: spans are derived from sequenced supports unless a future path sets
    # ``survey_circuit`` from captured line/circuit survey features.
    meta["span_layer_origin"] = meta.get("span_layer_origin") or "provisional_route"
