# GridFlow Current State

Purpose: canonical project state for all AI workers. Read this before interpreting any task prompt.

## Product Position

GridFlow is a validation-led survey-to-design intelligence and design-readiness tool for UK electrical OHL handoffs. It is strongest around real Trimble/controller survey workflows, C2E/C2E2 popup truthfulness, route review, lifecycle/replacement visualization, and evidence-led QA.

GridFlow is not currently a full CAD replacement, GIS platform, DNO compliance engine, field-survey platform, Field Maps replacement, or commercial multi-user SaaS product.

## Current Stable State

The stable product baseline includes:

- Post-survey QA gate and design-ready handoff outputs.
- Project/file intake and per-file map, PDF, design-chain, and audit outputs.
- Reality-based C2E2 pole/support popup scope.
- Review navigation, route highlighting, release map behavior, planner awareness, review focus, and lifecycle visualization.
- Manual Selenium review harness and validation evidence folders.
- Stage 4 structured capture foundation modules and template only; runtime integration is not built.
- Control Center v1.0 is being created on `codex/gridflow-control-center-v1`.

## Completed C2E2 Closeout

- `c2e2-popup-scope-reduction-complete`: complete.
- `c2e2-map-navigation-followups-complete`: complete and tagged.
- Popup scope: closed.
- Navigation follow-ups: closed.

Details live in `AI_CONTROL/13_C2E2_CLOSEOUT.md`.

## Source Of Truth Hierarchy

1. Real survey files and validation evidence.
2. Current task prompt from Noel or ChatGPT controller.
3. `AI_CONTROL/01_CURRENT_STATE.md`, `AI_CONTROL/02_CURRENT_TASK.md`, and `AI_CONTROL/00_PROJECT_BOARD.md`.
4. Protocol files `AI_CONTROL/06_*` through `AI_CONTROL/16_*`.
5. Code and tests.
6. Historical docs and older control files.
7. AI memory or chat summaries.

If sources conflict, stop and report the conflict before coding.

## Protected Runtime Areas

Do not modify these unless the current task explicitly allows it:

- `app/`
- `app/static/js/map-viewer.js`
- `app/routes/`
- QA engine, geometry pipeline, span generation, controller intake, API intake.
- Stage 4 schema/validator modules.
- Archive files.

## Validation Baseline

The normal branch readiness gate is:

- `pytest -v`
- `pre-commit run --all-files`
- Manual browser validation or `scripts/manual_review.py` when UI, map, popup, route, review navigation, planner awareness, or lifecycle behavior changes.

Validation evidence rules are in `AI_CONTROL/10_VALIDATION_EVIDENCE_PROTOCOL.md`.

## Current Risk Boundary

The app is display-ready for manual review, not a final engineering authority. Asset classification, stay detection, span sequencing, lifecycle matching, and grid/coordinate handling are useful review signals but must not be overclaimed as verified engineering truth without real-job validation evidence.

## Current Operating Instruction

Use the Control Center v1.0 files as the worker operating system. Do not start Stage 4 integration, rulepack implementation, or product feature work unless the current task file and board name that branch and scope.
