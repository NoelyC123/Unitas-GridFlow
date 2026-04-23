from __future__ import annotations

MATERIAL_VALUES = ["Wood", "Steel", "Concrete", "Composite"]
STRUCTURE_TYPE_VALUES = ["Wood Pole", "Steel Pole", "Concrete Pole", "Composite Pole"]


BASE_RULES = [
    {"check": "unique", "field": "pole_id"},
    {"check": "required", "field": "pole_id"},
    {"check": "required", "field": "height", "structural_only": True},
    {"check": "required", "field": "material"},
    {"check": "required", "field": "location"},
    {"check": "required", "field": "structure_type"},
    {"check": "required", "field": "lat"},
    {"check": "required", "field": "lon"},
    {"check": "required", "field": "easting"},
    {"check": "required", "field": "northing"},
    # Generic height range (overridden per DNO rulepack)
    {"check": "range", "field": "height", "min": 7, "max": 25, "structural_only": True},
    # UK-wide coordinate bounds
    {"check": "range", "field": "lat", "min": 49, "max": 62},
    {"check": "range", "field": "lon", "min": -9, "max": 3},
    {"check": "range", "field": "easting", "min": 0, "max": 700000},
    {"check": "range", "field": "northing", "min": 0, "max": 1300000},
    {"check": "allowed_values", "field": "material", "values": MATERIAL_VALUES},
    {
        "check": "allowed_values",
        "field": "structure_type",
        "values": STRUCTURE_TYPE_VALUES,
    },
]


# Backwards-compatible alias (older code/docs reference this name).
DNO_RULES = BASE_RULES


SPEN_11KV_RULES = [
    *BASE_RULES,
    # --- SPEN 11kV: voltage-correct height range ---
    # ENA TS 43-8 / SPEN overhead line policy:
    #   Wood poles: 7m-14m standard for 11kV distribution
    #   Steel poles: 8m-20m
    #   Using 7-20m to cover both materials without per-material branching
    {"check": "range", "field": "height", "min": 7, "max": 20, "structural_only": True},
    # --- Pole ID format ---
    {
        "check": "regex",
        "field": "pole_id",
        "pattern": r"^[A-Za-z0-9][A-Za-z0-9_-]{0,63}$",
        "description": "Pole IDs must be stable identifiers (no spaces or punctuation).",
    },
    # --- Coordinate pair integrity ---
    {
        "check": "paired_required",
        "fields": ["lat", "lon"],
        "description": "Coordinates must be provided as a lat/lon pair.",
    },
    {
        "check": "paired_required",
        "fields": ["easting", "northing"],
        "description": "OSGB coordinates must be provided as an easting/northing pair.",
    },
    # --- SPEN network area coordinate bounds ---
    # SPEN operates in Scotland and NW England - tighter than UK-wide BASE_RULES
    {"check": "range", "field": "lat", "min": 54.5, "max": 60.9},
    {"check": "range", "field": "lon", "min": -6.5, "max": -0.7},
    # --- Material must match declared structure type ---
    {
        "check": "dependent_allowed_values",
        "if_field": "structure_type",
        "then_field": "material",
        "mapping": {
            "Wood Pole": ["Wood"],
            "Steel Pole": ["Steel"],
            "Concrete Pole": ["Concrete"],
            "Composite Pole": ["Composite"],
        },
        "description": "Material must match the declared structure type.",
    },
    # --- Coordinate consistency cross-check ---
    # Converts lat/lon to OSGB27700 and checks against declared easting/northing.
    # Tolerance 100m catches transcription errors and mismatched pole records.
    {
        "check": "coord_consistency",
        "lat_field": "lat",
        "lon_field": "lon",
        "easting_field": "easting",
        "northing_field": "northing",
        "tolerance_m": 100,
        "description": "lat/lon must be consistent with easting/northing within 100m.",
    },
    {
        "check": "unique_pair",
        "fields": ["lat", "lon"],
        "description": "No two poles should share the same lat/lon — likely a duplicate entry.",
    },
    {
        "check": "span_distance",
        "lat_field": "lat",
        "lon_field": "lon",
        "min_m": 10,
        "max_m": 500,
        "description": "Consecutive pole spans must be 10–500m for 11kV distribution.",
    },
]


