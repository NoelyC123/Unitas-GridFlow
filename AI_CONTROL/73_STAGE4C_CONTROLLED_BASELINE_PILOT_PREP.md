# Stage 4C Controlled Baseline Pilot Preparation Pack

**Date:** 2026-05-11
**Purpose:** Define how Noel will execute the next controlled pilot against a real GridFlow/Trimble job baseline
**Authority:** Document 50 (Go/No-Go Gate), Document 72 (Next Controlled Pilot Plan)
**Status:** Ready for Noel's execution

---

## Why P_REAL_001_MINI Is Not Enough

P_REAL_001_MINI was a successful shakedown of the Stage 4 pilot workflow:
- ✅ Validator works (no crashes, correct row classification)
- ✅ Evidence linking works (100% coverage, no missing/orphaned/duplicates)
- ✅ Template is usable (no schema confusion)
- ✅ Local validation workflow is proven (capture → validate → interpret)

But it did **NOT** prove:
- ❌ Pole_id matching against a real Trimble baseline
- ❌ Electrical attribute correctness (voltage, class, strength, etc.)
- ❌ Production-scale evidence linking (only 10 poles)
- ❌ Acceptable review-required threshold (80% is too high)

**Gate blocker:** Document 50 (G4) explicitly requires: **"pole_id merge key validated against real Trimble job data"**

P_REAL_001_MINI used workbook-derived pole_ids (P-REAL-001-MINI-01 to 10). This does not satisfy G4.

**Next step:** A controlled pilot on a real job baseline where we can compare captured pole_ids against actual Trimble records.

---

## Job Selection Criteria

### Preferred: Full job baseline (30–50 poles)

Select a real job where:
- **Trimble CSV is complete** — pole_id, coordinates, basic attributes documented
- **Job is closed or mature** — Trimble data is stable, not actively changing
- **Geographic diversity** — mix of terrain, access levels, vegetation, distance to poles
- **Known reference frame** — ITM, OSGB, or Irish Grid; coordinate system is documented
- **No proprietary constraints** — data can be used for GridFlow testing without client approval conflicts
- **Candidate jobs:** P008/F001 (if available), or another past DNI/SPEN job with full Trimble baseline

**Minimum pole count:** 30
**Maximum pole count:** 200 (keep it testable and scoped)

### Acceptable fallback: Smaller real baseline (10–20 poles)

If a 30–50 pole job is not available:
- Select 10–20 poles from a real job where Trimble records are complete
- Reduce sample size does NOT reduce rigor — thresholds remain the same
- pole_id match rate must still be ≥80% (at least 8/10 or 16/20 poles matched)
- merge-ready rate must still be ≥50% (at least 5/10 or 10/20 rows)

### What NOT to use:
- ❌ Synthetic/test data (does not validate real-world capture accuracy)
- ❌ Incomplete Trimble records (cannot validate pole_id matching)
- ❌ Job with active design work (Trimble data may still change)
- ❌ Private client data (confidentiality concerns)

---

## Required Inputs

Before starting field capture, Noel must prepare:

1. **Trimble baseline CSV** — extracted from `sample_data/` or GridFlow database
   - Fields: pole_id, latitude, longitude, reference_frame
   - Optional but helpful: voltage, pole_class, pole_strength, structure_type

2. **Stage 4 template** — `templates/structured_capture_template.csv`
   - Pre-loaded or printed (iPad or paper)

3. **Evidence folder structure** — `real_pilot_data/<PILOT_ID>/photos_final/`
   - Subdirectories: `clear/`, `obscured/`, `proxy/`, `inferred/`, `none/`

4. **Field day checklist** — Document 62 (if available) or equivalent
   - What to capture per pole
   - When to take evidence photos
   - How to organize photos on-site

5. **Mapping reference** — Physical map or digital map of the job
   - Mark the 30–50 poles selected for capture
   - Identify access points, hazards, restricted areas

---

## Required Outputs

After field capture, Noel must produce:

1. **Captured CSV** — `real_pilot_data/<PILOT_ID>/csv/<PILOT_ID>.csv`
   - Filled Stage 4 template with 30–50 poles
   - pole_id exactly matching Trimble naming (or documented mismatch reasons)
   - All required fields filled; optional fields filled where applicable

