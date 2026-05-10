# 43 — Stage 4 Readiness Specification

Snapshot: master HEAD `58235a1`, specification date 2026-05-10.

## Purpose

This file defines the readiness boundary for Stage 4 structured capture before
any runtime integration starts. It is a planning/control document only. It does
not authorise upload-route, QA, popup, review workspace, geometry, or intake
pipeline changes.

Stage 4 remains library-only on current master:

- `app/structured_capture_schema.py`
- `app/structured_capture_validators.py`
- `scripts/generate_structured_capture_template.py`
- `templates/structured_capture_template.csv`
- `docs/STAGE4_STRUCTURED_CAPTURE.md`
- `docs/STRUCTURED_CAPTURE_TEMPLATE_GUIDE.md`

## Source Inputs

This specification is based on:

- `AI_CONTROL/42_NEXT_PHASE_READINESS.md`
- `AI_CONTROL/40_VALIDATION_AUDIT.md`
- `docs/STAGE4_STRUCTURED_CAPTURE.md`
- `docs/STRUCTURED_CAPTURE_TEMPLATE_GUIDE.md`
- `app/structured_capture_schema.py`
- `app/structured_capture_validators.py`
- `app/field_reference.py`
- `templates/structured_capture_template.csv`

## Current Stage 4 State

The Stage 4 foundation defines future structured fields for pole
specification, condition, defects, electrical/conductor, structural support,
equipment, and capture metadata. These fields are not wired into the live app
runtime.

Current guarantees:

- Stage 4 schema fields carry `current_status: "stage4_future_capture"`.
- Stage 4 schema fields carry `source: "structured_capture"` inside the Stage
  4 schema module.
- Validators are pure helpers with no Flask, pandas, persistence, or upload
  route dependency.
- The generated CSV template is not currently accepted by live uploads.
- C2E2 popups still show only the reality-based Trimble/derived field scope.

Current gaps:

- Structured rows cannot be safely keyed to current map/support records yet.
- A valid literal value of `none` is erased by current blank-token handling.
- The live popup field reference has no registered `structured_capture`
  source category.

## Known Stage 4 Blockers

### VLD-1: `none` Blank-Token Handling

`app/structured_capture_validators.py` currently includes `"none"` in
`_BLANK_TOKENS`. That makes `is_blank("none")` return `True`.

This is unsafe because the Stage 4 schema uses `none` as a meaningful enum value
for:

- `stay_type`
- `equipment_type`
- `lean_direction`
- `lean_severity`

Effect if runtime integration starts before the fix:

- A surveyor/designer can explicitly record "no stay", "no equipment", or "no
  lean", but GridFlow would normalise that answer to blank/unspecified.
- The UI could falsely say the value was not captured.
- QA/reporting could treat an explicit negative as missing evidence.

### VLD-2: Missing `pole_id` / Row Identity Handling

The current template headers begin with `pole_class`, not `pole_id`, and the
schema has no `pole_id`, `project_id`, or `file_id` fields.

This is unsafe because Stage 4 integration is intended to merge structured rows
with existing Trimble/map records by support identity.

Effect if runtime integration starts before the fix:

- Structured values cannot be attached to a specific pole with enough
  confidence.
- Coordinate/proximity matching would be tempting but unsafe as a first
  integration step.
- Duplicate or orphan structured rows could be silently merged into the wrong
  support record.

### VLD-3: Missing `source="structured_capture"` Registration

`app/structured_capture_schema.py` knows about `source: "structured_capture"`,
but `app/field_reference.py` currently documents and uses only:

- `survey`
- `derived`
- `trimble_attr`

This is unsafe because future popup/API/report surfaces need a registered
source category before Stage 4 values are displayed.

Effect if runtime integration starts before the fix:

- Stage 4 values may be displayed as normal survey values.
- Popup trust labels could blur measured Trimble evidence and structured
  supplementary capture.
- C2E2 truthfulness could regress by reintroducing unavailable fields as if
  they came from the controller export.

## Safe Implementation Order

The blockers must be fixed in this order:

1. **Stage 4A: library correctness fixes**
   - Remove the `none` ambiguity first.
   - Add identity fields to the schema/template and validators.
   - Register `structured_capture` as a source category in the live field
     reference only after source semantics are clear.
2. **Stage 4B: schema/field validation**
   - Strengthen validation around row identity, duplicates, unknowns, blank
     handling, metadata, and source provenance.
3. **Stage 4C: controlled runtime integration**
   - Accept and store Stage 4 CSV data only after library correctness is tested.
   - Merge by `pole_id` only for the first runtime release.
4. **Stage 4D: browser/review workspace surfacing**
   - Surface structured values with explicit provenance labels after controlled
     runtime integration is stable.

The first implementation branch must not combine 4A with runtime upload or UI
surfacing.

## Allowed Future Touch Points

Stage 4 implementation may later touch these areas, but only in the phase where
they are explicitly in scope:

- `app/structured_capture_schema.py`
- `app/structured_capture_validators.py`
- `scripts/generate_structured_capture_template.py`
- `templates/structured_capture_template.csv`
- Stage 4 docs and control docs
- New tests for structured capture schema, validators, template generation,
  merge rules, and runtime integration
- Later Stage 4C only: intake/upload route code required to accept a Stage 4
  CSV alongside a Trimble job
- Later Stage 4C only: a merge service that joins structured rows to Trimble
  records by `pole_id`
- Later Stage 4D only: popup/API/review workspace display code that labels
  structured values as structured capture

## Must Not Touch Yet

Until Stage 4A and Stage 4B are complete and green, Stage 4 work must not touch:

- Live upload runtime integration
- `app/routes/api_intake.py`
- `app/controller_intake.py`
- `app/qa_engine.py`
- `app/geometry_pipeline.py`
- `app/span_generator.py`
- C2E2 popup field scope or section structure
- Review workspace behaviour
- Manual review harness semantics
- Archive files
- Any inference that treats unavailable Trimble fields as missing survey data

## Runtime Truthfulness Rules

When Stage 4 eventually surfaces in the app:

- Trimble measured geometry remains the source of truth for position and measured
  height.
- Structured capture values must never overwrite measured Trimble evidence
  silently.
- Every structured value displayed in a popup/API/report must carry provenance:
  value, source, confidence, captured_by, capture_date, and verification state
  where available.
- Missing Stage 4 values must not create long "not captured" popup sections.
- C2E2 reality-based popup fields remain closed unless Stage 4 has supplied a
  real captured value.

## Readiness Verdict

Stage 4 specification work is ready now.

Stage 4 implementation is **not ready** until the three blockers above have
dedicated tests and are fixed in the safe order.
