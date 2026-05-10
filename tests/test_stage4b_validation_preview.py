"""Stage 4B structured-capture validation and import-preview tests."""

from __future__ import annotations

import csv
from pathlib import Path

from app.structured_capture_schema import get_stage4_template_headers
from app.structured_capture_validators import (
    validate_stage4_headers,
    validate_stage4_import_preview,
    validate_stage4_row,
)

BASE_ROW = {
    "pole_id": "P008-001",
    "capture_source": "office_audit",
    "captured_by": "N. Collins",
    "capture_date": "2026-05-09",
}


def _valid_row(**overrides: object) -> dict[str, object]:
    row: dict[str, object] = {
        **BASE_ROW,
        "structure_type": "EXpole",
        "asset_intent": "existing",
        "material": "wood",
        "measured_height_m": "9.2m",
        "height_source": "measured_tape",
        "condition": "good",
        "stay_required": "no",
        "stay_present": "no",
        "equipment_type": "none",
        "source": "structured_capture",
        "evidence_status": "measured",
    }
    row.update(overrides)
    return row


def test_clean_valid_row_is_merge_ready_in_preview() -> None:
    preview = validate_stage4_import_preview([_valid_row()])

    assert preview["verdict"] == "merge-ready"
    assert preview["safe_to_merge"] is True
    assert preview["total_rows"] == 1
    assert preview["valid_rows"] == 1
    assert preview["merge_ready_rows"] == 1
    assert preview["blocked_rows"] == 0
    assert preview["invalid_rows"] == 0

    height_field = next(
        field
        for field in preview["per_field_validation_results"]
        if field["field_name"] == "measured_height_m"
    )
    assert height_field["raw_value"] == "9.2m"
    assert height_field["normalised_value"] == 9.2
    assert height_field["severity"] == "PASS"
    assert height_field["source"] == "structured_capture"


def test_missing_pole_id_blocks_import_preview() -> None:
    row = _valid_row()
    row.pop("pole_id")

    preview = validate_stage4_import_preview([row])

    assert preview["verdict"] == "blocked"
    assert preview["safe_to_merge"] is False
    assert preview["blocked_rows"] == 1
    assert any("pole_id" in error for error in preview["errors"])
    pole_result = next(
        field
        for field in preview["per_field_validation_results"]
        if field["field_name"] == "pole_id"
    )
    assert pole_result["severity"] == "BLOCKER"
    assert pole_result["reason"] == "unsafe or missing row identity"
    assert pole_result["recommendation"] == (
        "provide stable pole_id before merge/runtime integration"
    )


def test_unsafe_pole_id_placeholders_block_import_preview() -> None:
    for unsafe in ("", "   ", "n/a", "null", "unknown", "UNKNOWN", "?"):
        preview = validate_stage4_import_preview([_valid_row(pole_id=unsafe)])
        assert preview["verdict"] == "blocked", unsafe
        assert preview["blocked_rows"] == 1, unsafe
        assert any("unsafe or missing row identity" in error for error in preview["errors"])


def test_duplicate_pole_id_blocks_both_rows() -> None:
    preview = validate_stage4_import_preview([_valid_row(), _valid_row(capture_date="2026-05-10")])

    assert preview["verdict"] == "blocked"
    assert preview["safe_to_merge"] is False
    assert preview["blocked_rows"] == 2
    assert any("Duplicate pole_id" in error for error in preview["errors"])
    assert all(row["row_status"] == "blocked" for row in preview["row_results"])


def test_valid_none_values_are_preserved_for_explicit_none_fields() -> None:
    row = _valid_row(
        stay_present="no",
        stay_type="none",
        equipment_type="none",
        lean_direction="none",
        lean_severity="none",
    )
    result = validate_stage4_row(row)

    assert result["valid"], result["errors"]
    assert result["normalised"]["stay_type"] == "none"
    assert result["normalised"]["equipment_type"] == "none"
    assert result["normalised"]["lean_direction"] == "none"
    assert result["normalised"]["lean_severity"] == "none"


def test_invalid_none_values_are_rejected_outside_allowed_fields() -> None:
    preview = validate_stage4_import_preview([_valid_row(condition="none")])

    assert preview["verdict"] == "invalid"
    assert preview["invalid_rows"] == 1
    assert any("condition" in error and "none" in error for error in preview["errors"])


def test_invalid_height_blocks_row() -> None:
    preview = validate_stage4_import_preview([_valid_row(measured_height_m="99")])

    assert preview["verdict"] == "blocked"
    assert preview["blocked_rows"] == 1
    height_result = next(
        field
        for field in preview["per_field_validation_results"]
        if field["field_name"] == "measured_height_m"
    )
    assert height_result["severity"] == "BLOCKER"
    assert height_result["reason"] == "invalid height"


def test_missing_required_metadata_invalidates_preview() -> None:
    row = _valid_row()
    row.pop("captured_by")

    preview = validate_stage4_import_preview([row])

    assert preview["safe_to_merge"] is False
    assert preview["invalid_rows"] == 1
    assert any("Required field missing: captured_by" in error for error in preview["errors"])


def test_unknown_source_is_invalid_and_structured_capture_source_is_valid() -> None:
    invalid = validate_stage4_import_preview([_valid_row(source="spreadsheet")])
    assert invalid["safe_to_merge"] is False
    assert any("source" in error and "spreadsheet" in error for error in invalid["errors"])

    valid = validate_stage4_import_preview([_valid_row(source="structured_capture")])
    assert valid["safe_to_merge"] is True
    source_field = next(
        field for field in valid["per_field_validation_results"] if field["field_name"] == "source"
    )
    assert source_field["normalised_value"] == "structured_capture"


def test_contradictory_evidence_requires_review_but_is_not_runtime_merged() -> None:
    preview = validate_stage4_import_preview([_valid_row(stay_present="no", stay_type="down")])

    assert preview["verdict"] == "review-required"
    assert preview["safe_to_merge"] is False
    assert preview["review_required_rows"] == 1
    assert any("contradictory evidence" in warning for warning in preview["warnings"])


def test_header_validation_tracks_missing_unknown_and_duplicate_columns() -> None:
    headers = ["pole_id", "pole_id", "capture_source", "capture_date", "extra_column"]

    result = validate_stage4_headers(headers)

    assert not result["valid"]
    assert "captured_by" in result["missing_required_columns"]
    assert "pole_id" in result["duplicate_columns"]
    assert "extra_column" in result["unknown_columns"]


def test_template_headers_match_schema() -> None:
    template_path = Path("templates/structured_capture_template.csv")
    with template_path.open(newline="", encoding="utf-8") as handle:
        headers = next(csv.reader(handle))

    assert headers == get_stage4_template_headers()
    assert validate_stage4_headers(headers)["valid"]
    for required in ("pole_id", "capture_source", "captured_by", "capture_date"):
        assert required in headers
