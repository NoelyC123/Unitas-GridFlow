#!/usr/bin/env python3
# ruff: noqa: E402
"""
GridFlow Unified Pipeline CLI

Runs the complete four-stage GridFlow pipeline in a single command:
  Stage 1: Baseline Ingest (CSV → BaselineDataset)
  Stage 2: Field Evidence Import (folders → FieldDataset)
  Stage 3: Baseline-to-Field Matching (→ MatchRegister)
  Stage 4: Merge + QA Analysis (→ MergedDataset + QA Report)
"""

import json
import logging
import sys
import time
from argparse import ArgumentParser
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from gridflow.baseline import (
    CoordinateTransformer,
    CSVParser,
    RouteReconstructor,
    SchemaValidator,
)
from gridflow.field import (
    EvidenceQualityScorer,
    FolderScanner,
)
from gridflow.matching import (
    ConfidenceScorer,
    RegisterBuilder,
    SupportNumberMatcher,
)
from gridflow.merge import DataMerger, QAReportGenerator
from gridflow.reports import (
    DesignReadinessReporter,
    DNORequestReporter,
    EvidenceProvenanceReporter,
    MatchConfidenceReporter,
    PilotIndexReporter,
    VerificationFlagsReporter,
)

logger = logging.getLogger(__name__)


# ─── Argument parsing ────────────────────────────────────────────────────────


def parse_args():
    p = ArgumentParser(
        description="GridFlow — Survey-to-Design Workflow Pipeline",
        epilog=(
            "Example:\n"
            "  python scripts/run_pipeline.py \\\n"
            "    --baseline baseline.csv \\\n"
            "    --field evidence_folder/ \\\n"
            "    --output ./output/"
        ),
    )
    p.add_argument("--baseline", required=True, type=Path, help="Path to DNO baseline CSV file")
    p.add_argument("--field", required=True, type=Path, help="Path to field evidence root folder")
    p.add_argument(
        "--output", required=True, type=Path, help="Output directory (created if not exists)"
    )
    p.add_argument(
        "--baseline-format",
        default="AUTO",
        choices=["AUTO", "ENWL", "TRIMBLE", "GENERIC"],
        help="Baseline CSV format (default: AUTO-detect)",
    )
    p.add_argument(
        "--report",
        action="store_true",
        default=True,
        help="Generate QA report markdown (default: yes)",
    )
    p.add_argument(
        "--csv",
        action="store_true",
        default=True,
        help="Generate per-pole CSV summary (default: yes)",
    )
    p.add_argument("--strict", action="store_true", help="Fail on any validation error")
    p.add_argument(
        "--no-coord-transform",
        action="store_true",
        help="Skip OSGB36→WGS84 coordinate transformation",
    )
    p.add_argument("--no-route-reconstruct", action="store_true", help="Skip route reconstruction")
    p.add_argument(
        "--job-id",
        type=str,
        default=None,
        help="Job ID for registration. Auto-generated if not provided.",
    )
    p.add_argument(
        "--register",
        action="store_true",
        default=False,
        help="Register pipeline output into uploads/jobs/<job_id>/ for web access.",
    )
    p.add_argument(
        "--overwrite-registration",
        action="store_true",
        default=False,
        help="Allow --register to replace an existing uploads/jobs/<job_id>/ directory.",
    )
    p.add_argument("--log-level", default="INFO", choices=["DEBUG", "INFO", "WARNING", "ERROR"])
    return p.parse_args()


# ─── Console helpers ─────────────────────────────────────────────────────────

SEP = "=" * 70


def banner(msg):
    print(SEP)
    print(msg)
    print(SEP)


def stage_header(n, total, name):
    print(f"\nStage {n}/{total} — {name}...")


def stage_ok(elapsed):
    print(f"  ✓ Complete ({elapsed:.2f}s)")


def stage_fail(elapsed, err):
    print(f"  ✗ FAILED ({elapsed:.2f}s): {err}")


