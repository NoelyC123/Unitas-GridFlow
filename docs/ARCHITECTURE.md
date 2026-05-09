# GridFlow Architecture Overview

This document maps the modules, the data flow, and the points where
future work attaches. It is aimed at developers (Codex, Claude Code,
Cursor, future maintainers) who need to know **where** to make a change
without reading every file.

## Purpose Recap

GridFlow is a **survey-to-design workflow intelligence and automation
tool** for UK electricity overhead line work. It sits between Trimble
GNSS controller exports and office-based design (PoleCAD / D2D /
designer review). It does not replace any of those — it is the pre-CAD
QA gatekeeper, lifecycle visualiser, and (in future stages) the
structured-capture and submission layer.

See [README.md](../README.md) and [CLAUDE.md](../CLAUDE.md) for the
6-stage product vision.

## Data Flow

```
┌────────────────────┐
│ Trimble controller │
│ CSV upload         │
└─────────┬──────────┘
          │
          ▼
┌─────────────────────────────────────┐
│ Controller intake                   │ app/controller_intake.py
│  - parse_raw_controller_dump()      │
│  - parse_controller_csv()           │
│  - detect_grid_crs()                │
│  - convert_grid_to_wgs84()          │
│  - classify_record_roles()          │
└─────────┬───────────────────────────┘
          │
          ▼
┌─────────────────────────────────────┐
│ Cleaning / normalisation            │ app/routes/api_intake.py
│  - clean_numeric_field()            │
│  - clean_text_field()               │
│  - _normalize_dataframe()           │
│  - validate_required_fields()       │
└─────────┬───────────────────────────┘
          │
          ▼
┌─────────────────────────────────────┐
│ Geometry pipeline                   │ app/geometry_pipeline.py
│  - normalize_geometry_for_span_     │
│    generation()                     │
│  - validate_coordinates()           │
│  - calculate_distance() / bearing() │
└─────────┬───────────────────────────┘
          │
          ▼
┌─────────────────────────────────────┐
│ Span generation + sequencing        │ app/span_generator.py,
│  - replacement-pair detection        │ app/replacement_pairs.py,
│  - route sequencing                  │ app/route_sequencer.py
└─────────┬───────────────────────────┘
          │
          ▼
┌─────────────────────────────────────┐
│ QA engine                           │ app/qa_engine.py
│  - run_qa_checks()                  │
│  - classify_height_confidence()     │
│  - classify_source_confidence()     │
│  - parse_attachments()              │
│  - rulepack inference (DNO)         │  app/dno_rules.py
└─────────┬───────────────────────────┘
          │
          ▼
┌─────────────────────────────────────┐
│ GeoJSON / map data assembly         │ app/routes/api_intake.py
│  - _build_feature_collection()      │ ::_build_feature_collection
│  - _build_replacement_links()       │
│  - _build_replacement_narratives()  │
└─────────┬───────────────────────────┘
          │
          ▼
┌─────────────────────────────────────┐
│ Frontend — Leaflet map viewer       │ app/static/js/map-viewer.js
│  - popup rendering                  │ app/static/css/map-viewer.css
│  - review navigation                │ app/templates/map_viewer.html
│  - planner-awareness layer          │
│  - C2F focus / issue filter         │
└─────────┬───────────────────────────┘
          │
          ▼
┌─────────────────────────────────────┐
│ Manual Review Harness               │ scripts/manual_review.py
│  - baseline review suite            │ validation_checklists/*.yml
│  - task-specific YAML checklists    │ validation_runs/<UTC>/...
└─────────────────────────────────────┘
```

## Major Backend Modules

### `app/controller_intake.py`

Trimble-aware parser. Handles the positional / attribute-pair format used
by F001-class files and the more compact 3-column variant. Detects CRS
(Irish Grid TM65, ITM, OSGB27700) and converts to WGS84. Also classifies
records into `structural` / `context` / etc.

