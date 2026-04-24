from __future__ import annotations

import pandas as pd

from app.issue_model import (
    build_evidence_gates,
    build_recommended_actions,
    classify_issue,
    enrich_issues,
)

# ---------------------------------------------------------------------------
# classify_issue
# ---------------------------------------------------------------------------


def test_classify_issue_replacement_pair_is_observation() -> None:
    meta = classify_issue("Replacement pair detected (EX → PR, 2.3m offset)")
    assert meta["issue_code"] == "REPL_PAIR"
    assert meta["severity"] == "observation"
    assert meta["is_observation"] is True
    assert meta["category"] == "replacement_intent"


def test_classify_issue_angle_no_stay_is_warning_with_action() -> None:
    meta = classify_issue(
        "Angle structure with no stay evidence detected — verify whether stay capture is missing"
    )
    assert meta["issue_code"] == "ANGLE_NO_STAY"
    assert meta["severity"] == "warning"
    assert meta["is_observation"] is False
    assert meta["recommended_action"] is not None


def test_classify_issue_missing_height_has_recommended_action() -> None:
    meta = classify_issue("Missing required field: height")
    assert meta["issue_code"] == "MISS_HEIGHT"
    assert meta["severity"] == "warning"
    assert meta["category"] == "data_completeness"
    assert "height" in meta["recommended_action"].lower()


def test_classify_issue_missing_material_has_structural_evidence_category() -> None:
    meta = classify_issue("Missing required field: material")
    assert meta["issue_code"] == "MISS_MATERIAL"
    assert meta["category"] == "structural_evidence"
    assert meta["recommended_action"] is not None


def test_classify_issue_missing_field_generic_fallback() -> None:
    meta = classify_issue("Missing required field: location")
    assert meta["issue_code"] == "MISS_FIELD"
    assert meta["category"] == "data_completeness"


def test_classify_issue_span_very_short_tier() -> None:
    meta = classify_issue("Span very short: 1.2m — likely duplicate or co-located pair, verify")
    assert meta["issue_code"] == "SPAN_VERY_SHORT"
    assert meta["category"] == "span_geometry"


def test_classify_issue_span_unusually_short_tier() -> None:
    meta = classify_issue("Span unusually short: 5.0m (min 10m) — verify no duplicate entry")
    assert meta["issue_code"] == "SPAN_SHORT"
    assert meta["category"] == "span_geometry"


def test_classify_issue_span_borderline_short_tier() -> None:
    meta = classify_issue("Span borderline short: 9.1m (min 10m) — verify no missing record")
    assert meta["issue_code"] == "SPAN_BORDERLINE"
    assert meta["category"] == "span_geometry"


def test_classify_issue_span_too_long() -> None:
    meta = classify_issue("Span too long: 520.0m between structural records (max 500m)")
    assert meta["issue_code"] == "SPAN_LONG"
    assert meta["category"] == "span_geometry"


def test_classify_issue_coordinate_mismatch_is_critical() -> None:
    meta = classify_issue(
        "Coordinate mismatch: lat/lon and easting/northing are 250m apart (tolerance 100m)"
    )
    assert meta["issue_code"] == "COORD_MISMATCH"
    assert meta["severity"] == "critical"
    assert meta["category"] == "coordinate_quality"


def test_classify_issue_duplicate_pair_is_critical() -> None:
    meta = classify_issue("Duplicate pair (lat, lon): 54.123, -1.456")
    assert meta["issue_code"] == "COORD_DUPLICATE"
    assert meta["severity"] == "critical"


def test_classify_issue_expole_height_estimated() -> None:
    meta = classify_issue("Height likely estimated / not captured (EXpole)")
    assert meta["issue_code"] == "EXPOLE_HEIGHT_EST"
    assert meta["category"] == "structural_evidence"
    assert meta["confidence"] == "medium"


def test_classify_issue_missing_column_is_critical() -> None:
    meta = classify_issue("Missing column: lat")
    assert meta["issue_code"] == "MISSING_COLUMN"
    assert meta["severity"] == "critical"


def test_classify_issue_unknown_text_uses_fallback() -> None:
    meta = classify_issue("Some completely unexpected issue text")
    assert meta["issue_code"] == "UNKNOWN"
    assert meta["severity"] == "warning"
    assert meta["confidence"] == "low"
    assert meta["is_observation"] is False


def test_classify_issue_height_range_before_generic_range() -> None:
    meta = classify_issue("height out of range (7-20)")
    assert meta["issue_code"] == "HEIGHT_RANGE"
    assert meta["category"] == "rulepack_validation"


def test_classify_issue_other_field_range_uses_generic() -> None:
    meta = classify_issue("lat out of range (49-61)")
    assert meta["issue_code"] == "FIELD_RANGE"


# ---------------------------------------------------------------------------
# enrich_issues
# ---------------------------------------------------------------------------


