# Field-Capture vs. Baseline Merge Gap

**For: Understanding what P_LOCAL_001 contributes and what remains before Stage 4C**

**Date:** 2026-05-12
**Purpose:** Clear gap analysis between current field evidence and Stage 4C authorization requirements
**Authority:** Documents 73–85, 87–88
**Scope:** Comparison of baseline files, field evidence, and future pilot; sequencing recommendation

---

## Three Evidence Sources: Comparison

### 1. Real Baseline Conversion Files (Bellsprings/Gordon)

**What they are:**
- Raw Trimble controller CSVs from historical surveys
- Design PDFs from office work
- Multiple points per pole; CRS transformations required

**What they provide:**
- Reference coordinates
- Authoritative pole_ids
- Baseline field attributes (voltage, equipment)
- Design context

**What they lack:**
- Current field condition
- Photos/evidence
- Operator observation
- Pole_id match verification

**Classification:** Baseline conversion evidence (Phase 1 input)

---

### 2. Local Field Evidence (P_LOCAL_001)

**What it is:**
- Noel's real 2026-05-11 local pole survey
- 30+ poles with photos
- Operator-completed observations
- Local/accessible (no baseline reference)

**What it provides:**
- Proof field capture works
- Proof operator can observe/document
- Real field condition assessment
- Proof evidence linking works
- Honest uncertainty handling

**What it lacks:**
- Independent baseline to compare against
- Exact pole_id match rate (no baseline comparison)
- Baseline field attributes to validate against
- GO/NO-GO verdict authority

**Classification:** Field-capture validation evidence (Phase 2 proof)

---

### 3. Future Full Controlled Pilot (Phase 4)

**What it will be:**
- Noel captures poles FROM a real baseline (Bellsprings or P_CONTROLLED_001)
- Both baseline AND field evidence present
- Exact pole_id matching possible
- Validator can calculate match rate

**What it will provide:**
- Baseline-field alignment proof
- Exact pole_id match rate (≥80% = GO)
- Confidence in merge safety
- Operator verdict authority
- Gate auditor approval pathway

**What it requires:**
- Accessible baseline + field evidence from same site
- Validator PASS/PARTIAL acceptance
- Noel's signed decision template
- Independent gate auditor
- All three pieces (baseline, field, validator) present

**Classification:** Stage 4C approval evidence (Phase 4)

---

## The Remaining Gap

### What P_LOCAL_001 Proves

✅ Field-capture workflow is executable
✅ Operator can document field realities
✅ Photo evidence can be organized and linked
✅ Validator runs successfully on real field data
✅ Unknown/uncertain fields can be documented honestly

### What P_LOCAL_001 Does NOT Prove

❌ Baseline-field alignment (no baseline to compare)
❌ Exact pole_id matching (no independent reference)
❌ Match rate ≥80% (no comparison possible)
❌ Merge algorithm safety (no actual merge test)
❌ Database integration readiness (no runtime code involved)

### The Gap (What's Missing for Stage 4C)

**To authorize Stage 4C, we need:**
1. Real baseline CSV (Bellsprings, Gordon, or equivalent)
2. Field evidence FROM THAT BASELINE (Noel captures same poles)
3. Validator comparison of baseline vs. field pole_ids
4. Exact match rate ≥80% (GO threshold)
5. Noel's signed verdict (GO / CONDITIONAL GO / NO-GO)
6. Gate auditor confirmation

**P_LOCAL_001 provides:** #2 (field-capture workflow proof)
**Missing:** #1 (baseline CSV for comparison), #3–6 (validation, verdict, approval)

**Example:**
```
P_LOCAL_001 says: "I can capture field data, here are 30 poles, photos linked, validator runs"
Stage 4C asks: "Can you capture field data that matches a real baseline with ≥80% exact pole_id?"
P_LOCAL_001 answers: "Yes, workflow works. But I have no baseline to compare against"
Stage 4C says: "Then bring baseline + field evidence, we'll measure the match, and if ≥80%, approve"
```

---

## Why P_LOCAL_001 Is Still Valuable

**P_LOCAL_001 proves the hardest part works: operator field execution.**

For Phase 4, Noel will need to:
- Capture same poles in field as in baseline
- Identify each pole (baseline pole_id vs. physical label)
- Photograph evidence
- Fill observations
- Handle unknowns/access constraints

**P_LOCAL_001 already proved all of this is possible.** Not theoretically. Actually. Noel did it.

**Lessons from P_LOCAL_001:**
- Operator took ~10–15 min per pole (matches field pack estimate)
- Photos can be organized cleanly (evidence linking works)
- Unknown fields can be documented (no forced filling)
- Difficult access is manageable (documented constraints)
- Validator processes real field data successfully

**These lessons reduce Phase 4 risk dramatically.**

---

## How P_LOCAL_001 Lessons Should Feed Into Future Controlled Baseline Pilot

### Pre-Phase 4 Preparation

**From P_LOCAL_001, we learned:**
1. Operator can sustain 30+ poles in single day ✓
2. Photo naming protocol works ✓
3. Validation workflow completes ✓
4. Unknown fields are handled cleanly ✓

**Implications for Phase 4:**
- 34-pole target is realistic (P_LOCAL_001 = 30–33 poles)
- Fallback 15-pole option is feasible
- Equipment (camera, device, chargers) requirements proven
- Field pack documentation sufficient

### Phase 4 Specific Preparation

**Lessons from P_LOCAL_001 to apply:**

1. **Voltage field challenges:** P_LOCAL_001 showed voltage difficult to observe (nameplate often illegible). Phase 4 guide should prepare Noel: "Voltage field is often blank or estimated; mark verification_required=yes if unsure"

