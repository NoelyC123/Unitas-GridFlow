# 45 — Stage 4 Go / No-Go Checklist

Snapshot: master HEAD `58235a1`, checklist date 2026-05-10.

## Purpose

This checklist must be completed before any worker starts Stage 4
implementation. It separates planning readiness from runtime readiness.

## Current Recommendation

**Go for Stage 4A library correctness fixes.**

**No-go for Stage 4 runtime integration.**

Runtime integration must wait until the three known blockers have dedicated
tests and are fixed on separate, reviewable branches.

## Pre-Implementation Checklist

Before opening a Stage 4 implementation branch, confirm:

- [ ] `AI_CONTROL/43_STAGE4_READINESS_SPECIFICATION.md` has been read.
- [ ] `AI_CONTROL/44_STAGE4_BLOCKER_FIX_PLAN.md` has been read.
- [ ] Current branch scope is Stage 4A, Stage 4B, Stage 4C, or Stage 4D.
- [ ] The branch name states the phase, for example
  `codex/stage4a-library-correctness`.
- [ ] The branch does not combine library fixes with runtime upload or UI work.
- [ ] The worker has confirmed `git status --short --branch` is clean before
  starting.
- [ ] The worker has recorded the active task in control logs.

## Stage 4A Go / No-Go

Stage 4A is allowed to start when:

- [ ] Scope is limited to library correctness, schema/template updates, source
  registration, docs, and tests.
- [ ] The branch fixes `none` blank-token handling.
- [ ] The branch adds row identity handling.
- [ ] The branch registers `structured_capture` source semantics before any UI
  display path uses them.
- [ ] The branch does not edit upload routes, QA runtime, geometry, span
  generation, review workspace behaviour, or C2E2 popup display scope.

Stage 4A is no-go if:

- [ ] It needs to accept Stage 4 CSV uploads in the app.
- [ ] It needs to merge Stage 4 rows with live jobs.
- [ ] It needs to show Stage 4 fields in popups.
- [ ] It relies on coordinate/proximity matching.

## Stage 4B Go / No-Go

Stage 4B is allowed to start when:

- [ ] Stage 4A is merged and validated.
- [ ] `none` enum regressions are covered by tests.
- [ ] `pole_id` / row identity behaviour is covered by tests.
- [ ] `structured_capture` source semantics are covered by tests.
- [ ] Duplicate/orphan/unknown/blank row scenarios are explicitly in scope.

Stage 4B is no-go if:

- [ ] Stage 4A is incomplete.
- [ ] It requires upload-route changes.
- [ ] It requires review workspace or popup surfacing.

## Stage 4C Go / No-Go

Stage 4C is allowed to start when:

- [ ] Stage 4A and Stage 4B are merged and validated.
- [ ] Merge rules are documented and accepted.
- [ ] Runtime upload/storage scope is explicit.
- [ ] `pole_id` is the primary and only automatic match key for the first
  runtime release.
- [ ] Orphan, duplicate, low-confidence, and verification-required rows have
  defined error/reporting behaviour.
- [ ] No app path can silently overwrite measured Trimble evidence.

Stage 4C is no-go if:

- [ ] Matching depends on coordinates/proximity before `pole_id` matching is
  reliable.
- [ ] Structured rows can merge without provenance.
- [ ] The QA engine would consume structured values without source/confidence.
- [ ] The branch would change popup field scope before structured values are
  merged and labelled.

## Stage 4D Go / No-Go

Stage 4D is allowed to start when:

- [ ] Stage 4C is merged and validated.
- [ ] At least one realistic Stage 4 CSV fixture exists.
- [ ] Popup/API/review workspace source labels are defined.
- [ ] Browser validation checklist includes structured capture surfacing.
- [ ] C2E2 forbidden-field tests still protect normal popup rows.

Stage 4D is no-go if:

- [ ] Structured values are not yet stored/merged by runtime code.
- [ ] Source labels are ambiguous.
- [ ] The UI would show empty Stage 4 sections.
- [ ] C2E2 popup truthfulness tests fail.

## Required Validation Gates

For Stage 4A and Stage 4B:

- [ ] `pytest tests/test_structured_capture_schema.py -v`
- [ ] `pytest tests/test_structured_capture_validators.py -v`
- [ ] `pytest tests/test_generate_structured_capture_template.py -v`
- [ ] Relevant C2E2 popup protection tests if source registration changes.
- [ ] `pytest -v`
- [ ] `pre-commit run --all-files`

For Stage 4C:

- [ ] All Stage 4A/4B tests.
- [ ] New integration tests for upload/storage/merge behaviour.
- [ ] `pytest -v`
- [ ] `pre-commit run --all-files`

For Stage 4D:

- [ ] All relevant Stage 4C tests.
- [ ] C2E2 popup rendering tests.
- [ ] Browser/manual review validation on `P008/F001`, `P010/F001`, and a job
  with Stage 4 fixture data.
- [ ] `pytest -v`
- [ ] `pre-commit run --all-files`

## Merge Gate

Before merging any Stage 4 branch:

- [ ] The completion report names the exact Stage 4 phase.
- [ ] The changed files match the phase scope.
- [ ] Validation logs include commands and results.
- [ ] No forbidden runtime files changed for Stage 4A/4B.
- [ ] No archive files changed.
- [ ] C2E2 popup truthfulness remains intact.
- [ ] Handoff states the next allowed phase.

## Final Go / No-Go Statement

The next safe implementation task is:

> Stage 4A: library correctness fixes.

The next unsafe task is:

> Stage 4 runtime integration, popup surfacing, or review workspace surfacing
> before Stage 4A and Stage 4B are complete.
