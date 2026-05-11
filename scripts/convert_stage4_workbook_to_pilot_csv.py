#!/usr/bin/env python3
"""Convert an existing workbook sheet into a Stage 4 pilot-compatible CSV."""

from __future__ import annotations

import argparse
import csv
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from xml.etree import ElementTree as ET
from zipfile import ZipFile

from app.structured_capture_schema import get_stage4_field_definition, get_stage4_fields

NS_MAIN = "http://schemas.openxmlformats.org/spreadsheetml/2006/main"
NS_REL = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
NS_PACKAGE = "http://schemas.openxmlformats.org/package/2006/relationships"
NSMAP = {"main": NS_MAIN, "rel": NS_REL, "pkg": NS_PACKAGE}


def _normalise_header(value: Any) -> str:
    text = "" if value is None else str(value).strip().lower()
    if not text:
        return ""
    text = re.sub(r"[^a-z0-9]+", "_", text)
    return re.sub(r"_+", "_", text).strip("_")


def _header_candidates(field_name: str) -> list[str]:
    definition = get_stage4_field_definition(field_name)
    if not definition:
        return []
    candidates = [definition["field_name"], *definition.get("aliases", ())]
    return [_normalise_header(candidate) for candidate in candidates if candidate]


def _build_header_lookup() -> dict[str, str]:
    mapping: dict[str, str] = {}
    for definition in get_stage4_fields():
        field_name = definition["field_name"]
        for candidate in _header_candidates(field_name):
            mapping.setdefault(candidate, field_name)
    return mapping


HEADER_LOOKUP = _build_header_lookup()
TEMPLATE_HEADERS = [definition["field_name"] for definition in get_stage4_fields()]


@dataclass
class SheetAnalysis:
    sheet_name: str
    source_headers: list[str]
    matching_fields: list[str]
    missing_fields: list[str]
    extra_columns: list[str]
    duplicate_target_fields: list[str]
    header_mapping: dict[str, str]
    row_count: int


@dataclass
class WorkbookSheet:
    title: str
    rows: list[list[str]]


@dataclass
class WorkbookData:
    sheets: list[WorkbookSheet]


def _column_index(cell_ref: str) -> int:
    letters = "".join(character for character in cell_ref if character.isalpha()).upper()
    index = 0
    for character in letters:
        index = index * 26 + (ord(character) - 64)
    return max(index - 1, 0)


def _load_shared_strings(archive: ZipFile) -> list[str]:
    try:
        data = archive.read("xl/sharedStrings.xml")
    except KeyError:
        return []

    root = ET.fromstring(data)
    values: list[str] = []
    for item in root.findall("main:si", NSMAP):
        texts = [node.text or "" for node in item.findall(".//main:t", NSMAP)]
        values.append("".join(texts))
    return values


def _sheet_cell_value(cell: ET.Element, shared_strings: list[str]) -> str:
    cell_type = cell.attrib.get("t")
    value_node = cell.find("main:v", NSMAP)

    if cell_type == "inlineStr":
        texts = [node.text or "" for node in cell.findall(".//main:t", NSMAP)]
        return "".join(texts).strip()

    if value_node is None or value_node.text is None:
        return ""

    raw_value = value_node.text
    if cell_type == "s":
        try:
            return shared_strings[int(raw_value)].strip()
        except (ValueError, IndexError):
            return raw_value.strip()
    return raw_value.strip()


def _load_sheet_rows(archive: ZipFile, target: str, shared_strings: list[str]) -> list[list[str]]:
    root = ET.fromstring(archive.read(target))
    rows: list[list[str]] = []
    for row in root.findall(".//main:sheetData/main:row", NSMAP):
        values: list[str] = []
        for cell in row.findall("main:c", NSMAP):
            ref = cell.attrib.get("r", "")
            index = _column_index(ref) if ref else len(values)
            while len(values) <= index:
                values.append("")
            values[index] = _sheet_cell_value(cell, shared_strings)
        rows.append(values)
    return rows


