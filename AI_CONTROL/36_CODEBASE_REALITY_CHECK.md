# GridFlow Codebase Reality Check

**Date:** 2026-05-17
**Method:** Direct code reading — not assumed from documentation

---

## Two Distinct Pipeline Tracks

The GridFlow codebase contains two separate, largely independent pipeline tracks. Many
planning documents conflate them. They must be understood separately.

### Track 1 — Stage 1/2 QA Pipeline (Trimble GNSS → QA reports)

**Entry point:** File upload via `app/routes/api_upload.py` or `app/routes/api_intake.py`
**Core engine:** `app/qa_engine.py` (1250 lines, uses pandas throughout)
**Purpose:** Parse Trimble GNSS controller dump CSVs, classify records, run QA checks,
detect EX/PR replacement pairs, generate issues, produce design-readiness flags

**Data flow:**

```
Trimble GNSS controller dump (.csv)
  → api_intake.py / api_upload.py (upload + trigger)
  → qa_engine.py (parse, classify, validate, QA checks)
  → app/routes/ (serve results to web UI + legacy reports)
```

**This is the Stage 1/2 product** — the original pre-CAD QA gatekeeper. It handles
survey records, pole coordinates, span distances, crossing heights, and design-readiness
scores from Trimble field data.

### Track 2 — Stage 4C Baseline-Field Matching Pipeline

**Entry point:** `scripts/run_pipeline.py` or `scripts/validate_phase4_matching.py`
**Core modules:** `gridflow/baseline/`, `gridflow/field/`, `gridflow/matching/`, `gridflow/merge/`
**Purpose:** Ingest a DNO baseline CSV, scan organised field evidence folders, match
poles by support number, merge evidence, flag verification requirements, produce reports

**Data flow:**

```
Baseline CSV + Field evidence folders
  → scripts/run_pipeline.py
  → gridflow/baseline/ (ingest, normalise, transform)
  → gridflow/field/ (scan, parse notes, score quality)
  → gridflow/matching/ (support_no match, confidence score, register)
  → gridflow/merge/ (merge, flags, QA report)
  → gridflow/reports/ (10 standard report files)
  → gridflow/registration.py (copy to uploads/jobs/<job_id>/)
```

---

## What Actually Exists

### Pipeline Scripts — `scripts/`

| Script | Purpose | Status |
|---|---|---|
| `run_pipeline.py` | Full 4-stage baseline-field pipeline; 10 reports | ✅ Exists |
| `validate_phase4_matching.py` | Lightweight structural gate (baseline row → field folder) | ✅ Exists |
| `audit_plocal002_evidence.py` | Evidence folder/notes audit for P_LOCAL_002 | ✅ Exists |
| `link_survey_poles.py` | Stage 6C formal linking CLI | ✅ Exists |
| `assess_readiness.py` | Stage 6E readiness assessment CLI | ✅ Exists |
| `detect_conflicts.py` | Stage 6D conflict detection CLI | ✅ Exists |
| `combine_pole_evidence.py` | Stage 6B evidence combiner CLI | ✅ Exists |
| `export_combined_evidence_bundle.py` | Evidence export bundle | ✅ Exists |
| `survey_evidence_summary.py` | All-poles evidence summary | ✅ Exists |
| `inspect_enwl_trace.py` | Stage 6A trace GeoJSON inspector | ✅ Exists |
| `ingest_baseline.py` | Standalone baseline ingest | ✅ Exists |
| `run_matching.py` | Standalone matching | ✅ Exists |
| `run_merge.py` | Standalone merge | ✅ Exists |
| `generate_match_register.py` | Match register export | ✅ Exists |
| `create_validation_pack.py` | Validation pack generator | ✅ Exists |
| `preflight_designer_review.py` | Designer review preflight check | ✅ Exists |

---

### QA Engine — `app/qa_engine.py`

**1250 lines. Uses pandas. This is Track 1 (Trimble GNSS processing), not Track 2.**

Key functions:

