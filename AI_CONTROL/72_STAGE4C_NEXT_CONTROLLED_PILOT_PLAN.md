# Stage 4C Next Controlled Pilot Plan

**Date:** 2026-05-11
**Authority:** Document 71 (P_REAL_001_MINI Independent Gate Audit)
**Purpose:** Define the controlled follow-up pilot that will determine if Stage 4C is ready for production integration
**Status:** Ready for Noel's approval and execution

---

## Objective

After the successful shakedown of P_REAL_001_MINI, the next controlled pilot must prove:

1. **Pole_id matching works at ≥80% rate against a real Trimble baseline** (not workbook-derived)
2. **Electrical attributes can be verified against known job baseline** (voltage, class, strength, conductor)
3. **Review-required threshold can be determined and accepted or improved** through better capture technique
4. **The workflow is production-ready** (minimal manual steps, clear error messages, usable reports)
5. **Evidence linking works at scale** (100% coverage maintainable on 30–50 pole job)

---

## Pilot Definition

### Scale

- **Sample size:** 30–50 poles (realistic job size, smaller than full production)
- **Rationale:** Large enough to test evidence linking and workflow at scale; small enough to control closely

### Site selection

- **Job baseline requirement:** Real completed job with known Trimble GNSS baseline (e.g., P008/F001, or another past job with full validation data)
- **Baseline criteria:**
  - Trimble CSV exists and is complete (pole_id, coordinates, basic attributes)
  - Job is geographically diverse (mix of terrain, access, vegetation, distance)
  - Grid reference system is known (ITM, OSGB, Irish Grid)
  - Minimum 30 poles, maximum 200 (control scope)

### Capture protocol

**What Noel will do:**

1. Review the Trimble baseline for the chosen job
2. Select 30–50 poles spanning:
   - Easy access (clear pole, close distance, good lighting)
   - Medium access (partial obstruction, moderate distance)
   - Difficult access (restricted, distant, vegetation, poor light)
3. Capture structured data using the Stage 4 template for each pole
4. Take evidence photos per the evidence protocol (document 54)
5. Organize photos in `photos_final` subfolder with normalized filenames
6. Run `python scripts/validate_stage4_pilot.py` locally
7. Compare validator results against Trimble baseline

**What the validator will do:**

1. Validate CSV structure (no errors)
2. Check pole_id format and uniqueness
3. Flag rows with missing or low-confidence attributes
4. Generate merge-ready / review-required / blocked classification
5. Verify evidence linking (0 missing, 0 orphaned, 0 duplicate filenames)
6. Produce JSON + Markdown reports

**What Noel will interpret:**

1. Compare validator pole_ids against Trimble baseline: calculate match %
2. For merge-ready rows: verify attributes against Trimble baseline values (voltage, class, etc.)
3. For review-required rows: understand the flag reason (low confidence? verification needed? inferred?)
4. Assess if the warning profile is acceptable OR if better capture technique can reduce warnings
5. Make a manual go/no-go judgment

---

## Success Criteria

### Quantitative thresholds (MUST meet all)

| Metric | Target | Rationale |
|--------|--------|-----------|
| **Sample size** | ≥30 poles | Statistical confidence for job-scale pilot |
| **Validation pass rate** | ≥90% (at most 3 invalid rows per 30) | No schema/parsing failures |
| **pole_id match rate** | ≥80% (at least 24/30 pole IDs match Trimble) | Primary merge key correctness |
| **Evidence linking** | 100% (0 missing, 0 orphaned, 0 duplicates) | Proven workflow integration |
| **merge-ready rows** | ≥50% (at least 15/30) | Demonstrates clean capture on real baseline |
| **review-required rows** | ≤50% (at most 15/30) | Confirms threshold is achievable |
| **Attribute match (voltage/class)** | ≥75% on merge-ready rows | Sample validation against baseline |

### Qualitative thresholds (MUST satisfy)

1. **Workflow simplicity:** No more than 3 manual steps required per pole (capture, organize, validate) without errors
2. **Error clarity:** Validator error/warning messages must be actionable by Noel (not cryptic)
3. **Baseline agreement:** Noel can explain any pole_id mismatch (typo? new pole? missing from Trimble? format difference?)
4. **Evidence quality:** Photos are clear, organized, and linked correctly without post-processing effort
5. **Reproducibility:** Second capture of the same 5 poles by Noel produces ≥95% identical results

---

## Exact Validation Commands

```bash
# Step 1: Prepare the pilot CSV
# Location: real_pilot_data/<PILOT_ID>/csv/<PILOT_ID>.csv
# Format: ISO 8601 dates, normalized values, required fields filled

# Step 2: Organize evidence photos
# Location: real_pilot_data/<PILOT_ID>/photos_final/
# Subdirs: clear/, obscured/, proxy/, inferred/, none/
# Filenames: <pole_id>_<evidence_type>_<sequence>.jpg

# Step 3: Run validation (locally, no runtime integration)
python scripts/validate_stage4_pilot.py \
  --csv real_pilot_data/<PILOT_ID>/csv/<PILOT_ID>.csv \
  --evidence-dir real_pilot_data/<PILOT_ID>/photos_final/ \
  --pilot-name <PILOT_ID> \
  --out validation_runs/stage4_pilots/<PILOT_ID>_FINAL

# Step 4: Review output
# Terminal: Verdict (GO / PARTIAL / NO-GO) + summary
# JSON: validation_runs/stage4_pilots/<PILOT_ID>_FINAL/pilot_validation_report.json
# Markdown: validation_runs/stage4_pilots/<PILOT_ID>_FINAL/pilot_validation_report.md

# Step 5: Compare against Trimble baseline
# Manual: Extract Trimble pole_ids from sample_data/
# Manual: Compare against <PILOT_ID>.csv pole_ids
# Manual: Calculate match rate and record mismatches

# Step 6: Record result
# Manual: Use AI_CONTROL/65_STAGE4C_DECISION_BOARD_TEMPLATE.md
# Manual: Document verdict, match rate, attribute sample, threshold assessment
```

