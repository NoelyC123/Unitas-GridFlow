from gridflow.merge.models import MergedPole
from gridflow.reports import EvidenceProvenanceReporter


def pole(support_no, **kwargs):
    defaults = {
        "support_no": support_no,
        "match_confidence": "HIGH",
        "match_type": "EXACT",
        "latitude": 54.1,
        "longitude": -2.9,
        "baseline_voltage": "LV",
        "field_photo_count": 3,
        "notes_content": "notes",
        "equipment_observed": ["streetlight"],
        "conductor_verification_required": True,
        "pole_class_verification_required": True,
        "design_ready": False,
        "design_blocked": True,
    }
    defaults.update(kwargs)
    return MergedPole(**defaults)


def test_provenance_per_pole_traces_sources():
    report = EvidenceProvenanceReporter().generate([pole("SUPPORT_001")])

    assert "Pole SUPPORT_001" in report
    assert "Baseline / match register" in report
    assert "Field survey" in report
    assert "DNO data required" in report
    assert "streetlight" in report


def test_provenance_summary_stats_include_gap_analysis():
    report = EvidenceProvenanceReporter().generate(
        [
            pole("SUPPORT_001"),
            pole("SUPPORT_002", field_photo_count=0, notes_content=None, equipment_observed=[]),
        ]
    )

    assert "Summary Statistics" in report
    assert "Conductor spec:** Missing for 2/2 poles" in report
    assert "Photo evidence captured for 1/2 poles" in report
    assert "Overall quality" in report


def test_provenance_empty_input_is_graceful():
    report = EvidenceProvenanceReporter().generate([])

    assert "No merged poles were supplied" in report
    assert "Summary Statistics" in report
    assert "Overall quality:** NO DATA" in report


def test_provenance_visual_indicators_present():
    report = EvidenceProvenanceReporter().generate([pole("SUPPORT_001")])

    assert "✅" in report
    assert "⚠️" in report
    assert "❌" in report
