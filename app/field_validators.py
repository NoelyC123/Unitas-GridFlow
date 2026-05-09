"""Field validation functions for C2E2 popup expansion.

Pure validation functions for field values in GeoJSON feature properties.
All functions are side-effect-free and depend only on field_reference.py.

Design rules:
- Never raises. Returns (bool, error_string | None) or a value.
- structure_type context makes missing-value judgements accurate.
- Suitable for popup rendering, intake validation, and QA checks.
"""

from __future__ import annotations

import math
from typing import Any

from app.field_reference import (
    FIELD_DEFINITIONS,
    get_field_definition,
    get_missing_wording,
)

# Structure types that are NOT expected to carry pole height measurements.
# For these types, missing height is the norm, not a quality gap.
_HEIGHT_OPTIONAL_TYPES: frozenset[str] = frozenset(
    {
        "Pol",  # Intermediate proposed pole — not typically measured in survey
        "Hedge",
        "Tree",
        "Wall",
        "Fence",
        "Gate",
        "Track",
        "Stream",
        "Road",
        "Post",
        "Pline",
        "Ignore",
        # Crossing measurements record height of the wire, not a pole
        "11xing",
        "33xing",
        "110xing",
        "BTxing",
        "HVxing",
        "LVxing",
    }
)

# Structure types where missing height warrants a note (should be measured).
_HEIGHT_EXPECTED_TYPES: frozenset[str] = frozenset(
    {
        "EXpole",
        "Angle",
        "EXangle",
        "PRpole",
        "PRangle",
    }
)


def is_measured(value: Any) -> bool:
    """Return True if value is non-None, non-NaN, and non-empty-string."""
    if value is None:
        return False
    if isinstance(value, float) and math.isnan(value):
        return False
    if isinstance(value, str) and not value.strip():
        return False
    return True


def is_missing_legitimate(
    field_name: str,
    structure_type: str | None = None,
    file_type: str | None = None,
) -> bool:
    """Return True when a missing value is expected (not a quality gap).

    Accounts for:
    - Fields that are absent from Trimble format (material, pole_class)
    - Fields optional for specific structure_types (height on Pol)
    - Derived fields that may be absent for records with no relationship
    """
    defn = get_field_definition(field_name)
    if defn is None:
        return True  # Unknown fields — treat as legitimate

    # Derived fields with no relationship/intent aren't quality gaps
    if field_name in ("relationship", "being_replaced_by", "replacing", "asset_intent"):
        return True

    # Height: legitimate if structure_type doesn't require it
    if field_name == "height":
        if structure_type and structure_type in _HEIGHT_OPTIONAL_TYPES:
            return True
        # Also legitimate if structure type is unknown
        if not structure_type:
            return True
        return False

    # Material is absent from Trimble format — always legitimate missing
    if field_name == "material":
        return True

    # land_use is currently not extracted from Trimble — legitimate missing
    if field_name == "land_use":
        return True

    # Survey notes (name/location) are optional
    if field_name == "name":
        return True

    # qa_status, issue_count, warn_count, pole_id, easting, northing, structure_type
    # should always be present — missing is NOT legitimate
    if defn.get("always_present"):
        return False

    return True


def validate_field_value(
    value: Any,
    field_name: str,
) -> tuple[bool, str | None]:
    """Validate a field value against its definition rules.

    Returns (True, None) if valid or not applicable.
    Returns (False, error_message) if invalid.
    """
    defn = get_field_definition(field_name)
    if defn is None:
        return True, None  # Unknown field — no validation

    if not is_measured(value):
        return True, None  # Missing values handled separately

    validation = defn.get("validation")
    if validation is None:
        return True, None

    # Numeric range check
    if "min" in validation or "max" in validation:
        try:
            num = float(value)
        except (ValueError, TypeError):
            return False, f"'{field_name}' must be numeric; got {value!r}"
        if "min" in validation and num < validation["min"]:
            return False, (f"'{field_name}' value {num} is below minimum {validation['min']}")
        if "max" in validation and num > validation["max"]:
            return False, (f"'{field_name}' value {num} exceeds maximum {validation['max']}")

    # Allowed values check
    if "allowed" in validation:
        allowed = validation["allowed"]
        if value not in allowed:
            return False, (f"'{field_name}' value {value!r} not in allowed set: {allowed}")

    return True, None


def validate_height_value(
    height: Any,
    structure_type: str | None = None,
) -> tuple[bool, str | None]:
    """Validate a height value with structure-type context.

    Returns (True, None) on success or when height is legitimately absent.
    Returns (False, reason) when height is present but implausible.
    Returns (True, advisory) when height is absent and this should be noted.
    """
    if not is_measured(height):
        if structure_type in _HEIGHT_EXPECTED_TYPES:
            return True, f"Height not measured for {structure_type} — check survey"
        return True, None

    try:
        h = float(height)
    except (ValueError, TypeError):
        return False, f"Height is not numeric: {height!r}"

    defn = FIELD_DEFINITIONS.get("height", {})
    validation = defn.get("validation", {})
    min_h = validation.get("min", 0.3)
    max_h = validation.get("max", 30.0)

    if h < min_h:
        return False, f"Height {h}m is below plausible minimum ({min_h}m)"
    if h > max_h:
        return False, f"Height {h}m exceeds plausible maximum ({max_h}m)"

    return True, None


def format_field_display(
    value: Any,
    field_name: str,
    structure_type: str | None = None,
) -> str:
    """Format a field value for display in a popup.

    Returns the formatted string, or the appropriate missing-value wording
    when value is absent.
    """
    defn = get_field_definition(field_name)

    if not is_measured(value):
        return get_missing_wording(field_name, structure_type)

    # Numeric fields: append unit
    unit = defn.get("unit") if defn else None
    try:
        num = float(value)
        if not math.isnan(num):
            formatted = f"{num:g}"  # removes trailing zeros
            return f"{formatted}{unit}" if unit else formatted
    except (ValueError, TypeError):
        pass

    # Boolean-ish coercion
    if isinstance(value, bool):
        return "Yes" if value else "No"

    return str(value).strip() or get_missing_wording(field_name, structure_type)


def get_popup_display_value(
    field_name: str,
    properties: dict[str, Any],
    structure_type: str | None = None,
) -> str:
    """Return the display string for a field from a feature's properties dict.

    Resolves the value from properties (using aliases if needed), then
    delegates to format_field_display for formatting and missing handling.
    """
    from app.field_reference import get_all_aliases

    # Try canonical name first, then aliases
    value = properties.get(field_name)
    if not is_measured(value):
        for alias in get_all_aliases(field_name)[1:]:  # skip canonical already tried
            candidate = properties.get(alias)
            if is_measured(candidate):
                value = candidate
                break

    # Use structure_type from properties if not provided
    if structure_type is None:
        structure_type = properties.get("structure_type")

    return format_field_display(value, field_name, structure_type)


def classify_field_completeness(
    properties: dict[str, Any],
    field_names: list[str],
) -> dict[str, str]:
    """Classify completeness of a set of fields for a feature's properties.

    Returns a dict of {field_name: status} where status is one of:
        'present'    — value is measured/non-null
        'absent_ok'  — missing but legitimately absent for this record
        'absent_warn' — missing and expected to be present
    """
    structure_type = properties.get("structure_type")
    result: dict[str, str] = {}

    for field in field_names:
        value = properties.get(field)
        measured = is_measured(value)

        if measured:
            result[field] = "present"
        elif is_missing_legitimate(field, structure_type):
            result[field] = "absent_ok"
        else:
            result[field] = "absent_warn"

    return result
