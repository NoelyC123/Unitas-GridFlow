# P_LOCAL_001 Field-Capture Result Record Template

**For: Recording the final governance verdict on P_LOCAL_001 as field-capture validation evidence**

**Date:** *to be filled on completion*
**Authority:** Documents 89–90 (field-capture review and baseline-merge gap analysis)
**Purpose:** Create a permanent project record of what P_LOCAL_001 proves and does not prove
**Status:** **TEMPLATE (not yet filled)**

---

## Pilot Metadata

| Item | Value |
|------|-------|
| Pilot name | P_LOCAL_001 |
| Pilot type | Local accessible field-capture validation proof |
| Survey date | 2026-05-11 |
| Operator | Noel Collins |
| Location | Local area (accessible, non-proprietary) |
| Authority source | Field observation (Noel operator assessment) |
| Classification | Stage 4 field-capture evidence (NOT Stage 4C approval) |
| Document status | *pending Codex consolidation completion* |

---

## Source Files Expected

**To be completed after Codex finishes consolidation.**

| File | Path | Purpose | Status |
|------|------|---------|--------|
| Pilot CSV | `real_pilot_data/P_LOCAL_001/csv/P_LOCAL_001.csv` | Field observations + metadata | *pending* |
| Photos (evidence) | `real_pilot_data/P_LOCAL_001/photos_final/` | Pole photo evidence organized by pole_id | *pending* |
| Validator report (JSON) | `validation_runs/stage4_pilots/P_LOCAL_001_FINAL/pilot_validation_report.json` | Machine-readable metrics | *pending* |
| Validator report (MD) | `validation_runs/stage4_pilots/P_LOCAL_001_FINAL/pilot_validation_report.md` | Human-readable summary | *pending* |
| Evidence audit (JSON) | `validation_runs/stage4_pilots/P_LOCAL_001_FINAL/evidence_audit.json` | Photo linking details | *pending* |

---

## Pole Structure Count

**Final count (to be confirmed after Codex consolidation):**

- **Total pole structures:** *pending* (expected: 9)
- **Individual timber supports:** *pending* (expected: 10 if H-frame counted as two physical poles)
- **Note on counting:** The H-frame (POLE-H-FRAME-RES-001) is a single structure but comprises two physical timber supports. Reporting should specify: "9 structures, including 1 H-frame with 2 timber supports" = "9 structures, 10 individual timber supports total."

**Structures expected:**
1. SPEN-QMM20
2. SPEN-NMFSP
3. POLE-FIELD-001
4. POLE-H-FRAME-RES-001 (2 timber supports)
5. POLE-RURAL-ROAD-001
6. POLE-RURAL-HEDGE-001
7. POLE-VILLAGE-LSTC2021
8. POLE-GARDEN-XFMR-001
9. POLE-TEE-VEG-001

---

## Photo Evidence Count

| Category | Count | Status |
|----------|-------|--------|
| Total photos taken | *pending* | *pending* |
| Photos with valid naming | *pending* | *pending* |
| Poles with ≥1 photo | *pending* (expected: all 9) | *pending* |
| Poles missing photos | *pending* (expected: 0) | *pending* |
| Orphaned photos (unlinked to pole) | *pending* (expected: 0) | *pending* |
| Evidence coverage % | *pending* (expected: ≥90%) | *pending* |

---

## Validator Result Section

**Status:** *pending Codex validator run completion*

### Quantitative Metrics

| Metric | Expected | Actual | Status |
|--------|----------|--------|--------|
| Valid rows (schema + required fields) | ≥85% | *pending* | *pending* |
| Review-required rows | 30–50% | *pending* | *pending* |
| Merge-ready rows | 10–30% | *pending* | *pending* |
| Blocked rows | 0–5% | *pending* | *pending* |
| Missing photos | 0 | *pending* | *pending* |
| Orphaned photos | 0 | *pending* | *pending* |
| Duplicate pole_ids | 0 | *pending* | *pending* |

### Validator Verdict

- **Overall result:** *pending* (expected: PASS or PARTIAL)
- **Validator verdict explanation:** *to be filled from pilot_validation_report.md*
- **Command run:** `python scripts/validate_stage4_pilot.py --csv real_pilot_data/P_LOCAL_001/csv/P_LOCAL_001.csv --evidence-dir real_pilot_data/P_LOCAL_001/photos_final/ --pilot-name P_LOCAL_001 --out validation_runs/stage4_pilots/P_LOCAL_001_FINAL`

