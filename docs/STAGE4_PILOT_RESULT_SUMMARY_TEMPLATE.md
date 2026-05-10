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
pytest -v tests/test_stage4_pilot_package.py -k real_pilot
```

Summary:

- Header validation:
- Merge-ready rows:
- Review-required rows:
- Blocked rows:
- Invalid rows:
- Duplicate `pole_id` issues:

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
- `NO-GO` — fix Stage 4B package issues before any Stage 4C work

Reason:

## Sign-off

| Field | Value |
| --- | --- |
| Signed off by | |
| Sign-off date | |
| Next action | |
