"""Pure validation helpers for Stage 4 structured-capture rows.

This module is deliberately decoupled from Flask, pandas, and any I/O. Each
helper takes plain dicts/values and returns plain results. It does not
mutate inputs and does not raise on validation failure — validation
problems are reported in the structured result dict described below.

Result shape returned by row-level validators:
    {
        "valid":      bool,                   # overall pass/fail
        "errors":     list[str],              # blocking problems
        "warnings":   list[str],              # non-blocking observations
        "normalised": dict[str, Any],         # the row after light normalisation
    }
"""

from __future__ import annotations

from typing import Any

from app.structured_capture_schema import (
    PRESENCE_VALUES,
    get_stage4_field_definition,
    get_stage4_fields,
    get_stage4_required_fields,
    is_stage4_field,
)

# Tokens treated as "blank" / unspecified when normalising user input.
_BLANK_TOKENS: frozenset[str] = frozenset({"", "n/a", "na", "none", "null", "tbc", "?"})

_TRUE_TOKENS: frozenset[str] = frozenset({"yes", "y", "true", "1"})
_FALSE_TOKENS: frozenset[str] = frozenset({"no", "n", "false", "0"})
_UNKNOWN_TOKENS: frozenset[str] = frozenset({"unknown", "?", "tbc", "tbd"})


# ---------------------------------------------------------------------------
# Primitive helpers
# ---------------------------------------------------------------------------


def is_blank(value: Any) -> bool:
    """Return True if ``value`` should be treated as unspecified."""

    if value is None:
        return True
    if isinstance(value, str):
        return value.strip().lower() in _BLANK_TOKENS
    return False


def normalise_bool(value: Any) -> str:
    """Coerce a user-supplied boolean-ish value to ``yes`` / ``no`` / ``unknown``."""

    if is_blank(value):
        return "unknown"
    text = str(value).strip().lower()
    if text in _TRUE_TOKENS:
        return "yes"
    if text in _FALSE_TOKENS:
        return "no"
    if text in _UNKNOWN_TOKENS:
        return "unknown"
    return "unknown"


def _normalise_enum_value(value: Any, allowed_values: tuple[str, ...]) -> str | None:
    """Return the canonical (case-preserving) member matching ``value``, or None."""

    if is_blank(value):
        return None
    needle = str(value).strip().lower()
    for allowed in allowed_values:
        if allowed.lower() == needle:
            return allowed
    return None


def _empty_result(normalised: dict[str, Any] | None = None) -> dict[str, Any]:
    return {
        "valid": True,
        "errors": [],
        "warnings": [],
        "normalised": dict(normalised or {}),
    }


# ---------------------------------------------------------------------------
# Per-field / per-row validators
# ---------------------------------------------------------------------------


def validate_allowed_value(field_name: str, value: Any) -> dict[str, Any]:
    """Validate that ``value`` matches the allowed_values for ``field_name``.

    Unknown fields are treated as a blocking error so typos don't silently
    pass. Blank values are accepted unless the field is required (handled
    elsewhere).
    """

    result = _empty_result()
    definition = get_stage4_field_definition(field_name)
    if definition is None:
        result["valid"] = False
        result["errors"].append(f"Unknown Stage 4 field: {field_name!r}")
        return result

    canonical = definition["field_name"]
    allowed = definition.get("allowed_values")

    if is_blank(value):
        # blank handled by required-field check; otherwise valid
        result["normalised"][canonical] = None
        return result

    if definition["type"] == "boolean_enum":
        normalised = normalise_bool(value)
        if normalised not in PRESENCE_VALUES:
            result["valid"] = False
            result["errors"].append(f"{canonical}: {value!r} is not one of {list(PRESENCE_VALUES)}")
            return result
        result["normalised"][canonical] = normalised
        return result

    if allowed is None:
        # free-text fields: accept the trimmed string
        result["normalised"][canonical] = str(value).strip()
        return result

    canonical_member = _normalise_enum_value(value, allowed)
    if canonical_member is None:
        result["valid"] = False
        result["errors"].append(f"{canonical}: {value!r} is not one of {list(allowed)}")
        return result
    result["normalised"][canonical] = canonical_member
    return result


def validate_required_fields(row: dict[str, Any]) -> dict[str, Any]:
    """Check every required Stage 4 field is present and non-blank in ``row``."""

    result = _empty_result()
    for field_name in get_stage4_required_fields():
        if is_blank(row.get(field_name)):
            result["valid"] = False
            result["errors"].append(f"Required field missing: {field_name}")
    return result


