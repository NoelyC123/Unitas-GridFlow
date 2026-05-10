---
status: ACTIVE
created: 2026-05-10
branch: codex/stage4c-runtime-integration-architecture
---

# 59 — Field Pilot Acceptance Gate

This document defines the **acceptance criteria** for the real field pilot (iPad-based structured capture). The pilot is a required input to the Stage 4C go/no-go gate (document 50). This gate determines whether the pilot data is sufficient evidence that Stage 4C runtime intake is ready to merge.

---

## Pilot objective

Prove that:
1. Surveyor can use the Stage 4 template without guidance
2. Resulting CSV is valid and survives validation
3. pole_id matching works at ≥80% rate
4. Template covers the essential real-world capture use cases

---

## Success criteria

| Criterion | Target | Acceptance logic |
|---|---|---|
| **Sample size** | ≥10 poles | Minimum n for statistical confidence |
| **Validation pass rate** | ≥90% | At most 1 invalid row per 10 |
| **pole_id match rate** | ≥80% | At least 8/10 pole IDs match Trimble baseline |
| **Template usability** | YES | Noel can fill template without consulting docs |
| **No schema confusion** | YES | Field names are clear; no ambiguity in capturing |
| **Completeness distribution** | ≥1 complete, ≥2 partial | Not all rows should be minimum |

---

## Data requirements: what the pilot must capture

### Mandatory coverage (every row must have)

- `pole_id` — exact Trimble ID (tests pole_id matching)
- `capture_source` — "office_audit" or "surveyor_tablet" (tests sourcing)
- `captured_by` — surveyor name (tests attribution)
- `capture_date` — YYYY-MM-DD (tests date parsing)

### Recommended coverage (at least 50% of rows should include)

- `condition` — good / fair / poor (tests enum normalization)
- `voltage_carried` — 11kV / 33kV / etc (tests case/spacing normalization)
- `stay_present` — yes / no (tests boolean enum)
- `confidence_level` — low / medium / high (tests rating self-assessment)

### Optional coverage (to assess completeness)

- `stay_type`, `lean_direction`, `equipment_type` — if applicable (tests none handling)
- `defect_notes`, `clearance_issues` — free text (tests optional text fields)

---

## Evaluation process

### Step 1: Run validation (during pilot)

```bash
python scripts/validate_stage4_csv.py tests/fixtures/stage4/pilot_real_<jobid>.csv
```

Record output in `53_REAL_FIELD_PILOT_RESULT_TEMPLATE.md`.

### Step 2: Cross-reference pole_id against Trimble baseline

For the chosen job (e.g., P008/F001):
1. Extract Trimble pole_ids from sample_data/
2. Compare against captured pole_ids in pilot CSV
3. Calculate match rate: (matched poles) / (total captured poles)
4. Record any unmatched pole_ids and reason (format mismatch? typo? new pole?)

### Step 3: Assess completeness distribution

Count by completeness level:
- minimum: only required fields
- partial: 50% of optional fields
- complete: >50% of optional fields

**Expected distribution**: skewed toward partial/complete (surveyor tried to capture detail).
**Bad distribution**: all minimum (suggests surveyor only filled required fields).

### Step 4: Review defect log (from checklist 52)

Any issues noted during capture?
- Field names confusing?
- Date format problems?
- Enum values unclear?
- Numbers/Sheets changed formatting?

**Pass criterion**: No critical usability issues; any minor issues are documented and fixable by release.

### Step 5: Assess template usability (from checklist 52)

Noel answers:
1. Was pole_id entry clear? YES / NO / NOTES
2. Were field names ambiguous? YES / NO / NOTES
3. Were enum values obvious? YES / NO / NOTES
4. Date format issues? YES / NO / NOTES
5. Would a new surveyor manage? YES / NO / NOTES

**Pass criterion**: Majority YES; any NO items have a clear fix documented.

---

## No-go conditions (pilot fails)

**Pilot fails if ANY of these are true**:

| Condition | Reason |
|---|---|
| Validation pass rate < 90% | Too many parsing/validation errors; schema or template is broken |
| pole_id match rate < 80% | Format or entry error is too high; pole_id matching unreliable |
| Rows captured < 10 | Sample too small for confidence; pilot is incomplete |
| Template requires guidance | Surveyors cannot use without documentation; UX failure |
| Completeness is all minimum | Suggests template doesn't encourage detail capture; incomplete design |
| Critical defect logged | Schema gap, hard parsing error, or safety risk (e.g., no pole_id possible) |

**If pilot fails**:
- Noel sets VERDICT: NO-GO
- Document blockers in defect log (59)
- Recommend fixes (schema change? template redesign? pilot retake?)
- Do NOT merge Stage 4C until pilot passes

---

## Go conditions (pilot succeeds)

**Pilot passes if ALL of these are true**:

