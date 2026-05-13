# P_CONTROLLED_LOCAL_001 Planning Document

**For: Governance plan for the next controlled local baseline-to-field pilot**

**Date:** 2026-05-13
**Authority:** Documents 88–95 (baseline-field decision memo, field-capture review, result template, audit checklist, gap confirmation, final result)
**Purpose:** Define scope, inputs, outputs, and success criteria for a controlled baseline-to-field matching pilot using real ENWL Network Asset Viewer baseline data
**Status:** PLANNING (awaiting approval to proceed)

---

## Purpose and Rationale

### Why P_CONTROLLED_LOCAL_001?

P_LOCAL_001 proved that field-capture workflow is feasible:
- ✅ Operator can capture 9+ structures with observations and photos
- ✅ Photos can be organized and linked by pole_id
- ✅ Unknown/uncertain fields can be documented honestly
- ✅ Validator processes real field data successfully

**But P_LOCAL_001 could not answer:** Can field evidence be matched to a real baseline with ≥80% accuracy?

P_CONTROLLED_LOCAL_001 will answer that question:
- Real baseline from ENWL Network Asset Viewer (not made-up pole_ids)
- Noel captures same poles as listed in baseline
- Validator calculates exact pole_id match rate
- If match rate ≥80% → confidence that Phase 4 (larger controlled pilot) will work
- If match rate <80% → reveals mismatches to address before full Phase 4

---

## Scope: Local Accessible Area

### Geographic Target

**Region:** Local route near Noel, accessible without trespassing

**Candidate areas:**
- Sheernest Lane / Burton Road / Holme area
- Other accessible local route (TBD based on ENWL Network Asset Viewer coverage)

**Selection criteria:**
- ENWL baseline data available in Network Asset Viewer
- Poles physically accessible to Noel
- Mix of overhead lines (not all underground)
- At least 8–12 poles in the route
- Geographic clustering (not scattered across multiple areas)

**Access requirement:**
- No trespassing needed
- Safe access for photo capture (standard footpath/road access)
- Daylight photography feasible
- Noel familiar with area (local to his location)

---

## Baseline Inputs

### What Codex Will Obtain from ENWL Network Asset Viewer

**Baseline data sources:**

1. **trace-results.csv** (exported from Asset Viewer)
   - Contains: support_no (unique identifier), spn, fid, lat, lon, height, strength_class, type, condition, age, material
   - Expected rows: 8–12 unique supports
   - Format: CSV with standard NAV column headers

2. **Pole popup screenshots** (one per baseline structure)
   - Capture: All visible fields in Asset Viewer pole popup (support name, spn, location, asset ID, condition, etc.)
   - Purpose: Verify baseline record matches physical pole in field
   - Format: PNG/JPG screenshots, organized by pole identifier

3. **Conductor popup screenshots** (one per unique conductor segment in baseline area)
   - Capture: All visible fields in Asset Viewer conductor popup (voltage, phase, conductor size, circuit, attachments, etc.)
   - Purpose: Baseline equipment record for field verification
   - Format: PNG/JPG screenshots, organized by conductor ID

4. **Route overview screenshot** (1 per route)
   - Capture: Map view showing baseline pole locations, route extent
   - Purpose: Reference for field navigation and pole clustering verification
   - Format: PNG/JPG, georeferenced or with clear road/landmark labels

### Storage (Local Only)

All baseline data stored locally in:
```
real_pilot_data/P_CONTROLLED_LOCAL_001/baseline/
├── trace-results.csv
├── pole_popups/
│   ├── support_001_popup.png
│   ├── support_002_popup.png
│   └── ...
├── conductor_popups/
│   ├── circuit_A_popup.png
│   ├── circuit_B_popup.png
│   └── ...
└── route_overview.png
```

**Critical:** All ENWL Network Asset Viewer data remains local-only. No committed to git. File .gitignore ensures `real_pilot_data/` is excluded.

---

## Field Inputs (Noel's Capture)

### What Noel Will Capture During Field Visit

**For each baseline pole (8–12 structures):**

1. **Pole context photo** (wide view)
   - Shows: Full pole in landscape context, nearby structures, road/footpath
   - Purpose: Confirm physical pole location matches baseline coordinates
   - Format: Photo named `support_NNN_context.jpg`

2. **Pole marking photo** (close-up, if safe and visible)
   - Shows: Painted pole identifier, carved marking (support number, SPG code, etc.)
   - Purpose: Verify baseline support_no matches physical pole label
   - Format: Photo named `support_NNN_marking.jpg`
   - Note: Only if safe to approach and marking visible. OK to skip if not accessible/visible.

