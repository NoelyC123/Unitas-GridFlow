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

from datetime import date
from typing import Any

from app.structured_capture_schema import (
    PRESENCE_VALUES,
    SOURCE,
    get_stage4_field_definition,
    get_stage4_fields,
    get_stage4_required_fields,
    get_stage4_template_headers,
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
_IDENTITY_FIELDS: frozenset[str] = frozenset(
    {"pole_id", "project_id", "file_id", "structure_type", "asset_intent"}
)
_CAPTURE_METADATA_FIELDS: frozenset[str] = frozenset(
    {
        "capture_source",
        "captured_by",
        "capture_date",
        "source",
        "confidence_level",
        "verification_required",
        "evidence_status",
        "photo_reference",
    }
)
_HEIGHT_LIMITS: dict[str, tuple[float, float]] = {"measured_height_m": (0.3, 30.0)}


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


def _normalise_float(value: Any) -> tuple[float | None, str | None]:
    if is_blank(value):
        return None, None
    try:
        number = float(str(value).strip().removesuffix("m").strip())
    except (TypeError, ValueError):
        return None, "not a valid number"
    return number, None


def _normalise_date(value: Any) -> tuple[str | None, str | None]:
    if is_blank(value):
        return None, None
    text = str(value).strip()
    try:
        date.fromisoformat(text)
    except ValueError:
        return None, "not a valid ISO date (YYYY-MM-DD)"
    return text, None


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
    value: Any = None,
    raw_value: Any = None,
    normalised_value: Any = None,
    valid: bool,
    severity: str = "PASS",
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
        "raw_value": raw_value,
        "normalised_value": normalised_value if normalised_value is not None else value,
        "value": value,
        "severity": severity,
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
        error = f"Unknown Stage 4 field: {field_name!r}"
        result["errors"].append(error)
        result["field_results"].append(
            _field_result(
                field_name=str(field_name),
                raw_value=value,
                normalised_value=None,
                valid=False,
                severity="ERROR",
                errors=[error],
                reason="unknown field",
                recommendation="remove the column or add it to the Stage 4 schema",
            )
        )
        return result

    canonical = definition["field_name"]
    allowed = definition.get("allowed_values")
    field_type = definition["type"]

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
                    raw_value=value,
                    normalised_value=None,
                    value=None,
                    valid=False,
                    severity="BLOCKER",
                    errors=[error],
                    reason=reason,
                    recommendation="provide stable pole_id before merge/runtime integration",
                )
            )
            return result
        normalised = str(value).strip()
        result["normalised"][canonical] = normalised
        result["field_results"].append(
            _field_result(
                field_name=canonical,
                raw_value=value,
                normalised_value=normalised,
                value=normalised,
                valid=True,
                severity="PASS",
            )
        )
        return result

    if is_blank_for_field(canonical, value):
        # blank handled by required-field check; otherwise valid
        result["normalised"][canonical] = None
        result["field_results"].append(
            _field_result(
                field_name=canonical,
                raw_value=value,
                normalised_value=None,
                value=None,
                valid=True,
                severity="INFO",
                reason="blank optional value",
                recommendation="leave blank only when the field was not captured",
            )
        )
        return result

    if field_type == "boolean_enum":
        if not _is_known_bool_token(value):
            error = f"{canonical}: {value!r} is not one of {list(PRESENCE_VALUES)}"
            result["valid"] = False
            result["invalid"] = True
            result["errors"].append(error)
            result["field_results"].append(
                _field_result(
                    field_name=canonical,
                    raw_value=value,
                    normalised_value=None,
                    value=None,
                    valid=False,
                    severity="ERROR",
                    errors=[error],
                    reason="invalid boolean-like value",
                    recommendation="use yes, no, or unknown",
                )
            )
            return result
        normalised = normalise_bool(value)
        result["normalised"][canonical] = normalised
        result["field_results"].append(
            _field_result(
                field_name=canonical,
                raw_value=value,
                normalised_value=normalised,
                value=normalised,
                valid=True,
            )
        )
        return result

    if field_type in {"float", "integer"}:
        normalised, error_reason = _normalise_float(value)
        if field_type == "integer" and normalised is not None and not normalised.is_integer():
            error_reason = "not a valid integer"
        if error_reason is None and normalised is not None and canonical in _HEIGHT_LIMITS:
            low, high = _HEIGHT_LIMITS[canonical]
            if normalised < low or normalised > high:
                error_reason = f"outside allowed range {low:g}-{high:g}m"
        if error_reason:
            error = f"{canonical}: {value!r} is {error_reason}"
            result["valid"] = False
            result["invalid"] = True
            result["errors"].append(error)
            result["field_results"].append(
                _field_result(
                    field_name=canonical,
                    raw_value=value,
                    normalised_value=None,
                    value=None,
                    valid=False,
                    severity="BLOCKER" if canonical == "measured_height_m" else "ERROR",
                    errors=[error],
                    reason="invalid height" if canonical == "measured_height_m" else error_reason,
                    recommendation=(
                        "provide measured height in metres within 0.3-30m"
                        if canonical == "measured_height_m"
                        else "provide a valid numeric value"
                    ),
                )
            )
            return result
        if field_type == "integer" and normalised is not None:
            normalised = int(normalised)
        result["normalised"][canonical] = normalised
        result["field_results"].append(
            _field_result(
                field_name=canonical,
                raw_value=value,
                normalised_value=normalised,
                value=normalised,
                valid=True,
            )
        )
        return result

    if field_type == "date":
        normalised_date, error_reason = _normalise_date(value)
        if error_reason:
            error = f"{canonical}: {value!r} is {error_reason}"
            result["valid"] = False
            result["invalid"] = True
            result["errors"].append(error)
            result["field_results"].append(
                _field_result(
                    field_name=canonical,
                    raw_value=value,
                    normalised_value=None,
                    value=None,
                    valid=False,
                    severity="ERROR",
                    errors=[error],
                    reason="invalid date",
                    recommendation="provide an ISO date in YYYY-MM-DD format",
                )
            )
            return result
        result["normalised"][canonical] = normalised_date
        result["field_results"].append(
            _field_result(
                field_name=canonical,
                raw_value=value,
                normalised_value=normalised_date,
                value=normalised_date,
                valid=True,
            )
        )
        return result

    if allowed is None:
        # free-text fields: accept the trimmed string
        normalised = str(value).strip()
        result["normalised"][canonical] = normalised
        result["field_results"].append(
            _field_result(
                field_name=canonical,
                raw_value=value,
                normalised_value=normalised,
                value=normalised,
                valid=True,
            )
        )
        return result

    canonical_member = _normalise_enum_value(value, allowed)
    if canonical_member is None:
        error = f"{canonical}: {value!r} is not one of {list(allowed)}"
        result["valid"] = False
        result["invalid"] = True
        result["errors"].append(error)
        result["field_results"].append(
            _field_result(
                field_name=canonical,
                raw_value=value,
                normalised_value=None,
                value=None,
                valid=False,
                severity="ERROR",
                errors=[error],
                reason="invalid enum",
                recommendation=f"use one of {', '.join(allowed)}",
            )
        )
        return result
    result["normalised"][canonical] = canonical_member
    result["field_results"].append(
        _field_result(
            field_name=canonical,
            raw_value=value,
            normalised_value=canonical_member,
            value=canonical_member,
            valid=True,
        )
    )
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

        if definition["type"] in {"float", "integer"}:
            number, error_reason = _normalise_float(value)
            if error_reason:
                normalised[canonical] = str(value).strip()
                continue
            normalised[canonical] = int(number) if definition["type"] == "integer" else number
            continue

        if definition["type"] == "date":
            date_value, error_reason = _normalise_date(value)
            normalised[canonical] = str(value).strip() if error_reason else date_value
            continue

        allowed = definition.get("allowed_values")
        if allowed is None:
            normalised[canonical] = str(value).strip()
            continue

        canonical_member = _normalise_enum_value(value, allowed)
        # Keep the original value if it doesn't match — validation will flag it.
        normalised[canonical] = canonical_member if canonical_member else str(value).strip()
    return normalised