def test_enrich_issues_adds_all_structured_columns() -> None:
    issues_df = pd.DataFrame(
        [
            {"Issue": "Missing required field: height", "Row": {}, "Severity": None},
            {
                "Issue": "Replacement pair detected (EX → PR, 3.0m offset)",
                "Row": {},
                "Severity": "WARN",
            },
        ]
    )
    enriched = enrich_issues(issues_df)

    for col in (
        "issue_code",
        "severity",
        "category",
        "scope",
        "confidence",
        "is_observation",
        "recommended_action",
    ):
        assert col in enriched.columns, f"Column {col!r} missing from enriched DataFrame"


def test_enrich_issues_preserves_existing_columns() -> None:
    issues_df = pd.DataFrame(
        [
            {
                "Issue": "Angle structure with no stay evidence detected",
                "Row": {"pole_id": "1"},
                "Severity": "WARN",
            }
        ]
    )
    enriched = enrich_issues(issues_df)

    assert "Issue" in enriched.columns
    assert "Row" in enriched.columns
    assert "Severity" in enriched.columns


def test_enrich_issues_replacement_pair_classified_correctly() -> None:
    issues_df = pd.DataFrame(
        [
            {
                "Issue": "Replacement pair detected (EX → PR, 2.1m offset)",
                "Row": {},
                "Severity": "WARN",
            }
        ]
    )
    enriched = enrich_issues(issues_df)

    row = enriched.iloc[0]
    assert row["issue_code"] == "REPL_PAIR"
    assert bool(row["is_observation"])
    assert row["severity"] == "observation"


def test_enrich_issues_empty_df_returns_empty_with_schema_columns() -> None:
    empty_df = pd.DataFrame(columns=["Issue", "Row", "Severity"])
    enriched = enrich_issues(empty_df)

    assert len(enriched) == 0
    for col in (
        "issue_code",
        "severity",
        "category",
        "scope",
        "confidence",
        "is_observation",
        "recommended_action",
    ):
        assert col in enriched.columns


def test_enrich_issues_does_not_mutate_original() -> None:
    original = pd.DataFrame([{"Issue": "Missing required field: height", "Row": {}}])
    _ = enrich_issues(original)

    assert "issue_code" not in original.columns


def test_enrich_issues_row_count_unchanged() -> None:
    issues_df = pd.DataFrame(
        [
            {"Issue": "Span very short: 1.5m — likely duplicate", "Row": {}},
            {"Issue": "Angle structure with no stay evidence detected", "Row": {}},
            {"Issue": "Missing required field: material", "Row": {}},
        ]
    )
    enriched = enrich_issues(issues_df)
    assert len(enriched) == 3


# ---------------------------------------------------------------------------
# build_recommended_actions
# ---------------------------------------------------------------------------


def _make_enriched(rows: list[dict]) -> pd.DataFrame:
    """Helper — build a minimal enriched issues DataFrame."""
    return pd.DataFrame(rows)


def test_build_recommended_actions_empty_df_returns_empty() -> None:
    result = build_recommended_actions(pd.DataFrame())
    assert result == []


def test_build_recommended_actions_excludes_null_actions() -> None:
    df = _make_enriched(
        [
            {"Issue": "x", "severity": "warning", "recommended_action": None},
            {"Issue": "y", "severity": "critical", "recommended_action": None},
        ]
    )
    assert build_recommended_actions(df) == []


def test_build_recommended_actions_returns_action_and_severity_keys() -> None:
    df = _make_enriched(
        [{"Issue": "x", "severity": "warning", "recommended_action": "Check the field notes"}]
    )
    result = build_recommended_actions(df)
    assert len(result) == 1
    assert result[0]["action"] == "Check the field notes"
    assert result[0]["severity"] == "warning"


def test_build_recommended_actions_deduplicates_same_action_text() -> None:
    df = _make_enriched(
        [
            {"Issue": "a", "severity": "warning", "recommended_action": "Check heights"},
            {"Issue": "b", "severity": "warning", "recommended_action": "Check heights"},
            {"Issue": "c", "severity": "warning", "recommended_action": "Check heights"},
        ]
    )
    result = build_recommended_actions(df)
    assert len(result) == 1
    assert result[0]["action"] == "Check heights"


def test_build_recommended_actions_orders_critical_before_warning() -> None:
    df = _make_enriched(
        [
            {
                "Issue": "w",
                "severity": "warning",
                "recommended_action": "Review field notes",
            },
            {
                "Issue": "c",
                "severity": "critical",
                "recommended_action": "Fix coordinate error",
            },
        ]
    )
    result = build_recommended_actions(df)
    assert result[0]["severity"] == "critical"
    assert result[1]["severity"] == "warning"


def test_build_recommended_actions_observation_after_warning() -> None:
    df = _make_enriched(
        [
            {
                "Issue": "o",
                "severity": "observation",
                "recommended_action": "Note for record",
            },
            {
                "Issue": "w",
                "severity": "warning",
                "recommended_action": "Action needed",
            },
        ]
    )
    result = build_recommended_actions(df)
    severities = [r["severity"] for r in result]
    assert severities.index("warning") < severities.index("observation")


def test_build_recommended_actions_missing_columns_returns_empty() -> None:
    df = pd.DataFrame([{"Issue": "x", "severity": "warning"}])
    assert build_recommended_actions(df) == []