3. **Pole top photo** (if safe, looking up)
   - Shows: Conductor attachments, top hardware, insulator configuration
   - Purpose: Verify conductor type and phase configuration
   - Format: Photo named `support_NNN_top.jpg`
   - Note: Only if safe and feasible. Binoculars acceptable if photo not possible.

4. **Base/access/vegetation photo** (ground level context)
   - Shows: Pole base, ground access, vegetation around pole, any visible condition issues
   - Purpose: Document pole condition, access constraints, vegetation-related observations
   - Format: Photo named `support_NNN_base.jpg`

**Total photos per pole:** Minimum 2 (context + one of: marking/top/base); target 3–4

**Noel's field notes:** Document for each pole:
- Confidence: "confident match", "likely match", "uncertain", "no match found"
- Reason: Why confident (e.g., "marking visible and matches support_001") or uncertain (e.g., "pole not found at coordinates, likely moved")
- Equipment observation: What you can see (voltage, conductor count, phase, condition assessment)
- Access/safety notes: Any constraints or issues with photo capture

---

## Field Evidence Consolidation

### Codex Consolidation Task (After Noel's Field Visit)

1. **Copy all field photos** to:
   ```
   real_pilot_data/P_CONTROLLED_LOCAL_001/field_photos/
   ```

2. **Create field evidence register:**
   ```
   real_pilot_data/P_CONTROLLED_LOCAL_001/field_evidence_register.csv
   ```
   Columns: support_no (from baseline), photo_count, photo_references, noel_confidence, noel_notes, equipment_observations, access_notes

3. **Create baseline-to-field match report:**
   ```
   real_pilot_data/P_CONTROLLED_LOCAL_001/baseline_field_match_report.md
   ```
   Table format:
   - support_no (baseline)
   - baseline_location (lat/lon from trace-results)
   - field_photo_evidence (confidence + why)
   - match_status (exact match / likely match / uncertain / no match)
   - equipment_match (baseline vs. field observation)
   - validator_status (valid / review-required / blocked)

4. **Run validator** on combined baseline+field CSV:
   ```
   python scripts/validate_baseline_field_pilot.py \
     --baseline real_pilot_data/P_CONTROLLED_LOCAL_001/baseline/trace-results.csv \
     --field real_pilot_data/P_CONTROLLED_LOCAL_001/field_evidence_register.csv \
     --photos real_pilot_data/P_CONTROLLED_LOCAL_001/field_photos/ \
     --match-report real_pilot_data/P_CONTROLLED_LOCAL_001/baseline_field_match_report.md \
     --output validation_runs/P_CONTROLLED_LOCAL_001_FINAL
   ```

---

## Matching Criteria

### Baseline Identifiers

Use these fields from trace-results.csv as matching references:

- **support_no:** Unique support identifier in ENWL baseline (primary key)
- **spn:** ENWL structure point number (secondary identifier)
- **fid:** Feature ID in ENWL asset layer (tertiary identifier)

When Noel finds a pole in the field:
1. Look for visible marking matching support_no (painted on pole)
2. If not visible, match by coordinates (lat/lon ±10m acceptable for local area)
3. If marking is partially visible, verify it's plausible (not reversed digit, etc.)

### Match Categories

For each baseline support, classify Noel's field evidence as:

#### ✅ EXACT MATCH
- Pole marking visible and matches baseline support_no exactly
- Field photos confirm pole location, equipment type
- Equipment observations match baseline (voltage, phase, conductor count)
- Confidence: High
- Row status: VALID (merge-ready if equipment confirmed)

#### ✅ LIKELY MATCH
- Pole marking not visible or unclear, but coordinates match within ~10m
- Field photos show pole at expected location
- Equipment type is consistent with baseline expectations
- Access/vegetation explains marking absence
- Confidence: Medium-high
- Row status: REVIEW-REQUIRED (need verification before design use)

#### ⚠️ UNCERTAIN MATCH
- Pole location is ambiguous (multiple poles nearby)
- Marking partially visible but unconfirmed
- Equipment observations do not match baseline (e.g., baseline says wooden, field shows concrete)
- Confidence: Medium or low
- Row status: REVIEW-REQUIRED (must be resolved before Stage 4C use)

#### ❌ NO MATCH
- Baseline coordinates point to empty space
- Pole that was marked in baseline has been removed or relocated
- Equipment type is fundamentally different
- No field evidence at expected location after thorough search
- Confidence: Low (confident that pole is missing, not that match is uncertain)
- Row status: BLOCKED (cannot be merged without manual correction)

### Critical Rule: No Invented Technical Values