---

## Operator Review-Required & Blocked Rows

### High-Risk Inferred Fields (Noel Manual Review)

**Instruction:** After validator run, Noel should spot-check these high-risk fields on 5–10 poles:

| Field | Risk | Spot-Check Action |
|-------|------|-------------------|
| `voltage_carried` | High | Spot-check 5–10 poles; flag if pattern wrong |
| `conductor_size` | High | Verify against photo detail if visible |
| `phase_configuration` | Medium | Verify single-phase vs. 3-phase matches equipment |
| `pole_class` | Medium | Confirm obvious classes (H/M/S) |
| `pole_strength` | Medium | Accept uncertainty; mark as review-required |
| `stay_required` | Medium | Accept obscured photos; expect uncertainty |
| `specification` | Low | Acceptable if blank or inferred |
| `defect_severity` | Low | Observable visual assessment OK |

**Noel's Review Notes:**
*to be filled after manual spot-check*

---

## Specific Technical Confirmations

**Before marking PASS verdict, Noel must manually confirm these field findings:**

### SPEN-QMM20 Voltage Classification

- **Field finding:** LV with two bare conductors (per Noel field observation)
- **Status:** *to be confirmed after review*
- **Note:** This is Noel's operator assessment, not surveyor certification. Spot-check photo against pole equipment.

### SPEN-QMM20 Streetlight Mounting Clarification

- **Field question:** Does SPEN-QMM20 incorrectly include streetlight mounted on wood pole?
- **Expected answer:** NO — photo evidence should show no streetlight, or if present, correctly separated from pole attribution.
- **Status:** *to be confirmed after photo review*

### POLE-GARDEN-XFMR-001 Vegetation Access Limits

- **Field finding:** Vegetation limits/blocks inspection access
- **Critical wording:** "limits access" or "blocks access for specific measurement" — NOT "impossible DNO access"
- **Status:** *to be confirmed*
- **Impact:** High-risk field; must be worded conservatively to avoid overstating access constraints.

### POLE-RURAL-ROAD-001 Inspection Plate Dates

- **Field question:** Are inspection plate dates documented correctly without overstatement?
- **Expected finding:** Dates observable from photo; no extrapolation beyond what visible
- **Status:** *to be confirmed*

### POLE-VILLAGE-LSTC2021 Photo Mapping

- **Field question:** Is photo mapping status correct? All required photos present?
- **Expected:** All pole_ids linked with ≥1 valid photo
- **Status:** *to be confirmed*

---

## Known Limitations

P_LOCAL_001 is valuable AND limited. Permanent record:

### What P_LOCAL_001 Proves ✅

✅ **Field-capture workflow is executable:** Operator can capture 9+ poles in a single field session
✅ **Template schema works in practice:** Operator filled all required fields without forcing unknown values
✅ **Photo evidence linking is feasible:** Photos successfully organized and named by pole_id
✅ **Validator processes real field data:** Validator runs successfully on real field CSV
✅ **Unknown/uncertain handling is clean:** Operator documents unknowns honestly; validator accepts partial data

### What P_LOCAL_001 Does NOT Prove ❌

❌ **Baseline-field pole_id matching:** No independent baseline to compare against
❌ **Exact match rate:** Cannot calculate match % without reference baseline
❌ **≥80% threshold:** Cannot demonstrate GO decision criterion (requires Phase 4)
❌ **Merge algorithm safety:** Validator only confirms schema; does not test merge logic
❌ **Database integration:** No Stage 4C runtime code involved
❌ **Stage 4C authorization:** Field evidence alone is insufficient; Phase 4 (baseline+field combined) required

---

## Operator Review Notes

**Section for Noel to document:**

- Overall workflow experience: *to be filled*
- Friction points encountered: *to be filled*
- Unexpected easy/hard tasks: *to be filled*
- Lessons for Phase 4 baseline pilot: *to be filled*
- Confidence assessment (1–5): *to be filled*
- Suggestions for template improvement: *to be filled*

---

## Final Verdict Section

**Status:** *PENDING — to be filled only after Codex consolidation and validator completion*

### Verdict Options

Choose ONE:

#### ✅ PASS AS FIELD-CAPTURE EVIDENCE

