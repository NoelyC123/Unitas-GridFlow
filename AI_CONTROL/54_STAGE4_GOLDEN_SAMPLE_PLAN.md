---
status: ACTIVE
created: 2026-05-10
branch: codex/stage4b-4c-safety-pilot-harness
---

# 54 — Stage 4 Golden Sample Plan

This document defines the golden sample dataset strategy for Stage 4
validation testing. Golden samples are the canonical test fixtures that all
Stage 4 validator correctness tests run against.

---

## Purpose

Golden samples provide:

1. **Regression protection** — a fixed expected output for each input type
2. **Edge-case coverage** — known-bad, duplicate, legacy-format, and ambiguous rows
3. **Pipeline integration testing** — end-to-end from CSV import → validation → merge
4. **Stage 4C readiness evidence** — real job data confirms pole_id matching works

---

## Sample categories

### Category 1 — Synthetic: valid rows

File: `tests/fixtures/stage4/golden_valid.csv`

| Row | Description | Expected outcome |
|---|---|---|
| 1 | Minimum required fields only | valid, merge_ready, completeness=minimum |
| 2 | Full optional fields (condition, voltage, stay, equipment) | valid, merge_ready, completeness=complete |
| 3 | Boolean fields as "yes"/"no" | valid, all boolean_enum normalised |
| 4 | Voltage "11kv" (lowercase) | valid, normalised to "11kV" |
| 5 | stay_type="none" (explicit no-stay) | valid, none preserved, not treated as blank |
| 6 | lean_direction="none" | valid, none preserved |
| 7 | equipment_type="none" | valid, none preserved |
| 8 | `Point` column instead of `pole_id` (alias) | valid, resolved to pole_id |
| 9 | confidence_level="high" | valid |
| 10 | All optional fields blank | valid, merge_ready, completeness=minimum |

### Category 2 — Synthetic: invalid rows

File: `tests/fixtures/stage4/golden_invalid.csv`

| Row | Defect | Expected outcome |
|---|---|---|
| 1 | pole_id missing | invalid, merge_ready=False, error names pole_id |
| 2 | pole_id="n/a" (blank token) | invalid, merge_ready=False |
| 3 | pole_id="unknown" (unsafe identity) | invalid, merge_ready=False |
| 4 | capture_source missing | invalid, error names capture_source |
| 5 | condition="excellent" (invalid enum) | invalid, error names condition |
| 6 | stay_type="flying_down" (unknown value) | invalid, error names stay_type |
| 7 | capture_date="10/05/2026" (wrong format) | invalid or warning, error notes format |
| 8 | voltage_carried="999kV" (not in allowed set) | invalid, error names voltage_carried |
| 9 | condition="none" (none not allowed here) | invalid, error notes none not allowed |
| 10 | stay_present="none" (boolean_enum, none invalid) | invalid |

### Category 3 — Duplicate detection

File: `tests/fixtures/stage4/golden_duplicates.csv`

| Row | Description | Expected outcome |
|---|---|---|
| 1 | pole_id="P008-001", valid otherwise | invalid after dedup check |
| 2 | pole_id="P008-001", duplicate | both rows flagged invalid, merge_ready=False |
| 3 | pole_id="P008-002", unique | valid, merge_ready=True |

### Category 4 — Known-bad: common field mistakes

File: `tests/fixtures/stage4/golden_known_bad.csv`

Common real-world mistakes that have been observed in survey spreadsheets:

| Row | Defect | Notes |
|---|---|---|
| 1 | pole_id has trailing space "P008-001 " | Should normalise or reject |
| 2 | capture_date="2026/05/10" (slashes not dashes) | ISO-8601 violation |
| 3 | condition="Good" (capitalised) | Should normalise to "good" |
| 4 | voltage_carried="11 kV" (space in unit) | Should normalise via alias map |
| 5 | pole_id="?" (blank token) | Rejected as blank identity |
| 6 | stay_present="Y" (alias for yes) | Should normalise to "yes" |
| 7 | equipment_present="FALSE" | Should normalise to "no" |
| 8 | All fields blank except pole_id | completeness=minimum (only required fields counted) |

### Category 5 — Real pilot data

File: `tests/fixtures/stage4/pilot_real_<jobid>.csv`

Generated from the real iPad pilot (see `51_REAL_FIELD_PILOT_PLAN.md`).

Expected: actual validation results captured in `53_REAL_FIELD_PILOT_RESULT_TEMPLATE.md`.
Test: parametrised against the recorded expected outcomes.

### Category 6 — Legacy format

File: `tests/fixtures/stage4/golden_legacy_headers.csv`

Rows using column names that might come from older template versions or
Trimble exports. Tests the alias resolution path.

| Header variant | Canonical field |
|---|---|
| `Point` | `pole_id` |
| `Has_Stay` | `stay_present` |
| `voltage` | `voltage_carried` |
| `class` | `pole_class` |
| `support_id` | `pole_id` |

---

## File location

All golden sample CSVs live in `tests/fixtures/stage4/`.

```
tests/fixtures/stage4/
  golden_valid.csv
  golden_invalid.csv
  golden_duplicates.csv
  golden_known_bad.csv
  golden_legacy_headers.csv
  pilot_real_<jobid>.csv    (added after real pilot)
```

---

## Test coverage

Golden samples are covered by:

- `tests/test_stage4_golden_samples.py` — parametrised tests for each row
- `tests/test_structured_capture_validators.py` — unit tests for individual validator functions

The golden sample test must:

1. Import each CSV from `tests/fixtures/stage4/`
2. Run the full `validate_stage4_rows()` pipeline
3. Assert per-row expected outcomes
4. Assert import-level counts (valid_count, invalid_count, warning_count)

---

## Maintenance rule

When the schema changes (new fields, new allowed values), update golden samples
in the same PR. Golden sample regressions indicate a breaking schema change.
