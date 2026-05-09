# C2E2/D Popup Expansion Specification

## Purpose

C2E real-job validation confirmed that the review workspace is stable: review intelligence, issue-to-map navigation, route highlighting, planner awareness, C2E UX improvements, navigation context refinement, and backend CSV robustness all passed the real-job validation gate.

Package A then audited five real survey files in `AI_CONTROL/31_REAL_JOB_FIELD_REALITY_REPORT.md`. That audit changed the C2E2/D popup expansion scope. Real Trimble controller exports do **not** contain most of the earlier theoretical popup fields. C2E2/D must therefore improve the display of fields that are actually present or derived today, not invent a 50-field survey model.

The C2E2/D goal is a readable, truthful popup expansion grounded in current Trimble field reality.

## Source Of Truth

Until `claude-code/c2e2-support-suite` is merged, use these support-suite files as planning input:

- `AI_CONTROL/31_REAL_JOB_FIELD_REALITY_REPORT.md`
- `AI_CONTROL/32_C2E2_PRE_IMPLEMENTATION_GUIDE.md`
- `app/field_reference.py`

After the support suite is merged, `app/field_reference.py` and its `FIELD_DEFINITIONS` should be treated as the canonical field catalogue for C2E2 popup display labels, aliases, missing-value wording, and field groups.

## Scope

- Reality-based popup expansion only.
- Initial implementation target: roughly 10 realistic fields.
- Use Tier 1 and practical Tier 2 fields from the field reality report.
- Keep popups readable and useful for planners/designers.
- Do not add unavailable theoretical fields to imply they were captured.
- Do not build electrical asset line interaction.
- Do not rewrite validation semantics.
- Do not change geometry pipeline or span generation.
- Do not create a full 50-field survey research model.

## Selected Initial Fields

Initial C2E2 implementation should focus on these realistic fields:

| Field | Tier | Source | Display intent |
|---|---|---|---|
| `pole_id` | Tier 1 | Trimble parsed | Point identity |
| `structure_type` | Tier 1 | Trimble parsed | Feature code / survey code |
| `asset_intent` | Tier 1 | Derived | Existing/proposed/context intent |
| `record_role` | Tier 2 | Derived | Structural/context/anchor role |
| `height` | Tier 1 | Trimble `CODE:HEIGHT` attribute | Measured height where actually recorded |
| `qa_status` | Tier 1 | Derived | QA/design review state |
| `name` / `location` | Tier 1 | Trimble `CODE:REMARK` attribute | Survey note / remark |
| `relationship` | Tier 1/2 | Derived | Replacement/stay relationship where present |
| `being_replaced_by` | Tier 2 | Derived from sequencer/replacement pairing | EXpole replacement link |
| `replacing` | Tier 2 | Derived from sequencer/replacement pairing | PRpole/Angle replacement link |

Secondary Tier 2 candidates after support-suite merge:

- `stay_evidence_status` - useful if already present in map feature properties or safely plumbed without changing validation semantics.
- `land_use` - present in Trimble `CODE:LAND USE` but currently discarded. Add only as a deliberate later parser enhancement, not as part of the first implementation unless Noel explicitly approves that small backend addition.

## Explicitly Deferred Fields

The following fields are absent from the audited Trimble format and must be deferred to Stage 4 structured capture unless future real exports prove otherwise:

- `pole_class`
- `specification`
- `condition`
- `defect_type`
- `defect_severity`
- `voltage_carried`
- `conductor_type`
- `conductor_size`
- `phase_configuration`
- `stay_type`
- `lean_direction`
- `lean_severity`
- `equipment_present`
- `equipment_type`

`material` is also absent from Trimble real jobs. It may be shown only as a truthful context row, using `Not recorded in survey`, because current schema includes the key but real Trimble jobs do not populate it. Do not present missing `material` as a survey failure.

## Why Theoretical Fields Are Excluded

