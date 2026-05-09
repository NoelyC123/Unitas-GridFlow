"""Field reference module for C2E2 popup expansion.

Defines the authoritative field catalogue for popup display:
- POPUP_FIELD_GROUPS: 5 logical groups for popup layout
- FIELD_DEFINITIONS: per-field metadata (label, aliases, missing wording, source)
- Helper functions for validators and popup renderers

No side effects. No imports from other app modules.
"""

from __future__ import annotations

# ---------------------------------------------------------------------------
# Field groups for popup layout
# ---------------------------------------------------------------------------

POPUP_FIELD_GROUPS: dict[str, list[str]] = {
    "identity": [
        "pole_id",
        "structure_type",
        "asset_intent",
        "record_role",
    ],
    "geometry": [
        "easting",
        "northing",
        "height",
    ],
    "quality": [
        "qa_status",
        "issue_count",
        "warn_count",
    ],
    "survey_context": [
        "name",
        "material",
        "land_use",
    ],
    "relationship": [
        "relationship",
        "being_replaced_by",
        "replacing",
    ],
}

# Ordered group display sequence
POPUP_GROUP_ORDER: list[str] = [
    "identity",
    "geometry",
    "quality",
    "survey_context",
    "relationship",
]

# ---------------------------------------------------------------------------
# Field definitions
# ---------------------------------------------------------------------------
# Each field has:
#   label           str   Display label in popup
#   aliases         list  Alternative column names accepted on intake
#   missing_wording str   Default text when value is None/empty
#   source          str   'survey' | 'derived' | 'trimble_attr'
#   always_present  bool  True if guaranteed non-null after processing
#   unit            str|None  Physical unit for display
#   trimble_attr    str|None  Trimble attribute key (e.g. 'HEIGHT', 'REMARK')
#   validation      dict|None  {'min': float, 'max': float, 'allowed': list}
#   conditional_missing  dict|None  {structure_type: wording} overrides
# ---------------------------------------------------------------------------

FIELD_DEFINITIONS: dict[str, dict] = {
    # --- Identity fields ---
    "pole_id": {
        "label": "Point ID",
        "aliases": ["point_id", "pt", "pnt", "point_no", "no", "number"],
        "missing_wording": "No ID",
        "source": "survey",
        "always_present": True,
        "unit": None,
        "trimble_attr": None,
        "validation": None,
        "conditional_missing": None,
    },
    "structure_type": {
        "label": "Feature Code",
        "aliases": ["code", "feature_code", "feat_code", "fc", "type"],
        "missing_wording": "Unknown",
        "source": "survey",
        "always_present": True,
        "unit": None,
        "trimble_attr": None,
        "validation": None,
        "conditional_missing": None,
    },
    "asset_intent": {
        "label": "Asset Intent",
        "aliases": [],
        "missing_wording": "Not classified",
        "source": "derived",
        "always_present": False,
        "unit": None,
        "trimble_attr": None,
        "validation": None,
        "conditional_missing": None,
    },
    "record_role": {
        "label": "Record Role",
        "aliases": ["_record_role"],
        "missing_wording": "Unclassified",
        "source": "derived",
        "always_present": True,
        "unit": None,
        "trimble_attr": None,
        "validation": {"allowed": ["structural", "context", "anchor", "third_party"]},
        "conditional_missing": None,
    },
    # --- Geometry fields ---
    "easting": {
        "label": "Easting",
        "aliases": ["e", "east", "osgb_e", "osgb_east", "grid_east", "x"],
        "missing_wording": "Not recorded",
        "source": "survey",
        "always_present": True,
        "unit": "m",
        "trimble_attr": None,
        "validation": {"min": 0.0, "max": 700_000.0},
        "conditional_missing": None,
    },
    "northing": {
        "label": "Northing",
        "aliases": ["n", "north", "osgb_n", "osgb_north", "grid_north", "y"],
        "missing_wording": "Not recorded",
        "source": "survey",
        "always_present": True,
        "unit": "m",
        "trimble_attr": None,
        "validation": {"min": 0.0, "max": 1_300_000.0},
        "conditional_missing": None,
    },
    "height": {
        "label": "Measured Height",
        "aliases": ["h", "ht", "elev", "elevation", "z", "pole_height", "heights"],
        "missing_wording": "Not measured",
        "source": "trimble_attr",
        "always_present": False,
        "unit": "m",
        "trimble_attr": "HEIGHT",
        "validation": {"min": 0.3, "max": 30.0},
        # Intermediate poles (Pol) are not expected to have height recorded
        "conditional_missing": {
            "Pol": "Not measured (intermediate pole)",
            "EXpole": "Not measured — check survey notes",
            "Angle": "Not measured — check survey notes",
            "PRpole": "Not measured",
            "PRangle": "Not measured",
        },
    },
    # --- Quality fields ---
    "qa_status": {
        "label": "QA Status",
        "aliases": ["status"],
        "missing_wording": "Not assessed",
        "source": "derived",
        "always_present": True,
        "unit": None,
        "trimble_attr": None,
        "validation": {"allowed": ["PASS", "WARN", "FAIL"]},
        "conditional_missing": None,
    },
    "issue_count": {
        "label": "Issues",
        "aliases": ["fail_count"],
        "missing_wording": "0",
        "source": "derived",
        "always_present": True,
        "unit": None,
        "trimble_attr": None,
        "validation": {"min": 0},
        "conditional_missing": None,
    },
    "warn_count": {
        "label": "Warnings",
        "aliases": [],
        "missing_wording": "0",
        "source": "derived",
        "always_present": True,
        "unit": None,
        "trimble_attr": None,
        "validation": {"min": 0},
        "conditional_missing": None,
    },
    # --- Survey context fields ---
    "name": {
        "label": "Survey Note",
        "aliases": [
            "location",
            "remark",
            "remarks",
            "note",
            "notes",
            "description",
            "comment",
            "desc",
        ],
        "missing_wording": "—",
        "source": "trimble_attr",
        "always_present": False,
        "unit": None,
        "trimble_attr": "REMARK",
        "validation": None,
        "conditional_missing": None,
    },
    "material": {
        "label": "Material",
        "aliases": ["mat", "pole_material"],
        "missing_wording": "Not recorded in survey",
        "source": "survey",
        "always_present": False,
        "unit": None,
        "trimble_attr": None,
        "validation": {"allowed": ["Wood", "Steel", "Concrete", "Composite", "Fibreglass"]},
        # Material is absent from Trimble controller format — not a quality gap
        "conditional_missing": {
            "_trimble_format": "Not recorded in survey",
        },
    },
    "land_use": {
        "label": "Land Use",
        "aliases": [],
        "missing_wording": "Not recorded",
        "source": "trimble_attr",
        "always_present": False,
        "unit": None,
        "trimble_attr": "LAND USE",
        "validation": None,
        "conditional_missing": None,
    },
    # --- Relationship fields ---
    "relationship": {
        "label": "Relationship",
        "aliases": [],
        "missing_wording": "—",
        "source": "derived",
        "always_present": False,
        "unit": None,
        "trimble_attr": None,
        "validation": {"allowed": ["replacement_pair", "stay_anchor"]},
        "conditional_missing": None,
    },
    "being_replaced_by": {
        "label": "Being Replaced By",
        "aliases": [],
        "missing_wording": "—",
        "source": "derived",
        "always_present": False,
        "unit": None,
        "trimble_attr": None,
        "validation": None,
        "conditional_missing": None,
    },
    "replacing": {
        "label": "Replacing",
        "aliases": [],
        "missing_wording": "—",
        "source": "derived",
        "always_present": False,
        "unit": None,
        "trimble_attr": None,
        "validation": None,
        "conditional_missing": None,
    },
    # Extra field present in GeoJSON properties
    "id": {
        "label": "ID",
        "aliases": [],
        "missing_wording": "No ID",
        "source": "derived",
        "always_present": True,
        "unit": None,
        "trimble_attr": None,
        "validation": None,
        "conditional_missing": None,
    },
}

