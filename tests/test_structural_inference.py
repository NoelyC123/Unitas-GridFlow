"""Tests for structural stay-wire inference from route angle deviation."""

from __future__ import annotations

from app.routes.map_preview import apply_structural_inference

# ---------------------------------------------------------------------------
# Core angle logic
# ---------------------------------------------------------------------------


def test_angle_above_threshold_infers_stay_required():
    props = {"route_deviation_deg": 20}
    apply_structural_inference(props)
    assert props["inferred_requires_stay"] is True
    assert props["inference_source"] == "geometry_angle"
    assert props["inference_confidence"] == "medium"


def test_angle_below_threshold_infers_no_stay():
    props = {"route_deviation_deg": 10}
    apply_structural_inference(props)
    assert props["inferred_requires_stay"] is False
    assert props["inference_source"] == "geometry_angle"
    assert props["inference_confidence"] == "low"


def test_angle_exactly_at_threshold_is_not_inferred():
    # > 15 is the rule; exactly 15 → False
    props = {"route_deviation_deg": 15}
    apply_structural_inference(props)
    assert props["inferred_requires_stay"] is False


def test_angle_just_above_threshold_infers_stay():
    props = {"route_deviation_deg": 15.1}
    apply_structural_inference(props)
    assert props["inferred_requires_stay"] is True


# ---------------------------------------------------------------------------
# Missing / unparseable angle → no inference
# ---------------------------------------------------------------------------


def test_missing_angle_adds_no_inference_fields():
    props: dict = {}
    apply_structural_inference(props)
    assert "inferred_requires_stay" not in props
    assert "inference_source" not in props
    assert "inference_confidence" not in props


def test_none_angle_adds_no_inference_fields():
    props = {"route_deviation_deg": None}
    apply_structural_inference(props)
    assert "inferred_requires_stay" not in props


def test_string_angle_that_cannot_be_parsed_adds_no_fields():
    props = {"route_deviation_deg": "unknown"}
    apply_structural_inference(props)
    assert "inferred_requires_stay" not in props


def test_valid_string_angle_is_parsed_correctly():
    props = {"route_deviation_deg": "22"}
    apply_structural_inference(props)
    assert props["inferred_requires_stay"] is True


# ---------------------------------------------------------------------------
# Survey truth is never overwritten
# ---------------------------------------------------------------------------


def test_existing_stay_present_false_not_overwritten():
    props = {"route_deviation_deg": 25, "stay_present": False}
    apply_structural_inference(props)
    assert props["stay_present"] is False  # survey truth preserved
    assert props["inferred_requires_stay"] is True  # inference visible alongside


def test_existing_stay_present_true_not_overwritten():
    props = {"route_deviation_deg": 5, "stay_present": True}
    apply_structural_inference(props)
    assert props["stay_present"] is True
    assert props["inferred_requires_stay"] is False


def test_stay_type_not_overwritten():
    props = {"route_deviation_deg": 30, "stay_type": "strut"}
    apply_structural_inference(props)
    assert props["stay_type"] == "strut"


def test_stay_configuration_not_overwritten():
    props = {"route_deviation_deg": 30, "stay_configuration": "back"}
    apply_structural_inference(props)
    assert props["stay_configuration"] == "back"


# ---------------------------------------------------------------------------
# Intentional tension case: survey says no stay, geometry says needed
# ---------------------------------------------------------------------------


def test_conflicting_case_shows_both_fields():
    props = {"route_deviation_deg": 25, "stay_present": False}
    apply_structural_inference(props)
    assert props["stay_present"] is False
    assert props["inferred_requires_stay"] is True
    assert props["inference_confidence"] == "medium"
