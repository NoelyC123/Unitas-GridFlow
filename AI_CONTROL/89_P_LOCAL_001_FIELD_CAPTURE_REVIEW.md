# P_LOCAL_001 Field-Capture Review

**For: Understanding P_LOCAL_001 as accessible real field-capture validation evidence**

**Date:** 2026-05-12
**Purpose:** Independent readiness review of P_LOCAL_001, Noel's real local field-capture pilot
**Authority:** Documents 73–85 (Controlled Baseline framework, field pack, acceptance gates)
**Scope:** What P_LOCAL_001 proves and does not prove, validator expectations, Stage 4C status

---

## Classification

**P_LOCAL_001 = Accessible Real Field-Capture Validation Pilot**

- ✅ Real survey data (Noel's 2026-05-11 local pole survey)
- ✅ Real evidence photos (33 cleaned images, linked to poles)
- ✅ Survey CSV compatible with Stage 4 template schema
- ✅ Operator-completed observations (pole type, condition, equipment, stays, voltage)
- ✅ Local/accessible (no DNO proprietary constraints)

**Not:** controlled baseline comparison pilot (P_LOCAL_001 is field evidence without independent baseline reference)

---

## What P_LOCAL_001 Proves

✅ **Survey CSV Usability**
- Stage 4 template schema works in practice
- Operator can capture all required fields
- No schema blockers

✅ **Photo Evidence Linkage**
- Photos successfully named by pole_id
- Photos organized by evidence type (clear, obscured, etc.)
- Evidence-linking workflow executable
- ≥1 photo per pole achievable

✅ **Unknown-Field Handling**
- Operator honestly marks fields as "unknown" when cannot fill
- Unknown-field counts measurable
- Workflow handles uncertainty gracefully

✅ **Access Constraint Handling**
- Some poles accessible (normal capture possible)
- Some poles difficult (vegetation, terrain, private land)
- Operator documents constraints in notes
- Workflow handles real-world access realities

✅ **Operator Workflow Realism**
- Captures 30+ poles in field (single day feasible)
- Operator able to take photos, fill observations, organize evidence
- Time estimate realistic (10–15 min per pole typical)
- Friction points (if any) documented and manageable

✅ **Validator Behavior on Real Field Evidence**
- Validator runs successfully on real local CSV
- Validator correctly identifies valid/invalid rows
- Validator correctly links/missing/orphaned photos
- Validator calculates match rate (even if no baseline comparison)
- Validator reports generate expected output structure

---

## What P_LOCAL_001 Does NOT Prove

❌ **Exact Pole_ID Matching Against Independent Baseline**
- P_LOCAL_001 has no independent baseline to compare against
- Cannot calculate baseline-field pole_id match rate
- Cannot prove ≥80% exact match threshold
- This is not a blocker; it's a classification issue

❌ **Stage 4C Runtime Merge Safety**
- Validator proves schema correctness, not merge safety
- Merge algorithm untested
- Database integration untested
- API route untested
- This requires full runtime integration testing (separate task)

❌ **DNO/Design Technical Truth**
- Noel's observations are operator assessment, not surveyor certification
- Voltage/conductor data are best-effort operator guesses
- Equipment observations are visual estimate, not nameplate verification
- Pole-class/strength data are inferred, not measured

❌ **Automatic Stage 4C Approval**
- Field evidence alone does not authorize Stage 4C
- Baseline + field evidence required for approval
- Even validator PASS does not bypass decision gate
- Stage 4C remains blocked

---

## Expected Validator Outcomes

**PASS or PARTIAL acceptable.** Real field data is messier than test data.

### Quantitative Expectations

- **Valid rows (schema + required fields):** ≥85% (real field data has unknowns)
- **Review-required rows:** 30–50% expected (unknowns, uncertain values, inferred fields)
- **Merge-ready rows:** 10–30% (only high-confidence, fully-filled rows)
- **Blocked rows:** 0–5% (empty pole_id, broken schema; should be minimal)
- **Missing photos:** 0 (all poles should have ≥1 photo)
- **Orphaned photos:** 0 (all photos named correctly and linked)
- **Duplicate pole_ids:** 0 (operator should not duplicate)

### Acceptable Patterns

✅ **Unknown voltage:** Common (nameplate not visible, operator honest)
✅ **Unknown conductor_size:** Common (cannot see from ground safely)
✅ **Uncertain pole_class:** Common (visual estimate; mark verification_required=yes)
✅ **Inferred stay_required:** Common (cannot see base clearly; mark evidence_status=obscured)
✅ **Obscured photos:** Expected (vegetation, terrain, access limits)

### Blockers (Should Be Rare)

❌ **Missing pole_id:** Blocker (cannot identify pole)
❌ **Blank required fields + no verification_required flag:** Blocker (silent uncertainty)
❌ **Photo naming mismatch:** Blocker (evidence cannot be linked)
❌ **Duplicate pole_ids:** Blocker (data integrity issue)

---

## Fields Requiring Manual Review

Noel should manually spot-check these high-risk inferred fields:

| Field | Risk | Why | Noel's Review |
|-------|------|-----|---|
| `voltage_carried` | High | Operator guessed from context (DNO rule, transformer size) | Spot-check 5–10 poles; flag if pattern seems wrong |
| `conductor_size` | High | Operator cannot see from ground safely | Spot-check against photo detail if visible |
| `phase_configuration` | Medium | Inferred from pole type and equipment | Verify single-phase vs. 3-phase matches equipment |
| `pole_class` | Medium | Visual estimate (angle, corrosion, defects) | Confirm obvious classes (H/M/S); uncertain = verify_required |
| `pole_strength` | Medium | Never measured; inferred from age/material | Expected uncertainty; mark as review-required if unsure |
| `stay_required` | Medium | Cannot see base if vegetation blocks | Obscured photos expected; mark evidence_status=obscured |
| `specification` | Low | Likely blank or inferred from pole type | Acceptable; not critical for field evidence |
| `defect_severity` | Low | Visual assessment (good/fair/poor); no structural analysis | Observable; acceptable for field evidence |

**Action:** If pattern in reviewed fields seems systematically off (e.g., all voltages guessed incorrectly), note in decision memo and adjust Phase 4 field guidance.

---

## Validator Command

Codex will run (or has run):

```bash
python scripts/validate_stage4_pilot.py \
  --csv real_pilot_data/P_LOCAL_001/csv/P_LOCAL_001.csv \
  --evidence-dir real_pilot_data/P_LOCAL_001/photos_final/ \
  --pilot-name P_LOCAL_001 \
  --out validation_runs/stage4_pilots/P_LOCAL_001_FINAL
```

**Outputs to review:**
- `pilot_validation_report.json` — machine-readable metrics (match rate, row counts, evidence audit)
- `pilot_validation_report.md` — human-readable summary
- `evidence_audit.json` — photo linking details (missing, orphaned, matched)

---

## Explicit Statement: Stage 4C Remains Blocked

**P_LOCAL_001 is NOT approval evidence for Stage 4C authorization.**

Reasons:
1. P_LOCAL_001 has no independent baseline to compare against
2. Cannot calculate exact pole_id match rate
3. Cannot prove ≥80% threshold required for GO verdict
4. Cannot demonstrate baseline-field alignment

**What IS required for Stage 4C:**
- Real baseline CSV (Bellsprings, Gordon, or P_CONTROLLED_001)
- Field evidence FROM THAT BASELINE (Noel captures same poles)
- Exact pole_id matching ≥80%
- Validator PASS/PARTIAL with accepted metrics
- Noel's signed decision template verdict
- Independent gate auditor confirmation

**P_LOCAL_001's role:**
- Workflow proof (capture is feasible)
- Operator learning (how to document field realities)
- Lessons for future Phase 4 pilot
- NOT approval evidence for Stage 4C

**Stage 4C authorization status: BLOCKED** (unchanged)

---

## Reference

- **Doc 80:** Controlled Pilot Field Pack (field-day procedure P_LOCAL_001 follows)
- **Doc 82:** Operator Decision Notes (Noel's friction, unknowns, confidence assessment)
- **Doc 84:** Field Decision Checklist (per-pole targets P_LOCAL_001 achieves)
- **Doc 85:** Post-Field Acceptance Gate (quantitative/qualitative criteria)
- **Doc 88:** Baseline vs. Field Evidence (why field evidence alone is insufficient)
- **Doc 90:** Field-Capture vs. Baseline Merge Gap (how P_LOCAL_001 fits into Phase sequencing)