def test_build_recommended_actions_integration_with_enrich_issues() -> None:
    raw = pd.DataFrame(
        [
            {"Issue": "Missing required field: height", "Row": {}, "Severity": None},
            {"Issue": "Missing required field: height", "Row": {}, "Severity": None},
            {
                "Issue": "Angle structure with no stay evidence detected",
                "Row": {},
                "Severity": "WARN",
            },
        ]
    )
    enriched = enrich_issues(raw)
    result = build_recommended_actions(enriched)

    actions = [r["action"] for r in result]
    assert len(result) == 2
    assert any("height" in a.lower() for a in actions)
    assert any("stay" in a.lower() for a in actions)


# ---------------------------------------------------------------------------
# build_evidence_gates
# ---------------------------------------------------------------------------


def _make_completeness(
    lat_pct: float = 0,
    east_pct: float = 0,
    st_pct: float = 0,
    height_pct: float = 0,
    material_pct: float = 0,
    structural_count: int = 0,
    feature_codes: list | None = None,
) -> dict:
    return {
        "fields": {
            "lat": {"coverage_pct": lat_pct, "present": 0, "missing": 0},
            "easting": {"coverage_pct": east_pct, "present": 0, "missing": 0},
            "structure_type": {"coverage_pct": st_pct, "present": 0, "missing": 0},
            "height": {"coverage_pct": height_pct, "present": 0, "missing": 0},
            "material": {"coverage_pct": material_pct, "present": 0, "missing": 0},
        },
        "structural_count": structural_count,
        "feature_codes_found": feature_codes or [],
    }


def _make_issues_with_codes(codes: list[str]) -> pd.DataFrame:
    return pd.DataFrame([{"issue_code": c, "severity": "warning"} for c in codes])


def test_build_evidence_gates_returns_seven_gates() -> None:
    completeness = _make_completeness(lat_pct=100, structural_count=5)
    result = build_evidence_gates(completeness, pd.DataFrame())
    assert len(result) == 7
    labels = [g["label"] for g in result]
    assert "Position / Mapping" in labels
    assert "Overall Handoff Status" in labels


def test_build_evidence_gates_each_gate_has_required_keys() -> None:
    completeness = _make_completeness(lat_pct=100, structural_count=5)
    result = build_evidence_gates(completeness, pd.DataFrame())
    for gate in result:
        assert "label" in gate
        assert "status" in gate
        assert "explanation" in gate


def test_build_evidence_gates_position_missing_when_no_coords() -> None:
    completeness = _make_completeness()
    result = build_evidence_gates(completeness, pd.DataFrame())
    pos_gate = next(g for g in result if g["label"] == "Position / Mapping")
    assert pos_gate["status"] == "Missing"


def test_build_evidence_gates_position_strong_when_full_coverage_no_issues() -> None:
    completeness = _make_completeness(lat_pct=100, structural_count=5)
    result = build_evidence_gates(completeness, pd.DataFrame())
    pos_gate = next(g for g in result if g["label"] == "Position / Mapping")
    assert pos_gate["status"] == "Strong"


def test_build_evidence_gates_stay_na_when_no_angle_code() -> None:
    completeness = _make_completeness(lat_pct=100, structural_count=5, feature_codes=["Pol"])
    result = build_evidence_gates(completeness, pd.DataFrame())
    stay_gate = next(g for g in result if g["label"] == "Stay Evidence")
    assert stay_gate["status"] == "N/A"


def test_build_evidence_gates_stay_weak_when_angle_no_stay_issues() -> None:
    completeness = _make_completeness(
        lat_pct=100,
        structural_count=5,
        feature_codes=["Pol", "Angle"],
    )
    issues_df = _make_issues_with_codes(["ANGLE_NO_STAY", "ANGLE_NO_STAY"])
    result = build_evidence_gates(completeness, issues_df)
    stay_gate = next(g for g in result if g["label"] == "Stay Evidence")
    assert stay_gate["status"] == "Weak"
    assert "2" in stay_gate["explanation"]


def test_build_evidence_gates_structural_spec_missing_when_both_zero() -> None:
    completeness = _make_completeness(lat_pct=100, height_pct=0, material_pct=0, structural_count=5)
    result = build_evidence_gates(completeness, pd.DataFrame())
    spec_gate = next(g for g in result if g["label"] == "Structural Specification")
    assert spec_gate["status"] == "Missing"


def test_build_evidence_gates_overall_blocked_when_position_missing() -> None:
    completeness = _make_completeness()
    result = build_evidence_gates(completeness, pd.DataFrame())
    overall = next(g for g in result if g["label"] == "Overall Handoff Status")
    assert overall["status"] == "Blocked"


def test_build_evidence_gates_conductor_scope_partial_with_few_span_issues() -> None:
    completeness = _make_completeness(lat_pct=100, structural_count=10)
    issues_df = _make_issues_with_codes(["SPAN_VERY_SHORT", "SPAN_LONG"])
    result = build_evidence_gates(completeness, issues_df)
    cond_gate = next(g for g in result if g["label"] == "Conductor Scope")
    assert cond_gate["status"] == "Partial"
