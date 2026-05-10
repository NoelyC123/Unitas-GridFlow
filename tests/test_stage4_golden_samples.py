"""Golden sample tests for Stage 4 structured capture validation pipeline.

These tests run the validator against fixed CSV fixtures and assert exact
per-row outcomes. They serve as:

  1. Regression protection for schema changes
  2. Stage 4B acceptance gate evidence (criterion D3)
  3. Stage 4C readiness evidence (gate G3)

Golden sample fixtures live in tests/fixtures/stage4/.
See AI_CONTROL/54_STAGE4_GOLDEN_SAMPLE_PLAN.md for fixture design rationale.
"""

from __future__ import annotations

import csv
from pathlib import Path

import pytest

from app.structured_capture_validators import validate_stage4_row, validate_stage4_rows

FIXTURES = Path(__file__).parent / "fixtures" / "stage4"


def _load(filename: str) -> list[dict[str, str]]:
    path = FIXTURES / filename
    if not path.exists():
        pytest.skip(f"Fixture not found: {path}")
    with path.open(encoding="utf-8") as fh:
        return [dict(row) for row in csv.DictReader(fh)]


# ---------------------------------------------------------------------------
# Category 1 — Valid rows
# ---------------------------------------------------------------------------


class TestGoldenValid:
    """golden_valid.csv: all rows should validate cleanly."""

    def test_minimum_row_is_valid_but_not_merge_ready(self) -> None:
        rows = _load("golden_valid.csv")
        result = validate_stage4_row(rows[0])
        assert result["valid"], result["errors"]
        assert result["pole_id"] == "P008-001"
        assert result["merge_ready"] is False
        assert result["row_status"] == "valid but not merge-ready"

    def test_full_optional_row_is_merge_ready(self) -> None:
        rows = _load("golden_valid.csv")
        result = validate_stage4_row(rows[1])
        assert result["valid"], result["errors"]
        assert result["merge_ready"] is True
        assert result["normalised"]["voltage_carried"] == "11kV"
        assert result["normalised"]["stay_present"] == "yes"

    def test_voltage_lowercase_normalises_to_canonical_case(self) -> None:
        rows = _load("golden_valid.csv")
        result = validate_stage4_row(rows[3])
        assert result["valid"], result["errors"]
        assert result["normalised"]["voltage_carried"] == "11kV"

    def test_stay_type_none_is_preserved_not_treated_as_blank(self) -> None:
        rows = _load("golden_valid.csv")
        result = validate_stage4_row(rows[4])
        assert result["valid"], result["errors"]
        assert result["normalised"]["stay_type"] == "none"

    def test_lean_direction_none_is_preserved(self) -> None:
        rows = _load("golden_valid.csv")
        result = validate_stage4_row(rows[5])
        assert result["valid"], result["errors"]
        assert result["normalised"]["lean_direction"] == "none"

    def test_equipment_type_none_is_preserved(self) -> None:
        rows = _load("golden_valid.csv")
        result = validate_stage4_row(rows[6])
        assert result["valid"], result["errors"]
        assert result["normalised"]["equipment_type"] == "none"

    def test_metadata_only_row_is_valid_but_not_merge_ready(self) -> None:
        rows = _load("golden_valid.csv")
        result = validate_stage4_row(rows[8])
        assert result["valid"], result["errors"]
        assert result["merge_ready"] is False

    def test_all_valid_rows_have_no_errors(self) -> None:
        rows = _load("golden_valid.csv")
        for i, row in enumerate(rows):
            result = validate_stage4_row(row)
            assert result["valid"], (
                f"Row {i + 1} ({row.get('pole_id')!r}) unexpectedly invalid: {result['errors']}"
            )


# ---------------------------------------------------------------------------
# Category 2 — Invalid rows
# ---------------------------------------------------------------------------


class TestGoldenInvalid:
    """golden_invalid.csv: each row should fail with a specific error."""

    @pytest.mark.parametrize(
        "row_index,expected_error_fragment",
        [
            (0, "pole_id"),
            (1, "pole_id"),
            (2, "pole_id"),
            (3, "capture_source"),
            (4, "condition"),
            (5, "stay_type"),
            (6, "capture_date"),
            (7, "voltage_carried"),
            (8, "condition"),
        ],
    )
    def test_invalid_row_fails_with_expected_error(
        self, row_index: int, expected_error_fragment: str
    ) -> None:
        rows = _load("golden_invalid.csv")
        result = validate_stage4_row(rows[row_index])
        assert not result["valid"], f"Row {row_index + 1} should be invalid but passed"
        assert any(expected_error_fragment in err for err in result["errors"]), (
            f"Row {row_index + 1}: expected error containing "
            f"{expected_error_fragment!r}, got {result['errors']}"
        )

    def test_all_invalid_rows_have_merge_ready_false(self) -> None:
        rows = _load("golden_invalid.csv")
        for i, row in enumerate(rows):
            result = validate_stage4_row(row)
            assert not result["valid"], f"Row {i + 1} should be invalid"
            assert result["merge_ready"] is False, f"Row {i + 1} invalid but merge_ready=True"

    def test_blank_pole_id_variants_are_all_rejected(self) -> None:
        rows = _load("golden_invalid.csv")
        blank_id_rows = rows[:3]
        for row in blank_id_rows:
            result = validate_stage4_row(row)
            assert not result["valid"]
            assert result["pole_id"] is None or not result["merge_ready"]