def _has_substantive_stage4_values(normalised: dict[str, Any]) -> bool:
    for field_name, value in normalised.items():
        if field_name in _IDENTITY_FIELDS or field_name in _CAPTURE_METADATA_FIELDS:
            continue
        if not is_blank(value):
            return True
    return False


def _row_review_findings(normalised: dict[str, Any]) -> list[dict[str, Any]]:
    findings: list[dict[str, Any]] = []

    def _add(reason: str, recommendation: str) -> None:
        findings.append(
            {
                "severity": "WARNING",
                "reason": reason,
                "recommendation": recommendation,
                "source": SOURCE,
            }
        )

    stay_present = normalised.get("stay_present")
    stay_type = normalised.get("stay_type")
    if stay_present == "no" and stay_type not in (None, "none", "unknown"):
        _add(
            "contradictory evidence: stay_present=no but stay_type is populated",
            "review stay evidence before merge/runtime integration",
        )

    equipment_present = normalised.get("equipment_present")
    equipment_type = normalised.get("equipment_type")
    if equipment_present == "no" and equipment_type not in (None, "none", "unknown"):
        _add(
            "contradictory evidence: equipment_present=no but equipment_type is populated",
            "review equipment evidence before merge/runtime integration",
        )

    height = normalised.get("measured_height_m")
    height_source = normalised.get("height_source")
    if height is not None and height_source in (None, "unknown"):
        _add(
            "measured height has no confident height_source",
            "provide height_source before clearance/design use",
        )
    if height is None and isinstance(height_source, str) and height_source.startswith("measured_"):
        _add(
            "height_source says measured but measured_height_m is blank",
            "provide measured_height_m or correct height_source",
        )

    if normalised.get("confidence_level") == "low":
        _add(
            "low confidence structured capture row",
            "field verification required before runtime merge",
        )
    if normalised.get("verification_required") == "yes":
        _add(
            "verification_required=yes",
            "complete verification before treating the row as merge-ready",
        )
    if normalised.get("evidence_status") == "verification_required":
        _add(
            "evidence status requires verification",
            "resolve evidence status before runtime merge",
        )

    return findings


