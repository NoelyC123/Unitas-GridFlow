#!/usr/bin/env python3
"""Prepare and compare Stage 4 controlled pilot baseline data.

This helper stays outside live GridFlow runtime behaviour. It can:

1. Inspect a local baseline CSV and generate a Stage 4 starter capture CSV.
2. Compare a completed Stage 4 capture CSV against the baseline using exact
   pole_id matching only (after approved whitespace/case normalisation).

The helper must not write to live job outputs and must not commit local pilot
data, baseline files, or generated reports.
"""

from __future__ import annotations

import argparse
import csv
import sys
from collections import defaultdict
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from app.structured_capture_schema import get_stage4_template_headers  # noqa: E402

UNSAFE_IDENTITY_TOKENS = {"", "n/a", "na", "null", "unknown", "?", "none", "missing"}
HEADER_IDENTITY_CANDIDATES = (
    "pole_id",
    "point",
    "point_id",
    "point_no",
    "pt",
    "pnt",
    "name",
    "asset_id",
    "support_id",
    "number",
    "no",
)
HEADER_TYPE_CANDIDATES = (
    "structure_type",
    "feature_code",
    "feat_code",
    "code",
    "fc",
    "type",
)
STRUCTURAL_TYPES = {
    "pol",
    "angle",
    "expole",
    "terminal",
    "pole",
    "wood pole",
    "steel pole",
    "concrete pole",
    "composite pole",
    "prpole",
    "prangle",
    "stay",
    "stay pole",
    "service pole",
}
TEXT_COLS = 15


def _relative(path: Path | None) -> str | None:
    if path is None:
        return None
    try:
        return str(path.resolve().relative_to(REPO_ROOT))
    except ValueError:
        return str(path.resolve())


def normalize_pole_id(value: Any) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    if not text or text.lower() in UNSAFE_IDENTITY_TOKENS:
        return None
    return text.upper()


def _safe_structure_type(value: Any) -> str:
    text = str(value or "").strip()
    return text if text else "unknown"


def _asset_intent_for_structure(structure_type: str) -> str:
    lowered = structure_type.strip().lower()
    if lowered in {"prpole", "prangle"}:
        return "proposed"
    if lowered in STRUCTURAL_TYPES:
        return "existing"
    return "unknown"


def _is_structural_type(value: Any) -> bool:
    return str(value or "").strip().lower() in STRUCTURAL_TYPES


def _looks_like_raw_controller_dump(first_row: list[str]) -> bool:
    if not first_row:
        return False
    first = str(first_row[0]).strip()
    row_text = ",".join(cell.strip() for cell in first_row if cell is not None)
    return first.startswith("Job:") and "Version:" in row_text and "Units:" in row_text


@dataclass
class BaselineCandidate:
    pole_id: str
    normalized_pole_id: str
    structure_type: str
    source_row_number: int
    remark: str = ""
    raw_height: str = ""
    land_use: str = ""


@dataclass
class BaselineExtract:
    baseline_csv: Path
    format_name: str
    total_rows: int
    candidate_count: int
    identity_source: str
    type_source: str
    all_rows_with_identity: int
    duplicates: dict[str, list[str]]
    candidates: list[BaselineCandidate]
    warnings: list[str]
    headers: list[str] | None = None

    @property
    def blocking(self) -> bool:
        return bool(self.duplicates) or self.candidate_count == 0


def _parse_attribute_pairs(values: list[str]) -> dict[str, str]:
    attributes: dict[str, str] = {}
    index = 5
    while index + 1 < len(values):
        key = str(values[index]).strip()
        value = str(values[index + 1]).strip()
        index += 2
        if ":" not in key:
            continue
        attr_name = key.split(":", 1)[1].strip().upper()
        if not attr_name:
            continue
        attributes[attr_name] = value
    return attributes


