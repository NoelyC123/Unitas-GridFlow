---
status: ACTIVE
created: 2026-05-10
branch: claude-code/stage4b-4c-safety-pilot-harness
---

# 50 — Stage 4C Go / No-Go Gate

This document defines the formal go/no-go gate for Stage 4C — the first phase
where Stage 4 structured capture data is accepted via a real upload route and
merged with live Trimble pole records.

Stage 4C is the **controlled runtime intake** phase. It is the first stage
where Stage 4 data can influence a live job result.

---

## Phase summary

| Phase | Status |
|---|---|
| Stage 4A (library correctness) | ✅ Merged |
| Stage 4B (validation preview) | Pending gate `49_STAGE4B_ACCEPTANCE_GATE.md` |
| **Stage 4C (controlled runtime intake)** | **This gate** |
| Stage 4D (browser popup surfacing) | Separate gate (not yet written) |

---

## Stage 4C scope

Stage 4C is STRICTLY LIMITED to:

1. Upload route (`api_intake.py`) accepts a Stage 4 CSV upload
2. Uploaded rows are validated via `validate_stage4_rows()`
3. Valid rows are merged into the per-pole record by `pole_id` match
4. Merged pole records carry Stage 4 fields with `source: "structured_capture"`
5. QA engine reads Stage 4 fields for confidence-aware rules (if explicitly scoped)

Stage 4C does NOT include:

- Browser popup rendering of Stage 4 fields (Stage 4D)
- New C2E2 popup sections for structured capture data
- Review OS template changes
- PoleCAD export changes

---

## Go / No-Go criteria

### GO conditions (ALL must be true)

| # | Criterion | Evidence required |
|---|---|---|
| G1 | Stage 4B acceptance gate fully passed | Link to merged Stage 4B PR |
| G2 | Real field pilot completed successfully | `53_REAL_FIELD_PILOT_RESULT_TEMPLATE.md` result = GO |
| G3 | Golden sample suite passes with 0 failures | `pytest tests/test_stage4_golden_samples.py -v` |
| G4 | `pole_id` merge key validated against real Trimble job data | Field pilot result table shows ≥1 confirmed match |
| G5 | Duplicate pole_id detection tested against real data | Field pilot or golden sample evidence |
| G6 | Stage 4C import does not corrupt existing Trimble pole records | Integration test: Trimble-only job still produces identical output after Stage 4C merge |
| G7 | Leakage guard suite still passes (Stage 4C tokens allowed only where approved) | `pytest tests/test_structured_capture_leakage.py -v` |
| G8 | `merge_safety_check.py` Stage 4C boundary check passes | merge_safety_check output |
| G9 | Noel has reviewed and signed off on the Stage 4C implementation plan | Explicit message in session notes |

### NO-GO conditions (ANY triggers a block)

| # | Condition | Action |
|---|---|---|
| N1 | Real field pilot result = NO-GO | Block Stage 4C; file defect report; fix Stage 4B before re-piloting |
| N2 | `pole_id` match rate < 80% on pilot dataset | Block; investigate ID format mismatch; fix normalisation |
| N3 | Any Trimble-only job output is changed by Stage 4C code path | Block; fix isolation; ensure opt-in only |
| N4 | Golden sample suite has any failures | Block; fix before merge |
| N5 | Any Stage 4C code path touches `map-viewer.js` or popup renderer | Immediate block; revert |
| N6 | Stage 4B not merged to master | Stage 4C must build on Stage 4B baseline |

---

## Stage 4C architecture requirements

Before writing Stage 4C code, the following architectural decisions must be
explicit in the implementation plan:

1. **Opt-in only**: Stage 4 data is used only if a Stage 4 CSV is uploaded.
   Existing Trimble-only uploads must produce byte-identical output to today.

2. **Merge by pole_id, not by file position**: Row matching is keyed on
   `pole_id`, not CSV row order.

3. **Stage 4 fields are additive**: Stage 4 values do not overwrite Trimble
   survey values for the same field. Conflicts are flagged, not silently resolved.

4. **Source label preserved**: Merged fields carry `source: "structured_capture"`
   so downstream code can distinguish their origin.

5. **Validation before merge**: `validate_stage4_rows()` must pass before any
   row is merged into the live pole record. Invalid rows are rejected with
   diagnostic output, not silently dropped.

---

## Gate verification command sequence

```bash
# 1. Confirm Stage 4B is merged
git log --oneline origin/master | head -20

# 2. Confirm field pilot result
cat AI_CONTROL/53_REAL_FIELD_PILOT_RESULT_TEMPLATE.md  # look for VERDICT: GO

# 3. Run full test suite
pytest -v

# 4. Run golden sample suite specifically
pytest tests/test_stage4_golden_samples.py -v

# 5. Run leakage guard suite
pytest tests/test_structured_capture_leakage.py -v

# 6. Run merge safety check
python scripts/merge_safety_check.py <stage4c-branch-name>

# 7. Run integration test confirming Trimble-only output unchanged
pytest tests/test_stage4c_trimble_isolation.py -v
```

---

## Gate owner

Noel Collins. The Stage 4C go/no-go decision belongs to Noel, not to an AI
worker. No Stage 4C branch merges without Noel's explicit sign-off.
