# GridFlow Current State

Purpose: authoritative current-state file for all GridFlow workers and project reviewers.

## Current Status

Stage 4C is COMPLETE.

GridFlow now has a working backend survey-to-design reconciliation pipeline for overhead line infrastructure workflows.

The operational backend pipeline is:

```text
Baseline -> Field -> Matching -> Merge -> QA
```

Expanded:

```text
Baseline Ingest
  -> Field Evidence Import
  -> Baseline-to-Field Matching
  -> Merge + QA
  -> Structured Outputs
```

## Current Product Identity

GridFlow is a survey-to-design reconciliation platform for UK overhead line infrastructure workflows.

It sits between field survey evidence and design preparation. It correlates DNO or survey baseline records with field evidence, identifies evidence confidence, generates verification flags, and produces QA outputs that help designers prepare structured DNO data requests.

GridFlow is not:

- an autonomous design system,
- a DNO records replacement,
- a compliance certifier,
- a PoleCAD replacement,
- a production multi-user SaaS deployment.

## Current Modules

Stage 4C backend modules now present:

- `gridflow/baseline/` - baseline ingestion, schema validation, coordinate transformation, support number normalization, route reconstruction.
- `gridflow/field/` - structured field evidence import, notes parsing, evidence quality scoring, special flag detection.
- `gridflow/matching/` - support number matching, confidence scoring, conflict detection, match register generation.
- `gridflow/merge/` - merged pole records, verification flags, design blocker analysis, QA report generation.

Unified CLI:

- `scripts/run_pipeline.py`

Stage CLIs:

- `scripts/ingest_baseline.py`
- `scripts/import_field_evidence.py`
- `scripts/run_matching.py`
- `scripts/run_merge.py`

## Current Validation Status

Validated against:

- `real_pilot_data/P_LOCAL_001/enwl_enrichment_clean`

Verified outcomes:

- 10/10 poles matched.
- 9 HIGH evidence quality.
- 1 MEDIUM evidence quality.
- 100% match rate.
- All 10 poles have `design_blocked=True`.
- QA reports generated successfully.
- Unified pipeline operational.
- 1,277 tests passing.

The `design_blocked=True` result is correct and expected. It reflects that identity and evidence reconciliation can succeed while final design remains blocked pending DNO engineering data such as voltage, conductor specification, pole class, equipment ratings, and inspection history.

## Current Limitations

GridFlow does not yet have:

- a review UI,
- production multi-user workflow,
- PoleCAD export,
- live DNO API integration,
- production deployment layer,
- broad multi-DNO validation beyond the current ENWL-focused evidence set,
- final design authorization capability.

Current validation is strongest for ENWL-style support number and evidence workflows. Additional pilot work is required before broader claims across DNO regions, larger route datasets, and production contractor workflows.

## Current Next Phase

Current next phase:

```text
Stage 5 - Pilot Hardening
```

Stage 5 focus:

- stabilize the completed Stage 4C backend pipeline,
- improve operational review workflows,
- plan and build review workspace capability,
- validate larger and multi-job datasets,
- prepare ICP/Tier-1 pilot workflows,
- package DNO request outputs and designer review evidence.

## Source Of Truth Hierarchy

1. Current task prompt from Noel or controller.
2. `AI_CONTROL/01_CURRENT_STATE.md`, `AI_CONTROL/02_CURRENT_TASK.md`, and `AI_CONTROL/00_PROJECT_BOARD.md`.
3. Stage completion reports and current specification docs.
4. Code, tests, and generated validation outputs.
5. Historical docs and older control files.
6. AI memory or chat summaries.

If sources conflict, prefer the newest committed control file and report the conflict before making broad changes.

## Protected Boundaries

Do not overclaim GridFlow output.

Stage 4C provides reconciliation and QA. It does not certify:

- voltage,
- conductor size or type,
- pole class,
- equipment ratings,
- inspection history,
- final design readiness.

These remain DNO/designer responsibilities.
