from __future__ import annotations

import csv
from pathlib import Path

from app.structured_capture_schema import get_stage4_template_headers
from scripts.prepare_stage4_controlled_pilot import (
    compare_pilot_to_baseline,
    extract_baseline_candidates,
    load_pilot_csv,
    main,
)


def _write(path: Path, text: str) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return path


def test_prepare_mode_extracts_raw_controller_baseline_and_writes_starter_csv(
    tmp_path: Path,
) -> None:
    baseline = _write(
        tmp_path / "baseline.csv",
        "\n".join(
            [
                "Job:Demo,Version:3.21,Units:Metres",
                "GB_Carlisle,339921.145,556034.754,41.094,,,,,,,,,,,",
                "3,320934.012,567908.226,40.644,Angle,Angle:REMARK,Pole 9,Angle:HEIGHT,5",
                "20,320930.338,567912.167,40.690,EXpole,EXpole:REMARK,,EXpole:HEIGHT,8.2",
                "99,320900.000,567900.000,40.000,Hedge,Hedge:REMARK,Not a support",
            ]
        )
        + "\n",
    )
    starter_csv = tmp_path / "starter.csv"
    notes_out = tmp_path / "extract.md"

    exit_code = main(
        [
            "--baseline-csv",
            str(baseline),
            "--pilot-name",
            "P_CONTROLLED_001",
            "--out",
            str(starter_csv),
            "--notes-out",
            str(notes_out),
        ]
    )

    assert exit_code == 0
    with starter_csv.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        rows = list(reader)
        assert reader.fieldnames == get_stage4_template_headers()

    assert [row["pole_id"] for row in rows] == ["3", "20"]
    assert rows[0]["structure_type"] == "Angle"
    assert rows[1]["structure_type"] == "EXpole"
    assert rows[0]["capture_source"] == "surveyor_tablet"
    assert rows[0]["source"] == "structured_capture"
    assert rows[0]["captured_by"] == ""
    assert rows[0]["capture_date"] == ""
    assert "Candidate pole_id extract" in notes_out.read_text(encoding="utf-8")
    assert "`3`" in notes_out.read_text(encoding="utf-8")


def test_extract_headered_baseline_prefers_identity_and_type_columns(tmp_path: Path) -> None:
    baseline = _write(
        tmp_path / "headered.csv",
        "\n".join(
            [
                "Point,Code,Description",
                "P008-001,Pol,Support 1",
                "P008-002,Angle,Support 2",
                "CTX-01,Hedge,Context",
            ]
        )
        + "\n",
    )

    extract = extract_baseline_candidates(baseline)

    assert extract.format_name == "headered_csv"
    assert extract.identity_source == "Point"
    assert extract.type_source == "Code"
    assert [candidate.pole_id for candidate in extract.candidates] == ["P008-001", "P008-002"]


def test_prepare_mode_blocks_duplicate_normalized_baseline_ids(tmp_path: Path) -> None:
    baseline = _write(
        tmp_path / "dupe.csv",
        "\n".join(
            [
                "Point,Code",
                "p008-001,Pol",
                " P008-001 ,Angle",
            ]
        )
        + "\n",
    )
    starter_csv = tmp_path / "starter.csv"
    notes_out = tmp_path / "extract.md"

    exit_code = main(
        [
            "--baseline-csv",
            str(baseline),
            "--pilot-name",
            "P_CONTROLLED_001",
            "--out",
            str(starter_csv),
            "--notes-out",
            str(notes_out),
        ]
    )

    assert exit_code == 1
    assert "Blocking duplicates" in notes_out.read_text(encoding="utf-8")


def test_match_mode_uses_exact_match_after_whitespace_and_case_only(tmp_path: Path) -> None:
    baseline = _write(
        tmp_path / "baseline.csv",
        "\n".join(
            [
                "Point,Code",
                "P008-001,Pol",
                "P008-002,Angle",
                "P008-003,Pol",
            ]
        )
        + "\n",
    )
    pilot = _write(
        tmp_path / "pilot.csv",
        "\n".join(
            [
                "pole_id,capture_source,captured_by,capture_date",
                " p008-001 ,surveyor_tablet,Noel,2026-05-11",
                "P008-002,surveyor_tablet,Noel,2026-05-11",
                "P008-NEW,surveyor_tablet,Noel,2026-05-11",
            ]
        )
        + "\n",
    )
    report = tmp_path / "match.md"

    exit_code = main(
        [
            "--baseline-csv",
            str(baseline),
            "--pilot-csv",
            str(pilot),
            "--pilot-name",
            "P_CONTROLLED_001",
            "--match-report-out",
            str(report),
        ]
    )

    assert exit_code == 0
    report_text = report.read_text(encoding="utf-8")
    assert "MATCH READY" not in report_text
    assert "`MATCH`" in report_text
    assert "`NO MATCH`" in report_text
    assert "` p008-001 `" in report_text


def test_match_mode_blocks_missing_and_duplicate_pole_ids(tmp_path: Path) -> None:
    baseline = _write(
        tmp_path / "baseline.csv",
        "\n".join(
            [
                "Point,Code",
                "P008-001,Pol",
                "P008-002,Angle",
            ]
        )
        + "\n",
    )
    pilot = _write(
        tmp_path / "pilot.csv",
        "\n".join(
            [
                "pole_id,capture_source,captured_by,capture_date",
                ",surveyor_tablet,Noel,2026-05-11",
                "P008-001,surveyor_tablet,Noel,2026-05-11",
                "p008-001,surveyor_tablet,Noel,2026-05-11",
            ]
        )
        + "\n",
    )
    report = tmp_path / "match.md"

    exit_code = main(
        [
            "--baseline-csv",
            str(baseline),
            "--pilot-csv",
            str(pilot),
            "--pilot-name",
            "P_CONTROLLED_001",
            "--match-report-out",
            str(report),
        ]
    )

    assert exit_code == 1
    report_text = report.read_text(encoding="utf-8")
    assert "Blocking pilot duplicates" in report_text
    assert "Missing or unsafe pole_id" in report_text


def test_load_pilot_csv_requires_pole_id_column(tmp_path: Path) -> None:
    pilot = _write(
        tmp_path / "pilot.csv",
        "\n".join(
            [
                "capture_source,captured_by,capture_date",
                "surveyor_tablet,Noel,2026-05-11",
            ]
        )
        + "\n",
    )
    try:
        load_pilot_csv(pilot)
    except ValueError as exc:
        assert "pole_id column" in str(exc)
    else:  # pragma: no cover
        raise AssertionError("Expected load_pilot_csv to reject a CSV without pole_id")


def test_compare_pilot_to_baseline_preserves_original_pole_ids(tmp_path: Path) -> None:
    baseline = _write(
        tmp_path / "baseline.csv",
        "\n".join(
            [
                "Point,Code",
                "P008-001,Pol",
            ]
        )
        + "\n",
    )
    pilot = _write(
        tmp_path / "pilot.csv",
        "\n".join(
            [
                "pole_id,capture_source,captured_by,capture_date",
                " p008-001 ,surveyor_tablet,Noel,2026-05-11",
            ]
        )
        + "\n",
    )

    extract = extract_baseline_candidates(baseline)
    comparison = compare_pilot_to_baseline(extract, load_pilot_csv(pilot))

    assert comparison["matched_count"] == 1
    assert comparison["row_results"][0]["pilot_pole_id"] == " p008-001 "
    assert comparison["row_results"][0]["baseline_pole_id"] == "P008-001"
