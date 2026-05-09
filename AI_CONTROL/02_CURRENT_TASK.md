# Current Task

## NEXT PHASE:

C2E2/D Modest Popup Expansion Planning

## Goal:

Plan a controlled, modest expansion of the C2/D popup data model using the C2E real-job validation findings and the Package A field reality audit.

## Scope:

- Use realistic Tier 1/2 fields from `AI_CONTROL/31_REAL_JOB_FIELD_REALITY_REPORT.md`.
- Keep the initial implementation target to roughly 10 fields that are actually parsed or derived today.
- Defer theoretical fields absent from Trimble to Stage 4 structured capture.
- Keep the popup practical, readable, and useful for planners/designers.

## Candidate field groups:

1. Identity / role
   - `pole_id`
   - `structure_type`
   - `asset_intent`
   - `record_role`

2. Geometry / measured evidence
   - `height`

3. Quality / review
   - `qa_status`

4. Survey context
   - `name` / `location`
   - `material` only as `Not recorded in survey`

5. Relationship
   - `relationship`
   - `being_replaced_by`
   - `replacing`

## Planning rules:

- Merge/read `claude-code/c2e2-support-suite` before implementation.
- Treat `app/field_reference.py` `FIELD_DEFINITIONS` as canonical after support-suite merge.
- Define exact fields before implementation.
- Define user-facing labels.
- Define missing-value wording.
- Define source/trust wording.
- Preserve existing validation/navigation/UX behaviour.
- Do not change geometry pipeline.
- Do not change span generation.
- Do not change validation semantics.
- Do not add speculative AI recommendations.
- Do not add absent theoretical fields as if they were captured.
- Do not use archive.

## Validation requirement after implementation:

- Re-test `P008/F001`.
- Re-test `P010`.
- Confirm popup readability.
- Confirm no review navigation regressions.
- Confirm no backend regressions.

## Immediate next action:

Create a C2E2/D popup expansion specification before coding.

Current planning docs:

- `AI_CONTROL/11_C2E2_POPUP_EXPANSION_SPEC.md`
- `AI_CONTROL/12_C2E2_FIELD_MAPPING_AUDIT.md`
- `AI_CONTROL/13_C2E2_IMPLEMENTATION_PLAN.md`
- `AI_CONTROL/14_C2E2_VALIDATION_MATRIX.md`