def normalise_stage4_row(row: dict[str, Any]) -> dict[str, Any]:
    """Return a copy of ``row`` with recognised Stage 4 values normalised.

    Unknown keys are preserved verbatim so the caller can decide whether to
    drop them. Blank/None values map to None.
    """

    normalised: dict[str, Any] = {}
    for key, value in row.items():
        if not is_stage4_field(key):
            normalised[key] = value
            continue
        definition = get_stage4_field_definition(key)
        if definition is None:
            normalised[key] = value
            continue
        canonical = definition["field_name"]

        if is_blank(value):
            normalised[canonical] = None
            continue

        if definition["type"] == "boolean_enum":
            normalised[canonical] = normalise_bool(value)
            continue

        allowed = definition.get("allowed_values")
        if allowed is None:
            normalised[canonical] = str(value).strip()
            continue

        canonical_member = _normalise_enum_value(value, allowed)
        # Keep the original value if it doesn't match — validation will flag it.
        normalised[canonical] = canonical_member if canonical_member else str(value).strip()
    return normalised


def validate_stage4_row(row: dict[str, Any]) -> dict[str, Any]:
    """Run required-field + per-field validation against a single row."""

    result = _empty_result()

    if not isinstance(row, dict):
        result["valid"] = False
        result["errors"].append("Row must be a dict")
        return result

    required_check = validate_required_fields(row)
    if not required_check["valid"]:
        result["valid"] = False
        result["errors"].extend(required_check["errors"])

    normalised: dict[str, Any] = {}
    unknown_keys: list[str] = []

    for key, value in row.items():
        if not is_stage4_field(key):
            unknown_keys.append(key)
            continue
        per_field = validate_allowed_value(key, value)
        if not per_field["valid"]:
            result["valid"] = False
            result["errors"].extend(per_field["errors"])
        normalised.update(per_field["normalised"])

    if unknown_keys:
        result["warnings"].append(
            "Unknown Stage 4 columns ignored: " + ", ".join(sorted(unknown_keys))
        )

    result["normalised"] = normalised
    return result


def validate_stage4_rows(rows: list[dict[str, Any]]) -> dict[str, Any]:
    """Validate a list of rows. Returns aggregate plus per-row results."""

    aggregate: dict[str, Any] = {
        "valid": True,
        "errors": [],
        "warnings": [],
        "row_results": [],
    }
    if not isinstance(rows, list):
        aggregate["valid"] = False
        aggregate["errors"].append("Rows payload must be a list")
        return aggregate

    for index, row in enumerate(rows):
        row_result = validate_stage4_row(row if isinstance(row, dict) else {})
        if not isinstance(row, dict):
            row_result["valid"] = False
            row_result["errors"].append(f"Row {index} is not a dict")
        if not row_result["valid"]:
            aggregate["valid"] = False
        aggregate["row_results"].append({"index": index, **row_result})

    return aggregate


# ---------------------------------------------------------------------------
# Completeness classification
# ---------------------------------------------------------------------------


def classify_stage4_completeness(row: dict[str, Any]) -> str:
    """Classify how complete a Stage 4 row is.

    Returns one of:
        ``"empty"``    — no Stage 4 values at all.
        ``"partial"``  — some values present but required fields missing.
        ``"minimum"``  — required fields filled, fewer than half optional.
        ``"complete"`` — required fields filled and at least half optional fields filled.

    Required = the capture metadata fields the schema marks ``required``.
    Optional = every other Stage 4 field.
    """

    if not isinstance(row, dict):
        return "empty"

    required = get_stage4_required_fields()
    optional = [d["field_name"] for d in get_stage4_fields() if d["field_name"] not in required]

    filled_required = sum(1 for name in required if not is_blank(row.get(name)))
    filled_optional = sum(1 for name in optional if not is_blank(row.get(name)))

    if filled_required == 0 and filled_optional == 0:
        return "empty"
    if filled_required < len(required):
        return "partial"
    # required fully filled
    if optional and filled_optional >= max(1, (len(optional) + 1) // 2):
        return "complete"
    return "minimum"


__all__ = [
    "is_blank",
    "normalise_bool",
    "validate_allowed_value",
    "validate_required_fields",
    "validate_stage4_row",
    "validate_stage4_rows",
    "classify_stage4_completeness",
    "normalise_stage4_row",
]