If baseline field is empty or field observation is unclear:
- Mark field as **unknown**, not guessed
- Mark row as REVIEW-REQUIRED, not VALID
- Document the reason (e.g., "nameplate illegible", "cannot see equipment safely")

---

## Required Outputs

### What Codex Will Deliver

1. **Baseline Pole Register**
   - File: `baseline_pole_register.csv`
   - Columns: support_no, spn, fid, lat, lon, baseline_type, baseline_condition, baseline_age, baseline_material
   - Rows: All 8–12 baseline structures
   - Source: Extracted from trace-results.csv

2. **Baseline Conductor Register**
   - File: `baseline_conductor_register.csv`
   - Columns: conductor_id, circuit, voltage, phase, conductor_size, attachments, condition
   - Rows: All unique conductors in baseline area
   - Source: Extracted from conductor popups

3. **Field Evidence Register**
   - File: `field_evidence_register.csv`
   - Columns: support_no, photo_count, photo_refs, noel_confidence, noel_notes, equipment_observations, access_notes
   - Rows: All 8–12 structures (or subset if some not found)
   - Source: Noel's field photos and notes

4. **Baseline-to-Field Match Report**
   - File: `baseline_field_match_report.md`
   - Format: Markdown table + narrative summary
   - Content: For each baseline pole: confidence assessment, match status, equipment verification, validator row status
   - Key metrics:
     - Exact match count / total baseline (target: ≥80%)
     - Likely match count (helps meet 80% if included)
     - Uncertain match count (needs resolution)
     - No match count (blocker poles)

5. **Validator Report**
   - File: `validator_report.json` + `validator_report.md`
   - Content: Row-level validation results, match rate calculation, row counts (valid/review-required/blocked)
   - Metrics:
     - Exact match rate (%): ___ (target: ≥80%)
     - Valid rows: ___ (expected: 8–12 or subset if no matches found)
     - Review-required rows: ___ (expected: 0–3, depending on matching confidence)
     - Blocked rows: ___ (target: 0)

---

## Success Criteria

### Acceptance Threshold for P_CONTROLLED_LOCAL_001

**Pilot is SUCCESSFUL if:**

