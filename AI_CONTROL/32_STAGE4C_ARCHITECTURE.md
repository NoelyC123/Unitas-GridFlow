# Stage 4C Architecture

**Date:** 2026-05-17
**Based on:** Actual codebase state + P_LOCAL_002 validation
**Reference:** `AI_CONTROL/30_STAGE4C_IMPLEMENTATION_PLAN.md`,
`AI_CONTROL/100_STAGE_4C_SPECIFICATION.md`

---

## Data Flow

```
INPUTS
──────────────────────────────────────────────────────────────────────────
[Baseline Data]                        [Field Evidence]
    │                                        │
    ▼                                        ▼
[P_LOCAL_002_baseline.csv]         [enwl_enrichment_clean/]
    │                                        │
    │  pole_id, easting, northing            │  01_SUPPORT_902202/
    │  voltage, asset_type, status           │    field_photos/
    │                                        │    enwl_screenshots/
    │                                        │    map_screenshots/
    │                                        │    notes/pole_notes.md
    │                                        │  ... (12 folders)
    │                                        │
    ▼                                        ▼

STAGE 1 — BASELINE INGEST                   STAGE 2 — FIELD EVIDENCE IMPORT
──────────────────────────────              ──────────────────────────────
gridflow/baseline/                          gridflow/field/
  csv_parser.py                               folder_scanner.py
  schema_validator.py                         notes_parser.py
  coordinate_transformer.py                   evidence_quality_scorer.py
  support_number_normalizer.py                dataset_validator.py
  route_reconstructor.py
    │                                              │
    ▼                                              ▼
[BaselineDataset]                          [FieldDataset]
  - 12 poles parsed                          - 12 folders scanned
  - support numbers normalised               - photos indexed
  - coordinates transformed                  - notes parsed
  - 2 coordinate gaps flagged               - quality scored per pole
  - route sequence reconstructed

                     │                      │
                     ▼                      ▼

                  STAGE 3 — MATCHING
                  ──────────────────────────────
                  gridflow/matching/
                    support_number_matcher.py
                    confidence_scorer.py
                    register_builder.py
                    │
                    ▼
                  [MatchRegister]
                    - 12/12 structural matches
                    - confidence: HIGH / MEDIUM / LOW / UNMATCHED
                    - 03_match_register.json + .csv

                     │
                     ▼

               STAGE 4 — MERGE + QA
               ──────────────────────────────────────────
               gridflow/merge/
                 data_merger.py              → MergedDataset (04_merged_dataset.json)
                 verification_flag_generator.py → per-pole flags
                 conflict_detector.py        → baseline-vs-field conflicts
                 qa_report_generator.py      → 05_qa_report.md

               gridflow/readiness/
                 assessor.py                → readiness_level per pole

                     │
                     ▼

OUTPUTS — 10 STANDARD REPORTS (scripts/run_pipeline.py)
────────────────────────────────────────────────────────
  00_pilot_output_pack_index.md
  01_baseline_dataset.json
  02_field_dataset.json
  03_match_register.csv / .json
  04_merged_dataset.json
  05_qa_report.md
  06_dno_data_request.md
  07_design_readiness_summary.md
  08_match_confidence_analysis.md
  09_verification_flags_breakdown.md
  10_evidence_provenance_log.md

PHASE 4 GATE — SEPARATE STRUCTURAL VALIDATOR
─────────────────────────────────────────────
scripts/validate_phase4_matching.py
  Purpose: lightweight structural gate (baseline row → field folder)
  Output:  validation_runs/P_LOCAL_002_phase4_validation.json
  Checks:  folder exists, photo counts, note presence
  Does NOT: run merge, generate reports, assess readiness
  Use for: pre-pipeline structural pass/fail gate
```

---

## Component Breakdown

### 1. Baseline Ingestion — `gridflow/baseline/`

**Status: WORKING ✅**

| Module | Role |
|---|---|
| `csv_parser.py` | Read baseline CSV; accept blank coordinate rows without error |
| `schema_validator.py` | Validate required columns (`pole_id`, `voltage`) |
| `coordinate_transformer.py` | BNG / ITM / OSGB → WGS84 transformation |
| `support_number_normalizer.py` | Normalise compound IDs (e.g., `900342A`) |
| `route_reconstructor.py` | Reconstruct route sequence from coordinates |

