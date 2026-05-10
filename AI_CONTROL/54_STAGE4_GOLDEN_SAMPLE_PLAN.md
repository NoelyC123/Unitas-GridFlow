---
status: ACTIVE
created: 2026-05-10
---

# 54 — Stage 4 Golden Sample Plan

Golden sample test data strategy for Stage 4 validation testing.

## Purpose

- Regression protection: fixed expected output for each input type
- Edge-case coverage: known-bad, duplicate, legacy-format rows
- Pipeline integration testing: end-to-end CSV import → validation → merge
- Stage 4C readiness evidence: real job data confirms pole_id matching works

## Sample categories

### Category 1 — Valid rows
`tests/fixtures/stage4/golden_valid.csv`
- Minimum required fields only
- Full optional fields (condition, voltage, stay, equipment)
- Boolean fields as yes/no, normalisation cases
- All-none enum fields preserved (stay_type="none", lean_direction="none", etc.)
- Metadata-only (no asset data — valid but not merge-ready)

### Category 2 — Invalid rows
`tests/fixtures/stage4/golden_invalid.csv`
- Blank/unsafe pole_id variants
- Missing required fields
- Invalid enum values
- Bad date formats (slashes not dashes)
- Condition="none" (none not allowed here)

### Category 3 — Duplicates
`tests/fixtures/stage4/golden_duplicates.csv`
- Same pole_id in 2 rows
- Both should be flagged invalid, merge_ready=False
- Unique row should pass

### Category 4 — Known-bad / normalisation
`tests/fixtures/stage4/golden_known_bad.csv`
- Trailing space in pole_id (strip on normalisation)
- Slash date format (ISO violation)
- Capitalised condition (normalise to lowercase)
- Space in voltage ("11 kV" → "11kV")
- Question mark as pole_id (blank token)
- Boolean aliases Y/FALSE (normalise)

### Category 5 — Legacy headers
`tests/fixtures/stage4/golden_legacy_headers.csv`
- `Point` column (alias for pole_id)
- Resolves via alias map correctly

### Category 6 — Real pilot data
`tests/fixtures/stage4/pilot_real_<jobid>.csv`
- Actual field pilot capture
- Validation results from `53_REAL_FIELD_PILOT_RESULT_TEMPLATE.md`

## Maintenance rule

When schema changes (new fields, new allowed values), update golden samples in the same PR. Regressions indicate breaking changes.
