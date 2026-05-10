"""Pure validation helpers for Stage 4 structured-capture rows.

This module is deliberately decoupled from Flask, pandas, and any I/O. Each
helper takes plain dicts/values and returns plain results. It does not
mutate inputs and does not raise on validation failure — validation
problems are reported in the structured result dict described below.

Result shape returned by row-level validators:
    {
        "valid":      bool,                   # overall pass/fail
        "invalid":    bool,                   # inverse of valid, for report consumers
        "errors":     list[str],              # blocking problems
        "warnings":   list[str],              # non-blocking observations
        "normalised": dict[str, Any],         # the row after light normalisation
        "field_results": list[dict[str, Any]], # per-field validation/provenance results
        "row_id":     str | None,             # deterministic row identity when available
        "pole_id":    str | None,             # primary merge identity when available
        "source":     "structured_capture",
        "merge_ready": bool,                  # valid and has pole_id
    }
"""

from __future__ import annotations

from typing import Any

from app.structured_capture_schema import (
    PRESENCE_VALUES,
    SOURCE,
    get_stage4_field_definition,
    get_stage4_fields,
    get_stage4_required_fields,
    is_stage4_field,
)

# Tokens treated as "blank" / unspecified when normalising user input.
_BLANK_TOKENS: frozenset[str] = frozenset({"", "n/a", "na", "null", "tbc", "?"})
_UNSAFE_IDENTITY_TOKENS: frozenset[str] = _BLANK_TOKENS | frozenset({"unknown", "none", "missing"})

# In Stage 4, "none" is an explicit survey/design answer for these fields.
_EXPLICIT_NONE_FIELDS: frozenset[str] = frozenset(
    {"stay_type", "equipment_type", "lean_direction", "lean_severity"}
)

_TRUE_TOKENS: frozenset[str] = frozenset({"yes", "y", "true", "1"})
_FALSE_TOKENS: frozenset[str] = frozenset({"no", "n", "false", "0"})
_UNKNOWN_TOKENS: frozenset[str] = frozenset({"unknown", "?", "tbc", "tbd"})


# ---------------------------------------------------------------------------
# Primitive helpers
# ---------------------------------------------------------------------------


def is_blank(value: Any) -> bool:
    """Return True if ``value`` should be treated as unspecified.

    The explicit value ``"none"`` is not globally blank. Field-level enum
    validation decides whether it is a valid value or a rejected token.
    """

    if value is None:
        return True
    if isinstance(value, str):
        return value.strip().lower() in _BLANK_TOKENS
    return False


def field_allows_explicit_none(field_name: str) -> bool:
    """Return True when ``"none"`` is an allowed explicit Stage 4 value."""

    definition = get_stage4_field_definition(field_name)
    canonical = definition["field_name"] if definition else field_name
    return canonical in _EXPLICIT_NONE_FIELDS


def is_blank_for_field(field_name: str, value: Any) -> bool:
    """Field-aware blank check for Stage 4 input values."""

    if isinstance(value, str) and value.strip().lower() == "none":
        # "none" is intentionally not a blank token. Enum validation decides
        # whether the specific field accepts explicit none.
        if field_allows_explicit_none(field_name):
            return False
        return False
    return is_blank(value)


def _is_known_bool_token(value: Any) -> bool:
    if is_blank(value):
        return True
    text = str(value).strip().lower()
    return text in _TRUE_TOKENS or text in _FALSE_TOKENS or text in _UNKNOWN_TOKENS


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


def _identity_value(row: dict[str, Any], field_name: str) -> Any:
    """Return a canonical identity field value, resolving aliases."""

    for key, value in row.items():
        definition = get_stage4_field_definition(key)
        if definition and definition["field_name"] == field_name:
            return value
    return None


def _clean_identity(value: Any) -> str | None:
    if is_blank(value):
        return None
    text = str(value).strip()
    if text.lower() in _UNSAFE_IDENTITY_TOKENS:
        return None
    return text or None


def _unsafe_identity_reason(value: Any) -> str | None:
    """Return a blocking reason when a value cannot be used as row identity."""

    if value is None:
        return "unsafe or missing row identity"
    text = str(value).strip()
    if not text or text.lower() in _UNSAFE_IDENTITY_TOKENS:
        return "unsafe or missing row identity"
    return None


