---
status: TEMPLATE — fill in after pilot
created: 2026-05-10
---

# 53 — Real Field Pilot Result Template

Fill in after completing the pilot. Required input to Stage 4C go/no-go gate (`50_STAGE4C_GO_NO_GO_GATE.md`).

## Pilot summary

| Field | Value |
|---|---|
| Date | |
| Job | |
| Rows captured | |
| Captured by | |
| Validation run date | |

## Validation results

Paste raw output of `python scripts/validate_stage4_csv.py <pilot-csv>`:

```
[PASTE HERE]
```

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

## pole_id match analysis

| Metric | Value |
|---|---|
| Total rows in pilot CSV | |
| Rows with valid pole_id | |
| Rows where pole_id matches a Trimble record | |
| Match rate (%) | |
| Unmatched pole_ids and reason | |

## Defect log

| # | Defect | Severity | Affected rows | Proposed fix |
|---|---|---|---|---|
| 1 | | | | |

## Template usability assessment

| Question | Answer |
|---|---|
| Was pole_id entry clear? | |
| Were any field names confusing? | |
| Were enum allowed values obvious? | |
| Date format issues? | |
| Would a new surveyor manage? | |

## Summary metrics

| Metric | Result | Target | Pass? |
|---|---|---|---|
| Rows captured | | ≥ 10 | |
| Validation pass rate | | ≥ 90% | |
| pole_id match rate | | ≥ 80% | |
| Template usable without docs | | YES | |

## Verdict

**VERDICT: GO / NO-GO**

Reasoning:

---

## Stage 4C sign-off

If VERDICT is GO, Noel signs off here:

Signed off by: ________________
Date: ________________
Notes:
