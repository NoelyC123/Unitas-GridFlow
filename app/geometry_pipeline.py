"""Deterministic geometry cleanup before route span generation.

The pipeline only normalises geometry used by downstream span construction. It
does not add display fields or make UI decisions.
"""

from __future__ import annotations

import math
from copy import deepcopy
from dataclasses import dataclass
from typing import Any

EARTH_RADIUS_M = 6371000.0


@dataclass(frozen=True)
class GeometryPipelineResult:
    point_features: list[dict[str, Any]]
    sequence_payload: dict[str, Any] | None


def _safe_float(value: Any) -> float | None:
    try:
        if value is None or value == "":
            return None
        out = float(value)
        if math.isnan(out) or math.isinf(out):
            return None
        return out
    except (TypeError, ValueError):
        return None


def _distance_m(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    rlat1 = math.radians(lat1)
    rlat2 = math.radians(lat2)
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat / 2) ** 2 + math.cos(rlat1) * math.cos(rlat2) * math.sin(dlon / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(max(0.0, 1.0 - a)))
    return EARTH_RADIUS_M * c


def _point_id(feature: dict[str, Any]) -> str | None:
    props = feature.get("properties")
    if not isinstance(props, dict):
        return None
    value = props.get("pole_id") or props.get("point_id") or props.get("id")
    if value is None:
        return None
    text = str(value).strip()
    return text or None


def _point_coords(feature: dict[str, Any]) -> tuple[float, float] | None:
    geom = feature.get("geometry")
    if not isinstance(geom, dict) or geom.get("type") != "Point":
        return None
    coords = geom.get("coordinates") or []
    if len(coords) < 2:
        return None
    lon = _safe_float(coords[0])
    lat = _safe_float(coords[1])
    if lat is None or lon is None:
        return None
    return lat, lon


def _set_point_coords(feature: dict[str, Any], lat: float, lon: float) -> None:
    geom = feature.setdefault("geometry", {})
    geom["type"] = "Point"
    geom["coordinates"] = [lon, lat]


def _route_point_ids(sequence_payload: dict[str, Any] | None) -> set[str]:
    if not sequence_payload or sequence_payload.get("status") != "ok":
        return set()
    out: set[str] = set()
    for item in sequence_payload.get("chain") or []:
        if not isinstance(item, dict):
            continue
        value = item.get("point_id")
        if value is None:
            continue
        text = str(value).strip()
        if text:
            out.add(text)
    return out


def _should_normalise(feature: dict[str, Any], route_point_ids: set[str] | None) -> bool:
    if route_point_ids is None:
        return True
    pid = _point_id(feature)
    return bool(pid and pid in route_point_ids)


def snap_nearby_points(
    point_features: list[dict[str, Any]],
    *,
    threshold_m: float = 3.0,
    route_point_ids: set[str] | None = None,
) -> list[dict[str, Any]]:
    """Snap route points within ``threshold_m`` to the first deterministic anchor."""

    snapped = deepcopy(point_features)
    anchors: list[tuple[float, float]] = []

    for feature in snapped:
        if not isinstance(feature, dict) or not _should_normalise(feature, route_point_ids):
            continue
        coords = _point_coords(feature)
        if coords is None:
            continue
        lat, lon = coords
        anchor = next(
            (
                (alat, alon)
                for alat, alon in anchors
                if _distance_m(lat, lon, alat, alon) <= threshold_m
            ),
            None,
        )
        if anchor is None:
            anchors.append((lat, lon))
            continue
        _set_point_coords(feature, anchor[0], anchor[1])

    return snapped


def merge_duplicates(
    point_features: list[dict[str, Any]],
    *,
    threshold_m: float = 2.0,
    route_point_ids: set[str] | None = None,
) -> tuple[list[dict[str, Any]], dict[str, str]]:
    """Collapse duplicate route point features and return removed-id aliases."""

    merged: list[dict[str, Any]] = []
    anchors: list[tuple[float, float, str | None]] = []
    id_aliases: dict[str, str] = {}

    for feature in deepcopy(point_features):
        if not isinstance(feature, dict):
            continue
        if not _should_normalise(feature, route_point_ids):
            merged.append(feature)
            continue

        coords = _point_coords(feature)
        pid = _point_id(feature)
        if coords is None:
            merged.append(feature)
            continue

        lat, lon = coords
        duplicate_anchor: tuple[float, float, str | None] | None = next(
            (
                anchor
                for anchor in anchors
                if _distance_m(lat, lon, anchor[0], anchor[1]) <= threshold_m
            ),
            None,
        )
        if duplicate_anchor is not None:
            retained_id = duplicate_anchor[2]
            if pid and retained_id:
                id_aliases[pid] = retained_id
            continue

        anchors.append((lat, lon, pid))
        merged.append(feature)

    return merged, id_aliases