# ─── Stage implementations ───────────────────────────────────────────────────


def run_stage1(args, run_dir: Path) -> tuple[object, dict]:
    """Stage 1: Baseline Ingest."""
    t0 = time.monotonic()
    result = {}

    parser = CSVParser()
    fmt_hint = None if args.baseline_format == "AUTO" else args.baseline_format
    fmt_detected = parser.detect_format(args.baseline) if fmt_hint is None else fmt_hint
    dataset = parser.parse(args.baseline, format_hint=fmt_hint)

    print(f"  Format detected: {fmt_detected}")
    print(f"  Poles loaded: {dataset.pole_count}")

    validator = SchemaValidator()
    report = validator.validate_dataset(dataset)
    dataset.validation_report = report
    print(f"  Validation: {report.valid_poles} valid, {report.error_count} errors")

    if report.error_count and args.strict:
        raise RuntimeError(f"Validation failed: {report.error_count} errors (strict mode)")

    if not args.no_coord_transform:
        try:
            transformer = CoordinateTransformer()
            dataset = transformer.transform_dataset(dataset)
            print("  Coordinates: OSGB36 → WGS84 transformed")
        except Exception as e:
            logger.warning("Coordinate transform skipped: %s", e)
            print("  Coordinates: transform skipped (pyproj unavailable)")

    if not args.no_route_reconstruct:
        reconstructor = RouteReconstructor()
        dataset = reconstructor.reconstruct_sequences(dataset)

    out_path = run_dir / "01_baseline_dataset.json"
    with open(out_path, "w") as f:
        json.dump(dataset.to_dict(), f, indent=2, default=str)

    elapsed = time.monotonic() - t0
    result = {
        "status": "PASS",
        "poles": dataset.pole_count,
        "errors": report.error_count,
        "format_detected": fmt_detected,
        "duration_seconds": round(elapsed, 3),
    }
    stage_ok(elapsed)
    return dataset, result


def run_stage2(args, run_dir: Path) -> tuple[object, dict]:
    """Stage 2: Field Evidence Import."""
    t0 = time.monotonic()

    scanner = FolderScanner()
    dataset = scanner.scan(args.field)

    scorer = EvidenceQualityScorer()
    dataset = scorer.score_dataset(dataset)

    summary = dataset.evidence_summary
    print(f"  Poles scanned: {dataset.total_poles}")
    print(
        f"  Evidence quality: {summary.get('high', 0)} HIGH / "
        f"{summary.get('medium', 0)} MEDIUM / {summary.get('low', 0)} LOW"
    )
    print(f"  Notes parsed: {summary.get('notes_present', 0)}/{dataset.total_poles}")

    # Collect special flags summary
    flag_counts: dict[str, int] = {}
    for pole in dataset.poles:
        for flag in pole.special_flags:
            flag_counts[flag] = flag_counts.get(flag, 0) + 1
    if flag_counts:
        flag_str = " ".join(f"{k}({v})" for k, v in sorted(flag_counts.items()))
        print(f"  Special flags: {flag_str}")

    out_path = run_dir / "02_field_dataset.json"
    with open(out_path, "w") as f:
        json.dump(dataset.model_dump(), f, indent=2, default=str)

    elapsed = time.monotonic() - t0
    result = {
        "status": "PASS",
        "poles": dataset.total_poles,
        "high": summary.get("high", 0),
        "medium": summary.get("medium", 0),
        "low": summary.get("low", 0),
        "duration_seconds": round(elapsed, 3),
    }
    stage_ok(elapsed)
    return dataset, result


