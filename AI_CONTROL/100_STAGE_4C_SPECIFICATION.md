# Stage 4C Specification — Production Baseline Pipeline

**Date:** 2026-05-17
**Status:** AUTHORIZED — validation in progress on P_LOCAL_002
**Gate:** Phase 4 same-site baseline pilot — CONDITIONAL GO (see `98_PHASE_4_VERDICT.md`)

---

## Context

Stage 4C is the production-hardening and multi-job validation phase of the GridFlow
baseline pipeline. The core pipeline components are already operational — built and proven
during Stage 4 prototype work and validated on P_LOCAL_001:

```
Baseline → Field → Matching → Merge → QA
```

P_LOCAL_001 (10 poles, NIE/SPEN reference set) proved:
- 10/10 structural matches
- Correct `design_blocked` outcome (no false positives)
- QA report generation working end-to-end
- Workspace and preview overlay functional

P_LOCAL_002 (12 poles, ENWL same-site baseline) is proving the pipeline on a new job
with a full ENWL baseline, enriched evidence folders, and two additional LV poles
beyond the initial 10. Phase 4 validation returned 100% structural match with 5 fixable
issues identified.

Stage 4C specification defines what "production-ready" means for this pipeline, what
P_LOCAL_002 must prove, and what issues must be resolved before design-readiness
clearance is granted on any P_LOCAL_002 pole.

---

## Stage 4C Goal

Validate and harden the GridFlow survey-to-design workflow against P_LOCAL_002 such that:

1. The baseline ingestion, field import, matching, merge, and QA pipeline runs
   automatically on a fresh ENWL job without manual intervention.
2. The pipeline correctly detects known structural issues (Pole 06 conflict, Poles 10/11/12
   documentation gaps) without being told where to look.
3. The pipeline output is accurate enough that a practising UK OHL designer can review
   results and understand what is proven vs what requires DNO verification.
4. The output does not overclaim: poles without confirmed conductor specification and
   pole class/strength rating remain design-blocked.

---

## Architecture — Existing Components

All core components exist. Stage 4C specifies their production validation requirements.

### 1. Baseline Ingestion — `gridflow/baseline/`

**What it does:**
- Parses ENWL/DNO asset CSVs (`csv_parser.py`)
- Validates against schema (`schema_validator.py`)
- Transforms coordinates BNG / ITM / OSGB → WGS84 (`coordinate_transformer.py`)
- Normalises support numbers to a canonical form (`support_number_normalizer.py`)
- Reconstructs route sequence from coordinates (`route_reconstructor.py`)

**Stage 4C validation requirement:**
- Ingest P_LOCAL_002 ENWL baseline CSV cleanly with zero parse errors.
- All 12 support numbers normalised correctly including the compound form `900342A`.
- Coordinates populated for at least 10/12 poles (Poles 10 and 12 have known gaps — see
  issues 3 and 4 in `98_PHASE_4_VERDICT.md`).
- Route sequence reconstructed without manual ordering.

**Known production gap:** Poles 10 (903101) and 12 (903203) have missing baseline
coordinates. These must be populated from ENWL popup evidence before full production
validation can complete.

---

### 2. Field Evidence Ingestion — `gridflow/field/`

**What it does:**
- Scans organised pole evidence folders (`folder_scanner.py`)
- Indexes field photos, ENWL screenshots, map screenshots, and notes
- Parses structured notes into extractable fields (`notes_parser.py`)
- Scores evidence quality per pole (`evidence_quality_scorer.py`)
- Detects special flags: `NO_POLE_POPUP`, missing photo categories, etc.
- Links each folder to a baseline pole by support number

**Stage 4C validation requirement:**
- Scan all 12 P_LOCAL_002 evidence folders correctly.
- Detect that Pole 11 (903202) notes file is empty (0 bytes).
- Detect that Pole 12 (903203) notes contain "Support UNKNOWN" — flag as incomplete.
- Correctly score Poles 01–10 as HIGH or MEDIUM evidence quality.
- Score Poles 11 and 12 as LOW evidence quality until notes are reconciled.

**Known production gap:** `notes_parser.py` currently extracts basic fields (support_no,
voltage, condition, access). It does not yet extract ENWL FID or SPN from notes text.
Stage 6B–6C bridge this gap using the evidence combiner and linker. For Stage 4C baseline
validation purposes, the absence of FID extraction is expected and does not block matching.

---

### 3. Matching Engine — `gridflow/matching/`

**What it does:**
- Matches baseline records to field evidence folders by support number
  (`support_number_matcher.py`)
- Scores match confidence (HIGH / MEDIUM / LOW / UNMATCHED) (`confidence_scorer.py`)
- Detects per-pole conflicts between baseline and field (`conflict_detector.py` within merge)
- Builds a match register with one entry per baseline pole (`register_builder.py`)

