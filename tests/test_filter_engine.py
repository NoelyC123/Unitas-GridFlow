"""Tests for Stage 7E PoleFilterEngine."""

from __future__ import annotations

import pytest

from gridflow.merge.models import MergedPole
from gridflow.workspace.filter_engine import PoleFilterEngine

# ── Fixtures ──────────────────────────────────────────────────────────────────


def _pole(
    support_no: str,
    folder_name: str | None = None,
    match_confidence: str = "HIGH",
    design_ready: bool = False,
    design_blocked: bool = True,
    review_required: bool = False,
    field_photo_count: int = 0,
    conflict_flags: list[str] | None = None,
    notes_content: str | None = None,
    conductor_verification_required: bool = True,
    voltage_verification_required: bool = True,
    pole_class_verification_required: bool = True,
) -> MergedPole:
    return MergedPole(
        support_no=support_no,
        folder_name=folder_name or f"01_SUPPORT_{support_no}",
        match_confidence=match_confidence,
        design_ready=design_ready,
        design_blocked=design_blocked,
        review_required=review_required,
        field_photo_count=field_photo_count,
        conflict_flags=conflict_flags or [],
        notes_content=notes_content,
        conductor_verification_required=conductor_verification_required,
        voltage_verification_required=voltage_verification_required,
        pole_class_verification_required=pole_class_verification_required,
        condition_verification_required=False,
        identity_verification_required=False,
        equipment_conflict_flag=False,
    )


@pytest.fixture
def sample_poles() -> list[MergedPole]:
    return [
        _pole(
            "900344",
            "05_SUPPORT_900344",
            match_confidence="HIGH",
            design_ready=False,
            design_blocked=True,
            field_photo_count=9,
            notes_content="Support number: 900344\nABS switch visible",
        ),
        _pole(
            "900345",
            "06_SUPPORT_900345",
            match_confidence="HIGH",
            design_ready=False,
            review_required=True,
            design_blocked=False,
            field_photo_count=14,
            conflict_flags=["POLE_TYPE_MISMATCH"],
        ),
        _pole(
            "902202",
            "01_SUPPORT_902202",
            match_confidence="MEDIUM",
            design_ready=False,
            design_blocked=True,
            field_photo_count=6,
        ),
        _pole(
            "903101",
            "10_SUPPORT_903101",
            match_confidence="MEDIUM",
            design_ready=False,
            design_blocked=True,
            field_photo_count=0,
        ),
        _pole(
            "999000",
            "99_SUPPORT_999000",
            match_confidence="UNMATCHED",
            design_ready=False,
            design_blocked=False,
            field_photo_count=0,
            voltage_verification_required=False,
            conductor_verification_required=False,
            pole_class_verification_required=False,
        ),
    ]


# ── No filters ────────────────────────────────────────────────────────────────


def test_no_filters_returns_all_poles(sample_poles):
    engine = PoleFilterEngine()
    result = engine.filter(sample_poles)
    assert len(result) == len(sample_poles)


def test_empty_pole_list_returns_empty(sample_poles):
    engine = PoleFilterEngine()
    assert engine.filter([]) == []


# ── Text search ───────────────────────────────────────────────────────────────


def test_search_matches_support_no(sample_poles):
    engine = PoleFilterEngine()
    result = engine.filter(sample_poles, query="900344")
    assert len(result) == 1
    assert result[0].support_no == "900344"


def test_search_matches_folder_name(sample_poles):
    engine = PoleFilterEngine()
    result = engine.filter(sample_poles, query="06_SUPPORT")
    assert len(result) == 1
    assert result[0].support_no == "900345"


def test_search_matches_notes_content(sample_poles):
    engine = PoleFilterEngine()
    result = engine.filter(sample_poles, query="ABS switch")
    assert len(result) == 1
    assert result[0].support_no == "900344"


def test_search_is_case_insensitive(sample_poles):
    engine = PoleFilterEngine()
    result = engine.filter(sample_poles, query="abs switch")
    assert len(result) == 1


def test_search_no_match_returns_empty(sample_poles):
    engine = PoleFilterEngine()
    result = engine.filter(sample_poles, query="NONEXISTENT_VALUE_XYZ")
    assert result == []


# ── Status filter ─────────────────────────────────────────────────────────────


def test_status_not_ready_returns_blocked_poles(sample_poles):
    engine = PoleFilterEngine()
    result = engine.filter(sample_poles, status="not_ready")
    support_nos = {p.support_no for p in result}
    assert "900344" in support_nos
    assert "902202" in support_nos
    assert "903101" in support_nos


def test_status_review_required_returns_review_poles(sample_poles):
    engine = PoleFilterEngine()
    result = engine.filter(sample_poles, status="review_required")
    assert len(result) == 1
    assert result[0].support_no == "900345"


def test_status_ready_returns_only_ready_poles():
    engine = PoleFilterEngine()
    poles = [
        _pole(
            "A",
            design_ready=True,
            design_blocked=False,
            conductor_verification_required=False,
            voltage_verification_required=False,
            pole_class_verification_required=False,
        ),
        _pole("B", design_ready=False, design_blocked=True),
    ]
    result = engine.filter(poles, status="ready")
    assert len(result) == 1
    assert result[0].support_no == "A"


