"""Tests for SupportNumberMatcher."""

import pytest

from gridflow.baseline.models import BaselineDataset, BaselinePole
from gridflow.field.models import FieldDataset, FieldPole
from gridflow.matching import SupportNumberMatcher


@pytest.fixture
def matcher():
    return SupportNumberMatcher()


def make_baseline_pole(pole_id: str, support_no: str) -> BaselinePole:
    return BaselinePole(
        pole_id=pole_id,
        support_no=support_no,
        easting=354123.0,
        northing=456789.0,
    )


def make_field_pole(folder_name: str, support_no: str) -> FieldPole:
    return FieldPole(folder_name=folder_name, support_no=support_no)


class TestMatchSingle:
    def test_exact_match(self, matcher):
        assert matcher.match_single("903203", "903203") is True

    def test_no_match(self, matcher):
        assert matcher.match_single("903203", "999999") is False

    def test_variant_match(self, matcher):
        # 903201A vs 903201 — both strip to same digits
        assert matcher.match_single("903201A", "903201") is True

    def test_sp_prefix_match(self, matcher):
        # SP903203 normalises to 903203
        assert matcher.match_single("SP903203", "903203") is True

    def test_empty_no_match(self, matcher):
        assert matcher.match_single("", "903203") is False


class TestMatchDataset:
    def test_exact_match_dataset(self, matcher):
        baseline = BaselineDataset(poles=[make_baseline_pole("P1", "903203")])
        field = FieldDataset(
            dataset_path="/t",
            scan_date="2026",
            poles=[make_field_pole("01_SUPPORT_903203_LV", "903203")],
        )
        results = matcher.match(baseline, field)
        assert len(results) == 1
        assert results[0].match_type == "EXACT"
        assert results[0].field_support_no == "903203"

    def test_unmatched_baseline(self, matcher):
        baseline = BaselineDataset(poles=[make_baseline_pole("P1", "999999")])
        field = FieldDataset(
            dataset_path="/t",
            scan_date="2026",
            poles=[make_field_pole("01_SUPPORT_903203_LV", "903203")],
        )
        results = matcher.match(baseline, field)
        assert results[0].match_type == "UNMATCHED"

    def test_extra_field_pole(self, matcher):
        baseline = BaselineDataset(poles=[make_baseline_pole("P1", "903203")])
        field = FieldDataset(
            dataset_path="/t",
            scan_date="2026",
            poles=[
                make_field_pole("01_SUPPORT_903203_LV", "903203"),
                make_field_pole("99_SUPPORT_888888_HV", "888888"),
            ],
        )
        results = matcher.match(baseline, field)
        # Only 1 result (per baseline pole)
        assert len(results) == 1
        assert results[0].match_type == "EXACT"

    def test_full_10_pole_match(self, matcher):
        support_nos = [
            "903203",
            "903202",
            "903201A",
            "903201",
            "902204",
            "903101",
            "903503",
            "900346",
            "900347",
            "902206",
        ]
        baseline_poles = [
            make_baseline_pole(f"P{i:02d}", sno) for i, sno in enumerate(support_nos, 1)
        ]
        field_poles = [
            make_field_pole(f"{i:02d}_SUPPORT_{sno}_LV", sno)
            for i, sno in enumerate(support_nos, 1)
        ]
        baseline = BaselineDataset(poles=baseline_poles)
        field = FieldDataset(dataset_path="/t", scan_date="2026", poles=field_poles)

        results = matcher.match(baseline, field)
        matched = sum(1 for r in results if r.match_type != "UNMATCHED")
        assert matched == 10

    def test_variant_support_no_match(self, matcher):
        """903201A in field should match 903201A in baseline."""
        baseline = BaselineDataset(poles=[make_baseline_pole("P1", "903201A")])
        field = FieldDataset(
            dataset_path="/t",
            scan_date="2026",
            poles=[make_field_pole("03_SUPPORT_903201A_LV", "903201A")],
        )
        results = matcher.match(baseline, field)
        assert results[0].match_type == "EXACT"
