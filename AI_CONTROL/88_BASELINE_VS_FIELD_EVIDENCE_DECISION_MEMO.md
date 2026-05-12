# Baseline vs. Field Evidence Decision Memo

**For: Understanding the relationship between survey baseline, field-capture pilots, and Stage 4C authorization**

**Date:** 2026-05-12
**Purpose:** Clarify why we need both baseline data AND field evidence, and how they combine for Stage 4C approval
**Authority:** Documents 73–85 (Controlled Baseline Pilot framework, exact pole_id protocol, acceptance gates)
**Scope:** Pilot sequencing recommendation, evidence combination, Stage 4C authorization pathway

---

## Three Different Pilots: What Each Proves

### Pilot Type 1: Baseline Conversion Pilot

**What it is:**
- Codex takes Bellsprings or Gordon raw survey CSV
- Applies coordinate transformation, de-duplication, field mapping
- Generates a starter CSV with 30–50 unique poles
- No field capture; no field photos; no Noel involvement yet

**What it proves:**
- ✅ Baseline extraction logic works
- ✅ Raw survey schema is understood
- ✅ Coordinate transformation is correct
- ✅ Starter CSV is valid and usable

**What it does NOT prove:**
- ❌ Exact pole_id matching with field observation
- ❌ Field photos can be linked to baseline poles
- ❌ Validator will accept the data for merge
- ❌ Stage 4C is ready to go

**Example:**
```
Codex: "I have a Bellsprings baseline CSV with 40 poles, coordinate-transformed to WGS84,
with pole_ids mapped to design labels. This starter CSV is ready for field use."

Status: Useful for Stage 4 planning, but NOT approval.
```

---

### Pilot Type 2: Local Field-Capture Pilot

**What it is:**
- Noel does a local field survey (e.g., the 2026-05-11 local survey)
- Captures ~30–50 local poles with photos and observations
- Does NOT compare against an existing baseline
- Records what he sees, where he is, what he captures

**What it proves:**
- ✅ Field-capture workflow is feasible
- ✅ Template schema works in practice
- ✅ Operator can fill in observations
- ✅ Photo evidence can be organized by pole

**What it does NOT prove:**
- ❌ Exact pole_id matching against a baseline
- ❌ Validator acceptance criteria
- ❌ Merge algorithm readiness
- ❌ Stage 4C authorization

**Example:**
```
Noel: "I captured 30 local poles, took photos, filled the template. Here's my local CSV."

Status: Demonstrates field capture works, but NOT authoritative for Stage 4C (no baseline match).
```

---

### Pilot Type 3: Controlled Baseline + Field Evidence Pilot (Full Pilot)

**What it is:**
- Noel takes a prepared baseline CSV (from Pilot 1 OR a fresh baseline like P_CONTROLLED_001)
- Noel goes to the field and captures the SAME poles against that baseline
- For each baseline pole: Noel confirms the pole, takes photos, records condition, equipment
- Validator compares captured pole_ids to baseline pole_ids
- Calculates exact match rate (≥80% = GO, 75–80% = CONDITIONAL GO, <75% = NO-GO)
- Noel fills decision template with verdict

**What it proves:**
- ✅ Baseline-field alignment works
- ✅ Exact pole_id matching is possible (or reveals mismatch)
- ✅ Field photos are correctly linked to baseline poles
- ✅ Validator accepts the combined dataset
- ✅ Operator confidence in the data is high
- ✅ Stage 4C authorization criteria can be evaluated

