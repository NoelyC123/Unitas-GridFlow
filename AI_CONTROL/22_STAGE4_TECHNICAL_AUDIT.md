# 22 — Stage 4 Structured Capture Technical Audit

## Purpose

Independent technical audit of the Stage 4 structured-capture foundation
(`stage4-structured-capture-foundation-complete`). Performed on
2026-05-10 against master HEAD `212bd23`.

This audit is read-only. It does not modify schema, validators, template
generator, or runtime code. Findings feed into Codex's Stage 4
Integration Plan but do not duplicate it.

## Scope of audit

- [`app/structured_capture_schema.py`](../app/structured_capture_schema.py)
- [`app/structured_capture_validators.py`](../app/structured_capture_validators.py)
- [`scripts/generate_structured_capture_template.py`](../scripts/generate_structured_capture_template.py)
- [`templates/structured_capture_template.csv`](../templates/structured_capture_template.csv)
- The three Stage 4 test files
- The two Stage 4 docs
- Boundary points in `app/routes/api_intake.py`, `app/qa_engine.py`,
  `app/field_reference.py`, `app/field_validators.py`

## What currently exists

### Schema (`app/structured_capture_schema.py`)

- 26 field definitions across 6 canonical groups (`pole_specification`,
  `condition_defects`, `electrical_conductor`, `structural_support`,
  `equipment_pole_top`, `capture_metadata`).
- Every definition carries `current_status="stage4_future_capture"` and
  `source="structured_capture"` (constants `CURRENT_STATUS`, `SOURCE`).
- Reusable enum vocabularies: `CONDITION_VALUES`, `SEVERITY_VALUES`,
  `LEAN_SEVERITY_VALUES`, `VOLTAGE_VALUES`, `PRESENCE_VALUES`,
  `CONFIDENCE_VALUES`.
- Required fields (3): `capture_source`, `captured_by`, `capture_date`.
- Helpers: `get_stage4_field_definition`, `get_stage4_fields`,
  `get_stage4_fields_by_group`, `get_stage4_required_fields`,
  `get_stage4_template_headers`, `is_stage4_field`.
- An alias map built once at import time resolves common synonyms
  (`class` → `pole_class`, `voltage` → `voltage_carried`, etc.) but is
  conservative: not every field has aliases.

### Validators (`app/structured_capture_validators.py`)

- Pure functions, no Flask, no pandas, no I/O.
- Returns `{valid: bool, errors: list[str], warnings: list[str], normalised: dict}`.
- Token sets: `_BLANK_TOKENS = {"", "n/a", "na", "none", "null", "tbc", "?"}`,
  `_TRUE_TOKENS`, `_FALSE_TOKENS`, `_UNKNOWN_TOKENS`.
- `validate_allowed_value` is case-insensitive and case-preserving for
  enums (e.g. accepts `"11kv"`, returns `"11kV"`).
- `validate_stage4_row` accumulates errors instead of raising; treats
  unknown columns as warnings, not errors.
- `classify_stage4_completeness` returns `"empty"` / `"partial"` /
  `"minimum"` / `"complete"`.

### Template generator (`scripts/generate_structured_capture_template.py`)

- CLI with `--output PATH`, `--include-descriptions`, `--stdout`.
- Default output: `templates/structured_capture_template.csv`.
- Pure stdlib (`argparse`, `csv`, `pathlib`).
- Imports only `app.structured_capture_schema` (not the Flask app).
- `render_template(include_descriptions=...)` is the pure render function;
  `main(argv=None)` is the CLI entry point.
- Comment header (with `--include-descriptions`) groups every field with
  its allowed values, unit, and description.

### Tests

| File | Tests | Coverage focus |
|---|---:|---|
| `tests/test_structured_capture_schema.py` | 8 | Group + field presence, header headers, required-field set, alias resolution, status/source constants. |
| `tests/test_structured_capture_validators.py` | 10 | Blank detection, bool normalisation, enum acceptance + rejection, required-field check, row + rows validation, completeness classification, normalisation, unknown columns. |
| `tests/test_generate_structured_capture_template.py` | 5 | CSV output, header equivalence to schema, description block, `main(argv=None)`, no-Flask sabotage. |

23 tests total.

## What tests currently cover

- Every documented helper function has at least one direct test path.
- Boolean/enum/blank inputs are exercised at the unit level.
- The template generator is verified to write a header-only CSV that
  matches `get_stage4_template_headers()`.
- `test_no_app_runtime_needed` asserts that the generator does not
  trigger `app.create_app` (proves the boundary is clean).

## What tests do NOT currently cover

