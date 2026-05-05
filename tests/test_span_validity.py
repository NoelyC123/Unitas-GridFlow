"""Tests for span validity classification."""

from __future__ import annotations

import pytest

from app.span_generator import build_span_feature, classify_span_validity

# ---------------------------------------------------------------------------
# classify_span_validity unit tests
# ---------------------------------------------------------------------------


def test_classify_invalid_below_threshold():
    result = classify_span_validity(1.0)
    assert result["span_validity"] == "invalid"
    assert result["design_usable"] is False
    assert result["clearance_check_allowed"] is False


def test_classify_invalid_just_below_5m():
    result = classify_span_validity(4.99)
    assert result["span_validity"] == "invalid"
    assert result["design_usable"] is False


def test_classify_suspect_at_lower_boundary():
    result = classify_span_validity(5.0)
    assert result["span_validity"] == "suspect"
    assert result["design_usable"] is True
    assert result["clearance_check_allowed"] is True


def test_classify_suspect_midrange():
    result = classify_span_validity(6.0)
    assert result["span_validity"] == "suspect"
    assert result["design_usable"] is True
    assert result["clearance_check_allowed"] is True


def test_classify_suspect_at_upper_boundary():
    result = classify_span_validity(8.0)
    assert result["span_validity"] == "suspect"
    assert result["design_usable"] is True


def test_classify_valid_above_threshold():
    result = classify_span_validity(15.0)
    assert result["span_validity"] == "valid"
    assert result["design_usable"] is True
    assert result["clearance_check_allowed"] is True


def test_classify_valid_just_above_8m():
    result = classify_span_validity(8.01)
    assert result["span_validity"] == "valid"


def test_classify_none_distance_is_invalid():
    result = classify_span_validity(None)
    assert result["span_validity"] == "invalid"
    assert result["design_usable"] is False
    assert result["clearance_check_allowed"] is False


# ---------------------------------------------------------------------------
# Required spec tests: 1m → invalid, 6m → suspect, 15m → valid
# ---------------------------------------------------------------------------


def test_spec_1m_span_is_invalid():
    result = classify_span_validity(1.0)
    assert result["span_validity"] == "invalid"


def test_spec_6m_span_is_suspect():
    result = classify_span_validity(6.0)
    assert result["span_validity"] == "suspect"


def test_spec_15m_span_is_valid():
    result = classify_span_validity(15.0)
    assert result["span_validity"] == "valid"


# ---------------------------------------------------------------------------
# Integration: build_span_feature carries all three fields
# ---------------------------------------------------------------------------


def _minimal_props() -> dict:
    return {}


def test_build_span_feature_carries_validity_fields_invalid():
    feat = build_span_feature(
        "P1",
        "P2",
        -3.014,
        54.521,
        -3.01401,
        54.521,
        _minimal_props(),
        _minimal_props(),
        rulepack_id=None,
        distance_m=1.0,
    )
    props = feat["properties"]
    assert props["span_validity"] == "invalid"
    assert props["design_usable"] is False
    assert props["clearance_check_allowed"] is False


def test_build_span_feature_carries_validity_fields_suspect():
    feat = build_span_feature(
        "P1",
        "P2",
        -3.014,
        54.521,
        -3.0141,
        54.521,
        _minimal_props(),
        _minimal_props(),
        rulepack_id=None,
        distance_m=6.0,
    )
    props = feat["properties"]
    assert props["span_validity"] == "suspect"
    assert props["design_usable"] is True
    assert props["clearance_check_allowed"] is True


def test_build_span_feature_carries_validity_fields_valid():
    feat = build_span_feature(
        "P1",
        "P2",
        -3.014,
        54.521,
        -3.016,
        54.521,
        _minimal_props(),
        _minimal_props(),
        rulepack_id=None,
        distance_m=150.0,
    )
    props = feat["properties"]
    assert props["span_validity"] == "valid"
    assert props["design_usable"] is True
    assert props["clearance_check_allowed"] is True


def test_build_span_feature_preserves_existing_fields():
    feat = build_span_feature(
        "P1",
        "P2",
        -3.014,
        54.521,
        -3.016,
        54.521,
        _minimal_props(),
        _minimal_props(),
        rulepack_id=None,
        distance_m=150.0,
        span_index=3,
    )
    props = feat["properties"]
    assert props["distance_m"] == pytest.approx(150.0)
    assert props["span_index"] == 3
    assert props["from_point_id"] == "P1"
    assert props["to_point_id"] == "P2"
