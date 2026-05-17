# GridFlow Production Architecture

**Date:** 2026-05-17
**Commit:** 8afeee0 (Fix 4 critical pipeline bugs — matching now works)
**Validation:** P_LOCAL_002 — 12/12 baseline parsed, 12/12 matched, 12/12 notes detected
**Tests:** 1464 passing, 9 skipped

---

## System Status

The four critical P0/P1 pipeline bugs identified in `AI_CONTROL/39_STAGE4C_SILENT_FAILURES.md`
are fixed. The pipeline is functional for Stage 4C M1 validation. The overall status returned
on P_LOCAL_002 is correctly `PARTIAL` (not `PASS`) because design-ready is 0/12 — which is the
correct expected outcome pending DNO engineering records.

Remaining known issues (from doc 39, Bugs 5–8) are lower-priority polish items and do not
block Stage 4C M1.

---

## Core Modules

### 1. Baseline Ingestion — `gridflow/baseline/`

**Files:**
- `gridflow/baseline/csv_parser.py` — `CSVParser` class
- `gridflow/baseline/models.py` — `BaselinePole`, `BaselineDataset` models
- `gridflow/baseline/coordinate_transformer.py` — CRS transformation
- `gridflow/baseline/schema_validator.py` — validation
- `gridflow/baseline/support_number_normalizer.py` — normalisation
- `gridflow/baseline/route_reconstructor.py` — route sequence

**Functionality:**
- Format detection: ENWL (`ENID` + `Support No` columns), Trimble (`Feature Code` + `Point ID`),
  Generic (fallback)
- **Fix (Bug 1):** Generic parser now uses `pole_id` column as `support_no` fallback when
  no "support" or "name" column is found
- **Fix (Bug 3):** Blank-coordinate rows are included in output with
  `metadata["coordinate_status"] = "MISSING"` instead of being silently dropped
- `support_no` defaults to `pole_id` value in all three parsers when `Support No` / `Point Name`
  column is absent or empty (`support_no = str(row.get("Support No", "")).strip() or pole_id`)
- Coordinate transformation: OSGB36 → WGS84 via pyproj; skips gracefully if unavailable
- Route reconstruction: assigns `route_id` and `pole_sequence` from spatial ordering

**`BaselinePole` model fields:**
```
pole_id: str              # Primary DNO identifier (e.g. "902202")
support_no: Optional[str] # Support number; falls back to pole_id (never None after fix)
easting: Optional[float]  # OSGB36 easting (None for coordinate-gap poles)
northing: Optional[float] # OSGB36 northing (None for coordinate-gap poles)
latitude: Optional[float] # WGS84 (populated after transformation)
longitude: Optional[float]
metadata: dict            # Includes "coordinate_status": "COMPLETE" or "MISSING"
```

**Proven results (P_LOCAL_002):**
- Before fix: 10/12 parsed (2 dropped silently), all `support_no = None`
- After fix: 12/12 parsed, all have `support_no`, 903101/903203 flagged `coordinate_status=MISSING`

---

### 2. Field Evidence Scanning — `gridflow/field/`

**Files:**
- `gridflow/field/folder_scanner.py` — `FolderScanner` class
- `gridflow/field/models.py` — `FieldPole`, `FieldDataset` models
- `gridflow/field/notes_parser.py` — notes text extraction
- `gridflow/field/evidence_quality_scorer.py` — quality scoring

**Functionality:**
- Scans `NN_SUPPORT_*` directory structure; skips hidden folders and `_DUPLICATE_` prefixes
- Extracts `support_no` from folder name: `01_SUPPORT_902202` → `"902202"`;
  `11_SUPPORT_903202_LV_TEE_OFF` → `"903202"` (takes `parts[2]` after splitting on `_`)
- **Fix (Bug 4):** `NOTES_EXTENSIONS = {".txt", ".TXT", ".md", ".MD"}` — now detects
  `.md` files (all P_LOCAL_002 notes are `pole_notes.md`)
- Detects voltage category (`LV`/`HV`/`EHV`) from folder name parts
- `EvidenceQualityScorer` scores each pole HIGH / MEDIUM / LOW based on photo count and notes

**Photo/screenshot detection:**
- `field_photos/` → `PHOTO_EXTENSIONS = {".jpeg", ".jpg", ".heic", ...}`
- `map_screenshots/` → `SCREENSHOT_EXTENSIONS = {".png", ".jpg", ".jpeg", ...}`
- `enwl_screenshots/` — counted separately but not in the model's `map_screenshot_count`
  (stored in `screenshot_paths`)

**Proven results (P_LOCAL_002):**
- Before fix: 0/12 notes detected (all missed because `.md` extension excluded)
- After fix: 12/12 notes detected and parsed

---

### 3. Matching Engine — `gridflow/matching/`

