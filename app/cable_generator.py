"""GeoJSON underground / cable LineString generation (Phase 3C).

Builds cable segments from connectivity fields (cable_from / cable_to, support IDs)
on point features. Coordinates use GeoJSON order [lon, lat].
"""

from __future__ import annotations

import math
from typing import Any

from app.electrical_schema import merge_electrical_fields_into_props
from app.qa_engine import infer_display_network_fields
from app.span_generator import (
    coalesce_electrical_source,
    haversine_distance_m,
    index_point_features_by_pole_id,
    line_segment_crossing_profile,
)


def _norm_id(v: Any) -> str | None:
    if v is None:
        return None
    s = str(v).strip()
    return s or None


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


def index_point_lonlat_by_pole_id(features: list[dict[str, Any]]) -> dict[str, tuple[float, float]]:
    out: dict[str, tuple[float, float]] = {}
    for feat in features:
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
        pid = _norm_id(props.get("pole_id"))
        if pid:
            out[pid] = (lon, lat)
    return out


def _pick_str(a: dict[str, Any], b: dict[str, Any], *keys: str) -> Any:
    for key in keys:
        for d in (a, b):
            v = d.get(key)
            if v not in (None, ""):
                return v
    return None


def collect_directed_cable_edges(
    point_features: list[dict[str, Any]],
) -> list[tuple[str, str, dict[str, Any]]]:
    """Directed edges (from_id, to_id, witness_props) before deduplication."""

    edges: list[tuple[str, str, dict[str, Any]]] = []
    for feat in point_features:
        if not isinstance(feat, dict) or feat.get("type") != "Feature":
            continue
        props = feat.get("properties")
        if not isinstance(props, dict):
            continue
        pid = _norm_id(props.get("pole_id"))
        if not pid:
            continue
        cf = _norm_id(props.get("cable_from_asset_id"))
        ct = _norm_id(props.get("cable_to_asset_id"))
        fs = _norm_id(props.get("from_support_id"))
        ts = _norm_id(props.get("to_support_id"))
        is_ug = bool(props.get("is_underground"))

        if cf and ct and cf != ct:
            edges.append((cf, ct, props))
        if ct and ct != pid and not (cf and ct and cf != ct):
            edges.append((pid, ct, props))
        if cf and cf != pid and not (cf and ct and cf != ct) and not (ct and ct != pid):
            edges.append((cf, pid, props))

        if is_ug and fs and ts and fs != ts:
            edges.append((fs, ts, props))

    dedup: dict[tuple[str, str], tuple[str, str, dict[str, Any]]] = {}
    for fr, to, wit in edges:
        key = tuple(sorted([fr, to]))
        if key not in dedup:
            dedup[key] = (fr, to, wit)
    return list(dedup.values())


def _coalesce_cable_aux(from_props: dict[str, Any], to_props: dict[str, Any]) -> dict[str, Any]:
    return {
        "burial_depth_m": _pick_str(from_props, to_props, "burial_depth_m", "depth_of_lay_m"),
        "ducting_type": _pick_str(
            from_props,
            to_props,
            "ducting_type",
            "duct_type",
            "cable_ducting",
        ),
    }


def derive_cable_designer_actions(props: dict[str, Any]) -> list[str]:
    actions: list[str] = []
    if not props.get("cable_type") and not props.get("cable_detail"):
        actions.append(
            "Confirm underground cable type / construction (e.g. XLPE, PILC) for this segment.",
        )
    if not props.get("cable_size") and not props.get("conductor_size"):
        actions.append(
            "Confirm cable size / cores for thermal and fault design on this segment.",
        )
    if not props.get("voltage") and not props.get("line_voltage"):
        actions.append("Confirm circuit voltage for this underground segment.")
    bd = props.get("burial_depth_m")
    if bd in (None, ""):
        actions.append(
            "Depth of lay / cover not recorded — confirm burial depth meets "
            "DNO / statutory requirements.",
        )
    risk = str(props.get("crossing_risk_level") or "none").lower()
    if risk == "blocker":
        actions.append(
            "Survey context indicates high-tier crossing within clearance proximity — "
            "verify route tracing and protection before civils design.",
        )
    elif risk == "high":
        actions.append(
            "Survey context indicates road-track-utility proximity — verify route tracing "
            "and protection before civils design.",
        )
    elif risk == "medium":
        actions.append(
            "Review third-party / obstruction context along the cable trace from survey records.",
        )

    seen: set[str] = set()
    out: list[str] = []
    for a in actions:
        if a not in seen:
            seen.add(a)
            out.append(a)
    return out


