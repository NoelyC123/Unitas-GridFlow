"""Tests for all-poles survey evidence summary CLI."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from scripts.survey_evidence_summary import evidence_quality


def write_trace(path: Path) -> None:
    path.write_text(json.dumps({"type": "FeatureCollection", "features": []}), encoding="utf-8")


def make_notes(
    survey_root: Path,
    pole_id: str,
    support: str,
    fid: str | None,
    spn: str | None,
    include_equipment: bool = False,
    include_conductor: bool = False,
) -> None:
    notes_dir = survey_root / "enwl_enrichment_clean" / pole_id / "notes"
    notes_dir.mkdir(parents=True)
    lines = [f"# Pole {support}", "", "## Field status", f"Support number: {support}"]
    if fid:
        lines.append(f"Pole FID: {fid}")
    if spn:
        lines.append(f"SPN: {spn}")
    if include_equipment:
        lines.extend(
            [
                "",
                "## ENWL switch / equipment record",
                "- fid: EQ001",
                "- switch_type: Isolator Pole Mounted Class 4",
                f"- fid_polestructure: {fid}",
            ]
        )
    if include_conductor:
        lines.extend(
            [
                "",
                "## ENWL conductor evidence",
                "- fid: COND001",
                "- voltage: 11kV",
                "- text_map: 3x 50 Al 11",
            ]
        )
    notes_dir.joinpath("pole_notes.md").write_text("\n".join(lines), encoding="utf-8")


def test_green_amber_red_logic():
    assert (
        evidence_quality(
            {"support_no": "1", "pole_fid": "2", "spn": "3", "direct_equipment_records": [{}]}
        )
        == "GREEN"
    )
    assert (
        evidence_quality(
            {"support_no": "1", "pole_fid": "2", "spn": "3", "direct_equipment_records": []}
        )
        == "AMBER"
    )
    assert (
        evidence_quality(
            {"support_no": "1", "pole_fid": None, "spn": "3", "direct_equipment_records": []}
        )
        == "RED"
    )


def test_all_poles_summary_runs_and_includes_quality_column(tmp_path):
    survey_root = tmp_path / "survey"
    make_notes(
        survey_root, "01_SUPPORT_900001", "900001", "FID001", "SPN001", include_conductor=True
    )
    make_notes(
        survey_root, "02_SUPPORT_900002", "900002", "FID002", "SPN002", include_equipment=True
    )
    make_notes(survey_root, "03_SUPPORT_UNKNOWN", "UNKNOWN", None, None)
    trace_path = tmp_path / "trace.geojson"
    write_trace(trace_path)

    result = subprocess.run(
        [
            sys.executable,
            "scripts/survey_evidence_summary.py",
            "--survey",
            str(survey_root),
            "--trace",
            str(trace_path),
        ],
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0
    assert "Evidence Quality" in result.stdout
    assert "AMBER" in result.stdout
    assert "GREEN" in result.stdout
    assert "RED" in result.stdout
    assert "Design-readiness caution:" in result.stdout


def test_real_plocal002_summary_if_available():
    survey_root = Path("real_pilot_data/P_LOCAL_002")
    trace_path = survey_root / "enwl_trace" / "enwl_trace_10924865_with_ratings.geojson"
    if not trace_path.exists() or not (survey_root / "enwl_enrichment_clean").exists():
        return

    result = subprocess.run(
        [
            sys.executable,
            "scripts/survey_evidence_summary.py",
            "--survey",
            str(survey_root),
            "--trace",
            str(trace_path),
        ],
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0
    assert "Total poles processed: 12" in result.stdout
    assert "| 05 | 900344 | 16869657 |" in result.stdout
