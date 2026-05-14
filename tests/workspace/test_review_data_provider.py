"""Tests for ReviewDataProvider — uses actual MergedPole field names."""

import json
from pathlib import Path

import pytest

from gridflow.workspace import ReviewDataProvider


def _make_dataset_json(poles_data: list[dict]) -> dict:
    """Wrap poles in MergedDataset structure as pipeline writes it."""
    return {
        "baseline_source": "test.csv",
        "field_source": "/test/field",
        "merge_date": "2026-05-14",
        "total_poles_baseline": len(poles_data),
        "total_poles_field": len(poles_data),
        "total_matched": len(poles_data),
        "poles": poles_data,
        "unmatched_baseline": [],
        "unmatched_field": [],
    }


def _ready_pole(support_no: str, **kwargs) -> dict:
    """Build a design-ready MergedPole dict."""
    return {
        "support_no": support_no,
        "design_ready": True,
        "design_blocked": False,
        "match_confidence": "HIGH",
        "field_photo_count": 5,
        "notes_content": "Support No: 903203\nVoltage: LV",
        "special_flags": [],
        "voltage_verification_required": False,
        "conductor_verification_required": False,
        "pole_class_verification_required": False,
        "condition_verification_required": False,
        "identity_verification_required": False,
        "equipment_conflict_flag": False,
        **kwargs,
    }


def _blocked_pole(support_no: str, **kwargs) -> dict:
    """Build a design-blocked MergedPole dict."""
    return {
        "support_no": support_no,
        "design_ready": False,
        "design_blocked": True,
        "match_confidence": "LOW",
        "field_photo_count": 3,
        "notes_content": "Support No: 900346\nVoltage: HV",
        "special_flags": ["NO_POLE_POPUP"],
        "voltage_verification_required": True,
        "conductor_verification_required": True,
        "pole_class_verification_required": True,
        "condition_verification_required": False,
        "identity_verification_required": True,
        "equipment_conflict_flag": False,
        **kwargs,
    }


@pytest.fixture
def mock_job_dir(tmp_path):
    """Job directory with two poles — one ready, one blocked."""
    job_dir = tmp_path / "test_job"
    job_dir.mkdir()

    poles = [_ready_pole("POLE001"), _blocked_pole("POLE002")]
    dataset_path = job_dir / "04_merged_dataset.json"
    dataset_path.write_text(json.dumps(_make_dataset_json(poles)), encoding="utf-8")
    return job_dir


def test_load_job_returns_metadata(mock_job_dir):
    """load_job returns pole_count and loaded=True."""
    provider = ReviewDataProvider(mock_job_dir)
    result = provider.load_job()

    assert result["loaded"] is True
    assert result["pole_count"] == 2


def test_load_job_missing_dataset_raises():
    """load_job raises FileNotFoundError when dataset is absent."""
    provider = ReviewDataProvider(Path("/nonexistent/job"))
    with pytest.raises(FileNotFoundError):
        provider.load_job()


def test_get_poles_no_filter_returns_all(mock_job_dir):
    """get_poles with no filters returns all loaded poles."""
    provider = ReviewDataProvider(mock_job_dir)
    poles = provider.get_poles()
    assert len(poles) == 2


def test_get_poles_filter_design_ready(mock_job_dir):
    """Filter by design_ready=True returns only ready pole."""
    provider = ReviewDataProvider(mock_job_dir)

    ready = provider.get_poles({"design_ready": True})
    assert len(ready) == 1
    assert ready[0].support_no == "POLE001"

    blocked = provider.get_poles({"design_ready": False})
    assert len(blocked) == 1
    assert blocked[0].support_no == "POLE002"


def test_get_poles_filter_evidence_quality(mock_job_dir):
    """Filter by evidence_quality derives quality from field data correctly."""
    provider = ReviewDataProvider(mock_job_dir)

    # POLE001: 5 photos, notes present, no NO_POLE_POPUP → HIGH
    high = provider.get_poles({"evidence_quality": "HIGH"})
    assert len(high) == 1
    assert high[0].support_no == "POLE001"

    # POLE002: 3 photos, notes present, NO_POLE_POPUP → MEDIUM
    medium = provider.get_poles({"evidence_quality": "MEDIUM"})
    assert len(medium) == 1
    assert medium[0].support_no == "POLE002"


def test_get_poles_filter_match_confidence(mock_job_dir):
    """Filter by match_confidence uses actual MergedPole field."""
    provider = ReviewDataProvider(mock_job_dir)

    high = provider.get_poles({"match_confidence": "HIGH"})
    assert len(high) == 1
    assert high[0].support_no == "POLE001"

    low = provider.get_poles({"match_confidence": "LOW"})
    assert len(low) == 1
    assert low[0].support_no == "POLE002"


def test_get_poles_filter_has_flags(mock_job_dir):
    """Filter by has_flags=True returns poles with any verification flag."""
    provider = ReviewDataProvider(mock_job_dir)

    flagged = provider.get_poles({"has_flags": True})
    assert len(flagged) == 1
    assert flagged[0].support_no == "POLE002"


def test_get_pole_details_found(mock_job_dir):
    """get_pole_details returns correct pole by support_no."""
    provider = ReviewDataProvider(mock_job_dir)

    pole = provider.get_pole_details("POLE001")
    assert pole is not None
    assert pole.support_no == "POLE001"


def test_get_pole_details_not_found(mock_job_dir):
    """get_pole_details returns None for unknown support_no."""
    provider = ReviewDataProvider(mock_job_dir)
    assert provider.get_pole_details("POLE999") is None


def test_get_statistics_counts(mock_job_dir):
    """get_statistics returns correct counts."""
    provider = ReviewDataProvider(mock_job_dir)
    stats = provider.get_statistics()

    assert stats["total_poles"] == 2
    assert stats["design_ready"] == 1
    assert stats["design_blocked"] == 1
    assert stats["evidence_quality"]["HIGH"] == 1
    assert stats["evidence_quality"]["MEDIUM"] == 1
    assert stats["match_confidence"]["HIGH"] == 1
    assert stats["match_confidence"]["LOW"] == 1
    assert stats["poles_with_flags"] == 1


def test_get_statistics_empty_job(tmp_path):
    """get_statistics handles an empty dataset gracefully."""
    job_dir = tmp_path / "empty_job"
    job_dir.mkdir()
    (job_dir / "04_merged_dataset.json").write_text(
        json.dumps(_make_dataset_json([])), encoding="utf-8"
    )

    provider = ReviewDataProvider(job_dir)
    stats = provider.get_statistics()
    assert stats["total_poles"] == 0
    assert stats["design_ready"] == 0
    assert stats["poles_with_flags"] == 0


def test_lazy_load_on_get_poles(mock_job_dir):
    """get_poles triggers load_job automatically if not called first."""
    provider = ReviewDataProvider(mock_job_dir)
    assert provider._poles is None

    poles = provider.get_poles()
    assert provider._poles is not None
    assert len(poles) == 2
