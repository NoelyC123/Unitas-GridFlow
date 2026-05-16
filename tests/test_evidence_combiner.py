"""Tests for Stage 6B three-source evidence combiner."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

from gridflow.evidence_combiner import DESIGN_READINESS_CAUTION, EvidenceCombiner


def write_trace(path: Path, features: list[dict]) -> None:
    path.write_text(
        json.dumps({"type": "FeatureCollection", "features": features}), encoding="utf-8"
    )


def feature(properties: dict, geometry: dict | None = None) -> dict:
    return {
        "type": "Feature",
        "properties": properties,
        "geometry": geometry or {"type": "Point", "coordinates": [-2.733156, 54.196464]},
    }


def make_survey(tmp_path: Path, notes: str, folder_name: str = "05_SUPPORT_900344") -> Path:
    survey_root = tmp_path / "survey"
    notes_dir = survey_root / "enwl_enrichment_clean" / folder_name / "notes"
    notes_dir.mkdir(parents=True)
    notes_dir.joinpath("pole_notes.md").write_text(notes, encoding="utf-8")
    return survey_root


SAMPLE_NOTES = """# P_LOCAL_002 — Pole 05 — Support 900344

## Field status

Support number: 900344
Pole FID: 16869657
SPN: 61090H00344

GPS/map pin:

- Latitude: 54.196464
- Longitude: -2.733156

## ENWL pole record

- pole_type: Intermediate
- pole_class: Single Wood Pole
- support_diameter: Stout
- support_no: 900344

## ENWL switch / equipment record

Record type: Fault Making Switch

- fid: 73189925
- voltage: 11kV
- switch_type: Isolator Pole Mounted Class 4
- fid_polestructure: 16869657
- spn: 6546784SW001

## ENWL conductor evidence near Pole 5

### Conductor record 1

Record type: HV Conductor

- fid: 73190266
- voltage: 11kV
- material: Aluminium Alloy Stranded
- cable_size: 50mm2
- text_map: 3x 50 Al 11

## Current uncertainties

- Confirm exact conductor FID-to-span relationship before using conductor data.
- Do not mark this pole design-ready from ENWL evidence alone.
"""


def test_pole_notes_parsed_correctly(tmp_path):
    survey_root = make_survey(tmp_path, SAMPLE_NOTES)
    trace_path = tmp_path / "trace.geojson"
    write_trace(trace_path, [])

    record = EvidenceCombiner().combine(survey_root, "05_SUPPORT_900344", trace_path)

    assert record["support_no"] == "900344"
    assert record["pole_fid"] == "16869657"
    assert record["spn"] == "61090H00344"
    assert record["pole_type"] == "Intermediate"
    assert record["pole_class"] == "Single Wood Pole"
    assert record["support_diameter"] == "Stout"
    assert record["coordinates"]["latitude"] == 54.196464


def test_fid_polestructure_match_classified_as_level_2(tmp_path):
    survey_root = make_survey(tmp_path, SAMPLE_NOTES)
    trace_path = tmp_path / "trace.geojson"
    write_trace(
        trace_path,
        [
            feature(
                {
                    "FID": "73189925",
                    "feature_type": "switch",
                    "spn": "6546784SW001",
                    "fid_polestructure": "16869657",
                    "voltage": "11kV",
                }
            )
        ],
    )

    record = EvidenceCombiner().combine(survey_root, "05_SUPPORT_900344", trace_path)

    direct = record["direct_equipment_records"]
    assert any(item["fid"] == "73189925" for item in direct)
    item = next(item for item in direct if item["fid"] == "73189925")
    assert item["relationship"] == "direct_equipment_linked_to_pole"
    assert item["evidence_level"] == 2
    assert item["fid_polestructure"] == "16869657"
    assert item["trace_match"] is True


def test_conductor_records_classified_as_level_3(tmp_path):
    survey_root = make_survey(tmp_path, SAMPLE_NOTES)
    trace_path = tmp_path / "trace.geojson"
    write_trace(
        trace_path,
        [
            feature(
                {
                    "FID": "73190266",
                    "feature_type": "conductor_hv",
                    "voltage": "11kV",
                    "material": "Aluminium Alloy Stranded",
                    "cable_size": "50mm2",
                    "text_map": "3x 50 Al 11",
                    "rated_current": "115.0",
                },
                geometry={
                    "type": "LineString",
                    "coordinates": [[-2.733156, 54.196464], [-2.733, 54.1965]],
                },
            )
        ],
    )

    record = EvidenceCombiner().combine(survey_root, "05_SUPPORT_900344", trace_path)

    conductors = record["route_conductor_evidence"]
    item = next(item for item in conductors if item["fid"] == "73190266")
    assert item["relationship"] == "route_span_evidence"
    assert item["evidence_level"] == 3
    assert item["text_map"] == "3x 50 Al 11"
    assert item["rated_current"] == "115.0"


def test_combiner_does_not_crash_on_missing_optional_fields(tmp_path):
    notes = """# Pole
