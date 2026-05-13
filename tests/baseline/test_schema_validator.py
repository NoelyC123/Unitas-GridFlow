"""Tests for schema validator."""

import pytest

from gridflow.baseline import (
    BaselineDataset,
    BaselinePole,
    SchemaValidator,
    VoltageLevel,
)


@pytest.fixture
def validator():
    """Return validator instance."""
    return SchemaValidator()


@pytest.fixture
def valid_dataset():
    """Return valid dataset."""
    poles = [
        BaselinePole(
            pole_id=f"POLE_{i:03d}",
            support_no=f"{900000 + i}",
            easting=354123.45 + (i * 100),
            northing=456789.12 + (i * 100),
            voltage_level=VoltageLevel.LV,
        )
        for i in range(5)
    ]
    return BaselineDataset(poles=poles)


def test_validate_valid_dataset(validator, valid_dataset):
    """Test validation of valid dataset."""
    report = validator.validate_dataset(valid_dataset)

    assert report.total_poles == 5
    assert report.valid_poles == 5
    assert report.is_valid
    assert report.error_count == 0


def test_detect_missing_support_numbers(validator):
    """Test detection of missing support numbers."""
    poles = [
        BaselinePole(
            pole_id="POLE_001",
            support_no=None,
            easting=354123.45,
            northing=456789.12,
        ),
    ]
    dataset = BaselineDataset(poles=poles)
    report = validator.validate_dataset(dataset)

    assert report.warning_count > 0
    assert any(issue.issue_type == "MISSING" for issue in report.issues)


def test_detect_invalid_coordinates(validator):
    """Test detection of out-of-bounds coordinates."""
    import pytest
    from pydantic import ValidationError

    # Pydantic will catch invalid coordinates during construction
    with pytest.raises(ValidationError):
        BaselinePole(
            pole_id="POLE_001",
            support_no="903203",
            easting=999999.0,  # Out of bounds
            northing=456789.12,
        )


def test_detect_duplicate_pole_ids(validator):
    """Test detection of duplicate pole IDs."""
    poles = [
        BaselinePole(
            pole_id="POLE_001",
            support_no="903203",
            easting=354123.45,
            northing=456789.12,
        ),
        BaselinePole(
            pole_id="POLE_001",  # Duplicate
            support_no="903204",
            easting=354234.56,
            northing=456890.23,
        ),
    ]
    dataset = BaselineDataset(poles=poles)
    report = validator.validate_dataset(dataset)

    assert report.error_count > 0
    assert any(issue.issue_type == "DUPLICATE" for issue in report.issues)


def test_validate_empty_baseline_dataset(validator):
    """Empty baseline datasets should return a warning-only report."""
    report = validator.validate_dataset(BaselineDataset(poles=[]))

    assert report.total_poles == 0
    assert report.valid_poles == 0
    assert report.error_count == 0
    assert "Dataset is empty" in report.warnings


def test_detect_all_poles_duplicate_support_numbers(validator):
    """If every pole shares a support_no, duplicate support warnings are emitted."""
    poles = [
        BaselinePole(
            pole_id=f"POLE_{i}",
            support_no="903203",
            easting=354123.45 + i,
            northing=456789.12 + i,
        )
        for i in range(3)
    ]
    report = validator.validate_dataset(BaselineDataset(poles=poles))

    duplicate_issues = [
        issue for issue in report.issues if issue.field == "support_no" and issue.issue_type == "DUPLICATE"
    ]
    assert duplicate_issues
    assert report.warning_count >= 1
    assert report.is_valid
