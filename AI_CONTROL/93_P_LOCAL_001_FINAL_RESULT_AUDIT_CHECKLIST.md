# P_LOCAL_001 Final Result Audit Checklist

**For: Independent audit of Codex's final P_LOCAL_001 consolidation outputs**

**Use this checklist after Codex finishes final consolidation.**

**Status:** READY FOR AUDIT USE

---

## Pre-Audit Setup

### What You Should Have Before Starting This Audit

**Codex deliverables expected:**
- [ ] `p_local_001_capture_final.csv` — final CSV with all 9 pole structures and all field data
- [ ] `p_local_001_capture_final.xlsx` — final Excel workbook (if created)
- [ ] `final_photo_mapping.md` — final documentation of photo-to-pole linking
- [ ] `final_field_review_summary.md` — final summary of field observations and any corrections
- [ ] `final_validation_report.md` — final validation report (human-readable)
- [ ] `final_validation_report.json` — final validation report (machine-readable metrics)

**Files you will compare against:**
- AI_CONTROL/91_P_LOCAL_001_FIELD_CAPTURE_RESULT_TEMPLATE.md (result template)
- AI_CONTROL/92_P_LOCAL_001_FINAL_REVIEW_CHECKLIST.md (Noel's review checklist)

**Reference documents:**
- AI_CONTROL/89_P_LOCAL_001_FIELD_CAPTURE_REVIEW.md (classification)
- AI_CONTROL/90_FIELD_CAPTURE_VS_BASELINE_MERGE_GAP.md (Phase 4 requirements)

---

## Section 1: Consolidation Files Present

### Audit: All Expected Outputs Delivered

Verify each file exists and is accessible:

- [ ] **p_local_001_capture_final.csv** exists
  - File size: _____ bytes (expected: >5KB)
  - Readable as CSV: [ ] Yes [ ] No
  - Contains 9 pole_ids: [ ] Verified [ ] Missing

- [ ] **p_local_001_capture_final.xlsx** exists (if created)
  - File size: _____ bytes (expected: >10KB if present)
  - Readable as XLSX: [ ] Yes [ ] No [ ] Not provided

- [ ] **final_photo_mapping.md** exists
  - File size: _____ bytes (expected: >1KB)
  - Markdown readable: [ ] Yes [ ] No

- [ ] **final_field_review_summary.md** exists
  - File size: _____ bytes (expected: >2KB)
  - Markdown readable: [ ] Yes [ ] No
  - Documents any corrections: [ ] Yes [ ] No

- [ ] **final_validation_report.md** exists
  - File size: _____ bytes (expected: >5KB)
  - Markdown readable: [ ] Yes [ ] No
  - Contains metrics table: [ ] Yes [ ] No

- [ ] **final_validation_report.json** exists
  - File size: _____ bytes (expected: >3KB)
  - Valid JSON: [ ] Yes [ ] No
  - Contains validator metrics: [ ] Yes [ ] No

**If any file is missing:** ❌ STOP. Contact Codex. Mark missing files and halt audit.

---

## Section 2: Pole Structure Inventory Audit

### Audit: All 9 Structures Present and Complete

Open the final CSV and verify all 9 pole_ids exist with complete data:

- [ ] **SPEN-QMM20**
  - Present in CSV: [ ] Yes
  - Data complete (not blank): [ ] Yes
  - Photo reference present: [ ] Yes
  - Audit notes: _____________________

- [ ] **SPEN-NMFSP**
  - Present in CSV: [ ] Yes
  - Data complete (not blank): [ ] Yes
  - Photo reference present: [ ] Yes
  - Audit notes: _____________________

- [ ] **POLE-FIELD-001**
  - Present in CSV: [ ] Yes
  - Data complete (not blank): [ ] Yes
  - Photo reference present: [ ] Yes
  - Audit notes: _____________________

- [ ] **POLE-H-FRAME-RES-001**
  - Present in CSV: [ ] Yes
  - Data complete (not blank): [ ] Yes
  - Photo reference present: [ ] Yes
  - Audit notes: _____________________

- [ ] **POLE-RURAL-ROAD-001**
  - Present in CSV: [ ] Yes
  - Data complete (not blank): [ ] Yes
  - Photo reference present: [ ] Yes
  - Audit notes: _____________________

- [ ] **POLE-RURAL-HEDGE-001**
  - Present in CSV: [ ] Yes
  - Data complete (not blank): [ ] Yes
  - Photo reference present: [ ] Yes
  - Audit notes: _____________________

- [ ] **POLE-VILLAGE-LSTC2021**
  - Present in CSV: [ ] Yes
  - Data complete (not blank): [ ] Yes
  - Photo reference present: [ ] Yes
  - Audit notes: _____________________

- [ ] **POLE-GARDEN-XFMR-001**
  - Present in CSV: [ ] Yes
  - Data complete (not blank): [ ] Yes
  - Photo reference present: [ ] Yes
  - Audit notes: _____________________

- [ ] **POLE-TEE-VEG-001**
  - Present in CSV: [ ] Yes
  - Data complete (not blank): [ ] Yes
  - Photo reference present: [ ] Yes
  - Audit notes: _____________________

**If any pole is missing or incomplete:** ❌ STOP. Note which and halt audit.

---

## Section 3: H-Frame Counting Verification

### Audit: H-Frame Is 1 Structure, 2 Timber Supports (Not Duplicated)

Check the final CSV for POLE-H-FRAME-RES-001 structure:

- [ ] **Single row rule:** POLE-H-FRAME-RES-001 appears as exactly **ONE row** (not two)
  - If present: [ ] 1 row [ ] 2 rows (ERROR)

- [ ] **H-frame notation:** CSV notes or field indicates this is an H-frame/double-support structure
  - Indicator present: [ ] Yes [ ] No

- [ ] **Support count documentation:** Final summary correctly states:
  - "9 pole structures total"
  - "1 H-frame structure (2 individual timber supports)"
  - "= 10 total individual timber supports"
  - Statement present and correct: [ ] Yes [ ] No

**If H-frame is duplicated as 2 rows:** ❌ STOP. Contact Codex for de-duplication.

---

## Section 4: Photo Mapping Audit

### Audit: All Photos Named Specifically, Not Generically, Mapped Per Pole

Review **final_photo_mapping.md** and check:

- [ ] **Non-generic naming:** Photos are named specifically (e.g., `SPEN-QMM20_clear.jpg`, `POLE-FIELD-001_close.jpg`)
  - NOT generic (e.g., `photo_001.jpg`, `image_1.jpg`)
  - Specificity level: [ ] Good [ ] Fair [ ] Poor

- [ ] **Per-pole mapping:** Each pole has explicit photo references
  - All 9 poles listed: [ ] Yes [ ] No
  - Photos mapped to pole_id: [ ] Yes [ ] No
  - Audit notes: _____________________

- [ ] **No orphan treatment:** Photos are not orphaned (unlinked to pole)
  - Orphaned photos reported: [ ] None [ ] Some (count: ____)

- [ ] **No uncertain photos marked as confirmed:**
  - Obscured/uncertain photos correctly marked (not treated as clear evidence)
  - Obscured flags present: [ ] Yes (count: ____) [ ] No [ ] N/A

- [ ] **Photo count validation:**
  - Total photos in mapping: ________
  - Poles with ≥1 photo: ________ / 9 (expected: 9)
  - Missing photos: [ ] None [ ] Some (which: __________)

**If photo mapping has issues:** [ ] Note severity and contact Codex if needed.

---

## Section 5: Specific Pole Corrections Audit

### SPEN-QMM20 Corrections Verification

**Final CSV row for SPEN-QMM20:**

- [ ] **Voltage field:** Correctly states "LV" or "~11kV" or similar low-voltage value
  - Current value: _________________
  - Correct: [ ] Yes [ ] No

- [ ] **Conductor field:** Correctly documents "2 bare" or similar observable feature
  - Current value: _________________
  - Correct: [ ] Yes [ ] No

- [ ] **No HV claim:** Voltage does NOT claim "HV" or "33kV" or "four conductors"
  - Current voltage: _________________
  - HV-free: [ ] Yes [ ] No (ERROR)

- [ ] **Streetlight NOT included:** Wood pole does not incorrectly include streetlight
  - Notes/equipment field: _________________
  - No streetlight misattribution: [ ] Yes [ ] No (ERROR)

- [ ] **Final field review summary:** Documents any corrections made to SPEN-QMM20
  - Corrections documented: [ ] Yes [ ] No

**If corrections not applied:** [ ] Mark as REQUIRES CODEX CORRECTION.

---

### SPEN-NMFSP Corrections Verification

**Final CSV row for SPEN-NMFSP:**

- [ ] **Marking visible:** Pole marking field or notes document visible SPEN/NMFSP/SPH/Q carving
  - Marking notes: _________________
  - Marking documented: [ ] Yes [ ] No

- [ ] **Condition conservative:** Condition field correctly states visual assessment (e.g., "fair", "poor")
  - Current condition: _________________
  - Conservative (not overstated): [ ] Yes [ ] No

- [ ] **No failure claim:** Condition does NOT claim structural failure as unsupported fact
  - Failure flags: [ ] None [ ] Present (ERROR)
  - Safe wording: [ ] Yes [ ] No

- [ ] **Final field review summary:** Documents any corrections made to SPEN-NMFSP
  - Corrections documented: [ ] Yes [ ] No

**If corrections not applied:** [ ] Mark as REQUIRES CODEX CORRECTION.

---

### POLE-GARDEN-XFMR-001 Wording Audit

**Final CSV row for POLE-GARDEN-XFMR-001:**

- [ ] **Access notes field:** Check the `access_notes` or similar field for wording
  - Current wording: _________________________________

- [ ] **Conservative wording:** Wording says "limits" or "blocks" measurement/inspection access
  - Examples: "Vegetation limits clear view of base", "Cannot measure base due to shrubs"
  - Current wording matches conservative pattern: [ ] Yes [ ] No

- [ ] **No DNO access claim:** Wording does NOT claim "DNO cannot access" as absolute fact
  - No DNO impossibility claim: [ ] Yes [ ] No (ERROR)

- [ ] **Evidence-based:** Wording is based on actual field observation, not assumption
  - Evidence-based: [ ] Yes [ ] No

- [ ] **Final field review summary:** Documents any corrections made to POLE-GARDEN-XFMR-001
  - Corrections documented: [ ] Yes [ ] No

**If wording is not conservative:** [ ] Mark as REQUIRES CODEX CORRECTION.

---

### POLE-RURAL-ROAD-001 Inspection Plate Dates Audit

**Final CSV row for POLE-RURAL-ROAD-001:**

- [ ] **Inspection plate date field:** Check if date is filled or marked "unknown"
  - Current value: _________________

- [ ] **Photo visibility:** Date is documented from visible photo evidence, not extrapolation
  - Photo evidence present: [ ] Yes [ ] No
  - Dates legible in photo: [ ] Yes [ ] No (if filled)

- [ ] **Conservative documentation:** Dates are only documented if clearly visible
  - Conservative: [ ] Yes [ ] No

- [ ] **No overstatement:** Field does not claim certainty beyond what photo shows
  - Conservative: [ ] Yes [ ] No

- [ ] **Final field review summary:** Documents any corrections made to POLE-RURAL-ROAD-001
  - Corrections documented: [ ] Yes [ ] No

**If dates are overstated:** [ ] Mark as REQUIRES CODEX CORRECTION.

---

### POLE-VILLAGE-LSTC2021 Photo Status Audit

**Final CSV row for POLE-VILLAGE-LSTC2021:**

- [ ] **Photo mapping confirmed:** Photo reference(s) present and linked
  - Photos linked: [ ] Yes [ ] No
  - Count: ________

- [ ] **Photo quality:** Photos are readable and relevant to pole
  - Quality acceptable: [ ] Yes [ ] No

- [ ] **Status documented:** CSV indicates photo mapping status (complete/provisional/requires_review)
  - Status field: _________________
  - Appropriately marked: [ ] Yes [ ] No

- [ ] **Final field review summary:** Documents photo mapping status for POLE-VILLAGE-LSTC2021
  - Documentation present: [ ] Yes [ ] No

**If photo mapping is incomplete:** [ ] Mark as PROVISIONAL (note in final verdict).

---

## Section 6: High-Risk Fields Remain Unknown/Review-Required Audit

### Audit: No Forced Filling of Genuinely Unknown Fields

Review the final CSV for 8 high-risk fields. Each should be either filled with confidence OR marked "unknown" / "verification_required":

| Field | Pole(s) | Expected Status | Actual Status | Correct? |
|-------|---------|-----------------|---------------|----------|
| voltage_carried | Multiple | Unknown/Estimated | ________________ | [ ] |
| conductor_size | Multiple | Unknown/Observable only | ________________ | [ ] |
| phase_configuration | Multiple | Inferred/Unknown | ________________ | [ ] |
| pole_class | Multiple | Visual estimate OK | ________________ | [ ] |
| pole_strength | Multiple | Unknown expected | ________________ | [ ] |
| measured_height | Multiple | Unknown if not measured | ________________ | [ ] |
| transformer_rating | SPEN-NMFSP, POLE-GARDEN-XFMR-001 | Unknown unless visible | ________________ | [ ] |
| specification | Multiple | Blank/Unknown acceptable | ________________ | [ ] |

**Audit rule:** Unknown = ✅ CORRECT. Honest uncertainty is the right operator behavior.

**Issues found:**
- [ ] All fields appropriately handled
- [ ] Some fields forced-filled (list): _____________________
- [ ] Some fields overstated (list): _____________________

**If forced-filled or overstated:** [ ] Mark as REQUIRES CODEX REVIEW.

---

## Section 7: Validator Result Review

### Audit: Validator Metrics Recorded in Final Report

Review **final_validation_report.md** and **final_validation_report.json** for metrics:

- [ ] **Valid rows count:** _________ % (expected: ≥85% for PASS, 75–85% for PARTIAL)
  - Acceptable: [ ] Yes (PASS) [ ] Yes (PARTIAL) [ ] No

- [ ] **Review-required rows count:** _________ % (expected: 30–50%)
  - Pattern reasonable: [ ] Yes [ ] No

- [ ] **Merge-ready rows count:** _________ % (expected: 10–30%)
  - Pattern reasonable: [ ] Yes [ ] No

- [ ] **Blocked rows count:** _________ % (expected: 0–5%)
  - Acceptable: [ ] Yes [ ] No

- [ ] **Missing photos:** _________ (expected: 0)
  - Correct: [ ] Yes [ ] No

- [ ] **Orphaned photos:** _________ (expected: 0)
  - Correct: [ ] Yes [ ] No

- [ ] **Duplicate pole_ids:** _________ (expected: 0)
  - Correct: [ ] Yes [ ] No

- [ ] **Overall validator verdict:** _________ (expected: PASS or PARTIAL)
  - Acceptable: [ ] Yes [ ] No

**If metrics show failures:** [ ] Note and include in audit findings.

---

## Section 8: Final Verdict Selection Readiness

### Audit: Readiness for Noel to Record Final Verdict

Verify that all information is ready for Noel to select final verdict:

- [ ] **All 9 structures verified:** [ ] Yes
- [ ] **H-frame counted correctly:** [ ] Yes
- [ ] **Photo mapping complete/documented:** [ ] Yes
- [ ] **Corrections applied:** [ ] Yes (or noted as provisional)
- [ ] **High-risk fields handled conservatively:** [ ] Yes
- [ ] **Validator result clear:** [ ] Yes

**Audit summary for verdict selection:**
- Ready for PASS verdict: [ ] Yes [ ] No (why: _______________)
- Ready for PARTIAL verdict: [ ] Yes [ ] No (why: _______________)
- Must be NO-GO verdict: [ ] Yes (why: ________________) [ ] No

---

## Section 9: Stage 4C Block Confirmation

### Audit: P_LOCAL_001 Does Not Authorize Stage 4C

Final confirmation before releasing result record:

- [ ] **Result template includes explicit Stage 4C block statement:** [ ] Yes
- [ ] **Noel understands:** P_LOCAL_001 proves field-capture workflow, NOT Stage 4C approval
- [ ] **Phase 4 requirement acknowledged:** Baseline + same-site field evidence + exact match ≥80% required
- [ ] **Audit confirms:** Stage 4C remains BLOCKED

**Final audit statement:**
- P_LOCAL_001 is field-capture validation evidence ✅
- P_LOCAL_001 is NOT Stage 4C authorization evidence ✅
- Stage 4C is BLOCKED pending Phase 4 ✅

---

## Audit Completion Checklist

Before releasing the audit:

- [ ] All 9 sections completed
- [ ] No files missing (Section 1)
- [ ] All 9 poles verified (Section 2)
- [ ] H-frame counted correctly (Section 3)
- [ ] Photo mapping audited (Section 4)
- [ ] Specific pole corrections verified (Section 5)
- [ ] High-risk fields reviewed (Section 6)
- [ ] Validator metrics recorded (Section 7)
- [ ] Final verdict readiness confirmed (Section 8)
- [ ] Stage 4C block re-confirmed (Section 9)

**Audit verdict:**
- [ ] **READY FOR NOEL REVIEW** — All checks passed; Noel can now fill result template and select final verdict
- [ ] **PROVISIONAL RELEASE** — Some items noted; document exceptions in result template
- [ ] **HOLD — REQUIRES CODEX CORRECTION** — Issues found; specify which sections above require fixes

**Audit summary for handoff:**
_________________________________________________________________

---

## Reference

- **Doc 91:** P_LOCAL_001 Field-Capture Result Template (verdict form)
- **Doc 92:** P_LOCAL_001 Final Review Checklist (Noel's review checklist)
- **Doc 89:** P_LOCAL_001 Field-Capture Review (classification)
- **Doc 90:** Field-Capture vs. Baseline Merge Gap (Phase 4 requirements)
