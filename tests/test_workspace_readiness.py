"""Tests for Stage 6E workspace readiness display adapter."""

from __future__ import annotations

import json
from pathlib import Path

from gridflow.merge.models import MergedPole
from gridflow.workspace.readiness_adapter import (
    CONDUCTOR_CAUTION,
    DISPLAY_INSUFFICIENT,
    DISPLAY_NOT_READY,
    DISPLAY_READY,
    DISPLAY_REVIEW,
    load_job_readiness_summary,
    load_pole_readiness,
)

# ── MergedPole helpers ────────────────────────────────────────────────────────


def _ready_pole(support_no: str = "900344") -> MergedPole:
    return MergedPole(
        support_no=support_no,
        design_ready=True,
        design_blocked=False,
        field_photo_count=5,
        notes_content="Support No: 900344",
        voltage_verification_required=False,
        conductor_verification_required=False,
        pole_class_verification_required=False,
        condition_verification_required=False,
        identity_verification_required=False,
        equipment_conflict_flag=False,
    )


def _blocked_pole(support_no: str = "900343") -> MergedPole:
    return MergedPole(
        support_no=support_no,
        design_ready=False,
        design_blocked=True,
        field_photo_count=3,
        notes_content="Support No: 900343",
        voltage_verification_required=True,
        conductor_verification_required=True,
        pole_class_verification_required=True,
        condition_verification_required=False,
        identity_verification_required=False,
        equipment_conflict_flag=False,
    )


def _minimal_pole(support_no: str = "999999") -> MergedPole:
    return MergedPole(
        support_no=support_no,
        design_ready=False,
        design_blocked=False,
        field_photo_count=0,
        voltage_verification_required=False,
        conductor_verification_required=False,
        pole_class_verification_required=False,
        condition_verification_required=False,
        identity_verification_required=False,
        equipment_conflict_flag=False,
    )


# ── load_pole_readiness — fallback from MergedPole flags ─────────────────────


def test_ready_pole_returns_display_ready(tmp_path):
    result = load_pole_readiness(tmp_path, _ready_pole())
    assert result.display_level == DISPLAY_READY
    assert result.blockers == []
    assert result.source == "merge_pipeline"


def test_blocked_pole_returns_not_ready(tmp_path):
    result = load_pole_readiness(tmp_path, _blocked_pole())
    assert result.display_level == DISPLAY_NOT_READY
    assert len(result.blockers) >= 1
    assert result.source == "merge_pipeline"


def test_blocked_pole_blockers_are_specific_strings(tmp_path):
    result = load_pole_readiness(tmp_path, _blocked_pole())
    blocker_text = " ".join(result.blockers)
    assert "conductor" in blocker_text.lower() or "voltage" in blocker_text.lower()


def test_not_ready_pole_has_conductor_caution(tmp_path):
    result = load_pole_readiness(tmp_path, _blocked_pole())
    assert result.cautions
    assert any("route-level" in c.lower() for c in result.cautions)


def test_minimal_pole_returns_insufficient(tmp_path):
    result = load_pole_readiness(tmp_path, _minimal_pole())
    assert result.display_level == DISPLAY_INSUFFICIENT


def test_pole_with_only_design_blocked_flag(tmp_path):
    pole = MergedPole(
        support_no="900001",
        design_ready=False,
        design_blocked=True,
        field_photo_count=1,
        voltage_verification_required=False,
        conductor_verification_required=False,
        pole_class_verification_required=False,
        condition_verification_required=False,
        identity_verification_required=False,
        equipment_conflict_flag=False,
    )
    result = load_pole_readiness(tmp_path, pole)
    assert result.display_level == DISPLAY_NOT_READY
    assert result.blockers


# ── load_pole_readiness — Stage 6E assessment file ───────────────────────────


def _write_assessment(job_dir: Path, records: list[dict]) -> None:
    path = job_dir / "06_readiness_assessment.json"
    path.write_text(json.dumps(records), encoding="utf-8")


def test_stage6e_design_ready_maps_to_display_ready(tmp_path):
    _write_assessment(
        tmp_path,
        [
            {
                "support_no": "900344",
                "readiness_level": "DESIGN_READY",
                "readiness_blockers": [],
                "readiness_cautions": [],
            }
        ],
    )
    result = load_pole_readiness(tmp_path, _ready_pole("900344"))
    assert result.display_level == DISPLAY_READY
    assert result.source == "stage_6e"


def test_stage6e_design_ready_with_cautions_maps_to_review(tmp_path):
    _write_assessment(
        tmp_path,
        [
            {
                "support_no": "900344",
                "readiness_level": "DESIGN_READY_WITH_CAUTIONS",
                "readiness_blockers": [],
                "readiness_cautions": ["Conductor route-level only"],
            }
        ],
    )
    result = load_pole_readiness(tmp_path, _ready_pole("900344"))
    assert result.display_level == DISPLAY_REVIEW
    assert "Conductor route-level only" in result.cautions