| Gap | Risk |
|---|---|
| Round-trip — write template → read it back → validate row | A surveyor's actual end-to-end workflow is not tested. |
| Enum values that overlap with `_BLANK_TOKENS` (e.g. `stay_type: none`, `equipment_type: none`, `lean_direction: none`, `lean_severity: none`) | The validator silently maps these to `None`, erasing real data (see "What validators do not guarantee" below). |
| `capture_date` format validation (the schema declares `type="date"` but no test exercises a malformed date). | Bad dates pass validation today. |
| `validate_stage4_rows` against a list with mixed valid/invalid rows | Per-row aggregation behaviour is only loosely covered. |
| `pole_id` joining behaviour | No test exists because the schema does not yet carry `pole_id` (see schema gap below). |
| Conflict handling between two rows with the same intended pole | Not testable today — the schema has no row identity. |

## What validators guarantee

- A row missing any of `capture_source` / `captured_by` / `capture_date`
  is rejected with a "Required field missing" error.
- An enum value not in `allowed_values` is rejected with a `field: value
  is not one of [...]` error.
- An unknown field name is rejected with a "Unknown Stage 4 field"
  error in `validate_allowed_value` (but only a *warning* in
  `validate_stage4_row` so partial templates still validate).
- Case-insensitive enum input is normalised to the schema's canonical
  case (`"11kv"` → `"11kV"`).
- Aliases resolve before validation (`voltage` is treated as
  `voltage_carried`).

## What validators do NOT guarantee

1. **`"none"` as a real enum value is erased.** `_BLANK_TOKENS` includes
   the string `"none"`, but the schema lists `"none"` as a valid enum
   member for `stay_type`, `equipment_type`, `lean_direction`, and
   `lean_severity`. `is_blank("none")` returns `True`, so:
   - `validate_allowed_value("stay_type", "none")` returns `valid=True`
     with `normalised["stay_type"] = None` — the same as if the cell
     were left empty.
   - A row stating "no stay on this pole, no pole-top equipment, no
     lean" — i.e. the most carefully captured row possible — is treated
     as if those fields were not captured.
   - `classify_stage4_completeness` for such a row returns `"minimum"`,
     not `"complete"`.
   - **Reproduced on master at `212bd23`.**

2. **`capture_date` is not format-checked.** The schema declares
   `type="date"` but the validator only checks `is_blank`. A row with
   `capture_date: "yesterday"` or `"2026-13-99"` passes validation.

3. **Free-text fields are not bounded.** `defect_notes`, `equipment_notes`,
   `pole_strength`, `specification`, `pole_class`, and `conductor_size`
   accept arbitrary strings of any length. A 50 KB `defect_notes` would
   pass validation.

4. **`captured_by` is not normalised.** Whitespace is stripped but case
   is preserved verbatim. Two rows from the same surveyor recorded as
   `"N. Collins"` and `"N Collins"` are different identities.

5. **No cross-field consistency checks.** A row with
   `stay_present: "no"` plus `stay_type: "down"` is accepted as valid.
   A row with `equipment_present: "no"` plus `equipment_type:
   "transformer"` is also accepted.

6. **No row identity.** `validate_stage4_row` does not require any field
   that identifies which pole the row describes (see schema gap below).

7. **Unknown columns are warnings, not errors.** A typo like
   `pol_class` instead of `pole_class` produces a warning and the
   intended value is dropped silently. The template generator and the
   alias map cover the canonical names but not all plausible mistakes.

## What the template generator produces

- Default invocation writes a single-row CSV: 26 column headers, no
  data rows.
- With `--include-descriptions`: 38 prefixed `#` comment lines (one per
  field plus group separators) followed by the same 26-column header.
- Headers are emitted in canonical declaration order (matches
  `get_stage4_template_headers()`).
- The CSV is `utf-8` encoded.
- Multiple invocations are idempotent — each run overwrites the target
  file with the current schema. Safe to wire into a build.

## Assumptions embedded in the schema

| Assumption | Where | Risk if wrong |
|---|---|---|
| Stage 4 rows are per-pole and linked by an external `pole_id` | docs/STAGE4 | Schema does not carry the join key. Integration must add it. |
| Required fields are *only* the capture metadata three | schema | Forces minimum-row to carry no asset data. Reasonable; document explicitly. |
| English-language enum values are sufficient | schema | Multi-language survey teams would need translation layer. |
| Voltage values cover GB DNO range only (LV / 11kV / 33kV / 110kV) | schema | 6.6kV (some legacy NIE), 22kV (some farm-supply), 132kV are absent. |
| `stay_type` includes `"none"` as a meaningful value | schema | Conflicts with validator blank-token behaviour (see above). |
| `confidence_level` and `verification_required` are independent | schema | A "low confidence + verification not required" row is allowed and probably wrong. |

## What code currently imports Stage 4 modules

Verified by `grep -rn "structured_capture" app/ scripts/ tests/` against
master `212bd23`. Imports of `app.structured_capture_schema` or
`app.structured_capture_validators`:

| Importer | Purpose |
|---|---|
| `app/structured_capture_validators.py` | Schema → validators dependency. |
| `scripts/generate_structured_capture_template.py` | Template generator → schema. |
| `tests/test_structured_capture_schema.py` | Tests. |
| `tests/test_structured_capture_validators.py` | Tests. |
| `tests/test_generate_structured_capture_template.py` | Tests + module under test. |

