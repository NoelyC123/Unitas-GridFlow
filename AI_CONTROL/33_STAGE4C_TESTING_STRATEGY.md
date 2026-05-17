# Stage 4C Testing Strategy

**Date:** 2026-05-17
**Purpose:** Define how Stage 4C will be validated beyond P_LOCAL_002
**Reference:** `AI_CONTROL/32_STAGE4C_ARCHITECTURE.md`,
`AI_CONTROL/30_STAGE4C_IMPLEMENTATION_PLAN.md`

---

## Test Jobs

### Job 1: P_LOCAL_002 ✅ CURRENT VALIDATION BASELINE

| Property | Value |
|---|---|
| Poles | 12 |
| DNO | ENWL / Electricity North West |
| Route type | Mixed LV/HV residential and farm route (3 sub-routes) |
| Baseline completeness | 10/12 coordinates present (2 documented gaps) |
| Conflicts | 1 — Pole 06 structural mismatch (ENWL Stub Pole vs field H-pole) |
| Status | CONDITIONAL GO — Phase 4 verdict signed |
| Purpose | Establish validation baseline for all subsequent jobs |

**Known P_LOCAL_002 coverage gaps that later jobs must prove:**
- 12 poles is a small dataset; scale testing requires 30–50+
- All poles are ENWL format; SPEN/NIE/SSEN not yet tested
- Both coordinate gaps are in the same DNO dataset; multi-DNO gap handling untested
- BNG confirmed; WGS84 supplementary from notes only

---

### Job 2: P_LOCAL_003 ⏳ PLANNED — Repeatability Test

| Property | Value |
|---|---|
| Poles | TBD (target 10–15) |
| DNO | ENWL or SPEN (different from P_LOCAL_002 preferred) |
| Route type | Different configuration — rural / industrial / different voltage profile |
| Baseline completeness | Target 12/12 — choose a cleaner baseline |
| Conflicts | Unknown until captured |
| Status | Not captured yet |
| Purpose | Prove methodology repeats on a different job |

**Capture guidelines for P_LOCAL_003:**
- Use the same folder structure as P_LOCAL_002 (`enwl_enrichment_clean/`)
- Capture at least one pole of a different type not seen in P_LOCAL_002
  (e.g., a pure HV terminal without LV context, or a wood pole with stay and no equipment)
- If SPEN baseline is used, confirm `gridflow/baseline/csv_parser.py` handles the format
- Target a job with complete BNG coordinates in the baseline — no known gaps

**P_LOCAL_003 success criteria:**
- Match rate ≥ 90% structural
- Pipeline completes without code changes
- `validate_phase4_matching.py` runs without modification
- Any conflicts detected and correctly flagged
- All 10 reports generated

---

### Job 3: Real DNO Job ⏳ FUTURE — Production Validation

| Property | Value |
|---|---|
| Poles | 20–50 |
| DNO | ENWL, SPEN, SSEN, or NIE |
| Route type | Real operational survey job |
| Baseline completeness | Target ≥ 80% — accept known gaps with warning flags |
| Status | Requires DNO data access agreement |
| Purpose | Prove production-readiness at scale |

**Prerequisites:**
- DNO data access confirmed (commercial or pilot agreement)
- `run_pipeline.py` proven on at least 2 prior jobs (P_LOCAL_002 + P_LOCAL_003)
- All Stage 4C M1–M5 acceptance criteria met

**Real job success criteria:**
- 100% structural match
- All conflicts auto-detected in QA report
- Coordinate gaps produce named flags, not errors
- 0/N design-ready poles (correct — awaiting DNO engineering records)
- Runtime under 5 minutes for a 50-pole job

---

## Test Coverage Matrix

| Test Scenario | P_LOCAL_002 | P_LOCAL_003 | Real Job |
|---|---|---|---|
| Baseline CSV ingestion (ENWL format) | ✅ Tested | ⏳ | ⏳ |
| Baseline CSV ingestion (SPEN format) | ❌ Not tested | ⏳ | ✅ |
| Field evidence folder match | ✅ 12/12 | ⏳ | ⏳ |
| Coordinate gaps → named warning flag | ⚠️ Gaps documented; flag TBD | ⏳ | ⏳ |
| Coordinate system — BNG | ✅ 10 poles | ⏳ | ⏳ |
| Coordinate system — WGS84 (supplementary) | ✅ Notes only | ⏳ | ⏳ |
| Coordinate system — Irish Grid TM65 | ❌ NIE jobs only | ⏳ | ⏳ |
| Structural conflict detection | ⚠️ Partial — Pole 06 found; auto-rule TBD | ⏳ | ⏳ |
| Multiple DNO formats in one run | ❌ | ⏳ | ✅ |
| Notes content validation (not just presence) | ⚠️ Manual | ⏳ | ⏳ |
| Large route (30+ poles) | ❌ | ❌ | ✅ |
| Complete 12/12 baseline coordinates | ❌ 10/12 | ⏳ Target | ✅ |
| All 10 reports generated | ✅ (P_LOCAL_001 proven) | ⏳ | ⏳ |
| Design-blocked for all poles (correct outcome) | ✅ Expected | ⏳ | ⏳ |