2. **Evidence photos** — `real_pilot_data/<PILOT_ID>/photos_final/`
   - Normalized filenames: `<pole_id>_<evidence_type>_<sequence>.jpg`
   - Each row has at least 1 photo; multiple references allowed

3. **Validation report** — JSON + Markdown from `validate_stage4_pilot.py`
   - Terminal verdict (PASS / PARTIAL / NO-GO)
   - Row-by-row classification (merge-ready / review-required / blocked / invalid)
   - Evidence audit (reference coverage, missing/orphaned/duplicates)
   - Warning profile (low confidence, verification required, etc.)

4. **Pole_id match analysis** — Manual comparison table
   - Trimble pole_id vs. captured pole_id
   - Match/mismatch reason (exact match? format difference? new pole? missing from Trimble?)
   - Match rate calculation: (matched poles) / (total captured poles)

5. **Controlled pilot decision board** — Document 75 template
   - Filled thresholds: row count, match %, merge-ready %, etc.
   - Noel's verdict: GO / CONDITIONAL GO / NO-GO / STOP
   - Explicit sign-off

---

## Exact Field-Day Workflow

### Morning (pre-capture)

1. **Verify Trimble baseline is accessible** — Can you read the pole_ids you're about to capture?
2. **Load template on device** — iPad with template, or printed pages
3. **Check equipment** — Camera battery, device charger, notebook
4. **Test one pole** — Capture and photo one familiar pole; validate format before leaving

### On-site (per pole)

For each of the 30–50 selected poles:

1. **Locate pole** — Use map reference and Trimble baseline
2. **Confirm pole_id** — Read the pole tag if available; otherwise use Trimble ID
3. **Fill template row:**
   - pole_id (EXACT match to Trimble or documented mismatch reason)
   - capture_source ("surveyor_tablet" or "field_manual")
   - captured_by (your name)
   - capture_date (YYYY-MM-DD)
   - pole_type, voltage, condition, stays, equipment (if visible/knowable)
   - Mark `verification_required=yes` if uncertain about any value
   - evidence_status: "clear" / "obscured" / "proxy" / "inferred" / "none"
4. **Take evidence photos:**
   - Minimum 1 photo per pole (clear view of pole, label if visible)
   - Additional photos if different angles/distances needed
   - Use naming format: `<pole_id>_<evidence_type>_01.jpg`, `<pole_id>_<evidence_type>_02.jpg`, etc.
5. **Organize photos locally:**
   - Move to `real_pilot_data/<PILOT_ID>/photos_final/<evidence_type>/`
   - Verify filename before moving

### End of day

1. **Backup CSV** — Save captured CSV locally
2. **Organize all photos** — Move to evidence folders, verify structure
3. **Check for obvious errors** — Any poles with zero photos? Any rows with blank required fields?

---

## Post-Field Validation Workflow

### Step 1: Run the validator

```bash
python scripts/validate_stage4_pilot.py \
  --csv real_pilot_data/<PILOT_ID>/csv/<PILOT_ID>.csv \
  --evidence-dir real_pilot_data/<PILOT_ID>/photos_final/ \
  --pilot-name <PILOT_ID> \
  --out validation_runs/stage4_pilots/<PILOT_ID>_FINAL
```

Review terminal output:
- Verdict (PASS / PARTIAL / NO-GO)
- Top issues (missing fields? duplicate pole_ids? broken evidence links?)
- Next-action guidance

### Step 2: Extract pole_id match analysis

1. Open `validation_runs/stage4_pilots/<PILOT_ID>_FINAL/pilot_validation_report.json`
2. Extract the `pole_id` column from your captured CSV
3. Compare against the Trimble baseline pole_ids
4. Calculate match rate: (exactly matching pole_ids) / (total rows)
5. Document any mismatches and reasons (typo? format? new pole? Trimble-missing?)

### Step 3: Interpret the warning profile

From the Markdown report, review:
- `verification_required=yes` count — rows you flagged as uncertain
- `low confidence structured capture row` — inferred/estimated values
- `evidence status requires verification` — photos that need closer review

**Question:** Can you explain each warning? Is it a capture technique issue (can be improved on next attempt)? Or a field reality (acceptable uncertainty)?

