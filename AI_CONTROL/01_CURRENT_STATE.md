# GridFlow Current State

Purpose: authoritative current-state file for all GridFlow workers and project reviewers.

## Current Status

Stage 7A Complete — Photo integration backend shipped. Stage 7 workspace maturation is
the active phase.

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

Stage 6 ENWL evidence integration is complete:

- ✅ Stage 6A: ENWL trace parser, four-level evidence classification
- ✅ Stage 6B: Three-source evidence combiner, workspace DNO Evidence display
- ✅ Stage 6C: Formal pole-to-ENWL linking (12/12 poles on P_LOCAL_002)
- ✅ Stage 6D: Conflict detection (0 conflicts detected on P_LOCAL_002)
- ✅ Stage 6E: Conservative design-readiness logic with four readiness levels

Stage 7 workspace maturation is in progress:

- ✅ Stage 7A: Photo backend — `gridflow/photos/loader.py`, CLI, 99 photos across 12 poles
- ⏳ Stage 7B: Workspace photo display (blocked on photo-serving strategy decision)

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

Stage 6 ENWL evidence modules:

- `gridflow/enwl_trace/` - Stage 6A: conservative ENWL trace GeoJSON parser, four-level relationship classification.
- `gridflow/evidence_combiner/` - Stage 6B/6C: three-source evidence combiner and formal pole-to-ENWL linker.
- `gridflow/conflict_detector/` - Stage 6D: field vs ENWL attribute conflict detection.
- `gridflow/readiness/` - Stage 6E: conservative four-level design-readiness assessor.
- `gridflow/workspace/` - workspace display adapters for ENWL evidence, readiness, and review data.

Stage 7A photo module:

- `gridflow/photos/` - photo loader, PhotoSet/PhotoFile schemas, type detection, survey-level photo summary.

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

Latest test baseline:

```text
1470 passed, 9 skipped
```

Validated reference datasets:

**P_LOCAL_001** (`real_pilot_data/P_LOCAL_001/enwl_enrichment_clean`):

- 10/10 poles matched.
- 9 HIGH evidence quality, 1 MEDIUM.
- 100% match rate.
- All 10 poles `design_blocked=True` (correct — awaiting DNO records).
- QA and pilot-pack reports generate successfully.

**P_LOCAL_002** (`real_pilot_data/P_LOCAL_002/enwl_enrichment_clean`):

- 12/12 poles matched (100% match rate).
- 12/12 notes detected (post-8afeee0 fix).
- 12/12 evidence quality HIGH.
- 12/12 poles formally linked to ENWL records via Stage 6C.
- 3 HIGH confidence links (Poles 03, 05, 06 via `fid_polestructure`).
- 7 MEDIUM confidence links (support_no match).
- 0 conflicts detected (Stage 6D).
- 0 poles `design_ready=True` (correct — conductor specification not per-span confirmed).
- 3 poles expected `review_required` (Stage 6E: Poles 03, 05, 06 — HIGH link, route conductor).
- 7 poles `not_ready` (MEDIUM link, no conductor evidence per span).
- 99 photos across 12 poles detected by Stage 7A loader.
- 10/12 baseline coordinates complete (903101 and 903203 still missing easting/northing).

The `design_blocked=True` result is correct for both datasets. Identity and evidence
reconciliation succeeded; final design remains blocked pending DNO engineering records
(conductor specification, pole class/strength rating).

## Current Weakness

Primary weakness: no real Unitas operational job validated end-to-end yet.

P_LOCAL_001 and P_LOCAL_002 both use local evidence from `real_pilot_data/` (gitignored).
Neither has been run against a job originating from a real Unitas project with a real
client baseline. Until GridFlow is used on an actual Unitas OHL job, the operational gap
remains unproven.

Secondary weakness: photo serving not resolved.

Stage 7A provides a photo loader and CLI but photos are not yet visible in the workspace.
The workspace still shows only "Photos: N" (a count). The serving strategy must be
decided and implemented before Stage 7B can be validated. See
`AI_CONTROL/133_STAGE7B_PHOTO_SERVING_DECISION.md`.

Coordinate gaps on P_LOCAL_002: supports 903101 and 903203 have blank easting/northing
in `P_LOCAL_002_baseline.csv`. They are flagged with `coordinate_status=MISSING` but
coordinates have not yet been populated from ENWL FID lookup.

## Current Next Phase

Current active phase:

```text
Stage 7B — Workspace Photo Display
```

Prerequisites before Stage 7B can start:

- Adopt photo-serving strategy from `AI_CONTROL/133_STAGE7B_PHOTO_SERVING_DECISION.md`
- Implement Flask route (Option A) for local dev validation
- Add photo section to `app/templates/workspace/pole_detail.html`

After Stage 7B, validate on the next real Unitas OHL project.

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
