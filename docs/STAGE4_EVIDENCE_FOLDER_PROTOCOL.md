# Stage 4 Evidence Folder Protocol

## Purpose

This protocol keeps photos and notes linked to `pole_id` values without adding
any runtime storage or live upload behaviour.

## Folder structure

Store field evidence outside runtime job outputs and outside Git using this
local-only structure:

```text
real_pilot_data/
  <pilot-name>/
    csv/
      pilot_real_<jobid>.csv
    photos/
      <pole_id>/
        <pole_id>_01_context.jpg
        <pole_id>_02_support.jpg
        <pole_id>_03_top.jpg
    notes/
      pilot_notes_<jobid>.md
```

Example:

```text
real_pilot_data/P_REAL_001/
  csv/pilot_real_P008_F001.csv
  photos/P008-001/P008-001_01_context.jpg
```

`real_pilot_data/` is git-ignored. Do not move real field photos or raw CSVs
into `tests/fixtures/` or any tracked path unless Noel explicitly approves a
redacted example for regression use.

## Photo naming

Use:

`<pole_id>_<sequence>_<view>.jpg`

Examples:

- `P008-001_01_context.jpg`
- `P008-001_02_support.jpg`
- `P008-001_03_top.jpg`
- `P008-014_02_stay.jpg`

Keep the same filename in the CSV `photo_reference` column.

The validator checks filenames only. It does not open or process image content.

## Minimum photo guidance

- **Context photo**: one wider shot showing approach, road, or crossing context
- **Support photo**: one full support photo where practical
- **Pole-top photo**: only when relevant equipment or attachment context exists
- **Stay/anchor photo**: required when stay evidence is part of the row
- **Defect photo**: required when a defect is significant enough to note

## Linking rules

- Every photo must map to exactly one `pole_id`.
- Every note about a specific support should mention that `pole_id`.
- Do not use generic names like `IMG_1024.jpg` in the CSV.

## Missing photos

If no photo was captured:

- leave `photo_reference` blank
- explain the reason in `survey_notes` or `access_notes` if it matters
- do not invent a file reference
- expect the validator report to show lower evidence/reference coverage

## Uncertain evidence

If the photo or observation is incomplete:

- use `confidence_level=low`
- set `verification_required=yes` when follow-up is needed
- use `evidence_status=verification_required` or `legacy_record` where appropriate

## Out of scope for this pilot

Do not capture or store:

- customer personal data
- faces or private property detail unless unavoidable for network context
- unrelated assets not tied to the pilot route
- videos
- cloud-storage links as the only reference

## What may be committed

Without explicit approval, do not commit:

- raw pilot CSVs
- real field photos
- local validation output under `validation_runs/stage4_pilots/`

Only explicitly approved redacted reports or synthetic fixtures should be added
to Git.

## Safety and privacy notes

- Do not take photos where access is unsafe.
- Do not enter private land without permission.
- Keep the pilot limited to support evidence relevant to design readiness.