def run_stage3(baseline_dataset, field_dataset, run_dir: Path) -> tuple[object, dict]:
    """Stage 3: Baseline-to-Field Matching."""
    t0 = time.monotonic()

    matcher = SupportNumberMatcher()
    match_results = matcher.match(baseline_dataset, field_dataset)

    scorer = ConfidenceScorer()
    b_by_id = {p.pole_id: p for p in baseline_dataset.poles}
    f_by_folder = {p.folder_name: p for p in field_dataset.poles}
    for mr in match_results:
        bp = b_by_id.get(mr.baseline_pole_id)
        fp = f_by_folder.get(mr.field_folder or "")
        if bp:
            scorer.score(mr, bp, fp)

    builder = RegisterBuilder()
    register = builder.build(match_results, baseline_dataset, field_dataset)

    matched = register.matched
    total_b = register.baseline_total
    print(f"  Matched: {matched}/{total_b} poles")
    print(f"  Match rate: {register.match_rate:.1f}%")
    print(
        f"  Confidence: {register.high_confidence} HIGH / "
        f"{register.medium_confidence} MEDIUM / {register.low_confidence} LOW"
    )

    # Conflict summary
    conflict_counts: dict[str, int] = {}
    for entry in register.entries:
        for flag in entry.conflict_flags:
            conflict_counts[flag] = conflict_counts.get(flag, 0) + 1
    if conflict_counts:
        conflict_str = " ".join(f"{k}({v})" for k, v in sorted(conflict_counts.items()))
        print(f"  Conflicts detected: {conflict_str}")

    # Write outputs
    out_json = run_dir / "03_match_register.json"
    out_data = {
        "metadata": {
            "baseline_total": register.baseline_total,
            "field_total": register.field_total,
            "matched": register.matched,
            "match_rate": register.match_rate,
            "high_confidence": register.high_confidence,
            "medium_confidence": register.medium_confidence,
            "low_confidence": register.low_confidence,
        },
        "entries": [e.model_dump() for e in register.entries],
    }
    with open(out_json, "w") as f:
        json.dump(out_data, f, indent=2, default=str)

    out_csv = run_dir / "03_match_register.csv"
    builder.export_csv(register, out_csv)

    elapsed = time.monotonic() - t0
    result = {
        "status": "PASS",
        "matched": matched,
        "unmatched": register.unmatched_baseline,
        "match_rate": round(register.match_rate, 1),
        "duration_seconds": round(elapsed, 3),
    }
    stage_ok(elapsed)
    return register, result


def run_stage4(baseline_dataset, field_dataset, register, run_dir: Path) -> tuple[object, dict]:
    """Stage 4: Merge + QA Analysis."""
    t0 = time.monotonic()

    merger = DataMerger()
    merged = merger.merge(baseline_dataset, field_dataset, register)

    print(f"  Merged poles: {merged.total_matched}")
    print(f"  Design ready: {merged.design_ready_count} poles")
    print(f"  Design blocked: {merged.design_blocked_count} poles")

    # Verification summary
    poles = merged.poles
    conductor_n = sum(1 for p in poles if p.conductor_verification_required)
    poleclass_n = sum(1 for p in poles if p.pole_class_verification_required)
    identity_n = sum(1 for p in poles if p.identity_verification_required)
    conflict_n = sum(1 for p in poles if p.equipment_conflict_flag)

    print("  Verification required:")
    if conductor_n:
        print(f"    - Conductor spec: {conductor_n} poles")
    if poleclass_n:
        print(f"    - Pole class: {poleclass_n} poles")
    if identity_n:
        print(f"    - Identity confirmation: {identity_n} poles")
    if conflict_n:
        print(f"    - Equipment conflicts: {conflict_n} poles")

    # Write outputs
    out_json = run_dir / "04_merged_dataset.json"
    with open(out_json, "w") as f:
        json.dump(merged.model_dump(), f, indent=2, default=str)

    reporter = QAReportGenerator()
    out_csv = run_dir / "04_merged_dataset.csv"
    reporter.export_csv(merged, out_csv)

    out_report = run_dir / "05_qa_report.md"
    report_text = reporter.generate(merged)
    with open(out_report, "w") as f:
        f.write(report_text)

    elapsed = time.monotonic() - t0
    result = {
        "status": "PASS",
        "merged": merged.total_matched,
        "design_ready": merged.design_ready_count,
        "design_blocked": merged.design_blocked_count,
        "duration_seconds": round(elapsed, 3),
    }
    stage_ok(elapsed)
    return merged, result


