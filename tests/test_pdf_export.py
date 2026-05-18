from __future__ import annotations

from pathlib import Path

from gridflow.exports import SurveyPDFExporter
from tests.test_exports import _make_survey


def test_pdf_export_creates_file(tmp_path: Path) -> None:
    survey_root, trace_path = _make_survey(tmp_path)
    output = tmp_path / "survey.pdf"
    SurveyPDFExporter().export(survey_root, trace_path, output)
    assert output.exists()


def test_pdf_export_file_size_gt_1kb(tmp_path: Path) -> None:
    survey_root, trace_path = _make_survey(tmp_path)
    output = tmp_path / "survey.pdf"
    SurveyPDFExporter().export(survey_root, trace_path, output)
    assert output.stat().st_size > 1024


def test_pdf_export_missing_trace_does_not_crash(tmp_path: Path) -> None:
    survey_root, _trace_path = _make_survey(tmp_path)
    output = tmp_path / "survey.pdf"
    SurveyPDFExporter().export(survey_root, tmp_path / "missing.geojson", output)
    assert output.exists()


def test_pdf_export_missing_photos_does_not_crash(tmp_path: Path) -> None:
    survey_root, trace_path = _make_survey(tmp_path, with_photos=False)
    output = tmp_path / "survey.pdf"
    SurveyPDFExporter().export(survey_root, trace_path, output)
    assert output.exists()
