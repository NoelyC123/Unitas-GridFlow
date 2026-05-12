# P_LOCAL_001 Final Review Checklist

**For: Noel's pre-verdict review before recording P_LOCAL_001 result**

**Use this checklist immediately after Codex completes validator consolidation.**

**Status:** READY FOR USE

---

## Pre-Review Setup

### What You Should Have Before Starting This Checklist

- [ ] Codex has finished P_LOCAL_001 consolidation
- [ ] Validator has run: `python scripts/validate_stage4_pilot.py --csv real_pilot_data/P_LOCAL_001/csv/P_LOCAL_001.csv --evidence-dir real_pilot_data/P_LOCAL_001/photos_final/ --pilot-name P_LOCAL_001 --out validation_runs/stage4_pilots/P_LOCAL_001_FINAL`
- [ ] You have read `validation_runs/stage4_pilots/P_LOCAL_001_FINAL/pilot_validation_report.md` (summary)
- [ ] You have read `validation_runs/stage4_pilots/P_LOCAL_001_FINAL/pilot_validation_report.json` (metrics)
- [ ] You have access to photos in `real_pilot_data/P_LOCAL_001/photos_final/`
- [ ] You have the CSV file: `real_pilot_data/P_LOCAL_001/csv/P_LOCAL_001.csv`

---

## Section 1: Pole Structure Inventory

### Checklist: All 9 Structures Present

Open your CSV and confirm each of these pole_ids exists and is complete:

- [ ] **SPEN-QMM20** — present, data filled, photo(s) linked
- [ ] **SPEN-NMFSP** — present, data filled, photo(s) linked
- [ ] **POLE-FIELD-001** — present, data filled, photo(s) linked
- [ ] **POLE-H-FRAME-RES-001** — present, data filled, photo(s) linked
- [ ] **POLE-RURAL-ROAD-001** — present, data filled, photo(s) linked
- [ ] **POLE-RURAL-HEDGE-001** — present, data filled, photo(s) linked
- [ ] **POLE-VILLAGE-LSTC2021** — present, data filled, photo(s) linked
- [ ] **POLE-GARDEN-XFMR-001** — present, data filled, photo(s) linked
- [ ] **POLE-TEE-VEG-001** — present, data filled, photo(s) linked

**If any pole is missing:** ❌ STOP. Note which pole(s) missing and contact Codex.

---

## Section 2: H-Frame Counting Verification

### Critical Rule: H-Frame Is 1 Structure, 2 Timber Supports

**Question:** In your CSV, does POLE-H-FRAME-RES-001 appear as:
- [ ] **ONE row** (correct) — single pole_id, but notes indicate it is an H-frame with 2 timber supports
- [ ] **TWO rows** (incorrect) — contact Codex for de-duplication

**Counting statement (to use in final verdict):**
```
9 pole structures total
  - 8 single-support structures
  - 1 H-frame structure (comprised of 2 individual timber supports)
= 10 individual timber supports
```

**Verify the narrative is clear:** [ ] Yes, count is 9 structures, 10 individual supports

---

## Section 3: Photo Reference & Mapping

### Photo Naming Convention Check

Each pole should have photos named like: `POLE-FIELD-001_evidence.jpg` or `SPEN-QMM20_clear.jpg`

Open photo directory: `real_pilot_data/P_LOCAL_001/photos_final/`

Count photos per structure:
- [ ] SPEN-QMM20: _____ photos (expected: ≥1)
- [ ] SPEN-NMFSP: _____ photos (expected: ≥1)
- [ ] POLE-FIELD-001: _____ photos (expected: ≥1)
- [ ] POLE-H-FRAME-RES-001: _____ photos (expected: ≥1)
- [ ] POLE-RURAL-ROAD-001: _____ photos (expected: ≥1)
- [ ] POLE-RURAL-HEDGE-001: _____ photos (expected: ≥1)
- [ ] POLE-VILLAGE-LSTC2021: _____ photos (expected: ≥1)
- [ ] POLE-GARDEN-XFMR-001: _____ photos (expected: ≥1)
- [ ] POLE-TEE-VEG-001: _____ photos (expected: ≥1)

