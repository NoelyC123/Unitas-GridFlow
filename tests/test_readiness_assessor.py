"""Tests for Stage 6E conservative design-readiness assessment."""

from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace

import pytest

from gridflow.conflict_detector import ConflictResult
from gridflow.readiness import ReadinessAssessor


def _make_combined(
    tmp_path: Path,
    *,
    pole_id: str = "03_SUPPORT_900343",
    support_no: str | None = "900343",
    pole_fid: str | None = "16869661",
    spn: str | None = "61090H00343",
    pole_class: str | None = "Single Wood Pole",
    route_conductor_evidence: list[dict] | None = None,
) -> dict:
    pole_dir = tmp_path / pole_id
    notes_dir = pole_dir / "notes"
    photo_dir = pole_dir / "field_photos"
    notes_dir.mkdir(parents=True)
    photo_dir.mkdir(parents=True)
    (notes_dir / "pole_notes.md").write_text("# Pole notes\n", encoding="utf-8")
    for idx in range(3):
        (photo_dir / f"photo_{idx}.jpg").write_text("x", encoding="utf-8")
    return {
        "pole_id": pole_id,
        "support_no": support_no,
        "pole_fid": pole_fid,
        "spn": spn,
        "pole_class": pole_class,
        "direct_equipment_records": [],
        "route_conductor_evidence": route_conductor_evidence or [],
        "nearby_context": [],
        "contributing_files": {
            "pole_folder": str(pole_dir),
            "pole_notes": str(notes_dir / "pole_notes.md"),
        },
    }


def _linking(
    confidence: str = "HIGH",
    method: str = "fid_polestructure",
    manual: bool = False,
):
    return SimpleNamespace(
        confidence=confidence, linking_method=method, manual_confirmation_required=manual
    )


def _critical_conflict() -> ConflictResult:
    return ConflictResult(
        pole_id="03_SUPPORT_900343",
        conflict_type="equipment_mismatch",
        severity="CRITICAL",
        field_value="Switch present",
        enwl_value="No equipment record",
        trace_value=None,
        description="Equipment mismatch unresolved.",
        recommended_action="Resolve before design.",
    )


def _warning_conflict() -> ConflictResult:
    return ConflictResult(
        pole_id="03_SUPPORT_900343",
        conflict_type="coordinate_mismatch",
        severity="WARNING",
        field_value="54.1,-2.7",
        enwl_value="54.1008,-2.7008",
        trace_value="65m",
        description="Coordinate mismatch exceeds threshold.",
        recommended_action="Verify with field photos.",
    )


def test_high_linking_plus_span_confirmed_conductor_is_ready(tmp_path):
    combined = _make_combined(
        tmp_path,
        route_conductor_evidence=[
            {"fid": "1", "span_confirmed": True, "link_basis": "span_link_confirmed"}
        ],
    )
    result = ReadinessAssessor().assess_from_records(combined, _linking("HIGH"), [])
    assert result.design_ready is True
    assert result.readiness_status == "ready"


def test_high_linking_plus_route_only_conductor_is_review_required(tmp_path):
    combined = _make_combined(
        tmp_path, route_conductor_evidence=[{"fid": "1", "link_basis": "proximity_candidate"}]
    )
    result = ReadinessAssessor().assess_from_records(combined, _linking("HIGH"), [])
    assert result.design_ready is False
    assert result.readiness_status == "review_required"
    assert "Conductor evidence route-level only" in " ".join(result.readiness_warnings)


def test_medium_linking_plus_route_conductor_is_review_required(tmp_path):
    combined = _make_combined(tmp_path, route_conductor_evidence=[{"fid": "1"}])
    result = ReadinessAssessor().assess_from_records(combined, _linking("MEDIUM", "support_no"), [])
    assert result.design_ready is False
    assert result.readiness_status == "review_required"
    assert result.readiness_confidence == "medium"


