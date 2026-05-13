"""Tests for QAReportGenerator."""

import csv
import pytest
from pathlib import Path
from gridflow.merge.models import MergedDataset, MergedPole
from gridflow.merge.qa_report_generator import QAReportGenerator


@pytest.fixture
def reporter():
    return QAReportGenerator()


def make_pole(support_no="903203", confidence="HIGH", blocked=True, **kwargs) -> MergedPole:
    pole = MergedPole(
        support_no=support_no,
        match_confidence=confidence,
        design_blocked=blocked,
        design_ready=not blocked,
        designer_actions=[
            "Obtain DNO-certified voltage specification",
            "Obtain DNO conductor specification (size, type, material)",
            "Obtain DNO pole class and strength rating",
        ],
        **kwargs,
    )
    return pole


def make_dataset(poles=None) -> MergedDataset:
    poles = poles or [make_pole("903203"), make_pole("903202")]
    d = MergedDataset(
        baseline_source="enwl_sample.csv",
        field_source="/test/field",
        merge_date="2026-05-13",
        total_poles_baseline=len(poles),
        total_poles_field=len(poles),
        total_matched=len(poles),
        design_blocked_count=sum(1 for p in poles if p.design_blocked),
        high_confidence_count=sum(1 for p in poles if p.match_confidence == "HIGH"),
        poles=poles,
    )
    return d


def test_report_has_executive_summary(reporter):
    report = reporter.generate(make_dataset())
    assert "Executive Summary" in report
    assert "Merge Date" in report
    assert "Match Rate" in report


def test_report_has_confidence_table(reporter):
    report = reporter.generate(make_dataset())
    assert "Match Confidence Distribution" in report
    assert "HIGH" in report


def test_report_has_verification_summary(reporter):
    report = reporter.generate(make_dataset())
    assert "Verification Requirements Summary" in report
    assert "Voltage" in report
    assert "Conductor" in report
    assert "Pole Class" in report


def test_report_has_per_pole_table(reporter):
    report = reporter.generate(make_dataset())
    assert "Per-Pole Summary" in report
    assert "903203" in report
    assert "903202" in report


def test_report_has_design_blockers_section(reporter):
    report = reporter.generate(make_dataset())
    assert "Design Blockers" in report
    assert "DNO" in report


def test_report_has_unmatched_section(reporter):
    dataset = make_dataset()
    dataset.unmatched_baseline = [{"support_no": "MISSING01", "easting": 100, "northing": 200}]
    report = reporter.generate(dataset)
    assert "Unmatched Poles" in report
    assert "MISSING01" in report


def test_report_has_action_items(reporter):
    report = reporter.generate(make_dataset())
    assert "Recommended Next Steps" in report
    assert "DNO" in report


def test_report_notes_design_blocked_expected(reporter):
    report = reporter.generate(make_dataset())
    # Check that the report explains design_blocked is expected
    assert "expected" in report.lower() or "specification" in report.lower()


def test_export_csv_columns_correct(reporter, tmp_path):
    dataset = make_dataset()
    csv_path = tmp_path / "export.csv"
    reporter.export_csv(dataset, csv_path)

    assert csv_path.exists()
    with open(csv_path) as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames
    assert "support_no" in fieldnames
    assert "design_blocked" in fieldnames
    assert "voltage_verification" in fieldnames
    assert "conductor_verification" in fieldnames
    assert "pole_class_verification" in fieldnames


def test_export_csv_row_count(reporter, tmp_path):
    poles = [make_pole(f"9032{i:02d}") for i in range(5)]
    dataset = make_dataset(poles)
    csv_path = tmp_path / "export.csv"
    reporter.export_csv(dataset, csv_path)

    with open(csv_path) as f:
        rows = list(csv.DictReader(f))
    assert len(rows) == 5
