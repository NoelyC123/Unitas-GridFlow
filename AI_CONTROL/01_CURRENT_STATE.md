# GridFlow Current State

Purpose: authoritative current-state file for all GridFlow workers and project reviewers.

## Current Status

Stage 5G Complete - Designer Review Ready.

Stage 4C is complete. The backend reconciliation pipeline is operational:

```text
Baseline -> Field -> Matching -> Merge -> QA
```

Stage 5 has produced a pilot-ready review package:

- ✅ Stage 5A: 11 pilot reports
- ✅ Stage 5B: Review workspace
- ✅ Stage 5C: Map overlay
- ✅ Stage 5D: Quick wins (job names, navigation, errors)
- ✅ Stage 5E: Pipeline output registration
- ✅ Stage 5F: Truthfulness hardening (114 review document)
- ✅ Stage 5G: Designer review kit

The next active phase is an in-person designer review, not broad new feature implementation.

## Current Product Identity

GridFlow is a survey-to-design reconciliation platform for UK overhead line infrastructure workflows.

It sits between field survey evidence and design preparation. It correlates DNO or survey baseline records with field evidence, identifies evidence confidence, generates verification flags, and produces QA outputs that help designers prepare structured DNO data requests.

GridFlow is not:

- an autonomous design system,
- a DNO records replacement,
- a compliance certifier,
- a PoleCAD replacement,
- a production multi-user SaaS deployment,
- a full GIS product.

The Stage 5C map overlay is a preview/review overlay for baseline-field comparison. It should not be described as production GIS.

## Current Modules And Surfaces

Stage 4C backend modules:

- `gridflow/baseline/` - baseline ingestion, schema validation, coordinate transformation, support number normalization, route reconstruction.
- `gridflow/field/` - structured field evidence import, notes parsing, evidence quality scoring, special flag detection.
- `gridflow/matching/` - support number matching, confidence scoring, conflict detection, match register generation.
- `gridflow/merge/` - merged pole records, verification flags, design blocker analysis, QA report generation.

Unified CLI:

- `scripts/run_pipeline.py`

Stage 5A pilot reports:

- `00_pilot_output_pack_index.md`
- `01_baseline_dataset.json`
- `02_field_dataset.json`
- `03_match_register.csv`
- `04_merged_dataset.json`
- `05_qa_report.md`
- `06_dno_data_request.md`
- `07_design_readiness_summary.md`
- `08_match_confidence_analysis.md`
- `09_verification_flags_breakdown.md`
- `10_evidence_provenance_log.md`

Stage 5B workspace routes:

- `/workspace/view/<job_id>`
- `/workspace/pole/<job_id>/<support_number>`

Stage 5C preview map overlay:

- `/map/overlay/<job_id>`
- overlay JSON endpoint
- baseline-field comparison view

Stage 5E registration bridge:

- `scripts/run_pipeline.py --register --job-id <job_id>`
- optional `--overwrite-registration`
- registered output under `uploads/jobs/<job_id>/`

Stage 5G designer review assets:

- `AI_CONTROL/115_DESIGNER_REVIEW_SCRIPT.md`
- `AI_CONTROL/115_DESIGNER_ONE_PAGER.html`

## Current Validation Status

Latest expected test baseline:

```text
1355 passed
```

Validated reference dataset:

- `real_pilot_data/P_LOCAL_001/enwl_enrichment_clean`

Known P_LOCAL_001 outcomes:

- 10/10 poles matched.
- 9 HIGH evidence quality.
- 1 MEDIUM evidence quality.
- 100% match rate.
- All 10 poles have `design_blocked=True`.
- QA and pilot-pack reports generate successfully.
- Workspace and preview overlay can review registered output.

The `design_blocked=True` result is correct and expected for this dataset. It reflects that identity and evidence reconciliation can succeed while final design remains blocked pending authoritative DNO engineering records such as voltage, conductor specification, pole class or strength rating, equipment ratings, and inspection history.

## Current Weakness

The current weakness is designer validation.

P_LOCAL_001 proves the workflow on a controlled reference evidence set. It does not yet prove that a practising UK OHL designer understands, trusts, or would use the output on a live project.

The next task is to conduct the structured designer review using:

- `AI_CONTROL/115_DESIGNER_REVIEW_SCRIPT.md`
- `AI_CONTROL/115_DESIGNER_ONE_PAGER.html`
- registered job `P_LOCAL_DESIGNER_REVIEW`
- live feedback capture route when available

## Current Next Phase

Current active phase:

```text
Conduct Designer Review - In-Person Walk-Through
```

Do not start Stage 6 implementation until designer feedback is captured and documented.

Expected review output:

- `AI_CONTROL/116_DESIGNER_FEEDBACK_FINDINGS.md`

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

Stage 4C and Stage 5 pilot-pack outputs provide reconciliation, QA, review navigation, and DNO request preparation. They do not certify:

- voltage,
- conductor size or type,
- pole class,
- equipment ratings,
- inspection history,
- final design readiness,
- DNO-grade compliance.

Conductor spec and pole class/strength rating require authoritative confirmation from DNO baseline engineering records. Field evidence may suggest these attributes, but they should not be treated as authoritative design inputs unless confirmed by DNO or baseline records.

Standards references in reports are guidance for review and request preparation only. They do not mean compliance has been verified.