2. **Unknown field patterns:** If P_LOCAL_001 shows >20% unknowns in specific fields (e.g., stays_count, pole_strength), Phase 4 should acknowledge this is normal and acceptable

3. **Access constraints:** If P_LOCAL_001 documented poles impossible to access, Phase 4 baseline selection should avoid similar geographies

4. **Photo quality issues:** If P_LOCAL_001 had obscured photos due to vegetation/lighting, Phase 4 site selection should consider lighting angles and seasonal vegetation

5. **Operator friction:** If P_LOCAL_001 identified template clarity issues, Phase 4 can fix those before baseline selection

---

## Recommended Next Sequencing After Codex Finishes

### Step 1: Review P_LOCAL_001 Validator Result (Codex/Noel)

**Timeline:** After Codex validation complete
**Action:** Review pilot_validation_report.md
**Check:**
- Valid rows ≥85% (expected: yes)
- Review-required rows 30–50% (expected: yes)
- Blocked rows 0–5% (expected: yes)
- Missing photos 0 (expected: yes)
- Evidence coverage ≥90% (expected: yes)

**Outcome:** PASS or PARTIAL acceptable. Record in validation log.

---

### Step 2: Noel Manually Reviews High-Risk Inferred Fields (Noel)

**Timeline:** Immediately after Step 1
**Action:** Spot-check 5–10 poles for fields marked "unknown" or "inferred"
**Focus:** voltage_carried, conductor_size, phase_configuration, pole_class, stay_required
**Record:** In decision memo (doc 82 equivalent) if field patterns seem systematically off

**Outcome:** Lessons document any operator training needs for Phase 4

---

### Step 3: Record P_LOCAL_001 Result (Claude Code)

**Timeline:** After Step 2
**Action:** Create governance record (similar to P_REAL_001_MINI result record)
**Includes:**
- Validator verdict (PASS/PARTIAL)
- Operator assessment (any friction, confidence, unknowns)
- Lessons learned (what Phase 4 should prepare for)
- Classification (field-capture validation evidence, NOT Stage 4C approval)

**Outcome:** Permanent project record that P_LOCAL_001 proved field-capture workflow

---

### Step 4: Compare P_LOCAL_001 Fields Against Bellsprings/Gordon Baseline Fields (Codex)

**Timeline:** After Steps 1–3
**Action:** Extract baseline field attributes from Bellsprings/Gordon; compare against P_LOCAL_001 observations
**Compare:**
- Baseline voltage vs. P_LOCAL_001 voltage observations (close match? discrepancies?)
- Baseline equipment vs. P_LOCAL_001 equipment observations
- Baseline structure type vs. P_LOCAL_001 pole_type observations

**Outcome:** Learning about field observation accuracy relative to baseline assumptions

---

### Step 5: Find or Arrange Accessible Same-Site Baseline+Photo Pilot (Noel/Codex)

**Timeline:** After Step 4
**Action:** Identify a real baseline (Bellsprings, Gordon, or equivalent) where Noel can capture field evidence
**Requirements:**
- Real baseline CSV available and accessible
- Poles physically accessible to Noel (no trespassing, safe access)
- 30–50 pole target achievable
- Geographic clustering (same area/region)

**Candidates:**
- Bellsprings (if accessible and location known)
- Gordon Pt1 (if accessible)
- P_CONTROLLED_001 (if baseline CSV available and site accessible)
- Other real baseline (TBD if discovered)

**Outcome:** Baseline + field evidence ready for Phase 4 (Stage 4C authorization pilot)

---

### Step 6: Execute Phase 4 Controlled Baseline Pilot (Phase 4)

**Timeline:** After Step 5
**Action:** Noel captures 34 (or 15 fallback) poles FROM chosen baseline
**Baseline:** Real baseline CSV (Bellsprings, Gordon, or P_CONTROLLED_001)
**Field:** Noel's observations + photos
**Validator:** Exact pole_id matching, match rate calculation
**Verdict:** Noel signs decision template (GO / CONDITIONAL GO / NO-GO)
**Approval:** If GO/CONDITIONAL GO + gate audit → Stage 4C implementation authorized

**Outcome:** Stage 4C authorization (or NO-GO analysis if issues found)

---

## Critical Point: P_LOCAL_001 Enables Phase 4, Does Not Replace It

```
P_LOCAL_001 outcome: "Field capture is feasible. Operator proved it."

Phase 4 question: "But does field evidence match a real baseline ≥80%?"

P_LOCAL_001 cannot answer: "I have no baseline to compare"

Only Phase 4 can answer: "Yes, baseline + field match 34/34, exact match 97%"
```

**Therefore:**
- P_LOCAL_001 is a prerequisite for Phase 4 confidence
- P_LOCAL_001 is NOT sufficient for Stage 4C authorization
- Phase 4 is still required and essential

---

## Summary Table

| Aspect | Bellsprings/Gordon Baseline | P_LOCAL_001 Field | Phase 4 Full Pilot |
|--------|---|---|---|
| **Provides** | Reference coords, pole_ids | Field evidence, photos | Baseline + field + match rate |
| **Proves** | Baseline exists and transforms | Capture workflow works | Baseline-field alignment |
| **Authorizes** | Nothing (learning only) | Nothing (proof only) | **Stage 4C implementation** |
| **Required for Stage 4C** | Yes (baseline must exist) | Yes (field must match) | **Yes (both + match + verdict)** |
| **Currently available** | Yes | Yes | No (Phase 4 must be done) |

---

## Reference

- **Doc 88:** Baseline vs. Field Evidence (why both required)
- **Doc 89:** P_LOCAL_001 Field-Capture Review (what P_LOCAL_001 proves)
- **Doc 85:** Post-Field Acceptance Gate (Phase 4 GO/NO-GO criteria)
- **Doc 87:** Real Survey Pack Readiness (baseline file classification)