SSEN_11KV_RULES = [
    *BASE_RULES,
    # --- SSEN 11kV: voltage-correct height range ---
    # ENA TS 43-8 / SSEN overhead line policy (same 11kV class as SPEN):
    #   Wood poles: 7m-14m standard for 11kV distribution
    #   Steel poles: 8m-20m
    #   Using 7-20m to cover both materials without per-material branching
    {"check": "range", "field": "height", "min": 7, "max": 20, "structural_only": True},
    # --- Pole ID format ---
    {
        "check": "regex",
        "field": "pole_id",
        "pattern": r"^[A-Za-z0-9][A-Za-z0-9_-]{0,63}$",
        "description": "Pole IDs must be stable identifiers (no spaces or punctuation).",
    },
    # --- Coordinate pair integrity ---
    {
        "check": "paired_required",
        "fields": ["lat", "lon"],
        "description": "Coordinates must be provided as a lat/lon pair.",
    },
    {
        "check": "paired_required",
        "fields": ["easting", "northing"],
        "description": "OSGB coordinates must be provided as an easting/northing pair.",
    },
    # --- SSEN network area coordinate bounds ---
    # SSEN operates two licence areas:
    #   SEPD (Southern Electric Power Distribution) - southern England
    #     (approx lat 50.0-52.5, lon -5.7 to +1.8)
    #   SHEPD (Scottish Hydro Electric Power Distribution) - northern Scotland
    #     (approx lat 55.8-60.9, lon -7.5 to -1.0)
    # These areas don't overlap geographically. A single bounding box is used
    # here for MVP simplicity - this will pass coordinates in non-SSEN areas
    # between the two licence zones (e.g. Midlands), but still catches grossly
    # wrong coordinates (e.g. mainland Europe). TODO: replace with polygon
    # check for tighter SSEN-territory validation.
    {"check": "range", "field": "lat", "min": 50.0, "max": 60.9},
    {"check": "range", "field": "lon", "min": -7.5, "max": 1.8},
    # --- Material must match declared structure type ---
    {
        "check": "dependent_allowed_values",
        "if_field": "structure_type",
        "then_field": "material",
        "mapping": {
            "Wood Pole": ["Wood"],
            "Steel Pole": ["Steel"],
            "Concrete Pole": ["Concrete"],
            "Composite Pole": ["Composite"],
        },
        "description": "Material must match the declared structure type.",
    },
    # --- Coordinate consistency cross-check ---
    # Converts lat/lon to OSGB27700 and checks against declared easting/northing.
    # Tolerance 100m catches transcription errors and mismatched pole records.
    {
        "check": "coord_consistency",
        "lat_field": "lat",
        "lon_field": "lon",
        "easting_field": "easting",
        "northing_field": "northing",
        "tolerance_m": 100,
        "description": "lat/lon must be consistent with easting/northing within 100m.",
    },
    {
        "check": "unique_pair",
        "fields": ["lat", "lon"],
        "description": "No two poles should share the same lat/lon — likely a duplicate entry.",
    },
    {
        "check": "span_distance",
        "lat_field": "lat",
        "lon_field": "lon",
        "min_m": 10,
        "max_m": 500,
        "description": "Consecutive pole spans must be 10–500m for 11kV distribution.",
    },
]


NIE_11KV_RULES = [
    *BASE_RULES,
    # --- NIE 11kV: voltage-correct height range ---
    # ENA TS 43-8 / NIE Networks overhead line policy (same 11kV class):
    #   Wood poles: 7m-14m standard for 11kV distribution
    #   Steel poles: 8m-20m
    #   Using 7-20m to cover both materials without per-material branching
    {"check": "range", "field": "height", "min": 7, "max": 20, "structural_only": True},
    # --- Pole ID format ---
    {
        "check": "regex",
        "field": "pole_id",
        "pattern": r"^[A-Za-z0-9][A-Za-z0-9_-]{0,63}$",
        "description": "Pole IDs must be stable identifiers (no spaces or punctuation).",
    },
    # --- Coordinate pair integrity ---
    {
        "check": "paired_required",
        "fields": ["lat", "lon"],
        "description": "Coordinates must be provided as a lat/lon pair.",
    },
    {
        "check": "paired_required",
        "fields": ["easting", "northing"],
        "description": "OSGB coordinates must be provided as an easting/northing pair.",
    },
    # --- NIE network area coordinate bounds ---
    # NIE Networks operates exclusively in Northern Ireland.
    # Northern Ireland bounding box: lat 54.0-55.3, lon -8.2 to -5.4
    # This is a single contiguous licence area — no disjoint-zone caveat needed.
    {"check": "range", "field": "lat", "min": 54.0, "max": 55.3},
    {"check": "range", "field": "lon", "min": -8.2, "max": -5.4},
    # --- Material must match declared structure type ---
    {
        "check": "dependent_allowed_values",
        "if_field": "structure_type",
        "then_field": "material",
        "mapping": {
            "Wood Pole": ["Wood"],
            "Steel Pole": ["Steel"],
            "Concrete Pole": ["Concrete"],
            "Composite Pole": ["Composite"],
        },
        "description": "Material must match the declared structure type.",
    },
    # --- Coordinate consistency cross-check ---
    # Converts lat/lon to OSGB27700 and checks against declared easting/northing.
    # Tolerance 100m catches transcription errors and mismatched pole records.
    {
        "check": "coord_consistency",
        "lat_field": "lat",
        "lon_field": "lon",
        "easting_field": "easting",
        "northing_field": "northing",
        "tolerance_m": 100,
        "description": "lat/lon must be consistent with easting/northing within 100m.",
    },
    {
        "check": "unique_pair",
        "fields": ["lat", "lon"],
        "description": "No two poles should share the same lat/lon — likely a duplicate entry.",
    },
    {
        "check": "span_distance",
        "lat_field": "lat",
        "lon_field": "lon",
        "min_m": 10,
        "max_m": 500,
        "description": "Consecutive pole spans must be 10–500m for 11kV distribution.",
    },
]


