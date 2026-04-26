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
- Validation against four real survey files from NIE and SPEN jobs.
- Active test suite with 186 passing tests.
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

Stage 2A has now been implemented as a provisional D2D replacement candidate output.

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

## Current Validation Focus

Stage 2A implementation is complete, but Stage 2 is not complete.

The next phase is real-file validation / Stage 2B refinement:

- Validate the D2D candidate export against `Gordon Pt1 - Original.csv`.
- Compare output against the manual split files:
  - `Gordon Pt1 - POLES 1-12 - PR1.csv`
  - `Gordon Pt1 - POLES 12-20- PR2.csv`
- Confirm whether the sequence matches the real route.
- Confirm whether EXpoles are paired sensibly.
- Separate `not required` / detached points from the main route chain where appropriate.
- Add section-aware sequencing if validation confirms the need.

## Important Boundary

Do not jump ahead to the tablet app, live sync, designer workspace or DNO submission layer until Stage 2 is properly validated.