**Validator result check:**
- [ ] Validator reports: Missing photos = 0
- [ ] Validator reports: Orphaned photos = 0
- [ ] Validator reports: Evidence coverage ≥90%

**If photo count is wrong:** ❌ STOP. Review photo mapping with Codex. Update CSV if needed.

---

## Section 4: High-Risk Technical Fields Verification

### Critical Rule: Accept "Unknown" — Don't Overstate Confidence

For each of these high-risk fields, you MUST verify that Noel documented them honestly:

| Pole | Field | Expected | Check | Status |
|------|-------|----------|-------|--------|
| SPEN-QMM20 | voltage_carried | LV (Noel observation) | Photo shows transformer/equipment size? | [ ] |
| SPEN-QMM20 | conductor_size | Unknown or observable | Photo detail visible? | [ ] |
| SPEN-NMFSP | phase_configuration | Inferred or uncertain | Mark as verification_required? | [ ] |
| POLE-FIELD-001 | pole_class | Visual estimate OK | Noel marked uncertainty? | [ ] |
| POLE-FIELD-001 | pole_strength | Unknown expected | Is it marked as unknown/review-required? | [ ] |
| POLE-RURAL-ROAD-001 | inspection_plate_date | Documented from photo | Visible in photo, not extrapolated? | [ ] |
| POLE-GARDEN-XFMR-001 | access_notes | Documents constraints | Wording correct (see below)? | [ ] |

**Rule:** Unknown ≠ failure. Honest uncertainty is correct operator behavior.

---

## Section 5: SPEN-QMM20 Specific Confirmations

### SPEN-QMM20: Voltage Classification (LV with 2 Bare Conductors)

Open the CSV row for SPEN-QMM20. Check:

- [ ] **voltage_carried field:** Contains "LV" or "~11kV" or similar low-voltage value
- [ ] **conductor_size field:** Documents "2 bare" or similar observable feature
- [ ] **phase_configuration field:** Is this filled correctly (single-phase or inferred)?
- [ ] **Photo evidence:** Do photos show the bare conductors and small equipment size consistent with LV?

**Confirmation:**
- [ ] SPEN-QMM20 is correctly classified as LV with two bare conductors per Noel field observation
- [ ] No discrepancies with expected LV equipment

**If voltage or conductor data looks wrong:** [ ] Note discrepancy in final verdict

---

### SPEN-QMM20: Streetlight Mounting (Should NOT Be Included)

**Question:** Do photos of SPEN-QMM20 show:
- [ ] A **wood pole** with **2 bare conductors** and **no attached streetlight** ✅ CORRECT
- [ ] A **wood pole** with **a mounted streetlight** incorrectly attributed to this pole ❌ ERROR

**Action if streetlight is present:**
- If streetlight is on a separate pole: Verify it has a separate pole_id (e.g., SPEN-QMM20-LIGHT)
- If streetlight is incorrectly linked to SPEN-QMM20: [ ] Contact Codex for data correction

**Confirmation:**
- [ ] SPEN-QMM20 does not incorrectly include streetlight mounted on wood pole
- [ ] If streetlight present, it is correctly separated or has its own pole_id

---

## Section 6: POLE-GARDEN-XFMR-001 Vegetation Access Limits

### CRITICAL: Wording Must Be Conservative

Open the CSV row for POLE-GARDEN-XFMR-001. Check the `access_notes` or similar field:

**CORRECT WORDING examples:**
- ✅ "Vegetation limits clear view of base"
- ✅ "Cannot measure base due to shrubs"
- ✅ "Vegetation blocks safe access to inspection plate"
- ✅ "Photo obscured by foliage"

**INCORRECT WORDING (overstates constraint):**
- ❌ "DNO cannot access this pole"
- ❌ "Pole completely inaccessible"
- ❌ "Impossible to inspect"

**Check:**
- [ ] Wording says "limits inspection" or "blocks measurement" (not "blocks DNO access")
- [ ] Notes are accurate reflection of Noel's field observation
- [ ] Field does NOT overstate the access constraint

**If wording is too strong:** [ ] Recommend Codex correct to "limits access for measurement" or similar

---

## Section 7: POLE-RURAL-ROAD-001 Inspection Plate Dates

### Rule: Document Only What Is Visible in Photo