---

## Risk Areas to Test

### 1. Baseline Format Variations

| Format | Status | Notes |
|---|---|---|
| ENWL CSV (pole_id, easting, northing) | ✅ Tested | P_LOCAL_002 |
| SPEN CSV | ⏳ Need sample | Different column names likely |
| Trimble GNSS controller dump | ⏳ Need sample | Handled by Stage 1 parser |
| Irish Grid TM65 coordinates | ⏳ NIE jobs | `coordinate_transformer.py` has TM65 support |

The coordinate transformer (`gridflow/baseline/coordinate_transformer.py`) already
supports BNG, ITM, and TM65 CRS detection and conversion. The risk is in CSV column
name variations across DNOs, not the transformation itself.

### 2. Evidence Quality Variations

| Scenario | P_LOCAL_002 result | Next test |
|---|---|---|
| Complete evidence folders | ✅ 10/12 at start | Target 12/12 for P_LOCAL_003 |
| Notes file present but empty | ✅ Detected (Pole 11) | Add content check to audit script |
| Notes file present but placeholder | ✅ Detected (Pole 12) | Add "Support UNKNOWN" detection |
| Partial ENWL screenshots | ✅ Handled | |
| Missing map screenshots | ✅ Handled (flagged) | |

### 3. Conflict Types

| Conflict type | P_LOCAL_002 result | Automation status |
|---|---|---|
| Structural classification mismatch (ENWL vs field) | ✅ Found manually — Pole 06 | ⚠️ Auto-detection TBD |
| Baseline coordinate blank | ✅ Found — Poles 10, 12 | ⚠️ Named flag TBD |
| Missing field evidence folder | ✅ Would be flagged | ✅ Handled |
| Voltage inconsistency | ✅ Handled by merge flags | ✅ Handled |
| Support number mismatch | ✅ Handled by matcher | ✅ Handled |

---

## Validation Criteria by Job

### P_LOCAL_002 (current baseline)

- ✅ 12/12 structural match confirmed
- ⚠️ Coordinate gap flag — needs confirmation that it surfaces in QA report
- ⚠️ Pole 06 conflict — needs confirmation of auto-detection
- ✅ Design-readiness: 0/12 (correct — no conductor spec or pole class confirmed)

### P_LOCAL_003 (next job)

- ≥ 90% structural match without code changes
- Different route type exercises different baseline attributes
- Pipeline completes end-to-end with all 10 reports
- Any conflicts detected and named
- Design-readiness: 0/N (expected correct outcome)

### Real Job (production)

- 100% structural match
- ≥ 80% baseline coordinate completeness (named flags for remainder)
- All conflicts auto-detected in QA report
- 0/N design-ready (correct — awaiting DNO engineering records)
- Sub-5-minute runtime for 50 poles

---

## Timing

P_LOCAL_003 capture should begin **after Stage 4C M1 is complete** — i.e., after the
pipeline validation run on P_LOCAL_002 confirms all acceptance criteria from
`AI_CONTROL/30_STAGE4C_IMPLEMENTATION_PLAN.md`.

Starting P_LOCAL_003 capture before M1 is complete risks wasting field time on a job
whose pipeline behaviour is not yet understood.

**P_LOCAL_003 capture target:**
- When: After Stage 4C M1 acceptance check complete
- Where: Different ENWL route (Carnforth area has other routes) or SPEN area
- Size: 10–15 poles
- Focus: At least one different pole configuration not in P_LOCAL_002

---

## Long-Term Testing Roadmap

| Phase | Job | Target | Gate |
|---|---|---|---|
| Phase 1 | P_LOCAL_002 | Validation baseline | CONDITIONAL GO ✅ |
| Phase 2 | P_LOCAL_003 | Repeatability test | ≥ 90% match; 10 reports |
| Phase 3 | Multi-DNO format test | Second DNO format | Parser handles SPEN/NIE CSV |
| Phase 4 | 30–50 pole route | Scale test | Sub-5-min runtime |
| Phase 5 | Real operational job | Production validation | DNO data access + all criteria |

No phase should be started until the prior phase gate is met. Phase 5 requires a
formal go/no-go decision by the project owner.