def _classify_row(
    *,
    valid: bool,
    pole_id: str | None,
    errors: list[str],
    warnings: list[str],
    has_substantive_values: bool,
) -> str:
    if not pole_id or any(
        token in err.lower()
        for err in errors
        for token in (
            "required field missing",
            "unsafe or missing row identity",
            "duplicate pole_id",
            "measured_height_m",
        )
    ):
        return "blocked"
    if not valid:
        return "invalid"
    if warnings:
        return "review-required"
    if not has_substantive_values:
        return "valid but not merge-ready"
    return "merge-ready"


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
                        raw_value=None,
                        normalised_value=None,
                        valid=False,
                        severity="BLOCKER" if field_name == "pole_id" else "ERROR",
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
            if isinstance(key, str):
                unknown_keys.append(key)
            continue
        per_field = validate_allowed_value(key, value)
        if not per_field["valid"]:
            result["valid"] = False
            result["invalid"] = True
            result["errors"].extend(per_field["errors"])
        normalised.update(per_field["normalised"])
        for field_result in per_field["field_results"]:
            enriched = dict(field_result)
            enriched["row_id"] = result["row_id"]
            enriched["pole_id"] = result["pole_id"]
            result["field_results"].append(enriched)

    if unknown_keys:
        result["warnings"].append(
            "Unknown Stage 4 columns ignored: " + ", ".join(sorted(unknown_keys))
        )

    result["normalised"] = normalised
    row_findings = _row_review_findings(normalised)
    for finding in row_findings:
        result["warnings"].append(finding["reason"])
    has_substantive_values = _has_substantive_stage4_values(normalised)
    row_status = _classify_row(
        valid=result["valid"],
        pole_id=result["pole_id"],
        errors=result["errors"],
        warnings=result["warnings"],
        has_substantive_values=has_substantive_values,
    )
    result["row_status"] = row_status
    result["classification"] = row_status
    result["blocked"] = row_status == "blocked"
    result["review_required"] = row_status == "review-required"
    result["has_substantive_values"] = has_substantive_values
    result["row_findings"] = row_findings
    result["merge_ready"] = row_status == "merge-ready"
    result["invalid"] = not result["valid"]
    return result


