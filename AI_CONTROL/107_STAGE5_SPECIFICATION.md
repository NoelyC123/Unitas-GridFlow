# Stage 5: Designer Review UI Specification

## Purpose

Stage 5 builds a web-based interface that allows designers to review the merged output from Stage 4C in a structured, visual workflow.

The UI must allow designers to:

- View matched poles with field photos, map screenshots, notes, and baseline data.
- Understand verification flags and design blockers.
- Track which poles have been reviewed, approved, or flagged.
- Export structured DNO data requests.
- Maintain a clear audit trail from field evidence to designer action.

Stage 5 is a review and workflow layer. It does not create engineering designs, certify DNO data, or approve poles automatically.

## Why Stage 5 Is Needed

The Stage 4C pipeline produces useful JSON, CSV, and Markdown outputs. Those outputs are suitable for technical validation, but a production designer needs a clearer interface.

A designer needs:

- Photos and map screenshots alongside the matched pole record.
- Fast filtering by confidence, verification flag, and design status.
- A practical queue of poles needing action.
- A simple way to mark poles as reviewed or blocked.
- Exportable DNO data requests.
- A workflow that is easier than manually comparing folders, CSVs, and reports.

Stage 5 turns the Stage 4C output into an operational designer workspace.

## Scope

### In Scope

- Web UI displaying one imported Stage 4C run at a time.
- Run dashboard with match rate, design-blocked count, and verification flag counts.
- Pole list with sorting and filtering.
- Pole detail view with field photos, map screenshots, notes, match data, and verification flags.
- Designer review actions: reviewed, approved for design preparation, flagged for attention.
- DNO data request generator using verification flags and support numbers.
- Export of review state and DNO request pack.
- Basic authentication suitable for a small pilot team.
- Local file serving for approved evidence folders.

### Out of Scope

- PoleCAD integration. This is Stage 6 or later.
- DNO API integration. This is Stage 6 or later.
- Automated design generation.
- Automated design approval.
- Mobile field capture interface.
- Computer vision or image interpretation.
- Replacement for DNO engineering records.

## Technical Architecture

### Recommended Stack

Backend: FastAPI, unless the implementation decision is made to integrate directly into the existing GridFlow web app.

Frontend: React with Tailwind CSS or the existing project UI system if integration into the current app is preferred.

Database:

- SQLite for single-user pilot deployment.
- PostgreSQL for multi-user contractor or ICP deployment.

File storage: Local filesystem for field photos and map screenshots, with paths controlled by imported Stage 4C run metadata.

Authentication: Simple JWT authentication for initial pilot use. Enterprise authentication can be considered after ICP pilot feedback.

### Data Flow

```text
Stage 4C output JSON
  -> Import into Stage 5 database
  -> FastAPI serves run, pole, evidence, and review endpoints
  -> React UI displays designer workspace
  -> Designer records review actions
  -> UI exports DNO data request and review summary
```

The UI must preserve the source authority hierarchy:

- Baseline data identifies support number, coordinates, and route context.
- Field evidence records current visible condition.
- DNO engineering records remain required for voltage, conductor specification, pole class, ratings, and compliance.

## API Endpoints

Minimum viable endpoints:

```text
GET  /api/runs
GET  /api/runs/{run_id}
GET  /api/runs/{run_id}/poles
GET  /api/runs/{run_id}/poles/{support_no}
GET  /api/runs/{run_id}/poles/{support_no}/photos
GET  /api/runs/{run_id}/qa-report
POST /api/runs/import
POST /api/runs/{run_id}/poles/{support_no}/review
POST /api/runs/{run_id}/poles/{support_no}/approve
POST /api/runs/{run_id}/poles/{support_no}/flag
POST /api/runs/{run_id}/export/dno-request
GET  /api/runs/{run_id}/export/review-summary
```

Endpoint requirements:

- All pole endpoints must return verification flags and match confidence.
- Review actions must store reviewer, timestamp, status, and notes.
- Export endpoints must not imply DNO approval or engineering certification.
- Photo endpoints must serve only evidence paths imported into the run.

## Database Schema

Minimum viable schema:

```text
pipeline_runs
  id
  run_date
  baseline_source
  field_source
  match_rate
  total_poles
  design_blocked_count
  review_required_count
  status
  imported_by
  created_at

merged_poles
  id
  run_id
  support_no
  pole_id
  match_confidence
  match_type
  design_blocked
  design_ready
  verification_flags_json
  designer_actions_json
  baseline_json
  field_json
  conflicts_json

pole_reviews
  id
  pole_id
  reviewer
  review_date
  status
  notes

evidence_files
  id
  pole_id
  file_type
  file_path
  display_name
  source_folder
```

Review status values:

- `NOT_REVIEWED`
- `REVIEWED`
- `APPROVED_FOR_DESIGN_PREPARATION`
- `FLAGGED`
- `AWAITING_DNO_DATA`
- `REQUIRES_RESURVEY`

Approval wording must remain careful. `APPROVED_FOR_DESIGN_PREPARATION` means the designer has reviewed the evidence and can proceed with preparation tasks, not that the pole is certified for final design.

## Frontend Views

### Dashboard

Shows all imported pipeline runs.

Display:

- Run name.
- Import date.
- Baseline source.
- Field source.
- Total poles.
- Match rate.
- Design-blocked count.
- Review progress.
- Status.

### Run Detail

Shows the summary for one run.

Cards:

- Total baseline poles.
- Field evidence poles.
- Matched poles.
- HIGH, MEDIUM, LOW, and UNMATCHED counts.
- Design-blocked poles.
- Poles awaiting DNO data.
- Poles requiring re-survey.

Charts are optional for v1. Tables and counts are sufficient.

### Pole List

Table of all poles in the run.

Columns:

- Support number.
- Match confidence.
- Match type.
- Design status.
- Review status.
- Verification flags.
- Conflict count.
- Primary action required.

Filters:

- Match confidence.
- Design blocked.
- Verification flag type.
- Review status.
- Conflict flag.
- Unmatched baseline.
- Unmatched field.

### Pole Detail

The main designer review screen.

Layout:

- Left panel: field photos and map screenshots.
- Right panel: match data, verification flags, conflicts, and actions.
- Bottom section: notes, parsed observations, and raw evidence text.

The page must make source authority obvious. Field observations should not be presented as certified engineering data.

### DNO Request View

Generates a structured DNO data request based on unresolved verification flags.

The designer should be able to:

- Select all unresolved poles or filter by flag type.
- Preview the request.
- Export Markdown, CSV, or DOCX in later phases.
- Include support numbers and reasons for each requested data item.

## Pole Detail Card

Each pole card should present the record in a predictable structure.

```text
HEADER
Support No: 903203
Confidence: HIGH
Design Status: BLOCKED
Primary Action: Obtain DNO voltage, conductor, and pole class data

TABS
[Evidence] [Match Data] [Verification] [Notes] [Review History]
```

### Evidence Tab

- Field photo carousel.
- Map screenshots.
- Evidence file count.
- Evidence quality score.
- Special flags, such as no popup, joint user, restricted access, or OH/UG transition.

### Match Data Tab

- Baseline pole ID.
- Baseline support number.
- Coordinates.
- Match type.
- Match confidence.
- Conflict flags.
- Source fields used for matching.

### Verification Tab

Show each verification flag with a clear state and action:

- Voltage verification required.
- Conductor verification required.
- Pole class verification required.
- Condition verification required.
- Identity verification required.
- Equipment conflict flag.

Each flag should include why it exists and what the designer should do next.

### Notes Tab

- Raw survey notes.
- Parsed notes fields, where available.
- Access constraints.
- Observed defects.
- Equipment observations.
- Survey limitations.

### Review History Tab

- Review status changes.
- Reviewer notes.
- Approval or flagging history.
- Export history, if available.

Action buttons:

- Mark reviewed.
- Approve for design preparation.
- Flag for attention.
- Mark awaiting DNO data.
- Mark re-survey required.
- Add note.

## Implementation Phases

### Phase 5.1 - Backend API

Estimated duration: 3 to 4 weeks.

Deliverables:

- API application structure.
- Database models and migrations.
- Stage 4C run import.
- Pole list and detail endpoints.
- Evidence file endpoints.
- Review action endpoints.
- Basic authentication.

Acceptance:

- P_LOCAL_001 Stage 4C output can be imported.
- API returns run summary and pole detail accurately.
- Review actions persist and can be retrieved.

### Phase 5.2 - Frontend Core

Estimated duration: 4 to 5 weeks.

Deliverables:

- Dashboard.
- Run detail page.
- Pole list with filters.
- Pole detail page.
- Evidence viewer.
- Verification flag display.

Acceptance:

- Designer can navigate from run summary to pole detail.
- Photos and map screenshots are viewable.
- Verification flags are visible without reading raw JSON.
- Filters work on confidence, design status, and review status.

### Phase 5.3 - Workflow Features

Estimated duration: 2 to 3 weeks.

Deliverables:

- Review tracking.
- Approval and flagging actions.
- DNO data request generator.
- CSV or Markdown export.
- Review summary export.

Acceptance:

- Designer can complete a review pass for a run.
- DNO data request can be generated from unresolved flags.
- Exported request uses support numbers and specific missing data items.

### Phase 5.4 - Polish and Pilot

Estimated duration: 2 to 3 weeks.

Deliverables:

- UI refinement from designer feedback.
- Performance improvements for large photo sets.
- Pilot deployment guide.
- Designer user guide.
- Pilot feedback capture.

Acceptance:

- At least one designer can use the UI on a real or representative job.
- Feedback is recorded and converted into follow-up issues.
- Known limitations are documented.

Total estimated duration: 11 to 15 weeks.

## Acceptance Criteria

Stage 5 is complete when:

- A designer can import or open a Stage 4C run.
- A designer can review each pole with photos, notes, match data, and verification flags.
- A designer can mark poles as reviewed, approved for design preparation, flagged, awaiting DNO data, or requiring re-survey.
- The system can generate a structured DNO data request from unresolved flags.
- The UI handles P_LOCAL_001 correctly.
- The UI remains clear that DNO engineering data is required before final design.
- At least one ICP or contractor designer has reviewed a pilot run and provided feedback.

## Risk Register

### Risk 1: Photo File Performance

Large evidence sets may load slowly.

Mitigation: Use thumbnail generation, lazy loading, and pagination where needed.

### Risk 2: Source Authority Confusion

Users may treat field observations as certified engineering data.

Mitigation: Label baseline, field, and DNO-required values clearly. Keep verification flags visible.

### Risk 3: Multi-user Review Conflicts

Two reviewers may edit the same pole status.

Mitigation: Store reviewer, timestamp, and status history. Use PostgreSQL for team deployment.

### Risk 4: Scope Creep Into Design Automation

Users may request PoleCAD integration or automatic design generation during Stage 5.

Mitigation: Keep Stage 5 focused on review workflow and exports. Defer CAD integration to Stage 6.

### Risk 5: DNO Format Variability

Different DNO baseline formats may produce sparse or inconsistent merged records.

Mitigation: UI must handle missing fields gracefully and show source authority for every value.

## Definition of Done

- Backend API endpoints are tested with pytest and httpx.
- Frontend components are tested with React Testing Library or equivalent.
- P_LOCAL_001 run imports and displays correctly.
- Verification flags appear consistently in list and detail views.
- Review actions persist and export correctly.
- DNO data request export includes specific support numbers and required data items.
- Documentation explains the designer workflow.
- Deployment instructions exist for a local pilot.
- Stage 5 remains governance-safe: no automatic design approval, no inferred engineering certification, and no replacement of DNO records.
