"""Operator-facing execution tests for the Stage 4 field pilot command center."""

from __future__ import annotations

import csv
import json
import subprocess
import sys
from pathlib import Path

import pytest

from scripts import validate_stage4_pilot

REPO_ROOT = Path(__file__).resolve().parent.parent
FIXTURES = REPO_ROOT / "tests" / "fixtures" / "stage4"
EVIDENCE = FIXTURES / "evidence"
STABLE_JSON_KEYS = {
    "pilot_metadata",
    "validation_summary",
    "evidence_summary",
    "row_findings",
    "field_findings",
    "recommendations",
    "stage4c_gate_status",
}


def _read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_csv(path: Path, headers: list[str], rows: list[list[str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(headers)
        writer.writerows(rows)


def test_cli_runs_on_valid_pilot_sample_and_writes_json_and_markdown(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    out_dir = tmp_path / "P_REAL_001"
    rc = validate_stage4_pilot.main(
        [
            "--csv",
            str(FIXTURES / "pilot_valid_sample.csv"),
            "--pilot-name",
            "P_REAL_001",
            "--evidence-dir",
            str(EVIDENCE / "valid"),
            "--out",
            str(out_dir),
        ]
    )

    captured = capsys.readouterr().out
    json_path = out_dir / "pilot_validation_report.json"
    md_path = out_dir / "pilot_validation_report.md"

    assert rc == 0
    assert "STAGE 4 PILOT RESULT: PARTIAL" in captured
    assert "Next action:" in captured
    assert "Reports:" in captured
    assert json_path.exists()
    assert md_path.exists()

    report = _read_json(json_path)
    assert STABLE_JSON_KEYS.issubset(report)
    assert report["validation_summary"]["total_rows"] == 7
    assert report["validation_summary"]["merge_ready_rows"] == 6
    assert report["stage4c_gate_status"]["decision"] == "PARTIAL / RE-PILOT REQUIRED"
    assert report["evidence_summary"]["referenced_photos_found"] == 6
    assert report["evidence_summary"]["missing_referenced_photos"] == []
    markdown = md_path.read_text(encoding="utf-8")
    assert "## Stage 4C Gate Implication" in markdown
    assert "## What Noel Should Do Next" in markdown
    assert "## What Must Not Happen Yet" in markdown


def test_cli_runs_on_invalid_pilot_sample_and_reports_no_go(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    out_dir = tmp_path / "P_REAL_BAD"
    rc = validate_stage4_pilot.main(
        [
            "--csv",
            str(FIXTURES / "pilot_invalid_sample.csv"),
            "--pilot-name",
            "P_REAL_BAD",
            "--out",
            str(out_dir),
        ]
    )

    captured = capsys.readouterr().out
    report = _read_json(out_dir / "pilot_validation_report.json")

    assert rc == 0
    assert "STAGE 4 PILOT RESULT: NO-GO" in captured
    assert report["validation_summary"]["blocked_rows"] == 1
    assert report["validation_summary"]["invalid_rows"] == 4
    assert report["stage4c_gate_status"]["decision"] == "NO-GO"
    assert report["top_issues"]


@pytest.mark.parametrize(
    ("fixture_name", "expected_decision"),
    [
        ("pilot_valid_sample.csv", "PARTIAL / RE-PILOT REQUIRED"),
        ("pilot_invalid_sample.csv", "NO-GO"),
        ("pilot_duplicate_identity_sample.csv", "NO-GO"),
        ("golden_valid.csv", "PARTIAL / RE-PILOT REQUIRED"),
        ("golden_invalid.csv", "NO-GO"),
        ("golden_duplicates.csv", "NO-GO"),
        ("golden_known_bad.csv", "NO-GO"),
    ],
)
def test_dry_run_fixtures_produce_expected_decisions(
    tmp_path: Path, fixture_name: str, expected_decision: str
) -> None:
    out_dir = tmp_path / fixture_name.replace(".csv", "")
    rc = validate_stage4_pilot.main(
        [
            "--csv",
            str(FIXTURES / fixture_name),
            "--pilot-name",
            fixture_name.replace(".csv", "").upper(),
            "--out",
            str(out_dir),
        ]
    )

    report = _read_json(out_dir / "pilot_validation_report.json")
    assert rc == 0
    assert report["stage4c_gate_status"]["decision"] == expected_decision


def test_json_report_contains_stable_keys(tmp_path: Path) -> None:
    out_dir = tmp_path / "stable_keys"
    validate_stage4_pilot.main(
        [
            "--csv",
            str(FIXTURES / "golden_valid.csv"),
            "--out",
            str(out_dir),
        ]
    )

    report = _read_json(out_dir / "pilot_validation_report.json")
    assert STABLE_JSON_KEYS.issubset(report)
    assert "decision" in report["stage4c_gate_status"]
    assert "implication" in report["stage4c_gate_status"]
    assert report["row_findings"] == report["row_level_findings"]
    assert report["field_findings"] == report["field_level_findings"]


def test_evidence_checker_detects_missing_unreferenced_duplicate_and_invalid_names(
    tmp_path: Path,
) -> None:
    out_dir = tmp_path / "evidence_check"
    rc = validate_stage4_pilot.main(
        [
            "--csv",
            str(FIXTURES / "pilot_valid_sample.csv"),
            "--pilot-name",
            "P_REAL_EVIDENCE",
            "--evidence-dir",
            str(EVIDENCE / "invalid"),
            "--out",
            str(out_dir),
        ]
    )

    report = _read_json(out_dir / "pilot_validation_report.json")
    evidence = report["evidence_summary"]

    assert rc == 0
    assert evidence["status"] == "checked"
    assert "P008-104_01_stay.jpg" in evidence["missing_referenced_photos"]
    assert "P999-999_01_context.jpg" in evidence["unreferenced_photos"]
    assert "P008-102_01_support.jpg" in evidence["duplicate_photo_names"]
    assert any(item.endswith("badname.jpg") for item in evidence["invalid_photo_naming_patterns"])


def test_photo_reference_that_does_not_match_csv_pole_id_is_detected(
    tmp_path: Path,
) -> None:
    csv_path = tmp_path / "mismatch.csv"
    _write_csv(
        csv_path,
        [
            "pole_id",
            "capture_source",
            "captured_by",
            "capture_date",
            "condition",
            "photo_reference",
            "source",
        ],
        [
            [
                "P008-500",
                "surveyor_tablet",
                "Noel Collins",
                "2026-05-11",
                "good",
                "P999-999_01_context.jpg",
                "structured_capture",
            ]
        ],
    )
    out_dir = tmp_path / "mismatch_out"

    validate_stage4_pilot.main(
        [
            "--csv",
            str(csv_path),
            "--pilot-name",
            "P_REAL_MISMATCH",
            "--evidence-dir",
            str(EVIDENCE / "invalid"),
            "--out",
            str(out_dir),
        ]
    )

    report = _read_json(out_dir / "pilot_validation_report.json")
    mismatches = report["evidence_summary"]["photo_reference_row_mismatches"]
    assert mismatches
    assert mismatches[0]["pole_id"] == "P008-500"
    assert mismatches[0]["parsed_pole_id"] == "P999-999"


def test_duplicate_pole_id_remains_blocked_and_slash_date_remains_invalid(
    tmp_path: Path,
) -> None:
    dup_out = tmp_path / "dup_out"
    invalid_out = tmp_path / "invalid_out"

    validate_stage4_pilot.main(
        [
            "--csv",
            str(FIXTURES / "pilot_duplicate_identity_sample.csv"),
            "--out",
            str(dup_out),
        ]
    )
    validate_stage4_pilot.main(
        [
            "--csv",
            str(FIXTURES / "pilot_invalid_sample.csv"),
            "--out",
            str(invalid_out),
        ]
    )

    dup_report = _read_json(dup_out / "pilot_validation_report.json")
    invalid_report = _read_json(invalid_out / "pilot_validation_report.json")

    assert dup_report["validation_summary"]["duplicate_pole_id_count"] == 1
    assert dup_report["stage4c_gate_status"]["decision"] == "NO-GO"
    assert any("Duplicate pole_id" in item for item in dup_report["top_blockers"])
    assert any("capture_date" in item["message"] for item in invalid_report["top_issues"])


def test_evidence_folder_missing_is_reported(tmp_path: Path) -> None:
    out_dir = tmp_path / "missing_evidence"
    missing_dir = tmp_path / "does_not_exist"

    rc = validate_stage4_pilot.main(
        [
            "--csv",
            str(FIXTURES / "pilot_valid_sample.csv"),
            "--evidence-dir",
            str(missing_dir),
            "--out",
            str(out_dir),
        ]
    )

    report = _read_json(out_dir / "pilot_validation_report.json")
    assert rc == 0
    assert report["evidence_summary"]["status"] == "missing"
    assert report["stage4c_gate_status"]["decision"] == "PARTIAL / RE-PILOT REQUIRED"
    assert report["evidence_summary"]["missing_referenced_photos"]


def test_evidence_folder_empty_is_reported(tmp_path: Path) -> None:
    out_dir = tmp_path / "empty_evidence"
    empty_dir = tmp_path / "empty"
    empty_dir.mkdir()

    rc = validate_stage4_pilot.main(
        [
            "--csv",
            str(FIXTURES / "pilot_valid_sample.csv"),
            "--evidence-dir",
            str(empty_dir),
            "--out",
            str(out_dir),
        ]
    )

    report = _read_json(out_dir / "pilot_validation_report.json")
    assert rc == 0
    assert report["evidence_summary"]["status"] == "empty"
    assert report["evidence_summary"]["is_empty"] is True
    assert report["evidence_summary"]["missing_referenced_photos"]


def test_multiple_photo_references_in_one_row_are_supported(tmp_path: Path) -> None:
    csv_path = tmp_path / "multi_refs.csv"
    evidence_dir = tmp_path / "evidence"
    evidence_dir.mkdir()
    for name in ("P008-500_01_context.jpg", "P008-500_02_support.jpg"):
        (evidence_dir / name).write_text("fixture", encoding="utf-8")

    _write_csv(
        csv_path,
        [
            "pole_id",
            "capture_source",
            "captured_by",
            "capture_date",
            "condition",
            "photo_reference",
            "source",
        ],
        [
            [
                "P008-500",
                "surveyor_tablet",
                "Noel Collins",
                "2026-05-11",
                "good",
                "P008-500_01_context.jpg; P008-500_02_support.jpg",
                "structured_capture",
            ]
        ],
    )
    out_dir = tmp_path / "multi_refs_out"

    validate_stage4_pilot.main(
        [
            "--csv",
            str(csv_path),
            "--evidence-dir",
            str(evidence_dir),
            "--out",
            str(out_dir),
        ]
    )

    report = _read_json(out_dir / "pilot_validation_report.json")
    evidence = report["evidence_summary"]
    assert evidence["rows_with_multiple_photo_references"] == 1
    assert evidence["referenced_photos_total"] == 2
    assert evidence["referenced_photos_found"] == 2


def test_real_pilot_folders_are_ignored_by_git() -> None:
    result = subprocess.run(
        [
            "git",
            "check-ignore",
            "-v",
            "real_pilot_data/example.csv",
            "validation_runs/stage4_pilots/P_REAL_001/pilot_validation_report.json",
        ],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0
    assert ".gitignore" in result.stdout
    assert "real_pilot_data/" in result.stdout
    assert "validation_runs/" in result.stdout or "validation_runs/stage4_pilots/" in result.stdout


def test_cli_does_not_write_to_live_job_outputs(tmp_path: Path) -> None:
    out_dir = tmp_path / "isolated_out"
    uploads_dir = REPO_ROOT / "uploads"
    before_exists = uploads_dir.exists()
    before_listing = sorted(str(path) for path in uploads_dir.rglob("*")) if before_exists else []

    validate_stage4_pilot.main(
        [
            "--csv",
            str(FIXTURES / "pilot_valid_sample.csv"),
            "--evidence-dir",
            str(EVIDENCE / "valid"),
            "--out",
            str(out_dir),
        ]
    )

    assert (out_dir / "pilot_validation_report.json").exists()
    assert (out_dir / "pilot_validation_report.md").exists()

    after_exists = uploads_dir.exists()
    after_listing = sorted(str(path) for path in uploads_dir.rglob("*")) if after_exists else []
    assert before_exists == after_exists
    assert before_listing == after_listing


def test_missing_csv_is_handled_gracefully(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    out_dir = tmp_path / "missing_csv"
    rc = validate_stage4_pilot.main(
        [
            "--csv",
            str(tmp_path / "no_such.csv"),
            "--out",
            str(out_dir),
        ]
    )

    captured = capsys.readouterr().out
    report = _read_json(out_dir / "pilot_validation_report.json")
    assert rc == 1
    assert "STAGE 4 PILOT RESULT: NO-GO" in captured
    assert "Pilot CSV not found" in captured
    assert report["stage4c_gate_status"]["decision"] == "NO-GO"


def test_malformed_csv_is_handled_gracefully(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    csv_path = tmp_path / "malformed.csv"
    csv_path.write_text(
        "pole_id,capture_source\nP008-001,surveyor_tablet,extra\n", encoding="utf-8"
    )
    out_dir = tmp_path / "malformed_out"

    rc = validate_stage4_pilot.main(
        [
            "--csv",
            str(csv_path),
            "--out",
            str(out_dir),
        ]
    )

    captured = capsys.readouterr().out
    report = _read_json(out_dir / "pilot_validation_report.json")
    assert rc == 1
    assert "STAGE 4 PILOT RESULT: NO-GO" in captured
    assert "Malformed CSV row" in captured
    assert report["top_issues"][0]["message"].startswith("Malformed CSV row")


def test_cli_can_be_run_via_subprocess_on_valid_fixture(tmp_path: Path) -> None:
    out_dir = tmp_path / "subprocess_out"
    result = subprocess.run(
        [
            sys.executable,
            str(REPO_ROOT / "scripts" / "validate_stage4_pilot.py"),
            "--csv",
            str(FIXTURES / "pilot_valid_sample.csv"),
            "--pilot-name",
            "P_REAL_SUBPROC",
            "--evidence-dir",
            str(EVIDENCE / "valid"),
            "--out",
            str(out_dir),
        ],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    assert "STAGE 4 PILOT RESULT: PARTIAL" in result.stdout
    assert "Next action:" in result.stdout
    assert (out_dir / "pilot_validation_report.json").exists()