def load_workbook_data(xlsx_path: Path) -> WorkbookData:
    with ZipFile(xlsx_path) as archive:
        workbook_root = ET.fromstring(archive.read("xl/workbook.xml"))
        rels_root = ET.fromstring(archive.read("xl/_rels/workbook.xml.rels"))
        shared_strings = _load_shared_strings(archive)

        relationships = {
            rel.attrib["Id"]: rel.attrib["Target"]
            for rel in rels_root.findall("pkg:Relationship", NSMAP)
        }

        sheets: list[WorkbookSheet] = []
        for sheet in workbook_root.findall("main:sheets/main:sheet", NSMAP):
            name = sheet.attrib.get("name", "")
            rel_id = sheet.attrib.get(f"{{{NS_REL}}}id")
            if not name or not rel_id:
                continue
            target = relationships.get(rel_id, "")
            if not target:
                continue
            target_path = target if target.startswith("xl/") else f"xl/{target}"
            sheets.append(
                WorkbookSheet(
                    title=name,
                    rows=_load_sheet_rows(archive, target_path, shared_strings),
                )
            )
    return WorkbookData(sheets=sheets)


def _sheet_rows(worksheet: WorkbookSheet) -> tuple[list[str], list[list[str]]]:
    header_row_index: int | None = None
    headers: list[str] = []

    for index, row in enumerate(worksheet.rows, start=1):
        values = ["" if value is None else str(value).strip() for value in row]
        if any(values):
            header_row_index = index
            headers = values
            break

    if header_row_index is None:
        return [], []

    data_rows: list[list[str]] = []
    for row in worksheet.rows[header_row_index:]:
        values = ["" if value is None else str(value).strip() for value in row[: len(headers)]]
        if any(values):
            if len(values) < len(headers):
                values.extend([""] * (len(headers) - len(values)))
            data_rows.append(values)

    return headers, data_rows


def analyse_sheet(worksheet: WorkbookSheet) -> tuple[SheetAnalysis, list[list[str]]]:
    headers, rows = _sheet_rows(worksheet)
    mapped_fields: list[str] = []
    header_mapping: dict[str, str] = {}
    source_headers: list[str] = []

    for header in headers:
        source_headers.append(header)
        canonical = HEADER_LOOKUP.get(_normalise_header(header), "")
        if canonical:
            mapped_fields.append(canonical)
            header_mapping[header] = canonical

    matching_fields = sorted(dict.fromkeys(mapped_fields))
    duplicate_target_fields = sorted(
        field_name for field_name, count in _count_items(mapped_fields).items() if count > 1
    )
    missing_fields = [field for field in TEMPLATE_HEADERS if field not in matching_fields]
    extra_columns = [header for header in headers if header not in header_mapping]

    return (
        SheetAnalysis(
            sheet_name=worksheet.title,
            source_headers=source_headers,
            matching_fields=matching_fields,
            missing_fields=missing_fields,
            extra_columns=extra_columns,
            duplicate_target_fields=duplicate_target_fields,
            header_mapping=header_mapping,
            row_count=len(rows),
        ),
        rows,
    )


def _count_items(items: list[str]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for item in items:
        counts[item] = counts.get(item, 0) + 1
    return counts


def choose_sheet(
    workbook: WorkbookData, explicit_sheet: str | None = None
) -> tuple[SheetAnalysis, list[list[str]]]:
    worksheets = list(workbook.sheets)
    if not worksheets:
        raise ValueError("Workbook does not contain any worksheets.")

    analyses: list[tuple[SheetAnalysis, list[list[str]]]] = [
        analyse_sheet(sheet) for sheet in worksheets
    ]

    if explicit_sheet:
        for analysis, rows in analyses:
            if analysis.sheet_name == explicit_sheet:
                return analysis, rows
        available = ", ".join(sheet.title for sheet in worksheets)
        raise ValueError(f"Sheet '{explicit_sheet}' not found. Available sheets: {available}")

    for analysis, rows in analyses:
        if _normalise_header(analysis.sheet_name) == "raw_capture":
            return analysis, rows

    return max(
        analyses,
        key=lambda item: (
            len(item[0].matching_fields),
            item[0].row_count,
            item[0].sheet_name.lower(),
        ),
    )


def convert_rows(headers: list[str], rows: list[list[str]]) -> list[dict[str, str]]:
    canonical_sources: dict[str, list[int]] = {}
    for index, header in enumerate(headers):
        canonical = HEADER_LOOKUP.get(_normalise_header(header))
        if canonical:
            canonical_sources.setdefault(canonical, []).append(index)

    converted: list[dict[str, str]] = []
    for row in rows:
        converted_row = {field: "" for field in TEMPLATE_HEADERS}
        for field_name, indexes in canonical_sources.items():
            for index in indexes:
                if index < len(row):
                    value = row[index].strip()
                    if value:
                        converted_row[field_name] = value
                        break
        converted.append(converted_row)
    return converted


def write_csv(output_path: Path, rows: list[dict[str, str]]) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=TEMPLATE_HEADERS)
        writer.writeheader()
        writer.writerows(rows)


