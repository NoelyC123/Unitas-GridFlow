---
status: TEMPLATE — fill in after pilot
created: 2026-05-10
branch: claude-code/real-field-pilot-readiness-stage4c-gate-audit
---

# 65 — Stage 4C Decision Board Template

Fill this in after the real field pilot is complete and validated. This decision board determines whether Stage 4C runtime integration can proceed, or whether additional work is needed.

**This is a required input to the Stage 4C go/no-go gate (document 50).**

---

## Pilot summary

| Field | Value |
|---|---|
| Date | |
| Job | |
| Rows captured | |
| Captured by | |
| Validation run date | |
| Result template location | `AI_CONTROL/53_REAL_FIELD_PILOT_RESULT_TEMPLATE.md` |

---

## Validation stats (from result template 53)

| Metric | Value | Target | Pass? |
|---|---|---|---|
| Validation pass rate | ____% | ≥90% | YES / NO |
| Merge-ready rate | ____% | ≥80% | YES / NO |
| pole_id match rate | ____% | ≥80% | YES / NO |
| Completeness: complete rows | ____ | ≥1 | YES / NO |
| Completeness: partial rows | ____ | ≥2 | YES / NO |
| Duplicate pole_ids found | ____ | ≤1 | YES / NO |
| Rows with warnings | ____% | ≤20% | YES / NO |

---

## Evidence stats

| Metric | Value | Target | Pass? |
|---|---|---|---|
| Photos captured | ____ | ≥1 per pole | YES / NO |
| Photos properly named | ____% | ≥80% | YES / NO |
| Observations logged | ____ | ≥1 issue | YES / NO |
| Template usability score | ____ / 5 | ≥4 | YES / NO |

---

## Defects found

| # | Defect | Severity | Affected rows | Resolution |
|---|---|---|---|---|
| 1 | | | | |
| 2 | | | | |
| 3 | | | | |

---

## Risks that fired during pilot

For each risk that manifested, document:

| Risk ID | Risk description | Observations | Control effectiveness |
|---|---|---|---|
| R01 | Wrong pole_id match | | Field control worked? / Validation caught? |
| R02 | Fake completeness | | Field control worked? / Validation caught? |
| R03 | Leakage | | (N/A — intake-only) |
| R04 | pole_id format mismatch | | Field control worked? / Validation caught? |
| R05 | B vs C divergence | | (N/A — validation-only) |
| R06 | Schema drift | | (N/A — schema frozen) |
| R07 | Scope creep | | (N/A — runtime not active) |
| R08 | Cross-session duplicate | | Field control worked? / Validation caught? |

---

## Unresolved questions

Document any questions that came up during the pilot that need resolution before Stage 4C implementation:

| # | Question | Owner | Action |
|---|---|---|---|
| 1 | | | |
| 2 | | | |

---

## Validation summary

**Raw pytest output**:
```
[Paste raw output from pytest run here]
```

---

## Pre-Stage4C gate readiness check

Using the Stage 4C gate criteria (document 50), check each GO condition:

| # | Criterion | Status | Notes |
|---|---|---|---|
| G1 | Stage 4B merged | ✓ / ✗ | Confirmed in master? |
| G2 | Real pilot passed | ✓ / ✗ | This template = YES? |
| G3 | Golden sample suite passes | ✓ / ✗ | Confirmed pytest? |
| G4 | pole_id match ≥80% | ✓ / ✗ | Pilot result shows: ___% |
| G5 | Duplicate detection tested | ✓ / ✗ | Confirmed pytest? |
| G6 | Trimble isolation test | ✓ / ✗ | (R05 — deferred to Stage 4C) |
| G7 | Leakage guard passes | ✓ / ✗ | Confirmed pytest? |
| G8 | merge_safety_check Stage 4C | ✓ / ✗ | Confirmed script? |
| G9 | Noel sign-off | ✓ / ✗ | Sign below? |

---

## Recommendation

Based on the pilot evidence above, choose ONE:

- [ ] **APPROVE Stage 4C** — All success metrics met, no blockers, recommend proceeding to Stage 4C implementation immediately.
- [ ] **APPROVE WITH CONDITIONS** — Metrics mostly met, minor defects documented; recommend Stage 4C with these fixes noted for implementation.
- [ ] **RE-PILOT** — One or more success metrics failed due to correctable template/procedure issue; recommend fixing and re-running pilot.
- [ ] **FIX STAGE 4B** — Validation itself broke or revealed schema gaps; recommend fixing Stage 4B before re-piloting.
- [ ] **STOP STAGE 4** — Fundamental blocker encountered; recommend halting Stage 4 work or investigating different approach.

---

## Recommendation rationale

Explain your choice above in 2–3 sentences:

_______________________________________________________________________________

_______________________________________________________________________________

---

## Final go/no-go decision

**DECISION: APPROVE / APPROVE WITH CONDITIONS / RE-PILOT / FIX STAGE 4B / STOP**

_(Delete options that do not apply.)_

**Reasoning**:

_______________________________________________________________________________

---

## Stage 4C sign-off

Noel: review the pilot result (53), validate stats, defects, and risks above, then sign off:

**Signed by**: __________________________

**Title**: __________________________

**Date**: __________________________

**Notes**:

_______________________________________________________________________________

---

## Next steps (if APPROVE or APPROVE WITH CONDITIONS)

If decision is APPROVE, Stage 4C implementation can start. Assign:

- [ ] Create Stage 4C runtime intake route in `api_intake.py`
- [ ] Create `JobStructuredCaptureRecord` model
- [ ] Implement merge algorithm per document 56
- [ ] Implement feature flag per document 57
- [ ] Write R05 integration test
- [ ] Write R07 boundary tests
- [ ] Merge to master

**Target Stage 4C merge date**: ____________________

**Owner**: __________________________

---

## Next steps (if RE-PILOT or FIX STAGE 4B)

If decision is RE-PILOT or FIX STAGE 4B, document the blockers:

1. **Issue**: ________________________________________________________________

   **Fix**: ________________________________________________________________

2. **Issue**: ________________________________________________________________

   **Fix**: ________________________________________________________________

**Target date for re-pilot or fix**: ____________________

**Owner**: __________________________

---

## Next steps (if STOP)

If decision is STOP, document the reason and recommendation:

**Blocker**: ________________________________________________________________

**Recommendation**: ________________________________________________________________

**Escalation**: Who should review this decision? ____________________

---

## Attachments

- Pilot checklist (52) — completed
- Pilot result template (53) — completed with VERDICT: GO/NO-GO
- Field day operating checklist (62) — used as field guide
- Success metrics (63) — evaluation reference
- Risk control matrix (64) — risk review reference
