"""Tests for the real iPad field pilot package built on Stage 4B validation."""

from __future__ import annotations

import csv
from pathlib import Path

import pytest

from app.structured_capture_schema import get_stage4_template_headers
from app.structured_capture_validators import (
    validate_stage4_headers,
    validate_stage4_import_preview,
)

REPO_ROOT = Path(__file__).resolve().parent.parent
FIXTURES = REPO_ROOT / "tests" / "fixtures" / "stage4"
PILOT_TEMPLATE = REPO_ROOT / "templates" / "structured_capture_ipad_pilot_template.csv"
RUNTIME_GUARD_FILES = (
    REPO_ROOT / "app" / "static" / "js" / "map-viewer.js",
    REPO_ROOT / "app" / "routes" / "api_intake.py",
    REPO_ROOT / "app" / "qa_engine.py",
)


def _load_csv(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        rows = [dict(row) for row in reader]
        return list(reader.fieldnames or []), rows


def test_pilot_template_headers_match_stage4b_schema() -> None:
    with PILOT_TEMPLATE.open(newline="", encoding="utf-8") as handle:
        headers = next(csv.reader(handle))

    schema_headers = get_stage4_template_headers()
    assert headers != schema_headers, "Pilot template should be field-ordered for iPad use"
    assert set(headers) == set(schema_headers)
    assert len(headers) == len(schema_headers)
    assert validate_stage4_headers(headers)["valid"]


def test_valid_pilot_sample_has_expected_mix_of_merge_ready_and_review_rows() -> None:
    headers, rows = _load_csv(FIXTURES / "pilot_valid_sample.csv")

    preview = validate_stage4_import_preview(rows, headers=headers)

    assert preview["total_rows"] == 7
    assert preview["valid_rows"] == 7
    assert preview["invalid_rows"] == 0
    assert preview["blocked_rows"] == 0
    assert preview["merge_ready_rows"] == 6
    assert preview["review_required_rows"] == 1
    assert preview["safe_to_merge"] is False
    assert preview["verdict"] == "review-required"

    no_stay = next(row for row in preview["row_results"] if row["pole_id"] == "P008-105")
    assert no_stay["normalised"]["stay_type"] == "none"

    legacy = next(row for row in preview["row_results"] if row["pole_id"] == "P008-107")
    assert legacy["row_status"] == "review-required"
    assert any("verification_required=yes" in warning for warning in legacy["warnings"])


def test_invalid_pilot_sample_fails_for_identity_date_enum_and_source() -> None:
    headers, rows = _load_csv(FIXTURES / "pilot_invalid_sample.csv")

    preview = validate_stage4_import_preview(rows, headers=headers)

    assert preview["total_rows"] == 4
    assert preview["blocked_rows"] == 1
    assert preview["invalid_rows"] == 4
    assert preview["merge_ready_rows"] == 0
    assert preview["safe_to_merge"] is False
    assert preview["verdict"] == "blocked"
    assert any("unsafe or missing row identity" in error for error in preview["errors"])
    assert any("capture_date" in error for error in preview["errors"])
    assert any("condition" in error and "none" in error for error in preview["errors"])
    assert any("source" in error and "spreadsheet" in error for error in preview["errors"])


def test_duplicate_identity_sample_blocks_only_the_duplicate_rows() -> None:
    headers, rows = _load_csv(FIXTURES / "pilot_duplicate_identity_sample.csv")

    preview = validate_stage4_import_preview(rows, headers=headers)

    assert preview["total_rows"] == 3
    assert preview["blocked_rows"] == 2
    assert preview["merge_ready_rows"] == 1
    assert preview["safe_to_merge"] is False
    assert any("Duplicate pole_id" in error for error in preview["errors"])


def test_iso_capture_date_rule_is_enforced_in_pilot_fixtures() -> None:
    _, rows = _load_csv(FIXTURES / "pilot_invalid_sample.csv")
    slash_date_row = rows[1]

    preview = validate_stage4_import_preview([slash_date_row], headers=list(slash_date_row))

    assert preview["invalid_rows"] == 1
    assert preview["blocked_rows"] == 0
    assert any("capture_date" in error for error in preview["errors"])


def test_explicit_none_examples_validate_only_in_allowed_fields() -> None:
    _, rows = _load_csv(FIXTURES / "pilot_valid_sample.csv")
    no_stay = next(row for row in rows if row["pole_id"] == "P008-105")

    preview = validate_stage4_import_preview([no_stay], headers=list(no_stay))

    assert preview["valid_rows"] == 1
    row = preview["row_results"][0]
    assert row["normalised"]["stay_type"] == "none"
    assert row["normalised"]["lean_direction"] == "none"
    assert row["normalised"]["lean_severity"] == "none"
    assert row["normalised"]["equipment_type"] == "none"


def test_pilot_validation_preview_is_runtime_isolated() -> None:
    before = {path: path.read_bytes() for path in RUNTIME_GUARD_FILES}
    headers, rows = _load_csv(FIXTURES / "pilot_valid_sample.csv")

    preview = validate_stage4_import_preview(rows, headers=headers)

    after = {path: path.read_bytes() for path in RUNTIME_GUARD_FILES}
    assert preview["total_rows"] == 7
    assert before == after


def test_real_pilot_csvs_validate_if_present() -> None:
    real_pilot_files = sorted(FIXTURES.glob("pilot_real_*.csv"))
    if not real_pilot_files:
        pytest.skip("No real pilot CSV recorded yet")

    for path in real_pilot_files:
        headers, rows = _load_csv(path)
        preview = validate_stage4_import_preview(rows, headers=headers)
        assert validate_stage4_headers(headers)["valid"], path.name
        assert preview["total_rows"] > 0, path.name
        assert preview["blocked_rows"] == 0, path.name
