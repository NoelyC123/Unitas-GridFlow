# Stage 3A Validation Acceptance

## Stage

Stage 3A1 — Local Daily Intake MVP

## Date

2026-04-27

## What was implemented

Stage 3A1 adds a lightweight intake layer to the existing project system:

- survey day / visit label per project file
- uploaded-by label
- surveyor note for handover context
- office feedback note per file
- derived intake status on the project overview
- review-aware project file status (`needs_review` vs `reviewed`)

The implementation intentionally remains local. It does not add cloud hosting, authentication, direct Trimble sync, tablet forms, photo capture, or combined cross-file route merging.

## Files changed

- `app/project_manager.py`
- `app/routes/api_projects.py`
- `app/templates/project.html`
- `app/templates/upload.html`
- `app/static/js/upload-manager.js`
- `tests/test_project_manager.py`
- `tests/test_project_integration.py`

## Automated tests

Focused test command:

```bash
.venv312/bin/python -m pytest tests/test_project_manager.py tests/test_project_integration.py
```

Result:

- 41 passing tests
- 1 external ReportLab deprecation warning

## Real-file validation

Validation was run using Flask `test_client` against a temporary project root, so no working upload data was changed.

Files used:

- `validation_data/gordon_pt1/raw/Gordon Pt1 - Original.csv`
- `validation_data/2814_474/raw/2814_4-474_raw_trimble_export.csv`
- `validation_data/2814_474/raw/2814_474c_raw_trimble_export.csv`

Validation results:

- Gordon created as a single-file intake project.
- Gordon file stored `Day 1` intake metadata.
- Office feedback saved and survived project reload.
- Gordon derived intake status was `needs_review`.
- Strabane 474 created as a project with one file.
- Strabane 474c added to the same project as a return visit.
- Strabane project summary showed 2 files.
- Strabane intake labels were `Day 1` and `Return visit`.

Validation output:

```json
{
  "gordon_project": "P001",
  "gordon_intake_status": "needs_review",
  "gordon_files": 1,
  "strabane_project": "P002",
  "strabane_files": 2,
  "strabane_labels": [
    "Day 1",
    "Return visit"
  ]
}
```

## Acceptance conclusion

Stage 3A1 is accepted as a local daily-intake MVP. The project page can now answer what survey files have arrived, which day/visit each file represents, who uploaded it, what the surveyor noted, what the office feedback is, and whether each file still needs designer review.

The next Stage 3A step should be a short Stage 3A2 cloud/remote access plan, not immediate deployment.
