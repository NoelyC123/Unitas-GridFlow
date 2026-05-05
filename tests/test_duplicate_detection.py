"""Tests for duplicate pole detection."""

from __future__ import annotations

import pytest

from app.duplicate_detection import _haversine_m, apply_duplicate_detection


def _make_feature(lon: float, lat: float, pid: str) -> dict:
    return {
        "type": "Feature",
        "geometry": {"type": "Point", "coordinates": [lon, lat]},
        "properties": {"point_id": pid},
    }


# ---------------------------------------------------------------------------
# Haversine sanity
# ---------------------------------------------------------------------------


def test_haversine_zero_distance():
    assert _haversine_m(54.521, -3.014, 54.521, -3.014) == pytest.approx(0.0, abs=1e-6)


def test_haversine_known_distance():
    # ~1m east along a latitude ~54°N — 1° lon ≈ 65 km at that latitude
    # 1m ≈ 1/65000 degrees ≈ 0.0000154°
    d = _haversine_m(54.521, -3.014, 54.521, -3.014 + 1 / 65000)
    assert 0.9 < d < 1.1


# ---------------------------------------------------------------------------
# Test 1: Points within 2m get same group_id
# ---------------------------------------------------------------------------


def test_duplicate_detection_groups_nearby_points():
    features = [
        _make_feature(-3.014, 54.521, "P1"),
        _make_feature(-3.01401, 54.521, "P2"),  # ~1m away
    ]

    apply_duplicate_detection(features)

    group_id_1 = features[0]["properties"]["duplicate_group_id"]
    group_id_2 = features[1]["properties"]["duplicate_group_id"]

    assert group_id_1 is not None
    assert group_id_1 == group_id_2
    assert features[0]["properties"]["duplicate_confidence"] == "high"


# ---------------------------------------------------------------------------
# Test 2: Isolated points get None
# ---------------------------------------------------------------------------


def test_duplicate_detection_isolated_points():
    features = [
        _make_feature(-3.014, 54.521, "P1"),
        _make_feature(-3.020, 54.525, "P2"),  # >500m away
    ]

    apply_duplicate_detection(features)

    assert features[0]["properties"]["duplicate_group_id"] is None
    assert features[0]["properties"]["duplicate_confidence"] is None
    assert features[1]["properties"]["duplicate_group_id"] is None
    assert features[1]["properties"]["duplicate_confidence"] is None


# ---------------------------------------------------------------------------
# Test 3: Confidence levels assigned correctly
# ---------------------------------------------------------------------------


def test_duplicate_detection_confidence_levels():
    # At 54.521°N, 1° lon ≈ 64,610m, so 1m ≈ 0.0000155°
    # P2 is ~0.52m from P1; P3 is ~2.52m from P1 (both within 3m threshold)
    # Max distance in cluster ≈ 2.52m → confidence "low"
    features = [
        _make_feature(-3.014, 54.521, "P1"),
        _make_feature(-3.014008, 54.521, "P2"),  # ~0.52m from P1 (high band alone)
        _make_feature(-3.014039, 54.521, "P3"),  # ~2.52m from P1 (low band)
    ]

    apply_duplicate_detection(features)

    group_id = features[0]["properties"]["duplicate_group_id"]
    assert group_id is not None
    assert features[1]["properties"]["duplicate_group_id"] == group_id
    assert features[2]["properties"]["duplicate_group_id"] == group_id

    # Max separation in cluster spans into low band
    assert features[0]["properties"]["duplicate_confidence"] == "low"
    assert features[1]["properties"]["duplicate_confidence"] == "low"
    assert features[2]["properties"]["duplicate_confidence"] == "low"


# ---------------------------------------------------------------------------
# Additional edge cases
# ---------------------------------------------------------------------------


def test_empty_features_list():
    apply_duplicate_detection([])  # should not raise


def test_non_point_features_skipped():
    features = [
        {
            "type": "Feature",
            "geometry": {"type": "LineString", "coordinates": [[-3.014, 54.521], [-3.015, 54.522]]},
            "properties": {"point_id": "L1"},
        }
    ]
    apply_duplicate_detection(features)
    assert "duplicate_group_id" not in features[0]["properties"]


def test_two_separate_clusters():
    features = [
        _make_feature(-3.014, 54.521, "A1"),
        _make_feature(-3.01401, 54.521, "A2"),  # ~1m from A1
        _make_feature(-3.020, 54.525, "B1"),
        _make_feature(-3.02001, 54.525, "B2"),  # ~1m from B1
    ]

    apply_duplicate_detection(features)

    gid_a1 = features[0]["properties"]["duplicate_group_id"]
    gid_a2 = features[1]["properties"]["duplicate_group_id"]
    gid_b1 = features[2]["properties"]["duplicate_group_id"]
    gid_b2 = features[3]["properties"]["duplicate_group_id"]

    assert gid_a1 is not None
    assert gid_a1 == gid_a2
    assert gid_b1 is not None
    assert gid_b1 == gid_b2
    assert gid_a1 != gid_b1


def test_exactly_at_threshold_boundary():
    # Points separated by slightly more than 3m should NOT be grouped
    # At 54.5° lat, 1° lon ≈ 64,900m → 3.1m ≈ 0.0000477°
    features = [
        _make_feature(-3.014, 54.521, "P1"),
        _make_feature(-3.014 + 0.0000477, 54.521, "P2"),
    ]

    apply_duplicate_detection(features)

    assert features[0]["properties"]["duplicate_group_id"] is None
    assert features[1]["properties"]["duplicate_group_id"] is None


def test_properties_dict_created_when_missing():
    features = [
        {"type": "Feature", "geometry": {"type": "Point", "coordinates": [-3.014, 54.521]}},
        {"type": "Feature", "geometry": {"type": "Point", "coordinates": [-3.01401, 54.521]}},
    ]

    apply_duplicate_detection(features)

    assert "duplicate_group_id" in features[0]["properties"]