| Function | Purpose |
|---|---|
| `run_qa_checks(df, rules)` | Core QA runner — applies rulepack checks to a Trimble records DataFrame |
| `validate_coordinate_consistency(records)` | Check coordinate plausibility and consistency |
| `validate_span_distances(...)` | Span length checks; suppresses EX→PR replacement pair false positives |
| `classify_height_confidence(record)` | Height measurement confidence classification |
| `classify_source_confidence(record)` | Evidence source confidence classification |
| `parse_attachments(record)` | Parse attachment/crossing records |
| `infer_display_network_fields(...)` | Infer network display fields from GNSS attributes |
| `_is_replacement_pair(prev_st, curr_st)` | Detect EX/PR replacement structure pairs |
| `_is_context_row(row, ...)` | Detect context/environmental records vs structural poles |
| `_deduplicate_issues(issues)` | Remove duplicate QA issue entries |

Feature code constants: `_CONTEXT_FEATURE_CODES` (Hedge, Tree, Wall, Fence, Gate, etc.),
`_EXPOLE_CODES`, `_ANGLE_CODES`, `_STAY_EVIDENCE_CODES` — all for Trimble GNSS record
classification per the OHL survey operational standard.

**This engine is not used by the Stage 4C baseline-field matching pipeline.**

---

### Routes — `app/routes/`

**17 route files; Flask blueprints throughout**

| Blueprint | URL prefix | Purpose |
|---|---|---|
| `api_intake_bp` | (no prefix) | Process uploaded Trimble GNSS CSV; trigger QA pipeline |
| `api_upload_bp` | (no prefix) | Handle file upload, store, trigger processing |
| `api_jobs_bp` | (no prefix) | Job list, metadata, status |
| `api_projects_bp` | (no prefix) | Project management API |
| `api_review_bp` | (no prefix) | Review state and filter API |
| `api_rulepacks_bp` | (no prefix) | DNO rulepack listing |
| `api_field_capture_bp` | (no prefix) | Structured field capture API (Stage 4) |
| `workspace_bp` | `/workspace` | Review workspace UI routes |
| `map_overlay_bp` | `/map` | Preview map overlay — `/map/overlay/<job_id>`, `/map/overlay/data/<job_id>` |
| `map_preview_bp` | (no prefix) | Legacy map preview |
| `feedback_bp` | `/feedback` | Designer feedback form — `/feedback/<job_id>` (GET + POST) |
| `d2d_export_bp` | (no prefix) | Design-to-Design chain export |
| `pdf_reports_bp` | (no prefix) | PDF QA report generation |
| `review_page_bp` | (no prefix) | Review page HTML |
| `projects_page_bp` | (no prefix) | Projects list HTML |
| `jobs_page_bp` | (no prefix) | Jobs list HTML |

---

### Readiness Assessment — `gridflow/readiness/assessor.py`

**This IS fully implemented — 241 lines. It is not missing.**

`ReadinessAssessor` consumes output from Stage 6B (evidence combiner), Stage 6C (linker),
and Stage 6D (conflict detector) to produce a `ReadinessResult` per pole.

**Four status levels:**

| Status | Meaning |
|---|---|
| `ready` | Identity linked, no critical conflicts, conductor span-confirmed |
| `review_required` | Identity linked, no critical conflicts, conductor route-level only |
| `not_ready` | Critical requirements not met (missing photos, conductor, pole class) |
| `insufficient_evidence` | Identity incomplete or linking confidence NONE/LOW |

**`design_ready = True` only when status == `"ready"`** — i.e., only when conductor
evidence is span-confirmed. For all current P_LOCAL_002 poles, `status = "not_ready"`
or `status = "review_required"` is expected; `design_ready = False` throughout.

**Actual checks performed:**
- Notes file exists
- Field photo count ≥ 3
- Identity fields present: support_no, pole_fid, spn
- Linking confidence not NONE or LOW; manual_confirmation_required == False
- No CRITICAL conflicts from Stage 6D
- Route conductor evidence present
- Span-confirmed conductor (required for `ready` status)
- Pole class confirmed

---

### Baseline Pipeline — `gridflow/baseline/`

Uses **stdlib csv** (not pandas). Handles BNG, ITM, and TM65 coordinate systems.

