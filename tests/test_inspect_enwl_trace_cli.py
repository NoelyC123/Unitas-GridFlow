"""Tests for the ENWL trace inspector CLI."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

SCRIPT = Path("scripts/inspect_enwl_trace.py")


def write_geojson(path: Path, features: list[dict]) -> None:
    path.write_text(
        json.dumps({"type": "FeatureCollection", "features": features}),
        encoding="utf-8",
    )


def feature(properties: dict, geometry: dict | None = None) -> dict:
    return {
        "type": "Feature",
        "properties": properties,
        "geometry": geometry or {"type": "Point", "coordinates": [-2.7, 54.1]},
    }


def run_cli(*paths: Path) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(SCRIPT), *[str(path) for path in paths]],
        capture_output=True,
        text=True,
        check=False,
    )


def test_cli_runs_on_temp_geojson_and_prints_relationship_counts(tmp_path):
    trace_path = tmp_path / "trace.geojson"
    write_geojson(
        trace_path,
        [
            feature(
                {
                    "FID": "16793152",
                    "feature_type": "pole_structure",
                    "support_no": "902201",
                    "spn": "61090H02201",
                    "pole_type": "Section",
                }
            ),
            feature(
                {
                    "FID": "5940634",
                    "feature_type": "conductor_hv",
                    "voltage": "11kV",
                    "material": "Hard Drawn Copper",
                    "cable_size": "0.025in2",
                    "text_map": "3x .025 Cu 11",
                    "rated_current": "115.0",
                },
                geometry={
                    "type": "LineString",
                    "coordinates": [[-2.7, 54.1], [-2.71, 54.11]],
                },
            ),
            feature(
                {
                    "FID": "20636886",
                    "feature_type": "transformer",
                    "spn": "6511294TX001",
                    "fid_polestructure": "53427080",
                }
            ),
            feature(
                {
                    "FID": "11970605",
                    "feature_type": "sleeve_hv",
                    "sleeve_type": "Overhead Termination",
                }
            ),
        ],
    )

    result = run_cli(trace_path)

    assert result.returncode == 0
    assert "Relationship category counts:" in result.stdout
    assert "- direct_pole_identity: 1" in result.stdout
    assert "- direct_equipment_linked_to_pole: 1" in result.stdout
    assert "- route_span_evidence: 1" in result.stdout
    assert "- nearby_context_only: 1" in result.stdout
    assert "- uncertain: 0" in result.stdout


def test_cli_output_includes_route_span_caution_and_conductor_fields(tmp_path):
    trace_path = tmp_path / "conductor.geojson"
    write_geojson(
        trace_path,
        [
            feature(
                {
                    "FID": "5940634",
                    "feature_type": "conductor_hv",
                    "voltage": "11kV",
                    "material": "Hard Drawn Copper",
                    "cable_size": "0.025in2",
                    "text_map": "3x .025 Cu 11",
                    "rated_current": "115.0",
                }
            )
        ],
    )

    result = run_cli(trace_path)

    assert result.returncode == 0
    assert "ROUTE/SPAN EVIDENCE ONLY — not per-pole design-ready proof" in result.stdout
    assert "FID=5940634" in result.stdout
    assert "type=conductor_hv" in result.stdout
    assert "voltage=11kV" in result.stdout
    assert "material=Hard Drawn Copper" in result.stdout
    assert "cable_size=0.025in2" in result.stdout
    assert "text_map=3x .025 Cu 11" in result.stdout
    assert "rated_current=115.0" in result.stdout


def test_cli_prints_direct_equipment_and_nearby_context_summaries(tmp_path):
    trace_path = tmp_path / "equipment.geojson"
    write_geojson(
        trace_path,
        [
            feature(
                {
                    "FID": "20636886",
                    "feature_type": "transformer",
                    "spn": "6511294TX001",
                    "fid_polestructure": "53427080",
                }
            ),
            feature({"FID": "11970605", "feature_type": "sleeve_hv"}),
            feature({"FID": "11970606", "feature_type": "sleeve_hv"}),
        ],
    )

    result = run_cli(trace_path)

    assert result.returncode == 0
    assert "Direct Equipment Link Summary" in result.stdout
    assert "FID=20636886" in result.stdout
    assert "spn=6511294TX001" in result.stdout
    assert "fid_polestructure=53427080" in result.stdout
    assert "Nearby Context Summary by feature_type" in result.stdout
    assert "- sleeve_hv: 2" in result.stdout


def test_cli_exits_nonzero_and_prints_clear_error_for_invalid_file(tmp_path):
    invalid_path = tmp_path / "invalid.geojson"
    invalid_path.write_text(json.dumps({"type": "Feature", "properties": {}}), encoding="utf-8")

    result = run_cli(invalid_path)

    assert result.returncode == 1
    assert "ERROR inspecting" in result.stderr
    assert "FeatureCollection" in result.stderr