Imports from any module under `app/routes/`, `app/qa_engine.py`,
`app/controller_intake.py`, `app/geometry_pipeline.py`,
`app/span_generator.py`, `app/field_reference.py`,
`app/field_validators.py`, `app/static/`, or `app/templates/`:

> **None.**

## Confirmation that runtime upload path does not yet use Stage 4

- `app/routes/api_intake.py::process_job` — does not import Stage 4
  modules; does not read `templates/structured_capture_template.csv`.
- `app/routes/api_intake.py::_build_feature_collection` — does not
  surface any value sourced from Stage 4 schema.
- `app/qa_engine.py::run_qa_checks` — no Stage 4 imports; no rules
  reference Stage 4 field names.
- `app/static/js/map-viewer.js` — no Stage 4 references; popups render
  only `field_reference.py::FIELD_DEFINITIONS` entries.

The previous Stage 4 foundation commit message and
`docs/STAGE4_STRUCTURED_CAPTURE.md`'s "What is NOT implemented yet"
list are accurate as of `212bd23`.

## Boundary observation — name collisions waiting to happen

`app/routes/api_intake.py` already aliases several Stage-4-style field
names from the Trimble intake path:

| api_intake alias group | Stage 4 field | Risk on integration |
|---|---|---|
| `material`, `pole_material` (line ~380) | `pole_material` | Both pipelines target the same GeoJSON property. |
| `condition`, `pole_condition`, `asset_condition` (line ~406) | `condition` | Same. |
| `voltage`, `line_voltage`, `network_voltage` (line ~431) | `voltage_carried` (alias `voltage`) | Same. |

For Trimble jobs these properties are always None today (per the C2E2
Field Reality Audit). On Stage 4 integration, the merge step must
clearly mark the source per-pole (`source=trimble` vs `source=stage4`)
or the popup will silently mix the two.

`app/field_reference.py::FIELD_DEFINITIONS` registers field sources of
`"survey"`, `"trimble_attr"`, and `"derived"`. There is no
`"structured_capture"` registered. The popup renderer would not know
how to label a Stage 4 field on its own.

## Technical readiness rating

**Library code: ✅ Production-ready as a foundation.**
- 23 tests passing on master.
- Pure stdlib boundary.
- Schema/validators/template generator are internally consistent.

**For runtime integration: ⚠ Not ready — three blocking gaps.**

1. **No `pole_id` (or any row identity field) in the schema.** A Stage 4
   CSV row cannot be joined to a Trimble pole today.
2. **`"none"` collision between `_BLANK_TOKENS` and valid enum values.**
   Real "no stay / no equipment / no lean" rows are silently erased.
3. **No `source: "structured_capture"` registered in
   `app/field_reference.py::FIELD_DEFINITIONS`.** Popup rendering has
   no path for Stage 4 values.

**For office-side spreadsheet review: ✅ Usable today**, with the
caveat that a designer recording `stay_type: none` will see that value
re-rendered as blank if they round-trip through `normalise_stage4_row`.

## Recommended audit follow-ups

The audit deliberately stops short of writing fixes. Suggested
follow-up tasks (each a separate scoped branch):

1. **Stage 4 schema-row-identity addendum**: add `pole_id` (and
   optionally `project_id` / `file_id`) to the schema and template;
   update validators + tests; do not yet integrate.
2. **Validator `"none"` disambiguation**: remove `"none"` from
   `_BLANK_TOKENS`, add `_NONE_TOKEN` for the explicit "no such item"
   case where the schema allows it; add a regression test for each
   field where `"none"` is a valid enum.
3. **`source: "structured_capture"` registration in field_reference**:
   add Stage 4 fields to `FIELD_DEFINITIONS` (or a parallel registry)
   so the popup renderer has a path to display them with a clear
   source label.
4. **`capture_date` ISO-8601 format check** in `validate_stage4_row`.
5. **Cross-field consistency checks**: `stay_present=no` ⇒
   `stay_type=none`; `equipment_present=no` ⇒ `equipment_type=none`.
   These are warnings, not errors — but worth surfacing.

## Cross-references

- [23_STAGE4_SCHEMA_READINESS_REVIEW.md](23_STAGE4_SCHEMA_READINESS_REVIEW.md) — group-by-group field review.
- [24_STAGE4_RUNTIME_INTEGRATION_RISKS.md](24_STAGE4_RUNTIME_INTEGRATION_RISKS.md) — risks and "do not integrate until" checklist.
- [docs/STAGE4_STRUCTURED_CAPTURE.md](../docs/STAGE4_STRUCTURED_CAPTURE.md) — original Stage 4 rationale.
- [AI_CONTROL/31_REAL_JOB_FIELD_REALITY_REPORT.md](31_REAL_JOB_FIELD_REALITY_REPORT.md) — the audit data motivating Stage 4.
