---
status: ACTIVE
created: 2026-05-10
branch: codex/stage4b-4c-safety-pilot-harness
---

# 51 — Real Field Pilot Plan

This document defines the plan for a real iPad-based field capture pilot using
the Stage 4 structured capture template. The pilot is a go/no-go prerequisite
for Stage 4C (see `50_STAGE4C_GO_NO_GO_GATE.md`).

---

## Pilot objective

Validate that the Stage 4 CSV template is usable by a real surveyor in real
field conditions, and that the resulting data round-trips correctly through the
Stage 4 validation pipeline with a useful `pole_id` match rate.

---

## Pilot scope

| Parameter | Value |
|---|---|
| Scale | 10–20 supports on a known job |
| Location | Any existing NIE or SPEN job with Trimble survey data in `sample_data/` |
| Recommended job | P008/F001 or P010 (both have validated Trimble baseline) |
| Capture device | iPad or similar tablet |
| Input method | Numbers / Google Sheets / Excel using `structured_capture_template.csv` headers |
| Minimum fields | `pole_id`, `capture_source`, `captured_by`, `capture_date` (required fields only) |
| Recommended fields | Add `condition`, `voltage_carried`, `stay_present`, `confidence_level` for meaningful preview |

---

## Preparation steps

1. **Export template**
   ```bash
   python scripts/generate_structured_capture_template.py
   ```
   Confirm `templates/structured_capture_template.csv` is current.

2. **Load template on iPad**
   Open in Numbers, Google Sheets, or Excel. The header row must not be altered.

3. **Confirm pole IDs**
   Pull the pole IDs from the Trimble survey file for the chosen job.
   Record them in the Pilot Checklist (`52_REAL_FIELD_PILOT_CHECKLIST.md`).
   These are the IDs Noel must use in the `pole_id` column.

4. **Set up result recording**
   Have the result template (`53_REAL_FIELD_PILOT_RESULT_TEMPLATE.md`) ready
   to fill in during/after the pilot.

---

## Field capture procedure

For each support in the pilot set:

1. Enter the Trimble `pole_id` exactly as it appears in the survey (e.g. `P008-001`)
2. Fill `capture_source`: use `office_audit` if doing a desk-based pilot, or
   `surveyor_tablet` if in the field
3. Fill `captured_by` with your name
4. Fill `capture_date` as `YYYY-MM-DD`
5. Fill any optional fields you can observe or retrieve from the survey record

Do NOT invent `pole_id` values. Use the exact IDs from the Trimble export.

---

## Post-capture validation steps

Once the CSV is saved:

```bash
# 1. Run the Stage 4B validation preview (once Stage 4B is merged)
python scripts/validate_stage4_csv.py <path-to-pilot-csv>

# 2. Note the outcome for each row:
#    - valid / invalid / merge_ready
#    - pole_id matches in Trimble baseline?
#    - any unexpected errors?
```

Manually cross-reference the pilot CSV `pole_id` values against the Trimble
baseline for the same job. Record the match count.

---

## Success criteria

| Criterion | Target |
|---|---|
| Rows captured | ≥ 10 |
| Validation pass rate | ≥ 90% (at most 1 invalid row in 10) |
| `pole_id` match rate vs Trimble | ≥ 80% |
| Template usable without instruction | Noel can fill it in without consulting docs |
| No schema confusion | No ambiguous or confusing field names |

---

## Known risks

| Risk | Mitigation |
|---|---|
| Trimble `pole_id` format differs from Stage 4 expectation | Normalise on import; document any reformatting needed |
| Optional fields too many / confusing | Reduce pilot to required + 4–6 key optional |
| CSV header case-sensitivity | Validator uses alias map; confirm aliases cover Trimble export variants |
| Numbers/Sheets changes field format | Ensure `capture_date` stays YYYY-MM-DD; check float fields are not reformatted |

---

## Output

Completed pilot data goes into `tests/fixtures/stage4/pilot_real_<jobid>.csv`.

Pilot result goes into `AI_CONTROL/53_REAL_FIELD_PILOT_RESULT_TEMPLATE.md`.
