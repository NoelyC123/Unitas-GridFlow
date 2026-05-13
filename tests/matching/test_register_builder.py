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