def _mark_duplicate_pole_ids(
    row_results: list[dict[str, Any]], aggregate_errors: list[str]
) -> None:
    seen_poles: dict[str, int] = {}
    for row_result in row_results:
        pole_id = row_result.get("pole_id")
        if not pole_id:
            continue
        if pole_id in seen_poles:
            first_index = seen_poles[pole_id]
            msg = f"Duplicate pole_id {pole_id!r} at rows {first_index} and {row_result['index']}"
            aggregate_errors.append(msg)
            first_result = row_results[first_index]
            for affected in (first_result, row_result):
                affected["valid"] = False
                affected["invalid"] = True
                affected["merge_ready"] = False
                affected["blocked"] = True
                affected["review_required"] = False
                affected["row_status"] = "blocked"
                affected["classification"] = "blocked"
                affected["errors"].append(msg)
                affected["field_results"].append(
                    _field_result(
                        field_name="pole_id",
                        raw_value=pole_id,
                        normalised_value=pole_id,
                        value=pole_id,
                        valid=False,
                        severity="BLOCKER",
                        errors=[msg],
                        row_id=affected.get("row_id"),
                        pole_id=pole_id,
                        reason="duplicate pole_id",
                        recommendation=(
                            "provide a unique stable pole_id before merge/runtime integration"
                        ),
                    )
                )
        else:
            seen_poles[pole_id] = row_result["index"]


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

    _mark_duplicate_pole_ids(aggregate["row_results"], aggregate["errors"])
    if aggregate["errors"]:
        aggregate["valid"] = False
    aggregate["total_rows"] = len(aggregate["row_results"])
    aggregate["valid_rows"] = sum(1 for row in aggregate["row_results"] if row.get("valid"))
    aggregate["invalid_rows"] = sum(1 for row in aggregate["row_results"] if row.get("invalid"))
    aggregate["merge_ready_rows"] = sum(
        1 for row in aggregate["row_results"] if row.get("merge_ready")
    )
    aggregate["blocked_rows"] = sum(1 for row in aggregate["row_results"] if row.get("blocked"))
    aggregate["review_required_rows"] = sum(
        1 for row in aggregate["row_results"] if row.get("review_required")
    )

    return aggregate


def validate_stage4_headers(headers: list[str] | tuple[str, ...]) -> dict[str, Any]:
    """Validate a structured-capture CSV header row against the Stage 4 schema."""

    schema_headers = get_stage4_template_headers()
    required = set(get_stage4_required_fields())
    result: dict[str, Any] = {
        "valid": True,
        "errors": [],
        "warnings": [],
        "headers": list(headers) if isinstance(headers, (list, tuple)) else [],
        "normalised_headers": [],
        "missing_columns": [],
        "missing_required_columns": [],
        "unknown_columns": [],
        "duplicate_columns": [],
    }

    if not isinstance(headers, (list, tuple)) or not headers:
        result["valid"] = False
        result["errors"].append("Structured capture header row is missing")
        result["missing_columns"] = schema_headers
        result["missing_required_columns"] = sorted(required)
        return result

    seen: set[str] = set()
    for header in headers:
        raw_header = str(header).strip()
        definition = get_stage4_field_definition(raw_header)
        if definition is None:
            result["unknown_columns"].append(raw_header)
            continue
        canonical = definition["field_name"]
        result["normalised_headers"].append(canonical)
        if canonical in seen:
            result["duplicate_columns"].append(canonical)
        seen.add(canonical)

    result["missing_columns"] = [header for header in schema_headers if header not in seen]
    result["missing_required_columns"] = sorted(required - seen)
    if result["missing_required_columns"]:
        result["valid"] = False
        result["errors"].append(
            "Missing required structured capture columns: "
            + ", ".join(result["missing_required_columns"])
        )
    if result["duplicate_columns"]:
        result["valid"] = False
        result["errors"].append(
            "Duplicate structured capture columns: " + ", ".join(result["duplicate_columns"])
        )
    if result["unknown_columns"]:
        result["warnings"].append(
            "Unknown structured capture columns ignored: "
            + ", ".join(sorted(result["unknown_columns"]))
        )
    if result["missing_columns"]:
        result["warnings"].append(
            "Template columns not present in upload: " + ", ".join(result["missing_columns"])
        )
    return result


