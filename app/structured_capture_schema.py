"""Canonical Stage 4 structured-capture field schema.

Stage 4 is GridFlow's future structured field-capture layer. The fields
defined here are NOT present in current Trimble controller exports — they
are intended for future structured input by surveyors (tablet capture) or
designers/office staff (supplementary record).

This module is the single source of truth for the Stage 4 field catalogue.
It is deliberately decoupled from the live upload, parsing, QA, and popup
flows: nothing in this module is wired into runtime behaviour today.

Each field carries:
    field_name      machine name used in CSV/JSON
    label           human-friendly display label
    group           one of the canonical groups defined below
    type            "string" | "enum" | "integer" | "float" | "boolean_enum" | "date"
    required        True if the field must be present in a Stage 4 row
    allowed_values  tuple of allowed strings (for enum / boolean_enum) or None
    unit            short unit string (e.g. "kV", "mm") or None
    description     short text describing the field's purpose
    current_status  always "stage4_future_capture"
    source          always "structured_capture"
    aliases         tuple of accepted alternative names (lowercased)

All helpers are pure (no I/O, no Flask, no pandas). Standard library only.
"""

from __future__ import annotations

from typing import Any

CURRENT_STATUS = "stage4_future_capture"
SOURCE = "structured_capture"

# Canonical group identifiers and their human-friendly labels.
GROUPS: dict[str, str] = {
    "row_identity": "Row identity",
    "pole_specification": "Pole specification",
    "condition_defects": "Condition / defects",
    "electrical_conductor": "Electrical / conductor",
    "structural_support": "Structural support",
    "equipment_pole_top": "Equipment / pole-top",
    "capture_metadata": "Capture metadata",
}


def _field(
    field_name: str,
    *,
    label: str,
    group: str,
    type_: str,
    required: bool = False,
    allowed_values: tuple[str, ...] | None = None,
    unit: str | None = None,
    description: str,
    aliases: tuple[str, ...] = (),
) -> dict[str, Any]:
    if group not in GROUPS:
        raise ValueError(f"Unknown group: {group}")
    return {
        "field_name": field_name,
        "label": label,
        "group": group,
        "type": type_,
        "required": required,
        "allowed_values": allowed_values,
        "unit": unit,
        "description": description,
        "current_status": CURRENT_STATUS,
        "source": SOURCE,
        "aliases": tuple(alias.lower() for alias in aliases),
    }


# Reused enum vocabularies. Keeping them as named tuples reduces drift
# between similar fields and matches the wording used in the task spec.
CONDITION_VALUES: tuple[str, ...] = ("good", "fair", "poor", "unsafe", "unknown")
SEVERITY_VALUES: tuple[str, ...] = ("low", "medium", "high", "critical", "unknown")
LEAN_SEVERITY_VALUES: tuple[str, ...] = ("none", "slight", "moderate", "severe", "unknown")
VOLTAGE_VALUES: tuple[str, ...] = ("LV", "11kV", "33kV", "110kV", "unknown")
PRESENCE_VALUES: tuple[str, ...] = ("yes", "no", "unknown")
CONFIDENCE_VALUES: tuple[str, ...] = ("high", "medium", "low", "unknown")