Open CSV row for POLE-RURAL-ROAD-001. Check:

- [ ] **inspection_plate_date field:** Is filled or marked "unknown"?
- [ ] **Evidence:** Check the photo — is the date actually readable?
- [ ] **Photo evidence:** Is the date clearly visible, or is this an inference?

**Confirmation:**
- [ ] Inspection plate dates are documented from what is visible in photo
- [ ] Dates are not extrapolated or inferred beyond photo visibility
- [ ] If unreadable, field correctly says "unknown"

**If date is guessed:** [ ] Mark for review-required status in final verdict

---

## Section 8: POLE-VILLAGE-LSTC2021 Photo Mapping Status

### Photo Linking Verification

Check the validator report (evidence_audit.json) for POLE-VILLAGE-LSTC2021:

- [ ] **In report:** `POLE-VILLAGE-LSTC2021` shows _____ linked photo(s)
- [ ] **Expected:** ≥1 photo(s)
- [ ] **Status:** Linked or missing?

**Manual photo check:**
- [ ] Look in `real_pilot_data/P_LOCAL_001/photos_final/` for files containing `VILLAGE-LSTC2021`
- [ ] Confirm file naming is correct (`POLE-VILLAGE-LSTC2021_*.jpg` or similar)
- [ ] Confirm photo is valid (not corrupted, readable)

**Confirmation:**
- [ ] POLE-VILLAGE-LSTC2021 photo mapping status is correct
- [ ] All required photos present and correctly named
- [ ] No orphaned photos for this pole

**If photo is missing or orphaned:** [ ] Contact Codex for remediation

---

## Section 9: High-Risk Field Verification Summary

### Spot-Check 5–10 Poles for Inferred Fields

Using the validator report, identify 5–10 poles with most "review-required" or "unknown" status.

For each pole, open its row in the CSV and check:

| Pole | Field | Value | Honest? | Status |
|------|-------|-------|---------|--------|
| | voltage_carried | | [ ] | |
| | conductor_size | | [ ] | |
| | pole_class | | [ ] | |
| | pole_strength | | [ ] | |
| | stay_required | | [ ] | |
| | | | | |

**Rule:** "Honest uncertainty" = ✅ GOOD. "Forced unknown where observable" = ❌ PROBLEM.

**Check for patterns:**
- [ ] Fields marked "unknown" are genuinely unknown (not observable from field/photo)
- [ ] Fields marked with values are observable or well-reasoned inferences
- [ ] No systematic pattern of over/under-reporting

**If systematic errors found:** [ ] Note in final verdict and recommend Phase 4 template refinement

---

## Section 10: Stage 4C Authorization Confirmation

### Critical Final Check: Stage 4C Remains BLOCKED

This is NOT a Stage 4C authorization pilot.

Read and confirm you understand:

- [ ] P_LOCAL_001 has NO independent baseline to compare against
- [ ] Exact pole_id match rate CANNOT be calculated
- [ ] P_LOCAL_001 CANNOT satisfy the ≥80% exact-match threshold
- [ ] Phase 4 (full baseline + field evidence combined) IS REQUIRED for Stage 4C
- [ ] This result record does NOT authorize Stage 4C implementation
- [ ] Stage 4C remains BLOCKED until Phase 4 is complete and approved

**Confirmation:**
- [ ] I understand P_LOCAL_001 is field-capture learning evidence, not Stage 4C approval evidence
- [ ] I have read Document 90 (Field-Capture vs. Baseline Merge Gap)
- [ ] I understand Phase 4 requirements before Stage 4C can proceed

---

## Final Decision Guide

### Choose ONE verdict based on evidence:

#### ✅ PASS AS FIELD-CAPTURE EVIDENCE

**Use this if:**
- [ ] All 9 structures present with correct naming
- [ ] H-frame counting is 1 structure, 2 supports (verified)
- [ ] Photo mapping: all poles have ≥1 photo, zero orphaned photos
- [ ] Validator result: ≥85% valid rows, ≤5% blocked rows
- [ ] High-risk fields verified: no systematic over/under-reporting
- [ ] SPEN-QMM20: LV classification confirmed, no streetlight misattribution
- [ ] POLE-GARDEN-XFMR-001: wording correct (limits access, not blocks DNO access)
- [ ] POLE-RURAL-ROAD-001: dates from photo only, not extrapolated
- [ ] POLE-VILLAGE-LSTC2021: photo mapping correct
- [ ] Operator confidence is high; no major friction noted
- [ ] Workflow is reusable for Phase 4

