from __future__ import annotations

import csv
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile

from app.structured_capture_schema import get_stage4_template_headers
from app.structured_capture_validators import validate_stage4_import_preview
from scripts import convert_stage4_workbook_to_pilot_csv
from scripts.validate_stage4_pilot import load_pilot_csv


def _build_workbook(path: Path) -> None:
    def inline_sheet(rows: list[list[str]]) -> str:
        xml_rows: list[str] = []
        for row_number, row in enumerate(rows, start=1):
            cells: list[str] = []
            for column_index, value in enumerate(row, start=1):
                if value == "":
                    continue
                letter = chr(64 + column_index)
                escaped = str(value).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
                cells.append(
                    f'<c r="{letter}{row_number}" t="inlineStr"><is><t>{escaped}</t></is></c>'
                )
            xml_rows.append(f'<row r="{row_number}">{"".join(cells)}</row>')
        return (
            '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
            '<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">'
            "<sheetData>" + "".join(xml_rows) + "</sheetData></worksheet>"
        )

    notes_rows = [["This", "sheet", "is", "not", "the", "capture", "sheet"]]
    raw_rows = [
        [
            "Point",
            "Project",
            "File",
            "capture_source",
            "captured_by",
            "capture_date",
            "Feature Code",
            "Role",
            "captured_material",
            "height",
            "condition",
            "notes",
            "photo_ref",
            "source",
        ],
        [
            "P011-001",
            "P011",
            "F001",
            "surveyor_tablet",
            "Noel Collins",
            "2026-05-11",
            "Pol",
            "existing",
            "wood",
            "9.2",
            "good",
            "Existing workbook rehearsal row",
            "P011-001_01_support.jpg",
            "structured_capture",
        ],
    ]
    office_rows = [
        ["pole_id", "capture_source", "captured_by", "capture_date", "source"],
        ["OFFICE-001", "desktop", "Analyst", "2026-05-12", "structured_capture"],
    ]

    workbook_xml = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main"
 xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">
  <sheets>
    <sheet name="Notes" sheetId="1" r:id="rId1"/>
    <sheet name="Raw Capture" sheetId="2" r:id="rId2"/>
    <sheet name="Office Copy" sheetId="3" r:id="rId3"/>
  </sheets>
</workbook>
"""
    relationship_type = (
        "http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet"
    )
    workbook_rels = f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="{relationship_type}" Target="worksheets/sheet1.xml"/>
  <Relationship Id="rId2" Type="{relationship_type}" Target="worksheets/sheet2.xml"/>
  <Relationship Id="rId3" Type="{relationship_type}" Target="worksheets/sheet3.xml"/>
</Relationships>
"""
    package_relationships = "application/vnd.openxmlformats-package.relationships+xml"
    worksheet_content_type = (
        "application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"
    )
    workbook_content_type = (
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"
    )
    content_types = f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
  <Default Extension="rels" ContentType="{package_relationships}"/>
  <Default Extension="xml" ContentType="application/xml"/>
  <Override PartName="/xl/workbook.xml" ContentType="{workbook_content_type}"/>
  <Override PartName="/xl/worksheets/sheet1.xml" ContentType="{worksheet_content_type}"/>
  <Override PartName="/xl/worksheets/sheet2.xml" ContentType="{worksheet_content_type}"/>
  <Override PartName="/xl/worksheets/sheet3.xml" ContentType="{worksheet_content_type}"/>
</Types>
"""
    office_document_type = (
        "http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument"
    )
    root_rels = f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rIdWorkbook" Type="{office_document_type}" Target="xl/workbook.xml"/>
</Relationships>
"""

    with ZipFile(path, "w", compression=ZIP_DEFLATED) as archive:
        archive.writestr("[Content_Types].xml", content_types)
        archive.writestr("_rels/.rels", root_rels)
        archive.writestr("xl/workbook.xml", workbook_xml)
        archive.writestr("xl/_rels/workbook.xml.rels", workbook_rels)
        archive.writestr("xl/worksheets/sheet1.xml", inline_sheet(notes_rows))
        archive.writestr("xl/worksheets/sheet2.xml", inline_sheet(raw_rows))
        archive.writestr("xl/worksheets/sheet3.xml", inline_sheet(office_rows))


