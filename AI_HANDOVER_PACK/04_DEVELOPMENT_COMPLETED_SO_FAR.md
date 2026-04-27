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

Stage 2A, Stage 2B and Stage 2C have now been implemented and validated against the current real-file set.

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
- `2814_4-474_raw_trimble_export.csv`: passed with expected high-ambiguity warning.
- `28-14 513 (2).csv`: passed clean/simple case.
- `2814_474c_raw_trimble_export.csv`: passed.

Stage 2B is accepted as a strong D2D replacement baseline, but Stage 2 is not formally closed yet.

## Stage 2C Implemented

Stage 2C commit: `4ca6bc0`

Stage 2C polished:

- export headers
- section summaries
- detached/reference wording
- sequence-note wording
- map page download labels
- export filenames (`_d2d_chain.csv`, `_d2d_working_view.csv`)

Stage 2C validation passed on:

- Gordon
- `2814_4-474_raw_trimble_export.csv`
- `28-14 513 (2).csv`
- `2814_474c_raw_trimble_export.csv`

## Stage 2 Closed

Stage 2 completion review was completed and Stage 2 was formally closed. It is accepted as a validated provisional D2D replacement baseline. Final PoleCAD import format remains out of scope until verified with additional evidence.

## Stage 3C Implemented and Validated

Stage 3C commit: `b0b5331`

Stage 3C added a named project container above the existing flat-job model:

- Sequential project IDs: P001, P002, …
- Sequential file IDs within each project: F001, F002, …
- `project.json` aggregates file summaries (total poles, issues, rulepacks)
- Project-aware upload flow with auto-suggested project name from filename
- Project overview page and projects list page
- Map, PDF, D2D chain and working view all routed per project file
- All legacy J##### routes unchanged — full backward compatibility
- 22 unit tests + 9 integration tests
- 244 tests passing, pre-commit clean

Stage 3C manual validation passed:
- Gordon Pt1: project created, map/PDF/D2D all accessible
- 474 + 474c: multi-file project, both files accessible independently
- 513: small file project
- Legacy J##### jobs: backward compat confirmed

## Stage 3B Implemented and Validated

Stage 3B commits: `a9b3ee2`, `7daa5a9`

Stage 3B added designer review and sign-off on auto-generated EXpole pairings:

- `review.json` overlay per project file — original sequenced_route.json never modified
- `app/review_manager.py` — data layer (load/save/delete/build/enrich/apply)
- `app/routes/api_review.py` — GET/POST/DELETE `/api/project/<pid>/file/<fid>/review`
- `app/routes/review_page.py` + `app/templates/review.html` — Bootstrap 5 review page
- D2D Chain and D2D Working View exports apply reviewed pairing overrides
- "Designer Reviewed — <timestamp>" header when reviewed; "provisional" when not
- Reset to auto-generated: single delete of review.json
- Reprocessing clears stale review at start of process_job
- 20 unit tests + 9 integration tests
- 273 tests passing, pre-commit clean

Stage 3B validation passed (all 9 specified integration scenarios).

## Current Development Focus

Stage 3B is closed. The next direction has not yet been decided by the project orchestrator.

Options: Stage 3B polish (section boundary editing, PDF update) vs Stage 3A planning (live intake platform).

## Important Boundary

Do not begin Stage 3A (live intake) or any later stage without explicit orchestrator approval. Do not begin section boundary editing without a new scope brief.