| Module | Role |
|---|---|
| `csv_parser.py` | Parse baseline CSV; accept blank coordinate rows without hard error |
| `schema_validator.py` | Validate required columns |
| `coordinate_transformer.py` | BNG / ITM / TM65 → WGS84 (pyproj) |
| `support_number_normalizer.py` | Normalise support numbers (handles compound IDs like 900342A) |
| `route_reconstructor.py` | Reconstruct route sequence from coordinates |

---

### Conflict Detection — `gridflow/conflict_detector/detector.py` + `gridflow/merge/conflict_detector.py`

**Two layers — partially automated, not fully manual:**

- `gridflow/merge/conflict_detector.py` — per-pole baseline-vs-field attribute comparison
  (voltage mismatch, equipment conflicts, identity flags). This runs as part of the merge step.
- `gridflow/conflict_detector/detector.py` — Stage 6D detector comparing ENWL record
  attributes against field note observations (structural classification, pole type, GPS gap).

---

### Data Models

| Model | Location | Key fields |
|---|---|---|
| `BaselineDataset` | `gridflow/baseline/models.py` | poles, route_id, scan_date |
| `FieldDataset` / `FieldPole` | `gridflow/field/models.py` | folder_name, support_no, photo_count, notes_content, evidence_quality |
| `MatchRegister` | `gridflow/matching/models.py` | entries, match_rate, confidence counts |
| `MergedPole` | `gridflow/merge/models.py` | support_no, design_ready, design_blocked, verification flags, designer_actions |
| `MergedDataset` | `gridflow/merge/models.py` | poles list, stats |
| `ReadinessResult` | `gridflow/readiness/assessor.py` | readiness_status, design_ready, blockers, warnings |
| `LinkingResult` | `gridflow/evidence_combiner/linker.py` | linking_method, confidence, direct_equipment_fids |
| `ConflictResult` | `gridflow/conflict_detector/detector.py` | severity, description |
| `ENWLEvidenceFeature` | `gridflow/enwl_trace/parser.py` | feature_id, relationship, fid_polestructure |

---

## Gap Analysis — Claimed vs Actual

| Claim in planning docs | Actual state |
|---|---|
| "Design-readiness assessment: NOT IMPLEMENTED" | **WRONG** — fully implemented in `gridflow/readiness/assessor.py` |
| "Conflict detection: MANUAL" | **PARTIAL** — Stage 6D module exists; Pole 06 rule needs confirming |
| "Baseline ingestion uses pandas" | **WRONG** — uses stdlib csv |
| "qa_engine.py handles Stage 4C validation" | **WRONG** — qa_engine is Stage 1/2 only (Trimble GNSS) |
| "No HTML report generation" | **CORRECT** — reports are markdown and JSON; no HTML/PDF generator in Stage 4C pipeline |
| "Coordinate validation — blank check only" | **MOSTLY CORRECT** — blank rows accepted; named `baseline_coordinate_missing` flag TBD |
| "`design_ready = True` only after Stage 6E" | **CORRECT** — assessor sets it True only when conductor is span-confirmed |

---

## Implementation Quality

**Test coverage:** Substantial test suite (~1468 tests passing as of 2026-05-17). Tests
exist for all major gridflow modules including the Stage 6A–6E additions.

**Error handling:** Conservative throughout gridflow modules — parsers never crash on
malformed input; errors logged and returned in structured results, not raised to callers.

**Inline documentation:** Docstrings present on public functions and classes in gridflow
modules. `app/qa_engine.py` has minimal inline comments relative to its size.

**Technical debt identified:**
- `app/qa_engine.py` is 1250 lines with mixed concerns; difficult to unit test individual
  rules. This is Stage 1/2 debt, not Stage 4C.
- The Stage 4C pipeline and Stage 1/2 pipeline share a web layer (`app/routes/`) but
  operate on completely different data models. A future refactor could cleanly separate them.
- `validate_phase4_matching.py` duplicates some folder-scanning logic from
  `gridflow/field/folder_scanner.py`; they could share a common file-counting utility.
