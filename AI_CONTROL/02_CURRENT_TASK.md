# Current Task

## NEXT PHASE:

C2E2/D Modest Popup Expansion Planning

## Goal:

Plan a controlled, modest expansion of the C2/D popup data model using the real-job validation findings.

## Scope:

- Add approximately 10-15 highest-value operational survey/design fields.
- Move current popups from roughly 12 fields toward roughly 25 useful fields.
- Do NOT jump to the full ~50-field survey research model yet.
- Keep the popup practical, readable, and useful for planners/designers.

## Candidate field groups:

1. Pole / support specification
   - `pole_class`
   - `pole_strength` or `specification`
   - `material`

2. Condition / defects
   - `condition`
   - `defect_type`
   - `defect_severity`

3. Electrical / conductor
   - `voltage_carried`
   - `conductor_type`
   - `conductor_size`
   - `phase_configuration`

4. Structural support
   - `stay_present`
   - `stay_type`
   - `lean_direction`
   - `lean_severity`

5. Equipment
   - `equipment_present`
   - `equipment_type`

## Planning rules:

- Define exact fields before implementation.
- Define user-facing labels.
- Define missing-value wording.
- Define source/trust wording.
- Preserve existing validation/navigation/UX behaviour.
- Do not change geometry pipeline.
- Do not change span generation.
- Do not change validation semantics.
- Do not add speculative AI recommendations.
- Do not use archive.

## Validation requirement after implementation:

- Re-test `P008/F001`.
- Re-test `P010`.
- Confirm popup readability.
- Confirm no review navigation regressions.
- Confirm no backend regressions.

## Immediate next action:

Create a C2E2/D popup expansion specification before coding.