_FIELD_DEFINITIONS: tuple[dict[str, Any], ...] = (
    # 1. Row identity -------------------------------------------------------
    _field(
        "pole_id",
        label="Pole ID",
        group="row_identity",
        type_="string",
        required=True,
        description="Stable support identifier used to match structured capture to Trimble data.",
        aliases=("point", "point_id", "support_id", "structure_id", "asset_id"),
    ),
    _field(
        "project_id",
        label="Project ID",
        group="row_identity",
        type_="string",
        description="Optional project identifier carried for provenance and audit.",
        aliases=("project", "job_id", "job"),
    ),
    _field(
        "file_id",
        label="File ID",
        group="row_identity",
        type_="string",
        description="Optional file/job segment identifier carried for provenance and audit.",
        aliases=("file", "folder_id", "survey_file"),
    ),
    _field(
        "structure_type",
        label="Structure type",
        group="row_identity",
        type_="enum",
        allowed_values=(
            "Pol",
            "EXpole",
            "Angle",
            "PRpole",
            "PRangle",
            "Stay",
            "Context",
            "unknown",
        ),
        description="Captured feature/structure type used for validation preview only.",
        aliases=("feature_code", "code"),
    ),
    _field(
        "asset_intent",
        label="Asset intent",
        group="row_identity",
        type_="enum",
        allowed_values=("existing", "proposed", "replacement", "context", "unknown"),
        description="Captured lifecycle/design intent used for validation preview only.",
        aliases=("role", "asset_role"),
    ),
    # 2. Pole specification --------------------------------------------------
    _field(
        "material",
        label="Material",
        group="pole_specification",
        type_="enum",
        allowed_values=("wood", "concrete", "steel", "composite", "fibreglass", "unknown"),
        description="Captured support material using the Stage 4 validation vocabulary.",
        aliases=("captured_material",),
    ),
    _field(
        "pole_class",
        label="Pole class",
        group="pole_specification",
        type_="string",
        description="Structural class designation (light/medium/heavy or DNO-specific code).",
        aliases=("class", "stoutness"),
    ),
    _field(
        "pole_strength",
        label="Pole strength",
        group="pole_specification",
        type_="string",
        description="Manufacturer or DNO strength rating identifier.",
        aliases=("strength", "stoutness_rating"),
    ),
    _field(
        "pole_material",
        label="Pole material",
        group="pole_specification",
        type_="enum",
        allowed_values=("wood", "concrete", "steel", "composite", "unknown"),
        description="Construction material of the pole shaft.",
        aliases=("material",),
    ),
    _field(
        "measured_height_m",
        label="Measured height",
        group="pole_specification",
        type_="float",
        unit="m",
        description="Structured measured support height in metres.",
        aliases=("measured_height", "height_m", "height"),
    ),
    _field(
        "height_source",
        label="Height source",
        group="pole_specification",
        type_="enum",
        allowed_values=(
            "measured_rtk",
            "measured_tape",
            "measured_rangefinder",
            "legacy_record",
            "estimated",
            "unknown",
        ),
        description="Source/provenance of the structured height value.",
    ),
    _field(
        "specification",
        label="Specification reference",
        group="pole_specification",
        type_="string",
        description="DNO or manufacturer specification reference for this pole.",
        aliases=("spec", "spec_ref"),
    ),
    # 3. Condition / defects ------------------------------------------------
    _field(
        "condition",
        label="Overall condition",
        group="condition_defects",
        type_="enum",
        allowed_values=CONDITION_VALUES,
        description="Overall pole condition assessed at capture time.",
    ),
    _field(
        "defect_type",
        label="Defect type",
        group="condition_defects",
        type_="string",
        description="Free-text or categorised defect (rot, split, lean, woodpecker, corrosion).",
        aliases=("defect",),
    ),
    _field(
        "defect_severity",
        label="Defect severity",
        group="condition_defects",
        type_="enum",
        allowed_values=SEVERITY_VALUES,
        description="Severity classification for the recorded defect.",
        aliases=("severity",),
    ),
    _field(
        "defect_notes",
        label="Defect notes",
        group="condition_defects",
        type_="string",
        description="Surveyor or designer free-text notes about the defect.",
    ),
    _field(
        "access_notes",
        label="Access notes",
        group="condition_defects",
        type_="string",
        description="Free-text notes on access constraints relevant to follow-up survey/design.",
    ),
    _field(
        "survey_notes",
        label="Survey notes",
        group="condition_defects",
        type_="string",
        description="Free-text structured capture notes for validation preview.",
        aliases=("notes", "remarks"),
    ),
    # 4. Electrical / conductor ---------------------------------------------
    _field(
        "voltage_carried",
        label="Voltage carried",
        group="electrical_conductor",
        type_="enum",
        allowed_values=VOLTAGE_VALUES,
        description="Operating voltage carried by conductors on this pole.",
        aliases=("voltage", "operating_voltage"),
    ),
    _field(
        "conductor_type",
        label="Conductor type",
        group="electrical_conductor",
        type_="enum",
        allowed_values=("bare", "covered", "abc", "underground", "unknown"),
        description="Conductor construction type.",
    ),
    _field(
        "conductor_size",
        label="Conductor size",
        group="electrical_conductor",
        type_="string",
        unit="mm² (or DNO code)",
        description="Conductor cross-section or DNO size code.",
    ),
    _field(
        "phase_configuration",
        label="Phase configuration",
        group="electrical_conductor",
        type_="enum",
        allowed_values=("single", "three", "split", "unknown"),
        description="Phase configuration carried at this pole.",
        aliases=("phases",),
    ),
    # 5. Structural support -------------------------------------------------
    _field(
        "stay_present",
        label="Stay present",
        group="structural_support",
        type_="boolean_enum",
        allowed_values=PRESENCE_VALUES,
        description="Whether a stay/support wire is present at this pole.",
        aliases=("has_stay",),
    ),
    _field(
        "stay_required",
        label="Stay required",
        group="structural_support",
        type_="boolean_enum",
        allowed_values=PRESENCE_VALUES,
        description="Whether structured capture says a stay is required.",
        aliases=("requires_stay",),
    ),
    _field(
        "stay_type",
        label="Stay type",
        group="structural_support",
        type_="enum",
        allowed_values=("down", "flying", "strut", "none", "unknown"),
        description="Construction style of the stay, if present.",
    ),
    _field(
        "stay_condition",
        label="Stay condition",
        group="structural_support",
        type_="enum",
        allowed_values=CONDITION_VALUES,
        description="Condition of the stay assembly, if present.",
    ),
    _field(
        "lean_direction",
        label="Lean direction",
        group="structural_support",
        type_="enum",
        allowed_values=("none", "north", "south", "east", "west", "unknown"),
        description="Cardinal direction of any observed pole lean.",
    ),
    _field(
        "lean_severity",
        label="Lean severity",
        group="structural_support",
        type_="enum",
        allowed_values=LEAN_SEVERITY_VALUES,
        description="Severity of any observed pole lean.",
    ),
    # 6. Equipment / pole-top ----------------------------------------------
    _field(
        "equipment_present",
        label="Equipment present",
        group="equipment_pole_top",
        type_="boolean_enum",
        allowed_values=PRESENCE_VALUES,
        description=(
            "Whether pole-top equipment is fitted (transformer, switchgear, regulator, etc.)."
        ),
        aliases=("has_equipment",),
    ),
    _field(
        "equipment_type",
        label="Equipment type",
        group="equipment_pole_top",
        type_="enum",
        allowed_values=(
            "transformer",
            "switchgear",
            "regulator",
            "recloser",
            "fuse",
            "isolator",
            "none",
            "unknown",
        ),
        description="Category of pole-top equipment, if present.",
    ),
    _field(
        "equipment_condition",
        label="Equipment condition",
        group="equipment_pole_top",
        type_="enum",
        allowed_values=CONDITION_VALUES,
        description="Condition of pole-top equipment, if present.",
    ),
    _field(
        "equipment_notes",
        label="Equipment notes",
        group="equipment_pole_top",
        type_="string",
        description="Free-text notes about pole-top equipment.",
    ),
    # 7. Capture metadata --------------------------------------------------
    _field(
        "capture_source",
        label="Capture source",
        group="capture_metadata",
        type_="enum",
        allowed_values=(
            "surveyor_tablet",
            "surveyor_paper",
            "office_audit",
            "designer_input",
            "historical_record",
            "unknown",
        ),
        required=True,
        description="Where this row of structured capture data originated.",
    ),
    _field(
        "source",
        label="Source",
        group="capture_metadata",
        type_="enum",
        allowed_values=(
            "structured_capture",
            "surveyor_tablet",
            "surveyor_paper",
            "office_audit",
            "designer_input",
            "historical_record",
            "unknown",
        ),
        description="Library-level provenance source for validation preview.",
        aliases=("provenance",),
    ),
    _field(
        "evidence_status",
        label="Evidence status",
        group="capture_metadata",
        type_="enum",
        allowed_values=(
            "measured",
            "observed",
            "legacy_record",
            "estimated",
            "not_recorded",
            "verification_required",
            "unknown",
        ),
        description="Validation-preview status for the captured evidence.",
    ),
    _field(
        "photo_reference",
        label="Photo reference",
        group="capture_metadata",
        type_="string",
        description="Optional photo/file reference if safely captured outside runtime storage.",
        aliases=("photo_ref", "photo_id"),
    ),
    _field(
        "captured_by",
        label="Captured by",
        group="capture_metadata",
        type_="string",
        required=True,
        description="Name or identifier of the person who captured the row.",
    ),
    _field(
        "capture_date",
        label="Capture date",
        group="capture_metadata",
        type_="date",
        required=True,
        description="ISO 8601 date (YYYY-MM-DD) the row was captured.",
    ),
    _field(
        "confidence_level",
        label="Confidence level",
        group="capture_metadata",
        type_="enum",
        allowed_values=CONFIDENCE_VALUES,
        description="Self-rated confidence in the captured values.",
    ),
    _field(
        "verification_required",
        label="Verification required",
        group="capture_metadata",
        type_="boolean_enum",
        allowed_values=PRESENCE_VALUES,
        description="Whether the capturer flags this row for follow-up verification.",
    ),
)


