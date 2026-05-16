"""Tests for Stage 6B ENWL workspace evidence adapter."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from gridflow.workspace.enwl_evidence_adapter import (
    ENWLPoleEvidence,
    extract_enwl_fid,
    load_enwl_pole_evidence,
    load_enwl_trace_summary,
)

# ── Helpers ──────────────────────────────────────────────────────────────────


def _geojson(*features: dict) -> dict:
    return {"type": "FeatureCollection", "features": list(features)}


def _point_feature(props: dict) -> dict:
    return {
        "type": "Feature",
        "properties": props,
        "geometry": {"type": "Point", "coordinates": [-2.733, 54.196]},
    }


def _line_feature(props: dict) -> dict:
    return {
        "type": "Feature",
        "properties": props,
        "geometry": {
            "type": "LineString",
            "coordinates": [[-2.733, 54.196], [-2.735, 54.197]],
        },
    }


def _write_trace(path: Path, *features: dict) -> None:
    path.write_text(json.dumps(_geojson(*features)), encoding="utf-8")


# ── extract_enwl_fid ──────────────────────────────────────────────────────────


def test_extract_enwl_fid_finds_pole_fid_label():
    assert extract_enwl_fid("Pole FID: 16869657\nSPN: 61090H00344") == "16869657"


def test_extract_enwl_fid_finds_enwl_fid_label():
    assert extract_enwl_fid("ENWL FID: 16793152\nSPN: 61090H02201") == "16793152"


def test_extract_enwl_fid_finds_enwl_pole_fid_label():
    assert extract_enwl_fid("ENWL pole FID: 53427080") == "53427080"


def test_extract_enwl_fid_returns_none_when_no_match():
    assert extract_enwl_fid("Support number: 900344\nSPN: 61090H00344") is None


def test_extract_enwl_fid_returns_none_for_empty_input():
    assert extract_enwl_fid(None) is None
    assert extract_enwl_fid("") is None


# ── load_enwl_trace_summary ───────────────────────────────────────────────────


def test_load_enwl_trace_summary_unavailable_when_no_trace_dir(tmp_path):
    result = load_enwl_trace_summary(tmp_path)
    assert not result.available
    assert result.total_features == 0
    assert result.error is None


def test_load_enwl_trace_summary_unavailable_when_trace_dir_is_empty(tmp_path):
    (tmp_path / "enwl_trace").mkdir()
    result = load_enwl_trace_summary(tmp_path)
    assert not result.available


def test_load_enwl_trace_summary_counts_features_by_category(tmp_path):
    trace_dir = tmp_path / "enwl_trace"
    trace_dir.mkdir()
    _write_trace(
        trace_dir / "trace.geojson",
        _point_feature({"FID": "A1", "feature_type": "switch", "fid_polestructure": "P1"}),
        _line_feature({"FID": "B1", "feature_type": "conductor_hv", "material": "Cu"}),
        _point_feature(
            {"FID": "C1", "feature_type": "sleeve_hv", "sleeve_type": "Overhead Termination"}
        ),
    )

    result = load_enwl_trace_summary(tmp_path)

    assert result.available
    assert result.trace_file_count == 1
    assert result.total_features == 3
    assert result.direct_equipment_count == 1
    assert result.conductor_count == 1
    assert result.nearby_context_count == 1
    assert result.poles_with_direct_equipment == 1


def test_load_enwl_trace_summary_counts_distinct_pole_fids(tmp_path):
    trace_dir = tmp_path / "enwl_trace"
    trace_dir.mkdir()
    _write_trace(
        trace_dir / "trace.geojson",
        _point_feature({"FID": "E1", "feature_type": "switch", "fid_polestructure": "POLE_A"}),
        _point_feature({"FID": "E2", "feature_type": "transformer", "fid_polestructure": "POLE_A"}),
        _point_feature({"FID": "E3", "feature_type": "switch", "fid_polestructure": "POLE_B"}),
    )

    result = load_enwl_trace_summary(tmp_path)

    assert result.direct_equipment_count == 3
    assert result.poles_with_direct_equipment == 2


# ── load_enwl_pole_evidence ───────────────────────────────────────────────────


def test_load_enwl_pole_evidence_unavailable_when_no_trace_dir(tmp_path):
    result = load_enwl_pole_evidence(tmp_path, pole_folder_name=None, notes_content=None)
    assert not result.available


def test_load_enwl_pole_evidence_trace_only_mode_returns_conductors(tmp_path):
    trace_dir = tmp_path / "enwl_trace"
    trace_dir.mkdir()
    _write_trace(
        trace_dir / "trace.geojson",
        _line_feature(
            {
                "FID": "73190266",
                "feature_type": "conductor_hv",
                "material": "Aluminium Alloy Stranded",
                "cable_size": "50mm2",
                "text_map": "3x 50 Al 11",
            }
        ),
        _point_feature(
            {"FID": "11970601", "feature_type": "sleeve_hv", "sleeve_type": "Overhead Termination"}
        ),
    )
    notes = "Pole FID: 16869657\nSPN: 61090H00344"

    result = load_enwl_pole_evidence(tmp_path, pole_folder_name=None, notes_content=notes)

    assert result.available
    assert result.pole_fid == "16869657"
    assert len(result.conductors) == 1
    assert result.conductors[0]["text_map"] == "3x 50 Al 11"
    assert len(result.nearby_context) == 1


def test_load_enwl_pole_evidence_filters_direct_equipment_by_pole_fid(tmp_path):
    trace_dir = tmp_path / "enwl_trace"
    trace_dir.mkdir()
    _write_trace(
        trace_dir / "trace.geojson",
        _point_feature(
            {"FID": "73189925", "feature_type": "switch", "fid_polestructure": "16869657"}
        ),
        _point_feature(
            {"FID": "20636886", "feature_type": "transformer", "fid_polestructure": "53427080"}
        ),
    )
    notes = "Pole FID: 16869657\nSPN: 61090H00344"

    result = load_enwl_pole_evidence(tmp_path, pole_folder_name=None, notes_content=notes)

    assert result.available
    assert len(result.direct_equipment) == 1
    assert result.direct_equipment[0]["fid"] == "73189925"
    assert result.direct_equipment[0]["fid_polestructure"] == "16869657"


def test_load_enwl_pole_evidence_no_direct_equipment_when_no_pole_fid_match(tmp_path):
    trace_dir = tmp_path / "enwl_trace"
    trace_dir.mkdir()
    _write_trace(
        trace_dir / "trace.geojson",
        _point_feature(
            {"FID": "111", "feature_type": "switch", "fid_polestructure": "DIFFERENT_POLE"}
        ),
    )
    notes = "Pole FID: 16869657"

    result = load_enwl_pole_evidence(tmp_path, pole_folder_name=None, notes_content=notes)

    assert result.available
    assert result.direct_equipment == []


def test_load_enwl_pole_evidence_dno_badge_green_when_direct_equipment_confirmed(tmp_path):
    trace_dir = tmp_path / "enwl_trace"
    trace_dir.mkdir()
    _write_trace(
        trace_dir / "trace.geojson",
        _point_feature(
            {"FID": "73189925", "feature_type": "switch", "fid_polestructure": "16869657"}
        ),
    )

    result = load_enwl_pole_evidence(
        tmp_path, pole_folder_name=None, notes_content="Pole FID: 16869657"
    )

    assert result.dno_badge == "GREEN"


def test_load_enwl_pole_evidence_dno_badge_amber_when_no_equipment_match(tmp_path):
    trace_dir = tmp_path / "enwl_trace"
    trace_dir.mkdir()
    _write_trace(
        trace_dir / "trace.geojson",
        _line_feature({"FID": "X1", "feature_type": "conductor_hv", "material": "Cu"}),
    )

    result = load_enwl_pole_evidence(
        tmp_path, pole_folder_name=None, notes_content="Pole FID: 16869657"
    )

    assert result.dno_badge == "AMBER"


# ── design_ready not affected ─────────────────────────────────────────────────


def test_enwl_pole_evidence_has_no_design_ready_attribute(tmp_path):
    trace_dir = tmp_path / "enwl_trace"
    trace_dir.mkdir()
    _write_trace(
        trace_dir / "trace.geojson",
        _line_feature({"FID": "Z1", "feature_type": "conductor_hv", "text_map": "3x 50 Al 11"}),
    )

    result = load_enwl_pole_evidence(tmp_path, pole_folder_name=None, notes_content=None)

    assert result.available
    assert not hasattr(result, "design_ready")
    assert not hasattr(result, "conductor_spec_missing")


def test_enwl_trace_summary_has_no_design_ready_attribute(tmp_path):
    trace_dir = tmp_path / "enwl_trace"
    trace_dir.mkdir()
    _write_trace(
        trace_dir / "trace.geojson",
        _line_feature({"FID": "Z2", "feature_type": "conductor_hv", "text_map": "4x 50 Cu"}),
    )

    result = load_enwl_trace_summary(tmp_path)

    assert result.available
    assert not hasattr(result, "design_ready")


# ── caution wording ───────────────────────────────────────────────────────────


def test_enwl_pole_evidence_caution_is_non_empty():
    ev = ENWLPoleEvidence(available=True)
    assert ev.caution
    assert "route" in ev.caution.lower()
    assert "design-readiness" in ev.caution.lower()


def test_enwl_pole_evidence_provenance_label_is_set():
    ev = ENWLPoleEvidence(available=True)
    assert "ENWL" in ev.provenance


# ── real P_LOCAL_002 trace integration ───────────────────────────────────────


def test_real_plocal002_trace_loads_via_summary(tmp_path):
    src = Path("real_pilot_data/P_LOCAL_002/enwl_trace")
    if not src.exists():
        pytest.skip("P_LOCAL_002 ENWL trace not available")

    import shutil

    job_dir = tmp_path / "job"
    job_dir.mkdir()
    shutil.copytree(src, job_dir / "enwl_trace")

    result = load_enwl_trace_summary(job_dir)

    assert result.available
    assert result.trace_file_count >= 1
    assert result.total_features > 0
    assert result.conductor_count > 0
    assert result.direct_equipment_count > 0


def test_real_plocal002_trace_pole05_direct_equipment(tmp_path):
    src = Path("real_pilot_data/P_LOCAL_002/enwl_trace")
    if not src.exists():
        pytest.skip("P_LOCAL_002 ENWL trace not available")

    import shutil

    job_dir = tmp_path / "job"
    job_dir.mkdir()
    shutil.copytree(src, job_dir / "enwl_trace")

    notes = "Pole FID: 16869657\nSPN: 61090H00344"
    result = load_enwl_pole_evidence(job_dir, pole_folder_name=None, notes_content=notes)

    assert result.available
    assert result.pole_fid == "16869657"
    assert len(result.conductors) > 0
    assert all(c["relationship"] == "route_span_evidence" for c in result.conductors)