**Key entry points:** `parse_raw_controller_dump(path)`,
`parse_controller_csv(df)`, `classify_record_roles(df)`,
`build_completeness_summary(df)`, `build_top_design_risks(...)`,
`build_design_readiness(completeness)`.

### `app/routes/api_intake.py`

Flask blueprint that orchestrates the upload → clean → geometry → span →
QA → GeoJSON pipeline. The single most important entry point is
`process_job(job_short, ...)` which produces the `map_data.json` blob the
viewer reads. Owns the cleaning helpers (`clean_numeric_field`,
`clean_text_field`, `_normalize_dataframe`) and the GeoJSON assembler
(`_build_feature_collection`).

### `app/qa_engine.py`

Confidence-aware QA checker. Severity tiers are PASS / WARN / FAIL.
Functions: `run_qa_checks(df, rules)`,
`classify_height_confidence(record)`,
`classify_source_confidence(record)`,
`parse_attachments(record)`,
`infer_display_network_fields(...)`.

### `app/geometry_pipeline.py`

Pure geometry helpers used before span generation. Snaps near-duplicate
points, removes zero-length sequences, validates coordinates, and
computes distances/bearings.

### `app/span_generator.py`, `app/replacement_pairs.py`, `app/route_sequencer.py`

Span and lifecycle reasoning. Detects EX/PR replacement pairs, sequences
poles into routes, and produces the design-narrative inputs.

### `app/field_reference.py` and `app/field_validators.py`

The canonical field metadata catalogue (labels, aliases, missing-value
wording, units, group membership) plus the field-display helpers
(`is_measured`, `is_missing_legitimate`, `format_field_display`,
`get_popup_display_value`, `classify_field_completeness`).

These are the modules the C2E2 popup truthfulness rules live in. **Do
not bypass them in popup code.**

### `app/structured_capture_schema.py` and `app/structured_capture_validators.py`

Stage 4 foundation. Schema for 26 fields × 6 groups; pure validators.
**Not wired into runtime.** Available as library code for future
integration. See [STAGE4_STRUCTURED_CAPTURE.md](STAGE4_STRUCTURED_CAPTURE.md).

### `app/dno_rules.py`

DNO rulepack inference (which DNO's rules apply to a job, based on
geography). Used by the QA engine to pick the right validation set.

## Frontend Modules

### `app/static/js/map-viewer.js`

The Leaflet viewer. Hosts the popup renderer (C2E2 truthfulness rules
applied here), review navigation, planner-awareness toggle, route
highlighting, release-map flow, and the C2F review-focus / issue-filter
workspace.

The page exposes a `window.gridflowMapViewer` hook that the manual
review harness drives directly via `driver.execute_script(...)`.

### `app/static/css/map-viewer.css`

All styling for the viewer including focused/muted route states,
review-target highlights, and popup layout (constrained to viewport,
internally scrollable).

### `app/templates/map_viewer.html`

Jinja template that scaffolds the page and renders the `#rulepack-badge`,
`#review-map-unlocked-note`, planner-awareness toggle, and the focus
workspace shell.

## Manual Review Harness

`scripts/manual_review.py`. A reusable Selenium-based browser
validation harness that boots its own Flask server, drives headless
Chrome, runs a 10-check baseline suite plus optional task-specific YAML
checklists, and writes timestamped artifacts under `validation_runs/`.

See [README_MANUAL_REVIEW.md](../README_MANUAL_REVIEW.md) for full
usage; see [VALIDATION_WORKFLOW.md](VALIDATION_WORKFLOW.md) for when to
use it in the workflow.

## Project Control Center

A lightweight, repo-based coordination layer — markdown files plus three
small stdlib scripts — that keeps Noel, Codex, Claude Code, Cursor, and
ChatGPT aligned on active task ownership, validation state, and handoff.

