from __future__ import annotations

import csv
import subprocess
import sys
from pathlib import Path

from scripts.propose_photo_renames import CSV_COLUMNS, build_manifest


def _make_survey(tmp_path: Path) -> Path:
    survey_root = tmp_path / "P_TEST"
    poles_root = survey_root / "enwl_enrichment_clean"

    generic_pole = poles_root / "01_SUPPORT_123456" / "field_photos"
    generic_pole.mkdir(parents=True)
    for name in ("IMG_0001.JPG", "IMG_0002.JPG", "IMG_0003.JPG", "IMG_0004.JPG"):
        (generic_pole / name).write_bytes(b"img")

    descriptive_pole = poles_root / "02_SUPPORT_654321" / "field_photos"
    descriptive_pole.mkdir(parents=True)
    for name in ("full_pole_IMG_0100.JPG", "switch_closeup.JPG", "span_west.JPG"):
        (descriptive_pole / name).write_bytes(b"img")

    return survey_root


def test_script_runs_without_error(tmp_path):
    survey_root = _make_survey(tmp_path)
    output = tmp_path / "manifest.csv"

    result = subprocess.run(
        [
            sys.executable,
            "scripts/propose_photo_renames.py",
            "--survey",
            str(survey_root),
            "--output",
            str(output),
        ],
        capture_output=True,
        text=True,
        check=True,
    )

    assert "Manifest complete:" in result.stdout
    assert output.exists()


def test_output_csv_has_correct_columns(tmp_path):
    survey_root = _make_survey(tmp_path)
    output = tmp_path / "manifest.csv"
    subprocess.run(
        [
            sys.executable,
            "scripts/propose_photo_renames.py",
            "--survey",
            str(survey_root),
            "--output",
            str(output),
        ],
        capture_output=True,
        text=True,
        check=True,
    )

    with output.open(encoding="utf-8") as handle:
        reader = csv.reader(handle)
        assert next(reader) == CSV_COLUMNS


def test_no_files_renamed_or_moved(tmp_path):
    survey_root = _make_survey(tmp_path)
    before = sorted(
        str(path.relative_to(survey_root)) for path in survey_root.rglob("*") if path.is_file()
    )

    build_manifest(survey_root)

    after = sorted(
        str(path.relative_to(survey_root)) for path in survey_root.rglob("*") if path.is_file()
    )
    assert before == after


def test_low_confidence_for_positional_assignments(tmp_path):
    survey_root = _make_survey(tmp_path)
    rows = build_manifest(survey_root)
    generic_rows = [row for row in rows if row["pole_folder"] == "01_SUPPORT_123456"]
    assert generic_rows
    assert all(row["confidence"] == "LOW" for row in generic_rows)
    assert all(row["reason"] == "positional_assignment" for row in generic_rows)


def test_high_confidence_for_descriptive_filenames(tmp_path):
    survey_root = _make_survey(tmp_path)
    rows = build_manifest(survey_root)
    descriptive_rows = [row for row in rows if row["pole_folder"] == "02_SUPPORT_654321"]
    assert descriptive_rows
    assert all(row["confidence"] == "HIGH" for row in descriptive_rows)
    assert all(row["reason"] == "already_descriptive" for row in descriptive_rows)


def test_action_required_yes_for_low_confidence(tmp_path):
    survey_root = _make_survey(tmp_path)
    rows = build_manifest(survey_root)
    low_rows = [row for row in rows if row["confidence"] == "LOW"]
    assert low_rows
    assert all(row["action_required"] == "YES" for row in low_rows)