def _extract_raw_controller(path: Path) -> BaselineExtract:
    candidates: list[BaselineCandidate] = []
    all_rows_with_identity = 0
    total_rows = 0

    with path.open(newline="", encoding="utf-8-sig") as handle:
        reader = csv.reader(handle)
        first_row = next(reader, [])
        if not _looks_like_raw_controller_dump(first_row):
            raise ValueError("Baseline does not look like a raw controller dump.")

        for row_number, row in enumerate(reader, start=2):
            values = [str(value).strip() for value in row]
            if not any(values):
                continue
            total_rows += 1
            point_value = values[0] if values else ""
            structure_type = values[4] if len(values) > 4 else ""

            normalized = normalize_pole_id(point_value)
            if normalized:
                all_rows_with_identity += 1

            if not normalized or not _is_structural_type(structure_type):
                continue

            attrs = _parse_attribute_pairs(values)
            candidates.append(
                BaselineCandidate(
                    pole_id=point_value.strip(),
                    normalized_pole_id=normalized,
                    structure_type=structure_type.strip(),
                    source_row_number=row_number,
                    remark=attrs.get("REMARK", ""),
                    raw_height=attrs.get("HEIGHT", ""),
                    land_use=attrs.get("LAND USE", ""),
                )
            )

    duplicates = _duplicate_candidate_ids(candidates)
    warnings: list[str] = []
    if duplicates:
        warnings.append("Duplicate normalized pole_id values found in the baseline candidate set.")
    if not candidates:
        warnings.append(
            "No structural pole/support candidates were extracted from the raw controller dump."
        )

    return BaselineExtract(
        baseline_csv=path,
        format_name="raw_controller_dump",
        total_rows=total_rows,
        candidate_count=len(candidates),
        identity_source="column 0 (point number)",
        type_source="column 4 (feature code)",
        all_rows_with_identity=all_rows_with_identity,
        duplicates=duplicates,
        candidates=candidates,
        warnings=warnings,
        headers=None,
    )


def _infer_header_column(
    headers: list[str],
    candidates: tuple[str, ...],
) -> str | None:
    normalized_map = {header.strip().lower(): header for header in headers}
    for candidate in candidates:
        if candidate in normalized_map:
            return normalized_map[candidate]
    return None


def _extract_headered_csv(path: Path) -> BaselineExtract:
    with path.open(newline="", encoding="utf-8-sig") as handle:
        reader = csv.DictReader(handle)
        headers = [str(header).strip() for header in reader.fieldnames or [] if header is not None]
        if not headers:
            raise ValueError("Headered baseline CSV has no readable header row.")

        identity_column = _infer_header_column(headers, HEADER_IDENTITY_CANDIDATES)
        type_column = _infer_header_column(headers, HEADER_TYPE_CANDIDATES)
        if identity_column is None:
            raise ValueError("Could not infer a baseline identity column from the CSV headers.")

        candidates: list[BaselineCandidate] = []
        total_rows = 0
        all_rows_with_identity = 0
        for row_number, row in enumerate(reader, start=2):
            if row is None:
                continue
            total_rows += 1
            pole_value = str(row.get(identity_column, "")).strip()
            normalized = normalize_pole_id(pole_value)
            if normalized:
                all_rows_with_identity += 1

            structure_type = str(row.get(type_column, "")).strip() if type_column else ""
            if not normalized:
                continue
            if type_column and not _is_structural_type(structure_type):
                continue

            candidates.append(
                BaselineCandidate(
                    pole_id=pole_value,
                    normalized_pole_id=normalized,
                    structure_type=structure_type or "unknown",
                    source_row_number=row_number,
                    remark=str(row.get("location", "") or row.get("remarks", "")).strip(),
                )
            )

    duplicates = _duplicate_candidate_ids(candidates)
    warnings: list[str] = []
    if duplicates:
        warnings.append("Duplicate normalized pole_id values found in the baseline candidate set.")
    if not candidates:
        warnings.append(
            "No structural pole/support candidates were extracted from the headered baseline CSV."
        )

    return BaselineExtract(
        baseline_csv=path,
        format_name="headered_csv",
        total_rows=total_rows,
        candidate_count=len(candidates),
        identity_source=identity_column,
        type_source=type_column or "not found",
        all_rows_with_identity=all_rows_with_identity,
        duplicates=duplicates,
        candidates=candidates,
        warnings=warnings,
        headers=headers,
    )


