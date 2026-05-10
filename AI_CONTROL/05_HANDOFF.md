# GridFlow Current Handoff

Purpose: latest operational handoff for Noel and AI workers.

## Summary

- Master is stable.
- Latest completed milestones: `project-control-worker-bootstrap-complete`, `c2g-lifecycle-replacement-visualization-complete`, `technical-docs-field-architecture-complete`, `stage4-structured-capture-foundation-complete`, `c2f-review-focus-issue-filtering-complete`, `project-control-center-first-use-polish-complete`, `project-control-center-foundation-complete`, `c2e2-popup-expansion-implementation-complete`.
- Two parallel Stage 4 follow-up branches:
  - `claude-code/stage4-structured-capture-technical-audit` (this branch) — audit/review/support, no runtime code changes.
  - `codex/stage4-structured-capture-integration-plan` — Codex's planning work for future Stage 4 CSV integration.
- Audit and integration-plan branches must not overlap. The audit deliberately stops at observations and risk-tracking; the integration plan is Codex's territory.
- Backend QA, geometry, span generation, intake, app routes, map-viewer, and Stage 4 schema/validators must not change on either branch.
- Next expected action: review the audit findings, fold them into the integration plan, then move to a separate scoped branch for any library-only fixes.

## Active Task

<!-- PROJECT_CONTROL:HANDOFF_ACTIVE_START -->
- Task: Stage 4 Structured Capture Technical Audit
- Owner: claude-code
- Branch: `claude-code/stage4-structured-capture-technical-audit`
- Status: ready for review
- Summary: Audited Stage 4 schema, validators, template generator, and runtime integration risks. Three blocking gaps identified for runtime integration.
- Updated: 2026-05-10T09:35:00Z
<!-- PROJECT_CONTROL:HANDOFF_ACTIVE_END -->

## Stage 4 Technical Audit — Status

- **Branch:** `claude-code/stage4-structured-capture-technical-audit`
- **Commit:** pending (filled in by post-commit follow-up)
- **Audit docs created:**
  - `AI_CONTROL/22_STAGE4_TECHNICAL_AUDIT.md` — what currently exists, test coverage, validator guarantees vs gaps, embedded assumptions, runtime-import inventory, technical readiness rating.
  - `AI_CONTROL/23_STAGE4_SCHEMA_READINESS_REVIEW.md` — group-by-group review (pole spec / condition / electrical / structural / equipment / metadata) with fields, allowed values, data-quality risks, matching dependencies, UI display risk, QA use risk, plus required-metadata gaps.
  - `AI_CONTROL/24_STAGE4_RUNTIME_INTEGRATION_RISKS.md` — risks of integrating too early, pole_id matching risks, duplicate/conflicting rows, low-confidence data, popup clutter, QA-as-truth risk, mitigations, and a "do not integrate until" checklist.
- **Key findings:**
  1. **Validator bug — `"none"` enum erased.** `_BLANK_TOKENS` includes `"none"`, but the schema lists `"none"` as a valid enum for `stay_type`, `equipment_type`, `lean_direction`, `lean_severity`. A surveyor row recording `stay_type: none` (meaning "no stay on this pole") is silently normalised to Python `None`, identical to a row that didn't capture the field. Reproduced on master at `212bd23`.
  2. **No row identity in the schema.** No `pole_id`, `project_id`, or `file_id` field exists. Docs claim per-pole keying but the template CSV has no column to record it.
  3. **No `source: "structured_capture"` registered in `app/field_reference.py::FIELD_DEFINITIONS`.** The popup renderer has no path to display Stage 4 fields with a clear source label today.
- **What is NOT changed:**
  - No app runtime files modified (no schema, validator, template generator, route, QA engine, geometry, span generation, controller intake, field reference, field validators, map-viewer.js, CSS, or template changes).
  - No archive files touched.
  - No tests added or removed.
- **Validation status:**
  - `pytest tests/test_structured_capture_schema.py tests/test_structured_capture_validators.py tests/test_generate_structured_capture_template.py -v` — 23 passed.
  - `pytest -v` — 866 passed, 13 warnings.
  - `pre-commit run --all-files` — all hooks pass.
  - Manual review harness not required (no UI changes).
- **Readiness rating:**
  - **Library code: ✅ Production-ready as a foundation.**
  - **Runtime integration: ⚠ Not ready — three blocking gaps above.**
  - **Office-side spreadsheet review: ✅ Usable today** with the `"none"` caveat.
- **Next action:** review the audit; Codex's integration plan should consume the "do not integrate until" checklist; library-only fixes (`"none"` disambiguation, `pole_id` addition, field_reference registration) belong to separate scoped branches.

## Worker Bootstrap Status

- **Branch:** `codex/project-control-worker-bootstrap` (merged into master, tag re-pointed at merge commit `212bd23`).

## C2G Lifecycle Replacement Visualization — Status

- **Branch:** `codex/c2g-lifecycle-replacement-visualization` (merged).
- **Milestone:** `c2g-lifecycle-replacement-visualization-complete`.

## Technical Documentation Package — Status

- **Branch:** `claude-code/technical-docs-field-architecture` (merged).
- **Milestone:** `technical-docs-field-architecture-complete`.

## Stage 4 Foundation — Status

- **Branch:** `claude-code/stage4-structured-capture-foundation` (merged).
- **Milestone:** `stage4-structured-capture-foundation-complete`.
- Schema, validators, template generator, docs, and tests for the Stage 4 structured-capture layer — library code only, not wired into runtime. (See audit docs 22 / 23 / 24 for runtime-readiness analysis.)

## Next Action

- Review the three new audit docs.
- Roll the audit's "do not integrate until" checklist into Codex's Stage 4 integration plan.
- Open separate scoped library-only branches for the three blocking gaps (`"none"` disambiguation, `pole_id` schema addition, `field_reference` registration).
- Defer any runtime integration (upload route, QA wiring, popup rendering) until the checklist is closed.

## Do Not Start On This Branch

- Any code change beyond docs (this is an audit branch).
- Stage 4 schema/validator/template-generator edits — those belong to follow-up scoped branches.
- Any app runtime feature work.
- DNO-grade rulepack implementation.

## Completed Stable Milestones

- `project-control-worker-bootstrap-complete` — merged to master.
- `c2g-lifecycle-replacement-visualization-complete` — merged to master.
- `technical-docs-field-architecture-complete` — merged to master.
- `stage4-structured-capture-foundation-complete` — merged to master.
- `c2f-review-focus-issue-filtering-complete` — merged to master.
- `project-control-center-first-use-polish-complete` — merged to master.
- `project-control-center-foundation-complete` — merged to master.
- `c2e2-popup-expansion-implementation-complete` — merged to master.