# ---------------------------------------------------------------------------
# Category 3 — Duplicate detection
# ---------------------------------------------------------------------------


class TestGoldenDuplicates:
    """golden_duplicates.csv: duplicate pole_ids invalidate both rows."""

    def test_duplicate_pole_id_makes_both_rows_invalid(self) -> None:
        rows = _load("golden_duplicates.csv")
        result = validate_stage4_rows(rows)
        assert not result["valid"]
        assert any("Duplicate pole_id" in err for err in result["errors"])

    def test_duplicate_rows_are_not_merge_ready(self) -> None:
        rows = _load("golden_duplicates.csv")
        result = validate_stage4_rows(rows)
        dup_results = [r for r in result["row_results"] if r["pole_id"] == "P008-001"]
        assert len(dup_results) == 2
        for r in dup_results:
            assert r["merge_ready"] is False

    def test_unique_row_remains_merge_ready_despite_duplicates(self) -> None:
        rows = _load("golden_duplicates.csv")
        result = validate_stage4_rows(rows)
        unique = next(r for r in result["row_results"] if r["pole_id"] == "P008-002")
        assert unique["merge_ready"] is True

    def test_duplicate_file_has_correct_row_count(self) -> None:
        rows = _load("golden_duplicates.csv")
        result = validate_stage4_rows(rows)
        assert len(result["row_results"]) == 3


# ---------------------------------------------------------------------------
# Category 4 — Known-bad / normalisation
# ---------------------------------------------------------------------------


class TestGoldenKnownBad:
    """golden_known_bad.csv: common real-world mistakes and normalisation cases."""

    def test_trailing_space_pole_id_is_handled(self) -> None:
        rows = _load("golden_known_bad.csv")
        result = validate_stage4_row(rows[0])
        # Trailing space is stripped on normalisation — row should be valid
        assert result["valid"], result["errors"]

    def test_slash_date_format_is_rejected(self) -> None:
        rows = _load("golden_known_bad.csv")
        result = validate_stage4_row(rows[1])
        assert not result["valid"]
        assert any("capture_date" in err for err in result["errors"])

    def test_capitalised_condition_normalises_to_lowercase(self) -> None:
        rows = _load("golden_known_bad.csv")
        result = validate_stage4_row(rows[2])
        assert result["valid"], result["errors"]
        assert result["normalised"]["condition"] == "good"

    def test_question_mark_pole_id_is_rejected(self) -> None:
        rows = _load("golden_known_bad.csv")
        result = validate_stage4_row(rows[4])
        assert not result["valid"]

    def test_boolean_alias_y_normalises_to_yes(self) -> None:
        rows = _load("golden_known_bad.csv")
        result = validate_stage4_row(rows[5])
        assert result["valid"], result["errors"]
        assert result["normalised"]["stay_present"] == "yes"

    def test_boolean_alias_false_normalises_to_no(self) -> None:
        rows = _load("golden_known_bad.csv")
        result = validate_stage4_row(rows[6])
        assert result["valid"], result["errors"]
        assert result["normalised"]["equipment_present"] == "no"


# ---------------------------------------------------------------------------
# Category 5 — Legacy header aliases
# ---------------------------------------------------------------------------


class TestGoldenLegacyHeaders:
    """golden_legacy_headers.csv: alias column names resolve to canonical pole_id."""

    def test_point_column_resolves_to_pole_id(self) -> None:
        rows = _load("golden_legacy_headers.csv")
        for row in rows:
            result = validate_stage4_row(row)
            assert result["valid"], result["errors"]
            assert result["pole_id"] is not None
            assert result["pole_id"] is not None and result["pole_id"].startswith("P010-")

    def test_legacy_header_rows_have_pole_id_set(self) -> None:
        rows = _load("golden_legacy_headers.csv")
        result = validate_stage4_rows(rows)
        assert result["valid"], result["errors"]
        for row_result in result["row_results"]:
            assert row_result["pole_id"] is not None