def build_cable_feature(
    from_pid: str,
    to_pid: str,
    from_lon: float,
    from_lat: float,
    to_lon: float,
    to_lat: float,
    from_props: dict[str, Any],
    to_props: dict[str, Any],
    witness_props: dict[str, Any],
    *,
    rulepack_id: str | None,
    cable_index: int,
    routing_source: str,
    point_features: list[dict[str, Any]],
) -> dict[str, Any]:
    dist = haversine_distance_m(from_lat, from_lon, to_lat, to_lon)
    base = coalesce_electrical_source(from_props, to_props, rulepack_id)
    aux = _coalesce_cable_aux(from_props, to_props)
    # Witness row sometimes holds the only UG annotation
    for k in ("burial_depth_m", "ducting_type"):
        if k not in witness_props or witness_props.get(k) in (None, ""):
            continue
        if aux.get(k) in (None, ""):
            aux[k] = witness_props.get(k)

    base.update(aux)
    base["from_point_id"] = from_pid
    base["to_point_id"] = to_pid
    base["distance_m"] = dist
    base["cable_index"] = cable_index
    base["feature_type"] = "underground_cable_segment"
    base["routing_source"] = routing_source
    base["is_underground"] = True
    base["is_overhead"] = False

    nf_w = infer_display_network_fields(witness_props, rulepack_id)
    for k in ("cable_type", "voltage", "phase_count"):
        if base.get(k) in (None, "") and nf_w.get(k) not in (None, ""):
            base[k] = nf_w[k]

    hits, level = line_segment_crossing_profile(from_lat, from_lon, to_lat, to_lon, point_features)
    base["crossing_hits_survey"] = hits
    base["crossing_risk_level"] = level
    base["designer_suggested_actions"] = derive_cable_designer_actions(base)

    merge_electrical_fields_into_props(base)

    return {
        "type": "Feature",
        "geometry": {"type": "LineString", "coordinates": [[from_lon, from_lat], [to_lon, to_lat]]},
        "properties": base,
    }


def generate_cable_features_geojson(
    point_features: list[dict[str, Any]],
    metadata: dict[str, Any] | None = None,
) -> list[dict[str, Any]]:
    meta = metadata or {}
    rulepack_id = meta.get("rulepack_id")
    by_pole = index_point_features_by_pole_id(point_features)
    ll_by = index_point_lonlat_by_pole_id(point_features)
    edges = collect_directed_cable_edges(point_features)
    cables: list[dict[str, Any]] = []

    for fr, to, wit in edges:
        fr_c = ll_by.get(fr)
        to_c = ll_by.get(to)
        if not fr_c or not to_c:
            continue
        from_lon, from_lat = fr_c
        to_lon, to_lat = to_c
        f_pr = by_pole.get(fr, {})
        t_pr = by_pole.get(to, {})
        ws = _norm_id(wit.get("from_support_id"))
        wt = _norm_id(wit.get("to_support_id"))
        if ws and wt and {ws, wt} == {fr, to}:
            src = "support_span"
        else:
            src = "cable_link"
        cables.append(
            build_cable_feature(
                fr,
                to,
                from_lon,
                from_lat,
                to_lon,
                to_lat,
                f_pr,
                t_pr,
                wit,
                rulepack_id=rulepack_id,
                cable_index=len(cables),
                routing_source=src,
                point_features=point_features,
            )
        )
    return cables


def attach_cable_features_to_collection(collection: dict[str, Any]) -> None:
    feats = collection.get("features")
    if not isinstance(feats, list):
        feats = []
    meta = collection.get("metadata")
    if not isinstance(meta, dict):
        meta = {}
        collection["metadata"] = meta
    cable_features = generate_cable_features_geojson(feats, meta)
    collection["cable_features"] = cable_features
    meta["cable_feature_count"] = len(cable_features)