### Step 4: Fill the decision template

Use Document 75 (Controlled Pilot Decision Template) to record:
- Row count, match %, merge-ready %, review-required %
- Evidence summary (photos found, coverage %)
- Defects and warnings
- Your interpretation
- GO / CONDITIONAL GO / NO-GO / STOP verdict
- Sign-off

---

## What Counts as Success

**GO (Stage 4C ready to merge):**
- ✅ pole_id match rate ≥80%
- ✅ merge-ready rows ≥50%
- ✅ review-required rows ≤50%
- ✅ Evidence linking 100%
- ✅ Noel signs GO on decision board
- **Impact:** Stage 4C implementation begins immediately

**CONDITIONAL GO (Stage 4C open with cautions):**
- ⚠️ pole_id match 75–80% (lower but acceptable)
- ⚠️ merge-ready 40–50% (lower but acceptable)
- ⚠️ Workflow has 1–2 minor friction points
- ✅ Noel signs CONDITIONAL GO with written cautions
- **Impact:** Stage 4C implementation begins with explicit risk acceptance

**NO-GO (Stage 4C remains blocked, re-pilot needed):**
- ❌ pole_id match <75%
- ❌ merge-ready <40%
- ❌ review-required >60%
- ❌ Evidence linking <90%
- ❌ Any unclear field value or mismatch pattern
- **Impact:** Root-cause analysis; template/validator/capture-technique improvements; re-pilot after fixes

**STOP (Pilot cannot continue):**
- ❌ Runtime integration attempted (violates isolation)
- ❌ Real pilot data committed to repo
- ❌ Stage 4 fields leaked into map/popup/QA runtime
- ❌ Validator crashes on the real CSV
- **Impact:** Emergency investigation; Stage 4 frozen

---

## Next Controlled Pilot Timeline

**When:** After P_REAL_001_MINI results are recorded and reviewed
**Who:** Noel (field capture) + Claude Code (gate audit)
**Deliverable:** Controlled pilot decision board (doc 75) with GO/CONDITIONAL GO/NO-GO/STOP verdict
**Blocker removed:** Stage 4C runtime integration can begin immediately on GO verdict

---

## Critical Notes

1. **This is NOT the mini pilot.** P_REAL_001_MINI was 10 workbook-derived poles. This is 30–50 real job poles with Trimble baseline comparison.

2. **This IS the gate criterion.** Document 50 (G4) says: **"pole_id merge key validated against real Trimble job data."** This controlled pilot satisfies G4.

3. **Real data stays local.** All captured CSVs, photos, and validation reports remain in `real_pilot_data/` and `validation_runs/` (git-ignored). Only the decision verdict is tracked on master.

4. **No runtime code in this task.** Stage 4C implementation (upload route, merge algorithm, database integration) happens on a SEPARATE task after GO verdict.

5. **Noel is the gate.** Your pole_id match analysis and GO/NO-GO decision are the criteria. No mechanical approval; your judgment is the control.

---

## Noel's Pre-Pilot Checklist

Before you go to the field:

- [ ] Real job baseline selected (30–50 poles, Trimble records complete)
- [ ] Trimble pole_ids extracted and reviewed
- [ ] Stage 4 template loaded on device (iPad or printed)
- [ ] Evidence folder structure created locally
- [ ] Field day checklist reviewed
- [ ] Map reference prepared (poles marked)
- [ ] Camera/device charged
- [ ] Test capture completed for 1 pole
- [ ] Ready to capture 30–50 poles

After field capture:

- [ ] Validator run: no crashes, verdict clear
- [ ] pole_id match rate calculated
- [ ] Mismatch reasons documented
- [ ] Warning profile reviewed and interpreted
- [ ] Decision template filled
- [ ] Verdict recorded (GO / CONDITIONAL GO / NO-GO / STOP)
- [ ] Decision signed and dated

---

## Delivery Sign-Off

**Prep Pack Author:** Claude Code
**Date:** 2026-05-11
**Authority:** Document 50 (Go/No-Go Gate G4), Document 72 (Next Controlled Pilot Plan)

This prep pack gives Noel everything needed to execute the controlled baseline pilot that will decide whether Stage 4C runtime integration can proceed.