# Aliases pointing at canonical names. Built once at import time so that
# get_stage4_field_definition() can resolve common synonyms cheaply.
def _build_alias_map() -> dict[str, str]:
    mapping: dict[str, str] = {}
    for definition in _FIELD_DEFINITIONS:
        canonical = definition["field_name"]
        mapping[canonical.lower()] = canonical
        for alias in definition["aliases"]:
            mapping.setdefault(alias, canonical)
    return mapping


_ALIAS_MAP: dict[str, str] = _build_alias_map()


def _resolve(field_name: str) -> str | None:
    if not isinstance(field_name, str):
        return None
    return _ALIAS_MAP.get(field_name.strip().lower())


# ---------------------------------------------------------------------------
# Public helpers
# ---------------------------------------------------------------------------


def get_stage4_field_definition(field_name: str) -> dict[str, Any] | None:
    """Return the canonical field definition for ``field_name`` (or alias)."""

    canonical = _resolve(field_name)
    if canonical is None:
        return None
    for definition in _FIELD_DEFINITIONS:
        if definition["field_name"] == canonical:
            return dict(definition)
    return None


def get_stage4_fields() -> list[dict[str, Any]]:
    """Return every Stage 4 field definition (copied)."""

    return [dict(definition) for definition in _FIELD_DEFINITIONS]