---

## Decision Criteria for Stage 4C Gate

### GO Decision (Stage 4C ready to integrate)

**All quantitative AND qualitative criteria met, AND:**

1. pole_id match rate ≥80% (or mismatch reasons are documented and acceptable)
2. merge-ready rows ≥50% (demonstrates consistent, clean capture on real baseline)
3. review-required rows ≤50% (and Noel accepts the threshold OR confirms capture technique improvements resolved them)
4. Evidence linking 100% (proven workflow)
5. Noel explicitly signs the decision board template with **GO** verdict

**Impact:** Stage 4C runtime integration can begin immediately after gate approval.

### CONDITIONAL GO (Stage 4C open with cautions)

**Quantitative criteria met, but qualitative concerns remain, OR:**

1. pole_id match 75–80% (acceptable but with documented mismatch causes)
2. merge-ready 40–50% (lower than ideal but workable)
3. Workflow has 1–2 minor friction points (e.g., photo naming requires a checklist)

**Decision:** Noel approves with written cautions documented on decision board. Stage 4C integration proceeds with explicit risk acknowledgment. Post-merge, a Stage 4C-specific control task will address the cautions.

### NO-GO (Stage 4C remains blocked)

**Any quantitative threshold not met, OR:**

1. pole_id match <75% and reason is unclear (baseline mismatch? measurement error? systematic?)
2. merge-ready <40% (more than 60% of rows require review; captures unacceptable data quality)
3. review-required >60% and Noel cannot determine root cause or remedy
4. Evidence linking <90% (broken links, orphaned photos, or duplicate filenames)
5. Workflow has >2 critical friction points or error messages are unclear

**Decision:** Noel marks NO-GO on decision board. Root cause is investigated. Remediation plan is created (template changes? validator improvements? training materials?). A second controlled pilot is planned after remediation.

### STOP (Pilot cannot continue)

**Immediate termination if:**

1. Runtime integration is attempted (violates isolation contract)
2. Real pilot data is accidentally committed to repo
3. Stage 4 data leaks into map-viewer, popups, or QA engine
4. Validator crashes on the real CSV

**Decision:** Emergency investigation. Stage 4 is immediately frozen pending review.

---

## Failure / Re-Pilot Rules

If the controlled pilot produces NO-GO or STOP:

1. **Investigate root cause:** Is it a template defect? Validator bug? Capture technique issue? Baseline mismatch?
2. **Create a remediation plan:** Fix template, update validator, create guidance docs, or revise capture protocol
3. **Plan re-pilot:** Decide if the same job baseline will be retried OR a different job is chosen
4. **Do not merge Stage 4C runtime:** Keep it blocked until re-pilot succeeds
5. **Do not bypass the gate:** Noel's manual sign-off is required; no force-push shortcuts

---

## What Happens After GO Decision

**If Noel signs GO:**

1. The Stage 4C architecture is now approved for runtime integration (document 56–60)
2. The decision board template (document 65) is filled out, signed, and recorded
3. A new task is created: "Stage 4C Controlled Runtime Integration" (separate from this task)
4. Pole_id matching algorithm is wired into the intake route (api_intake.py)
5. Feature flag `FEATURE_STAGE4C_INTAKE_ENABLED` is set to True in config
6. A Stage 4C runtime test plan runs against the validation test suite
7. Noel's real pilot CSV is the first production data to flow through the intake route
8. Map, Review OS, and popup surfacing are tested (Stage 4D gate, separate)

**Blocking conditions until Stage 4C runtime is released:**

- All test coverage for Stage 4C boundary checks must pass (document 60)
- merge_safety_check.py must confirm no leakage to forbidden files
- Noel must run through a final rehearsal with the real CSV on the local validation CLI

---

## What Noel Should Do Now

1. **Select a real job baseline** (ideally P008/F001 or another completed job with full Trimble data)
2. **Plan the 30–50 pole sample** (mix of easy, medium, difficult access)
3. **Schedule the capture** (expect 2–3 hours for 30 poles with evidence photos)
4. **Communicate timeline:** When does Noel plan to run the controlled pilot?
5. **Stage 4C remains blocked** until this controlled pilot is complete and produces a GO decision

---

## Ownership and Timeline

- **Noel:** Execute capture, run validation, interpret results, sign decision board
- **Claude Code:** Support the audit process, review decision board, confirm gate verdict
- **No enforcement:** This is a gate, not a hard block. If Noel chooses to proceed with NO-GO, that is Noel's decision to document and own.

---

## Sign-Off

**Auditor:** Claude Code
**Date:** 2026-05-11
**Document Authority:** AI_CONTROL/71_P_REAL_001_MINI_INDEPENDENT_GATE_AUDIT.md

This plan defines the controlled pilot that will open or keep closed the Stage 4C runtime integration gate. Noel's execution and decision on this pilot are the gate control.
