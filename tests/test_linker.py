"""Tests for Stage 6C formal pole-to-ENWL linking."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

from gridflow.evidence_combiner.combiner import EvidenceCombiner
from gridflow.evidence_combiner.linker import link_pole


def _feature(properties: dict, geometry: dict | None = None) -> dict:
    return {
        "type": "Feature",
        "properties": properties,
        "geometry": geometry or {"type": "Point", "coordinates": [-2.733156, 54.196464]},
    }


def _write_trace(path: Path, features: list[dict]) -> None:
    import json

    path.write_text(
        json.dumps({"type": "FeatureCollection", "features": features}),
        encoding="utf-8",
    )


def _make_survey(tmp_path: Path, notes: str, folder_name: str = "05_SUPPORT_900344") -> Path:
    survey_root = tmp_path / "survey"
    notes_dir = survey_root / "enwl_enrichment_clean" / folder_name / "notes"
    notes_dir.mkdir(parents=True)
    notes_dir.joinpath("pole_notes.md").write_text(notes, encoding="utf-8")
    return survey_root


SAMPLE_NOTES = """# Pole
Support number: 900344
Pole FID: 16869657
SPN: 61090H00344
Latitude: 54.196464
Longitude: -2.733156
"""


def test_fid_polestructure_match_is_high(tmp_path):
    survey_root = _make_survey(tmp_path, SAMPLE_NOTES)
    trace_path = tmp_path / "trace.geojson"
    _write_trace(
        trace_path,
        [
            _feature(
                {
                    "FID": "73189925",
                    "feature_type": "switch",
                    "fid_polestructure": "16869657",
                }
            )
        ],
    )

    result = link_pole(survey_root, "05_SUPPORT_900344", trace_path)
    assert result.confidence == "HIGH"
    assert result.linking_method == "fid_polestructure"
    assert result.manual_confirmation_required is False
    assert "fid_polestructure" in result.matched_methods


def test_support_no_match_is_medium(tmp_path, monkeypatch):
    survey_root = _make_survey(tmp_path, SAMPLE_NOTES)
    trace_path = tmp_path / "trace.geojson"
    _write_trace(trace_path, [])

    original = EvidenceCombiner.combine

    def fake_combine(self, *_args, **_kwargs):
        record = original(self, *_args, **_kwargs)
        record["spn"] = None
        return record

    monkeypatch.setattr(EvidenceCombiner, "combine", fake_combine)

    result = link_pole(survey_root, "05_SUPPORT_900344", trace_path)
    assert result.confidence == "MEDIUM"
    assert result.linking_method == "support_no"
    assert result.manual_confirmation_required is False
    assert "support_no" in result.matched_methods


def test_gps_proximity_alone_is_low_and_manual_required(tmp_path):
    notes = """# Pole
Support number:
SPN:
Latitude: 54.196464
Longitude: -2.733156
"""
    survey_root = _make_survey(tmp_path, notes, folder_name="01_SUPPORT_UNKNOWN")
    trace_path = tmp_path / "trace.geojson"
    _write_trace(
        trace_path,
        [
            _feature(
                {
                    "FID": "73190266",
                    "feature_type": "conductor_hv",
                    "text_map": "3x 50 Al 11",
                },
                geometry={
                    "type": "LineString",
                    "coordinates": [[-2.733156, 54.196464], [-2.733, 54.1965]],
                },
            )
        ],
    )

    result = link_pole(survey_root, "01_SUPPORT_UNKNOWN", trace_path)
    assert result.confidence == "LOW"
    assert result.linking_method == "gps_proximity"
    assert result.manual_confirmation_required is True
    assert result.distance_m is not None
    assert "gps_proximity" in result.matched_methods


def test_no_match_returns_none_and_manual_required(tmp_path):
    notes = """# Pole
Support number:
SPN:
"""
    survey_root = _make_survey(tmp_path, notes, folder_name="01_SUPPORT_UNKNOWN")
    trace_path = tmp_path / "trace.geojson"
    _write_trace(trace_path, [])

    result = link_pole(survey_root, "01_SUPPORT_UNKNOWN", trace_path)
    assert result.confidence == "NONE"
    assert result.linking_method == "manual"
    assert result.manual_confirmation_required is True


def test_multiple_matching_methods_recorded(tmp_path):
    survey_root = _make_survey(tmp_path, SAMPLE_NOTES)
    trace_path = tmp_path / "trace.geojson"
    _write_trace(
        trace_path,
        [
            _feature(
                {
                    "FID": "73189925",
                    "feature_type": "switch",
                    "fid_polestructure": "16869657",
                }
            ),
            _feature(
                {
                    "FID": "73190266",
                    "feature_type": "conductor_hv",
                    "text_map": "3x 50 Al 11",
                },
                geometry={
                    "type": "LineString",
                    "coordinates": [[-2.733156, 54.196464], [-2.733, 54.1965]],
                },
            ),
        ],
    )

    result = link_pole(survey_root, "05_SUPPORT_900344", trace_path)
    assert "fid_polestructure" in result.matched_methods
    assert "support_no" in result.matched_methods
    assert "spn" in result.matched_methods
    assert "gps_proximity" in result.matched_methods


def test_real_plocal002_linking_distribution_if_available():
    survey_root = Path("real_pilot_data/P_LOCAL_002")
    trace_path = survey_root / "enwl_trace" / "enwl_trace_10924865_with_ratings.geojson"
    if not trace_path.exists():
        pytest.skip("P_LOCAL_002 trace file not available")

    result = subprocess.run(
        [
            sys.executable,
            "scripts/link_survey_poles.py",
            "--survey",
            str(survey_root),
            "--trace",
            str(trace_path),
            "--output",
            "/tmp/P_LOCAL_002_LINKING_REPORT_TEST.md",
        ],
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0
    report = Path("/tmp/P_LOCAL_002_LINKING_REPORT_TEST.md").read_text(encoding="utf-8")
    assert "HIGH confidence: 3" in report
    assert "MEDIUM confidence: 9" in report
    assert "Manual confirmation required: 0" in report
