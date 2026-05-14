from gridflow.merge.models import MergedPole
from gridflow.reports import VerificationFlagsReporter


def pole(support_no, **kwargs):
    defaults = {
        "support_no": support_no,
        "design_ready": False,
        "design_blocked": True,
        "conductor_verification_required": False,
        "pole_class_verification_required": False,
        "voltage_verification_required": False,
        "identity_verification_required": False,
        "condition_verification_required": False,
    }
    defaults.update(kwargs)
    return MergedPole(**defaults)


def test_verification_flags_all_types_are_parsed():
    merged_poles = [
        pole(
            "SUPPORT_001",
            conductor_verification_required=True,
            pole_class_verification_required=True,
            voltage_verification_required=True,
            identity_verification_required=True,
            condition_verification_required=True,
            conflict_flags=["EQUIPMENT_CONFLICT"],
        )
    ]

    report = VerificationFlagsReporter().generate(merged_poles)

    assert "conductor_spec_missing" in report
    assert "pole_class_missing" in report
    assert "voltage_conflict" in report
    assert "identity_confirmation_required" in report
    assert "equipment_conflict" in report
    assert "condition_verification_required" in report
    assert "| SUPPORT_001 | 6 |" in report


def test_verification_flags_standards_references_present():
    report = VerificationFlagsReporter().generate(
        [
            pole(
                "SUPPORT_001",
                conductor_verification_required=True,
                voltage_verification_required=True,
            )
        ]
    )

    assert "ENA G7/4" in report
    assert "ESQCR 2002" in report
    assert "BS EN 50341-1" in report


def test_verification_flags_empty_input_is_graceful():
    report = VerificationFlagsReporter().generate([])

    assert "Total poles with flags:** 0" in report
    assert "No verification flags were raised" in report
    assert "Recommended Resolution Priority" in report


def test_verification_flags_counts_by_flag_type():
    merged_poles = [
        pole("SUPPORT_001", conductor_verification_required=True),
        pole("SUPPORT_002", conductor_verification_required=True),
        pole("SUPPORT_003", pole_class_verification_required=True),
    ]

    report = VerificationFlagsReporter().generate(merged_poles)

    assert "**Count:** 2 poles affected" in report
    assert "**Count:** 1 poles affected" in report
    assert "Missing conductor specification: 2 poles" in report
    assert "Missing pole class: 1 poles" in report
