# Stage 3A Design Brief — Local Daily Intake

## Status

Approved for implementation as a small Stage 3A1 MVP.

## Purpose

Stage 3A starts the move from after-the-fact processing toward live intake. The first useful step is not cloud deployment. The first useful step is making the current project app behave like an intake dashboard: survey files arrive under a named project, each upload can be labelled as a survey day or return visit, and the office can leave feedback while the survey is still active.

## Stage 3A Split

### Stage 3A1 — Local Daily Intake MVP

Build inside the current Flask/project app.

The MVP adds:

- survey day / visit label per uploaded project file
- uploaded-by label
- surveyor note for handover context
- office feedback note per file
- intake status derived from processing and designer review state
- project dashboard wording that makes the project page usable as an intake view

### Stage 3A2 — Cloud / Remote Access Plan

Do not implement cloud access yet.

After Stage 3A1 is validated, create a short deployment plan covering:

- simple managed hosting
- shared-password/basic access control
- upload storage and backup
- mobile upload constraints
- UK/EU data sensitivity and hosting preference

## Data Model

Stage 3A1 stores intake metadata in each project file's `meta.json`:

```json
{
  "intake": {
    "survey_day_label": "Day 1",
    "uploaded_by": "Surveyor",
    "surveyor_note": "Uploaded from van at end of day.",
    "office_feedback": "Please confirm EXpole 67 before export."
  }
}
```

The project summary exposes derived fields per file:

- `intake_status`
- `review_status`
- `intake`

`intake_status` is derived rather than manually edited:

- `reviewed` if the file has a reviewed `review.json`
- `needs_review` if processing is complete but not reviewed
- `needs_attention` if processing failed
- otherwise the processing state (`awaiting_upload`, `uploaded`, `processing`, etc.)

## User Flow

1. Open a project.
2. Click **Add Survey File**.
3. Enter optional survey day / visit label, uploaded-by, and surveyor note.
4. Upload the CSV as normal.
5. Project page shows the file as an intake row with status, notes, and output actions.
6. Office adds feedback if the surveyor needs to check anything.
7. Designer uses the existing Review page and D2D exports when ready.

## Non-Goals

- No cloud deployment in Stage 3A1
- No authentication or user accounts
- No direct Trimble live sync
- No tablet forms
- No photo capture
- No combined cross-file chain merging
- No PoleCAD-specific exporter
- No new QA algorithms unless real validation evidence requires them

## Validation

Use real files as intake examples:

- **Gordon Pt1** as a single-day/single-file intake project
- **Strabane 474 + 474c** as a multi-file or multi-visit intake project

Validation should confirm:

- survey-day metadata is stored and visible on the project page
- office feedback can be saved and survives reload
- intake status changes from processed/needs review to reviewed when Stage 3B review exists
- existing Map, PDF, D2D Chain, D2D Working, and Review actions still work
- the flow is understandable without explaining the underlying file structure

## Success Criteria

Stage 3A1 is successful when a project page can answer:

- What survey files have arrived?
- Which day or visit does each file represent?
- Who uploaded it?
- What did the surveyor want the office to know?
- What does the office need the surveyor/designer to check?
- Is the file processed, needing review, or reviewed?