def validate_stage4_import_preview(
    rows: list[dict[str, Any]],
    *,
    headers: list[str] | tuple[str, ...] | None = None,
) -> dict[str, Any]:
    """Return a pre-runtime structured-capture validation/import preview artefact."""

    inferred_headers: list[str] = []
    if headers is None and isinstance(rows, list):
        seen: set[str] = set()
        for row in rows:
            if not isinstance(row, dict):
                continue
            for key in row:
                if key not in seen:
                    seen.add(key)
                    inferred_headers.append(key)

    header_validation = validate_stage4_headers(headers or inferred_headers)
    row_validation = validate_stage4_rows(rows)
    row_results = row_validation.get("row_results", [])

    errors = list(header_validation["errors"]) + list(row_validation.get("errors", []))
    warnings = list(header_validation["warnings"]) + list(row_validation.get("warnings", []))
    for row_result in row_results:
        errors.extend(row_result.get("errors", []))
        warnings.extend(row_result.get("warnings", []))

    total_rows = len(rows) if isinstance(rows, list) else 0
    merge_ready_rows = sum(1 for row in row_results if row.get("merge_ready"))
    blocked_rows = sum(1 for row in row_results if row.get("blocked"))
    invalid_rows = sum(1 for row in row_results if row.get("invalid"))
    review_required_rows = sum(1 for row in row_results if row.get("review_required"))
    valid_rows = sum(1 for row in row_results if row.get("valid"))

    if not isinstance(rows, list):
        errors.append("Rows payload must be a list")
    if total_rows == 0:
        errors.append("Structured capture file contains no data rows")

    safe_to_merge = (
        header_validation["valid"]
        and row_validation.get("valid", False)
        and merge_ready_rows > 0
        and blocked_rows == 0
        and invalid_rows == 0
        and review_required_rows == 0
    )
    if blocked_rows:
        verdict = "blocked"
    elif invalid_rows:
        verdict = "invalid"
    elif review_required_rows:
        verdict = "review-required"
    elif merge_ready_rows:
        verdict = "merge-ready"
    else:
        verdict = "valid but not merge-ready"

    return {
        "valid": not errors,
        "safe_to_merge": safe_to_merge,
        "verdict": verdict,
        "source": SOURCE,
        "total_rows": total_rows,
        "valid_rows": valid_rows,
        "invalid_rows": invalid_rows,
        "merge_ready_rows": merge_ready_rows,
        "blocked_rows": blocked_rows,
        "review_required_rows": review_required_rows,
        "warnings": warnings,
        "errors": errors,
        "header_validation": header_validation,
        "row_results": row_results,
        "per_row_validation_results": row_results,
        "per_field_validation_results": [
            field_result
            for row_result in row_results
            for field_result in row_result.get("field_results", [])
        ],
        "preview_summary": {
            "total_rows": total_rows,
            "merge_ready_rows": merge_ready_rows,
            "blocked_rows": blocked_rows,
            "review_required_rows": review_required_rows,
            "safe_to_merge": safe_to_merge,
            "verdict": verdict,
        },
    }


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
    "validate_stage4_headers",
    "validate_stage4_import_preview",
    "classify_stage4_completeness",
    "normalise_stage4_row",
]