def _duplicate_candidate_ids(candidates: list[BaselineCandidate]) -> dict[str, list[str]]:
    seen: dict[str, list[str]] = defaultdict(list)
    for candidate in candidates:
        seen[candidate.normalized_pole_id].append(candidate.pole_id)
    return {key: values for key, values in seen.items() if len(values) > 1}


def extract_baseline_candidates(path: Path) -> BaselineExtract:
    with path.open(newline="", encoding="utf-8-sig") as handle:
        reader = csv.reader(handle)
        first_row = next(reader, [])
    if _looks_like_raw_controller_dump(first_row):
        return _extract_raw_controller(path)
    return _extract_headered_csv(path)


def build_starter_rows(
    extract: BaselineExtract,
    pilot_name: str,
) -> list[dict[str, str]]:
    headers = get_stage4_template_headers()
    rows: list[dict[str, str]] = []
    for candidate in extract.candidates:
        row = {header: "" for header in headers}
        row["pole_id"] = candidate.pole_id
        row["project_id"] = pilot_name
        row["file_id"] = "baseline_extract"
        row["structure_type"] = _safe_structure_type(candidate.structure_type)
        row["asset_intent"] = _asset_intent_for_structure(candidate.structure_type)
        row["capture_source"] = "surveyor_tablet"
        row["source"] = "structured_capture"
        row["evidence_status"] = "unknown"
        row["confidence_level"] = "unknown"
        row["verification_required"] = "unknown"
        row["captured_by"] = ""
        row["capture_date"] = ""
        if candidate.remark:
            row["survey_notes"] = (
                f"Starter row generated from baseline. Baseline remark: {candidate.remark}"
            )
        rows.append(row)
    return rows


def write_csv(path: Path, headers: list[str], rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=headers)
        writer.writeheader()
        writer.writerows(rows)


def write_prepare_notes(
    path: Path, extract: BaselineExtract, starter_csv: Path, pilot_name: str
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# Stage 4 Controlled Pilot Baseline Extract",
        "",
        f"- Pilot name: `{pilot_name}`",
        f"- Baseline CSV: `{_relative(extract.baseline_csv)}`",
        f"- Detected format: `{extract.format_name}`",
        f"- Total baseline rows scanned: `{extract.total_rows}`",
        f"- Rows with usable pole_id values: `{extract.all_rows_with_identity}`",
        f"- Structural candidate rows extracted: `{extract.candidate_count}`",
        f"- Identity source: `{extract.identity_source}`",
        f"- Structure/type source: `{extract.type_source}`",
        f"- Starter CSV output: `{_relative(starter_csv)}`",
        f"- Generated at UTC: `{datetime.now(UTC).isoformat()}`",
        "",
    ]

    if extract.warnings:
        lines.extend(["## Warnings", ""])
        for warning in extract.warnings:
            lines.append(f"- {warning}")
        lines.append("")

    if extract.duplicates:
        lines.extend(["## Blocking duplicates", ""])
        for normalized, originals in sorted(extract.duplicates.items()):
            joined = ", ".join(f"`{value}`" for value in originals)
            lines.append(f"- `{normalized}` from {joined}")
        lines.append("")

    lines.extend(
        [
            "## Candidate pole_id extract",
            "",
            "| Baseline pole_id | Structure type | Source row | Remark | Raw height |",
            "| --- | --- | --- | --- | --- |",
        ]
    )
    for candidate in extract.candidates:
        remark = candidate.remark.replace("|", "/")
        raw_height = candidate.raw_height.replace("|", "/")
        lines.append(
            f"| `{candidate.pole_id}` | `{candidate.structure_type}` | "
            f"`{candidate.source_row_number}` | {remark or '—'} | {raw_height or '—'} |"
        )
    lines.extend(
        [
            "",
            "## Next step",
            "",
            "- Fill `captured_by` and `capture_date` during real field capture.",
            "- Keep all unconfirmed technical fields blank or `unknown`.",
            "- Use exact `pole_id` matching only when the completed pilot CSV "
            "is compared back to this baseline.",
        ]
    )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def load_pilot_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8-sig") as handle:
        reader = csv.DictReader(handle)
        headers = [str(header).strip() for header in reader.fieldnames or [] if header is not None]
        if "pole_id" not in headers:
            raise ValueError("Pilot CSV must contain a pole_id column.")
        return [
            {str(key): "" if value is None else str(value) for key, value in row.items()}
            for row in reader
        ]