- ✅ At least 8–12 structures were baseline candidates
- ✅ Noel visited field area and captured photos for ≥8 structures
- ✅ Baseline-to-field exact match rate ≥80% (e.g., 8/10 = 80%, 10/12 = 83%)
- ✅ 0 blocked rows (no poles that cannot be identified)
- ✅ All unmatched/uncertain poles explicitly documented (why they don't match)
- ✅ No invented technical values (unknowns are marked as unknown)
- ✅ Validator passes or partially-passes
- ✅ Noel's confidence assessment is reasonable and documented

**Outcome if SUCCESSFUL:**
- Confidence that Phase 4 (larger 30–50 pole baseline pilot) can work
- Readiness to select a larger baseline (Bellsprings, Gordon, etc.) for Phase 4
- Lessons learned about field matching technique

**Pilot is UNSUCCESSFUL (requires rework) if:**

- ❌ Exact match rate <80% (e.g., 5/10 = 50%, 6/12 = 50%)
  - Questions: Are baseline coordinates accurate? Are markings visible? Is area suitable?
  - Action: Analyze failures, adjust approach or select different area for retry
- ❌ >10% blocked rows (cannot identify poles)
  - Questions: Are baselines outdated? Have poles been removed/relocated?
  - Action: Investigate why matches failed before proceeding
- ❌ Invented or unsupported technical values in field evidence
  - Question: Did Noel follow template guidance to mark unknowns?
  - Action: Review feedback, clarify template for next attempt
- ❌ Validator fails with critical errors
  - Question: Data format issues? Schema misalignment?
  - Action: Fix data issues and revalidate

---

## Stage 4C Authorization Status

### Current: BLOCKED (No Change)

P_CONTROLLED_LOCAL_001 does NOT authorize Stage 4C.

It is a **prerequisite confidence test** for Phase 4.

**Critical distinction:**
```
P_CONTROLLED_LOCAL_001 (this pilot): "Can we match field to baseline?"
                                      → YES: confidence for Phase 4
                                      → NO: reconsider approach

Phase 4 (larger pilot, 30–50 poles): "Does operator + validator + exact match
                                       deliver ≥80% match + confident verdict?"
                                      → YES: Stage 4C is authorized
                                      → NO: design handoff not ready
```

**Stage 4C unblocked only when:**
1. Phase 4 completes (30–50 pole controlled pilot)
2. Exact match rate ≥80%
3. Noel signs GO or CONDITIONAL GO verdict
4. Independent gate auditor approves
5. Implementation team is assigned

---

## Timeline and Ownership

### Pre-Pilot (This Branch)

- **Task:** Create planning document (this file)
- **Owner:** Claude Code
- **Deliverable:** AI_CONTROL/96_P_CONTROLLED_LOCAL_001_PLAN.md
- **Timeline:** 2026-05-13
- **Status:** Planning (awaiting approval to proceed with pilot execution)

### Pilot Execution (After Approval)

**Phase 1: Baseline Data Collection** (Codex)
- Obtain ENWL Network Asset Viewer baseline data for selected local route
- Extract trace-results.csv
- Capture baseline popups (pole, conductor, route overview)
- Storage: `real_pilot_data/P_CONTROLLED_LOCAL_001/baseline/`
- Timeline: ~2–3 days (depends on NAV access and route complexity)

**Phase 2: Field Capture** (Noel)
- Visit selected route
- Capture context, marking, top, and base photos for each baseline pole
- Document confidence assessment and equipment observations
- Storage: Local on field device (to be synced to PC)
- Timeline: ~2–4 hours field time (depending on area size and pole accessibility)

**Phase 3: Consolidation** (Codex)
- Organize field photos
- Create field evidence register
- Create baseline-to-field match report
- Run validator
- Storage: `real_pilot_data/P_CONTROLLED_LOCAL_001/field_*` + `validation_runs/P_CONTROLLED_LOCAL_001_FINAL`
- Timeline: ~1–2 days (depends on photo count and matching complexity)

**Phase 4: Review & Verdict** (Noel)
- Review match report and validator results
- Assess confidence in baseline-to-field alignment
- Fill verdict form (SUCCESSFUL / UNSUCCESSFUL)
- Record lessons learned
- Timeline: ~2–4 hours (depends on match rate and complexity)

**Overall Timeline:** ~1–2 weeks (assumes sequential phases with Codex/Noel coordination)

---

## Real Data Handling

### Local-Only Storage (Not Committed)

All real ENWL Network Asset Viewer data and field evidence remains strictly local:

```
real_pilot_data/P_CONTROLLED_LOCAL_001/
├── baseline/
│   ├── trace-results.csv (ENWL export — DO NOT COMMIT)
│   ├── pole_popups/ (ENWL screenshots — DO NOT COMMIT)
│   ├── conductor_popups/ (ENWL screenshots — DO NOT COMMIT)
│   └── route_overview.png (ENWL screenshot — DO NOT COMMIT)
├── field_photos/ (Noel's photos — DO NOT COMMIT)
├── field_evidence_register.csv (Consolidated — DO NOT COMMIT)
└── baseline_field_match_report.md (Consolidated — DO NOT COMMIT)

validation_runs/P_CONTROLLED_LOCAL_001_FINAL/
├── validator_report.json (Output — DO NOT COMMIT)
└── validator_report.md (Output — DO NOT COMMIT)
```

**Git handling:** `real_pilot_data/` and `validation_runs/` are in `.gitignore`. All real data is excluded from version control.

**Governance record:** Only AI_CONTROL/97_P_CONTROLLED_LOCAL_001_VERDICT.md (verdict form, after pilot completes) will be committed.

---

## Next Steps

### After This Plan Is Approved

1. **Codex:** Select specific local route from ENWL Network Asset Viewer (confirm accessibility)
2. **Codex:** Extract and prepare baseline data
3. **Noel:** Visit field area, capture photos
4. **Codex:** Consolidate field evidence, run validator
5. **Noel:** Review results, fill verdict form
6. **Claude Code:** Create AI_CONTROL/97_P_CONTROLLED_LOCAL_001_VERDICT.md with final results
7. **Decision:** If SUCCESSFUL → authorize Phase 4 planning; if UNSUCCESSFUL → analyze failures and retry or adjust scope

---

## Reference

- **Doc 88:** Baseline vs. Field Evidence Decision Memo (why both required for Stage 4C)
- **Doc 89:** P_LOCAL_001 Field-Capture Review (what field-capture workflow proves)
- **Doc 90:** Field-Capture vs. Baseline Merge Gap (Phase 4 requirements)
- **Doc 91:** P_LOCAL_001 Field-Capture Result Template (verdict form example)
- **Doc 92:** P_LOCAL_001 Final Review Checklist (Noel's review process)
- **Doc 93:** P_LOCAL_001 Final Result Audit Checklist (independent audit)
- **Doc 94:** P_LOCAL_001 Stage 4C Gap Confirmation (Phase 4 requirements)
- **Doc 95:** P_LOCAL_001 Field-Capture Result (final result record)
