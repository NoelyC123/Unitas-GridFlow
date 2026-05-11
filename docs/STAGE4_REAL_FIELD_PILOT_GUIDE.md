# Stage 4 Real iPad Field Pilot Guide

## Purpose

This pilot proves two things before any Stage 4C runtime work starts:

1. Noel can capture structured support data on an iPad without inventing values.
2. The captured CSV validates cleanly through the Stage 4B preview rules.

This is a field-operating pack, not a runtime integration step. Nothing in this
pilot should change live GridFlow job outputs, popups, or Review OS behaviour.

## Pilot objective

Capture a small but varied real support sample, export it as CSV, and run it
through the Stage 4B validator so Noel can decide whether Stage 4C is safe to
start later.

## Site selection rules

- Use a job with known Trimble baseline data already in GridFlow.
- Prefer `P008/F001` or `P010` because the baseline review path is already
  stable.
- Choose a short route where 10 to 20 supports can be visited in one session.
- Use supports where the Trimble `pole_id` can be read and copied exactly.
- Do not use a route where most supports have missing or ambiguous identity.

## Recommended sample mix

Target 10 to 20 supports with this minimum variety:

- 3 to 5 existing poles
- 2 to 4 proposed poles
- 1 angle pole
- 1 stay or anchor example
- 1 no-stay example where `stay_type` is explicitly `none`
- 1 crossing or context support/point
- 1 support with missing or uncertain evidence
- 1 support where legacy or low-confidence information can be compared to field observation

The goal is not broad network coverage. The goal is enough variety to prove the
template and validator behave correctly under real capture conditions.

## What Noel should capture

Capture only what can be observed or reliably confirmed at the support:

- exact Trimble `pole_id`
- support role and structure type
- material when known
- measured height only when actually measured or reliably verified
- condition and obvious defects
- stay presence and type
- lean direction and severity where visible
- equipment presence/type only when clear
- concise survey notes and access notes
- evidence state, confidence, and whether verification is required
- photo references that match the evidence folder protocol

## What not to record yet

Do not invent or force future-scope data into this pilot:

- no runtime merge assumptions
- no guessed voltage if it is not clear
- no made-up pole class or strength
- no fake asset relationship links
- no extra fields outside the Stage 4B schema
- no C2E2 popup expectations

## Truthfulness rules

Use these rules in the field:

- If you did not capture it, leave it blank.
- If a field allows explicit `none`, use `none` only when the absence is known.
- If the evidence is weak, set `confidence_level=low`.
- If the row needs follow-up before design/runtime use, set
  `verification_required=yes`.
- If the observation depends on legacy notes or partial evidence, use
  `evidence_status=legacy_record`, `estimated`, or `verification_required` as
  appropriate.
- Keep `capture_date` in ISO format only: `YYYY-MM-DD`.

## Field workflow on the iPad

1. Open [structured_capture_ipad_pilot_template.csv](/Users/noelcollins/Unitas-GridFlow/templates/structured_capture_ipad_pilot_template.csv).
2. Load it into Numbers, Excel, or Google Sheets on the iPad.
3. Freeze the header row.
4. Fill the first six columns first on every row:
   `pole_id`, `project_id`, `file_id`, `capture_source`, `captured_by`,
   `capture_date`.
5. Add support facts next:
   `structure_type`, `asset_intent`, `material`, `condition`, `stay_*`,
   `lean_*`, `equipment_*`.
6. Add notes, photo reference, evidence, and confidence last.

## Minimal good pilot row

A minimum acceptable pilot row has:

- `pole_id`
- `capture_source`
- `captured_by`
- `capture_date`

That row validates, but it is not merge-ready unless it also contains real
support data beyond identity and capture metadata.

## End-of-day output

After the field session:

- save the CSV as UTF-8
- name it `pilot_real_<jobid>.csv`
- place it in `real_pilot_data/<pilot-name>/csv/`
- place photos in `real_pilot_data/<pilot-name>/photos/`
- run the validation steps in
  [STAGE4_PILOT_VALIDATION_INSTRUCTIONS.md](/Users/noelcollins/Unitas-GridFlow/docs/STAGE4_PILOT_VALIDATION_INSTRUCTIONS.md)
- complete the result summary template in
  [STAGE4_PILOT_RESULT_SUMMARY_TEMPLATE.md](/Users/noelcollins/Unitas-GridFlow/docs/STAGE4_PILOT_RESULT_SUMMARY_TEMPLATE.md)
- keep the raw CSV, photos, and operator reports local unless Noel explicitly
  approves a redacted artifact for Git

The command-center result should be read like this:

- `PASS`: the pilot result is strong enough for Noel to review as Stage 4C evidence
- `PARTIAL / RE-PILOT REQUIRED`: usable evidence exists, but more cleanup or capture is needed
- `NO-GO`: the pilot package or export needs fixing before any Stage 4C discussion

## Using an existing workbook before the live pilot

An existing workbook can be used as a rehearsal dataset before Noel goes into
the field with the iPad template.

Use this workflow:

1. Keep the original workbook local under
   `real_pilot_data/<pilot-name>/source/`.
2. Convert the best matching sheet with
   `scripts/convert_stage4_workbook_to_pilot_csv.py`.
3. Run `scripts/validate_stage4_pilot.py` on the converted CSV.
4. Review the missing, extra, and matched fields before the live pilot.

This helps answer:

- whether existing captured columns line up with the Stage 4B schema
- whether `photo_reference` values already follow the expected naming pattern
- which fields still need cleaner operator guidance

This does not prove the live pilot workflow. A real iPad capture session is
still required to validate field-entry friction, truthfulness under live
capture, and evidence-folder discipline.

## Stage 4C status

Stage 4C remains blocked until:

- a real pilot CSV exists
- the pilot validation result is recorded
- Noel records a GO decision