def convert_workbook_to_pilot_csv(
    *,
    xlsx_path: Path,
    output_path: Path,
    sheet_name: str | None = None,
) -> dict[str, Any]:
    workbook = load_workbook_data(xlsx_path)
    selected_analysis, sheet_rows = choose_sheet(workbook, explicit_sheet=sheet_name)
    converted_rows = convert_rows(selected_analysis.source_headers, sheet_rows)
    write_csv(output_path, converted_rows)

    workbook_sheets = [sheet.title for sheet in workbook.sheets]
    best_match_counts = {
        analysis.sheet_name: len(analysis.matching_fields)
        for analysis, _ in (analyse_sheet(sheet) for sheet in workbook.sheets)
    }
    return {
        "xlsx_path": str(xlsx_path),
        "output_path": str(output_path),
        "selected_sheet": selected_analysis.sheet_name,
        "available_sheets": workbook_sheets,
        "best_match_counts": best_match_counts,
        "matching_fields": selected_analysis.matching_fields,
        "missing_fields": selected_analysis.missing_fields,
        "extra_columns": selected_analysis.extra_columns,
        "duplicate_target_fields": selected_analysis.duplicate_target_fields,
        "row_count": selected_analysis.row_count,
    }


def build_argument_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Convert a workbook sheet into a Stage 4 pilot-compatible CSV."
    )
    parser.add_argument("--xlsx", required=True, help="Path to the source workbook (.xlsx).")
    parser.add_argument("--out", required=True, help="Path to the converted CSV output.")
    parser.add_argument(
        "--sheet",
        help=(
            "Optional explicit sheet name. Defaults to 'Raw Capture' if present, "
            "otherwise the best field match."
        ),
    )
    return parser


def _print_summary(result: dict[str, Any]) -> None:
    matching = ", ".join(result["matching_fields"]) or "none"
    missing = ", ".join(result["missing_fields"]) or "none"
    extras = ", ".join(result["extra_columns"]) or "none"

    print("Stage 4 workbook conversion complete")
    print(f"Source workbook: {result['xlsx_path']}")
    print(f"Selected sheet: {result['selected_sheet']}")
    print(f"Converted CSV: {result['output_path']}")
    print(f"Available sheets: {', '.join(result['available_sheets'])}")
    print(f"Converted rows: {result['row_count']}")
    print(f"Matching fields ({len(result['matching_fields'])}): {matching}")
    print(f"Missing Stage 4 fields ({len(result['missing_fields'])}): {missing}")
    print(f"Extra workbook columns ({len(result['extra_columns'])}): {extras}")
    if result["duplicate_target_fields"]:
        print("Duplicate mapped targets: " + ", ".join(result["duplicate_target_fields"]))


def main(argv: list[str] | None = None) -> int:
    parser = build_argument_parser()
    args = parser.parse_args(argv)

    xlsx_path = Path(args.xlsx).expanduser().resolve()
    output_path = Path(args.out).expanduser().resolve()

    if not xlsx_path.exists():
        parser.error(f"Workbook not found: {xlsx_path}")

    result = convert_workbook_to_pilot_csv(
        xlsx_path=xlsx_path,
        output_path=output_path,
        sheet_name=args.sheet,
    )
    _print_summary(result)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
