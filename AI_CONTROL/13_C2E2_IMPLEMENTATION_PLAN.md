# C2E2/D Implementation Plan

## Branch

Use:

`codex/c2e2-popup-expansion-implementation`

## Required Dependency

Merge `claude-code/c2e2-support-suite` first.

The implementation depends on:

- `AI_CONTROL/31_REAL_JOB_FIELD_REALITY_REPORT.md`
- `AI_CONTROL/32_C2E2_PRE_IMPLEMENTATION_GUIDE.md`
- `app/field_reference.py`
- `app/field_validators.py` if included by the support-suite merge

Do not implement C2E2 popup changes before the support-suite field catalogue is available on the implementation branch.

## Reality-Based Implementation Scope

Initial implementation target is roughly 10 realistic fields:

- `pole_id`
- `structure_type`
- `asset_intent`
- `record_role`
- `height`
- `qa_status`
- `name` / `location`
- `relationship`
- `being_replaced_by`
- `replacing`

Allowed wording-only field:

- `material` as `Not recorded in survey`

Do not implement absent theoretical fields from the earlier candidate list.

## Safe Implementation Order

### Step 1: Adopt field catalogue

- Use `app/field_reference.py` `FIELD_DEFINITIONS` as canonical source after support-suite merge.
- Use field labels and missing wording from the catalogue.
- Confirm all selected fields exist in the catalogue or are already present in current feature properties.

### Step 2: Popup grouping and display

- Render selected fields in the support-suite group order where practical:
  - identity
  - geometry
  - quality
  - survey_context
  - relationship
- Keep existing popup content and validation banners unless directly replaced by equivalent clearer rows.
- Do not display long raw field dumps.
- Show relationship rows only when derived evidence exists.

### Step 3: Height wording

- Apply field-catalogue missing wording for height by `structure_type`.
- Ensure `Pol` missing height says `Not measured (intermediate pole)`.
- Ensure `EXpole` and `Angle` missing height says `Not measured - check survey notes`.
- Never use GPS elevation as pole height.

### Step 4: Material wording

- If `material` is shown, display `Not recorded in survey` when absent.
- Do not mark absent `material` as a validation failure.
- Do not imply material was captured by Trimble.

### Step 5: Tests

- Add/update popup display tests for selected fields.
- Add/update height wording tests for `Pol`, `EXpole`, and `Angle`.
- Add material wording tests.
- Add relationship field display tests.
- Run review navigation regression tests.

### Step 6: Manual validation

- Re-test `P008/F001`.
- Re-test `P010`.
- Confirm no review navigation regressions.
- Confirm no console errors except favicon/browser-extension noise.

## Backend Changes

Avoid backend changes for initial implementation.

Only deliberate future backend addition currently supported by the real audit:

- `land_use` from Trimble `CODE:LAND USE`

Do not add `land_use` in the first implementation unless Noel explicitly approves it as a small parser enhancement.

## Files Likely To Modify Later

- `app/static/js/map-viewer.js`
- `app/static/css/map-viewer.css` only if compact rendering needs minor adjustment
- popup/static truthfulness tests
- review navigation tests
- C2E2 popup field tests from support-suite if merged

Only if deliberately adding `land_use` later:

- `app/controller_intake.py`
- relevant intake tests

## Files Not To Modify

- `app/geometry_pipeline.py`
- `app/span_generator.py`
- `app/qa_engine.py` validation semantics
- planner awareness generation
- electrical asset line interaction
- archive files
- generated job outputs

## Risk Register

| Risk | Mitigation |
|---|---|
| Reintroducing theoretical unavailable fields | Use `31_REAL_JOB_FIELD_REALITY_REPORT.md` and `field_reference.py` as source of truth. |
| Misleading missing wording | Use `FIELD_DEFINITIONS` missing wording and structure-specific height rules. |
| Treating missing `Pol` height as a defect | Explicitly test `Pol` height wording. |
| Showing GPS elevation as pole height | Keep GPS elevation excluded from height display. |
| Review navigation regression | Run `tests/test_review_navigation_layer.py` and manual P008/P010 navigation checks. |
| Backend scope creep | Avoid backend changes unless Noel approves `land_use`. |

## Rollback Plan

- Revert the implementation branch.
- Keep these planning docs.
- Keep C2E validated master untouched.

## Implementation Gate

Start coding only after:

- `claude-code/c2e2-support-suite` is merged.
- Field catalogue APIs are available.
- Noel confirms whether `land_use` is in or out of the first implementation.