def compare_pilot_to_baseline(
    extract: BaselineExtract,
    pilot_rows: list[dict[str, str]],
) -> dict[str, Any]:
    baseline_map = {candidate.normalized_pole_id: candidate for candidate in extract.candidates}
    baseline_duplicates = extract.duplicates

    pilot_seen: dict[str, list[int]] = defaultdict(list)
    row_results: list[dict[str, Any]] = []

    for index, row in enumerate(pilot_rows, start=2):
        original = "" if row.get("pole_id") is None else str(row.get("pole_id"))
        normalized = normalize_pole_id(original)
        if normalized:
            pilot_seen[normalized].append(index)
        row_results.append(
            {
                "csv_row_number": index,
                "pilot_pole_id": original,
                "normalized_pole_id": normalized,
                "baseline_pole_id": baseline_map.get(normalized).pole_id
                if normalized in baseline_map
                else None,
                "status": "PENDING",
                "reason": "",
            }
        )

    duplicate_pilot_ids = {key: rows for key, rows in pilot_seen.items() if len(rows) > 1}

    matched = 0
    missing = 0
    no_match = 0
    duplicate = 0
    for row_result in row_results:
        normalized = row_result["normalized_pole_id"]
        if normalized is None:
            row_result["status"] = "BLOCKED"
            row_result["reason"] = "Missing or unsafe pole_id"
            missing += 1
            continue
        if normalized in duplicate_pilot_ids:
            row_result["status"] = "BLOCKED"
            row_result["reason"] = "Duplicate pole_id in pilot CSV"
            duplicate += 1
            continue
        if normalized in baseline_map:
            row_result["status"] = "MATCH"
            row_result["reason"] = "Exact match after whitespace/case normalisation"
            matched += 1
        else:
            row_result["status"] = "NO MATCH"
            row_result["reason"] = "No exact baseline pole_id match"
            no_match += 1

    baseline_only = [
        candidate
        for candidate in extract.candidates
        if candidate.normalized_pole_id not in pilot_seen
    ]
    comparable_rows = len(row_results)
    match_rate = round((matched / comparable_rows) * 100, 1) if comparable_rows else 0.0
    blocking = bool(baseline_duplicates or duplicate_pilot_ids or missing)

    return {
        "baseline_candidate_count": extract.candidate_count,
        "pilot_row_count": len(row_results),
        "matched_count": matched,
        "no_match_count": no_match,
        "missing_pole_id_count": missing,
        "duplicate_pole_id_count": len(duplicate_pilot_ids),
        "match_rate_percent": match_rate,
        "baseline_duplicates": baseline_duplicates,
        "pilot_duplicates": duplicate_pilot_ids,
        "baseline_only_count": len(baseline_only),
        "baseline_only": baseline_only,
        "row_results": row_results,
        "blocking": blocking,
        "verdict": "BLOCKED"
        if blocking
        else ("MATCH READY" if no_match == 0 else "REVIEW REQUIRED"),
    }