## Field status
Support number: 900000
SPN: 61090H00000
"""
    survey_root = make_survey(tmp_path, notes, folder_name="01_SUPPORT_900000")
    trace_path = tmp_path / "trace.geojson"
    write_trace(trace_path, [feature({"unexpected": "value"})])

    record = EvidenceCombiner().combine(survey_root, "01_SUPPORT_900000", trace_path)

    assert record["support_no"] == "900000"
    assert record["pole_fid"] is None
    assert record["direct_equipment_records"] == []
    assert record["route_conductor_evidence"] == []


def test_combined_record_has_no_design_ready_field_and_contains_caution(tmp_path):
    survey_root = make_survey(tmp_path, SAMPLE_NOTES)
    trace_path = tmp_path / "trace.geojson"
    write_trace(trace_path, [])

    record = EvidenceCombiner().combine(survey_root, "05_SUPPORT_900344", trace_path)

    assert "design_ready" not in record
    assert "conductor_spec_missing" not in record
    assert record["design_readiness_caution"] == DESIGN_READINESS_CAUTION


def test_evidence_record_contains_provenance_fields(tmp_path):
    survey_root = make_survey(tmp_path, SAMPLE_NOTES)
    trace_path = tmp_path / "trace.geojson"
    write_trace(trace_path, [])

    record = EvidenceCombiner().combine(survey_root, "05_SUPPORT_900344", trace_path)

    assert record["contributing_files"]["survey_root"] == str(survey_root)
    assert record["contributing_files"]["pole_notes"].endswith("pole_notes.md")
    assert record["contributing_files"]["trace_geojson"] == str(trace_path)
    assert record["direct_equipment_records"][0]["source"] == "pole_notes"


def test_real_pole05_combined_record_contains_abs_and_route_conductor():
    survey_root = Path("real_pilot_data/P_LOCAL_002")
    trace_path = survey_root / "enwl_trace" / "enwl_trace_10924865_with_ratings.geojson"
    pole_notes = (
        survey_root / "enwl_enrichment_clean" / "05_SUPPORT_900344" / "notes" / "pole_notes.md"
    )
    if not trace_path.exists() or not pole_notes.exists():
        pytest.skip("P_LOCAL_002 Pole 05 evidence is not available")

    record = EvidenceCombiner().combine(survey_root, "05_SUPPORT_900344", trace_path)

    assert record["support_no"] == "900344"
    assert record["pole_fid"] == "16869657"
    assert any(item["fid"] == "73189925" for item in record["direct_equipment_records"])
    abs_record = next(
        item for item in record["direct_equipment_records"] if item["fid"] == "73189925"
    )
    assert abs_record["relationship"] == "direct_equipment_linked_to_pole"
    assert abs_record["evidence_level"] == 2
    assert abs_record["fid_polestructure"] == "16869657"
    assert any(item["fid"] == "73190266" for item in record["route_conductor_evidence"])
    conductor = next(
        item for item in record["route_conductor_evidence"] if item["fid"] == "73190266"
    )
    assert conductor["relationship"] == "route_span_evidence"
    assert conductor["evidence_level"] == 3
    assert conductor["text_map"] == "3x 50 Al 11"


def test_cli_runs_on_real_plocal002_pole05_if_available():
    survey_root = Path("real_pilot_data/P_LOCAL_002")
    trace_path = survey_root / "enwl_trace" / "enwl_trace_10924865_with_ratings.geojson"
    pole_notes = (
        survey_root / "enwl_enrichment_clean" / "05_SUPPORT_900344" / "notes" / "pole_notes.md"
    )
    if not trace_path.exists() or not pole_notes.exists():
        pytest.skip("P_LOCAL_002 Pole 05 evidence is not available")

    result = subprocess.run(
        [
            sys.executable,
            "scripts/combine_pole_evidence.py",
            "--survey",
            str(survey_root),
            "--pole",
            "05_SUPPORT_900344",
            "--trace",
            str(trace_path),
        ],
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0
    payload = json.loads(result.stdout)
    assert payload["support_no"] == "900344"
    assert any(item["fid"] == "73189925" for item in payload["direct_equipment_records"])
    assert "design_ready" not in payload
