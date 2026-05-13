"""Tests for VerificationFlagGenerator."""

import pytest
from gridflow.merge.models import MergedPole
from gridflow.merge.verification_flag_generator import VerificationFlagGenerator


@pytest.fixture
def gen():
    return VerificationFlagGenerator()


def make_pole(**kwargs) -> MergedPole:
    defaults = dict(
        support_no="903203",
        match_confidence="HIGH",
        defects=[],
        equipment_observed=[],
        conflict_flags=[],
    )
    defaults.update(kwargs)
    return MergedPole(**defaults)


def test_voltage_flag_when_baseline_null(gen):
    pole = make_pole(baseline_voltage=None)
    pole = gen.generate_flags(pole)
    assert pole.voltage_verification_required is True


def test_voltage_flag_when_baseline_unknown(gen):
    pole = make_pole(baseline_voltage="UNKNOWN")
    pole = gen.generate_flags(pole)
    assert pole.voltage_verification_required is True


def test_voltage_flag_when_baseline_known(gen):
    pole = make_pole(baseline_voltage="LV")
    pole = gen.generate_flags(pole)
    assert pole.voltage_verification_required is False


def test_conductor_flag_always_true(gen):
    pole = make_pole()
    pole = gen.generate_flags(pole)
    assert pole.conductor_verification_required is True


def test_pole_class_flag_always_true(gen):
    pole = make_pole()
    pole = gen.generate_flags(pole)
    assert pole.pole_class_verification_required is True


def test_condition_flag_no_defects(gen):
    pole = make_pole(defects=[])
    pole = gen.generate_flags(pole)
    assert pole.condition_verification_required is False


def test_condition_flag_severe_defects(gen):
    pole = make_pole(defects=["Severe rot at base — urgent"])
    pole = gen.generate_flags(pole)
    assert pole.condition_verification_required is True


def test_condition_flag_minor_defects(gen):
    pole = make_pole(defects=["Paint worn", "Minor surface rust"])
    pole = gen.generate_flags(pole)
    assert pole.condition_verification_required is False


def test_identity_flag_high_confidence(gen):
    pole = make_pole(match_confidence="HIGH")
    pole = gen.generate_flags(pole)
    assert pole.identity_verification_required is False


def test_identity_flag_medium_confidence(gen):
    pole = make_pole(match_confidence="MEDIUM")
    pole = gen.generate_flags(pole)
    assert pole.identity_verification_required is True


def test_identity_flag_unmatched(gen):
    pole = make_pole(match_confidence="UNMATCHED")
    pole = gen.generate_flags(pole)
    assert pole.identity_verification_required is True


def test_equipment_conflict_flag(gen):
    pole = make_pole(conflict_flags=["EQUIPMENT_CONFLICT"])
    pole = gen.generate_flags(pole)
    assert pole.equipment_conflict_flag is True


def test_voltage_conflict_sets_equipment_flag(gen):
    pole = make_pole(conflict_flags=["VOLTAGE_CONFLICT"])
    pole = gen.generate_flags(pole)
    assert pole.equipment_conflict_flag is True


def test_design_blocked_any_flag(gen):
    # Always blocked because conductor + pole_class always true
    pole = make_pole(match_confidence="HIGH", baseline_voltage="LV")
    pole = gen.generate_flags(pole)
    assert pole.design_blocked is True  # conductor/pole_class are always True


def test_design_ready_all_clear_theoretical(gen):
    """design_ready would be True only if all flags were False — not possible in practice."""
    # Manually bypass to test the logic
    pole = make_pole(match_confidence="HIGH")
    pole.conductor_verification_required = False
    pole.pole_class_verification_required = False
    pole.voltage_verification_required = False
    pole.identity_verification_required = False
    pole.condition_verification_required = False
    pole.equipment_conflict_flag = False
    blocked, ready = gen._compute_design_status(pole)
    assert ready is True


def test_designer_actions_populated(gen):
    pole = make_pole(match_confidence="HIGH", baseline_voltage="LV")
    pole = gen.generate_flags(pole)
    # Should have at least conductor and pole_class actions
    assert len(pole.designer_actions) >= 2
    actions_str = " ".join(pole.designer_actions).lower()
    assert "conductor" in actions_str
    assert "pole class" in actions_str