def write_match_report(
    path: Path,
    extract: BaselineExtract,
    comparison: dict[str, Any],
    pilot_csv: Path,
    pilot_name: str,
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# Stage 4 Controlled Pilot Pole ID Match Report",
        "",
        f"- Pilot name: `{pilot_name}`",
        f"- Baseline CSV: `{_relative(extract.baseline_csv)}`",
        f"- Pilot CSV: `{_relative(pilot_csv)}`",
        f"- Baseline format: `{extract.format_name}`",
        f"- Baseline candidate count: `{comparison['baseline_candidate_count']}`",
        f"- Pilot row count: `{comparison['pilot_row_count']}`",
        f"- Exact matches: `{comparison['matched_count']}`",
        f"- No-match rows: `{comparison['no_match_count']}`",
        f"- Missing/unsafe pole_id rows: `{comparison['missing_pole_id_count']}`",
        f"- Duplicate pilot pole_id count: `{comparison['duplicate_pole_id_count']}`",
        f"- Match rate: `{comparison['match_rate_percent']}%`",
        f"- Verdict: `{comparison['verdict']}`",
        "",
    ]

    if comparison["baseline_duplicates"]:
        lines.extend(["## Blocking baseline duplicates", ""])
        for normalized, originals in sorted(comparison["baseline_duplicates"].items()):
            joined = ", ".join(f"`{value}`" for value in originals)
            lines.append(f"- `{normalized}` from {joined}")
        lines.append("")

    if comparison["pilot_duplicates"]:
        lines.extend(["## Blocking pilot duplicates", ""])
        for normalized, rows in sorted(comparison["pilot_duplicates"].items()):
            joined_rows = ", ".join(str(row) for row in rows)
            lines.append(f"- `{normalized}` at pilot CSV rows {joined_rows}")
        lines.append("")

    lines.extend(
        [
            "## Row-level exact match results",
            "",
            "| Pilot CSV row | Pilot pole_id | Baseline pole_id | Status | Reason |",
            "| --- | --- | --- | --- | --- |",
        ]
    )
    for row_result in comparison["row_results"]:
        pilot_pole_id = row_result["pilot_pole_id"] or "—"
        baseline_pole_id = row_result["baseline_pole_id"] or "—"
        reason = row_result["reason"].replace("|", "/")
        lines.append(
            f"| `{row_result['csv_row_number']}` | `{pilot_pole_id}` | "
            f"`{baseline_pole_id}` | `{row_result['status']}` | {reason} |"
        )

    lines.extend(["", "## Baseline-only rows not captured in pilot CSV", ""])
    if comparison["baseline_only"]:
        lines.append("| Baseline pole_id | Structure type | Source row |")
        lines.append("| --- | --- | --- |")
        for candidate in comparison["baseline_only"]:
            lines.append(
                f"| `{candidate.pole_id}` | `{candidate.structure_type}` | "
                f"`{candidate.source_row_number}` |"
            )
    else:
        lines.append("- None.")

    lines.extend(
        [
            "",
            "## Decision guidance",
            "",
            "- Exact match only. No fuzzy matching is permitted.",
            "- Duplicates are blocking.",
            "- Missing or unsafe pole_id values are blocking.",
            "- Preserve original pole_id values in the decision board and operator notes.",
        ]
    )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _print_prepare_summary(
    extract: BaselineExtract,
    starter_csv: Path,
    notes_out: Path,
) -> None:
    print(f"BASELINE FORMAT: {extract.format_name}")
    print(f"TOTAL BASELINE ROWS: {extract.total_rows}")
    print(f"CANDIDATE SUPPORT ROWS: {extract.candidate_count}")
    print(f"IDENTITY SOURCE: {extract.identity_source}")
    print(f"TYPE SOURCE: {extract.type_source}")
    print(f"STARTER CSV: {_relative(starter_csv)}")
    print(f"NOTES REPORT: {_relative(notes_out)}")
    if extract.duplicates:
        print(f"BLOCKING DUPLICATE IDS: {len(extract.duplicates)}")
    print(
        "NEXT ACTION: Fill captured_by, capture_date, evidence, and only "
        "confirmed field values during field capture."
    )


