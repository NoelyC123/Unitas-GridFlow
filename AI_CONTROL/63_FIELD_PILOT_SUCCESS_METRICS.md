---
status: ACTIVE
created: 2026-05-10
branch: claude-code/real-field-pilot-readiness-stage4c-gate-audit
---

# 63 — Field Pilot Success Metrics

This document defines the quantitative thresholds for every measurable aspect of the real iPad field pilot. These metrics are evaluated AFTER the pilot is run and validation is complete.

---

## Scope

These metrics apply to the real iPad field pilot using `pilot_real_<jobid>.csv` captured during the field day. The pilot tests both the template usability AND the validation pipeline on real-world data.

---

## Core success metrics

| Metric | Minimum | Target | Threshold |
|---|---|---|---|
| **Rows captured** | ≥10 | 15–20 | Hard minimum: ≥10 |
| **Validation pass rate** | ≥90% | ≥95% | ≤1 invalid per 10 rows |
| **pole_id match rate** | ≥80% | ≥90% | At least 8 of 10 matched to Trimble |
| **Template usable** | YES | YES | Noel fills 5/5 usability Qs as YES |
| **Completeness distribution** | ≥1 complete, ≥2 partial | Skewed toward complete | Not all minimum |

---

## Asset mix coverage (required)

For the pilot to be representative, it must span multiple support types.

| Asset type | Minimum count | Notes |
|---|---|---|
| Structural poles (line support) | ≥3 | Basic main-line structures |
| Angle/deviation structures | ≥1 | Turn or angle in route |
| Stay structures | ≥1 | With stay attachment |
| No-stay, isolated, or context | ≥1 | Non-structural or referenced pole |

**Coverage verdict**: All 4 types captured = representative sample.

---

## Validation results thresholds

### Validation pass rate

**Definition**: (rows with valid=true) / (total rows) × 100%

**Acceptable**:
- ≥90% pass rate = GO
- 80–89% pass rate = GO WITH REVIEW (examine failures)
- <80% pass rate = NO-GO (schema/template issue)

**Examples**:
- 15 rows, 14 valid, 1 invalid = 93% pass rate = GO ✓
- 15 rows, 12 valid, 3 invalid = 80% pass rate = REVIEW (expected issue per 53)
- 15 rows, 11 valid, 4 invalid = 73% pass rate = NO-GO ✗ (template broken)

### pole_id match rate

**Definition**: (rows where pole_id matches Trimble baseline) / (total rows with valid pole_id) × 100%

**Acceptable**:
- ≥80% match rate = GO (pole_id normalization working)
- 70–79% match rate = GO WITH CAUTION (investigate format mismatches)
- <70% match rate = NO-GO (ID format problem unsolved)

**Examples**:
- 10 rows captured, 9 match Trimble, 1 unmatched = 90% match = GO ✓
- 10 rows, 8 match, 2 unmatched (both format variations) = 80% match = GO with review
- 10 rows, 6 match, 4 unmatched = 60% match = NO-GO ✗ (format normalisation failed)

### Merge-ready count

**Definition**: rows where both valid=true AND merge_ready=true

**Acceptable**:
- ≥80% merge-ready = GO (most rows can safely merge)
- 60–79% merge-ready = GO WITH CAUTION (duplicates or edge cases present)
- <60% merge-ready = REVIEW (may indicate duplicate detection issue)

**Examples**:
- 15 rows valid, 12 merge-ready = 80% merge-ready = GO ✓
- 15 rows valid, 10 merge-ready (2 duplicates detected) = 67% = CAUTION
- 15 rows valid, 8 merge-ready = 53% = REVIEW ✗ (unexpected)

---

## Completeness distribution

**Definition**: Classify each row as minimum / partial / complete (from validation output)

**Acceptable distribution**:
- ≥1 row classified as "complete" (50%+ optional fields filled)
- ≥2 rows classified as "partial" (25–49% optional fields)
- Remaining rows can be "minimum" (required fields only)