def test_stage6e_design_blocked_maps_to_not_ready(tmp_path):
    _write_assessment(
        tmp_path,
        [
            {
                "support_no": "900343",
                "readiness_level": "DESIGN_BLOCKED",
                "readiness_blockers": ["Conductor not span-linked"],
                "readiness_cautions": [],
            }
        ],
    )
    result = load_pole_readiness(tmp_path, _blocked_pole("900343"))
    assert result.display_level == DISPLAY_NOT_READY
    assert "Conductor not span-linked" in result.blockers


def test_stage6e_unknown_level_maps_to_insufficient(tmp_path):
    _write_assessment(
        tmp_path,
        [
            {
                "support_no": "900344",
                "readiness_level": "UNKNOWN_LEVEL",
                "readiness_blockers": [],
                "readiness_cautions": [],
            }
        ],
    )
    result = load_pole_readiness(tmp_path, _ready_pole("900344"))
    assert result.display_level == DISPLAY_INSUFFICIENT


def test_stage6e_missing_support_no_falls_back_to_pole_flags(tmp_path):
    _write_assessment(tmp_path, [{"support_no": "DIFFERENT", "readiness_level": "DESIGN_READY"}])
    result = load_pole_readiness(tmp_path, _blocked_pole("900343"))
    # falls back because support_no "900343" not in assessment
    assert result.source == "merge_pipeline"
    assert result.display_level == DISPLAY_NOT_READY


# ── load_job_readiness_summary ────────────────────────────────────────────────


def test_summary_from_poles_counts_correctly(tmp_path):
    poles = [_ready_pole("A"), _blocked_pole("B"), _blocked_pole("C"), _minimal_pole("D")]
    summary = load_job_readiness_summary(tmp_path, poles)
    assert summary.total_poles == 4
    assert summary.ready_count == 1
    assert summary.not_ready_count == 2
    assert summary.insufficient_count == 1
    assert summary.review_count == 0
    assert summary.source == "merge_pipeline"


def test_summary_from_stage6e_assessment(tmp_path):
    _write_assessment(
        tmp_path,
        [
            {"support_no": "A", "readiness_level": "DESIGN_READY"},
            {"support_no": "B", "readiness_level": "DESIGN_READY_WITH_CAUTIONS"},
            {"support_no": "C", "readiness_level": "DESIGN_READY_WITH_CAUTIONS"},
            {"support_no": "D", "readiness_level": "DESIGN_BLOCKED"},
            {"support_no": "E", "readiness_level": "DESIGN_BLOCKED"},
            {"support_no": "F", "readiness_level": "DESIGN_BLOCKED"},
        ],
    )
    summary = load_job_readiness_summary(tmp_path, [])
    assert summary.ready_count == 1
    assert summary.review_count == 2
    assert summary.not_ready_count == 3
    assert summary.source == "stage_6e"


def test_summary_p_local_002_profile(tmp_path):
    """Simulate P_LOCAL_002: 7 blocked + 3 would-be-review once Stage 6E runs."""
    poles = [_blocked_pole(f"P{i}") for i in range(10)]
    summary = load_job_readiness_summary(tmp_path, poles)
    assert summary.total_poles == 10
    assert summary.not_ready_count == 10
    assert summary.ready_count == 0


# ── design_ready not mutated ──────────────────────────────────────────────────


def test_readiness_adapter_does_not_set_design_ready(tmp_path):
    pole = _blocked_pole()
    original_flag = pole.design_ready
    load_pole_readiness(tmp_path, pole)
    assert pole.design_ready == original_flag


def test_readiness_adapter_does_not_clear_conductor_flag(tmp_path):
    pole = _blocked_pole()
    assert pole.conductor_verification_required is True
    load_pole_readiness(tmp_path, pole)
    assert pole.conductor_verification_required is True


def test_pole_readiness_display_has_no_design_ready_attribute():
    from gridflow.workspace.readiness_adapter import PoleReadinessDisplay

    pr = PoleReadinessDisplay(available=True, display_level=DISPLAY_READY)
    assert not hasattr(pr, "design_ready")
    assert not hasattr(pr, "conductor_spec_missing")


# ── caution wording ───────────────────────────────────────────────────────────


def test_conductor_caution_constant_contains_route_level():
    assert "route-level" in CONDUCTOR_CAUTION.lower()


def test_not_ready_fallback_includes_conductor_caution(tmp_path):
    result = load_pole_readiness(tmp_path, _blocked_pole())
    assert any("route-level" in c.lower() for c in result.cautions)