**Stage 4C validation requirement:**
- Match all 12 P_LOCAL_002 poles at 100% structural match rate (already confirmed in
  Phase 4 structural validation).
- Achieve HIGH confidence for poles where support number is unambiguous and photos + notes
  are present.
- Flag Poles 11 and 12 as MEDIUM or LOW confidence pending notes reconciliation.
- The compound support number 900342A must match correctly without manual handling.

---

### 4. Conflict Detection — `gridflow/merge/conflict_detector.py` + `gridflow/conflict_detector/`

**What it does:**
- Compares baseline attributes against field-observed attributes
- Flags structural mismatches (pole type, pole class, voltage)
- Flags missing coordinates in baseline
- Flags incomplete or placeholder documentation in field evidence

**Stage 4C validation requirement (critical):**

The pipeline must detect these specific P_LOCAL_002 issues automatically:

| Issue | Pole | Expected Flag |
|---|---|---|
| ENWL "Stub Pole" vs field H-pole arrangement | 06 (900345) | Structural classification conflict |
| Baseline coordinates missing | 10 (903101) | Coordinate gap |
| Notes file empty | 11 (903202) | Documentation incomplete |
| Notes placeholder / "Support UNKNOWN" | 12 (903203) | Documentation incomplete |
| Baseline coordinates missing | 12 (903203) | Coordinate gap |

If the conflict detector does not surface all five issues automatically in the QA report,
Stage 4C validation is incomplete.

**Pole 06 conflict specifically:** ENWL records `pole_class = Stub Pole`. Field photos
show a double-pole / H-pole arrangement with a 100 kVA support-mounted transformer. This
is a structural classification discrepancy between the DNO asset register and ground-truth
field observation. It must appear as a flagged conflict in the QA output, not be silently
passed or suppressed.

---

### 5. Design-Readiness Validation — `gridflow/merge/` + `gridflow/readiness/`

**What it does:**
- Sets `design_blocked = True` by default; clears only when all verification requirements
  are met
- Sets verification flags: `conductor_verification_required`, `pole_class_verification_required`,
  `voltage_verification_required`, `condition_verification_required`,
  `identity_verification_required`, `equipment_conflict_flag`
- Generates `designer_actions` list: specific, actionable items per pole

**Stage 4C validation requirement:**
- All 12 P_LOCAL_002 poles must remain `design_blocked = True` at Stage 4C completion.
  No pole has confirmed conductor specification per span or pole class/strength rating —
  this is the correct expected outcome.
- Poles 11 and 12 must carry `identity_verification_required = True` and
  `documentation_incomplete` flag until their notes are reconciled.
- `designer_actions` for each pole must be specific and actionable, not generic.

**Design-readiness caution:** The correct outcome for P_LOCAL_002 after full Stage 4C
validation is 0/12 `design_ready = True`. This is not a failure. It reflects that field
survey evidence and ENWL pole/equipment evidence are present, but DNO engineering records
(conductor schedule, pole class/strength ratings) have not yet been confirmed. The pipeline
is correctly identifying what is missing before design can proceed.

---

### 6. Reporting and Output — `gridflow/reports/` + `scripts/run_pipeline.py`

**What it produces:**
- `01_baseline_dataset.json` — canonical parsed baseline
- `02_field_dataset.json` — parsed field evidence with quality scores
- `03_match_register.csv/.json` — pole-by-pole match outcomes
- `04_merged_dataset.json` — unified record per pole
- `05_qa_report.md` — QA findings and conflicts
- `06_dno_data_request.md` — structured request for missing DNO records
- `07_design_readiness_summary.md` — per-pole readiness status
- `08_match_confidence_analysis.md` — matching confidence breakdown
- `09_verification_flags_breakdown.md` — flags per pole
- `10_evidence_provenance_log.md` — evidence sources per pole

**Stage 4C validation requirement:**
- All 10 reports must generate for P_LOCAL_002 without error.
- Report 05 (QA report) must surface all 5 known P_LOCAL_002 issues.
- Report 06 (DNO data request) must list conductor specification and pole class/strength
  rating as required items for all 12 poles.
- Report 07 (design readiness) must show 0/12 design-ready with specific blockers per pole.

**CLI run command for P_LOCAL_002:**

```bash
python scripts/run_pipeline.py \
  --baseline <P_LOCAL_002_baseline.csv> \
  --field real_pilot_data/P_LOCAL_002/enwl_enrichment_clean \
  --output /tmp/plocal002_stage4c \
  --job-id P_LOCAL_002 \
  --register \
  --overwrite-registration
```

---

## Success Criteria

Stage 4C validation on P_LOCAL_002 is complete when all of the following are true:

| Criterion | Target |
|---|---|
| Structural match rate | 12 / 12 = 100% ✅ (already confirmed) |
| Baseline coordinate coverage | 12 / 12 after Pole 10/12 fixes |
| Content quality — complete documentation | 12 / 12 after Pole 11/12 fixes |
| Pole 06 conflict detected automatically | YES — appears in QA report |
| Poles 10, 11, 12 issues flagged automatically | YES — all 5 issues in QA report |
| All 12 poles remain `design_blocked = True` | YES — correct expected outcome |
| All 10 pipeline reports generated without error | YES |
| Report 06 actionable for a DNO data request | YES — confirmed by designer review |

---

## Identified Issues — Resolution Required

All 5 issues from the Phase 4 verdict must be resolved before Stage 4C is declared complete.
None block the pipeline from running; all block design-readiness clearance.

| # | Pole | Issue | Resolution Owner | Blocking |
|---|---|---|---|---|
| 1 | 11 / 903202 | Notes file empty (0 bytes) | Evidence reconciliation | Design readiness for Pole 11 |
| 2 | 12 / 903203 | Notes placeholder — "Support UNKNOWN" | Evidence reconciliation | Design readiness for Pole 12 |
| 3 | 10 / 903101 | Baseline coordinates missing | Baseline update from ENWL evidence | Full route geometry for Pole 10 |
| 4 | 12 / 903203 | Baseline coordinates missing | Baseline update after notes fix | Full route geometry for Pole 12 |
| 5 | 06 / 900345 | ENWL "Stub Pole" vs field H-pole | DNO investigation + conflict review | Pole 06 conflict resolution |

Issues 1–4 are fixable from existing evidence on disk. Issue 5 requires DNO engagement or
a field revisit to confirm the actual pole configuration.

---

## Risk Assessment

| Risk | Impact | Mitigation |
|---|---|---|
| DNO baseline format variations | Ingest failures on non-ENWL jobs | Extend `csv_parser.py` schema coverage; add SPEN schema test cases |
| Field evidence organisation variations | Folder scanning misses evidence | Validate against multiple job structures; add scanner robustness tests |
| Coordinate system conversion errors | Poles placed in wrong location | CRS detection and transformation already implemented; add ITM/TM65 test cases |
| Pole 06 conflict is a systemic gap in ENWL records | More conflicts undetected | Requires field-level structural checking; flag as known risk in QA output |
| Notes files empty or placeholder | Pipeline scores LOW quality silently | Explicit empty/placeholder detection already targeted in Stage 4C criteria above |

---

## Dependencies

| Dependency | Status |
|---|---|
| P_LOCAL_002 issue fixes (5 items) | In progress |
| P_LOCAL_001 reference validation | COMPLETE |
| Designer review on P_LOCAL_001 output | In progress (see `AI_CONTROL/02_CURRENT_TASK.md`) |
| ENWL baseline CSV format confirmed | CONFIRMED on P_LOCAL_001 + P_LOCAL_002 |
| Additional validation jobs (P_LOCAL_003+) | Planned — not yet started |

---

## Timeline

The Stage 4C backend pipeline is already built and operational. The Stage 4C validation
timeline covers hardening and issue resolution, not greenfield implementation.

| Task | Estimate | Status |
|---|---|---|
| Structural validation on P_LOCAL_002 | Complete | ✅ DONE (Phase 4 verdict) |
| Fix Poles 11/12 documentation gaps | 1–2 days | In progress |
| Fix Poles 10/12 coordinate gaps | 1 day | In progress |
| Investigate Pole 06 structural conflict | 1–2 weeks | Pending |
| Re-run content quality validation | 1 day | After fixes |
| Designer review on P_LOCAL_002 output | 1–2 weeks | After fixes |
| Stage 4C declared complete | — | After all criteria met |

---

## What Stage 4C Does Not Cover

Stage 4C does not include:

- Mobile field capture tools (tablet/phone structured entry)
- ENWL evidence integration beyond the existing Stage 6 pilot work
- PoleCAD export format
- Multi-user deployment infrastructure
- Automated conductor-to-span assignment
- Photo content parsing or OCR

These are separate stages. Stage 4C proves the core pipeline on real jobs. Subsequent
phases extend it.

---

## Connection to Stage 6 Evidence Work

Stage 6A–6E ENWL evidence integration (see `AI_CONTROL/121` onwards) builds on the Stage
4C pipeline. The Stage 4C `MergedPole` output feeds the Stage 6 evidence combiner, linker,
conflict detector, and readiness assessor. Stage 4C does not need to be repeated when Stage
6 modules are added — they are additive layers on top of the same merged dataset.

The Stage 4C baseline pipeline and the Stage 6 ENWL evidence pipeline are designed to be
run in sequence:

```
Stage 4C pipeline output (04_merged_dataset.json)
  → Stage 6C linker (formal pole-to-ENWL linking)
  → Stage 6D conflict detector (field vs ENWL conflicts)
  → Stage 6E readiness assessor (updated design readiness)
```