**Inputs:** `P_LOCAL_002_baseline.csv`
(12 rows; 10 with BNG coordinates; 903101 and 903203 have blank easting/northing)

**Outputs:** `BaselineDataset` — parsed poles with normalised identifiers

**P_LOCAL_002 state:** 10/12 rows have coordinates. The two blank rows are accepted
without error; they do not block the pipeline run.

---

### 2. Field Evidence Scanner — `gridflow/field/`

**Status: WORKING ✅**

| Module | Role |
|---|---|
| `folder_scanner.py` | Scan `enwl_enrichment_clean/` and build a `FieldDataset` |
| `notes_parser.py` | Extract structured fields from `pole_notes.md` text |
| `evidence_quality_scorer.py` | Score each pole HIGH / MEDIUM / LOW |
| `dataset_validator.py` | Flag missing photos, screenshots, or notes |

**Inputs:** `real_pilot_data/P_LOCAL_002/enwl_enrichment_clean/` (12 folders)

**Outputs:** `FieldDataset` — one `FieldPole` per folder with photo counts,
parsed notes, and quality score

**P_LOCAL_002 state:** 12/12 folders complete; 12/12 notes present;
all evidence quality scored.

---

### 3. Matching Engine — `gridflow/matching/`

**Status: WORKING ✅**

| Module | Role |
|---|---|
| `support_number_matcher.py` | Match baseline `pole_id` to field folder support number |
| `confidence_scorer.py` | Score match: HIGH / MEDIUM / LOW / UNMATCHED |
| `register_builder.py` | Build `MatchRegister` with one entry per baseline pole |

**Inputs:** `BaselineDataset` + `FieldDataset`

**Outputs:** `MatchRegister` — 12/12 matches for P_LOCAL_002; confidence per pole

**Note:** `scripts/validate_phase4_matching.py` is a separate, lighter-weight structural
validator that runs before the full pipeline. It checks folder existence and evidence
counts only, without producing merged records or reports. Use it as a pre-pipeline gate.

---

### 4. Conflict Detection — `gridflow/merge/conflict_detector.py` + `gridflow/conflict_detector/detector.py`

**Status: PARTIALLY AUTOMATED ⚠️**

Two layers exist:

- `gridflow/merge/conflict_detector.py` — per-pole baseline-vs-field comparison built
  into the merge step; flags voltage mismatches, equipment conflicts, identity issues
- `gridflow/conflict_detector/detector.py` — Stage 6D-level detector comparing ENWL
  record attributes against field note observations (pole_type, structural classification)

**P_LOCAL_002 state:** The Pole 06 structural conflict (ENWL Stub Pole vs field H-pole)
is a Stage 6D-level conflict requiring explicit rules in `conflict_detector/detector.py`.
Whether it is currently surfaced automatically in the Stage 4C QA report requires Task 3
from the implementation plan (read-only review).

**Stage 4C gap:** Coordinate-gap flag (`baseline_coordinate_missing`) may not be surfaced
by existing merge logic for blank easting/northing rows. This is Task 2 in the plan.

---

### 5. Coordinate Validation

**Status: WORKING FOR BLANKS; NO AUTO-FLAG YET ⚠️**

- `csv_parser.py` accepts blank coordinate rows (no hard error)
- `coordinate_transformer.py` transforms present coordinates correctly
- Blank rows currently pass through without a named flag in the merged output

**P_LOCAL_002 state:** 903101 and 903203 have blank easting/northing in the baseline CSV.
The coordinate review (`P_LOCAL_002_COORDINATE_COMPLETENESS_REVIEW.md`) documents the gaps.
A `baseline_coordinate_missing` verification flag needs to be confirmed or added.

---

### 6. Merge and Verification Flags — `gridflow/merge/`

**Status: WORKING ✅**

| Module | Role |
|---|---|
| `data_merger.py` | Combine baseline + field + match into `MergedPole` per pole |
| `verification_flag_generator.py` | Set per-pole flags: conductor, pole class, voltage, identity |
| `qa_report_generator.py` | Generate `05_qa_report.md` from merged dataset |

