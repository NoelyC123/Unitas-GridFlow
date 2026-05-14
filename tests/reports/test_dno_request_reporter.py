from gridflow.merge.models import MergedPole
from gridflow.reports import DNORequestReporter


def pole(support_no, ready=False, confidence="HIGH", **kwargs):
    blocked = not ready
    defaults = {
        "support_no": support_no,
        "design_ready": ready,
        "design_blocked": blocked,
        "match_confidence": confidence,
        "voltage_verification_required": blocked,
        "conductor_verification_required": blocked,
        "pole_class_verification_required": blocked,
        "identity_verification_required": confidence != "HIGH",
    }
    defaults.update(kwargs)
    return MergedPole(**defaults)


def test_dno_request_all_poles_blocked_groups_critical_and_high_counts():
    merged_poles = [
        pole(f"NN_SUPPORT_00{i}", confidence="LOW" if i <= 4 else "HIGH") for i in range(1, 11)
    ]

    report = DNORequestReporter().generate(merged_poles)

    assert len(report) > 500
    assert "DNO Data Request" in report
    assert "CRITICAL PRIORITY - Missing Conductor Specification" in report
    assert "CRITICAL PRIORITY - Missing Pole Class" in report
    assert "HIGH PRIORITY - Voltage Conflicts" in report
    assert "HIGH PRIORITY - Identity Confirmation Required" in report
    assert "10 of 10 poles" in report
    assert "DNO data gaps from pipeline failure" in report
    for i in range(1, 11):
        assert f"NN_SUPPORT_00{i}" in report


def test_dno_request_no_blockers_reports_design_ready_state():
    merged_poles = [
        pole(
            f"READY_00{i}",
            ready=True,
            voltage_verification_required=False,
            conductor_verification_required=False,
            pole_class_verification_required=False,
        )
        for i in range(1, 6)
    ]

    report = DNORequestReporter().generate(merged_poles)

    assert "0 poles require DNO engineering data" in report
    assert "No DNO Request Blockers" in report
    assert "Missing Conductor Specification" not in report


def test_dno_request_partial_blockers_excludes_ready_from_blocker_lists():
    merged_poles = [
        pole(
            "READY_001",
            ready=True,
            voltage_verification_required=False,
            conductor_verification_required=False,
            pole_class_verification_required=False,
        ),
        pole(
            "BLOCKED_001",
            conductor_verification_required=True,
            pole_class_verification_required=False,
        ),
        pole(
            "BLOCKED_002",
            conductor_verification_required=False,
            pole_class_verification_required=True,
        ),
    ]

    report = DNORequestReporter().generate(merged_poles)

    assert "BLOCKED_001" in report
    assert "BLOCKED_002" in report
    conductor_section = report.split("CRITICAL PRIORITY - Missing Conductor Specification", 1)[1]
    conductor_section = conductor_section.split("##", 1)[0]
    assert "READY_001" not in conductor_section


def test_dno_request_empty_input_is_graceful():
    report = DNORequestReporter().generate([])

    assert "No merged poles were supplied" in report
    assert "Next Steps" in report
