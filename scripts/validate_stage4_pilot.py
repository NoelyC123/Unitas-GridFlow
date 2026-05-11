#!/usr/bin/env python3
"""Validate a Stage 4 real field pilot CSV and generate local reports.

This command stays outside runtime integration. It validates a pilot CSV,
optionally checks an evidence/photo folder by filename only, prints an
operator-facing summary, and writes JSON plus Markdown reports.
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
    (
        r"^(?P<pole_id>[^_]+)_(?P<sequence>\d{2})_"
        r"(?P<view>[A-Za-z0-9-]+)\.(?P<ext>jpg|jpeg|png|heic|heif|webp)$"
    ),
    re.IGNORECASE,
)
REFERENCE_SPLIT_RE = re.compile(r"[,\n;|]+")
MANDATORY_JSON_KEYS = (
    "pilot_metadata",
    "validation_summary",
    "evidence_summary",
    "row_findings",
    "field_findings",
    "recommendations",
    "stage4c_gate_status",
)
DO_NOT_START_YET = [
    "Do not start Stage 4C runtime integration from this result alone.",
    "Do not add Stage 4 fields to live popups or the Review OS yet.",
    "Do not commit raw pilot CSVs, real photos, or local pilot reports "
    "unless Noel explicitly approves a redacted artifact.",
]


def _relative(path: Path | None) -> str | None:
    if path is None:
        return None
    try:
        return str(path.resolve().relative_to(REPO_ROOT))
    except ValueError:
        return str(path.resolve())


def _split_photo_references(reference: str) -> list[str]:
    return [item.strip() for item in REFERENCE_SPLIT_RE.split(reference) if item.strip()]


def _reference_basename(reference: str) -> str:
    return Path(reference.strip()).name


def _headline_label(decision: str) -> str:
    if decision == "GO":
        return "PASS"
    if decision == "PARTIAL / RE-PILOT REQUIRED":
        return "PARTIAL"
    return "NO-GO"


def _report_stub(
    *,
    csv_path: Path,
    pilot_name: str,
    out_dir: Path,
    evidence_dir: Path | None,
) -> dict[str, Any]:
    return {
        "pilot_metadata": {
            "pilot_name": pilot_name,
            "csv_path": _relative(csv_path),
            "out_dir": _relative(out_dir),
            "generated_at_utc": datetime.now(UTC).isoformat(),
            "evidence_dir": _relative(evidence_dir),
        }
    }


def load_pilot_csv(csv_path: Path) -> tuple[list[str], list[dict[str, str]]]:
    try:
        with csv_path.open(newline="", encoding="utf-8") as handle:
            reader = csv.DictReader(handle)
            headers = [
                str(header).strip() if header is not None else ""
                for header in reader.fieldnames or []
            ]
            if not headers or not any(headers):
                raise ValueError("CSV header row is missing or unreadable.")
            if any(not header for header in headers):
                raise ValueError("CSV header row contains a blank column name.")

            rows: list[dict[str, str]] = []
            for row_number, row in enumerate(reader, start=2):
                if row is None:
                    continue
                if None in row:
                    extra_values = [
                        str(value).strip() for value in row.pop(None) or [] if str(value).strip()
                    ]
                    if extra_values:
                        last_header = headers[-1]
                        current_last_value = str(row.get(last_header, "")).strip()
                        if len(extra_values) == 1 and not current_last_value:
                            row[last_header] = extra_values[0]
                        else:
                            raise ValueError(
                                "Malformed CSV row "
                                f"{row_number}: more values were found than the "
                                "header allows."
                            )
                rows.append(
                    {str(key): "" if value is None else str(value) for key, value in row.items()}
                )
    except csv.Error as exc:
        raise ValueError(f"Malformed CSV: {exc}") from exc

    return headers, rows


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
    rows_with_multiple_photo_references = 0

    for index, row in enumerate(rows, start=1):
        pole_id = str(row.get("pole_id", "")).strip()
        raw_reference = str(row.get("photo_reference", "")).strip()
        references = _split_photo_references(raw_reference)
        if not references:
            continue

        rows_with_photo_reference += 1
        if len(references) > 1:
            rows_with_multiple_photo_references += 1

        for reference in references:
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

    base_result = {
        "checked": evidence_dir is not None,
        "status": "not_provided",
        "evidence_dir": _relative(evidence_dir),
        "exists": False,
        "is_empty": False,
        "csv_pole_ids": csv_pole_ids,
        "rows_with_photo_reference": rows_with_photo_reference,
        "rows_without_photo_reference": rows_without_photo_reference,
        "rows_with_multiple_photo_references": rows_with_multiple_photo_references,
        "photo_reference_entries_total": len(referenced_names),
        "referenced_photos_total": len(referenced_names),
        "referenced_photos_found": 0,
        "referenced_photos_missing": 0,
        "referenced_photos_coverage_percent": 0.0 if referenced_names else 100.0,
        "missing_referenced_photos": [],
        "unreferenced_photos": [],
        "duplicate_photo_names": [],
        "invalid_photo_naming_patterns": [],
        "photo_references_not_matching_csv_pole_ids": (photo_references_not_matching_csv_pole_ids),
        "photo_reference_row_mismatches": photo_reference_row_mismatches,
        "evidence_files_total": 0,
        "all_evidence_files": [],
    }

    if evidence_dir is None:
        return base_result

    if not evidence_dir.exists():
        base_result["status"] = "missing"
        base_result["missing_referenced_photos"] = sorted(set(referenced_names))
        base_result["referenced_photos_missing"] = len(base_result["missing_referenced_photos"])
        return base_result

    all_files = sorted(path for path in evidence_dir.rglob("*") if path.is_file())
    base_result["exists"] = True
    if not all_files:
        base_result["status"] = "empty"
        base_result["is_empty"] = True
        base_result["missing_referenced_photos"] = sorted(set(referenced_names))
        base_result["referenced_photos_missing"] = len(base_result["missing_referenced_photos"])
        return base_result

    base_result["status"] = "checked"
    basenames_to_paths: dict[str, list[str]] = defaultdict(list)
    invalid_patterns: list[str] = []
    for path in all_files:
        basenames_to_paths[path.name].append(_relative(path) or str(path))
        if not PHOTO_NAME_RE.match(path.name):
            invalid_patterns.append(_relative(path) or str(path))

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

    base_result.update(
        {
            "referenced_photos_found": found_count,
            "referenced_photos_missing": len(missing_referenced_photos),
            "referenced_photos_coverage_percent": coverage_percent,
            "missing_referenced_photos": missing_referenced_photos,
            "unreferenced_photos": unreferenced_photos,
            "duplicate_photo_names": duplicate_photo_names,
            "invalid_photo_naming_patterns": invalid_patterns,
            "evidence_files_total": len(all_files),
            "all_evidence_files": sorted(_relative(path) or str(path) for path in all_files),
        }
    )
    return base_result


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
        "top_errors": error_counter.most_common(10),
        "top_warnings": warning_counter.most_common(10),
        "evidence_photo_reference_coverage": {
            "checked": evidence["checked"],
            "status": evidence["status"],
            "rows_with_photo_reference": evidence["rows_with_photo_reference"],
            "rows_without_photo_reference": evidence["rows_without_photo_reference"],
            "rows_with_multiple_photo_references": evidence["rows_with_multiple_photo_references"],
            "referenced_photos_found": evidence["referenced_photos_found"],
            "referenced_photos_missing": evidence["referenced_photos_missing"],
            "coverage_percent": evidence["referenced_photos_coverage_percent"],
            "evidence_files_total": evidence["evidence_files_total"],
        },
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
    evidence_not_ready = evidence.get("status") in {"missing", "empty"}

    if total_rows == 0 or blocked_rows > 0 or invalid_rows > 0 or pass_rate < 90:
        return (
            "NO-GO",
            "Stage 4C remains blocked. The current pilot has blocking validation "
            "failures or an insufficient pass rate.",
        )

    if (
        total_rows < 10
        or review_required_rows > 0
        or not evidence.get("checked", False)
        or evidence_not_ready
        or evidence_has_problems
    ):
        return (
            "PARTIAL / RE-PILOT REQUIRED",
            "Stage 4C remains blocked. The pilot is usable for feedback, but it "
            "is not yet complete enough for a GO decision.",
        )

    return (
        "GO",
        "Pilot evidence is strong enough to support Noel's manual Stage 4C "
        "go/no-go review. Stage 4C still requires Noel's explicit sign-off.",
    )


def collect_top_issues(summary: dict[str, Any], evidence: dict[str, Any]) -> list[dict[str, Any]]:
    issues: list[dict[str, Any]] = []
    for message, count in summary["top_errors"]:
        issues.append({"severity": "ERROR", "count": count, "message": message})
    for message, count in summary["top_warnings"]:
        issues.append({"severity": "WARN", "count": count, "message": message})

    if evidence["status"] == "missing":
        issues.append(
            {
                "severity": "WARN",
                "count": 1,
                "message": "Evidence folder path was supplied but does not exist.",
            }
        )
    if evidence["status"] == "empty":
        issues.append(
            {
                "severity": "WARN",
                "count": 1,
                "message": "Evidence folder exists but contains no files.",
            }
        )
    if evidence["missing_referenced_photos"]:
        issues.append(
            {
                "severity": "WARN",
                "count": len(evidence["missing_referenced_photos"]),
                "message": "Referenced photos are missing from the evidence folder.",
            }
        )
    if evidence["unreferenced_photos"]:
        issues.append(
            {
                "severity": "WARN",
                "count": len(evidence["unreferenced_photos"]),
                "message": "Evidence folder contains unreferenced photos.",
            }
        )
    if evidence["duplicate_photo_names"]:
        issues.append(
            {
                "severity": "WARN",
                "count": len(evidence["duplicate_photo_names"]),
                "message": "Evidence folder contains duplicate photo filenames.",
            }
        )
    if evidence["invalid_photo_naming_patterns"]:
        issues.append(
            {
                "severity": "WARN",
                "count": len(evidence["invalid_photo_naming_patterns"]),
                "message": "Some evidence filenames do not follow the required naming format.",
            }
        )
    if evidence["photo_reference_row_mismatches"]:
        issues.append(
            {
                "severity": "WARN",
                "count": len(evidence["photo_reference_row_mismatches"]),
                "message": (
                    "One or more photo references point at a filename whose "
                    "pole_id does not match the CSV row."
                ),
            }
        )

    return issues[:5]


def build_operator_next_action(
    *,
    decision: str,
    summary: dict[str, Any],
    evidence: dict[str, Any],
) -> str:
    if decision == "NO-GO":
        if summary["missing_pole_id_count"] or summary["duplicate_pole_id_count"]:
            return "Fix pole_id identity issues first, then rerun the pilot validator."
        if summary["invalid_rows"]:
            return (
                "Correct the invalid rows shown in the report, export the CSV "
                "again, and rerun the validator."
            )
        return "Fix the blocking issues in the report before considering any Stage 4C work."

    if evidence["status"] == "missing":
        return "Point the command at the correct evidence folder and rerun the validator."
    if evidence["status"] == "empty":
        return "Add the captured evidence files to the evidence folder and rerun the validator."
    if evidence["missing_referenced_photos"] or evidence["unreferenced_photos"]:
        return (
            "Reconcile the photo_reference values against the evidence folder "
            "and rerun the validator."
        )
    if summary["review_required_rows"]:
        return (
            "Review the flagged rows, record the explanation in Noel's pilot "
            "summary, and rerun if any capture data changes."
        )
    return (
        "Record this result in Noel's pilot summary template and complete the "
        "manual Stage 4C decision review."
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
    gate_recommendation, gate_implication = recommend_stage4c_gate(preview, evidence)

    invalid_field_results = [
        field
        for field in preview.get("per_field_validation_results", [])
        if not field.get("valid", True)
    ]
    row_findings = [
        {
            "row_index": row.get("index"),
            "csv_row_number": (
                int(row.get("index")) + 2 if str(row.get("index", "")).isdigit() else None
            ),
            "pole_id": row.get("pole_id"),
            "row_status": row.get("row_status"),
            "merge_ready": row.get("merge_ready"),
            "errors": row.get("errors", []),
            "warnings": row.get("warnings", []),
        }
        for row in preview.get("row_results", [])
    ]

    recommendations: list[str] = []
    if summary["missing_pole_id_count"]:
        recommendations.append(
            "Fix missing or unsafe pole_id values before any Stage 4C discussion."
        )
    if summary["duplicate_pole_id_count"]:
        recommendations.append(
            "Resolve duplicate pole_id rows so every structured capture row maps to one support."
        )
    if summary["invalid_rows"]:
        recommendations.append(
            "Correct invalid enum/date/source rows and rerun the pilot validator."
        )
    if summary["review_required_rows"]:
        recommendations.append(
            "Resolve review-required rows or carry them explicitly into Noel's pilot result notes."
        )
    if evidence["status"] == "missing":
        recommendations.append(
            "Supply the correct evidence folder path so photo coverage can be checked."
        )
    if evidence["status"] == "empty":
        recommendations.append(
            "Move the captured evidence files into the evidence folder before sign-off."
        )
    if evidence["missing_referenced_photos"]:
        recommendations.append(
            "Add the missing referenced photos or remove stale photo_reference values."
        )
    if evidence["invalid_photo_naming_patterns"]:
        recommendations.append(
            "Rename photos to <pole_id>_<sequence>_<view>.<ext> before sign-off."
        )
    if evidence["unreferenced_photos"]:
        recommendations.append(
            "Either reference surplus photos from the CSV or move them out "
            "of the pilot evidence folder."
        )
    if not recommendations:
        recommendations.append(
            "Record the result in Noel's pilot summary template and "
            "complete the manual Stage 4C gate review."
        )

    top_issues = collect_top_issues(summary, evidence)
    next_action = build_operator_next_action(
        decision=gate_recommendation,
        summary=summary,
        evidence=evidence,
    )

    report = _report_stub(
        csv_path=csv_path,
        pilot_name=pilot_name,
        out_dir=out_dir,
        evidence_dir=Path(evidence["evidence_dir"]).resolve()
        if evidence.get("evidence_dir")
        else None,
    )
    report.update(
        {
            "validation_summary": summary,
            "evidence_summary": evidence,
            "row_findings": row_findings,
            "field_findings": invalid_field_results,
            "top_issues": top_issues,
            "recommendations": recommendations,
            "operator_next_action": next_action,
            "stage4c_gate_status": {
                "decision": gate_recommendation,
                "headline": _headline_label(gate_recommendation),
                "implication": gate_implication,
                "runtime_integration_allowed_now": False,
                "manual_signoff_required": True,
            },
            "what_must_not_happen_yet": DO_NOT_START_YET,
            # Compatibility keys retained for the existing execution-system tests
            "row_level_findings": row_findings,
            "field_level_findings": invalid_field_results,
            "evidence_findings": evidence,
            "top_blockers": [item["message"] for item in top_issues if item["severity"] == "ERROR"],
            "recommended_fixes": recommendations,
            "gate_recommendation": gate_recommendation,
            "stage4c_readiness_status": gate_implication,
        }
    )
    return report


def build_failure_report(
    *,
    csv_path: Path,
    pilot_name: str,
    out_dir: Path,
    evidence_dir: Path | None,
    error_message: str,
) -> dict[str, Any]:
    report = _report_stub(
        csv_path=csv_path,
        pilot_name=pilot_name,
        out_dir=out_dir,
        evidence_dir=evidence_dir,
    )
    evidence_summary = {
        "checked": evidence_dir is not None,
        "status": "not_checked_due_to_csv_error",
        "evidence_dir": _relative(evidence_dir),
        "exists": bool(evidence_dir and evidence_dir.exists()),
        "is_empty": False,
        "csv_pole_ids": [],
        "rows_with_photo_reference": 0,
        "rows_without_photo_reference": 0,
        "rows_with_multiple_photo_references": 0,
        "photo_reference_entries_total": 0,
        "referenced_photos_total": 0,
        "referenced_photos_found": 0,
        "referenced_photos_missing": 0,
        "referenced_photos_coverage_percent": 0.0,
        "missing_referenced_photos": [],
        "unreferenced_photos": [],
        "duplicate_photo_names": [],
        "invalid_photo_naming_patterns": [],
        "photo_references_not_matching_csv_pole_ids": [],
        "photo_reference_row_mismatches": [],
        "evidence_files_total": 0,
        "all_evidence_files": [],
    }
    report.update(
        {
            "validation_summary": {
                "total_rows": 0,
                "valid_rows": 0,
                "invalid_rows": 0,
                "merge_ready_rows": 0,
                "review_required_rows": 0,
                "blocked_rows": 0,
                "duplicate_pole_id_count": 0,
                "duplicate_pole_ids": [],
                "missing_pole_id_count": 0,
                "invalid_field_count": 0,
                "warning_count": 0,
                "error_count": 1,
                "validation_pass_rate_percent": 0.0,
                "safe_to_merge": False,
                "verdict": "csv_load_failed",
                "top_errors": [(error_message, 1)],
                "top_warnings": [],
                "evidence_photo_reference_coverage": {
                    "checked": evidence_summary["checked"],
                    "status": evidence_summary["status"],
                    "rows_with_photo_reference": 0,
                    "rows_without_photo_reference": 0,
                    "rows_with_multiple_photo_references": 0,
                    "referenced_photos_found": 0,
                    "referenced_photos_missing": 0,
                    "coverage_percent": 0.0,
                    "evidence_files_total": 0,
                },
            },
            "evidence_summary": evidence_summary,
            "row_findings": [],
            "field_findings": [],
            "top_issues": [{"severity": "ERROR", "count": 1, "message": error_message}],
            "recommendations": [
                "Fix the CSV path or export format, then rerun the pilot validator.",
            ],
            "operator_next_action": "Fix the CSV problem shown below and rerun the validator.",
            "stage4c_gate_status": {
                "decision": "NO-GO",
                "headline": "NO-GO",
                "implication": (
                    "Stage 4C remains blocked. The pilot CSV could not be loaded reliably."
                ),
                "runtime_integration_allowed_now": False,
                "manual_signoff_required": True,
            },
            "what_must_not_happen_yet": DO_NOT_START_YET,
            "row_level_findings": [],
            "field_level_findings": [],
            "evidence_findings": evidence_summary,
            "top_blockers": [error_message],
            "recommended_fixes": [
                "Fix the CSV path or export format, then rerun the pilot validator.",
            ],
            "gate_recommendation": "NO-GO",
            "stage4c_readiness_status": (
                "Stage 4C remains blocked. The pilot CSV could not be loaded reliably."
            ),
        }
    )
    return report


def render_markdown_report(report: dict[str, Any]) -> str:
    meta = report["pilot_metadata"]
    summary = report["validation_summary"]
    evidence = report["evidence_summary"]
    gate = report["stage4c_gate_status"]

    lines = [
        f"# Stage 4 Pilot Validation Report — {meta['pilot_name']}",
        "",
        "## Executive Summary",
        "",
        f"- Pilot verdict: **{gate['headline']}**",
        f"- Stage 4C gate decision: **{gate['decision']}**",
        f"- Stage 4C implication: **{gate['implication']}**",
        f"- Next action: **{report['operator_next_action']}**",
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
        "",
        "## Pilot Verdict",
        "",
        f"**{gate['headline']}**",
        "",
        f"- Decision: `{gate['decision']}`",
        f"- Gate implication: {gate['implication']}",
        "",
        "## Evidence / Photo Status",
        "",
        f"- Evidence check status: **{evidence['status']}**",
        f"- Evidence checked: **{evidence['checked']}**",
        f"- Evidence files found: **{evidence['evidence_files_total']}**",
        f"- Rows with photo reference: **{evidence['rows_with_photo_reference']}**",
        f"- Rows with multiple references: **{evidence['rows_with_multiple_photo_references']}**",
        "- Referenced photos found: "
        f"**{evidence['referenced_photos_found']} / "
        f"{evidence['referenced_photos_total']}**",
        f"- Missing referenced photos: **{len(evidence['missing_referenced_photos'])}**",
        f"- Unreferenced photos: **{len(evidence['unreferenced_photos'])}**",
        f"- Duplicate photo names: **{len(evidence['duplicate_photo_names'])}**",
        f"- Invalid photo naming patterns: **{len(evidence['invalid_photo_naming_patterns'])}**",
        "",
        "## Top Issues",
        "",
    ]
    if report["top_issues"]:
        for item in report["top_issues"]:
            lines.append(f"- {item['severity']} x{item['count']}: {item['message']}")
    else:
        lines.append("- None")

    lines.extend(
        [
            "",
            "## Row-Level Findings",
            "",
            "| CSV Row | pole_id | Status | Merge-ready | Errors | Warnings |",
            "| --- | --- | --- | --- | --- | --- |",
        ]
    )
    for row in report["row_findings"]:
        errors = "; ".join(row["errors"]) or "—"
        warnings = "; ".join(row["warnings"]) or "—"
        lines.append(
            f"| {row['csv_row_number'] or row['row_index']} | {row['pole_id'] or '—'} | "
            f"{row['row_status']} | {row['merge_ready']} | {errors} | {warnings} |"
        )

    lines.extend(
        [
            "",
            "## Field-Level Issue Summary",
            "",
            "| Field | pole_id | Severity | Reason | Recommendation |",
            "| --- | --- | --- | --- | --- |",
        ]
    )
    if report["field_findings"]:
        for field in report["field_findings"]:
            lines.append(
                f"| {field.get('field_name')} | {field.get('pole_id') or '—'} | "
                f"{field.get('severity') or '—'} | {field.get('reason') or '—'} | "
                f"{field.get('recommendation') or '—'} |"
            )
    else:
        lines.append("| — | — | — | No invalid field-level findings | — |")

    if evidence["missing_referenced_photos"]:
        lines.extend(["", "### Missing Referenced Photos", ""])
        lines.extend(f"- `{item}`" for item in evidence["missing_referenced_photos"])
    if evidence["unreferenced_photos"]:
        lines.extend(["", "### Unreferenced Photos", ""])
        lines.extend(f"- `{item}`" for item in evidence["unreferenced_photos"])
    if evidence["duplicate_photo_names"]:
        lines.extend(["", "### Duplicate Photo Names", ""])
        lines.extend(f"- `{item}`" for item in evidence["duplicate_photo_names"])
    if evidence["invalid_photo_naming_patterns"]:
        lines.extend(["", "### Invalid Photo Naming Patterns", ""])
        lines.extend(f"- `{item}`" for item in evidence["invalid_photo_naming_patterns"])
    if evidence["photo_reference_row_mismatches"]:
        lines.extend(["", "### Photo Reference / pole_id Mismatches", ""])
        for item in evidence["photo_reference_row_mismatches"]:
            lines.append(
                f"- CSV row {item['row_index']}: `{item['photo_reference']}` "
                f"does not match row pole_id `{item['pole_id']}`"
            )

    lines.extend(
        [
            "",
            "## Recommended Fixes",
            "",
        ]
    )
    lines.extend(f"- {item}" for item in report["recommendations"])

    lines.extend(
        [
            "",
            "## What Noel Should Do Next",
            "",
            f"- {report['operator_next_action']}",
            "- Record the outcome in the pilot result summary template.",
            "- Keep Stage 4C blocked until Noel makes a manual decision from real pilot evidence.",
            "",
            "## What Must Not Happen Yet",
            "",
        ]
    )
    lines.extend(f"- {item}" for item in report["what_must_not_happen_yet"])

    lines.extend(
        [
            "",
            "## Stage 4C Gate Implication",
            "",
            f"{gate['implication']}",
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
    evidence = report["evidence_summary"]
    gate = report["stage4c_gate_status"]

    print("=" * 72)
    print(f"STAGE 4 PILOT RESULT: {gate['headline']}")
    print("=" * 72)
    print(f"Pilot: {meta['pilot_name']}")
    print(f"CSV: {meta['csv_path']}")
    print(
        "Rows: total={total_rows} valid={valid_rows} invalid={invalid_rows} "
        "merge_ready={merge_ready_rows} review_required={review_required_rows} "
        "blocked={blocked_rows}".format(**summary)
    )
    print(
        "Blockers: errors={error_count} warnings={warning_count} "
        "invalid_fields={invalid_field_count} duplicate_pole_id={duplicate_pole_id_count} "
        "missing_pole_id={missing_pole_id_count}".format(**summary)
    )
    print(
        "Evidence: status={status} checked={checked} found={found}/{total} "
        "missing={missing} unreferenced={unreferenced} duplicate_names={duplicate_names} "
        "invalid_names={invalid_names}".format(
            status=evidence["status"],
            checked=evidence["checked"],
            found=evidence["referenced_photos_found"],
            total=evidence["referenced_photos_total"],
            missing=len(evidence["missing_referenced_photos"]),
            unreferenced=len(evidence["unreferenced_photos"]),
            duplicate_names=len(evidence["duplicate_photo_names"]),
            invalid_names=len(evidence["invalid_photo_naming_patterns"]),
        )
    )
    print("Top issues:")
    if report["top_issues"]:
        for index, item in enumerate(report["top_issues"], start=1):
            print(f"  {index}. {item['severity']} x{item['count']}: {item['message']}")
    else:
        print("  1. None")
    print(f"Next action: {report['operator_next_action']}")
    print(f"Stage 4C gate: {gate['decision']}")
    print(f"Gate implication: {gate['implication']}")
    print("Reports:")
    print(f"  JSON: {_relative(Path(report_paths['json']))}")
    print(f"  Markdown: {_relative(Path(report_paths['markdown']))}")
    print("Do not start Stage 4C runtime integration from this result alone.")


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


def _ensure_required_json_keys(report: dict[str, Any]) -> None:
    missing = [key for key in MANDATORY_JSON_KEYS if key not in report]
    if missing:
        raise RuntimeError(f"Generated report is missing mandatory JSON keys: {missing}")


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)

    csv_path = args.csv.resolve()
    pilot_name = args.pilot_name or args.csv.stem
    out_dir = args.out.resolve() if args.out else (DEFAULT_OUT_ROOT / pilot_name)
    evidence_dir = args.evidence_dir.resolve() if args.evidence_dir else None

    try:
        if not csv_path.exists():
            raise FileNotFoundError(f"Pilot CSV not found: {csv_path}")

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
        exit_code = 0
    except (FileNotFoundError, OSError, UnicodeError, ValueError) as exc:
        report = build_failure_report(
            csv_path=csv_path,
            pilot_name=pilot_name,
            out_dir=out_dir,
            evidence_dir=evidence_dir,
            error_message=str(exc),
        )
        exit_code = 1

    _ensure_required_json_keys(report)
    report_paths = write_reports(report, out_dir)
    print_terminal_summary(report, report_paths)
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