# Complete set of known field names
ALL_FIELD_NAMES: frozenset[str] = frozenset(FIELD_DEFINITIONS)

# Fields that come directly from Trimble attribute pairs
TRIMBLE_ATTRIBUTE_FIELDS: frozenset[str] = frozenset(
    name for name, defn in FIELD_DEFINITIONS.items() if defn["source"] == "trimble_attr"
)

# Fields that are always guaranteed non-null after processing
ALWAYS_PRESENT_FIELDS: frozenset[str] = frozenset(
    name for name, defn in FIELD_DEFINITIONS.items() if defn.get("always_present")
)

# Fields that are derived by the pipeline (not from raw CSV)
DERIVED_FIELDS: frozenset[str] = frozenset(
    name for name, defn in FIELD_DEFINITIONS.items() if defn["source"] == "derived"
)


# ---------------------------------------------------------------------------
# Helper functions
# ---------------------------------------------------------------------------


def get_field_definition(field_name: str) -> dict | None:
    """Return the field definition dict for field_name, or None if unknown."""
    return FIELD_DEFINITIONS.get(field_name)


def get_all_aliases(field_name: str) -> list[str]:
    """Return all known aliases for a field, including the canonical name itself."""
    defn = FIELD_DEFINITIONS.get(field_name)
    if defn is None:
        return [field_name]
    return [field_name] + list(defn.get("aliases") or [])


def get_display_label(field_name: str) -> str:
    """Return the human-readable display label for a field."""
    defn = FIELD_DEFINITIONS.get(field_name)
    if defn is None:
        return field_name.replace("_", " ").title()
    return defn["label"]


def get_missing_wording(field_name: str, structure_type: str | None = None) -> str:
    """Return appropriate missing-value wording for a field.

    Uses conditional_missing overrides when structure_type is provided and
    a matching override exists. Falls back to the default missing_wording.
    """
    defn = FIELD_DEFINITIONS.get(field_name)
    if defn is None:
        return "—"
    conditional = defn.get("conditional_missing")
    if conditional and structure_type and structure_type in conditional:
        return conditional[structure_type]
    return defn.get("missing_wording", "—")


def get_fields_for_group(group_name: str) -> list[str]:
    """Return the list of field names belonging to a popup group."""
    return POPUP_FIELD_GROUPS.get(group_name, [])


def get_field_unit(field_name: str) -> str | None:
    """Return the unit string for a field, or None if unitless."""
    defn = FIELD_DEFINITIONS.get(field_name)
    if defn is None:
        return None
    return defn.get("unit")


def resolve_alias(column_name: str) -> str | None:
    """Return the canonical field name for a column name or alias.

    Returns None if the column name is not recognised as any field or alias.
    """
    lower = column_name.strip().lower()
    for field_name, defn in FIELD_DEFINITIONS.items():
        if lower == field_name:
            return field_name
        aliases = [a.lower() for a in (defn.get("aliases") or [])]
        if lower in aliases:
            return field_name
    return None
