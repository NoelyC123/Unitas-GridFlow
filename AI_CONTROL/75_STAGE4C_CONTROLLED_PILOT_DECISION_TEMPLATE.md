# Stage 4C Controlled Pilot Decision Template

**For use after running the controlled baseline pilot (30–50 poles, real Trimble baseline)**

---

## Pilot Metadata

| Field | Value |
|---|---|
| Pilot ID | _______________ |
| Date (start) | _______________ |
| Date (end) | _______________ |
| Real job baseline | _______________ |
| Trimble pole_id count | _______________ (how many poles in baseline) |
| Captured pole count | _______________ |
| Evidence folder | `real_pilot_data/<PILOT_ID>/photos_final/` |
| Validation report | `validation_runs/stage4_pilots/<PILOT_ID>_FINAL/` |
| Operator (name) | _______________ (Noel or field team) |

---

## Measured Thresholds

### Row-level findings

| Metric | Target | Actual | Status |
|---|---|---|---|
| **Total captured rows** | ≥30 | ___ | ✅ / ⚠️ / ❌ |
| **Valid rows** | ≥90% | ___% | ✅ / ⚠️ / ❌ |
| **Invalid rows** | 0 | ___ | ✅ / ⚠️ / ❌ |
| **Merge-ready rows** | ≥50% | ___% | ✅ / ⚠️ / ❌ |
| **Review-required rows** | ≤50% | ___% | ✅ / ⚠️ / ❌ |
| **Blocked rows** | 0 | ___ | ✅ / ⚠️ / ❌ |

### Pole_id matching findings

| Metric | Target | Actual | Status |
|---|---|---|---|
| **pole_id match rate** | ≥80% | ___% | ✅ / ⚠️ / ❌ |
| **Exact matches** | ≥24/30 (or proportional) | ___/___ | ✅ / ⚠️ / ❌ |
| **Mismatches** | ≤6/30 (or proportional) | ___/___ | ✅ / ⚠️ / ❌ |
| **Mismatch categories:** | | | |
|   - New poles | acceptable | ___ | ✅ / ⚠️ / ❌ |
|   - Typos | fixable | ___ | ✅ / ⚠️ / ❌ |
|   - Format differences | investigate | ___ | ✅ / ⚠️ / ❌ |
|   - Ambiguous/uncertain | document | ___ | ✅ / ⚠️ / ❌ |

### Evidence findings

| Metric | Target | Actual | Status |
|---|---|---|---|
| **Evidence photos found** | ≥1 per row | ___ | ✅ / ⚠️ / ❌ |
| **Reference coverage** | ≥90% | ___% | ✅ / ⚠️ / ❌ |
| **Missing referenced photos** | 0 | ___ | ✅ / ⚠️ / ❌ |
| **Unreferenced photos** | 0 | ___ | ✅ / ⚠️ / ❌ |
| **Duplicate filenames** | 0 | ___ | ✅ / ⚠️ / ❌ |
| **Invalid filename patterns** | 0 | ___ | ✅ / ⚠️ / ❌ |

### Warning profile

| Warning type | Count | Explanation |
|---|---|---|
| `verification_required=yes` | ___ | Rows you marked as uncertain |
| `low confidence structured capture row` | ___ | Inferred/estimated values |
| `evidence status requires verification` | ___ | Photos needing closer review |
| **Total warnings** | ___ | (should be non-blocking) |

---

## Attribute Verification (Sample)

For 5–10 merge-ready rows, verify attributes against Trimble baseline:

| pole_id | Trimble voltage | Captured voltage | Match | Notes |
|---|---|---|---|---|
| _______________ | _______________ | _______________ | ✅/❌ | _______________ |
| _______________ | _______________ | _______________ | ✅/❌ | _______________ |
| _______________ | _______________ | _______________ | ✅/❌ | _______________ |
| _______________ | _______________ | _______________ | ✅/❌ | _______________ |
| _______________ | _______________ | _______________ | ✅/❌ | _______________ |

**Attribute match rate:** ___/5 = ___%
**Assessment:** ✅ Attributes match / ⚠️ Minor discrepancies / ❌ Significant mismatches

---

## Operator Friction Assessment

Rate the workflow difficulty (1 = easy, 5 = very difficult):

| Aspect | Rating | Notes |
|---|---|---|
| **Template clarity** | 1 2 3 4 5 | Were field labels clear? |
| **Capture ease** | 1 2 3 4 5 | How easy was it to fill each row? |
| **Evidence organization** | 1 2 3 4 5 | Was photo naming/folder structure manageable? |
| **Validation usability** | 1 2 3 4 5 | Were error messages helpful? |
| **Overall workflow** | 1 2 3 4 5 | Would you recommend this to another surveyor? |

