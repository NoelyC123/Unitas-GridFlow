from __future__ import annotations

import math
from typing import Any


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


def _distance_m(a: tuple[float, float], b: tuple[float, float]) -> float:
    """Approximate distance in metres for short duplicate checks."""
    lat1, lon1 = a
    lat2, lon2 = b
    return math.sqrt((lat1 - lat2) ** 2 + (lon1 - lon2) ** 2) * 111_000


def _get_point(feature: dict[str, Any]) -> tuple[float, float] | None:
    geom = feature.get("geometry") or {}
    coords = geom.get("coordinates") or []
    if len(coords) < 2:
        return None

    lon = _safe_float(coords[0])
    lat = _safe_float(coords[1])
    if lat is None or lon is None:
        return None

    return lat, lon


def _get_id(feature: dict[str, Any]) -> str:
    props = feature.get("properties") or {}
    return str(props.get("pole_id") or props.get("point_id") or props.get("id") or "").strip()


def detect_duplicate_groups(
    features: list[dict[str, Any]],
    threshold_m: float = 3.0,
) -> list[list[int]]:
    """Detect nearby point-feature groups without changing geometry."""
    groups: list[list[int]] = []
    used: set[int] = set()

    for i, f1 in enumerate(features):
        if i in used:
            continue

        p1 = _get_point(f1)
        if not p1:
            continue

        group = [i]

        for j, f2 in enumerate(features):
            if i == j or j in used:
                continue

            p2 = _get_point(f2)
            if not p2:
                continue

            if _distance_m(p1, p2) <= threshold_m:
                group.append(j)

        if len(group) > 1:
            for g in group:
                used.add(g)
            groups.append(group)

    return groups


def classify_duplicate_type(group_features: list[dict[str, Any]]) -> str:
    """Classify duplicate group using feature-code evidence only."""
    types = [
        str(feature.get("properties", {}).get("feature_code", "")).strip().lower()
        for feature in group_features
    ]

    if any("ex" in item for item in types) and any("pr" in item or "pol" in item for item in types):
        return "replacement_pair"

    if len(set(types)) == 1:
        return "co_located"

    return "unknown"


def apply_duplicate_detection(features: list[dict[str, Any]]) -> None:
    """Annotate duplicate candidates in place.

    This function must not remove features, move geometry, or alter spans.
    """
    groups = detect_duplicate_groups(features)

    for idx, group in enumerate(groups):
        group_features = [features[i] for i in group]
        duplicate_type = classify_duplicate_type(group_features)
        group_id = f"dup_{idx}"

        for i in group:
            props = features[i].setdefault("properties", {})
            props["duplicate_candidate"] = True
            props["duplicate_type"] = duplicate_type
            props["duplicate_group_id"] = group_id
            props["duplicate_confidence"] = "medium"