**Outputs:** `04_merged_dataset.json` with `MergedPole` per pole; `design_blocked = True`
for all 12 P_LOCAL_002 poles (correct expected outcome).

---

### 7. Design-Readiness Assessment — `gridflow/readiness/assessor.py`

**Status: IMPLEMENTED ✅** (not absent as sometimes assumed)

The readiness assessor consumes Stage 6C linking results and Stage 6D conflict reports
to produce a `readiness_level` per pole: `DESIGN_READY` / `DESIGN_READY_WITH_CAUTIONS` /
`DESIGN_BLOCKED`. It is Stage 6E logic and does not change `design_ready` without
confirmed conductor specification and pole class data.

**P_LOCAL_002 expected outcome:** All 12 poles `DESIGN_BLOCKED`. This is correct — no
pole has confirmed conductor specification per span or pole class/strength rating.

---

### 8. Report Generation — `gridflow/reports/` + `scripts/run_pipeline.py`

**Status: WORKING ✅**

All 10 standard reports are generated by `scripts/run_pipeline.py`. The pipeline
registration bridge (`gridflow/registration.py`) copies output to `uploads/jobs/<job_id>/`
for web workspace access.

---

## Current vs Target State

| Component | Current state | Stage 4C target |
|---|---|---|
| Baseline ingestion | stdlib CSV; blank coordinates accepted without error | Add `baseline_coordinate_missing` flag for blank rows |
| Evidence scanner | Folder structure + notes parsed | Confirm quality scoring handles empty/placeholder notes |
| Matching | Support number → folder; confidence scored | Validate 12/12 on P_LOCAL_002; no code change expected |
| Conflict detection | Partially automated; Stage 6D rules exist | Confirm Pole 06 structural conflict surfaces in QA report |
| Coordinate validation | Blank detection; no named flag | Add named flag; warn not error |
| Merge + flags | Per-pole verification flags | Confirm `baseline_coordinate_missing` propagates to QA |
| Design-readiness | Implemented in `gridflow/readiness/assessor.py` | Run on P_LOCAL_002; confirm 0/12 design-ready |
| Reports | All 10 generate | Confirm all 10 generate on P_LOCAL_002 without error |

---

## Implementation Priority

### Milestone 1 — Validation run (no code change)
Run `scripts/run_pipeline.py` against P_LOCAL_002. Record which of the five known issues
surface automatically. This is Task 1 from `30_STAGE4C_IMPLEMENTATION_PLAN.md`.

**Estimated effort:** Hours (run + document)

### Milestone 2 — Coordinate gap flag
If M1 shows blank coordinates do not produce a named flag in the QA report, add
`baseline_coordinate_missing` to `verification_flag_generator.py`. Add test.

**Estimated effort:** 1 day
**Files:** `gridflow/merge/verification_flag_generator.py`, tests

### Milestone 3 — Pole 06 conflict rule
If M1 shows the structural conflict at Pole 06 is not auto-detected, define or extend
a rule in `gridflow/conflict_detector/detector.py`.

**Estimated effort:** 1–2 days
**Files:** `gridflow/conflict_detector/detector.py`, tests

### Milestone 4 — Coordinate closure (Noel action)
Look up FID 16788439 (903101) and FID 16938106 (903203) in ENWL NAV. Enter coordinates
into baseline CSV. Re-run pipeline. Confirm 12/12 coordinate completeness.

**Estimated effort:** 1 hour (lookup + data entry)
**Files:** `real_pilot_data/P_LOCAL_002/csv/P_LOCAL_002_baseline.csv`

### Milestone 5 — Full M1 acceptance check
After M2–M4, re-run pipeline and confirm all acceptance criteria in the implementation
plan are met.

**Estimated effort:** Hours (run + document)

---

## What Is Explicitly Out of Scope

- Multi-format baseline ingest (SPEN, Trimble CSV) — future stage
- HTML or PDF report generation — future stage
- Photo content analysis or OCR — out of scope
- Mobile field capture tooling — Stage 4 structured capture track
- Web UI changes — separate track
- PoleCAD export — future stage
- `conductor_spec_missing` clearance from route-level evidence alone
- `design_ready = True` for any P_LOCAL_002 pole