The real-job audit found that Trimble raw dump parsing extracts only:

- `pole_id`
- `easting`
- `northing`
- `height`
- `structure_type`
- `location`

Everything else is either derived by GridFlow or absent from current Trimble exports. Adding theoretical fields such as conductor type, condition, defect severity, lean direction, equipment type, or pole class would create noise and risk misleading users into thinking the field was captured but missing. Those fields belong in a future structured capture model, not this C2E2 popup refinement.

## Field Groups

Use the support-suite `POPUP_FIELD_GROUPS` design after merge:

1. Identity
   - `pole_id`
   - `structure_type`
   - `asset_intent`
   - `record_role`

2. Geometry
   - `height`
   - retain existing coordinates/location rows where currently displayed

3. Quality
   - `qa_status`
   - retain existing issue/warning summaries where currently displayed

4. Survey Context
   - `name` / `location`
   - `material` only as `Not recorded in survey`
   - `land_use` only if deliberately added from Trimble `CODE:LAND USE`

5. Relationship
   - `relationship`
   - `being_replaced_by`
   - `replacing`

## User-Facing Labels

| Field | Popup label |
|---|---|
| `pole_id` | Point ID |
| `structure_type` | Feature Code |
| `asset_intent` | Asset Intent |
| `record_role` | Record Role |
| `height` | Measured Height |
| `qa_status` | QA Status |
| `name` / `location` | Survey Note |
| `relationship` | Relationship |
| `being_replaced_by` | Being Replaced By |
| `replacing` | Replacing |
| `material` | Material |
| `land_use` | Land Use |
| `stay_evidence_status` | Stay Evidence |

## Missing-Value Wording

Use `field_reference.py` `FIELD_DEFINITIONS` and `get_missing_wording()` once support-suite is merged.

Critical wording:

- `height` on `Pol`: `Not measured (intermediate pole)`
- `height` on `EXpole`: `Not measured - check survey notes`
- `height` on `Angle`: `Not measured - check survey notes`
- `height` otherwise: `Not measured`
- `material`: `Not recorded in survey`
- `name` / `location`: `-`
- `relationship`: `-`
- absent theoretical fields: do not show, or if Noel explicitly asks to show them, use `Not recorded in survey`

Important distinctions:

- Missing height on intermediate `Pol` records is expected survey practice, not a data quality failure.
- GPS elevation is terrain/instrument elevation and must not be shown as pole height.
- `material`, `pole_class`, conductor fields, condition, defects, lean, and equipment are absent from current Trimble format.
- Derived relationship and role values must be labelled as derived, not captured survey fields.

## Source / Trust Wording

Use these source categories:

- Survey parsed: directly extracted from Trimble fields or attributes.
- Derived: computed by GridFlow from structure code, QA, route sequencing, or replacement pairing.
- Not recorded in survey: the real Trimble format did not contain this field.
- Parser candidate: present in Trimble but not currently extracted, such as `land_use`.

Do not show inferred or derived values as measured/captured values.

## Non-Goals

- No geometry changes.
- No span-generation changes.
- No validation semantics changes.
- No speculative AI recommendations.
- No electrical asset line interaction.
- No review focus mode.
- No issue filtering rewrite.
- No full 50-field survey research model.
- No Stage 4 structured capture fields in C2E2.

## Acceptance Criteria

C2E2 implementation is complete when:

- Selected Tier 1/2 fields render clearly in relevant popups.
- Height wording correctly distinguishes `Pol`, `EXpole`, and `Angle`.
- Material, if shown, says `Not recorded in survey`.
- Replacement relationship fields display only where derived evidence exists.
- Absent theoretical fields are not displayed as blank or failed fields.
- Review navigation, route highlight, current target span, Release map, planner awareness, and popup close/reset still work.
- No console errors except favicon/browser-extension noise.
- Automated tests and `pre-commit run --all-files` pass.
- `P008/F001` and `P010` manual validation pass.
