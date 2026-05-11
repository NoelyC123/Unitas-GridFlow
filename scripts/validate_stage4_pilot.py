#!/usr/bin/env python3
"""Validate a Stage 4 real field pilot CSV and generate local reports.

This script wraps the existing Stage 4B preview validator with a practical
execution workflow for Noel's real iPad field pilot:

- reads a pilot CSV
- optionally inspects an evidence/photo folder by filename only
- prints a concise terminal summary
- writes JSON + Markdown reports to a local output folder

The script is intentionally pre-runtime only. It does not import Flask routes,
does not touch live job outputs, and does not process image contents.
"""

from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from collections import Counter, defaultdict
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from app.structured_capture_validators import validate_stage4_import_preview  # noqa: E402

DEFAULT_OUT_ROOT = REPO_ROOT / "validation_runs" / "stage4_pilots"
PHOTO_NAME_RE = re.compile(
    r"^(?P<pole_id>[^_]+)_(?P<sequence>\d{2})_(?P<view>[A-Za-z0-9-]+)\.(?P<ext>jpg|jpeg|png|heic|heif|webp)$",
    re.IGNORECASE,
)


def _relative(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(REPO_ROOT))
    except ValueError:
        return str(path.resolve())


def load_pilot_csv(csv_path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with csv_path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        rows = [dict(row) for row in reader]
        headers = list(reader.fieldnames or [])
    return headers, rows


def _reference_basename(reference: str) -> str:
    return Path(reference.strip()).name


def check_evidence_folder(
    rows: list[dict[str, str]],
    *,
    evidence_dir: Path | None = None,
) -> dict[str, Any]:
    csv_pole_ids = sorted(
        {str(row.get("pole_id", "")).strip() for row in rows if str(row.get("pole_id", "")).strip()}
    )
    row_refs: list[dict[str, Any]] = []
    referenced_names: list[str] = []
    rows_with_photo_reference = 0

    for index, row in enumerate(rows, start=1):
        pole_id = str(row.get("pole_id", "")).strip()
        reference = str(row.get("photo_reference", "")).strip()
        if not reference:
            continue
        rows_with_photo_reference += 1
        basename = _reference_basename(reference)
        referenced_names.append(basename)
        parsed = PHOTO_NAME_RE.match(basename)
        ref_pole_id = parsed.group("pole_id") if parsed else None
        mismatch = bool(ref_pole_id and pole_id and ref_pole_id != pole_id)
        row_refs.append(
            {
                "row_index": index,
                "pole_id": pole_id or None,
                "photo_reference": reference,
                "basename": basename,
                "parsed_pole_id": ref_pole_id,
                "matches_row_pole_id": not mismatch,
            }
        )

    rows_without_photo_reference = max(0, len(rows) - rows_with_photo_reference)
    photo_reference_row_mismatches = [item for item in row_refs if not item["matches_row_pole_id"]]
    photo_references_not_matching_csv_pole_ids = sorted(
        {
            item["basename"]
            for item in row_refs
            if item["parsed_pole_id"] and item["parsed_pole_id"] not in csv_pole_ids
        }
    )

    if evidence_dir is None:
        return {
            "checked": False,
            "evidence_dir": None,
            "csv_pole_ids": csv_pole_ids,
            "rows_with_photo_reference": rows_with_photo_reference,
            "rows_without_photo_reference": rows_without_photo_reference,
            "referenced_photos_total": len(referenced_names),
            "referenced_photos_found": 0,
            "referenced_photos_missing": 0,
            "referenced_photos_coverage_percent": 0.0 if referenced_names else 100.0,
            "missing_referenced_photos": [],
            "unreferenced_photos": [],
            "duplicate_photo_names": [],
            "invalid_photo_naming_patterns": [],
            "photo_references_not_matching_csv_pole_ids": (
                photo_references_not_matching_csv_pole_ids
            ),
            "photo_reference_row_mismatches": photo_reference_row_mismatches,
            "evidence_files_total": 0,
            "all_evidence_files": [],
        }

    all_files = sorted(p for p in evidence_dir.rglob("*") if p.is_file())
    basenames_to_paths: dict[str, list[str]] = defaultdict(list)
    invalid_patterns: list[str] = []
    for path in all_files:
        basenames_to_paths[path.name].append(_relative(path))
        if not PHOTO_NAME_RE.match(path.name):
            invalid_patterns.append(_relative(path))

    referenced_set = set(referenced_names)
    found_names = sorted(name for name in referenced_set if name in basenames_to_paths)
    missing_referenced_photos = sorted(
        name for name in referenced_set if name not in basenames_to_paths
    )
    unreferenced_photos = sorted(name for name in basenames_to_paths if name not in referenced_set)
    duplicate_photo_names = sorted(
        name for name, paths in basenames_to_paths.items() if len(paths) > 1
    )

    found_count = len(found_names)
    total_refs = len(referenced_names)
    coverage_percent = round((found_count / total_refs) * 100, 1) if total_refs else 100.0

    return {
        "checked": True,
        "evidence_dir": _relative(evidence_dir),
        "csv_pole_ids": csv_pole_ids,
        "rows_with_photo_reference": rows_with_photo_reference,
        "rows_without_photo_reference": rows_without_photo_reference,
        "referenced_photos_total": total_refs,
        "referenced_photos_found": found_count,
        "referenced_photos_missing": len(missing_referenced_photos),
        "referenced_photos_coverage_percent": coverage_percent,
        "missing_referenced_photos": missing_referenced_photos,
        "unreferenced_photos": unreferenced_photos,
        "duplicate_photo_names": duplicate_photo_names,
        "invalid_photo_naming_patterns": invalid_patterns,
        "photo_references_not_matching_csv_pole_ids": (photo_references_not_matching_csv_pole_ids),
        "photo_reference_row_mismatches": photo_reference_row_mismatches,
        "evidence_files_total": len(all_files),
        "all_evidence_files": sorted(_relative(path) for path in all_files),
    }


def summarise_preview(preview: dict[str, Any], evidence: dict[str, Any]) -> dict[str, Any]:
    row_results = list(preview.get("row_results", []))
    field_results = list(preview.get("per_field_validation_results", []))

    duplicate_ids = sorted(
        {
            row.get("pole_id")
            for row in row_results
            if row.get("pole_id")
            and any(
                field.get("reason") == "duplicate pole_id" for field in row.get("field_results", [])
            )
        }
    )
    missing_pole_id_count = sum(1 for row in row_results if not row.get("pole_id"))
    invalid_field_results = [field for field in field_results if not field.get("valid", True)]
    warning_counter = Counter(preview.get("warnings", []))
    error_counter = Counter(preview.get("errors", []))

    total_rows = int(preview.get("total_rows", 0))
    valid_rows = int(preview.get("valid_rows", 0))
    pass_rate = round((valid_rows / total_rows) * 100, 1) if total_rows else 0.0

    return {
        "total_rows": total_rows,
        "valid_rows": valid_rows,
        "invalid_rows": int(preview.get("invalid_rows", 0)),
        "merge_ready_rows": int(preview.get("merge_ready_rows", 0)),
        "review_required_rows": int(preview.get("review_required_rows", 0)),
        "blocked_rows": int(preview.get("blocked_rows", 0)),
        "duplicate_pole_id_count": len(duplicate_ids),
        "duplicate_pole_ids": duplicate_ids,
        "missing_pole_id_count": missing_pole_id_count,
        "invalid_field_count": len(invalid_field_results),
        "warning_count": len(preview.get("warnings", [])),
        "error_count": len(preview.get("errors", [])),
        "validation_pass_rate_percent": pass_rate,
        "safe_to_merge": bool(preview.get("safe_to_merge", False)),
        "verdict": preview.get("verdict"),
        "evidence_photo_reference_coverage": {
            "checked": evidence["checked"],
            "rows_with_photo_reference": evidence["rows_with_photo_reference"],
            "rows_without_photo_reference": evidence["rows_without_photo_reference"],
            "referenced_photos_found": evidence["referenced_photos_found"],
            "referenced_photos_missing": evidence["referenced_photos_missing"],
            "coverage_percent": evidence["referenced_photos_coverage_percent"],
            "evidence_files_total": evidence["evidence_files_total"],
        },
        "top_errors": error_counter.most_common(10),
        "top_warnings": warning_counter.most_common(10),
    }


def recommend_stage4c_gate(preview: dict[str, Any], evidence: dict[str, Any]) -> tuple[str, str]:
    total_rows = int(preview.get("total_rows", 0))
    valid_rows = int(preview.get("valid_rows", 0))
    blocked_rows = int(preview.get("blocked_rows", 0))
    invalid_rows = int(preview.get("invalid_rows", 0))
    review_required_rows = int(preview.get("review_required_rows", 0))
    pass_rate = (valid_rows / total_rows) * 100 if total_rows else 0.0

    evidence_has_problems = any(
        (
            evidence.get("missing_referenced_photos"),
            evidence.get("duplicate_photo_names"),
            evidence.get("invalid_photo_naming_patterns"),
            evidence.get("photo_references_not_matching_csv_pole_ids"),
            evidence.get("photo_reference_row_mismatches"),
        )
    )

    if total_rows == 0 or blocked_rows > 0 or invalid_rows > 0 or pass_rate < 90:
        return (
            "NO-GO",
            "Stage 4C remains blocked. The current pilot has blocking "
            "validation failures or an insufficient pass rate.",
        )

    if (
        total_rows < 10
        or review_required_rows > 0
        or not evidence.get("checked", False)
        or evidence_has_problems
    ):
        return (
            "PARTIAL / RE-PILOT REQUIRED",
            "Stage 4C remains blocked. The pilot is usable for feedback, "
            "but it is not yet complete enough for a GO decision.",
        )

    return (
        "GO",
        "Pilot evidence is strong enough to support Noel's manual Stage 4C "
        "go/no-go review. Stage 4C still requires Noel's explicit sign-off.",
    )


def build_report(
    *,
    csv_path: Path,
    pilot_name: str,
    out_dir: Path,
    preview: dict[str, Any],
    evidence: dict[str, Any],
) -> dict[str, Any]:
    summary = summarise_preview(preview, evidence)
    gate_recommendation, stage4c_status = recommend_stage4c_gate(preview, evidence)

    invalid_field_results = [
        field
        for field in preview.get("per_field_validation_results", [])
        if not field.get("valid", True)
    ]
    row_findings = [
        {
            "row_index": row.get("index"),
            "pole_id": row.get("pole_id"),
            "row_status": row.get("row_status"),
            "merge_ready": row.get("merge_ready"),
            "errors": row.get("errors", []),
            "warnings": row.get("warnings", []),
        }
        for row in preview.get("row_results", [])
    ]

    recommended_fixes: list[str] = []
    if summary["missing_pole_id_count"]:
        recommended_fixes.append(
            "Fix missing or unsafe pole_id values before any Stage 4C discussion."
        )
    if summary["invalid_rows"]:
        recommended_fixes.append(
            "Correct invalid enum/date/source rows and rerun the pilot validator."
        )
    if summary["review_required_rows"]:
        recommended_fixes.append(
            "Resolve review-required rows or carry them explicitly into Noel's pilot result notes."
        )
    if evidence["missing_referenced_photos"]:
        recommended_fixes.append(
            "Add the missing referenced photos or remove stale photo_reference values."
        )
    if evidence["invalid_photo_naming_patterns"]:
        recommended_fixes.append(
            "Rename photos to <pole_id>_<sequence>_<view>.<ext> before sign-off."
        )
    if evidence["unreferenced_photos"]:
        recommended_fixes.append(
            "Either reference surplus photos from the CSV or move them out "
            "of the pilot evidence folder."
        )
    if not recommended_fixes:
        recommended_fixes.append(
            "Record the result in Noel's pilot summary template and "
            "complete the manual Stage 4C gate review."
        )

    report = {
        "pilot_metadata": {
            "pilot_name": pilot_name,
            "csv_path": _relative(csv_path),
            "out_dir": _relative(out_dir),
            "generated_at_utc": datetime.now(UTC).isoformat(),
            "evidence_dir": evidence.get("evidence_dir"),
        },
        "validation_summary": summary,
        "row_level_findings": row_findings,
        "field_level_findings": invalid_field_results,
        "evidence_findings": evidence,
        "top_blockers": [message for message, _count in summary["top_errors"][:10]],
        "recommended_fixes": recommended_fixes,
        "gate_recommendation": gate_recommendation,
        "stage4c_readiness_status": stage4c_status,
    }
    return report


def render_markdown_report(report: dict[str, Any]) -> str:
    meta = report["pilot_metadata"]
    summary = report["validation_summary"]
    evidence = report["evidence_findings"]

    lines = [
        f"# Stage 4 Pilot Validation Report — {meta['pilot_name']}",
        "",
        "## Pilot Metadata",
        "",
        f"- CSV: `{meta['csv_path']}`",
        f"- Output directory: `{meta['out_dir']}`",
        f"- Generated at (UTC): `{meta['generated_at_utc']}`",
        f"- Evidence directory: `{meta['evidence_dir'] or 'not provided'}`",
        "",
        "## Validation Summary",
        "",
        f"- Total rows: **{summary['total_rows']}**",
        f"- Valid rows: **{summary['valid_rows']}**",
        f"- Invalid rows: **{summary['invalid_rows']}**",
        f"- Merge-ready rows: **{summary['merge_ready_rows']}**",
        f"- Review-required rows: **{summary['review_required_rows']}**",
        f"- Blocked rows: **{summary['blocked_rows']}**",
        f"- Duplicate pole_id count: **{summary['duplicate_pole_id_count']}**",
        f"- Missing pole_id count: **{summary['missing_pole_id_count']}**",
        f"- Invalid field count: **{summary['invalid_field_count']}**",
        f"- Warning count: **{summary['warning_count']}**",
        f"- Error count: **{summary['error_count']}**",
        "- Evidence/photo reference coverage: "
        f"**{summary['evidence_photo_reference_coverage']['coverage_percent']}%**",
        f"- Safe to merge: **{summary['safe_to_merge']}**",
        f"- Stage 4C gate recommendation: **{report['gate_recommendation']}**",
        f"- Stage 4C readiness status: **{report['stage4c_readiness_status']}**",
        "",
        "## Row-Level Findings",
        "",
        "| Row | pole_id | Status | Merge-ready | Errors | Warnings |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for row in report["row_level_findings"]:
        errors = "; ".join(row["errors"]) or "—"
        warnings = "; ".join(row["warnings"]) or "—"
        lines.append(
            f"| {row['row_index']} | {row['pole_id'] or '—'} | "
            f"{row['row_status']} | {row['merge_ready']} | {errors} | "
            f"{warnings} |"
        )

    lines.extend(
        [
            "",
            "## Field-Level Findings",
            "",
            "| Field | pole_id | Severity | Reason | Recommendation |",
            "| --- | --- | --- | --- | --- |",
        ]
    )
    field_findings = report["field_level_findings"]
    if field_findings:
        for field in field_findings:
            lines.append(
                f"| {field.get('field_name')} | {field.get('pole_id') or '—'} | "
                f"{field.get('severity')} | {field.get('reason') or '—'} | "
                f"{field.get('recommendation') or '—'} |"
            )
    else:
        lines.append("| — | — | — | No invalid field-level findings | — |")

    lines.extend(
        [
            "",
            "## Evidence Findings",
            "",
            f"- Evidence checked: **{evidence['checked']}**",
            "- Referenced photos found: "
            f"**{evidence['referenced_photos_found']} / "
            f"{evidence['referenced_photos_total']}**",
            f"- Missing referenced photos: **{len(evidence['missing_referenced_photos'])}**",
            f"- Unreferenced photos: **{len(evidence['unreferenced_photos'])}**",
            f"- Duplicate photo names: **{len(evidence['duplicate_photo_names'])}**",
            "- Invalid photo naming patterns: "
            f"**{len(evidence['invalid_photo_naming_patterns'])}**",
            "",
        ]
    )
    if evidence["missing_referenced_photos"]:
        lines.append("### Missing Referenced Photos")
        lines.extend([f"- `{item}`" for item in evidence["missing_referenced_photos"]])
        lines.append("")
    if evidence["unreferenced_photos"]:
        lines.append("### Unreferenced Photos")
        lines.extend([f"- `{item}`" for item in evidence["unreferenced_photos"]])
        lines.append("")
    if evidence["duplicate_photo_names"]:
        lines.append("### Duplicate Photo Names")
        lines.extend([f"- `{item}`" for item in evidence["duplicate_photo_names"]])
        lines.append("")
    if evidence["invalid_photo_naming_patterns"]:
        lines.append("### Invalid Photo Naming Patterns")
        lines.extend([f"- `{item}`" for item in evidence["invalid_photo_naming_patterns"]])
        lines.append("")
    if evidence["photo_reference_row_mismatches"]:
        lines.append("### Photo References Not Matching Their CSV pole_id")
        for item in evidence["photo_reference_row_mismatches"]:
            lines.append(
                f"- Row {item['row_index']}: `{item['photo_reference']}` "
                f"does not match row pole_id `{item['pole_id']}`"
            )
        lines.append("")

    lines.extend(
        [
            "## Top Blockers",
            "",
        ]
    )
    if report["top_blockers"]:
        lines.extend([f"- {item}" for item in report["top_blockers"]])
    else:
        lines.append("- None")

    lines.extend(
        [
            "",
            "## Recommended Fixes",
            "",
        ]
    )
    lines.extend([f"- {item}" for item in report["recommended_fixes"]])
    lines.extend(
        [
            "",
            "## GO / NO-GO Decision",
            "",
            f"**Recommendation:** {report['gate_recommendation']}",
            "",
            report["stage4c_readiness_status"],
            "",
        ]
    )
    return "\n".join(lines)


def write_reports(report: dict[str, Any], out_dir: Path) -> dict[str, str]:
    out_dir.mkdir(parents=True, exist_ok=True)
    json_path = out_dir / "pilot_validation_report.json"
    md_path = out_dir / "pilot_validation_report.md"
    json_path.write_text(json.dumps(report, indent=2, sort_keys=False), encoding="utf-8")
    md_path.write_text(render_markdown_report(report), encoding="utf-8")
    return {"json": str(json_path), "markdown": str(md_path)}


def print_terminal_summary(report: dict[str, Any], report_paths: dict[str, str]) -> None:
    meta = report["pilot_metadata"]
    summary = report["validation_summary"]
    evidence = report["evidence_findings"]
    print(f"Stage 4 pilot: {meta['pilot_name']}")
    print(f"CSV: {meta['csv_path']}")
    print(
        "Rows: total={total_rows} valid={valid_rows} invalid={invalid_rows} "
        "merge_ready={merge_ready_rows} "
        "review_required={review_required_rows} blocked={blocked_rows}".format(**summary)
    )
    print(
        "Pole IDs: duplicates={duplicate_pole_id_count} "
        "missing={missing_pole_id_count} "
        "invalid_fields={invalid_field_count}".format(**summary)
    )
    print(
        "Findings: warnings={warning_count} errors={error_count} "
        "safe_to_merge={safe_to_merge}".format(**summary)
    )
    print(
        "Evidence: checked={checked} "
        "referenced_found={referenced_photos_found}/{referenced_photos_total} "
        "missing={missing_referenced_count} "
        "unreferenced={unreferenced_count} "
        "invalid_names={invalid_name_count}".format(
            checked=evidence["checked"],
            referenced_photos_found=evidence["referenced_photos_found"],
            referenced_photos_total=evidence["referenced_photos_total"],
            missing_referenced_count=len(evidence["missing_referenced_photos"]),
            unreferenced_count=len(evidence["unreferenced_photos"]),
            invalid_name_count=len(evidence["invalid_photo_naming_patterns"]),
        )
    )
    print(f"Recommendation: {report['gate_recommendation']}")
    print(f"Stage 4C status: {report['stage4c_readiness_status']}")
    print(f"JSON report: {_relative(Path(report_paths['json']))}")
    print(f"Markdown report: {_relative(Path(report_paths['markdown']))}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--csv", type=Path, required=True, help="Path to the pilot CSV file")
    parser.add_argument(
        "--out",
        type=Path,
        help=(
            "Output directory for JSON/Markdown reports "
            "(default: validation_runs/stage4_pilots/<pilot-name>)"
        ),
    )
    parser.add_argument(
        "--pilot-name",
        help="Human-readable pilot or job name for the report (default: CSV filename stem)",
    )
    parser.add_argument(
        "--evidence-dir",
        type=Path,
        help="Optional photo/evidence folder to inspect by filename/reference only",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    csv_path = args.csv.resolve()
    if not csv_path.exists():
        print(f"Pilot CSV not found: {csv_path}", file=sys.stderr)
        return 2

    pilot_name = args.pilot_name or csv_path.stem
    out_dir = args.out.resolve() if args.out else (DEFAULT_OUT_ROOT / pilot_name)
    evidence_dir = args.evidence_dir.resolve() if args.evidence_dir else None

    headers, rows = load_pilot_csv(csv_path)
    preview = validate_stage4_import_preview(rows, headers=headers)
    evidence = check_evidence_folder(rows, evidence_dir=evidence_dir)
    report = build_report(
        csv_path=csv_path,
        pilot_name=pilot_name,
        out_dir=out_dir,
        preview=preview,
        evidence=evidence,
    )
    report_paths = write_reports(report, out_dir)
    print_terminal_summary(report, report_paths)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