def test_status_insufficient_evidence(sample_poles):
    engine = PoleFilterEngine()
    result = engine.filter(sample_poles, status="insufficient_evidence")
    assert len(result) == 1
    assert result[0].support_no == "999000"


# ── Confidence filter ─────────────────────────────────────────────────────────


def test_confidence_high_filter(sample_poles):
    engine = PoleFilterEngine()
    result = engine.filter(sample_poles, confidence="HIGH")
    support_nos = {p.support_no for p in result}
    assert "900344" in support_nos
    assert "900345" in support_nos
    assert "902202" not in support_nos


def test_confidence_medium_filter(sample_poles):
    engine = PoleFilterEngine()
    result = engine.filter(sample_poles, confidence="MEDIUM")
    support_nos = {p.support_no for p in result}
    assert "902202" in support_nos
    assert "903101" in support_nos
    assert "900344" not in support_nos


def test_confidence_unmatched_filter(sample_poles):
    engine = PoleFilterEngine()
    result = engine.filter(sample_poles, confidence="UNMATCHED")
    assert len(result) == 1
    assert result[0].support_no == "999000"


# ── Photo filter ──────────────────────────────────────────────────────────────


def test_has_photos_yes_returns_poles_with_photos(sample_poles):
    engine = PoleFilterEngine()
    result = engine.filter(sample_poles, has_photos=True)
    assert all(p.field_photo_count > 0 for p in result)
    assert len(result) == 3


def test_has_photos_no_returns_poles_without_photos(sample_poles):
    engine = PoleFilterEngine()
    result = engine.filter(sample_poles, has_photos=False)
    assert all(p.field_photo_count == 0 for p in result)
    assert len(result) == 2


# ── Conflict filter ───────────────────────────────────────────────────────────


def test_has_conflicts_yes_returns_poles_with_conflict_flags(sample_poles):
    engine = PoleFilterEngine()
    result = engine.filter(sample_poles, has_conflicts=True)
    assert len(result) == 1
    assert result[0].support_no == "900345"


def test_has_conflicts_no_returns_poles_without_conflict_flags(sample_poles):
    engine = PoleFilterEngine()
    result = engine.filter(sample_poles, has_conflicts=False)
    assert all(len(p.conflict_flags) == 0 for p in result)
    assert len(result) == 4


# ── Combined filters (AND logic) ──────────────────────────────────────────────


def test_multiple_filters_combined_and_logic(sample_poles):
    engine = PoleFilterEngine()
    result = engine.filter(sample_poles, confidence="HIGH", has_photos=True)
    assert len(result) == 2
    support_nos = {p.support_no for p in result}
    assert "900344" in support_nos
    assert "900345" in support_nos


def test_search_plus_status_combined(sample_poles):
    engine = PoleFilterEngine()
    result = engine.filter(sample_poles, query="900", status="not_ready")
    assert all(
        p.support_no.startswith("9003") or p.support_no.startswith("9021") or "903" in p.support_no
        for p in result
    )


def test_combined_filter_returning_empty(sample_poles):
    engine = PoleFilterEngine()
    result = engine.filter(
        sample_poles, confidence="HIGH", status="review_required", has_photos=False
    )
    assert result == []


# ── Sort ──────────────────────────────────────────────────────────────────────


def test_default_sort_is_by_folder_name(sample_poles):
    engine = PoleFilterEngine()
    result = engine.filter(sample_poles)
    folder_names = [p.folder_name for p in result]
    assert folder_names == sorted(folder_names)


def test_sort_by_pole_number(sample_poles):
    engine = PoleFilterEngine()
    result = engine.filter(sample_poles, sort_by="pole_number")
    folder_names = [p.folder_name for p in result]
    assert folder_names == sorted(folder_names)


def test_sort_by_photo_count_descending(sample_poles):
    engine = PoleFilterEngine()
    result = engine.filter(sample_poles, sort_by="photo_count")
    counts = [p.field_photo_count for p in result]
    assert counts == sorted(counts, reverse=True)


def test_sort_by_conflict_count_descending(sample_poles):
    engine = PoleFilterEngine()
    result = engine.filter(sample_poles, sort_by="conflict_count")
    counts = [len(p.conflict_flags) for p in result]
    assert counts == sorted(counts, reverse=True)


def test_sort_by_readiness_status(sample_poles):
    engine = PoleFilterEngine()
    result = engine.filter(sample_poles, sort_by="readiness_status")
    assert len(result) == len(sample_poles)


def test_sort_by_linking_confidence(sample_poles):
    engine = PoleFilterEngine()
    result = engine.filter(sample_poles, sort_by="linking_confidence")
    confidences = [p.match_confidence for p in result]
    assert confidences[0] in ("HIGH",)


def test_unknown_sort_key_falls_back_to_pole_number(sample_poles):
    engine = PoleFilterEngine()
    result = engine.filter(sample_poles, sort_by="NONEXISTENT")
    assert len(result) == len(sample_poles)
