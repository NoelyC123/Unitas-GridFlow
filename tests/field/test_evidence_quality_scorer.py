"""Tests for EvidenceQualityScorer."""

import pytest

from gridflow.field import EvidenceQualityScorer, FieldDataset, FieldPole


@pytest.fixture
def scorer():
    return EvidenceQualityScorer()


def make_pole(**kwargs) -> FieldPole:
    defaults = dict(
        folder_name="01_SUPPORT_903203_LV",
        support_no="903203",
        field_photo_count=3,
        map_screenshot_count=1,
        notes_present=True,
        map_popup_present="yes",
        special_flags=[],
    )
    defaults.update(kwargs)
    return FieldPole(**defaults)


def test_score_high(scorer):
    pole = make_pole(
        field_photo_count=3,
        map_screenshot_count=1,
        notes_present=True,
        map_popup_present="yes",
    )
    assert scorer.score(pole) == "HIGH"


def test_score_medium_no_popup(scorer):
    pole = make_pole(
        field_photo_count=3,
        map_screenshot_count=1,
        notes_present=True,
        map_popup_present="uncertain",
    )
    assert scorer.score(pole) == "MEDIUM"


def test_score_low_photos(scorer):
    pole = make_pole(field_photo_count=2)
    assert scorer.score(pole) == "LOW"


def test_score_low_unknown_support(scorer):
    pole = make_pole(special_flags=["UNKNOWN_SUPPORT"])
    assert scorer.score(pole) == "LOW"


def test_score_low_no_notes(scorer):
    pole = make_pole(notes_present=False)
    assert scorer.score(pole) == "LOW"


def test_score_low_no_screenshots(scorer):
    pole = make_pole(map_screenshot_count=0)
    assert scorer.score(pole) == "LOW"


def test_score_dataset(scorer):
    poles = [
        make_pole(folder_name="01_SUPPORT_903203_LV", support_no="903203"),
        make_pole(
            folder_name="08_SUPPORT_900346_HV",
            support_no="900346",
            map_popup_present="uncertain",
        ),
    ]
    dataset = FieldDataset(
        dataset_path="/test",
        scan_date="2026-01-01",
        total_poles=2,
        poles=poles,
    )
    scored = scorer.score_dataset(dataset)
    qualities = {p.support_no: p.evidence_quality for p in scored.poles}
    assert qualities["903203"] == "HIGH"
    assert qualities["900346"] == "MEDIUM"
    assert scored.evidence_summary["high"] == 1
    assert scored.evidence_summary["medium"] == 1
