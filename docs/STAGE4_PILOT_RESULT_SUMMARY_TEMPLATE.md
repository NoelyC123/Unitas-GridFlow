# Stage 4 Pilot Result Summary Template

Use this after the real iPad field pilot.

## Pilot summary

| Field | Value |
| --- | --- |
| Date | |
| Job / route | |
| Captured by | |
| CSV filename | |
| Supports captured | |

## Asset mix captured

- Existing poles:
- Proposed poles:
- Angle poles:
- Stay / anchor examples:
- Context / crossing points:
- Missing / uncertain evidence rows:
- Legacy / low-confidence rows:

## Evidence captured

- Total photos:
- Rows with `photo_reference`:
- Rows without photos:
- Folder used:

## Validation result

Paste the key output from:

```bash
python3.13 scripts/validate_stage4_pilot.py \
  --csv real_pilot_data/<pilot-name>/csv/pilot_real_<jobid>.csv \
  --pilot-name <pilot-name> \
  --evidence-dir real_pilot_data/<pilot-name>/photos \
  --out validation_runs/stage4_pilots/<pilot-name>
```

Summary:

- Header validation:
- Merge-ready rows:
- Review-required rows:
- Blocked rows:
- Invalid rows:
- Duplicate `pole_id` issues:
- Missing `pole_id` issues:
- Evidence/photo coverage:
- Stage 4C recommendation:

Report paths:

- JSON:
- Markdown:

## Issues found

| Issue | Severity | Rows affected | Action needed |
| --- | --- | --- | --- |
| | | | |
| | | | |
| | | | |

## Field workflow friction

- Which columns were easy:
- Which columns were confusing:
- Which columns slowed field capture:
- Which fields were impossible to fill honestly on site:

## Missing fields

List anything Noel needed but the template did not support cleanly:

-
-
-

## Unnecessary fields

List anything present in the pilot template that did not add real value:

-
-
-

## Recommendation

Choose one:

- `GO` — pilot pack usable, Stage 4C planning can start when separately approved
- `PARTIAL / RE-PILOT REQUIRED` — useful pilot evidence collected, but more capture or cleanup is needed before Stage 4C review
- `NO-GO` — fix Stage 4B package issues before any Stage 4C work

Reason:

## Sign-off

| Field | Value |
| --- | --- |
| Signed off by | |
| Sign-off date | |
| Next action | |