**Comments:** _______________________________________________________________

---

## Defects and Issues

| Issue | Severity | Root cause | Resolution |
|---|---|---|---|
| _______________ | Critical / Major / Minor | _______________ | _______________ |
| _______________ | Critical / Major / Minor | _______________ | _______________ |
| _______________ | Critical / Major / Minor | _______________ | _______________ |

---

## Risk Assessment (for Stage 4C implementation)

**Did this pilot reveal any unexpected risks?**

- R01 (Pole_id matching): ✅ Confirmed safe / ⚠️ Partially safe / ❌ At risk
  - **Finding:** _______________________________________________________________
- R02 (Electrical attributes): ✅ Confirmed safe / ⚠️ Partially safe / ❌ At risk
  - **Finding:** _______________________________________________________________
- R03 (Evidence linking): ✅ Confirmed safe / ⚠️ Partially safe / ❌ At risk
  - **Finding:** _______________________________________________________________
- R04 (Review-required threshold): ✅ Defined / ⚠️ Partially defined / ❌ Undefined
  - **Finding:** _______________________________________________________________
- R05/R06 (Runtime safety): ✅ Deferred (as planned) / ❌ Issues discovered
  - **Finding:** _______________________________________________________________

---

## Verdict

### Your recommendation

**Based on the measured thresholds, attribute verification, and risk assessment, my recommendation is:**

○ **GO** — Stage 4C ready for runtime integration
   (All thresholds met or exceeded; confidence high)

○ **CONDITIONAL GO** — Stage 4C can proceed with documented cautions
   (Most thresholds met; minor issues are acceptable/fixable)

○ **NO-GO** — Stage 4C remains blocked; re-pilot needed after fixes
   (Key thresholds not met; root cause must be investigated)

○ **STOP** — Pilot terminated; emergency review required
   (Blocker discovered; isolation or data integrity concern)

---

### Why this verdict

**Explain your recommendation in 2–3 sentences:**

_______________________________________________________________________________

_______________________________________________________________________________

_______________________________________________________________________________

---

### If CONDITIONAL GO or NO-GO: What would make it GO?

**What needs to happen before Stage 4C can proceed?**

1. _________________________________________________________________
2. _________________________________________________________________
3. _________________________________________________________________

---

### Stage 4C Implementation Scope (If GO or CONDITIONAL GO)

**If you voted GO or CONDITIONAL GO, understand:**

- ✅ This verdict **authorises a NEW TASK** to implement Stage 4C runtime integration
- ✅ That task will wire the upload route, merge algorithm, and database integration
- ✅ **It does NOT auto-merge** — your verdict opens the gate; implementation is separate work
- ❌ This verdict **does NOT approve** Stage 4D (popup surfacing) or beyond
- ❌ Stage 4C runtime will have a feature flag; enable only after final test

---

## Sign-Off

**By signing below, you confirm:**

1. ✅ "I have personally verified pole_id matching against the Trimble baseline"
2. ✅ "I have reviewed all NO MATCH reasons and documented them"
3. ✅ "I have verified evidence photos are correctly linked (no missing/orphaned)"
4. ✅ "I understand what merge-ready, review-required, and blocked rows mean"
5. ✅ "My verdict is based on the measured thresholds and my field experience"
6. ✅ "I accept responsibility for this verdict"

**Operator (field team / Noel):**
Name: ___________________________
Signature: ________________________
Date: ___________________________

**Reviewer (Claude Code / gate auditor):**
Name: ___________________________
Signature: ________________________
Date: ___________________________

---

## Approval Authority

**This decision board is the formal record of GO / CONDITIONAL GO / NO-GO / STOP for Stage 4C.**

- If **GO** or **CONDITIONAL GO:** A new Stage 4C implementation task can begin immediately
- If **NO-GO:** Root-cause analysis and re-pilot planning begin immediately
- If **STOP:** Emergency investigation; Stage 4 is frozen pending review

**No Stage 4C code changes will be merged to master without this signed decision board.**

---

## Archive

This template, once filled and signed, becomes part of the permanent project record.

- **File location:** `AI_CONTROL/75_STAGE4C_CONTROLLED_PILOT_DECISION_TEMPLATE.md` (this file, updated with your answers)
- **Backup location:** Noel's field notebook or project archive
- **Reference:** Future Stage 4D, 4E, 4F decisions will cite this pilot
