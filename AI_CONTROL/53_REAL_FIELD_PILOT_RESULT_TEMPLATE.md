---
status: TEMPLATE — fill in after pilot
created: 2026-05-10
branch: codex/stage4b-4c-safety-pilot-harness
---

# 53 — Real Field Pilot Result Template

Fill this in after completing the pilot described in `51_REAL_FIELD_PILOT_PLAN.md`.
This document is a **required input** to the Stage 4C go/no-go gate
(`50_STAGE4C_GO_NO_GO_GATE.md`).

---

## Pilot summary

| Field | Value |
|---|---|
| Date | |
| Job | |
| Rows captured | |
| Captured by | |
| Validation run date | |

---

## Validation results

Paste the raw output of `python scripts/validate_stage4_csv.py <pilot-csv>` here:

```
[PASTE OUTPUT HERE]
```

---

## Row result table

| # | pole_id | valid | merge_ready | errors / warnings |
|---|---|---|---|---|
| 1 | | | | |
| 2 | | | | |
| 3 | | | | |
| 4 | | | | |
| 5 | | | | |
| 6 | | | | |
| 7 | | | | |
| 8 | | | | |
| 9 | | | | |
| 10 | | | | |

---

## pole_id match analysis

| Metric | Value |
|---|---|
| Total rows in pilot CSV | |
| Rows with valid pole_id | |
| Rows where pole_id matches a Trimble record | |
| Match rate (%) | |
| Unmatched pole_ids and reason | |

---

## Defect log

Document any validation errors, schema gaps, or usability issues found.

| # | Defect | Severity | Affected rows | Proposed fix |
|---|---|---|---|---|
| 1 | | | | |
| 2 | | | | |
| 3 | | | | |

---

## Template usability assessment

| Question | Answer |
|---|---|
| Was pole_id entry clear? | |
| Were any field names confusing? | |
| Were enum allowed values obvious? | |
| Date format issues? | |
| Would a new surveyor manage? | |

---

## Summary metrics

| Metric | Result | Target | Pass? |
|---|---|---|---|
| Rows captured | | ≥ 10 | |
| Validation pass rate | | ≥ 90% | |
| pole_id match rate | | ≥ 80% | |
| Template usable without docs | | YES | |

---

## Verdict

**VERDICT: GO / NO-GO**

_(Delete whichever does not apply and add one sentence of reasoning)_

Reasoning:

---

## Stage 4C sign-off

If VERDICT is GO, Noel should sign off here to authorise Stage 4C work:

Signed off by: ________________

Date: ________________

Notes:
