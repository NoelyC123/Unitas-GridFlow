"""Stage 4A safety boundary tests.

This file has two jobs:

1. **Stage 4A fixed-blocker tests** — document the three Stage 4A blockers
   (VLD-1, VLD-2, VLD-3) as explicit passing assertions now that the library
   fixes have landed.

2. **Library isolation tests** — pass on current master and must continue to
   pass after Stage 4A. They verify that Stage 4 library modules have no
   runtime dependencies (Flask, routes, QA engine, geometry, map renderer).

Blocker reference:  AI_CONTROL/43_STAGE4_READINESS_SPECIFICATION.md
Fix plan:           AI_CONTROL/44_STAGE4_BLOCKER_FIX_PLAN.md
Go/no-go:           AI_CONTROL/45_STAGE4_GO_NO_GO_CHECKLIST.md
"""

from __future__ import annotations

import ast
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
# sys is intentionally not imported here — inline imports keep this safety
# harness cheap to collect.

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _imports_in(source_path: Path) -> set[str]:
    """Return the set of top-level module names imported by a Python file."""
    tree = ast.parse(source_path.read_text(encoding="utf-8"))
    names: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                names.add(alias.name.split(".")[0])
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                names.add(node.module.split(".")[0])
    return names


# ---------------------------------------------------------------------------
# Library isolation — must pass on current master and after Stage 4A
# ---------------------------------------------------------------------------


STAGE4_LIBRARY_FILES = [
    REPO_ROOT / "app" / "structured_capture_schema.py",
    REPO_ROOT / "app" / "structured_capture_validators.py",
    REPO_ROOT / "scripts" / "generate_structured_capture_template.py",
]

FORBIDDEN_RUNTIME_IMPORTS = {
    "flask",
    "Flask",
    "pandas",
    "api_intake",
    "qa_engine",
    "controller_intake",
    "geometry_pipeline",
    "span_generator",
    "field_validators",
}


@pytest.mark.parametrize("library_file", STAGE4_LIBRARY_FILES, ids=lambda p: p.name)
def test_stage4_library_has_no_runtime_imports(library_file: Path) -> None:
    """Stage 4 library modules must not import any runtime app modules."""
    if not library_file.exists():
        pytest.skip(f"{library_file.name} does not exist yet")
    imports = _imports_in(library_file)
    leaks = imports & FORBIDDEN_RUNTIME_IMPORTS
    assert not leaks, (
        f"{library_file.name} imports forbidden runtime modules: {sorted(leaks)}. "
        "Stage 4 library code must remain decoupled from Flask, pandas, QA, and "
        "intake pipelines until Stage 4C."
    )


def test_structured_capture_schema_is_stdlib_only() -> None:
    """Schema module may only use standard library and typing imports."""
    schema_path = REPO_ROOT / "app" / "structured_capture_schema.py"
    imports = _imports_in(schema_path)
    # Only __future__ and typing are acceptable extras alongside stdlib
    third_party = imports - {
        "__future__",
        "typing",
        "collections",
        "dataclasses",
        "enum",
        "pathlib",
        "re",
        "json",
        "datetime",
        "functools",
        "itertools",
        "operator",
    }
    assert not third_party, (
        f"structured_capture_schema.py has non-stdlib imports: {sorted(third_party)}. "
        "The schema module must remain stdlib-only."
    )


def test_structured_capture_schema_current_status_constant() -> None:
    """All Stage 4 schema fields must carry current_status='stage4_future_capture'."""
    from app.structured_capture_schema import CURRENT_STATUS, get_stage4_fields

    assert CURRENT_STATUS == "stage4_future_capture"
    for field in get_stage4_fields():
        assert field["current_status"] == "stage4_future_capture", (
            f"Field {field['field_name']!r} has current_status={field['current_status']!r}; "
            "expected 'stage4_future_capture'."
        )


def test_structured_capture_schema_source_constant() -> None:
    """All Stage 4 schema fields must carry source='structured_capture'."""
    from app.structured_capture_schema import SOURCE, get_stage4_fields

    assert SOURCE == "structured_capture"
    for field in get_stage4_fields():
        assert field["source"] == "structured_capture", (
            f"Field {field['field_name']!r} has source={field['source']!r}; "
            "expected 'structured_capture'."
        )


# ---------------------------------------------------------------------------
# VLD-1: "none" blank-token handling
# ---------------------------------------------------------------------------
#
# Current bug: "none" is in _BLANK_TOKENS so is_blank("none") returns True.
# This causes validate_allowed_value("stay_type", "none") to normalise to
# None (unspecified) rather than preserving the valid enum value "none".
#
# Fields that declare "none" as a valid enum member:
#   stay_type:       ("down", "flying", "strut", "none", "unknown")
#   equipment_type:  (..., "none", "unknown")
#   lean_direction:  ("none", "north", ..., "unknown")
#   lean_severity:   ("none", "slight", ..., "unknown")
#
# Fields that do NOT allow "none":
#   condition:       ("good", "fair", "poor", "unsafe", "unknown")


def test_vld1_none_is_not_blank() -> None:
    """'none' must NOT be treated as a blank/unspecified value."""
    from app.structured_capture_validators import is_blank

    assert is_blank("none") is False, (
        "is_blank('none') returned True — 'none' is being erased as if unspecified. "
        "Remove 'none' from _BLANK_TOKENS."
    )


def test_vld1_stay_type_none_is_valid_enum() -> None:
    """stay_type='none' must validate as a valid enum member and normalise to 'none'."""
    from app.structured_capture_validators import validate_allowed_value

    result = validate_allowed_value("stay_type", "none")
    assert result["valid"], f"stay_type='none' was rejected: {result['errors']}"
    assert result["normalised"].get("stay_type") == "none", (
        f"stay_type='none' normalised to {result['normalised'].get('stay_type')!r} "
        "instead of 'none'."
    )


def test_vld1_equipment_type_none_is_valid_enum() -> None:
    """equipment_type='none' must validate as a valid enum member."""
    from app.structured_capture_validators import validate_allowed_value

    result = validate_allowed_value("equipment_type", "none")
    assert result["valid"], f"equipment_type='none' was rejected: {result['errors']}"
    assert result["normalised"].get("equipment_type") == "none"


def test_vld1_lean_direction_none_is_valid_enum() -> None:
    """lean_direction='none' must validate as a valid enum member."""
    from app.structured_capture_validators import validate_allowed_value

    result = validate_allowed_value("lean_direction", "none")
    assert result["valid"], f"lean_direction='none' was rejected: {result['errors']}"
    assert result["normalised"].get("lean_direction") == "none"


def test_vld1_lean_severity_none_is_valid_enum() -> None:
    """lean_severity='none' must validate as a valid enum member."""
    from app.structured_capture_validators import validate_allowed_value

    result = validate_allowed_value("lean_severity", "none")
    assert result["valid"], f"lean_severity='none' was rejected: {result['errors']}"
    assert result["normalised"].get("lean_severity") == "none"


def test_vld1_condition_does_not_allow_none_as_valid_enum() -> None:
    """'none' is not in condition's allowed_values — it must be rejected after VLD-1 fix.

    Currently FAILS because is_blank('none')=True causes the function to return
    valid=True (blank is OK). After VLD-1 fix, 'none' is no longer blank so the
    enum check runs and correctly rejects it for condition.

    This verifies the fix does not over-broaden 'none' acceptance.
    """
    from app.structured_capture_validators import validate_allowed_value

    result = validate_allowed_value("condition", "none")
    assert not result["valid"], (
        "condition='none' was accepted but 'none' is not in condition's allowed_values. "
        "After fixing VLD-1, 'none' must remain invalid for fields that don't declare it."
    )


def test_vld1_normalise_does_not_erase_none_enum_values() -> None:
    """normalise_stage4_row must preserve explicit 'none' enum values as the string 'none'.

    Currently FAILS because is_blank('none')=True causes normalisation to set
    None (unspecified) for stay_type='none'. After VLD-1 fix, the normalised
    row must contain 'none' (the valid enum value) not None.
    """
    from app.structured_capture_validators import normalise_stage4_row

    row = {
        "capture_source": "office_audit",
        "captured_by": "N. Collins",
        "capture_date": "2026-05-10",
        "stay_type": "none",
        "lean_direction": "none",
        "equipment_type": "none",
    }
    normalised = normalise_stage4_row(row)
    assert normalised.get("stay_type") == "none", (
        f"stay_type='none' normalised to {normalised.get('stay_type')!r}. "
        "Explicit 'none' (no stay fitted) must not be erased to None (unspecified)."
    )


# Blank tokens that must remain blank after VLD-1 fix — regression guard.
@pytest.mark.parametrize(
    "token",
    ["", "  ", "n/a", "N/A", "na", "NA", "null", "NULL", "tbc", "TBC", "?"],
)
def test_true_blank_tokens_remain_blank_after_vld1_fix(token: str) -> None:
    """Tokens that are genuinely unspecified must still register as blank."""
    from app.structured_capture_validators import is_blank

    assert is_blank(token), (
        f"is_blank({token!r}) returned False — this is a real blank token that "
        "must remain blank after removing 'none' from _BLANK_TOKENS."
    )


# ---------------------------------------------------------------------------
# VLD-1 extended: case variants and whitespace for "none"
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("variant", ["None", "NONE", " none ", "NONE "])
def test_vld1_none_case_variants_treated_as_enum_for_allowed_field(variant: str) -> None:
    """Mixed-case and whitespace variants of 'none' must resolve to the 'none' enum member."""
    from app.structured_capture_validators import validate_allowed_value

    result = validate_allowed_value("stay_type", variant)
    assert result["valid"], f"stay_type={variant!r} was rejected: {result['errors']}"
    assert result["normalised"].get("stay_type") == "none", (
        f"stay_type={variant!r} normalised to {result['normalised'].get('stay_type')!r}."
    )


# ---------------------------------------------------------------------------
# VLD-2: row identity / pole_id
# ---------------------------------------------------------------------------


def test_vld2_pole_id_field_exists_in_schema() -> None:
    """pole_id must be a registered Stage 4 field."""
    from app.structured_capture_schema import get_stage4_field_definition

    definition = get_stage4_field_definition("pole_id")
    assert definition is not None, (
        "get_stage4_field_definition('pole_id') returned None. "
        "Add pole_id to the Stage 4 schema as a required identity field."
    )
    assert definition["field_name"] == "pole_id"


def test_vld2_pole_id_in_template_headers() -> None:
    """pole_id must appear in the CSV template headers."""
    from app.structured_capture_schema import get_stage4_template_headers

    headers = get_stage4_template_headers()
    assert "pole_id" in headers, (
        f"pole_id not in template headers. Current headers start with: {headers[:5]}"
    )


def test_vld2_missing_pole_id_fails_required_field_check() -> None:
    """A row with all metadata but no pole_id must fail required-field validation."""
    from app.structured_capture_validators import validate_required_fields

    row_without_pole_id = {
        "capture_source": "office_audit",
        "captured_by": "N. Collins",
        "capture_date": "2026-05-10",
        "condition": "good",
    }
    result = validate_required_fields(row_without_pole_id)
    assert not result["valid"], (
        "validate_required_fields passed a row with no pole_id. "
        "pole_id must be required for evidence-bearing rows."
    )
    assert any("pole_id" in err for err in result["errors"]), (
        f"No error mentions pole_id. Errors: {result['errors']}"
    )


