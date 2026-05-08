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


def validate_coordinates(
    easting: Any,
    northing: Any,
    record_id: str | None = None,
) -> tuple[bool, str | None]:
    """Validate an OSGB easting/northing pair before geometry operations.

    Returns (True, None) on success.  Returns (False, reason) on failure.
    Checks: not-None, numeric, finite, within OSGB national grid bounds.
    """
    label = f" for record {record_id}" if record_id else ""
    if easting is None or northing is None:
        return False, f"Missing coordinates{label}"
    try:
        e = float(easting)
        n = float(northing)
    except (ValueError, TypeError):
        return False, f"Non-numeric coordinates{label}: ({easting}, {northing})"
    if math.isnan(e) or math.isnan(n) or math.isinf(e) or math.isinf(n):
        return False, f"Non-finite coordinates{label}: ({easting}, {northing})"
    if not (0 < e < 700_000):
        return False, f"Easting {e} outside OSGB range (0–700000){label}"
    if not (0 < n < 1_300_000):
        return False, f"Northing {n} outside OSGB range (0–1300000){label}"
    return True, None


def calculate_distance(
    record1: dict[str, Any],
    record2: dict[str, Any],
    include_elevation: bool = True,
) -> tuple[float | None, str | None]:
    """Calculate planar distance (metres) between two records using easting/northing.

    Optionally incorporates elevation difference for 3-D distance.
    Falls back to horizontal distance when elevation is missing or non-numeric.
    Returns (distance, None) on success or (None, error_string) on failure.
    """
    id1 = str(record1.get("point_id") or "unknown")
    id2 = str(record2.get("point_id") or "unknown")
    for rec, rid in ((record1, id1), (record2, id2)):
        ok, err = validate_coordinates(rec.get("easting"), rec.get("northing"), rid)
        if not ok:
            return None, err
    try:
        e1, n1 = float(record1["easting"]), float(record1["northing"])
        e2, n2 = float(record2["easting"]), float(record2["northing"])
        dx, dy = e2 - e1, n2 - n1
        horizontal = math.sqrt(dx * dx + dy * dy)
        if include_elevation:
            elev1 = record1.get("elevation")
            elev2 = record2.get("elevation")
            if elev1 is not None and elev2 is not None:
                try:
                    dz = float(elev2) - float(elev1)
                    return math.sqrt(horizontal * horizontal + dz * dz), None
                except (ValueError, TypeError):
                    pass
        return horizontal, None
    except Exception as exc:
        return None, f"Distance calculation failed between {id1} and {id2}: {exc}"


def calculate_bearing(
    record1: dict[str, Any],
    record2: dict[str, Any],
) -> tuple[float | None, str | None]:
    """Calculate bearing (0–360°, north = 0°) between two records using easting/northing.

    Returns (bearing_degrees, None) on success or (None, error_string) on failure.
    """
    id1 = str(record1.get("point_id") or "unknown")
    id2 = str(record2.get("point_id") or "unknown")
    for rec, rid in ((record1, id1), (record2, id2)):
        ok, err = validate_coordinates(rec.get("easting"), rec.get("northing"), rid)
        if not ok:
            return None, err
    try:
        e1, n1 = float(record1["easting"]), float(record1["northing"])
        e2, n2 = float(record2["easting"]), float(record2["northing"])
        dx, dy = e2 - e1, n2 - n1
        bearing = math.degrees(math.atan2(dx, dy))
        if bearing < 0:
            bearing += 360.0
        return bearing, None
    except Exception as exc:
        return None, f"Bearing calculation failed between {id1} and {id2}: {exc}"