def _print_match_summary(comparison: dict[str, Any], report_path: Path) -> None:
    print(f"VERDICT: {comparison['verdict']}")
    print(f"PILOT ROWS: {comparison['pilot_row_count']}")
    print(f"EXACT MATCHES: {comparison['matched_count']}")
    print(f"NO MATCH: {comparison['no_match_count']}")
    print(f"MISSING/UNSAFE POLE_ID: {comparison['missing_pole_id_count']}")
    print(f"DUPLICATE PILOT POLE_ID: {comparison['duplicate_pole_id_count']}")
    print(f"MATCH RATE: {comparison['match_rate_percent']}%")
    print(f"MATCH REPORT: {_relative(report_path)}")
    if comparison["blocking"]:
        print(
            "NEXT ACTION: Resolve missing/duplicate pole_id blockers before any Stage 4C decision."
        )
    elif comparison["no_match_count"]:
        print("NEXT ACTION: Review the NO MATCH rows and document exact reasons before decision.")
    else:
        print("NEXT ACTION: Use this exact-match result in Noel's controlled pilot decision board.")


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--baseline-csv",
        required=True,
        help="Local baseline CSV path.",
    )
    parser.add_argument(
        "--pilot-name",
        required=True,
        help="Pilot identifier, e.g. P_CONTROLLED_001.",
    )
    parser.add_argument(
        "--pilot-csv",
        help="Completed Stage 4 pilot CSV to compare against baseline.",
    )
    parser.add_argument(
        "--out",
        help="Starter CSV output path for prepare mode.",
    )
    parser.add_argument(
        "--notes-out",
        help="Markdown notes output path for prepare mode.",
    )
    parser.add_argument(
        "--match-report-out",
        help="Markdown report output path for match mode.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)
    baseline_csv = Path(args.baseline_csv)
    if not baseline_csv.exists():
        print(f"ERROR: baseline CSV not found: {baseline_csv}", file=sys.stderr)
        return 2

    try:
        extract = extract_baseline_candidates(baseline_csv)
    except Exception as exc:  # pragma: no cover - defensive CLI guard
        print(f"ERROR: could not extract baseline candidates: {exc}", file=sys.stderr)
        return 2

    if args.pilot_csv:
        if not args.match_report_out:
            print("ERROR: --match-report-out is required in match mode.", file=sys.stderr)
            return 2
        try:
            pilot_rows = load_pilot_csv(Path(args.pilot_csv))
        except Exception as exc:
            print(f"ERROR: could not load pilot CSV: {exc}", file=sys.stderr)
            return 2
        comparison = compare_pilot_to_baseline(extract, pilot_rows)
        report_path = Path(args.match_report_out)
        write_match_report(
            report_path,
            extract,
            comparison,
            Path(args.pilot_csv),
            args.pilot_name,
        )
        _print_match_summary(comparison, report_path)
        return 1 if comparison["blocking"] else 0

    if not args.out or not args.notes_out:
        print(
            "ERROR: --out and --notes-out are required in prepare mode.",
            file=sys.stderr,
        )
        return 2

    starter_csv = Path(args.out)
    notes_out = Path(args.notes_out)
    headers = get_stage4_template_headers()
    rows = build_starter_rows(extract, args.pilot_name)
    write_csv(starter_csv, headers, rows)
    write_prepare_notes(notes_out, extract, starter_csv, args.pilot_name)
    _print_prepare_summary(extract, starter_csv, notes_out)
    return 1 if extract.blocking else 0


if __name__ == "__main__":
    raise SystemExit(main())