def extract_stage4_row_identity(
    row: dict[str, Any],
    *,
    allow_fallback: bool = False,
    fallback_fields: tuple[str, ...] = (),
) -> dict[str, Any]:
    """Extract deterministic row identity for Stage 4 rows.

    ``pole_id`` is the only merge-ready identity in Stage 4A. Explicit fallback
    fields can create an audit ``row_id`` when requested, but they do not make a
    row merge-ready without ``pole_id``.
    """

    result: dict[str, Any] = {
        "valid": False,
        "errors": [],
        "warnings": [],
        "row_id": None,
        "pole_id": None,
        "project_id": None,
        "file_id": None,
        "source": SOURCE,
        "merge_ready": False,
    }

    if not isinstance(row, dict):
        result["errors"].append("Row must be a dict")
        return result

    pole_id = _clean_identity(_identity_value(row, "pole_id"))
    project_id = _clean_identity(_identity_value(row, "project_id"))
    file_id = _clean_identity(_identity_value(row, "file_id"))
    result["pole_id"] = pole_id
    result["project_id"] = project_id
    result["file_id"] = file_id

    if pole_id:
        row_id_parts = [part for part in (project_id, file_id, pole_id) if part]
        result["row_id"] = "/".join(row_id_parts)
        result["valid"] = True
        result["merge_ready"] = True
        return result

    if allow_fallback and fallback_fields:
        fallback_values = []
        for field_name in fallback_fields:
            fallback = _clean_identity(_identity_value(row, field_name))
            if fallback is None:
                break
            fallback_values.append(f"{field_name}={fallback}")
        if len(fallback_values) == len(fallback_fields):
            result["row_id"] = "fallback:" + "|".join(fallback_values)
            result["warnings"].append(
                "Fallback identity is audit-only in Stage 4A; "
                "pole_id is required for merge readiness"
            )

    result["errors"].append("Structured capture row is missing required pole_id identity")
    return result


def _field_result(
    *,
    field_name: str,
    value: Any,
    valid: bool,
    errors: list[str] | None = None,
    warnings: list[str] | None = None,
    row_id: str | None = None,
    pole_id: str | None = None,
    reason: str | None = None,
    recommendation: str | None = None,
) -> dict[str, Any]:
    return {
        "valid": valid,
        "invalid": not valid,
        "warnings": list(warnings or []),
        "errors": list(errors or []),
        "field_name": field_name,
        "value": value,
        "source": SOURCE,
        "row_id": row_id,
        "pole_id": pole_id,
        "reason": reason,
        "recommendation": recommendation,
    }