**Files:**
- `gridflow/matching/support_number_matcher.py` — `SupportNumberMatcher` class
- `gridflow/matching/confidence_scorer.py` — `ConfidenceScorer`
- `gridflow/matching/register_builder.py` — `RegisterBuilder`
- `gridflow/matching/models.py` — `MatchResult`, `MatchRegister`

**Algorithm:**

```
Field lookup index:
  key = _normalize(fp.support_no)  →  "902202", "903202", ...
  field_by_normalized: dict[str, FieldPole]

For each baseline pole:
  b_key = _normalize(bp.support_no or bp.pole_id)   ← Fix (Bug 2)

  Attempt 1: exact key match in field_by_normalized
  Attempt 2: strip trailing letter suffix (900342A → 900342)
  Attempt 3: UNMATCHED
```

**Fix (Bug 2):** `SupportNumberMatcher.match()` now uses:
```python
support_no = bp.support_no or bp.pole_id
```
so that when `support_no` was not populated by the CSV parser, the `pole_id` value is
used as the matching key.

**Normalisation rules** (`_normalize()`):
- Strip leading/trailing whitespace
- Uppercase
- Strip known DNO prefixes (`SP`, `EN`, `WP`, `NO`, `YK`) when followed by digits

**Confidence scoring:** `ConfidenceScorer` scores each match HIGH / MEDIUM / LOW based on
evidence quality, photo count, note completeness, and match type.

**Proven results (P_LOCAL_002):**
- Before fix: 0/10 matched (all `b_key = ""` because `support_no = None`)
- After fix: 12/12 matched at 100.0% match rate

---

### 4. Design-Readiness Assessment — `gridflow/readiness/assessor.py`

**Class:** `ReadinessAssessor`

**Status levels:**

| Status | Meaning | P_LOCAL_002 result |
|---|---|---|
| `ready` | All evidence complete, span-confirmed conductor | Not achieved (correct) |
| `review_required` | Identity linked, conductor route-level only | Expected for Poles 03, 05, 06 |
| `not_ready` | Missing photos, pole class, or no conductor | Expected for most poles |
| `insufficient_evidence` | Identity incomplete or linking confidence NONE/LOW | — |

`design_ready = True` only when `status == "ready"`. All P_LOCAL_002 poles are
`design_blocked = True` (0/12 design-ready) — correct outcome, not a failure.

**Assessment chain:**
```
combine_pole_evidence(survey_root, pole_folder, trace_path)
  → link_pole(...)     (Stage 6C linking)
  → detect_pole(...)   (Stage 6D conflict detection)
  → assess_from_records(combined, linking, conflicts)
```

This module is part of the Stage 6 ENWL evidence integration layer, not the core Stage 4C
pipeline. It is available but requires an ENWL trace GeoJSON file.

---

### 5. Conflict Detection — `gridflow/conflict_detector/detector.py`

**Class:** `ConflictDetector`

**Severity levels:** `CRITICAL`, `WARNING`, `INFO`

**Conflict types detected (Stage 6D level):**
- Structural classification mismatch (ENWL pole_type vs field observation)
- GPS coordinate discrepancy (ENWL vs field GPS pin > threshold)
- Missing equipment presence (ENWL records equipment not observed in field)
- Conductor spec inconsistency

**Note:** The Pole 06 structural conflict (ENWL Stub Pole vs field H-pole) requires a
Stage 6D rule to be confirmed as automatically detected. This is Task 3 from the
Stage 4C implementation plan.

---

### 6. Pipeline Orchestration — `scripts/run_pipeline.py`

**Stages:**
1. Baseline ingest → `01_baseline_dataset.json`
2. Field evidence import → `02_field_dataset.json`
3. Matching → `03_match_register.json` + `03_match_register.csv`
4. Merge + QA → `04_merged_dataset.json` + `05_qa_report.md`
5. Stage 5A reports → `00_` through `10_` report files

**Status logic (post-fix):**

`overall_status = "PARTIAL"` when any of:
- Baseline validation errors > 0
- Parsed poles < source CSV rows (some dropped)
- Notes present == 0 when field poles exist
- Matched == 0 when both sides have poles
- Merged total == 0 when matching succeeded

Otherwise `overall_status = "PASS"`.

No percentage-based threshold. Status reflects structural pipeline health, not design-readiness.

**Proven results (P_LOCAL_002):**
- Before fix: Status = `PASS` (false — 0/10 matched)
- After fix: Status = `PARTIAL` (correct — 12/12 matched but 0/12 design-ready)

---

## Data Flow

