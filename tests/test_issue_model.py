from __future__ import annotations

import pandas as pd

from app.issue_model import classify_issue, enrich_issues

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
