"""Tests for RegisterBuilder."""

import csv

import pytest

from gridflow.baseline.models import BaselineDataset, BaselinePole
from gridflow.field.models import FieldDataset, FieldPole
from gridflow.matching import RegisterBuilder
from gridflow.matching.models import MatchResult


@pytest.fixture
def builder():
    return RegisterBuilder()


def make_bp(pole_id="P01", support_no="903203") -> BaselinePole:
    return BaselinePole(
        pole_id=pole_id,
        support_no=support_no,
        easting=354123.0,
        northing=456789.0,
    )


def make_fp(folder="01_SUPPORT_903203_LV", support_no="903203") -> FieldPole:
    return FieldPole(folder_name=folder, support_no=support_no)


def make_mr(support_no="903203", match_type="EXACT", folder="01_SUPPORT_903203_LV") -> MatchResult:
    return MatchResult(
        baseline_pole_id="P01",
        baseline_support_no=support_no,
        field_folder=folder,
        field_support_no=support_no,
        match_type=match_type,
        match_confidence="HIGH" if match_type == "EXACT" else "UNMATCHED",
    )


def test_build_complete_register(builder):
    baseline = BaselineDataset(poles=[make_bp()])
    field = FieldDataset(
        dataset_path="/t",
        scan_date="2026",
        poles=[make_fp()],
        total_poles=1,
    )
    match_results = [make_mr()]

    register = builder.build(match_results, baseline, field)
    assert register.baseline_total == 1
    assert register.field_total == 1
    assert register.matched == 1
    assert register.unmatched_baseline == 0


def test_match_rate_calculation(builder):
    baseline = BaselineDataset(poles=[make_bp("P01", "903203"), make_bp("P02", "903202")])
    field = FieldDataset(
        dataset_path="/t",
        scan_date="2026",
        poles=[make_fp()],
        total_poles=1,
    )
    match_results = [
        make_mr("903203", "EXACT"),
        MatchResult(
            baseline_pole_id="P02",
            baseline_support_no="903202",
            match_type="UNMATCHED",
            match_confidence="UNMATCHED",
        ),
    ]
    register = builder.build(match_results, baseline, field)
    assert register.match_rate == pytest.approx(50.0)
    assert register.matched == 1
    assert register.unmatched_baseline == 1


def test_unmatched_poles_in_register(builder):
    baseline = BaselineDataset(poles=[make_bp()])
    field = FieldDataset(
        dataset_path="/t",
        scan_date="2026",
        poles=[make_fp("99_SUPPORT_888888_HV", "888888")],
        total_poles=1,
    )
    match_results = [
        MatchResult(
            baseline_pole_id="P01",
            baseline_support_no="903203",
            match_type="UNMATCHED",
            match_confidence="UNMATCHED",
        )
    ]
    register = builder.build(match_results, baseline, field)
    assert register.unmatched_field == 1
    assert register.unmatched_baseline == 1


def test_match_rate_excludes_extra_field_entries(builder):
    """EXTRA_FIELD poles must not inflate the match rate (Stage 5F regression)."""
    # 10 baseline poles, 9 matched, 1 baseline UNMATCHED (blank name), 1 field EXTRA
    baseline = BaselineDataset(poles=[make_bp(f"P{i:02d}", f"90320{i}") for i in range(10)])
    field = FieldDataset(
        dataset_path="/t",
        scan_date="2026",
        poles=[make_fp(f"0{i + 1}_SUPPORT_90320{i}_LV", f"90320{i}") for i in range(9)]
        + [make_fp("10_SUPPORT_902204_HV", "902204")],
        total_poles=10,
    )
    match_results = [
        make_mr(f"90320{i}", "EXACT", f"0{i + 1}_SUPPORT_90320{i}_LV") for i in range(9)
    ] + [
        MatchResult(
            baseline_pole_id="P09",
            baseline_support_no="",  # blank — like Trimble row with no Point Name
            match_type="UNMATCHED",
            match_confidence="UNMATCHED",
        )
    ]
    register = builder.build(match_results, baseline, field)

    assert register.matched == 9
    assert register.unmatched_baseline == 1
    assert register.unmatched_field == 1
    assert register.match_rate == pytest.approx(90.0)


def test_compute_stats_extra_field_not_counted_as_matched():
    """compute_stats must exclude EXTRA_FIELD from matched count."""
    from gridflow.matching.models import MatchRegister, MatchRegisterEntry

    reg = MatchRegister(baseline_total=10, field_total=10)
    reg.entries = [
        MatchRegisterEntry(support_no="A", match_type="EXACT", match_confidence="HIGH"),
        MatchRegisterEntry(support_no="B", match_type="EXACT", match_confidence="HIGH"),
        MatchRegisterEntry(support_no="C", match_type="UNMATCHED", match_confidence="UNMATCHED"),
        MatchRegisterEntry(support_no="D", match_type="EXTRA_FIELD", match_confidence="UNMATCHED"),
    ]
    reg.compute_stats()

    assert reg.matched == 2  # EXACT only, not EXTRA_FIELD
    assert reg.match_rate == pytest.approx(20.0)  # 2/10


def test_export_csv(builder, tmp_path):
    baseline = BaselineDataset(poles=[make_bp()])
    field = FieldDataset(
        dataset_path="/t",
        scan_date="2026",
        poles=[make_fp()],
        total_poles=1,
    )
    match_results = [make_mr()]
    register = builder.build(match_results, baseline, field)

    csv_path = tmp_path / "register.csv"
    builder.export_csv(register, csv_path)

    assert csv_path.exists()
    with open(csv_path) as f:
        rows = list(csv.DictReader(f))
    assert len(rows) == 1
    assert rows[0]["support_no"] == "903203"
    assert rows[0]["match_confidence"] == "HIGH"


def test_duplicate_support_numbers_preserved_in_register(builder):
    """Duplicate baseline support numbers should remain visible in register output."""
    baseline = BaselineDataset(poles=[make_bp("P01", "903203"), make_bp("P02", "903203")])
    field = FieldDataset(
        dataset_path="/t",
        scan_date="2026",
        poles=[make_fp()],
        total_poles=1,
    )
    match_results = [
        make_mr("903203", "EXACT"),
        MatchResult(
            baseline_pole_id="P02",
            baseline_support_no="903203",
            match_type="UNMATCHED",
            match_confidence="UNMATCHED",
        ),
    ]

    register = builder.build(match_results, baseline, field)

    entries_for_support = [e for e in register.entries if e.support_no == "903203"]
    assert len(entries_for_support) == 2
    assert register.unmatched_baseline == 1


def test_empty_register_build(builder):
    """Empty source datasets should produce an empty register without error."""
    register = builder.build(
        [],
        BaselineDataset(poles=[]),
        FieldDataset(dataset_path="/t", scan_date="2026", total_poles=0, poles=[]),
    )

    assert register.baseline_total == 0
    assert register.field_total == 0
    assert register.entries == []
    assert register.match_rate == 0.0
