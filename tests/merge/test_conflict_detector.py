"""Tests for ConflictDetector."""

import pytest
from gridflow.baseline.models import BaselinePole, VoltageLevel, AssetType
from gridflow.field.models import FieldPole
from gridflow.merge.conflict_detector import ConflictDetector


@pytest.fixture
def detector():
    return ConflictDetector()


def make_bp(support_no="903203", voltage=VoltageLevel.LV, asset_type=AssetType.POLE) -> BaselinePole:
    return BaselinePole(
        pole_id="P01",
        support_no=support_no,
        easting=354123.0,
        northing=456789.0,
        voltage_level=voltage,
        asset_type=asset_type,
    )


def make_fp(support_no="903203", notes=None, content=None) -> FieldPole:
    return FieldPole(
        folder_name=f"01_SUPPORT_{support_no}_LV",
        support_no=support_no,
        parsed_notes=notes or {"support_no": support_no, "voltage": "LV"},
        notes_content=content or f"Support No: {support_no}\nVoltage: LV",
    )


def test_no_conflict_matching_voltage(detector):
    conflicts = detector.detect(make_bp(voltage=VoltageLevel.LV), make_fp())
    assert "VOLTAGE_CONFLICT" not in conflicts


def test_voltage_conflict_lv_vs_hv(detector):
    fp = make_fp(notes={"support_no": "903203", "voltage": "HV"})
    conflicts = detector.detect(make_bp(voltage=VoltageLevel.LV), fp)
    assert "VOLTAGE_CONFLICT" in conflicts


def test_voltage_conflict_hv_vs_lv(detector):
    fp = make_fp(notes={"support_no": "903203", "voltage": "LV"})
    conflicts = detector.detect(make_bp(voltage=VoltageLevel.HV), fp)
    assert "VOLTAGE_CONFLICT" in conflicts


def test_no_conflict_when_baseline_voltage_unknown(detector):
    fp = make_fp(notes={"support_no": "903203", "voltage": "HV"})
    conflicts = detector.detect(make_bp(voltage=VoltageLevel.UNKNOWN), fp)
    assert "VOLTAGE_CONFLICT" not in conflicts


def test_no_conflict_when_field_voltage_unknown(detector):
    fp = make_fp(notes={"support_no": "903203", "voltage": ""})
    conflicts = detector.detect(make_bp(voltage=VoltageLevel.LV), fp)
    assert "VOLTAGE_CONFLICT" not in conflicts


def test_equipment_conflict_transformer(detector):
    fp = make_fp(
        content="Support No: 903203\nVoltage: LV\nTransformer: Yes\nTransformer: Present",
        notes={
            "support_no": "903203",
            "voltage": "LV",
            "equipment": ["Transformer: Yes"],
        },
    )
    # The content check for "transformer: yes" should trigger
    fp.notes_content = "Support No: 903203\ntransformer: yes"
    conflicts = detector.detect(make_bp(asset_type=AssetType.POLE), fp)
    assert "EQUIPMENT_CONFLICT" in conflicts


def test_no_equipment_conflict_no_transformer(detector):
    fp = make_fp(
        notes={"support_no": "903203", "voltage": "LV", "equipment": ["Warning Signs: Present"]},
        content="Support No: 903203\nTransformer: No",
    )
    fp.notes_content = "Support No: 903203\nTransformer: No"
    conflicts = detector.detect(make_bp(asset_type=AssetType.POLE), fp)
    assert "EQUIPMENT_CONFLICT" not in conflicts


def test_support_no_conflict(detector):
    fp = make_fp(
        support_no="903203",
        notes={"support_no": "999999", "voltage": "LV"},
    )
    conflicts = detector.detect(make_bp(support_no="903203"), fp)
    assert "SUPPORT_NO_CONFLICT" in conflicts


def test_no_support_no_conflict_matching(detector):
    fp = make_fp(notes={"support_no": "903203", "voltage": "LV"})
    conflicts = detector.detect(make_bp(support_no="903203"), fp)
    assert "SUPPORT_NO_CONFLICT" not in conflicts


def test_no_conflict_when_notes_support_absent(detector):
    fp = make_fp(notes={"voltage": "LV"})
    conflicts = detector.detect(make_bp(support_no="903203"), fp)
    assert "SUPPORT_NO_CONFLICT" not in conflicts
