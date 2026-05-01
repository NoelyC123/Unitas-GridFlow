"""Tests for D2-C/D2-D survey connectivity and metadata helpers."""

from __future__ import annotations

from app.survey_connectivity import (
    merge_connectivity_into_props,
    merge_survey_metadata_into_props,
    parse_capture_method_display,
    parse_gnss_block,
)


def test_parse_gnss_rtk_and_accuracy() -> None:
    rec = {"gnss_accuracy": "RTK horizontal: 0.02m vertical: 0.05m"}
    out = parse_gnss_block(rec)
    assert out["gnss_fix_type"] == "RTK fixed"
    assert out["horizontal_accuracy_m"] == 0.02
    assert out["vertical_accuracy_m"] == 0.05


def test_parse_capture_prefers_rtk_label() -> None:
    d = parse_capture_method_display({"capture_method": "RTK GNSS"})
    assert d["capture_method_key"] == "gnss"
    assert "RTK" in d["capture_method_label"] or d["capture_method_label"] == "RTK GNSS"


def test_merge_connectivity_parent_prefers_explicit_parent() -> None:
    props = {"parent_support_id": "P9", "linked_pole_id": "P1"}
    merge_connectivity_into_props(props)
    assert props["connectivity_parent_pole"] == "P9"


def test_merge_survey_metadata_job_ref() -> None:
    props = {"survey_job_ref": "JOB-77", "capture_method": "GNSS"}
    merge_survey_metadata_into_props(props)
    assert props["survey_job_ref"] == "JOB-77"
    assert props["capture_method_label"]
