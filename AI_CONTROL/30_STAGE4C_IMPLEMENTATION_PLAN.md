# Stage 4C Implementation Plan

**Date:** 2026-05-17
**Based on:** P_LOCAL_002 Phase 4 pilot — CONDITIONAL GO verdict
**Reference:** `AI_CONTROL/98_PHASE_4_VERDICT.md`, `AI_CONTROL/100_STAGE_4C_SPECIFICATION.md`,
`real_pilot_data/P_LOCAL_002/route_notes/P_LOCAL_002_COORDINATE_COMPLETENESS_REVIEW.md`

---

## Current Evidence Basis

P_LOCAL_002 Phase 4 pilot completed on 2026-05-17 with the following confirmed state:

### Evidence audit — folder/audit level: CLEAN

| Measure | Result |
|---|---|
| Pole folders | 12 / 12 |
| Known support numbers | 12 / 12 |
| Notes present | 12 / 12 |
| Folders with missing evidence flags | 0 / 12 |

Source: `real_pilot_data/P_LOCAL_002/route_notes/P_LOCAL_002_EVIDENCE_AUDIT.md`

### Coordinate completeness: CONDITIONAL

| Measure | Result |
|---|---|
| Baseline records with easting + northing | 10 / 12 |
| Supports with confirmed coordinates | 902202, 902201, 900343, 900342A, 900344, 900345, 903104, 903103, 903102, 903202 |
| Supports missing coordinates | **903101** (FID 16788439) and **903203** (FID 16938106) |

Coordinate values for 903101 and 903203 were not found in any structured text source in
the current evidence pack. They must not be inferred, estimated from adjacent poles, or
invented. They must come from a direct ENWL Network Asset Viewer / FID popup lookup or
GPS capture.

Source: `real_pilot_data/P_LOCAL_002/route_notes/P_LOCAL_002_COORDINATE_COMPLETENESS_REVIEW.md`

### Phase 4 verdict

The Phase 4 same-site baseline pilot returned **CONDITIONAL GO**. Stage 4C is authorized
to proceed with the conditions documented in `AI_CONTROL/98_PHASE_4_VERDICT.md`.

---

## Stage 4C Objective

Stage 4C is the validation and hardening phase for the GridFlow baseline pipeline. The
core modules already exist and were proven on P_LOCAL_001. Stage 4C must:

1. Run the full pipeline (`Baseline → Field → Matching → Merge → QA`) on P_LOCAL_002
   without manual intervention.
2. Detect the five known P_LOCAL_002 issues automatically in QA output (see
   `98_PHASE_4_VERDICT.md`): coordinate gaps for supports 903101 and 903203, the
   Pole 06 structural conflict, and the content-quality notes for Pole 11 at the
   time it was first examined.
3. Handle missing baseline coordinates conservatively: produce a warning flag per pole,
   not a hard error, and do not invent or estimate coordinates.
4. Confirm that all 12 poles remain `design_blocked = True` — this is the correct
   expected outcome at this stage.
5. Confirm that the pipeline produces all 10 standard reports without error.

Stage 4C does not authorise design. It proves the pipeline is reliable on a real ENWL job.

---

## Recommended Decision

**Conditional build after coordinate closure**

The evidence pack is strong. The baseline-to-evidence structural match is 12/12. Identity
is confirmed for all 12 poles via ENWL FID, SPN, and support number. The two missing
coordinates are a baseline completeness gap, not an identity or evidence gap.

The recommended approach is:

1. Close the coordinate gap (Options A, B, or C in the coordinate review) before
   claiming 12/12 baseline readiness.
2. In the interim, proceed with Stage 4C pipeline implementation using the current
   10/12 coordinate state, with conservative gap handling.
3. Re-run pipeline validation after coordinate closure to confirm the full 12/12 result.

This allows Stage 4C work to begin without waiting for the coordinate gap, provided
the gap handling produces visible, honest warnings in the output rather than silence.

---

## First Milestone

**M1 — Pipeline run on P_LOCAL_002 with coordinate-gap warnings**

The first safe Stage 4C milestone is to run `scripts/run_pipeline.py` against P_LOCAL_002
and confirm:

- 12/12 structural matches
- Poles 903101 and 903203 flagged with `baseline_coordinate_missing` in merged output
- Pole 06 conflict surfaces in QA report
- All 10 reports generated without error
- `design_blocked = True` for all 12 poles

This milestone is achievable with the existing pipeline code. It requires only:
- A P_LOCAL_002 baseline CSV (already at `real_pilot_data/P_LOCAL_002/csv/P_LOCAL_002_baseline.csv`)
- The enriched evidence folder (already at `real_pilot_data/P_LOCAL_002/enwl_enrichment_clean/`)
- Possibly a minor addition to the merge/merge-flags layer to surface `baseline_coordinate_missing`

No new modules are required for M1. It is a validation run.

---

## Out of Scope

The following are explicitly out of scope for Stage 4C:

- Design-ready clearance for any pole
- Automatic conductor-to-span acceptance
- Inferred or estimated coordinates treated as truth
- Photo content analysis or OCR
- Mobile field capture tooling
- Structured tablet/digital field entry
- Large workspace UI changes
- PoleCAD export format

---

## Candidate Files / Modules

All existing. No new modules required for M1.

| Module / file | Role | Stage 4C action |
|---|---|---|
| `scripts/run_pipeline.py` | Unified pipeline CLI | Run against P_LOCAL_002; no code change expected |
| `gridflow/baseline/csv_parser.py` | Baseline ingest | Verify blank coordinate rows are accepted, not errored |
| `gridflow/merge/data_merger.py` | Merge engine | Add or confirm `baseline_coordinate_missing` flag propagation |
| `gridflow/merge/verification_flag_generator.py` | Verification flags | Confirm coordinate gap produces a flag, not silent pass |
| `gridflow/merge/qa_report_generator.py` | QA report | Confirm coordinate gap appears in QA report output |
| `real_pilot_data/P_LOCAL_002/csv/P_LOCAL_002_baseline.csv` | Baseline source | Input to pipeline run; has two blank coordinate rows |
| `real_pilot_data/P_LOCAL_002/enwl_enrichment_clean/` | Field evidence | Input to pipeline run |
| `AI_CONTROL/98_PHASE_4_VERDICT.md` | Phase 4 gate | Reference for known issues to be detected |
| `real_pilot_data/P_LOCAL_002/route_notes/P_LOCAL_002_COORDINATE_COMPLETENESS_REVIEW.md` | Coordinate review | Reference for gap status |

---

## Acceptance Criteria

Stage 4C M1 is complete when all of the following hold:

| Criterion | Requirement |
|---|---|
| Evidence audit clean | 12/12 folders, 12/12 notes, 0 missing flags — no regression from current audit |
| Coordinate review exists and is referenced | `P_LOCAL_002_COORDINATE_COMPLETENESS_REVIEW.md` present and cited in pipeline output or QA report |
| Coordinate gaps produce warnings | Poles 903101 and 903203 appear in QA output with `baseline_coordinate_missing` or equivalent flag |
| Coordinate gaps do not produce hard errors | Pipeline completes for all 12 poles; gaps do not block the run |
| Pole 06 conflict appears in QA report | ENWL structural conflict (Stub Pole vs H-pole) appears as a flagged item |
| All 12 poles `design_blocked = True` | No pole is cleared as design-ready |
| All 10 standard reports generated | No report generation error |
| No fabricated coordinates | Baseline CSV rows for 903101 and 903203 remain blank; no values inserted |
| Tests added or updated where code changes | Any change to flag propagation or CSV parser has a corresponding test |
| No design-readiness claim in output | Reports do not assert that any pole is ready for design |

---

## Worker Task Breakdown

Small, independently executable tasks for Codex, Cursor, or Claude Code.

### Task 1 — Validation run (no code change)

**Owner:** Codex or Claude Code
**Scope:** Run `scripts/run_pipeline.py` against P_LOCAL_002 baseline and evidence.
Record the exact output. Confirm which known issues surface automatically and which do not.
Produce a brief result note listing what passed and what was silent.

**Files touched:** None (read-only validation run)
**Acceptance:** Run completes; result note exists

---

### Task 2 — Coordinate gap flag (if not already surfaced)

**Owner:** Codex
**Scope:** If Task 1 shows that blank easting/northing rows in the baseline CSV do not
produce a visible flag in the QA report or merged output, add a `baseline_coordinate_missing`
flag to `gridflow/merge/verification_flag_generator.py` (or equivalent).

**Files touched:** `gridflow/merge/verification_flag_generator.py`,
`tests/merge/` or `tests/test_verification_flags.py`
**Acceptance:** Poles with blank coordinates produce a named flag; poles with coordinates
do not; test covers both paths

---

### Task 3 — Pole 06 conflict detection review

**Owner:** Codex
**Scope:** Confirm whether the structural conflict at Pole 06 (ENWL Stub Pole vs field
H-pole) is surfaced by `gridflow/conflict_detector/` or `gridflow/merge/conflict_detector.py`.
If not, document what rule would be needed and whether it is in scope for Stage 4C.

**Files touched:** Read-only review; possibly `gridflow/conflict_detector/detector.py`
**Acceptance:** Documented finding — either conflict is surfaced automatically or a scoped
task is created for a future Stage 4C sub-task

---

### Task 4 — Coordinate closure (Noel action, not a code task)

**Owner:** Noel
**Scope:** Use the ENWL Network Asset Viewer to look up FID 16788439 (support 903101) and
FID 16938106 (support 903203). Read the coordinates from the pole popup. Enter values into
`real_pilot_data/P_LOCAL_002/csv/P_LOCAL_002_baseline.csv`. Update the pole notes.

**Files touched:** `P_LOCAL_002_baseline.csv`, pole notes for poles 10 and 12
**Acceptance:** Both rows have valid easting and northing; coordinate review updated to
COMPLETE; pipeline re-run confirms 12/12 coordinate completeness

---

### Task 5 — Full M1 acceptance check

**Owner:** Claude Code or Codex
**Scope:** After Tasks 2–4, re-run the pipeline and confirm all M1 acceptance criteria
are met. Produce a short Stage 4C M1 completion note.

**Files touched:** None (validation run + document)
**Acceptance:** All criteria in the acceptance table above are met; no regression in
evidence audit; no design-readiness claim introduced

---

## Notes on Control File Consistency

The project board (`00_PROJECT_BOARD.md`) and handoff (`05_HANDOFF.md`) both still show
Stage 4C as blocked and the active task as `P_CONTROLLED_LOCAL_001 Planning`. Those files
reflect the state before P_LOCAL_002 was executed. They should be updated to record:

- P_LOCAL_002 Phase 4 pilot complete — CONDITIONAL GO
- Stage 4C AUTHORIZED (conditional — see `98_PHASE_4_VERDICT.md`)
- Active task updated to reflect Stage 4C M1 planning

That update is a separate control-layer task and should be done by the project owner or a
dedicated governance branch, not as part of M1 implementation.
