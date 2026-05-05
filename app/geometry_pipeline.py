"""Geometry normalization pipeline for span generation.

Cleans survey geometry before span/cable generation to handle:
- GPS bounce (duplicate points within ~2-3m)
- Zero-length sequences
- Coordinate precision issues

This runs BEFORE attach_span_features_to_collection to ensure
clean geometry for electrical display.
"""

from __future__ import annotations

import math
from typing import Any, NamedTuple


class CleanedGeometry(NamedTuple):
    """Result of geometry normalization pipeline."""

    sequence_payload: dict[str, Any]
    snap_count: int
    merge_count: int
    zero_length_removed: int


def _haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculate haversine distance in meters between two lat/lon points."""
    EARTH_RADIUS_M = 6371000.0

    lat1_rad = math.radians(lat1)
    lat2_rad = math.radians(lat2)
    delta_lat = math.radians(lat2 - lat1)
    delta_lon = math.radians(lon2 - lon1)

    a = (
        math.sin(delta_lat / 2) ** 2
        + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(delta_lon / 2) ** 2
    )
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    return EARTH_RADIUS_M * c


def _snap_nearby_points(
    chain: list[dict[str, Any]], threshold_m: float = 3.0
) -> tuple[list[dict], int]:
    """Snap points within threshold distance to first occurrence.

    Returns: (cleaned_chain, snap_count)
    """
    if not chain:
        return chain, 0

    cleaned = []
    snap_count = 0

    for point in chain:
        lat = point.get("lat")
        lon = point.get("lon")

        if lat is None or lon is None:
            cleaned.append(point)
            continue

        # Check if this point is within threshold of any existing point
        snapped = False
        for existing in cleaned:
            ex_lat = existing.get("lat")
            ex_lon = existing.get("lon")

            if ex_lat is None or ex_lon is None:
                continue

            distance = _haversine_distance(lat, lon, ex_lat, ex_lon)

            if distance <= threshold_m:
                # Snap to existing point (use existing coordinates)
                snapped = True
                snap_count += 1
                break

        if not snapped:
            cleaned.append(point)

    return cleaned, snap_count


def _merge_duplicates(
    chain: list[dict[str, Any]], threshold_m: float = 2.0
) -> tuple[list[dict], int]:
    """Merge consecutive duplicate points within threshold.

    Returns: (cleaned_chain, merge_count)
    """
    if len(chain) < 2:
        return chain, 0

    cleaned = [chain[0]]
    merge_count = 0

    for i in range(1, len(chain)):
        curr = chain[i]
        prev = cleaned[-1]

        curr_lat = curr.get("lat")
        curr_lon = curr.get("lon")
        prev_lat = prev.get("lat")
        prev_lon = prev.get("lon")

        if None in (curr_lat, curr_lon, prev_lat, prev_lon):
            cleaned.append(curr)
            continue

        distance = _haversine_distance(prev_lat, prev_lon, curr_lat, curr_lon)

        if distance <= threshold_m:
            # Merge: keep previous, skip current
            merge_count += 1
        else:
            cleaned.append(curr)

    return cleaned, merge_count


def _remove_zero_length_sequences(chain: list[dict[str, Any]]) -> tuple[list[dict], int]:
    """Remove consecutive points with identical coordinates.

    Returns: (cleaned_chain, removed_count)
    """
    if len(chain) < 2:
        return chain, 0

    cleaned = [chain[0]]
    removed = 0

    for i in range(1, len(chain)):
        curr = chain[i]
        prev = cleaned[-1]

        curr_lat = curr.get("lat")
        curr_lon = curr.get("lon")
        prev_lat = prev.get("lat")
        prev_lon = prev.get("lon")

        # Skip if missing coordinates
        if None in (curr_lat, curr_lon, prev_lat, prev_lon):
            cleaned.append(curr)
            continue

        # Check if identical coordinates (exact match)
        if curr_lat == prev_lat and curr_lon == prev_lon:
            removed += 1
        else:
            cleaned.append(curr)

    return cleaned, removed


def _recompute_span_distances(chain: list[dict[str, Any]]) -> None:
    """Recompute span_to_next_m after cleaning.

    Mutates chain in-place.
    """
    for i in range(len(chain) - 1):
        curr = chain[i]
        next_point = chain[i + 1]

        curr_lat = curr.get("lat")
        curr_lon = curr.get("lon")
        next_lat = next_point.get("lat")
        next_lon = next_point.get("lon")

        if None in (curr_lat, curr_lon, next_lat, next_lon):
            curr["span_to_next_m"] = None
        else:
            distance = _haversine_distance(curr_lat, curr_lon, next_lat, next_lon)
            curr["span_to_next_m"] = round(distance, 1)

    # Last point has no next span
    if chain:
        chain[-1]["span_to_next_m"] = None


def normalize_geometry_for_span_generation(
    features: list[dict[str, Any]], sequence_payload: dict[str, Any]
) -> CleanedGeometry:
    """Clean geometry pipeline before span generation.

    Pipeline:
    1. Snap nearby points (~3m)
    2. Merge duplicates (~2m)
    3. Remove zero-length sequences
    4. Recompute span distances

    Args:
        features: GeoJSON feature list (not currently used, reserved for future)
        sequence_payload: Route sequencer output with 'chain' key

    Returns:
        CleanedGeometry with cleaned sequence_payload and operation counts
    """
    # Extract chain
    chain = sequence_payload.get("chain", [])

    if not chain or not isinstance(chain, list):
        return CleanedGeometry(
            sequence_payload=sequence_payload,
            snap_count=0,
            merge_count=0,
            zero_length_removed=0,
        )

    # Run cleaning pipeline
    chain, snap_count = _snap_nearby_points(chain, threshold_m=3.0)
    chain, merge_count = _merge_duplicates(chain, threshold_m=2.0)
    chain, zero_removed = _remove_zero_length_sequences(chain)

    # Recompute span distances after cleaning
    _recompute_span_distances(chain)

    # Build cleaned sequence payload
    cleaned_payload = {**sequence_payload, "chain": chain}

    return CleanedGeometry(
        sequence_payload=cleaned_payload,
        snap_count=snap_count,
        merge_count=merge_count,
        zero_length_removed=zero_removed,
    )