**Action:** Select **PASS** in doc 91 verdict section

---

#### ⚠️ PARTIAL AS FIELD-CAPTURE EVIDENCE

**Use this if:**
- [ ] 8–9 structures present (1 structure may be unclear)
- [ ] H-frame counted correctly but with minor naming ambiguity
- [ ] Photo mapping: most poles have ≥1 photo; 1–2 minor orphaned photos
- [ ] Validator result: 75–85% valid rows, 5–10% blocked rows
- [ ] High-risk fields have pattern: one field (e.g., voltage) consistently uncertain
- [ ] SPEN-QMM20: LV likely but photo quality unclear for conductor count
- [ ] POLE-GARDEN-XFMR-001: wording acceptable but could be more precise
- [ ] POLE-RURAL-ROAD-001: date inference reasonable but not fully clear
- [ ] POLE-VILLAGE-LSTC2021: photo mapping mostly correct, minor gap
- [ ] Operator noted specific friction; suggests template improvement
- [ ] Workflow is mostly reusable for Phase 4 with noted adjustments

**Action:** Select **PARTIAL** in doc 91 verdict section; list remediation needed

---

#### ❌ NO-GO FIELD-CAPTURE EVIDENCE

**Use this if:**
- [ ] <8 structures present OR missing key poles
- [ ] H-frame counting is wrong or unclear
- [ ] Photo mapping: missing photos, orphaned photos, or orphaned poles
- [ ] Validator result: <75% valid rows OR >10% blocked rows
- [ ] High-risk fields show systematic errors (e.g., voltages all guessed)
- [ ] SPEN-QMM20: voltage/conductor classification contradicts photo evidence
- [ ] POLE-GARDEN-XFMR-001: wording overstates constraint or misleads
- [ ] POLE-RURAL-ROAD-001: dates are extrapolated without photo evidence
- [ ] POLE-VILLAGE-LSTC2021: photo mapping is broken or unclear
- [ ] Operator reported major friction or workflow blockers
- [ ] Workflow cannot be reused for Phase 4 without major changes

**Action:** Select **NO-GO** in doc 91 verdict section; identify root cause and recommended fixes

---

## Submission Checklist

Before you record your final verdict:

- [ ] You have completed all 10 sections above
- [ ] You have reviewed the validator output (JSON and MD reports)
- [ ] You have spot-checked 5–10 poles manually
- [ ] You have confirmed the H-frame count (9 structures, 10 supports)
- [ ] You have verified SPEN-QMM20 voltage and streetlight questions
- [ ] You have checked POLE-GARDEN-XFMR-001 wording
- [ ] You have confirmed POLE-RURAL-ROAD-001 inspection date sourcing
- [ ] You have confirmed POLE-VILLAGE-LSTC2021 photo mapping
- [ ] You have confirmed Stage 4C remains BLOCKED
- [ ] You have chosen your verdict: PASS / PARTIAL / NO-GO

**Ready to proceed:** [ ] Yes, I am ready to fill doc 91 final verdict section

---

## Next Actions

After completing this checklist:

1. **Fill Document 91 (Result Template)** with your findings
2. **Choose your verdict:** PASS / PARTIAL / NO-GO
3. **Add your notes** on operator experience and Phase 4 lessons learned
4. **Sign/date your verdict** (or record your review completion)
5. **Submit for gate audit** (if required by project governance)
6. **Notify:** This completes P_LOCAL_001 field-capture validation evidence record

---

## Reference

- **Doc 89:** P_LOCAL_001 Field-Capture Review (classification)
- **Doc 90:** Field-Capture vs. Baseline Merge Gap (Phase 4 requirements)
- **Doc 91:** P_LOCAL_001 Field-Capture Result Template (verdict form)
- **Validator:** `python scripts/validate_stage4_pilot.py`
- **Project rule:** Only Phase 4 (baseline + field + ≥80% match) authorizes Stage 4C