def _feature_coord_index(point_features: list[dict[str, Any]]) -> dict[str, tuple[float, float]]:
    out: dict[str, tuple[float, float]] = {}
    for feature in point_features:
        if not isinstance(feature, dict):
            continue
        pid = _point_id(feature)
        coords = _point_coords(feature)
        if pid and coords:
            out[pid] = coords
    return out


def remove_zero_length_sequences(
    sequence_payload: dict[str, Any] | None,
    *,
    point_features: list[dict[str, Any]] | None = None,
    id_aliases: dict[str, str] | None = None,
    threshold_m: float = 2.0,
) -> dict[str, Any] | None:
    """Remove consecutive duplicate or near-zero route steps before span creation."""

    if sequence_payload is None:
        return None
    cleaned = deepcopy(sequence_payload)
    if cleaned.get("status") != "ok":
        return cleaned

    coord_index = _feature_coord_index(point_features or [])
    aliases = id_aliases or {}
    chain = cleaned.get("chain") or []
    if not isinstance(chain, list) or len(chain) < 2:
        return cleaned

    normalised_chain: list[dict[str, Any]] = []
    changed = False
    for item in chain:
        if not isinstance(item, dict):
            changed = True
            continue
        nxt = deepcopy(item)
        pid_raw = nxt.get("point_id")
        pid = str(pid_raw).strip() if pid_raw is not None else ""
        if pid in aliases:
            pid = aliases[pid]
            nxt["point_id"] = pid
            changed = True
        if pid in coord_index:
            lat, lon = coord_index[pid]
            old_lat = _safe_float(nxt.get("lat"))
            old_lon = _safe_float(nxt.get("lon"))
            if old_lat != lat or old_lon != lon:
                changed = True
                nxt["lat"] = lat
                nxt["lon"] = lon
        normalised_chain.append(nxt)

    out_chain: list[dict[str, Any]] = []
    for item in normalised_chain:
        if not out_chain:
            out_chain.append(item)
            continue
        prev = out_chain[-1]
        prev_id = str(prev.get("point_id") or "").strip()
        item_id = str(item.get("point_id") or "").strip()
        prev_lat = _safe_float(prev.get("lat"))
        prev_lon = _safe_float(prev.get("lon"))
        item_lat = _safe_float(item.get("lat"))
        item_lon = _safe_float(item.get("lon"))
        if prev_id and item_id and prev_id == item_id:
            changed = True
            continue
        if None not in (prev_lat, prev_lon, item_lat, item_lon):
            assert prev_lat is not None
            assert prev_lon is not None
            assert item_lat is not None
            assert item_lon is not None
            if _distance_m(prev_lat, prev_lon, item_lat, item_lon) <= threshold_m:
                changed = True
                continue
        out_chain.append(item)

    if changed:
        for idx, item in enumerate(out_chain):
            if idx >= len(out_chain) - 1:
                item["span_to_next_m"] = None
                continue
            nxt = out_chain[idx + 1]
            lat = _safe_float(item.get("lat"))
            lon = _safe_float(item.get("lon"))
            nlat = _safe_float(nxt.get("lat"))
            nlon = _safe_float(nxt.get("lon"))
            if None not in (lat, lon, nlat, nlon):
                assert lat is not None
                assert lon is not None
                assert nlat is not None
                assert nlon is not None
                item["span_to_next_m"] = round(_distance_m(lat, lon, nlat, nlon), 1)

    cleaned["chain"] = out_chain
    return cleaned


def normalize_geometry_for_span_generation(
    point_features: list[dict[str, Any]],
    sequence_payload: dict[str, Any] | None,
    *,
    snap_threshold_m: float = 3.0,
    duplicate_threshold_m: float = 2.0,
    zero_length_threshold_m: float = 2.0,
) -> GeometryPipelineResult:
    """Run snap, duplicate merge, and zero-length route cleanup for span building."""

    route_ids = _route_point_ids(sequence_payload)
    normalise_ids = route_ids or None
    snapped = snap_nearby_points(
        point_features,
        threshold_m=snap_threshold_m,
        route_point_ids=normalise_ids,
    )
    merged, aliases = merge_duplicates(
        snapped,
        threshold_m=duplicate_threshold_m,
        route_point_ids=normalise_ids,
    )
    cleaned_sequence = remove_zero_length_sequences(
        sequence_payload,
        point_features=merged,
        id_aliases=aliases,
        threshold_m=zero_length_threshold_m,
    )
    return GeometryPipelineResult(point_features=merged, sequence_payload=cleaned_sequence)