**What it STILL does not prove:**
- ❌ Stage 4C is automatically enabled (authorization requires signed verdict)
- ❌ Merge algorithm works end-to-end (that comes next)
- ❌ Real-time upload works (that's a separate implementation)

**Example:**
```
Noel: "I captured 34 poles against the Bellsprings baseline. 33/34 exact match (97%).
All photos linked. Operator confidence = 5. Signing GO on decision template."

Status: AUTHORIZES Stage 4C implementation task to start.
```

---

## Why You Need Both Baseline AND Field Evidence

### Problem: Baseline Alone

```
Scenario: Codex extracts a beautiful baseline CSV with 50 poles,
         coordinates perfectly transformed, all labels mapped.

Question: Does this baseline actually match the field?

Answer: We don't know. The baseline is months old. Poles might be demolished.
        Transformers might have been replaced. Labels might be worn off.
        We can't know without going to the field.
```

**Lesson:** Baseline proves only that surveyor data *existed*. It doesn't prove that baseline is suitable for *today's field*.

---

### Problem: Field Evidence Alone

```
Scenario: Noel captures 30 local poles, fills the template, takes photos.

Question: Do these field observations match an accessible baseline?

Answer: We don't know which baseline (if any) these poles belong to.
        Are they Bellsprings? Gordon? Some other job?
        Without baseline coordinates to compare, we can't calculate match rate.
        We can't use the validator's exact-match logic.
```

**Lesson:** Field evidence proves only that field capture *works*. It doesn't prove that the captured data can be *merged* into a baseline.

---

### Solution: Baseline + Field Evidence Together

```
Scenario: Noel captures 34 poles FROM the Bellsprings baseline.
         - Bellsprings baseline = reference coordinates + pole_ids
         - Noel's field data = observed pole_ids + photos + condition
         - Validator compares baseline pole_id vs. captured pole_id
         - Result: 97% exact match rate

Question: Can this data be merged into design work?

Answer: YES, with the conditions met:
        ✅ Exact match rate high (97% > 80% threshold)
        ✅ Validator confirms valid rows, merge-ready rows
        ✅ Operator confidence high
        ✅ Photo evidence linked
        ✅ Noel signs GO verdict
        → Stage 4C implementation can proceed
```

**Lesson:** Only when baseline and field evidence are combined CAN WE KNOW that poles match, data is reliable, and operator is confident.

---

## Why Noel's Local Field CSV Is Valuable (But Not Sufficient)

### What Noel's 2026-05-11 Survey Demonstrates

```
pole_id         | observed_type | observed_condition | observed_equipment | photo_count | notes
P009-LOCAL-001  | wooden        | good               | transformer        | 2           | clear field access
P009-LOCAL-002  | concrete      | fair               | switch             | 3           | vegetation blocked base
...
```

**Valuable because:**
1. ✅ Proves Noel can capture full template rows
2. ✅ Proves photos can be organized by pole
3. ✅ Proves field observations are possible
4. ✅ Provides baseline for field-capture training

**Not sufficient because:**
1. ❌ No baseline CSV to compare against
2. ❌ Pole_ids are local (P009-LOCAL-001) with no known baseline equivalent
3. ❌ Cannot calculate exact-match rate (against what baseline?)
4. ❌ Validator cannot run without a reference baseline
5. ❌ Cannot prove Stage 4C acceptance criteria

---

## Why Bellsprings/Gordon Baseline Files Are Valuable (But Not Sufficient)

### What Bellsprings/Gordon Baseline Demonstrates

```
Raw survey extract:
point_number   | lat           | lon          | crs       | voltage | type
1001           | 54.123456     | -2.987654    | TM65      | 11kV    | Wooden
1002           | 54.123789     | -2.987890    | TM65      | 11kV    | Concrete
...
```

**Valuable because:**
1. ✅ Provides authoritative pole locations (from original survey)
2. ✅ Gives baseline voltage/equipment (reference for comparison)
3. ✅ Enables coordinate transformation (real-world CRS conversion)
4. ✅ Supports baseline-field matching (once field evidence collected)

**Not sufficient because:**
1. ❌ No field evidence (no photos, no current condition)
2. ❌ Baseline is historical (could be months old)
3. ❌ Cannot prove poles still match physical reality
4. ❌ Cannot validate current condition or accessibility
5. ❌ Cannot prove Stage 4C acceptance criteria

---

## Recommended Project Sequencing

### Phase 1: Baseline Conversion Learning (Can start now)

**Task:** Codex converts Bellsprings (or another real baseline) using the prepared baseline extraction workflow.

**Deliverables:**
- Baseline extraction script (with configurable column mapping)
- Bellsprings starter CSV (30–50 poles, WGS84 coordinates, design pole_ids mapped)
- Extraction notes (survey date, source CRS, transformation method, any issues)
- Baseline readiness assessment (coordinate verification, design PDF cross-check, pole-label authority)

**Approval gate:** Independent review confirms:
- ✅ Starter CSV schema is correct
- ✅ Coordinates are plausible (spot-check against design PDF)
- ✅ Pole_id mapping is authoritative
- ✅ Extraction is repeatable

**Next:** This baseline is ready for field capture (Pilot 3).

---

### Phase 2: Field-Capture Learning (Can start now)

**Task:** Noel captures another 30–50 local poles (or reuses 2026-05-11 survey if accessible).

**Deliverables:**
- Field capture CSV (local poles with observations)
- Photo evidence (organized by pole)
- Field-capture notes (workflow friction, unknowns, confidence assessment)
- Workflow improvement suggestions

**Approval gate:** Independent review confirms:
- ✅ Template schema is correct
- ✅ Photos are properly named and linked
- ✅ Coverage is ≥90% (each pole has ≥1 photo)
- ✅ Operator confidence is documented

**Next:** This field evidence is ready for baseline comparison (Phase 3).

---

### Phase 3: Baseline-Field Matching Analysis (After Phase 1 AND Phase 2)

**Task:** Compare Phase 1 baseline with Phase 2 field evidence.

**Deliverables:**
- Baseline-field comparison report
- Pole_id match analysis (if local poles belong to same area as baseline)
- Coordinate overlap analysis
- Lessons learned (are field pole_ids consistent with baseline? Do photos match design expectations?)

**Approval gate:** Independent review confirms:
- ✅ Comparison method is valid
- ✅ Any mismatches are explained
- ✅ Lessons are documented

**Next:** Informs decision about which baseline to use for full Pilot 3.

---

### Phase 4: Controlled Baseline + Field Evidence Pilot (Full authorization pilot)

**Prerequisites:**
- Phase 1 complete (baseline CSV ready)
- Phase 2 complete (field-capture workflow proven)
- Phase 3 complete (lessons learned documented)

**Task:** Find (or use) one accessible baseline job (e.g., Bellsprings, Gordon, or P_CONTROLLED_001).
Noel captures 30–50 poles FROM THAT BASELINE in the field.

**Deliverables:**
- Baseline CSV (from Phase 1)
- Captured field CSV (baseline poles only, with observations + photos)
- Validator pass/PARTIAL verdict
- Operator decision notes (friction, unknowns, confidence)
- Signed decision template (GO / CONDITIONAL GO / NO-GO)
- Gate auditor review and confirmation

**Approval gate:** Independent review confirms:
- ✅ Baseline-field match rate ≥80% (GO) or ≥75% (CONDITIONAL GO)
- ✅ Valid rows ≥90%, merge-ready ≥50%, evidence ≥90%
- ✅ Operator confidence ≥4
- ✅ Decision verdict matches thresholds
- ✅ Verdict is properly signed and audited

**Next:** If GO or CONDITIONAL GO → **Stage 4C implementation task is authorized**.

---

## Stage 4C Authorization Pathway

```
BLOCKED (today)
    ↓
Phase 1: Baseline extraction (Codex)
    ↓
Phase 2: Field-capture workflow (Noel)
    ↓
Phase 3: Baseline-field matching analysis
    ↓
Phase 4: Controlled Pilot (baseline + field evidence, 30–50 poles)
    ↓
Pilot validation: Validator verdict PASS/PARTIAL
    ↓
Operator assessment: Noel fills decision notes
    ↓
Verdict decision: Noel signs GO / CONDITIONAL GO
    ↓
Gate audit: Independent auditor confirms
    ↓
AUTHORIZED → Stage 4C implementation task starts
    ↓
New task: Runtime upload route, merge algorithm, database integration
    ↓
Tests + code review + merge_safety_check
    ↓
Merge to master → Stage 4C available (feature flag disabled by default)
```

---

## What This Means for Bellsprings, Gordon, and Noel's Local Survey

### Bellsprings Baseline
- ✅ Use for Phase 1 (baseline extraction learning)
- ✅ Use for Phase 4 (controlled pilot baseline)
- ❌ Cannot use alone for Stage 4C approval (no field evidence yet)

### Gordon Original/PR1/PR2
- ✅ Use for Phase 1 (baseline extraction learning + design evolution)
- ✅ Use for Phase 4 IF accessible (controlled pilot baseline)
- ❌ Cannot use alone for Stage 4C approval (no field evidence yet)

### Noel's Local Field Survey (2026-05-11)
- ✅ Use for Phase 2 (field-capture workflow proof)
- ✅ Use for Phase 3 IF poles match Bellsprings/Gordon area (baseline-field matching)
- ❌ Cannot use alone for Stage 4C approval (no baseline to compare against)

### Full Controlled Pilot (Phase 4)
- ✅ Can be Bellsprings baseline + Noel field capture (if accessible)
- ✅ Can be Gordon baseline + Noel field capture (if accessible)
- ✅ Can be P_CONTROLLED_001 baseline + Noel field capture (already set up)
- ✅ If meets acceptance criteria → **AUTHORIZES Stage 4C**

---

## Decision: Recommended Next Step

### Immediate (Phases 1–2, parallel work)

1. **Codex:** Extract Bellsprings baseline using baseline extraction script
   - Target: Bellsprings starter CSV ready in 1–2 days
   - Deliverable: 30–50 pole baseline, coordinates verified, pole_id mapping documented
   - Not yet approval; just learning and preparing

2. **Noel:** Optionally extend local field survey or refresh it if time permits
   - Target: 30–50 additional field observations (any accessible poles)
   - Deliverable: Field CSV + photos showing workflow proof
   - Not yet approval; just demonstrating field-capture works

### Medium-term (Phase 3, after 1–2, before 4)

3. **Codex + Noel:** Analyze baseline-field matching
   - Do Noel's local poles overlap with Bellsprings baseline area?
   - If yes: Calculate match rate, document lessons
   - If no: Document geographic separation, plan Phase 4 separately

### Final (Phase 4, full authorization pilot)

4. **Noel + Codex:** Execute controlled baseline + field evidence pilot
   - Use Bellsprings (or Gordon, or P_CONTROLLED_001) as baseline
   - Noel captures 30–50 poles from that baseline
   - Validator runs; Noel signs verdict
   - Gate audit; if GO → **Stage 4C implementation authorized**

---

## Critical Point: No Auto-Approval

**Even if all Phases 1–3 are complete:**

- Bellsprings baseline alone = "ready for field use" (not Stage 4C approval)
- Noel's field evidence alone = "field capture works" (not Stage 4C approval)
- Bellsprings + Noel field evidence matching = "baseline-field align is possible" (not Stage 4C approval)

**Only Phase 4 (full controlled pilot with signed verdict + gate audit) = Stage 4C authorization.**

---

## Summary Table

| Item | Phase | Proves | Authorizes |
|------|-------|--------|------------|
| Bellsprings baseline extraction | 1 | Extraction works; baseline is valid | Nothing (learning only) |
| Noel's local field CSV | 2 | Field capture works; template is usable | Nothing (learning only) |
| Baseline-field matching analysis | 3 | Baseline and field CAN be compared | Nothing (learning only) |
| Controlled pilot (baseline + field + validator + verdict) | 4 | Full pipeline works; match rate ≥80%; operator confident | **Stage 4C implementation task** |

---

## Reference

- **Doc 73:** Controlled Baseline Pilot Prep (why baseline pilot matters)
- **Doc 74:** Pole_ID Match Protocol (exact matching rules)
- **Doc 75:** Controlled Pilot Decision Template (verdict mechanism)
- **Doc 83:** P_CONTROLLED_001 Readiness Gate (baseline readiness)
- **Doc 84:** P_CONTROLLED_001 Field Decision Checklist (field targets)
- **Doc 85:** P_CONTROLLED_001 Post-Field Acceptance Gate (GO/NO-GO criteria)
- **Doc 87:** Real Survey Pack Readiness Review (baseline file suitability)
