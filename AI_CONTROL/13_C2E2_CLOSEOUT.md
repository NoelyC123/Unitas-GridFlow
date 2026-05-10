# C2E2 Closeout Record

Purpose: final control record for C2E2 popup scope and map-navigation follow-ups.

## Status

- `c2e2-popup-scope-reduction-complete`: complete.
- `c2e2-map-navigation-followups-complete`: complete after merge/tag.
- Popup scope: closed.
- Navigation follow-ups: closed.

## Popup Scope Closeout

The C2E2 popup was reduced to reality-based fields only. Unavailable Trimble/export fields are not to be shown as normal popup rows unless a future Stage 4 structured capture task makes them real captured values with provenance.

Closed behavior:

- Pole/support popup scope is limited to identity/role, measured geometry/evidence, QA/review status, survey context, and lifecycle/relationship fields.
- C2E2 truthfulness wording distinguishes measured values, not measured values, not recorded values, and legacy/low-confidence values.
- Theoretical electrical, conductor, cable, equipment, voltage, defect, and unavailable Trimble fields remain absent from normal popup rows.

## Navigation Follow-Up Closeout

The C2E2 map navigation follow-up fixed:

- Next moves to the next review item, updates the popup, and pans/centres to the selected feature.
- Previous moves to the previous review item, updates the popup, and pans/centres to the selected feature.
- Release Map clears active review selection, route highlight, selected/current span classes, popup state, and returns the map to the normal review view.

Evidence:

- Tag: `c2e2-map-navigation-followups-complete`.
- Commit: `f2587ed`.
- Branch: `codex/c2e2-map-navigation-followups`.
- Validation: `pytest -v` passed; `pre-commit run --all-files` passed; browser check passed on `P008/F001` and `P010/F001`.

## Protection Rule

Future tasks must not reopen C2E2 popup field scope or navigation behavior unless the task prompt explicitly says so and names this closeout record as source material.
