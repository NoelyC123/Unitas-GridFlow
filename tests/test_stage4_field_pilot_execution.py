"""Execution-system tests for the Stage 4 real field pilot validator CLI."""

from __future__ import annotations

import csv
import json
import subprocess
import sys
from pathlib import Path

from scripts import validate_stage4_pilot

REPO_ROOT = Path(__file__).resolve().parent.parent
FIXTURES = REPO_ROOT / "tests" / "fixtures" / "stage4"
EVIDENCE = FIXTURES / "evidence"


def _read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_csv(path: Path, headers: list[str], rows: list[list[str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(headers)
        writer.writerows(rows)


def test_cli_runs_on_valid_pilot_sample_and_writes_json_and_markdown(
    tmp_path: Path, capsys
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
    assert "Stage 4 pilot: P_REAL_001" in captured
    assert json_path.exists()
    assert md_path.exists()

    report = _read_json(json_path)
    assert report["validation_summary"]["total_rows"] == 7
    assert report["validation_summary"]["merge_ready_rows"] == 6
    assert report["gate_recommendation"] == "PARTIAL / RE-PILOT REQUIRED"
    assert report["evidence_findings"]["referenced_photos_found"] == 6
    assert report["evidence_findings"]["missing_referenced_photos"] == []
    assert "Stage 4C readiness status" in md_path.read_text(encoding="utf-8")


def test_cli_runs_on_invalid_pilot_sample_and_reports_no_go(tmp_path: Path) -> None:
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

    report = _read_json(out_dir / "pilot_validation_report.json")

    assert rc == 0
    assert report["validation_summary"]["blocked_rows"] == 1
    assert report["validation_summary"]["invalid_rows"] == 4
    assert report["gate_recommendation"] == "NO-GO"


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
    evidence = report["evidence_findings"]

    assert rc == 0
    assert "P008-104_01_stay.jpg" in evidence["missing_referenced_photos"]
    assert "P999-999_01_context.jpg" in evidence["unreferenced_photos"]
    assert "P008-102_01_support.jpg" in evidence["duplicate_photo_names"]
    assert any(item.endswith("badname.jpg") for item in evidence["invalid_photo_naming_patterns"])


def test_photo_reference_that_does_not_match_csv_pole_id_is_detected(tmp_path: Path) -> None:
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
    mismatches = report["evidence_findings"]["photo_reference_row_mismatches"]
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
    assert any("Duplicate pole_id" in item for item in dup_report["top_blockers"])
    assert any("capture_date" in item for item in invalid_report["top_blockers"])


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
    assert "Recommendation: PARTIAL / RE-PILOT REQUIRED" in result.stdout
    assert (out_dir / "pilot_validation_report.json").exists()
