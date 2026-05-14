from gridflow.merge.models import MergedPole
from gridflow.reports import DesignReadinessReporter


def pole(support_no, ready=False, confidence="HIGH", photos=3, notes="notes", **kwargs):
    blocked = not ready
    defaults = {
        "support_no": support_no,
        "design_ready": ready,
        "design_blocked": blocked,
        "match_confidence": confidence,
        "field_photo_count": photos,
        "notes_content": notes,
        "voltage_verification_required": blocked,
        "conductor_verification_required": blocked,
        "pole_class_verification_required": blocked,
        "identity_verification_required": confidence != "HIGH",
    }
    defaults.update(kwargs)
    return MergedPole(**defaults)


def test_design_readiness_all_blocked_explains_dno_data_not_pipeline_failure():
    merged_poles = [pole(f"NN_SUPPORT_00{i}") for i in range(1, 11)]

    report = DesignReadinessReporter().generate(merged_poles)

    assert "DESIGN-BLOCKED (DNO Data Required)" in report
    assert "**Design-ready poles:** 0 (0%)" in report
    assert "**Design-blocked poles:** 10 (100%)" in report
    assert "not a survey failure or pipeline error" in report
    assert "Missing conductor specification" in report
    assert "Missing pole class" in report


def test_design_readiness_all_ready_reports_design_ready():
    merged_poles = [
        pole(
            f"READY_00{i}",
            ready=True,
            voltage_verification_required=False,
            conductor_verification_required=False,
            pole_class_verification_required=False,
        )
        for i in range(1, 4)
    ]

    report = DesignReadinessReporter().generate(merged_poles)

    assert "DESIGN-READY" in report
    assert "**Design-ready poles:** 3 (100%)" in report
    assert "No design blockers were raised" in report


def test_design_readiness_mixed_counts_are_mathematically_correct():
    merged_poles = [
        pole(
            "READY_001",
            ready=True,
            voltage_verification_required=False,
            conductor_verification_required=False,
            pole_class_verification_required=False,
        ),
        pole("BLOCKED_001", ready=False),
        pole("BLOCKED_002", ready=False, confidence="MEDIUM"),
        pole("LOW_001", ready=False, confidence="LOW", photos=1, notes=None),
    ]

    report = DesignReadinessReporter().generate(merged_poles)

    assert "PARTIALLY READY" in report
    assert "**Design-ready poles:** 1 (25%)" in report
    assert "**Design-blocked poles:** 3 (75%)" in report
    assert "**LOW quality:** 1 pole (25%)" in report
    assert "**MEDIUM confidence:** 1 match (25%)" in report
    assert "**LOW confidence:** 1 match (25%)" in report


def test_design_readiness_empty_input_is_graceful():
    report = DesignReadinessReporter().generate([])

    assert "NO DATA" in report
    assert "No merged poles were supplied" in report
