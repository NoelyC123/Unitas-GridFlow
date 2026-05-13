"""Tests for FieldDatasetValidator."""

import pytest

from gridflow.field import FieldDataset, FieldDatasetValidator, FieldPole


@pytest.fixture
def validator():
    return FieldDatasetValidator()


def make_dataset(poles) -> FieldDataset:
    return FieldDataset(
        dataset_path="/test",
        scan_date="2026-01-01",
        total_poles=len(poles),
        poles=poles,
    )


def make_pole(**kwargs) -> FieldPole:
    defaults = dict(
        folder_name="01_SUPPORT_903203_LV_TERMINAL",
        support_no="903203",
        field_photo_count=3,
        map_screenshot_count=1,
        notes_present=True,
        notes_content="Support No: 903203\nVoltage: LV",
        parsed_notes={"support_no": "903203", "voltage": "LV"},
        special_flags=[],
    )
    defaults.update(kwargs)
    return FieldPole(**defaults)


def test_validate_compliant(validator):
    poles = [make_pole(), make_pole(folder_name="02_SUPPORT_903202_LV", support_no="903202")]
    dataset = make_dataset(poles)
    report = validator.validate(dataset)
    assert report.is_valid
    assert report.error_count == 0


def test_validate_empty_dataset(validator):
    dataset = make_dataset([])
    report = validator.validate(dataset)
    assert report.total_poles == 0
    assert len(report.warnings) > 0


def test_detect_insufficient_photos(validator):
    poles = [make_pole(field_photo_count=1)]
    report = validator.validate(make_dataset(poles))
    assert any(i.field == "field_photo_count" for i in report.issues)


def test_detect_missing_notes(validator):
    poles = [make_pole(notes_present=False, parsed_notes={})]
    report = validator.validate(make_dataset(poles))
    assert any(i.field == "notes_present" for i in report.issues)


def test_detect_duplicate_support_numbers(validator):
    poles = [
        make_pole(folder_name="01_SUPPORT_903203_LV", support_no="903203"),
        make_pole(folder_name="02_SUPPORT_903203_HV", support_no="903203"),
    ]
    report = validator.validate(make_dataset(poles))
    assert any(i.issue_type == "DUPLICATE" for i in report.issues)


def test_detect_bad_naming(validator):
    bad_pole = make_pole(folder_name="BAD_FOLDER_NAME", support_no="UNKNOWN")
    report = validator.validate(make_dataset([bad_pole]))
    assert any(i.field == "folder_name" for i in report.issues)


def test_alphabetic_support_number_from_partial_folder_warns(validator):
    """Alphabetic-only support identity is represented as UNKNOWN and warned."""
    pole = make_pole(
        folder_name="01_SUPPORT_ALPHA_LV",
        support_no="UNKNOWN",
        parsed_notes={"support_no": None},
    )

    report = validator.validate(make_dataset([pole]))

    assert report.warning_count >= 1
    assert any(i.field == "parsed_notes.support_no" for i in report.issues)


def test_all_poles_duplicate_unknown_support_numbers(validator):
    """Duplicate UNKNOWN support numbers should be visible to reviewers."""
    poles = [
        make_pole(folder_name="01_SUPPORT_ALPHA_LV", support_no="UNKNOWN"),
        make_pole(folder_name="02_SUPPORT_BETA_LV", support_no="UNKNOWN"),
    ]

    report = validator.validate(make_dataset(poles))

    assert any(i.issue_type == "DUPLICATE" for i in report.issues)
