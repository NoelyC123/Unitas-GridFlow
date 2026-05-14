from gridflow.merge.models import MergedPole
from gridflow.reports import MatchConfidenceReporter


def pole(support_no, confidence="HIGH", **kwargs):
    defaults = {
        "support_no": support_no,
        "match_confidence": confidence,
        "design_ready": False,
        "design_blocked": True,
        "identity_verification_required": confidence != "HIGH",
    }
    defaults.update(kwargs)
    return MergedPole(**defaults)


def test_match_confidence_distribution_sections_and_counts():
    merged_poles = [
        pole("HIGH_001", "HIGH"),
        pole("HIGH_002", "HIGH"),
        pole("MED_001", "MEDIUM"),
        pole("LOW_001", "LOW"),
    ]

    report = MatchConfidenceReporter().generate(merged_poles)

    assert "HIGH Confidence Matches" in report
    assert "**Count:** 2 matches (50%)" in report
    assert "**Count:** 1 match (25%)" in report
    assert "LOW_001" in report
    assert "ACTION REQUIRED" in report


def test_match_confidence_normalization_log_shows_variant_changes():
    merged_poles = [pole("NN SUPPORT 006", "MEDIUM"), pole("NN-SUPPORT-004", "LOW")]

    report = MatchConfidenceReporter().generate(merged_poles)

    assert "Support Number Normalization" in report
    assert "NN SUPPORT 006" in report
    assert "NNSUPPORT006" in report
    assert "NN_SUPPORT_004" in report
    assert "manual identity review is urgent" in report


def test_match_confidence_unmatched_records_are_reported():
    merged_poles = [pole("UNMATCHED_001", "UNMATCHED")]

    report = MatchConfidenceReporter().generate(merged_poles)

    assert "**Unmatched records:** 1" in report
    assert "UNMATCHED_001" in report
    assert "Unmatched records must be resolved" in report


def test_match_confidence_empty_input_is_graceful():
    report = MatchConfidenceReporter().generate([])

    assert "0 matches (0%)" in report
    assert "No merged poles were supplied" in report