def test_medium_linking_plus_no_conductor_is_not_ready(tmp_path):
    combined = _make_combined(tmp_path, route_conductor_evidence=[])
    result = ReadinessAssessor().assess_from_records(combined, _linking("MEDIUM", "support_no"), [])
    assert result.design_ready is False
    assert result.readiness_status == "not_ready"
    assert "No conductor evidence present" in result.readiness_blockers


def test_low_linking_is_insufficient_evidence(tmp_path):
    combined = _make_combined(tmp_path, route_conductor_evidence=[{"fid": "1"}])
    result = ReadinessAssessor().assess_from_records(
        combined, _linking("LOW", "gps_proximity", manual=True), []
    )
    assert result.design_ready is False
    assert result.readiness_status == "insufficient_evidence"


def test_any_critical_conflict_is_not_ready(tmp_path):
    combined = _make_combined(
        tmp_path, route_conductor_evidence=[{"fid": "1", "span_confirmed": True}]
    )
    result = ReadinessAssessor().assess_from_records(
        combined, _linking("HIGH"), [_critical_conflict()]
    )
    assert result.design_ready is False
    assert result.readiness_status == "not_ready"
    assert result.critical_conflicts == 1


def test_no_support_number_is_insufficient_evidence(tmp_path):
    combined = _make_combined(tmp_path, support_no=None, route_conductor_evidence=[{"fid": "1"}])
    result = ReadinessAssessor().assess_from_records(combined, _linking("MEDIUM", "support_no"), [])
    assert result.readiness_status == "insufficient_evidence"
    assert any("support_no" in blocker for blocker in result.readiness_blockers)


def test_enwl_conductor_alone_does_not_make_design_ready_true(tmp_path):
    combined = _make_combined(
        tmp_path, route_conductor_evidence=[{"fid": "1", "text_map": "3x 50 Al 11"}]
    )
    result = ReadinessAssessor().assess_from_records(combined, _linking("HIGH"), [])
    assert result.design_ready is False
    assert result.readiness_status == "review_required"


def test_backward_compatibility_design_ready_boolean_present(tmp_path):
    combined = _make_combined(tmp_path, route_conductor_evidence=[{"fid": "1"}])
    result = ReadinessAssessor().assess_from_records(combined, _linking("MEDIUM"), [])
    assert isinstance(result.design_ready, bool)


def test_blockers_and_warnings_are_specific(tmp_path):
    combined = _make_combined(tmp_path, route_conductor_evidence=[])
    result = ReadinessAssessor().assess_from_records(
        combined, _linking("MEDIUM"), [_warning_conflict()]
    )
    assert any("No conductor evidence present" in blocker for blocker in result.readiness_blockers)
    assert any("Stage 6D WARNING" in warning for warning in result.readiness_warnings)


def test_evidence_basis_populated(tmp_path):
    combined = _make_combined(tmp_path, route_conductor_evidence=[{"fid": "1"}])
    result = ReadinessAssessor().assess_from_records(combined, _linking("HIGH"), [])
    assert result.evidence_basis
    assert "field_notes" in result.evidence_basis
    assert "enwl_linking" in result.evidence_basis


def test_real_plocal002_assessment_if_available():
    survey_root = Path("real_pilot_data/P_LOCAL_002")
    trace_path = survey_root / "enwl_trace" / "enwl_trace_10924865_with_ratings.geojson"
    if not trace_path.exists():
        pytest.skip("P_LOCAL_002 trace file not available")

    results = ReadinessAssessor().assess_survey(survey_root, trace_path)
    by_status: dict[str, list[str]] = {}
    for result in results:
        by_status.setdefault(result.readiness_status, []).append(result.pole_id)

    assert len([r for r in results if r.design_ready]) == 0
    assert sorted(by_status.get("review_required", [])) == [
        "03_SUPPORT_900343",
        "05_SUPPORT_900344",
        "06_SUPPORT_900345",
    ]
    assert len(by_status.get("not_ready", [])) == 7
