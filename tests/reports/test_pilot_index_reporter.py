from gridflow.merge.models import MergedPole
from gridflow.reports import PilotIndexReporter


def pole(support_no, ready=False, confidence="HIGH", **kwargs):
    blocked = not ready
    defaults = {
        "support_no": support_no,
        "design_ready": ready,
        "design_blocked": blocked,
        "match_confidence": confidence,
        "field_photo_count": 3,
        "notes_content": "notes",
        "conductor_verification_required": blocked,
        "pole_class_verification_required": blocked,
        "voltage_verification_required": False,
        "identity_verification_required": confidence != "HIGH",
    }
    defaults.update(kwargs)
    return MergedPole(**defaults)


def test_pilot_index_all_blocked_decision_explains_dno_gap():
    merged_poles = [pole(f"SUPPORT_{i:03d}") for i in range(1, 6)]

    report = PilotIndexReporter().generate(merged_poles)

    assert "NOT READY FOR DESIGN" in report
    assert "Design blocked pending DNO engineering data" in report
    assert "This is NOT a pipeline failure" in report
    assert "Missing conductor specification" in report
    assert "05_qa_report.md" in report
    assert "10_evidence_provenance_log.md" in report


def test_pilot_index_all_ready_decision_lists_ready_poles():
    merged_poles = [
        pole(
            f"READY_{i:03d}",
            ready=True,
            conductor_verification_required=False,
            pole_class_verification_required=False,
        )
        for i in range(1, 4)
    ]

    report = PilotIndexReporter().generate(merged_poles)

    assert "DESIGN-READY" in report
    assert "READY FOR DESIGN (3 poles)" in report
    assert "READY_001, READY_002, READY_003" in report


def test_pilot_index_partial_ready_counts_are_correct():
    merged_poles = [
        pole(
            "READY_001",
            ready=True,
            conductor_verification_required=False,
            pole_class_verification_required=False,
        ),
        pole("BLOCKED_001", confidence="MEDIUM"),
        pole("BLOCKED_002", confidence="LOW"),
    ]

    report = PilotIndexReporter().generate(merged_poles)

    assert "PARTIAL READINESS (1 ready, 2 blocked)" in report
    assert "| Design-ready poles | 1 (33%) |" in report
    assert "| Design-blocked poles | 2 (67%) |" in report
    assert "LOW: 1 matches (33%)" in report


def test_pilot_index_visual_indicators_are_present():
    report = PilotIndexReporter().generate([pole("SUPPORT_001", confidence="LOW")])

    assert "✅" in report
    assert "⚠️" in report
    assert "❌" in report or "NOT READY" in report
    assert "ℹ️" in report
