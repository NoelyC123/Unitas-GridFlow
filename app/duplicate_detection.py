"""Duplicate pole detection using spatial clustering.

Annotates co-located features in-place with group identity and confidence.
Does NOT modify geometry, merge points, or delete features.
"""

from __future__ import annotations

import math
from typing import Any

_THRESHOLD_M = 3.0
_HIGH_M = 1.0
_MEDIUM_M = 2.0


def _haversine_m(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    R = 6371000.0
    lat1_r = math.radians(lat1)
    lat2_r = math.radians(lat2)
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat / 2) ** 2 + math.cos(lat1_r) * math.cos(lat2_r) * math.sin(dlon / 2) ** 2
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


def _confidence(max_dist_m: float) -> str:
    if max_dist_m < _HIGH_M:
        return "high"
    if max_dist_m < _MEDIUM_M:
        return "medium"
    return "low"


def apply_duplicate_detection(features: list[dict[str, Any]]) -> None:
    """Detect and annotate co-located poles.

    Mutates features in-place by adding:
    - duplicate_group_id (str or None)
    - duplicate_confidence ("low" | "medium" | "high" | None)

    Uses haversine distance on lat/lon coordinates.
    Threshold: 3 metres for duplicate detection.
    """
    # Collect valid point indices and their coordinates
    point_indices: list[int] = []
    coords: list[tuple[float, float]] = []  # (lat, lon)

    for i, feat in enumerate(features):
        if not isinstance(feat, dict):
            continue
        geom = feat.get("geometry") or {}
        if geom.get("type") != "Point":
            continue
        raw = geom.get("coordinates")
        if not raw or len(raw) < 2:
            continue
        try:
            lon, lat = float(raw[0]), float(raw[1])
        except (TypeError, ValueError):
            continue
        point_indices.append(i)
        coords.append((lat, lon))

    n = len(point_indices)
    if n == 0:
        return

    # Greedy union-find clustering
    parent = list(range(n))

    def find(x: int) -> int:
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    def union(x: int, y: int) -> None:
        parent[find(x)] = find(y)

    # Track pairwise distances for confidence calculation
    pair_distances: list[tuple[int, int, float]] = []

    for i in range(n):
        for j in range(i + 1, n):
            d = _haversine_m(coords[i][0], coords[i][1], coords[j][0], coords[j][1])
            if d <= _THRESHOLD_M:
                union(i, j)
                pair_distances.append((i, j, d))

    # Build clusters: root → list of member indices
    clusters: dict[int, list[int]] = {}
    for i in range(n):
        root = find(i)
        clusters.setdefault(root, []).append(i)

    # Per-cluster max distance for confidence
    cluster_max: dict[int, float] = {}
    for i, j, d in pair_distances:
        root = find(i)
        if d > cluster_max.get(root, 0.0):
            cluster_max[root] = d

    # Assign group IDs (only to genuine clusters — 2+ members)
    group_counter = 1
    group_id_for_root: dict[int, str | None] = {}
    for root, members in clusters.items():
        if len(members) >= 2:
            group_id_for_root[root] = f"DUP_{group_counter:03d}"
            group_counter += 1
        else:
            group_id_for_root[root] = None

    # Annotate features
    for i, feat_idx in enumerate(point_indices):
        root = find(i)
        gid = group_id_for_root[root]
        props = features[feat_idx].setdefault("properties", {})
        if gid is None:
            props["duplicate_group_id"] = None
            props["duplicate_confidence"] = None
        else:
            props["duplicate_group_id"] = gid
            props["duplicate_confidence"] = _confidence(cluster_max.get(root, 0.0))
