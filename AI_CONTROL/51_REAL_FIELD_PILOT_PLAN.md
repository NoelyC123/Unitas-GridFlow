---
status: ACTIVE
created: 2026-05-10
---

# 51 — Real Field Pilot Plan

iPad-based field capture pilot using Stage 4 CSV template. Go/no-go prerequisite for Stage 4C (see `50_STAGE4C_GO_NO_GO_GATE.md`).

## Pilot objective

Validate that the Stage 4 CSV template is usable by a real surveyor in real field conditions, and that the resulting data round-trips correctly through Stage 4 validation with useful `pole_id` match rate.

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

## Preparation

1. Export template: `python scripts/generate_structured_capture_template.py`
2. Load template on iPad in Numbers/Sheets/Excel
3. Confirm pole IDs from Trimble survey file (must use exact IDs)
4. Have result template ready (`53_REAL_FIELD_PILOT_RESULT_TEMPLATE.md`)

## Field capture procedure

For each support:
1. Enter Trimble `pole_id` exactly as it appears (e.g. `P008-001`)
2. Fill `capture_source`: `office_audit` (desk) or `surveyor_tablet` (field)
3. Fill `captured_by` with your name
4. Fill `capture_date` as `YYYY-MM-DD`
5. Fill any optional fields observable

Do NOT invent `pole_id` values.

## Post-capture validation

```bash
python scripts/validate_stage4_csv.py <path-to-pilot-csv>
```

Cross-reference pilot CSV `pole_id` values against Trimble baseline for the same job. Record match count.

## Success criteria

| Criterion | Target |
|---|---|
| Rows captured | ≥ 10 |
| Validation pass rate | ≥ 90% |
| `pole_id` match rate vs Trimble | ≥ 80% |
| Template usable without instruction | Noel can fill it in without consulting docs |
| No schema confusion | No ambiguous or confusing field names |

## Known risks

| Risk | Mitigation |
|---|---|
| Trimble `pole_id` format differs from Stage 4 expectation | Normalise on import; document reformatting |
| Optional fields too many / confusing | Reduce pilot to required + 4–6 key optional |
| CSV header case-sensitivity | Validator uses alias map; confirm coverage |
| Numbers/Sheets changes field format | Ensure `capture_date` stays YYYY-MM-DD |

## Output

Completed pilot CSV: `tests/fixtures/stage4/pilot_real_<jobid>.csv`
Pilot result: `AI_CONTROL/53_REAL_FIELD_PILOT_RESULT_TEMPLATE.md`
