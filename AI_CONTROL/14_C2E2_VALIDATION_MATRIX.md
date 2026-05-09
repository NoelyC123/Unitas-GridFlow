# C2E2/D Validation Matrix

## Purpose

Validate the C2E2 popup expansion against real Trimble field availability and existing C2E review navigation behaviour.

## Automated Checks

Required:

- `pytest -v`
- `pre-commit run --all-files`

Focused tests should include:

- C2E2 popup field display tests from support-suite if available.
- Popup/static truthfulness tests.
- Review navigation regression tests.
- Route highlight tests.
- Material missing wording tests.
- Relationship field display tests.

## Field-Level Validation

| Field | Expected validation |
|---|---|
| `pole_id` | Displays captured point id. |
| `structure_type` | Displays captured feature code. |
| `asset_intent` | Displays derived intent or `Not classified`. |
| `record_role` | Displays derived role without implying capture. |
| `height` | Displays captured `CODE:HEIGHT` value with metres when present. |
| `qa_status` | Displays existing derived QA status without semantic changes. |
| `name` / `location` | Displays captured `CODE:REMARK` survey note or `-`. |
| `relationship` | Displays only when derived relationship exists. |
| `being_replaced_by` | Displays only for relevant EXpole replacement evidence. |
| `replacing` | Displays only for relevant PRpole/Angle replacement evidence. |
| `material` | If shown, absent value displays `Not recorded in survey`. |

## Required Wording Tests

Height:

- `Pol` missing height: `Not measured (intermediate pole)`.
- `EXpole` missing height: `Not measured - check survey notes`.
- `Angle` missing height: `Not measured - check survey notes`.
- Captured height: display the measured `CODE:HEIGHT` value, not GPS elevation.

Material:

- Trimble material absent: `Not recorded in survey`.
- Do not show absent material as failed, unknown, or captured.

Absent theoretical fields:

- `pole_class`, `condition`, `defect_type`, `voltage_carried`, `conductor_type`, `lean_direction`, and `equipment_type` are not shown as ordinary blank popup fields.
- If future UI explicitly shows any absent field, wording must be `Not recorded in survey` and it must be clearly out of current Trimble capture scope.

## Job Validation

### `P008/F001`

Validate:

- Existing review navigation still works.
- Design Blockers, Review Required, Evidence Gaps, and Planner Awareness cards remain clickable.
- Next / Previous still cycles targets.
- Release map still pauses automatic refocus.
- Route highlight and current target span highlight still work.
- Popups show realistic selected fields only.
- `Pol` height wording is not treated as a defect.
- Material wording, if visible, is `Not recorded in survey`.
- Planner awareness toggle still works.
- No console errors except favicon/browser-extension noise.

### `P010`

Validate:

- Normal operational SPEN workflow remains usable.
- EXpole and Angle height wording is correct.
- Replacement relationship fields display where derived.
- Popup remains readable and compact.
- Review navigation and popup close/reset still work.
- No console errors except favicon/browser-extension noise.

### `P011`

Validate if support-suite or implementation touches messy CSV alias handling:

- Messy import robustness remains intact.
- Alias resolution uses `field_reference.py` where applicable.
- Import summary unaffected.
- Missing values display gracefully.

## Regression Tests

Must preserve:

- Review intelligence summary.
- Issue-to-map navigation.
- Next / Previous.
- Release map.
- Popup close/reset route styling.
- Route highlight and current target span styling.
- Planner awareness markers and toggle.
- Smart popup side positioning.
- Existing validation banners.
- Backend CSV robustness.

## Merge Gate

C2E2 implementation can merge only when:

- Support-suite dependency is merged first.
- Automated tests pass.
- `pre-commit run --all-files` passes.
- `P008/F001` manual validation passes.
- `P010` manual validation passes.
- No console errors are observed except favicon/browser-extension noise.
- No backend geometry/span-generation files changed.
- No validation semantics changed.
- No archive files changed.
