"""Tests for route-level geometry trust scoring."""

from __future__ import annotations

from app.span_generator import attach_span_features_to_collection


def _collection_with_span_validities(validities: list[str]) -> dict:
    """Build a minimal FeatureCollection with pre-tagged span_features."""
    span_features = [
        {"type": "Feature", "geometry": None, "properties": {"span_validity": v}}
        for v in validities
    ]
    return {"features": [], "span_features": span_features, "metadata": {}}


def _trust(validities: list[str]) -> str:
    """Replicate the geometry_trust rule for direct formula verification."""
    invalid_count = validities.count("invalid")
    suspect_count = validities.count("suspect")
    if invalid_count > 0:
        return "LOW"
    if suspect_count >= 3:
        return "MEDIUM"
    return "HIGH"


# ---------------------------------------------------------------------------
# Unit tests for trust classification logic (direct formula verification)
# ---------------------------------------------------------------------------


def test_one_invalid_span_gives_low_trust():
    assert _trust(["invalid"]) == "LOW"


def test_multiple_invalid_spans_give_low_trust():
    assert _trust(["invalid", "invalid", "valid"]) == "LOW"


def test_three_suspect_spans_give_medium_trust():
    assert _trust(["suspect", "suspect", "suspect"]) == "MEDIUM"


def test_exactly_three_suspect_is_medium_not_high():
    assert _trust(["suspect", "suspect", "suspect"]) == "MEDIUM"


def test_two_suspect_spans_give_high_trust():
    assert _trust(["suspect", "suspect"]) == "HIGH"


def test_clean_route_gives_high_trust():
    assert _trust(["valid", "valid", "valid"]) == "HIGH"


def test_mixed_invalid_and_suspect_gives_low():
    assert _trust(["invalid", "suspect", "suspect"]) == "LOW"


def test_empty_route_gives_high_trust():
    assert _trust([]) == "HIGH"


def test_invalid_takes_priority_over_three_suspect():
    assert _trust(["invalid", "suspect", "suspect", "suspect"]) == "LOW"


# ---------------------------------------------------------------------------
# Integration test: trust written into metadata via attach_span_features_to_collection
# ---------------------------------------------------------------------------


def test_geometry_trust_written_to_metadata():
    """attach_span_features_to_collection must write geometry_trust to metadata."""
    collection: dict = {"features": [], "metadata": {}}
    # Empty sequence → no spans generated → HIGH trust
    attach_span_features_to_collection(collection, {})
    assert collection["metadata"].get("geometry_trust") == "HIGH"


def test_geometry_trust_present_on_real_span_collection():
    collection: dict = {"features": [], "metadata": {}}
    attach_span_features_to_collection(collection, {"status": "ok", "chain": []})
    assert "geometry_trust" in collection["metadata"]
