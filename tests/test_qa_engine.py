from __future__ import annotations

import pandas as pd

from app.qa_engine import run_qa_checks


def test_required_treats_blank_string_as_missing() -> None:
    df = pd.DataFrame(
        [
            {"material": "Wood"},
            {"material": ""},
        ]
    )

    rules = [{"check": "required", "field": "material"}]

    issues = run_qa_checks(df, rules)

    assert len(issues) == 1
    assert issues.iloc[0]["Issue"] == "Missing required field: material"


def test_required_treats_whitespace_only_string_as_missing() -> None:
    df = pd.DataFrame(
        [
            {"location": "Dalton Road Junction"},
            {"location": "   "},
        ]
    )

    rules = [{"check": "required", "field": "location"}]

    issues = run_qa_checks(df, rules)

    assert len(issues) == 1
    assert issues.iloc[0]["Issue"] == "Missing required field: location"


def test_range_ignores_non_numeric_values_instead_of_failing_them() -> None:
    df = pd.DataFrame(
        [
            {"height": 11.0},
            {"height": "not-a-number"},
            {"height": 28.0},
        ]
    )

    rules = [{"check": "range", "field": "height", "min": 10, "max": 25}]

    issues = run_qa_checks(df, rules)

    assert len(issues) == 1
    assert issues.iloc[0]["Issue"] == "height out of range (10-25)"
    assert issues.iloc[0]["Row"]["height"] == 28.0


def test_allowed_values_flags_invalid_material() -> None:
    df = pd.DataFrame(
        [
            {"material": "Wood"},
            {"material": "Plastic"},
        ]
    )

    rules = [
        {
            "check": "allowed_values",
            "field": "material",
            "values": ["Wood", "Steel", "Concrete", "Composite"],
        }
    ]

    issues = run_qa_checks(df, rules)

    assert len(issues) == 1
    assert issues.iloc[0]["Issue"] == "Invalid value for 'material': Plastic"


def test_allowed_values_ignores_blank_values_when_required_is_separate() -> None:
    df = pd.DataFrame(
        [
            {"material": ""},
            {"material": "Wood"},
        ]
    )

    rules = [
        {
            "check": "allowed_values",
            "field": "material",
            "values": ["Wood", "Steel", "Concrete", "Composite"],
        }
    ]

    issues = run_qa_checks(df, rules)

    assert len(issues) == 0


def test_nie_11kv_rulepack_is_registered() -> None:
    """NIE_11kV must be registered in RULEPACKS as a non-empty rule list."""
    from app.dno_rules import RULEPACKS

    assert "NIE_11kV" in RULEPACKS
    assert isinstance(RULEPACKS["NIE_11kV"], list)
    assert len(RULEPACKS["NIE_11kV"]) > 0


def test_nie_11kv_rulepack_passes_valid_nie_pole() -> None:
    """A realistic valid NIE pole in Northern Ireland (Belfast) should produce no issues.

    Uses Belfast centre (approx 54.597, -5.930) with OSGB coords derived from
    pyproj: E=146246, N=529526. Tolerance 100m.
    """
    from app.dno_rules import RULEPACKS

    df = pd.DataFrame(
        [
            {
                "pole_id": "NIE-BEL-0001",
                "height": 10.0,
                "material": "Wood",
                "structure_type": "Wood Pole",
                "location": "Belfast Substation Approach",
                "lat": 54.597,
                "lon": -5.930,
                "easting": 146246,
                "northing": 529526,
            }
        ]
    )

    issues = run_qa_checks(df, RULEPACKS["NIE_11kV"])

    assert len(issues) == 0


def test_ssen_11kv_rulepack_is_registered() -> None:
    """SSEN_11kV must be registered in RULEPACKS as a non-empty rule list."""
    from app.dno_rules import RULEPACKS

    assert "SSEN_11kV" in RULEPACKS
    assert isinstance(RULEPACKS["SSEN_11kV"], list)
    assert len(RULEPACKS["SSEN_11kV"]) > 0


