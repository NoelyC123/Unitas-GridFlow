# Development Completed So Far

This file summarises the current implementation state for AI tools that need a fast project update.

## Current Product State

Unitas GridFlow currently has a working Stage 1 post-survey QA gate.

It can process raw Trimble/GNSS controller dump CSVs and produce useful pre-design intelligence before a designer opens PoleCAD.

## Completed Capabilities

- Raw Trimble GNSS/controller dump CSV parsing.
- Coordinate reference system detection.
- Support for Irish Grid TM65, ITM and OSGB27700 context.
- Coordinate conversion for map display.
- Record-role classification into structural, context and anchor-type records.
- Classification of context features such as Hedge, Fence, BTxing, LVxing, Road and Ignore.
- Detection of EX/PR replacement pairs.
- Design narrative generation for replacement pairs and design handoff context.
- Confidence-aware QA checks using PASS/WARN/FAIL severity tiers.
- Seven scoped design evidence gates:
  - Position
  - Structure Identity
  - Structural Spec
  - Stay Evidence
  - Clearance Design
  - Conductor Scope
  - Overall Handoff Status
- Interactive Leaflet map with design-readiness signals.
- PDF pre-design briefing report.
- DNO rulepack inference from geography.
- Validation against real Gordon, NIE and SPEN-style survey files.
- Active test suite with 211 passing tests.
- Active CI with pre-commit and pytest.

## Phase 3A Completed

Phase 3A improved real-file handling by:

- Treating crossing codes such as BTxing, LVxing, Road and Ignore as context, not structural records.
- Reducing false QA positives for height and span checks.
- Reducing the span minimum threshold from 10m to 5m to better match dense real survey jobs.
- Cleaning location field contamination from Trimble compound codes such as `Pol:LAND USE`.
- Adding targeted tests for these changes.

## Current Development Focus

Current focus is Stage 2: D2D elimination.

Stage 2A and Stage 2B have now been implemented and validated against the current real-file set.

## Stage 2A Implemented

Stage 2A commit: `5f99bf0`

Stage 2A added:

- `app/route_sequencer.py`
- `app/routes/d2d_export.py`
- `tests/test_route_sequencer.py`
- D2D candidate CSV download route
- `sequenced_route.json` saved per job
- `sequence_summary` in job metadata
- Map-view D2D export button
- Graceful unavailable state when D2D export cannot be generated

Stage 2A can now produce a provisional designer-readable export containing:

- Automatic pole sequencing.
- EXpole matching/replacement references.
- Span-to-next calculations.
- Deviation angle calculations.
- Candidate section breaks.
- Context features separated from the structural chain.

## Stage 2B Implemented

Stage 2B commit: `54417ba`

Stage 2B validation bugfix commit: `e51d0ee`

Stage 2B added:

- detached / `not required` record handling
- section-aware sequencing
- Angle records as section candidates
- `sections` metadata
- global `design_pole_number`
- section-local `section_sequence_number`
- interleaved D2D working view
- `/d2d/interleaved/<job_id>` endpoint
- confidence warnings for high-ambiguity files
- clean-chain export preserved and extended

## Current Validation Result

Stage 2B has passed the current real-file validation set:

- Gordon original: passed.
- Gordon manual PR1/PR2 comparison: passed.
- `28-14 4-474.csv`: passed with expected high-ambiguity warning.
- `28-14 513 (2).csv`: passed clean/simple case.
- `28-14 474c.csv`: passed.

Stage 2B is accepted as a strong D2D replacement baseline, but Stage 2 is not formally closed yet.

## Current Decision Point

The next decision is whether to:

1. do a small Stage 2C polish pass, focused on output clarity and validation reporting, or
2. move to a Stage 2 completion review.

## Important Boundary

Do not jump ahead to the tablet app, live sync, designer workspace or DNO submission layer until Stage 2 is properly validated.
