"""Tests for NotesParser."""

import pytest

from gridflow.field import NotesParser

SAMPLE_NOTES = """POLE IDENTITY
Support No: 903203
Type: TIMBER
Voltage: LV

LOCATION
Grid Ref: SD 54123 56789
Access: Roadside public highway

CONDITION
Overall: GOOD
Base: Sound, no rot visible

EQUIPMENT OBSERVED
Warning Signs: Present - LV warning triangle
Transformer: No
Stay: No

DEFECTS
None observed

VERIFICATION REQUIRED
voltage_verification_required
conductor_verification_required
pole_class_verification_required"""


@pytest.fixture
def parser():
    return NotesParser()


def test_parse_support_no(parser):
    result = parser.parse(SAMPLE_NOTES)
    assert result["support_no"] == "903203"


def test_parse_voltage(parser):
    result = parser.parse(SAMPLE_NOTES)
    assert result["voltage"] == "LV"


def test_parse_condition(parser):
    result = parser.parse(SAMPLE_NOTES)
    assert result["condition"] == "GOOD"


def test_parse_access(parser):
    result = parser.parse(SAMPLE_NOTES)
    assert result["access"] == "Roadside public highway"


def test_parse_equipment(parser):
    result = parser.parse(SAMPLE_NOTES)
    assert len(result["equipment"]) >= 1
    equipment_str = " ".join(result["equipment"])
    assert "Warning Signs" in equipment_str


def test_parse_defects_empty(parser):
    result = parser.parse(SAMPLE_NOTES)
    # "None observed" should not be added to defects
    assert len(result["defects"]) == 0


def test_parse_verification_flags(parser):
    result = parser.parse(SAMPLE_NOTES)
    assert "voltage_verification_required" in result["verification_flags"]
    assert "conductor_verification_required" in result["verification_flags"]
    assert "pole_class_verification_required" in result["verification_flags"]


def test_parse_empty_notes(parser):
    result = parser.parse("")
    assert result["support_no"] is None
    assert result["voltage"] is None
    assert result["equipment"] == []
    assert result["free_text"] == ""


def test_parse_none_notes(parser):
    result = parser.parse(None)
    assert result["support_no"] is None


def test_parse_freetext_notes(parser):
    notes = "This is a free text note without any structured sections."
    result = parser.parse(notes)
    assert result["support_no"] is None
    assert "free text note" in result["free_text"]


def test_parse_partial_notes(parser):
    partial = "Support No: 903203\nVoltage: HV"
    result = parser.parse(partial)
    assert result["support_no"] == "903203"
    assert result["voltage"] == "HV"