**Bad distribution**:
- All rows are "minimum" (no optional fields captured) = REVIEW
- Zero "complete" rows = CAUTION (suggests surveyor didn't attempt detail)

**Examples**:
- 15 rows: 2 complete, 5 partial, 8 minimum = GOOD ✓
- 15 rows: 0 complete, 3 partial, 12 minimum = CAUTION (low effort)
- 15 rows: 1 complete, 0 partial, 14 minimum = NO-GO (template didn't encourage detail)

---

## Evidence coverage

### Photo evidence

**Requirement**: ≥1 photo per captured pole

**Calculation**:
- Photo count ÷ pole count ≥ 1.0

**Acceptable**:
- ≥100% coverage (every pole has ≥1 photo) = GO
- 75–99% coverage (1–2 poles missing photos) = GO WITH NOTE
- <75% coverage (≥3 poles missing photos) = REVIEW (not enough evidence)

**Examples**:
- 10 poles, 12 photos (some poles have 2) = 120% coverage = GO ✓
- 10 poles, 9 photos = 90% coverage = GO ✓
- 10 poles, 7 photos = 70% coverage = REVIEW (3 missing)

### Photo metadata

**Expected**: Photos named per protocol `<pole_id>_<seq>_<view>.jpg`

**Acceptable**:
- ≥80% of photos follow naming convention = GO
- 60–79% follow convention = GO WITH NOTE (rename before archiving)
- <60% follow convention = CAUTION (protocol not understood)

---

## Defect threshold

### Unacceptable defects (hard blocks)

If ANY of these are true, result is automatic NO-GO:

- [ ] Cannot extract pole_id from pilot CSV (header missing or corrupted)
- [ ] More than 50% of rows have pole_id = blank/null/"unknown"/"n/a"
- [ ] CSV is not valid UTF-8 (encoding error)
- [ ] Validation cannot complete (pytest crash, schema error)
- [ ] capture_date format is not parseable (not YYYY-MM-DD)
- [ ] Data dictionary is misaligned with template (field names don't match)

**Impact**: Any of these = immediate VERDICT: NO-GO. Do NOT proceed to Stage 4C.

### Acceptable defects (log and evaluate)

These are acceptable if ≤5% of rows are affected:

- [ ] capture_date format variation (mixed MM/DD/YYYY and YYYY-MM-DD)
- [ ] pole_id whitespace (leading/trailing spaces)
- [ ] condition values capitalized (Good vs good)
- [ ] voltage_carried with space (11 kV vs 11kV)
- [ ] Boolean fields as Y/N instead of yes/no

**Impact**: Log in defect table (53); note normalization is needed; still GO if < 5%.

---

## Warning threshold

**Definition**: Rows with valid=true but warnings present (e.g., redundant fields, missing optional)

**Acceptable**:
- ≤20% of rows with warnings = GO (normal)
- 20–50% of rows with warnings = GO WITH REVIEW
- >50% of rows with warnings = REVIEW (widespread issue)

---

## Template usability threshold

**Question set** (from checklist 52):
1. Was pole_id entry clear? YES / NO / NOTES
2. Were field names ambiguous? YES / NO / NOTES
3. Were enum values obvious? YES / NO / NOTES
4. Date format issues? YES / NO / NOTES
5. Would a new surveyor manage? YES / NO / NOTES

**Acceptable**:
- ≥4 YES answers = template is usable without docs = GO ✓
- 3 YES, 1 NO = template usable with minor note = GO WITH CAUTION
- ≤2 YES = template needs redesign = REVIEW (identify issues for re-pilot)

---

## Stage 4C GO threshold

**All of the following must be true**:

- [ ] Rows captured ≥ 10
- [ ] Validation pass rate ≥ 90%
- [ ] pole_id match rate ≥ 80%
- [ ] Merge-ready count ≥ 80%
- [ ] Completeness distribution includes ≥1 complete AND ≥2 partial
- [ ] Photo coverage ≥ 75%
- [ ] Template usability score ≥ 4/5 YES
- [ ] NO unacceptable defects (hard blocks all false)
- [ ] Defect count ≤ 5%
- [ ] Noel signs off VERDICT = GO in template 53

**If all TRUE**: Stage 4C can proceed.

---

## Stage 4C NO-GO threshold

**Result is NO-GO if ANY of the following**:

- [ ] Rows captured < 10 (insufficient sample)
- [ ] Validation pass rate < 90% (template broken)
- [ ] pole_id match rate < 80% (format mismatch unsolved)
- [ ] Merge-ready count < 60% (duplicates or edge cases widespread)
- [ ] All rows are "minimum" completeness (template didn't encourage detail)
- [ ] Photo coverage < 75% (insufficient evidence)
- [ ] Template usability score < 3/5 YES (not usable without redesign)
- [ ] ≥1 unacceptable defect present (hard block)
- [ ] Defect count > 5%
- [ ] Noel signs off VERDICT = NO-GO in template 53

**If any TRUE**: Stage 4C is blocked. Document blockers; decide: re-pilot, fix Stage 4B, or stop.

---

## Decision logic (summary)

**STAGE 4C GATE OPENS IF**:
- Pilot passes ALL Stage 4C GO thresholds
- AND Noel signs VERDICT = GO in template 53
- AND No hard blockers

**STAGE 4C GATE REMAINS CLOSED IF**:
- Pilot fails ANY Stage 4C NO-GO threshold
- OR Noel signs VERDICT = NO-GO in template 53
- OR Hard blockers present

---

## Success metrics checklist (for post-pilot evaluation)

Noel: after running validation, complete this checklist:

| Metric | Target | Actual | Pass? |
|---|---|---|---|
| Rows captured | ≥10 | _____ | YES / NO |
| Validation pass rate | ≥90% | _____ % | YES / NO |
| pole_id match rate | ≥80% | _____ % | YES / NO |
| Merge-ready rate | ≥80% | _____ % | YES / NO |
| Completeness (≥1 complete + ≥2 partial) | YES | YES / NO | YES / NO |
| Photo coverage | ≥75% | _____ % | YES / NO |
| Template usability | ≥4/5 YES | _____ / 5 | YES / NO |
| Unacceptable defects | 0 | _____ | YES / NO |
| Acceptable defect rate | <5% | _____ % | YES / NO |

**Summary**: All YES? → VERDICT: GO. Any NO? → Evaluate against NO-GO thresholds.
