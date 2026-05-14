# Stage 5 - Pilot Hardening & Operational Review Layer

## Purpose

Stage 5 prepares GridFlow for real pilot use by ICPs, Tier-1 contractors, designers, and survey teams.

Stage 5 is not primarily more backend processing. Stage 4C has completed the backend reconciliation pipeline. Stage 5 focuses on operational usability, review workflow, evidence navigation, pilot packaging, and designer-facing clarity.

The objective is to make Stage 4C outputs usable in a practical survey-to-design workflow.

## Objectives

Stage 5 objectives:

- Provide an operational review workflow for designers and project teams.
- Make field evidence easy to navigate alongside matched baseline records.
- Improve designer usability for QA outputs and blocker triage.
- Prepare structured DNO data request packs.
- Support real pilot deployment and feedback collection.
- Preserve workflow traceability from baseline record to field evidence to designer action.
- Keep source authority clear: field observations do not replace DNO engineering records.

## Planned Components

### Review Workspace UI

A web-based or app-integrated workspace for reviewing Stage 4C pipeline outputs.

The workspace should show:

- run summary,
- match rate,
- confidence distribution,
- verification flag counts,
- design-blocked poles,
- review progress.

### Map Overlay System

A visual layer for reviewing matched poles in route context.

The overlay should support:

- matched baseline pole locations,
- evidence confidence indicators,
- design blocker indicators,
- unmatched baseline or field records,
- route context where available.

This should not alter geometry generation or claim survey-grade field positioning unless backed by baseline coordinates.

### Evidence / Photo Viewer

A focused evidence viewer for:

- field photos,
- map screenshots,
- notes,
- identity details,
- access constraints,
- special flags.

The viewer must keep field observations separate from DNO-certified data.

### Merged Record Explorer

A per-pole record view showing:

- baseline values,
- field evidence values,
- match confidence,
- verification flags,
- conflict flags,
- designer action required.

### Blocker / Action Dashboard

A dashboard for grouping unresolved work:

- voltage verification required,
- conductor verification required,
- pole class verification required,
- identity confirmation required,
- condition or defect review required,
- evidence gaps,
- unmatched baseline records,
- unmatched field evidence.

### Export Packaging

Exports for pilot and designer workflows:

- DNO data request pack,
- per-pole CSV,
- QA Markdown report,
- review summary,
- evidence manifest.

### Pilot Workflow Support

Pilot support materials should include:

- run checklist,
- surveyor evidence checklist,
- designer review checklist,
- pilot success criteria,
- issue log,
- feedback template.

## Operational Requirements

### Multi-job Handling

Stage 5 must handle multiple pipeline runs without mixing evidence.

Each run should preserve:

- baseline source,
- field evidence source,
- pipeline timestamp,
- match register,
- merged dataset,
- QA report,
- review status.

### Audit Trail

Designer actions must be traceable.

At minimum, record:

- reviewer,
- timestamp,
- status,
- notes,
- action taken,
- export generated.

### Evidence Traceability

Every displayed field observation must link back to its evidence source:

- folder,
- photo file,
- map screenshot,
- notes file,
- pipeline run.

### User Review States

Suggested review states:

- `not_reviewed`
- `reviewed`
- `awaiting_dno_data`
- `requires_resurvey`
- `flagged_for_designer`
- `approved_for_design_preparation`

`approved_for_design_preparation` must not imply final engineering design approval.

### Exportable DNO Request Packs

Stage 5 should generate a DNO request pack that groups support numbers by missing engineering data:

- voltage,
- conductor specification,
- pole class,
- equipment details,
- identity confirmation,
- inspection or condition history.

## Technical Priorities

### Backend Stabilization

Before pilot deployment, Stage 4C should be hardened around:

- input validation,
- error messages,
- malformed evidence folders,
- incomplete baseline rows,
- predictable output schema,
- stable CLI behavior.

### Larger Dataset Validation

P_LOCAL_001 proves the pipeline against a controlled 10-pole ENWL dataset. Stage 5 should validate larger datasets before production use.

Target validation:

- 30 to 50 pole controlled pilot,
- 100+ pole route or project sample where available,
- clear recording of match confidence distribution and unresolved blockers.

### Multi-DNO Testing

ENWL is the primary validated DNO context. Stage 5 should test baseline variability across:

- NGED,
- SPEN,
- SSEN,
- UKPN,
- NPG.

The goal is to identify schema mapping differences, not to claim all DNOs are fully supported before testing.

### Operational Performance Testing

Stage 5 should test:

- larger photo sets,
- many evidence folders,
- repeated pipeline runs,
- export generation time,
- review workspace responsiveness.

## Pilot Goals

Stage 5 pilot goals:

- Evaluate GridFlow with an ICP or Tier-1 contractor workflow.
- Confirm that surveyors can capture evidence consistently.
- Confirm that designers can use QA reports and merged records.
- Validate DNO data request preparation.
- Identify where real workflows need UI support, not just CLI output.
- Record feedback from surveyor, designer, and project manager.

The pilot should answer:

- Does GridFlow reduce ambiguity in survey-to-design handoff?
- Does the QA report help designers request DNO data more clearly?
- Are match confidence and verification flags understandable?
- Is the evidence standard practical in field conditions?
- What is required before broader deployment?

## Success Criteria

Stage 5 pilot hardening is successful when:

- A complete Stage 4C run can be reviewed without reading raw JSON.
- Designers can navigate baseline, field, match, merge, and QA outputs from one workflow.
- Evidence can be traced from QA result back to photos, map screenshots, and notes.
- DNO data request packs can be generated from verification flags.
- Review states persist for each pole or are captured in a controlled export.
- At least one real or representative ICP pilot job is processed end to end.
- Pilot feedback is recorded and converted into product decisions.
- Limitations remain explicit: DNO engineering data is still required for final design.

## Non-goals

Stage 5 must not:

- certify final design,
- perform load calculations,
- infer conductor specifications from images,
- infer pole class from photos,
- replace PoleCAD or CAD design tools,
- replace formal DNO approval,
- hide verification flags to make outputs look more complete than they are.

## Stage 5 Deliverable

The Stage 5 deliverable is an operational review layer that makes the completed Stage 4C backend pipeline usable by real project teams in a pilot setting.

It should prepare GridFlow for controlled ICP evaluation while keeping claims evidence-based and governance-safe.