def test_ssen_11kv_rulepack_passes_valid_ssen_pole() -> None:
    """A realistic valid SSEN pole in SHEPD (Inverness) should produce no issues.

    Uses Inverness centre (approx 57.477, -4.225) with OSGB coords derived from
    pyproj to match within the 100m coord_consistency tolerance.
    """
    from app.dno_rules import RULEPACKS

    df = pd.DataFrame(
        [
            {
                "pole_id": "SSEN-INV-0001",
                "height": 11.0,
                "material": "Wood",
                "structure_type": "Wood Pole",
                "location": "Inverness Substation Approach",
                "lat": 57.477,
                "lon": -4.225,
                "easting": 266679,
                "northing": 845157,
            }
        ]
    )

    issues = run_qa_checks(df, RULEPACKS["SSEN_11kV"])

    assert len(issues) == 0


def test_missing_column_still_returns_issue() -> None:
    df = pd.DataFrame([{"pole_id": "P-1001"}])

    rules = [{"check": "required", "field": "material"}]

    issues = run_qa_checks(df, rules)

    assert len(issues) == 1
    assert issues.iloc[0]["Issue"] == "Missing column: material"


def test_regex_flags_invalid_format() -> None:
    df = pd.DataFrame([{"pole_id": "P-1001"}, {"pole_id": "P 1002"}])
    rules = [{"check": "regex", "field": "pole_id", "pattern": r"^[A-Za-z0-9_-]+$"}]

    issues = run_qa_checks(df, rules)

    assert len(issues) == 1
    assert issues.iloc[0]["Issue"] == "Invalid format for 'pole_id': P 1002"


def test_paired_required_flags_half_coordinates() -> None:
    df = pd.DataFrame(
        [
            {"lat": 54.5, "lon": -3.0},
            {"lat": 54.5, "lon": None},
            {"lat": None, "lon": -3.0},
            {"lat": None, "lon": None},
        ]
    )
    rules = [{"check": "paired_required", "fields": ["lat", "lon"]}]

    issues = run_qa_checks(df, rules)

    assert len(issues) == 2
    assert "Missing required paired field(s)" in issues.iloc[0]["Issue"]


def test_dependent_allowed_values_flags_inconsistent_material() -> None:
    df = pd.DataFrame(
        [
            {"structure_type": "Wood Pole", "material": "Wood"},
            {"structure_type": "Wood Pole", "material": "Steel"},
        ]
    )
    rules = [
        {
            "check": "dependent_allowed_values",
            "if_field": "structure_type",
            "then_field": "material",
            "mapping": {"Wood Pole": ["Wood"]},
        }
    ]

    issues = run_qa_checks(df, rules)

    assert len(issues) == 1
    assert (
        issues.iloc[0]["Issue"] == "Inconsistent 'material' for 'structure_type=Wood Pole': Steel"
    )


def test_coord_consistency_flags_mismatched_coordinates() -> None:
    """lat/lon pointing to Glasgow but easting/northing pointing to London."""
    df = pd.DataFrame(
        [
            {
                "lat": 55.861,
                "lon": -4.251,
                "easting": 530000,  # London area
                "northing": 180000,  # London area
            }
        ]
    )
    rules = [
        {
            "check": "coord_consistency",
            "lat_field": "lat",
            "lon_field": "lon",
            "easting_field": "easting",
            "northing_field": "northing",
            "tolerance_m": 100,
        }
    ]

    issues = run_qa_checks(df, rules)

    assert len(issues) == 1
    assert "Coordinate mismatch" in issues.iloc[0]["Issue"]


def test_coord_consistency_passes_matching_coordinates() -> None:
    """Glasgow lat/lon with matching OSGB easting/northing — should produce no issues.

    Reference values derived from pyproj EPSG:4326 -> EPSG:27700 transform:
    lat=55.861, lon=-4.251 -> E=259214, N=665382
    """
    df = pd.DataFrame(
        [
            {
                "lat": 55.861,
                "lon": -4.251,
                "easting": 259214,
                "northing": 665382,
            }
        ]
    )
    rules = [
        {
            "check": "coord_consistency",
            "lat_field": "lat",
            "lon_field": "lon",
            "easting_field": "easting",
            "northing_field": "northing",
            "tolerance_m": 100,
        }
    ]

    issues = run_qa_checks(df, rules)

    assert len(issues) == 0
