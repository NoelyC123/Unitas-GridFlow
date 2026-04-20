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