def run_stage5a_reports(merged, run_dir: Path, job_context: dict | None = None) -> list[Path]:
    """Generate Stage 5A pilot output pack reports."""
    logger.info("=" * 60)
    logger.info("Stage 5A — Generating Pilot Reports")
    logger.info("=" * 60)

    merged_poles = merged.poles
    reporters = [
        ("00_pilot_output_pack_index.md", PilotIndexReporter()),
        ("06_dno_data_request.md", DNORequestReporter()),
        ("07_design_readiness_summary.md", DesignReadinessReporter()),
        ("08_match_confidence_analysis.md", MatchConfidenceReporter()),
        ("09_verification_flags_breakdown.md", VerificationFlagsReporter()),
        ("10_evidence_provenance_log.md", EvidenceProvenanceReporter()),
    ]

    written: list[Path] = []
    for filename, reporter in reporters:
        logger.info("Generating %s...", filename)
        report_text = reporter.generate(merged_poles, job_context=job_context)
        path = run_dir / filename
        path.write_text(report_text, encoding="utf-8")
        logger.info("✓ Report: %s (%d chars)", path.name, len(report_text))
        written.append(path)

    logger.info("Stage 5A reports generated successfully")
    return written


# ─── Pipeline orchestrator ───────────────────────────────────────────────────


