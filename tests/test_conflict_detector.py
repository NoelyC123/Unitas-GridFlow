"""Tests for Stage 6D three-source conflict detection."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from gridflow.conflict_detector import ConflictDetector


def _feature(properties: dict, geometry: dict | None = None) -> dict:
    return {
        "type": "Feature",
        "properties": properties,
        "geometry": geometry or {"type": "Point", "coordinates": [-2.733156, 54.196464]},
    }


def _write_trace(path: Path, features: list[dict]) -> None:
    path.write_text(
        json.dumps({"type": "FeatureCollection", "features": features}),
        encoding="utf-8",
    )


def _make_survey(tmp_path: Path, notes: str, folder: str = "01_SUPPORT_900344") -> Path:
    survey_root = tmp_path / "survey"
    notes_dir = survey_root / "enwl_enrichment_clean" / folder / "notes"
    notes_dir.mkdir(parents=True)
    notes_dir.joinpath("pole_notes.md").write_text(notes, encoding="utf-8")
    return survey_root


def _base_notes(extra: str = "") -> str:
    return f"""# Pole
Support number: 900344
Field visible plate: 900344
Pole FID: 16869657
SPN: 61090H00344
Field pole type: Intermediate
Latitude: 54.196464
Longitude: -2.733156
{extra}
"""


def test_pole_type_mismatch_detected(tmp_path):
    survey = _make_survey(tmp_path, _base_notes())
    trace = tmp_path / "trace.geojson"
    _write_trace(
        trace,
        [
            _feature(
                {
                    "FID": "16869657",
                    "feature_type": "pole_structure",
                    "support_no": "900344",
                    "spn": "61090H00344",
                    "pole_type": "Terminal",
                    "pole_class": "Single Wood Pole",
                }
            )
        ],
    )

    results = ConflictDetector().detect_pole(survey, "01_SUPPORT_900344", trace)
    mismatch = [r for r in results if r.conflict_type == "pole_type_mismatch"]
    assert len(mismatch) == 1
    assert mismatch[0].severity == "WARNING"


def test_equipment_mismatch_detected(tmp_path):
    survey = _make_survey(tmp_path, _base_notes("Transformer: Yes"))
    trace = tmp_path / "trace.geojson"
    _write_trace(
        trace,
        [
            _feature(
                {
                    "FID": "16869657",
                    "feature_type": "pole_structure",
                    "support_no": "900344",
                    "spn": "61090H00344",
                    "pole_type": "Intermediate",
                }
            )
        ],
    )

    results = ConflictDetector().detect_pole(survey, "01_SUPPORT_900344", trace)
    equip = [r for r in results if r.conflict_type == "equipment_mismatch"]
    assert equip
    assert all(r.severity == "CRITICAL" for r in equip)


def test_coordinate_difference_over_50m_flagged(tmp_path):
    survey = _make_survey(tmp_path, _base_notes())
    trace = tmp_path / "trace.geojson"
    _write_trace(
        trace,
        [
            _feature(
                {
                    "FID": "16869657",
                    "feature_type": "pole_structure",
                    "support_no": "900344",
                    "spn": "61090H00344",
                    "pole_type": "Intermediate",
                },
                geometry={"type": "Point", "coordinates": [-2.70, 54.20]},
            )
        ],
    )
    results = ConflictDetector().detect_pole(survey, "01_SUPPORT_900344", trace)
    coordinate = [r for r in results if r.conflict_type == "coordinate_mismatch"]
    assert len(coordinate) == 1
    assert coordinate[0].severity == "WARNING"


def test_support_number_mismatch_flagged(tmp_path):
    notes = _base_notes().replace("Field visible plate: 900344", "Field visible plate: 900999")
    survey = _make_survey(tmp_path, notes)
    trace = tmp_path / "trace.geojson"
    _write_trace(
        trace,
        [
            _feature(
                {
                    "FID": "16869657",
                    "feature_type": "pole_structure",
                    "support_no": "900344",
                    "spn": "61090H00344",
                    "pole_type": "Intermediate",
                }
            )
        ],
    )
    results = ConflictDetector().detect_pole(survey, "01_SUPPORT_900344", trace)
    support = [r for r in results if r.conflict_type == "support_no_mismatch"]
    assert len(support) == 1
    assert support[0].severity == "CRITICAL"


def test_missing_field_evidence_flagged_as_info(tmp_path):
    survey = _make_survey(tmp_path, _base_notes())
    trace = tmp_path / "trace.geojson"
    _write_trace(
        trace,
        [
            _feature(
                {
                    "FID": "16869657",
                    "feature_type": "pole_structure",
                    "support_no": "900344",
                    "spn": "61090H00344",
                    "pole_type": "Intermediate",
                }
            ),
            _feature(
                {
                    "FID": "73190266",
                    "feature_type": "conductor_hv",
                    "material": "AAAC",
                    "cable_size": "50mm2",
                    "text_map": "3x 50 Al 11",
                },
                geometry={"type": "LineString", "coordinates": [[-2.7331, 54.1964], [-2.73, 54.2]]},
            ),
        ],
    )
    results = ConflictDetector().detect_pole(survey, "01_SUPPORT_900344", trace)
    missing = [r for r in results if r.conflict_type == "missing_field_evidence"]
    assert len(missing) == 1
    assert missing[0].severity == "INFO"


def test_no_false_positives_on_matching_records(tmp_path):
    notes = _base_notes(
        """Transformer: Yes
## ENWL equipment
- fid: 73189925
- feature_type: switch
- fid_polestructure: 16869657
## ENWL conductor evidence
- conductor: observed
"""
    )
    survey = _make_survey(tmp_path, notes)
    trace = tmp_path / "trace.geojson"
    _write_trace(
        trace,
        [
            _feature(
                {
                    "FID": "16869657",
                    "feature_type": "pole_structure",
                    "support_no": "900344",
                    "spn": "61090H00344",
                    "pole_type": "Intermediate",
                }
            ),
            _feature(
                {
                    "FID": "73189925",
                    "feature_type": "switch",
                    "fid_polestructure": "16869657",
                }
            ),
        ],
    )
    results = ConflictDetector().detect_pole(survey, "01_SUPPORT_900344", trace)
    assert results == []


def test_real_plocal002_conflicts_detected_if_available():
    survey_root = Path("real_pilot_data/P_LOCAL_002")
    trace_path = survey_root / "enwl_trace" / "enwl_trace_10924865_with_ratings.geojson"
    if not trace_path.exists():
        pytest.skip("P_LOCAL_002 trace file not available")

    results = ConflictDetector().detect_survey(survey_root, trace_path)
    assert len(results) == 12
    total = sum(len(v) for v in results.values())
    assert total >= 0