def _empty_result(normalised: dict[str, Any] | None = None) -> dict[str, Any]:
    return {
        "valid": True,
        "invalid": False,
        "errors": [],
        "warnings": [],
        "normalised": dict(normalised or {}),
        "field_results": [],
        "row_id": None,
        "pole_id": None,
        "source": SOURCE,
        "merge_ready": False,
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
        result["invalid"] = True
        result["errors"].append(f"Unknown Stage 4 field: {field_name!r}")
        return result

    canonical = definition["field_name"]
    allowed = definition.get("allowed_values")

    if canonical == "pole_id":
        reason = _unsafe_identity_reason(value)
        if reason:
            error = "pole_id: unsafe or missing row identity"
            result["valid"] = False
            result["invalid"] = True
            result["errors"].append(error)
            result["normalised"][canonical] = None
            result["field_results"].append(
                _field_result(
                    field_name=canonical,
                    value=None,
                    valid=False,
                    errors=[error],
                    reason=reason,
                    recommendation="provide stable pole_id before merge/runtime integration",
                )
            )
            return result
        result["normalised"][canonical] = str(value).strip()
        return result

    if is_blank_for_field(canonical, value):
        # blank handled by required-field check; otherwise valid
        result["normalised"][canonical] = None
        return result

    if definition["type"] == "boolean_enum":
        if not _is_known_bool_token(value):
            result["valid"] = False
            result["invalid"] = True
            result["errors"].append(f"{canonical}: {value!r} is not one of {list(PRESENCE_VALUES)}")
            return result
        normalised = normalise_bool(value)
        result["normalised"][canonical] = normalised
        return result

    if allowed is None:
        # free-text fields: accept the trimmed string
        result["normalised"][canonical] = str(value).strip()
        return result

    canonical_member = _normalise_enum_value(value, allowed)
    if canonical_member is None:
        result["valid"] = False
        result["invalid"] = True
        result["errors"].append(f"{canonical}: {value!r} is not one of {list(allowed)}")
        return result
    result["normalised"][canonical] = canonical_member
    return result


def validate_required_fields(row: dict[str, Any]) -> dict[str, Any]:
    """Check every required Stage 4 field is present and non-blank in ``row``."""

    result = _empty_result()
    normalised_row = normalise_stage4_row(row) if isinstance(row, dict) else {}
    for field_name in get_stage4_required_fields():
        if is_blank_for_field(field_name, normalised_row.get(field_name)):
            result["valid"] = False
            result["invalid"] = True
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

        if is_blank_for_field(canonical, value):
            normalised[canonical] = None
            continue

        if definition["type"] == "boolean_enum":
            normalised[canonical] = (
                normalise_bool(value) if _is_known_bool_token(value) else str(value).strip()
            )
            continue

        if canonical == "pole_id" and _unsafe_identity_reason(value):
            normalised[canonical] = None
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
        result["invalid"] = True
        result["errors"].append("Row must be a dict")
        return result

    identity = extract_stage4_row_identity(row)
    result["row_id"] = identity["row_id"]
    result["pole_id"] = identity["pole_id"]
    result["merge_ready"] = identity["merge_ready"]

    required_check = validate_required_fields(row)
    if not required_check["valid"]:
        result["valid"] = False
        result["invalid"] = True
        result["errors"].extend(required_check["errors"])
        normalised_for_required = normalise_stage4_row(row)
        for field_name in get_stage4_required_fields():
            if is_blank_for_field(field_name, normalised_for_required.get(field_name)):
                reason = (
                    "unsafe or missing row identity"
                    if field_name == "pole_id"
                    else "required identity or metadata is missing"
                )
                recommendation = (
                    "provide stable pole_id before merge/runtime integration"
                    if field_name == "pole_id"
                    else "Populate the required field before merge readiness checks"
                )
                result["field_results"].append(
                    _field_result(
                        field_name=field_name,
                        value=None,
                        valid=False,
                        errors=[f"Required field missing: {field_name}"],
                        row_id=result["row_id"],
                        pole_id=result["pole_id"],
                        reason=reason,
                        recommendation=recommendation,
                    )
                )

    normalised: dict[str, Any] = {}
    unknown_keys: list[str] = []

    for key, value in row.items():
        if not is_stage4_field(key):
            unknown_keys.append(key)
            continue
        per_field = validate_allowed_value(key, value)
        if not per_field["valid"]:
            result["valid"] = False
            result["invalid"] = True
            result["errors"].extend(per_field["errors"])
        normalised.update(per_field["normalised"])
        definition = get_stage4_field_definition(key)
        if definition is None:
            continue
        canonical = definition["field_name"]
        result["field_results"].append(
            _field_result(
                field_name=canonical,
                value=per_field["normalised"].get(canonical),
                valid=per_field["valid"],
                errors=per_field["errors"],
                warnings=per_field["warnings"],
                row_id=result["row_id"],
                pole_id=result["pole_id"],
                reason=None if per_field["valid"] else "; ".join(per_field["errors"]),
                recommendation=(
                    None
                    if per_field["valid"]
                    else "Correct the value or leave the field blank if it was not captured"
                ),
            )
        )

    if unknown_keys:
        result["warnings"].append(
            "Unknown Stage 4 columns ignored: " + ", ".join(sorted(unknown_keys))
        )

    result["normalised"] = normalised
    result["merge_ready"] = bool(result["valid"] and result["pole_id"])
    result["invalid"] = not result["valid"]
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
            row_result["invalid"] = True
            row_result["errors"].append(f"Row {index} is not a dict")
        if not row_result["valid"]:
            aggregate["valid"] = False
        aggregate["row_results"].append({"index": index, **row_result})

    seen_poles: dict[str, int] = {}
    for row_result in aggregate["row_results"]:
        pole_id = row_result.get("pole_id")
        if not pole_id:
            continue
        if pole_id in seen_poles:
            aggregate["valid"] = False
            first_index = seen_poles[pole_id]
            msg = f"Duplicate pole_id {pole_id!r} at rows {first_index} and {row_result['index']}"
            aggregate["errors"].append(msg)
            first_result = aggregate["row_results"][first_index]
            first_result["valid"] = False
            first_result["invalid"] = True
            first_result["merge_ready"] = False
            first_result["errors"].append(msg)
            row_result["valid"] = False
            row_result["invalid"] = True
            row_result["merge_ready"] = False
            row_result["errors"].append(msg)
        else:
            seen_poles[pole_id] = row_result["index"]

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
    "field_allows_explicit_none",
    "is_blank_for_field",
    "extract_stage4_row_identity",
    "normalise_bool",
    "validate_allowed_value",
    "validate_required_fields",
    "validate_stage4_row",
    "validate_stage4_rows",
    "classify_stage4_completeness",
    "normalise_stage4_row",
]