def main():
    args = parse_args()

    logging.basicConfig(
        level=getattr(logging, args.log_level),
        format="%(asctime)s %(name)s %(levelname)s %(message)s",
    )

    # Create run directory
    run_id = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    run_dir = args.output / f"pipeline_run_{run_id}"
    run_dir.mkdir(parents=True, exist_ok=True)

    t_pipeline_start = time.monotonic()

    banner(
        f"GRIDFLOW PIPELINE — SURVEY-TO-DESIGN WORKFLOW\n"
        f"{'=' * 70}\n"
        f"Run ID:  {run_id}\n"
        f"Baseline: {args.baseline}\n"
        f"Field:    {args.field}\n"
        f"Output:   {run_dir}/"
    )

    stages: dict[str, dict] = {}
    overall_status = "PASS"
    baseline_dataset = field_dataset = register = merged = None

    # ── Stage 1 ──
    stage_header(1, 4, "Baseline Ingest")
    try:
        baseline_dataset, stages["baseline_ingest"] = run_stage1(args, run_dir)
    except Exception as e:
        elapsed = time.monotonic() - t_pipeline_start
        stage_fail(elapsed, e)
        stages["baseline_ingest"] = {"status": "FAILED", "error": str(e)}
        overall_status = "FAILED"
        _write_summary(run_id, args, run_dir, stages, overall_status, None, t_pipeline_start)
        return 1

    # ── Stage 2 ──
    stage_header(2, 4, "Field Evidence Import")
    try:
        field_dataset, stages["field_import"] = run_stage2(args, run_dir)
    except Exception as e:
        elapsed = time.monotonic() - t_pipeline_start
        stage_fail(elapsed, e)
        stages["field_import"] = {"status": "FAILED", "error": str(e)}
        overall_status = "FAILED"
        _write_summary(run_id, args, run_dir, stages, overall_status, None, t_pipeline_start)
        return 1

    # ── Stage 3 ──
    stage_header(3, 4, "Baseline-to-Field Matching")
    try:
        register, stages["matching"] = run_stage3(baseline_dataset, field_dataset, run_dir)
    except Exception as e:
        elapsed = time.monotonic() - t_pipeline_start
        stage_fail(elapsed, e)
        stages["matching"] = {"status": "FAILED", "error": str(e)}
        overall_status = "FAILED"
        _write_summary(run_id, args, run_dir, stages, overall_status, None, t_pipeline_start)
        return 1

    # ── Stage 4 ──
    stage_header(4, 4, "Merge + QA Analysis")
    try:
        merged, stages["merge"] = run_stage4(baseline_dataset, field_dataset, register, run_dir)
    except Exception as e:
        elapsed = time.monotonic() - t_pipeline_start
        stage_fail(elapsed, e)
        stages["merge"] = {"status": "FAILED", "error": str(e)}
        overall_status = "FAILED"
        _write_summary(run_id, args, run_dir, stages, overall_status, None, t_pipeline_start)
        return 1

    registration_job_id = None
    if args.register:
        from gridflow.registration import generate_job_id

        registration_job_id = args.job_id or generate_job_id()

    job_context = {
        "job_id": registration_job_id or run_id,
        "baseline_file": Path(args.baseline).name,
        "baseline_path": str(args.baseline),
        "field_folder": Path(args.field).name,
        "field_path": str(args.field),
        "output_dir": str(run_dir),
        "run_timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }

    try:
        report_paths = run_stage5a_reports(merged, run_dir, job_context=job_context)
        print(f"  Stage 5A reports: {len(report_paths)} files")
    except Exception as e:
        logger.warning("Stage 5A reporting failed (pipeline result preserved): %s", e)
        print(f"  Stage 5A reports: FAILED ({e})")

    # ── Summary ──
    total_elapsed = time.monotonic() - t_pipeline_start
    _write_summary(run_id, args, run_dir, stages, overall_status, merged, t_pipeline_start)

    match_rate = stages.get("matching", {}).get("match_rate", 0.0)
    design_ready = merged.design_ready_count if merged else 0
    design_blocked = merged.design_blocked_count if merged else 0
    total_poles = baseline_dataset.pole_count if baseline_dataset else 0

    print(f"\n{SEP}")
    print(f"PIPELINE COMPLETE — {total_elapsed:.2f}s")
    print(SEP)
    print(f"Overall status:  {overall_status}")
    print(f"Match rate:      {match_rate:.1f}%")
    print(f"Design ready:    {design_ready}/{total_poles} poles")
    print(f"Design blocked:  {design_blocked}/{total_poles} poles (DNO data required)")
    print()
    print("Output files:")
    for f in sorted(run_dir.iterdir()):
        print(f"  {f.name}")
    print()
    print("Next steps: Review 05_qa_report.md for required DNO actions.")
    print(SEP)

    if args.register:
        from gridflow.registration import (
            print_registration_summary,
            register_pipeline_output,
        )

        job_id = registration_job_id or args.job_id
        job_dir = register_pipeline_output(
            pipeline_run_dir=run_dir,
            job_id=job_id,
            overwrite=args.overwrite_registration,
        )
        print_registration_summary(job_id, job_dir)

    return 0


def _write_summary(
    run_id: str,
    args,
    run_dir: Path,
    stages: dict,
    overall_status: str,
    merged,
    t_start: float,
) -> None:
    """Write pipeline_summary.json to run directory."""
    elapsed = time.monotonic() - t_start
    match_rate = stages.get("matching", {}).get("match_rate", 0.0)

    summary = {
        "run_id": run_id,
        "run_date": datetime.now().isoformat(),
        "baseline_source": str(args.baseline),
        "field_source": str(args.field),
        "baseline_format_detected": stages.get("baseline_ingest", {}).get(
            "format_detected", "UNKNOWN"
        ),
        "duration_seconds": round(elapsed, 3),
        "stages": stages,
        "overall_status": overall_status,
        "match_rate": match_rate,
        "design_ready_count": merged.design_ready_count if merged else 0,
        "design_blocked_count": merged.design_blocked_count if merged else 0,
        "output_directory": str(run_dir),
    }

    with open(run_dir / "pipeline_summary.json", "w") as f:
        json.dump(summary, f, indent=2, default=str)


if __name__ == "__main__":
    sys.exit(main())