**Conditions for PASS:**
- Valid rows ≥85%
- Blocked rows ≤5%
- Missing photos = 0
- Orphaned photos = 0
- Noel spot-check confirms no systematic field errors
- All 9 pole structures present with correct naming
- H-frame counted correctly (1 structure, 2 timber supports)

**Verdict:**
- [ ] **PASS** — P_LOCAL_001 successfully proves field-capture workflow is executable. Validator result acceptable. Operator confident. Proceed to Phase 4.

---

#### ⚠️ PARTIAL AS FIELD-CAPTURE EVIDENCE

**Conditions for PARTIAL:**
- Valid rows 75–85%
- Blocked rows 5–10%
- Review-required rows >50% (common for real field data)
- Validator returns PARTIAL verdict (acceptable for learning)
- Noel spot-check finds specific field patterns that may need Phase 4 adjustment
- All 9 structures present but some with photo or naming issues
- H-frame counting verified but with minor uncertainties

**Verdict:**
- [ ] **PARTIAL** — P_LOCAL_001 proves field-capture workflow is workable with operator training adjustments. Validator result acceptable for learning. Proceed to Phase 4 with noted improvements.
- **Remediation notes:** *to be filled*

---

#### ❌ NO-GO FIELD-CAPTURE EVIDENCE

**Conditions for NO-GO:**
- Valid rows <75%
- Blocked rows >10%
- Missing poles or photos
- Orphaned photos present
- Validator returns FAIL verdict
- Noel spot-check finds systematic field errors
- H-frame counting incorrect
- Systematic issue preventing workflow reuse

**Verdict:**
- [ ] **NO-GO** — P_LOCAL_001 reveals workflow/schema issues requiring rework before proceeding to Phase 4.
- **Root cause:** *to be filled*
- **Recommended remediation:** *to be filled*

---

## Explicit Statement: Stage 4C Authorization Status

### Does P_LOCAL_001 Authorize Stage 4C Implementation?

**ANSWER: NO**

**Reason:**
- P_LOCAL_001 is field-capture evidence WITHOUT baseline comparison
- Exact pole_id matching is impossible (no baseline to compare against)
- Cannot calculate match rate or demonstrate ≥80% threshold
- Cannot prove merge algorithm safety
- Cannot satisfy Stage 4C authorization criteria

### What IS Required for Stage 4C Authorization?

**Phase 4 Full Controlled Baseline + Field Evidence Pilot:**

1. **Real baseline CSV** (Bellsprings, Gordon, or P_CONTROLLED_001)
2. **Field evidence FROM THAT BASELINE** (Noel captures same poles)
3. **Validator exact-match comparison** (baseline pole_id vs. captured pole_id)
4. **Exact match rate ≥80%** (GO decision threshold)
5. **Noel's signed decision template verdict** (GO / CONDITIONAL GO / NO-GO)
6. **Independent gate auditor confirmation**

**P_LOCAL_001's contribution:** Proves field-capture workflow is feasible and operator is capable (items 1–2 prerequisites)

**P_LOCAL_001 does NOT provide:** Items 3–6 (matching, comparison, verdict, approval)

### Stage 4C Authorization Pathway

```
P_LOCAL_001: "Field capture works"
    ↓
Phase 4 Required: "Can field evidence match a real baseline ≥80%?"
    ↓
If Phase 4 → PASS with ≥80% match + signed verdict
    ↓
THEN → Stage 4C authorization is granted
```

**Current status: BLOCKED** ← awaiting Phase 4 controlled baseline pilot

---

## Review Trail

| Reviewer | Date | Verdict | Notes |
|----------|------|---------|-------|
| Noel Collins | *to be filled* | *to be filled* | Operator assessment |
| Codex | *to be filled* | *to be filled* | Validator completion |
| Gate Auditor | *if required* | *if required* | Independent confirmation |

---

## Reference

- **Doc 89:** P_LOCAL_001 Field-Capture Review (what P_LOCAL_001 proves)
- **Doc 90:** Field-Capture vs. Baseline Merge Gap (Phase 4 requirements)
- **Doc 88:** Baseline vs. Field Evidence Decision Memo (authorization pathway)
- **Doc 85:** Post-Field Acceptance Gate (general Phase 4 criteria)
- **Validator command:** `python scripts/validate_stage4_pilot.py`
