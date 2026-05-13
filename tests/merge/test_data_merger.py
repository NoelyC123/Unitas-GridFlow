"""Tests for DataMerger."""

import pytest
from gridflow.baseline.models import BaselineDataset, BaselinePole, VoltageLevel, AssetType
from gridflow.field.models import FieldDataset, FieldPole
from gridflow.matching.models import MatchRegister, MatchRegisterEntry
from gridflow.merge import DataMerger


def make_bp(pole_id="P01", support_no="903203", voltage=VoltageLevel.LV) -> BaselinePole:
    return BaselinePole(
        pole_id=pole_id,
        support_no=support_no,
        easting=354123.0,
        northing=456789.0,
        voltage_level=voltage,
        asset_type=AssetType.POLE,
    )


def make_fp(support_no="903203", quality="HIGH", flags=None, notes=None) -> FieldPole:
    return FieldPole(
        folder_name=f"01_SUPPORT_{support_no}_LV",
        support_no=support_no,
        field_photo_count=3,
        map_screenshot_count=1,
        notes_present=True,
        evidence_quality=quality,
        special_flags=flags or [],
        parsed_notes=notes or {"support_no": support_no, "voltage": "LV", "condition": "GOOD"},
        notes_content=f"Support No: {support_no}\nVoltage: LV\nOverall: GOOD",
    )


def make_entry(support_no="903203", confidence="HIGH", folder=None) -> MatchRegisterEntry:
    return MatchRegisterEntry(
        support_no=support_no,
        baseline_pole_id="P01",
        field_folder=folder or f"01_SUPPORT_{support_no}_LV",
        match_confidence=confidence,
        match_type="EXACT",
    )


def make_register(*entries) -> MatchRegister:
    return MatchRegister(
        baseline_total=len(entries),
        field_total=len(entries),
        matched=len(entries),
        entries=list(entries),
    )


@pytest.fixture
def merger():
    return DataMerger()


def test_merge_single_pole_high_confidence(merger):
    baseline = BaselineDataset(poles=[make_bp()])
    field = FieldDataset(
        dataset_path="/t", scan_date="2026",
        poles=[make_fp()], total_poles=1,
    )
    register = make_register(make_entry())

    dataset = merger.merge(baseline, field, register)

    assert dataset.total_matched == 1
    assert len(dataset.poles) == 1
    pole = dataset.poles[0]
    assert pole.support_no == "903203"
    assert pole.match_confidence == "HIGH"
    assert pole.easting == 354123.0


def test_merge_single_pole_medium_confidence(merger):
    baseline = BaselineDataset(poles=[make_bp()])
    field = FieldDataset(
        dataset_path="/t", scan_date="2026",
        poles=[make_fp(quality="MEDIUM", flags=["NO_POLE_POPUP"])],
        total_poles=1,
    )
    register = make_register(make_entry(confidence="MEDIUM"))

    dataset = merger.merge(baseline, field, register)
    pole = dataset.poles[0]
    assert pole.match_confidence == "MEDIUM"
    assert pole.identity_verification_required is True
    assert pole.review_required is True


def test_merge_complete_10_pole_dataset(merger):
    support_nos = ["903203", "903202", "903201A", "903201", "902204",
                   "903101", "903503", "900346", "900347", "902206"]
    bps = [make_bp(f"P{i:02d}", sno) for i, sno in enumerate(support_nos, 1)]
    # Field poles and entries must use identical folder names
    folder_names = [f"{i:02d}_SUPPORT_{sno}_LV" for i, sno in enumerate(support_nos, 1)]
    fps = []
    for sno, folder in zip(support_nos, folder_names):
        fp = make_fp(sno)
        fp.folder_name = folder
        fps.append(fp)
    entries = [
        MatchRegisterEntry(
            support_no=sno,
            baseline_pole_id=f"P{i:02d}",
            field_folder=folder,
            match_confidence="HIGH" if sno != "900346" else "MEDIUM",
            match_type="EXACT",
        )
        for i, (sno, folder) in enumerate(zip(support_nos, folder_names), 1)
    ]

    baseline = BaselineDataset(poles=bps)
    field = FieldDataset(dataset_path="/t", scan_date="2026", poles=fps, total_poles=10)
    register = make_register(*entries)

    dataset = merger.merge(baseline, field, register)
    assert dataset.total_matched == 10
    assert dataset.total_unmatched_baseline == 0
    assert dataset.total_unmatched_field == 0


def test_merge_unmatched_baseline(merger):
    baseline = BaselineDataset(poles=[make_bp("P01", "903203"), make_bp("P02", "999999")])
    field = FieldDataset(
        dataset_path="/t", scan_date="2026",
        poles=[make_fp()], total_poles=1,
    )
    register = make_register(make_entry())

    dataset = merger.merge(baseline, field, register)
    assert len(dataset.unmatched_baseline) == 1
    assert dataset.unmatched_baseline[0]["support_no"] == "999999"


def test_merge_unmatched_field(merger):
    baseline = BaselineDataset(poles=[make_bp()])
    fps = [make_fp("903203"), make_fp("888888")]
    field = FieldDataset(dataset_path="/t", scan_date="2026", poles=fps, total_poles=2)
    register = make_register(make_entry())

    dataset = merger.merge(baseline, field, register)
    assert len(dataset.unmatched_field) == 1
    assert dataset.unmatched_field[0]["support_no"] == "888888"


def test_extract_condition_from_notes(merger):
    fp = make_fp(notes={"condition": "GOOD", "defects": [], "equipment": ["Warning Signs: Present"]})
    fp.notes_content = "Base: Sound, no rot\nTop: Intact\nOverall: GOOD"
    cond = merger._extract_condition(fp)
    assert cond["condition_overall"] == "GOOD"
    assert cond["condition_base"] == "Sound, no rot"


def test_designer_actions_voltage(merger):
    baseline = BaselineDataset(poles=[make_bp(voltage=VoltageLevel.UNKNOWN)])
    field = FieldDataset(
        dataset_path="/t", scan_date="2026",
        poles=[make_fp()], total_poles=1,
    )
    register = make_register(make_entry())
    dataset = merger.merge(baseline, field, register)

    pole = dataset.poles[0]
    assert pole.voltage_verification_required is True
    assert any("voltage" in a.lower() for a in pole.designer_actions)


def test_designer_actions_identity_medium(merger):
    baseline = BaselineDataset(poles=[make_bp()])
    field = FieldDataset(
        dataset_path="/t", scan_date="2026",
        poles=[make_fp(quality="MEDIUM")], total_poles=1,
    )
    register = make_register(make_entry(confidence="MEDIUM"))
    dataset = merger.merge(baseline, field, register)

    pole = dataset.poles[0]
    assert pole.identity_verification_required is True
    assert any("identity" in a.lower() or "confirm" in a.lower() for a in pole.designer_actions)


def test_summary_statistics_correct(merger):
    baseline = BaselineDataset(poles=[make_bp()])
    field = FieldDataset(
        dataset_path="/t", scan_date="2026",
        poles=[make_fp()], total_poles=1,
    )
    register = make_register(make_entry())
    dataset = merger.merge(baseline, field, register)

    assert dataset.total_poles_baseline == 1
    assert dataset.total_poles_field == 1
    assert dataset.total_matched == 1
    assert dataset.design_blocked_count == 1  # Always blocked — no DNO specs
