"""Tests for combined evidence bundle export CLI."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


def write_trace(path: Path) -> None:
    path.write_text(json.dumps({"type": "FeatureCollection", "features": []}), encoding="utf-8")


def make_notes(survey_root: Path, pole_id: str, support: str, fid: str, spn: str) -> None:
    notes_dir = survey_root / "enwl_enrichment_clean" / pole_id / "notes"
    notes_dir.mkdir(parents=True)
    notes_dir.joinpath("pole_notes.md").write_text(
        f"""# Pole {support}

## Field status
Support number: {support}
Pole FID: {fid}
SPN: {spn}

## ENWL switch / equipment record
- fid: EQ{support}
- switch_type: Isolator Pole Mounted Class 4
- fid_polestructure: {fid}

## ENWL conductor evidence
- fid: COND{support}
- voltage: 11kV
- text_map: 3x 50 Al 11
""",
        encoding="utf-8",
    )


def test_export_creates_correct_files_for_target_poles(tmp_path):
    survey_root = tmp_path / "survey"
    make_notes(survey_root, "03_SUPPORT_900343", "900343", "16869661", "61090H00343")
    make_notes(survey_root, "05_SUPPORT_900344", "900344", "16869657", "61090H00344")
    trace_path = tmp_path / "trace.geojson"
    write_trace(trace_path)
    output_dir = tmp_path / "bundle"

    result = subprocess.run(
        [
            sys.executable,
            "scripts/export_combined_evidence_bundle.py",
            "--survey",
            str(survey_root),
            "--trace",
            str(trace_path),
            "--poles",
            "03_SUPPORT_900343",
            "05_SUPPORT_900344",
            "--output-dir",
            str(output_dir),
        ],
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0
    assert (output_dir / "03_SUPPORT_900343_combined_evidence.json").exists()
    assert (output_dir / "05_SUPPORT_900344_combined_evidence.json").exists()
    assert (output_dir / "bundle_summary.md").exists()
    record = json.loads((output_dir / "05_SUPPORT_900344_combined_evidence.json").read_text())
    assert record["support_no"] == "900344"
    assert "design_ready" not in record


def test_export_invalid_pole_raises_clear_error(tmp_path):
    survey_root = tmp_path / "survey"
    (survey_root / "enwl_enrichment_clean").mkdir(parents=True)
    trace_path = tmp_path / "trace.geojson"
    write_trace(trace_path)

    result = subprocess.run(
        [
            sys.executable,
            "scripts/export_combined_evidence_bundle.py",
            "--survey",
            str(survey_root),
            "--trace",
            str(trace_path),
            "--poles",
            "99_SUPPORT_MISSING",
            "--output-dir",
            str(tmp_path / "bundle"),
        ],
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode != 0
    assert "99_SUPPORT_MISSING" in result.stderr


def test_real_plocal002_bundle_export_if_available(tmp_path):
    survey_root = Path("real_pilot_data/P_LOCAL_002")
    trace_path = survey_root / "enwl_trace" / "enwl_trace_10924865_with_ratings.geojson"
    if not trace_path.exists():
        return

    result = subprocess.run(
        [
            sys.executable,
            "scripts/export_combined_evidence_bundle.py",
            "--survey",
            str(survey_root),
            "--trace",
            str(trace_path),
            "--poles",
            "03_SUPPORT_900343",
            "05_SUPPORT_900344",
            "06_SUPPORT_900345",
            "--output-dir",
            str(tmp_path / "bundle"),
        ],
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0
    assert (tmp_path / "bundle" / "03_SUPPORT_900343_combined_evidence.json").exists()
    assert (tmp_path / "bundle" / "05_SUPPORT_900344_combined_evidence.json").exists()
    assert (tmp_path / "bundle" / "06_SUPPORT_900345_combined_evidence.json").exists()
