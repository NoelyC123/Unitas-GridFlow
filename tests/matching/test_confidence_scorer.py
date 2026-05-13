"""Tests for ConfidenceScorer."""

import pytest

from gridflow.baseline.models import BaselinePole, VoltageLevel
from gridflow.field.models import FieldPole
from gridflow.matching import ConfidenceScorer
from gridflow.matching.models import MatchResult


@pytest.fixture
def scorer():
    return ConfidenceScorer()


def make_bp(support_no="903203", voltage=VoltageLevel.LV) -> BaselinePole:
    return BaselinePole(
        pole_id="P01",
        support_no=support_no,
        easting=354123.0,
        northing=456789.0,
        voltage_level=voltage,
    )


def make_fp(support_no="903203", quality="HIGH", flags=None, notes=None) -> FieldPole:
    return FieldPole(
        folder_name=f"01_SUPPORT_{support_no}_LV",
        support_no=support_no,
        evidence_quality=quality,
        map_popup_present="yes",
        special_flags=flags or [],
        parsed_notes=notes or {"support_no": support_no, "voltage": "LV"},
    )


def make_mr(
    support_no="903203",
    match_type="EXACT",
    reasons=None,
) -> MatchResult:
    return MatchResult(
        baseline_pole_id="P01",
        baseline_support_no=support_no,
        field_folder=f"01_SUPPORT_{support_no}_LV",
        field_support_no=support_no,
        match_type=match_type,
        confidence_reasons=reasons or [],
    )


def test_high_confidence_exact_high_evidence(scorer):
    mr = scorer.score(make_mr(), make_bp(), make_fp())
    assert mr.match_confidence == "HIGH"
    assert not mr.review_required


def test_medium_confidence_no_popup(scorer):
    fp = make_fp()
    fp.map_popup_present = "uncertain"
    fp.evidence_quality = "MEDIUM"
    fp.special_flags = ["NO_POLE_POPUP"]
    mr = scorer.score(make_mr(), make_bp(), fp)
    assert mr.match_confidence == "MEDIUM"


def test_medium_confidence_variant_support(scorer):
    fp = make_fp(support_no="903201A")
    fp.special_flags = ["VARIANT_SUPPORT_NO"]
    bp = make_bp(support_no="903201A")
    mr = make_mr(support_no="903201A")
    result = scorer.score(mr, bp, fp)
    assert result.match_confidence in ("HIGH", "MEDIUM")


def test_low_confidence_low_evidence(scorer):
    fp = make_fp(quality="LOW")
    mr = scorer.score(make_mr(), make_bp(), fp)
    assert mr.match_confidence == "LOW"


def test_unmatched_confidence(scorer):
    mr = MatchResult(
        baseline_pole_id="P01",
        baseline_support_no="903203",
        match_type="UNMATCHED",
    )
    result = scorer.score(mr, make_bp(), None)
    assert result.match_confidence == "UNMATCHED"
    assert result.review_required is True


def test_conflict_detection_support_no(scorer):
    # Notes say support_no = 900000 but baseline is 903203 — conflict
    fp = make_fp(notes={"support_no": "900000", "voltage": "LV"})
    mr = scorer.score(make_mr(), make_bp(support_no="903203"), fp)
    assert "SUPPORT_NO_CONFLICT" in mr.conflict_flags


def test_no_conflict_matching_support_no(scorer):
    fp = make_fp(notes={"support_no": "903203", "voltage": "LV"})
    mr = scorer.score(make_mr(), make_bp(support_no="903203"), fp)
    assert "SUPPORT_NO_CONFLICT" not in mr.conflict_flags