def get_stage4_fields_by_group(group: str) -> list[dict[str, Any]]:
    """Return every Stage 4 field in the given canonical group identifier."""

    if group not in GROUPS:
        raise ValueError(f"Unknown group: {group}")
    return [dict(d) for d in _FIELD_DEFINITIONS if d["group"] == group]


def get_stage4_required_fields() -> list[str]:
    """Return the list of required field names, in declaration order."""

    return [d["field_name"] for d in _FIELD_DEFINITIONS if d["required"]]


def get_stage4_template_headers() -> list[str]:
    """Return CSV-template headers in canonical declaration order."""

    return [d["field_name"] for d in _FIELD_DEFINITIONS]


def is_stage4_field(field_name: str) -> bool:
    """Return True if ``field_name`` (or one of its aliases) is a Stage 4 field."""

    return _resolve(field_name) is not None


__all__ = [
    "CURRENT_STATUS",
    "SOURCE",
    "GROUPS",
    "CONDITION_VALUES",
    "SEVERITY_VALUES",
    "LEAN_SEVERITY_VALUES",
    "VOLTAGE_VALUES",
    "PRESENCE_VALUES",
    "CONFIDENCE_VALUES",
    "get_stage4_field_definition",
    "get_stage4_fields",
    "get_stage4_fields_by_group",
    "get_stage4_required_fields",
    "get_stage4_template_headers",
    "is_stage4_field",
]