- ✓ Validation pass rate ≥ 90%
- ✓ pole_id match rate ≥ 80%
- ✓ Rows captured ≥ 10
- ✓ Template usability YES (or clear fix for any NO)
- ✓ Completeness distribution includes partial/complete rows
- ✓ No critical defects

**If pilot passes**:
- Noel sets VERDICT: GO
- Documents summary: "X/Y poles captured, Z% validation pass rate, W% pole_id match, completeness distribution: A minimum / B partial / C complete"
- Signs off in document 53
- Signals go/no-go gate (50) to proceed

---

## Pilot result documentation

### Document 52: Checklist (filled during pilot)

- Pre-pilot setup checklist
- Pole ID reference list
- Capture observation log
- Post-capture file format checklist
- Template usability assessment

### Document 53: Result template (filled after validation)

- Pilot summary table
- Raw validation output (copy/paste)
- Per-row result table (pole_id, valid, merge_ready, errors)
- pole_id match analysis (match rate, unmatched list)
- Defect log (any validation errors or usability issues)
- Template usability assessment (repeat from 52)
- Summary metrics (validation %, match %, rows captured)
- VERDICT: GO / NO-GO + reasoning
- Noel sign-off

### Golden sample fixture (if pilot passes)

Save pilot CSV as golden sample:
```bash
cp tests/fixtures/stage4/pilot_real_<jobid>.csv \
   tests/fixtures/stage4/golden_pilot_real_<jobid>.csv
```

This becomes a permanent test fixture, parametrized into `test_stage4_golden_samples.py`:

```python
@pytest.mark.parametrize("csv_file, expected_results", [
    ("tests/fixtures/stage4/golden_valid.csv", GOLDEN_VALID_EXPECTED),
    ("tests/fixtures/stage4/golden_invalid.csv", GOLDEN_INVALID_EXPECTED),
    ...
    ("tests/fixtures/stage4/golden_pilot_real_P008F001.csv", PILOT_REAL_EXPECTED),
])
def test_golden_sample_validation(csv_file, expected_results):
    # Validate CSV
    # Assert actual results match expected
    ...
```

Pilot becomes regression evidence for all future Stage 4B/4C work.

---

## Gate integration

### Before Stage 4C merge to master:

1. **Pilot plan** (51) is finalized
2. **Pilot checklist** (52) is started
3. **Pilot is run** (real job, real surveyor or Noel doing a desk-based simulation)
4. **Pilot result** (53) is filled in with VERDICT
5. **This gate** (59) is reviewed
6. **Stage 4C go/no-go gate** (50) is checked:
   - Pilot VERDICT = GO?
   - Golden samples complete?
   - Merge safety checks pass?
   - Leakage guards pass?
   - Noel approves?

If all checks pass: Stage 4C code merges to master.

---

## Re-pilot scenario (if pilot fails)

If pilot fails:

1. Noel documents blockers in defect log
2. If blocker is **schema**: fix in `structured_capture_schema.py`, update golden samples, retry with new template
3. If blocker is **template UX**: redesign in `templates/structured_capture_template.csv`, update 51 pilot plan, retry with new template
4. If blocker is **validation logic**: fix in `validate_stage4_rows()`, golden samples may need update, retry
5. Re-run pilot (same job or new one)
6. Repeat evaluation until VERDICT = GO

---

## Relationship to golden samples

| Document | Purpose | Timing |
|---|---|---|
| **54 Golden Sample Plan** | Design synthetic test cases | Before 4B/4C branch |
| **51 Real Pilot Plan** | Define real-world validation | Before pilot run |
| **52 Pilot Checklist** | Operational guide during pilot | During pilot |
| **59 This gate** | Evaluate pilot results | After pilot completed |
| **53 Pilot Result** | Record pilot outcome + metrics | After pilot completed |

**Connection**: Pilot result becomes golden sample, which is parametrized into golden sample test suite (54).

---

## Sign-off authority

**Noel** (project owner) signs off on pilot VERDICT.

Requirements:
- Noel must review the completed result (53) personally
- Noel must verify pole_id match rate personally (spot-check CSV against Trimble)
- Noel must assess template usability (can I use this without docs?)
- Noel makes final GO / NO-GO call

If Noel signs NO-GO, Stage 4C merge is blocked until issues are resolved.

---

## Escalation path

If pilot result is ambiguous (e.g., 85% validation pass rate — is that acceptable?):

1. Noel consults defect log (59)
2. Noel evaluates if failures are fixable or indicate systematic issue
3. Noel may request partial re-pilot (just re-capture the failed rows)
4. Noel decides: is this "good enough" for Stage 4C intake, or does it indicate schema/template gaps?

---

## Schedule

Real field pilot is scheduled for:
- **When**: After Stage 4B merges and is stable (1–2 weeks post-4B merge)
- **Duration**: 1–2 hours (10–20 poles on known job)
- **Outcome needed by**: Stage 4C go/no-go gate date (TBD)

See `51_REAL_FIELD_PILOT_PLAN.md` for details.
