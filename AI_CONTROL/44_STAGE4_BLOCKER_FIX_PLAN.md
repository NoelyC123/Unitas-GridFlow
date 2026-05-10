# 44 — Stage 4 Blocker Fix Plan

Snapshot: master HEAD `58235a1`, plan date 2026-05-10.

## Purpose

This plan decomposes the known Stage 4 blockers into small implementation
branches. It defines the safe order, acceptance tests, and stop conditions.

This file is a specification only. It does not implement any Stage 4 runtime
feature.

## Blocker Summary

| ID | Blocker | Severity | Scope | Runtime impact today |
| --- | --- | --- | --- | --- |
| VLD-1 | `"none"` is treated as blank | High | Stage 4 validators | None; Stage 4 not in runtime |
| VLD-2 | No row identity fields | Medium | Stage 4 schema/template/validators | None; Stage 4 not in runtime |
| VLD-3 | No registered structured source in field reference | Low | Field reference/source metadata | None; no Stage 4 popup path |

## Implementation Order

### 1. Fix VLD-1 First: `none` Blank-Token Handling

Rationale:

- It is a pure library correctness bug.
- It can erase explicit negative evidence.
- It affects validation, normalisation, completeness, and future merge behaviour.

Required implementation:

- Remove `"none"` from `_BLANK_TOKENS`.
- Keep `""`, `"n/a"`, `"na"`, `"null"`, `"tbc"`, and `"?"` as blank tokens
  unless a future schema decision says otherwise.
- Confirm `unknown` remains a captured enum value, not a blank.
- Confirm `none` remains valid only where the field schema declares it as an
  allowed enum.
- Confirm fields that do not allow `none` reject it as an invalid value.

Acceptance tests:

- `is_blank("none") is False`.
- `validate_allowed_value("stay_type", "none")` is valid and normalises to
  `"none"`.
- `validate_allowed_value("equipment_type", "none")` is valid and normalises
  to `"none"`.
- `validate_allowed_value("lean_direction", "none")` is valid and normalises
  to `"none"`.
- `validate_allowed_value("lean_severity", "none")` is valid and normalises
  to `"none"`.
- `validate_allowed_value("condition", "none")` is invalid because `condition`
  does not allow `none`.
- Required metadata still fails on blank tokens such as `""`, `"n/a"`, and
  `"null"`.
- `classify_stage4_completeness` does not treat the four valid `none` enum
  values as absent.

Expected test files:

- `tests/test_structured_capture_validators.py`
- Add one targeted regression test per allowed `none` field.

### 2. Fix VLD-2 Second: Row Identity Fields

Rationale:

- Runtime integration cannot safely merge structured rows without a stable key.
- `pole_id` must be present before upload/merge code exists.
- `project_id` and `file_id` provide traceability without being merge keys.

Required implementation:

- Add `pole_id` to the Stage 4 schema/template.
- Make `pole_id` required for evidence-bearing rows.
- Add `project_id` and `file_id` as optional metadata fields or define why they
  are intentionally deferred.
- Keep metadata fields clear from Trimble measurement fields.
- Update template generation so new headers appear in the expected order.
- Define duplicate `pole_id` handling in validators or a dedicated merge-plan
  helper before runtime integration.

Initial matching rule:

- Primary match: `pole_id`.
- Do not auto-match by coordinates in Stage 4A.
- Do not proximity-match in Stage 4A.
- Do not merge orphan Stage 4 rows into app records silently.

Acceptance tests:

- `get_stage4_field_definition("pole_id")` exists.
- `pole_id` appears in `get_stage4_template_headers()`.
- Generated `templates/structured_capture_template.csv` includes `pole_id`.
- A row with capture metadata but no `pole_id` fails when the row is
  evidence-bearing.
- A metadata-only placeholder row without `pole_id` is either explicitly
  rejected or explicitly classified according to the final schema decision.
- Duplicate `pole_id` rows are detected by the planned aggregate validator or
  recorded as a Stage 4B requirement if duplicate handling is deferred.
- Unknown/blank `pole_id` values do not pass as real keys.

Expected test files:

- `tests/test_structured_capture_schema.py`
- `tests/test_generate_structured_capture_template.py`
- `tests/test_structured_capture_validators.py`

### 3. Fix VLD-3 Third: Structured Source Registration

Rationale:

- Source registration is only useful after structured values can be interpreted
  and keyed correctly.
- It must be in place before popup/API/report surfacing.
- It protects C2E2 truthfulness by making structured values visibly different
  from survey/controller values.

Required implementation:

- Extend the field reference source vocabulary to include
  `structured_capture`.
- Define display wording for the source, such as `Structured capture`.
- Do not add Stage 4 fields to the C2E2 normal popup row list yet.
- Do not show Stage 4 sections unless a later Stage 4D task has real merged
  structured values to display.
- Ensure existing `survey`, `trimble_attr`, and `derived` semantics are
  unchanged.

Acceptance tests:

- `structured_capture` is accepted/registered as a field source.
- Existing C2E2 popup tests still prove forbidden fields are absent from normal
  rows.
- Existing source sets for Trimble attribute fields and derived fields are
  unchanged.
- No Stage 4 field is displayed by default in the current popup renderer.
- Future source-label helper returns clear wording for structured capture.

Expected test files:

- `tests/test_c2e2_popup_fields.py`
- `tests/test_c2e2_popup_rendering.py`
- A new focused source-registration test if the implementation adds a helper.

## Stage 4A Acceptance Gate

Stage 4A can be considered complete only when:

- VLD-1, VLD-2, and VLD-3 each have explicit regression tests.
- `pytest tests/test_structured_capture_schema.py -v` passes.
- `pytest tests/test_structured_capture_validators.py -v` passes.
- `pytest tests/test_generate_structured_capture_template.py -v` passes.
- C2E2 popup rendering tests still pass.
- `pytest -v` passes.
- `pre-commit run --all-files` passes.
- No upload route, QA engine, geometry, span generation, or review workspace
  runtime files changed.

## Stage 4B: Schema / Field Validation

Purpose:

- Harden structured capture validation before any runtime merge.

Required coverage:

- Perfect `pole_id` match input shape.
- Missing `pole_id`.
- Duplicate `pole_id`.
- Unknown `pole_id`.
- Blank and unknown enum handling.
- Invalid enum.
- Required metadata missing.
- `confidence_level=low`.
- `verification_required=yes`.
- Unknown extra columns.
- Rows with only metadata versus rows with substantive evidence fields.

Exit gate:

- Validation produces structured, user-readable errors.
- Duplicate/orphan rows cannot pass silently.
- No runtime upload integration exists yet.

## Stage 4C: Controlled Runtime Integration

Purpose:

- Add the first live path for Stage 4 CSV data.

Allowed only after Stage 4A and Stage 4B are merged.

Required behaviour:

- Accept a Stage 4 CSV alongside, or explicitly associated with, a Trimble job.
- Validate rows before merge.
- Merge by `pole_id` only.
- Store structured rows with provenance.
- Report orphans, duplicates, conflicts, and low-confidence values.
- Never overwrite measured Trimble evidence silently.

Initial non-goals:

- Coordinate/proximity matching.
- QA rules that assume all Stage 4 fields are present.
- Popup clutter from empty Stage 4 fields.

## Stage 4D: Browser / Review Workspace Surfacing

Purpose:

- Surface structured values only after controlled runtime integration is stable.

Required behaviour:

- Popup labels distinguish Trimble measured, GridFlow derived, and Stage 4
  structured capture.
- Review workspace identifies structured evidence and verification-required
  values.
- Missing structured capture does not appear as a long list of missing fields.
- Browser validation covers at least `P008/F001`, `P010/F001`, and one job with
  a known Stage 4 CSV fixture.

## Stop Conditions

Stop and hand back if:

- A Stage 4 branch needs to edit app runtime files before Stage 4A and Stage 4B
  are complete.
- A proposed merge rule requires coordinate/proximity auto-matching before
  `pole_id` matching works.
- A popup change would show Stage 4 fields without real structured values.
- Any change would reintroduce forbidden C2E2 fields as normal popup rows.
- Validation falls below the current master baseline without a documented reason.
