"""Tests for the Stage 4 template generator script."""

from __future__ import annotations

import csv
from pathlib import Path

from app.structured_capture_schema import get_stage4_template_headers
from scripts import generate_structured_capture_template


def test_cli_writes_csv_to_requested_output_path(tmp_path: Path) -> None:
    target = tmp_path / "out" / "stage4.csv"
    rc = generate_structured_capture_template.main(["--output", str(target)])

    assert rc == 0
    assert target.exists()
    rows = list(csv.reader(target.read_text(encoding="utf-8").splitlines()))
    assert rows, "CSV must contain at least the header row"
    assert rows[0] == get_stage4_template_headers()


def test_headers_match_schema(tmp_path: Path) -> None:
    target = tmp_path / "stage4.csv"
    generate_structured_capture_template.main(["--output", str(target)])

    rows = list(csv.reader(target.read_text(encoding="utf-8").splitlines()))
    schema_headers = get_stage4_template_headers()
    assert rows[0] == schema_headers
    # the only data row should be the header — template ships empty
    assert len(rows) == 1


def test_include_descriptions_mode_writes_useful_content(tmp_path: Path) -> None:
    target = tmp_path / "stage4_described.csv"
    generate_structured_capture_template.main(["--output", str(target), "--include-descriptions"])

    text = target.read_text(encoding="utf-8")
    assert text.startswith("# GridFlow Stage 4 structured capture template")
    # mentions every group label
    for label in (
        "Pole specification",
        "Condition / defects",
        "Electrical / conductor",
        "Structural support",
        "Equipment / pole-top",
        "Capture metadata",
    ):
        assert label in text
    # mentions each required field name
    for required_field in ("capture_source", "captured_by", "capture_date"):
        assert required_field in text

    # CSV header row still parses cleanly when comment lines are stripped
    body_lines = [line for line in text.splitlines() if not line.startswith("#")]
    rows = list(csv.reader(body_lines))
    assert rows[0] == get_stage4_template_headers()


def test_script_exposes_main_with_default_argv() -> None:
    assert callable(generate_structured_capture_template.main)
    # main(argv=None) should be valid; we exercise it with a tmp output via stdout mode
    import contextlib
    import io

    buffer = io.StringIO()
    with contextlib.redirect_stdout(buffer):
        rc = generate_structured_capture_template.main(["--stdout"])
    assert rc == 0
    output = buffer.getvalue()
    assert "capture_source" in output


def test_no_app_runtime_needed(monkeypatch) -> None:
    """Ensure the script can build the template without any Flask state."""

    # Sabotage the create_app entry point: if the generator touched it,
    # this test would fail. The schema import is the only app-package
    # dependency expected.
    import app

    def _explode(*args, **kwargs):  # pragma: no cover - guard only
        raise AssertionError("Stage 4 template generator must not start the Flask app")

    if hasattr(app, "create_app"):
        monkeypatch.setattr(app, "create_app", _explode)

    rendered = generate_structured_capture_template.render_template(include_descriptions=False)
    assert get_stage4_template_headers()[0] in rendered