ENWL_11KV_RULES = [
    *BASE_RULES,
    # ENA TS 43-8 / ENWL 11kV: 7-20m covers wood (7-14m) and steel (8-20m)
    {"check": "range", "field": "height", "min": 7, "max": 20, "structural_only": True},
    {
        "check": "regex",
        "field": "pole_id",
        "pattern": r"^[A-Za-z0-9][A-Za-z0-9_-]{0,63}$",
        "description": "Pole IDs must be stable identifiers (no spaces or punctuation).",
    },
    {
        "check": "paired_required",
        "fields": ["lat", "lon"],
        "description": "Coordinates must be provided as a lat/lon pair.",
    },
    {
        "check": "paired_required",
        "fields": ["easting", "northing"],
        "description": "OSGB coordinates must be provided as an easting/northing pair.",
    },
    # ENWL licence area: Lancashire, Cumbria, Cheshire, Greater Manchester
    {"check": "range", "field": "lat", "min": 53.3, "max": 55.0},
    {"check": "range", "field": "lon", "min": -3.5, "max": -1.8},
    {
        "check": "dependent_allowed_values",
        "if_field": "structure_type",
        "then_field": "material",
        "mapping": {
            "Wood Pole": ["Wood"],
            "Steel Pole": ["Steel"],
            "Concrete Pole": ["Concrete"],
            "Composite Pole": ["Composite"],
        },
        "description": "Material must match the declared structure type.",
    },
    {
        "check": "coord_consistency",
        "lat_field": "lat",
        "lon_field": "lon",
        "easting_field": "easting",
        "northing_field": "northing",
        "tolerance_m": 100,
        "description": "lat/lon must be consistent with easting/northing within 100m.",
    },
    {
        "check": "unique_pair",
        "fields": ["lat", "lon"],
        "description": "No two poles should share the same lat/lon — likely a duplicate entry.",
    },
    {
        "check": "span_distance",
        "lat_field": "lat",
        "lon_field": "lon",
        "min_m": 10,
        "max_m": 500,
        "description": "Consecutive pole spans must be 10–500m for 11kV distribution.",
    },
]


def filter_rules_for_controller(rules: list[dict]) -> list[dict]:
    """
    Remove checks that produce noise rather than signal for raw controller dump
    files. Material is absent from the format; structure_type holds surveyor
    feature codes (Angle, Pol, Hedge) rather than schema values. Per-row
    required checks for height and location are already covered more usefully
    by the completeness summary.
    """
    _noise_keys: frozenset[tuple[str, str | None]] = frozenset(
        {
            ("required", "material"),
            ("required", "height"),
            ("required", "location"),
            ("allowed_values", "material"),
            ("allowed_values", "structure_type"),
        }
    )
    result = []
    for rule in rules:
        check = rule.get("check")
        field = rule.get("field")
        if check == "dependent_allowed_values":
            # All current instances map structure_type → material — meaningless
            # for controller files where material is not a digital field.
            continue
        if (check, field) in _noise_keys:
            continue
        result.append(rule)
    return result


RULEPACKS: dict[str, list[dict]] = {
    "DEFAULT": BASE_RULES,
    "SPEN_11kV": SPEN_11KV_RULES,
    "SSEN_11kV": SSEN_11KV_RULES,
    "NIE_11kV": NIE_11KV_RULES,
    "ENWL_11kV": ENWL_11KV_RULES,
}
