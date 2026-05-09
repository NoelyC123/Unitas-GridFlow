# Stage 4 — Structured Field Capture

## Why Stage 4 Exists

GridFlow's earlier stages parse and interpret raw Trimble controller dumps.
The C2E2 field reality audit ([AI_CONTROL/31_REAL_JOB_FIELD_REALITY_REPORT.md](../AI_CONTROL/31_REAL_JOB_FIELD_REALITY_REPORT.md))
confirmed that the Trimble export format only carries **6 useful per-pole
fields** (`pole_id`, `easting`, `northing`, `height`, `structure_type`,
`location`), and that height/location are deliberately partial because
surveyors only annotate key features. Many fields a designer needs
— pole class, condition, defects, voltage, conductor, stays, equipment —
are simply not there.

Stage 4 is the future structured-capture layer that fills that gap.
Surveyors will record these fields directly (tablet-based capture), and
office/design staff will be able to add supplementary records where the
field crew did not. The result is a per-pole record that combines:

- the **measured** data the Trimble GNSS controller produced, and
- the **structured** designer-grade attributes the survey could not carry.

This document describes the foundation: a canonical schema, validators,
and a CSV template generator. **No app runtime behaviour changes.**

## Three Field Categories — Don't Conflate Them

GridFlow now has three distinct sources of per-pole data. The schema in
[app/structured_capture_schema.py](../app/structured_capture_schema.py)
keeps them strictly separate.

| Category | Origin | Examples | Where |
|---|---|---|---|
| Captured (Trimble) | Survey controller | `pole_id`, `easting`, `northing`, `height`, `structure_type`, `location` | live today |
| Derived (GridFlow) | QA / sequencer / pipeline | `record_role`, `relationship`, `qa_status`, `asset_intent`, `stay_evidence_status` | live today |
| Stage 4 structured | Future structured capture | `pole_class`, `condition`, `defect_type`, `voltage_carried`, `stay_type`, `equipment_type`, capture metadata | **not live** |

Every Stage 4 field carries `current_status: "stage4_future_capture"` and
`source: "structured_capture"` so callers can never accidentally treat a
Stage 4 placeholder as if it had been measured today.

## Fields Absent from Trimble Exports

The reality report enumerates fields surveyors do not record:

- **Pole specification** — `pole_class`, `pole_strength`, `pole_material`, `specification`
- **Condition / defects** — `condition`, `defect_type`, `defect_severity`, `defect_notes`
- **Electrical / conductor** — `voltage_carried`, `conductor_type`, `conductor_size`, `phase_configuration`
- **Structural support** — `stay_present`, `stay_type`, `stay_condition`, `lean_direction`, `lean_severity`
- **Equipment / pole-top** — `equipment_present`, `equipment_type`, `equipment_condition`, `equipment_notes`

Stage 4 also adds **capture metadata** (who captured the row, when, with
what confidence, source) so any downstream consumer can audit provenance
without inferring it from filenames or upload timestamps.

## How Structured Capture Complements Trimble

Trimble controllers remain the source of truth for geometry. Stage 4
records are **per-pole keyed by `pole_id`** so they can be joined to the
existing parsed survey output without changing the controller workflow.

The intended end-to-end flow (post-Stage-4 integration, **not built yet**):

1. Surveyor captures geometry on the Trimble controller as they do today.
2. Surveyor (tablet) or designer (office) fills in the Stage 4 structured
   row for each pole that needs design-grade attributes.
3. GridFlow upload accepts both files; the Stage 4 row is validated using
   `app.structured_capture_validators.validate_stage4_row`.
4. The popup, QA engine, and design-readiness gates pull from the merged
   per-pole record while preserving the trust labels for each source.

Until that integration lands, the schema and validators are available as
**library code** for any internal tool that wants to start collecting
this data on the side (e.g. an offline spreadsheet review).

## Field Groups

| Group | Fields |
|---|---|
| Pole specification | `pole_class`, `pole_strength`, `pole_material`, `specification` |
| Condition / defects | `condition`, `defect_type`, `defect_severity`, `defect_notes` |
| Electrical / conductor | `voltage_carried`, `conductor_type`, `conductor_size`, `phase_configuration` |
| Structural support | `stay_present`, `stay_type`, `stay_condition`, `lean_direction`, `lean_severity` |
| Equipment / pole-top | `equipment_present`, `equipment_type`, `equipment_condition`, `equipment_notes` |
| Capture metadata | `capture_source`, `captured_by`, `capture_date`, `confidence_level`, `verification_required` |

Group identifiers are stable machine names; human-friendly labels are in
`structured_capture_schema.GROUPS`.

## Validation Rules

`app.structured_capture_validators` provides pure helpers (no Flask, no
pandas, no I/O). Result shape:

```python
{
    "valid": bool,
    "errors": list[str],
    "warnings": list[str],
    "normalised": dict[str, Any],
}
```

Key rules:

- Required fields (`capture_source`, `captured_by`, `capture_date`) must be
  non-blank.
- Enum fields are case-insensitive on input but normalise to the canonical
  case stored in the schema (e.g. `LV` / `11kV` / `33kV` / `110kV`).
- Boolean-style fields (`stay_present`, `equipment_present`,
  `verification_required`) accept `yes/y/true/1`, `no/n/false/0`,
  `unknown/?/blank` and normalise to `yes` / `no` / `unknown`.
- Unknown column names produce a warning (not an error) so partial
  templates from older versions still validate.
- `classify_stage4_completeness(row)` returns `empty` / `partial` /
  `minimum` / `complete` and is the recommended gate for "is this row
  worth merging into the per-pole record yet?".

## How Stage 4 Will Connect To Live Flows (Future Work)

The intentional design of this foundation is that **none of these touch
points exist yet**. They are the contract for the next stage of work:

- `app/routes/api_intake.py` will accept an additional Stage 4 file upload
  alongside the controller dump, validate it via this module, and merge
  per-pole records by `pole_id`.
- `app/qa_engine.py` will consume Stage 4 condition/defect/equipment
  fields to lift current "Not recorded in survey" placeholders into
  evidence-bearing checks.
- `app/static/js/map-viewer.js` popup rendering will surface Stage 4
  fields with a trust label (`Source: structured capture`) so designers
  can tell measured from declared.

Until those changes land, Stage 4 fields **must not** appear in the popup
as if they were captured.

## What Is NOT Implemented Yet

- No upload route accepts a Stage 4 file.
- No part of the live request path imports
  `app.structured_capture_schema` or `app.structured_capture_validators`.
- No QA gate, design-readiness gate, or popup field uses Stage 4 data.
- No persistence layer stores Stage 4 rows against existing jobs.

This foundation is the schema, validators, template generator, and tests.
Integration is a separate task on a separate branch.

## Source-of-Truth References

- [AI_CONTROL/31_REAL_JOB_FIELD_REALITY_REPORT.md](../AI_CONTROL/31_REAL_JOB_FIELD_REALITY_REPORT.md)
- [AI_CONTROL/11_C2E2_POPUP_EXPANSION_SPEC.md](../AI_CONTROL/11_C2E2_POPUP_EXPANSION_SPEC.md)
- [AI_CONTROL/12_C2E2_FIELD_MAPPING_AUDIT.md](../AI_CONTROL/12_C2E2_FIELD_MAPPING_AUDIT.md)
- [AI_CONTROL/02_CURRENT_TASK.md](../AI_CONTROL/02_CURRENT_TASK.md)