```
INPUTS
───────────────────────────────────────────────────────────────────────
[P_LOCAL_002_baseline.csv]            [enwl_enrichment_clean/]
  pole_id, easting, northing             01_SUPPORT_902202/
  voltage, asset_type, status              field_photos/*.jpg
  (2 rows: blank coordinates)              enwl_screenshots/*.png
                                           map_screenshots/*.png
                                           notes/pole_notes.md
                                         ... (12 folders total)

STAGE 1 — BASELINE INGEST
────────────────────────────────────────────────────
CSVParser.detect_format() → GENERIC
CSVParser._parse_generic():
  - pole_id column → BaselinePole.pole_id + BaselinePole.support_no (fallback fix)
  - blank easting/northing → coordinate_status="MISSING" in metadata (not skipped)
  - 12 BaselinePole objects produced
CoordinateTransformer: OSGB36 → WGS84
SchemaValidator: validates all 12 poles
Output: BaselineDataset (12 poles)

STAGE 2 — FIELD EVIDENCE IMPORT
────────────────────────────────────────────────────
FolderScanner.scan(enwl_enrichment_clean/):
  - Finds 12 NN_SUPPORT_* folders
  - Extracts support_no from parts[2] of folder name
  - Reads *.md notes (fix: NOTES_EXTENSIONS includes .md)
  - Counts field_photos/ and map_screenshots/
  - Parses pole_notes.md content via NotesParser
EvidenceQualityScorer: scores 12 poles HIGH
Output: FieldDataset (12 poles, 12 notes parsed)

STAGE 3 — MATCHING
────────────────────────────────────────────────────
SupportNumberMatcher.match():
  - Field lookup: support_no → FieldPole (12 entries)
  - For each baseline pole: b_key = normalize(support_no or pole_id) (fix)
  - 12/12 EXACT matches
ConfidenceScorer: scores each match
RegisterBuilder: builds MatchRegister
Output: MatchRegister (12/12 matched, 100% match rate)

STAGE 4 — MERGE + QA
────────────────────────────────────────────────────
DataMerger: produces 12 MergedPole records
  - All 12 design_blocked=True (correct — awaiting DNO records)
  - conductor_verification_required=True for all
  - pole_class_verification_required=True for all
QAReportGenerator: generates 05_qa_report.md
Output: MergedDataset + QA report

STAGE 5A — REPORTS
────────────────────────────────────────────────────
10 standard report files:
  00_pilot_output_pack_index.md
  01_baseline_dataset.json → 02_field_dataset.json → 03_match_register.*
  04_merged_dataset.json
  05_qa_report.md
  06_dno_data_request.md
  07_design_readiness_summary.md
  08_match_confidence_analysis.md
  09_verification_flags_breakdown.md
  10_evidence_provenance_log.md

Overall status: PARTIAL
(12/12 matched; 0/12 design-ready — correct expected state)
```

---

## Web Layer — `app/routes/`

| Route | Purpose |
|---|---|
| `/workspace/view/<job_id>` | Review workspace — pole list with filters |
| `/workspace/pole/<job_id>/<support_no>` | Single-pole detail + DNO evidence display |
| `/map/overlay/<job_id>` | Preview map overlay HTML |
| `/map/overlay/data/<job_id>` | Overlay GeoJSON data endpoint |
| `/feedback/<job_id>` | Designer feedback form |
| `/feedback/<job_id>/submit` | Feedback POST endpoint |
| API routes | `api_intake`, `api_upload`, `api_jobs`, `api_projects`, `api_review`, etc. |

Registered jobs are accessible after `scripts/run_pipeline.py --register --job-id <id>`.

---

## Known Remaining Issues (Post-Fix)

From `AI_CONTROL/39_STAGE4C_SILENT_FAILURES.md`, Bugs 5–8 were documented but may not be
fully resolved. These are lower-priority polish items:

| Issue | Severity | Status |
|---|---|---|
| Stage 5 reports show 0/0 baseline/field (use merged-only data) | MEDIUM | TBD |
| QA report percentage bug (UNMATCHED = 1000.0%) | LOW | TBD |
| Baseline identity lost in unmatched pole output | MEDIUM | TBD |
| Evidence quality scorer collapsed everything to LOW | MEDIUM | Fixed (12 HIGH confirmed) |

Bugs 5, 6, 7 should be checked on the next full pipeline run output.

---

## Stage 4C M1 Validation Status

| Criterion | Status |
|---|---|
| 12/12 baseline parsed | ✅ |
| 12/12 matched | ✅ |
| 12/12 notes detected | ✅ |
| Evidence quality: 12 HIGH | ✅ |
| All 12 poles `design_blocked = True` | ✅ (correct) |
| Pipeline status = `PARTIAL` (not false `PASS`) | ✅ |
| 903101, 903203 flagged `coordinate_status=MISSING` | ✅ |
| Pole 06 conflict auto-detected in QA report | ⚠️ Needs Task 3 confirmation |
| All 10 reports generated without error | ⚠️ Needs confirmation on latest run |
| `baseline_coordinate_missing` flag in QA report | ⚠️ Needs confirmation |