Files: `AI_CONTROL/00_PROJECT_BOARD.md`, `AI_CONTROL/03_WORKER_LOG.md`,
`AI_CONTROL/04_VALIDATION_LOG.md`, `AI_CONTROL/05_HANDOFF.md`,
`AI_CONTROL/06_WORKER_RULES.md`.

Scripts: `scripts/start_task.py`, `scripts/log_worker_update.py`,
`scripts/log_validation_run.py`. See [README_PROJECT_CONTROL.md](../README_PROJECT_CONTROL.md).

## Validation-Led Workflow

GridFlow follows a strict **validation-led, not feature-led** model.
Every change must answer:

> Does this improve the reliability, clarity, and design-readiness of
> real survey data?

In practice that means:

1. New behaviour is gated on real survey files (`P008/F001`, `P010`,
   `Gordon`, `Bellsprings`).
2. The manual review harness is the standard validation gate after UI
   changes.
3. Pure unit tests (currently ~860 passing) gate everything else.
4. `pre-commit run --all-files` is required before commit.
5. Project Control Center logs the `validation_runs/...` report path
   and the `failures.json` status.

See [VALIDATION_WORKFLOW.md](VALIDATION_WORKFLOW.md).

## Branch / Worker Workflow

- `master` is the only stable branch.
- Each task lives on its own `<owner>/<slug>` branch (e.g.
  `claude-code/stage4-structured-capture-foundation`).
- Branches must be **scope-pure** — never mix unrelated feature work.
- `app/static/js/map-viewer.js` may only be modified by tasks that
  explicitly say so (popup truthfulness, review navigation, focus mode,
  etc.).
- Archive (`_archive/`) is read-only.

See [AI_CONTROL/06_WORKER_RULES.md](../AI_CONTROL/06_WORKER_RULES.md).

## Extension Points

Where future work attaches without redesigning the pipeline:

### Stage 4 structured capture integration

- New upload route (alongside controller dump) that accepts the Stage 4
  CSV and runs `validate_stage4_rows`.
- Persist Stage 4 rows keyed by `pole_id` against the existing job.
- Merge into the per-pole record consumed by `_build_feature_collection`.
- Update `app/qa_engine.py` to lift current "Not recorded in survey"
  placeholders into evidence-bearing checks when Stage 4 data is
  available.
- Update popup rendering to label Stage 4 fields with `Source:
  structured capture` so designers can tell measured from declared.

### DNO-grade rulepacks

`app/dno_rules.py` already infers the DNO from job geography. The
extension point is the rulepack detail level: clearance schedules,
crossing rules, conductor-specific spans. Each DNO's rulepack should
plug into `run_qa_checks(df, rules)` without needing engine changes.

### PoleCAD export

The end of the pipeline currently produces map data + design-chain
outputs but not a PoleCAD-compatible file. Stage 2 closure will add an
exporter that consumes the same per-pole record the popup reads.

### Lifecycle visualisation expansion

`relationship`, `being_replaced_by`, and `replacing` already exist
per-pole. The viewer surfaces them in popups but does not yet visualise
them across a route (e.g. fade-out for retired poles, badges for new).
That's a frontend-only extension.

### Electrical asset / line / cable interaction layer

`app/electrical_schema.py` and `app/cable_generator.py` model conductors
and cables. Stage 4 conductor fields plus the existing schema will
combine to power a per-span electrical view — currently visualised only
as a route, not a circuit.

## Important Constraints

> **Do not claim Stage 4 is integrated into live upload yet.**
> The schema and validators are library code; nothing in
> `process_job()` reads from them.

> **Do not claim unavailable fields are captured today.**
> The popup must label absent fields per the rules in
> [FIELD_REFERENCE_GUIDE.md](FIELD_REFERENCE_GUIDE.md).

> **Do not redesign the pipeline.**
> The data flow above is intentional. New behaviour fits at the marked
> extension points; if a change does not fit, that is a signal to
> discuss the design with Noel before proceeding.