@pytest.mark.parametrize(
    "bad_id",
    ["", "  ", "n/a", "null", "unknown", "?", "UNKNOWN"],
)
def test_vld2_blank_or_unknown_pole_id_is_rejected(bad_id: str) -> None:
    """Blank or 'unknown' pole_id must not pass as a valid value.

    This verifies blank/placeholder pole_id values are rejected for identity
    validation rather than accepted as merge keys.
    """
    from app.structured_capture_validators import validate_allowed_value

    result = validate_allowed_value("pole_id", bad_id)
    assert not result["valid"], (
        f"pole_id={bad_id!r} was accepted. "
        "Blank and unknown pole_id values cannot serve as merge keys."
    )
    assert any("unsafe or missing row identity" in err for err in result["errors"])
    assert result["field_results"], "pole_id identity failures must include field-level evidence"
    field_result = result["field_results"][0]
    assert field_result["field_name"] == "pole_id"
    assert field_result["reason"] == "unsafe or missing row identity"
    assert (
        field_result["recommendation"] == "provide stable pole_id before merge/runtime integration"
    )


# ---------------------------------------------------------------------------
# VLD-3: structured_capture source registration
# ---------------------------------------------------------------------------


def test_vld3_structured_capture_registered_as_source() -> None:
    """field_reference must recognise 'structured_capture' as a valid source label."""
    from app.field_reference import (
        FIELD_SOURCE_STRUCTURED_CAPTURE,
        STRUCTURED_CAPTURE_FIELDS,
        VALID_FIELD_SOURCES,
        is_valid_field_source,
    )

    assert FIELD_SOURCE_STRUCTURED_CAPTURE == "structured_capture"
    assert "structured_capture" in VALID_FIELD_SOURCES
    assert is_valid_field_source("structured_capture")
    assert STRUCTURED_CAPTURE_FIELDS == frozenset()


def test_vld3_existing_source_labels_unchanged() -> None:
    """Existing source labels (survey, derived, trimble_attr) must not change.

    This test passes NOW and must continue to pass after VLD-3 is fixed.
    Adding 'structured_capture' must not rename or remove existing source labels.
    """
    from app.field_reference import FIELD_DEFINITIONS

    all_sources = {defn.get("source") for defn in FIELD_DEFINITIONS.values()}
    for expected_source in ("survey", "derived", "trimble_attr"):
        assert expected_source in all_sources, (
            f"Source label {expected_source!r} has disappeared from field_reference. "
            "Fixing VLD-3 must not remove existing source labels."
        )


# ---------------------------------------------------------------------------
# Identity safety — deterministic error expectations (pass now, stay passing)
# ---------------------------------------------------------------------------


def test_non_dict_row_is_rejected() -> None:
    """Row validators must reject non-dict input with a clear error."""
    from app.structured_capture_validators import validate_stage4_row

    for bad_input in [None, "a string", 42, ["list"]]:
        result = validate_stage4_row(bad_input)  # type: ignore[arg-type]
        assert not result["valid"], f"validate_stage4_row({bad_input!r}) returned valid=True"
        assert result["errors"], f"No error reported for non-dict row: {bad_input!r}"


def test_empty_row_is_partial_not_valid() -> None:
    """An empty dict is not a valid Stage 4 row (required fields are missing)."""
    from app.structured_capture_validators import validate_stage4_row

    result = validate_stage4_row({})
    assert not result["valid"]
    assert len(result["errors"]) >= 3


def test_required_metadata_blank_tokens_fail() -> None:
    """Required metadata fields must reject blank tokens as values."""
    from app.structured_capture_validators import validate_required_fields

    for blank in ("", "n/a", "null", "tbc", "?"):
        row = {
            "capture_source": blank,
            "captured_by": blank,
            "capture_date": blank,
        }
        result = validate_required_fields(row)
        assert not result["valid"], (
            f"validate_required_fields passed with all required fields set to {blank!r}."
        )