def _read_csv(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        return list(reader.fieldnames or []), list(reader)


def test_converter_defaults_to_raw_capture_sheet_and_writes_stage4_headers(tmp_path: Path) -> None:
    workbook_path = tmp_path / "survey_records_sorted_tabs.xlsx"
    output_path = tmp_path / "pilot_existing_P011.csv"
    _build_workbook(workbook_path)

    rc = convert_stage4_workbook_to_pilot_csv.main(
        ["--xlsx", str(workbook_path), "--out", str(output_path)]
    )

    headers, rows = _read_csv(output_path)
    assert rc == 0
    assert headers == get_stage4_template_headers()
    assert len(rows) == 1
    assert rows[0]["pole_id"] == "P011-001"
    assert rows[0]["project_id"] == "P011"
    assert rows[0]["file_id"] == "F001"
    assert rows[0]["structure_type"] == "Pol"
    assert rows[0]["asset_intent"] == "existing"
    assert rows[0]["material"] == "wood"
    assert rows[0]["measured_height_m"] == "9.2"
    assert rows[0]["survey_notes"] == "Existing workbook rehearsal row"
    assert rows[0]["photo_reference"] == "P011-001_01_support.jpg"


def test_converter_honours_explicit_sheet_name(tmp_path: Path) -> None:
    workbook_path = tmp_path / "survey_records_sorted_tabs.xlsx"
    output_path = tmp_path / "pilot_existing_office.csv"
    _build_workbook(workbook_path)

    convert_stage4_workbook_to_pilot_csv.main(
        [
            "--xlsx",
            str(workbook_path),
            "--sheet",
            "Office Copy",
            "--out",
            str(output_path),
        ]
    )

    _, rows = _read_csv(output_path)
    assert len(rows) == 1
    assert rows[0]["pole_id"] == "OFFICE-001"
    assert rows[0]["capture_source"] == "desktop"


def test_converted_csv_can_be_validated_by_stage4_preview(tmp_path: Path) -> None:
    workbook_path = tmp_path / "survey_records_sorted_tabs.xlsx"
    output_path = tmp_path / "pilot_existing_P011.csv"
    _build_workbook(workbook_path)

    convert_stage4_workbook_to_pilot_csv.main(
        ["--xlsx", str(workbook_path), "--out", str(output_path)]
    )

    headers, rows = load_pilot_csv(output_path)
    preview = validate_stage4_import_preview(headers=headers, rows=rows)
    assert preview["total_rows"] == 1
    assert preview["valid_rows"] == 1
    assert preview["invalid_rows"] == 0


def test_converter_reports_missing_sheet_name(tmp_path: Path) -> None:
    workbook_path = tmp_path / "survey_records_sorted_tabs.xlsx"
    output_path = tmp_path / "pilot_existing_P011.csv"
    _build_workbook(workbook_path)

    try:
        convert_stage4_workbook_to_pilot_csv.main(
            [
                "--xlsx",
                str(workbook_path),
                "--sheet",
                "Missing Sheet",
                "--out",
                str(output_path),
            ]
        )
    except ValueError as exc:
        message = str(exc)
    else:  # pragma: no cover - defensive
        raise AssertionError("Expected ValueError for missing worksheet")

    assert "Missing Sheet" in message


def test_real_pilot_local_data_paths_remain_git_ignored() -> None:
    gitignore_text = (Path(__file__).resolve().parent.parent / ".gitignore").read_text(
        encoding="utf-8"
    )
    assert "real_pilot_data/" in gitignore_text
    assert "validation_runs/stage4_pilots/" in gitignore_text
