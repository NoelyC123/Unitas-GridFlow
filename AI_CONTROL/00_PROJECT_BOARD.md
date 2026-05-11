# GridFlow Control Center Board

Purpose: single operational board for ChatGPT, Codex, Claude Code, Claude Desktop, Cursor, and Noel.

This board is the first file to read after `01_CURRENT_STATE.md`. It records the active task, branch ownership, validation state, open follow-ups, and merge readiness. Older control files that are not listed in the v1 file set are historical unless a current task explicitly names them.

## Current Stable Milestones

- `c2e2-popup-scope-reduction-complete`
- `c2e2-popup-expansion-implementation-complete`
- `c2e2-map-navigation-followups-complete`
- `project-control-center-foundation-complete`
- `project-control-center-first-use-polish-complete`
- `stage4-structured-capture-foundation-complete`
- `c2f-review-focus-issue-filtering-complete`
- `technical-docs-field-architecture-complete`
- `c2g-lifecycle-replacement-visualization-complete`
- `project-control-worker-bootstrap-complete`
- `stage4c-architecture-gate-complete`
- `real-field-pilot-execution-system-v1-complete`
- `pre-pilot-cleanroom-release-readiness-audit-complete`
- `p-real-001-mini-independent-gate-audit-complete`
- `stage4c-controlled-baseline-pilot-prep-complete`

## Active Task

<!-- PROJECT_CONTROL:ACTIVE_TASK_START -->
- Task: Audit Existing Survey Files for Stage 4C Controlled Baseline Pilot Suitability
- Branch: `codex/audit-existing-files-for-stage4c-baseline-pilot`
- Owner: codex
- Status: validated_ready_for_merge
- Summary: Audited the requested baseline candidate paths and broader tracked CSV inventory. This checkout contains no auditable real survey/job baseline CSVs, so Noel still needs an accessible real Trimble export before the controlled baseline pilot can start.
<!-- PROJECT_CONTROL:ACTIVE_TASK_END -->

## In Progress

| Task | Branch | Owner | Lane | Status |
| --- | --- | --- | --- | --- |
| Existing survey baseline candidate audit | `codex/audit-existing-files-for-stage4c-baseline-pilot` | codex | Stage 4 field pilot execution | validated, ready for merge |

## Review / Validation

**Baseline Audit Branch (`codex/audit-existing-files-for-stage4c-baseline-pilot`):**

- Added `AI_CONTROL/79_EXISTING_SURVEY_BASELINE_CANDIDATE_AUDIT.md`
- Audited all named candidate paths plus the broader tracked CSV inventory in this checkout
- Result: no eligible real survey/job baseline CSVs are present under `uploads/projects/`, `uploads/jobs/`, or `validation_data/`
- Best candidate in this checkout: none available
- Next acquisition target: real `P008/F001` or `P009/F001` Trimble export with exact `pole_id` values and enough support rows for a controlled pilot
- Validation passed: `pytest -v` (1067 passed, 2 skipped), `pre-commit run --all-files`, `python3.13 scripts/repo_health.py` (warning-only for known numbering collisions), `python3.13 scripts/merge_safety_check.py codex/audit-existing-files-for-stage4c-baseline-pilot` (safe to merge)
- Browser validation: not required; control/docs only, no runtime UI changes

**Prior Audit Branches (ready for merge or merged):**

- P_REAL_001_MINI Independent Gate Audit (docs 71–72): verdict = successful shakedown, NO-GO for Stage 4C
- Pre-Pilot Cleanroom Audit (docs 66–69): verdict = READY WITH CAUTIONS for field trial; critical finding: docs 61–65 on unmerged branches

## Blocked

- Stage 4C runtime integration (pending next controlled pilot approval)
- Stage 4C controlled baseline pilot execution (blocked until Noel provides an accessible real Trimble baseline CSV)

## In Review / Audit

| Task | Branch | Owner | Status |
| --- | --- | --- | --- |
| P_REAL_001_MINI Independent Gate Audit | `claude-code/p-real-001-mini-independent-gate-audit` | claude-code | ready for review |
| Next Controlled Pilot Plan | `claude-code/p-real-001-mini-independent-gate-audit` | claude-code | ready for review |

## Done

- Branch retirement and control file deconfliction closed and tagged.
- Stage 4 readiness specification closed and tagged.
- C2E2 popup scope reduction closed and tagged.
- C2E2 map navigation follow-ups closed and tagged.
- C2F review focus + issue filtering closed and tagged.
- C2G lifecycle replacement visualization closed and tagged.
- Stage 4 structured capture foundation closed and tagged; runtime integration remains a future branch.
- Stage 4B structured capture validation preview complete; runtime integration remains blocked pending pilot evidence.
- Stage 4B/4C safety pilot harness complete; Stage 4C remains blocked pending a real pilot result.
- Real iPad field pilot package complete; raw-data handling is now extended by the execution-system branch.
- Real Field Pilot Execution System v1 complete on master; this branch adds operator workflow polish on top.
- `P_REAL_001_MINI` mini pilot completed as a successful workflow shakedown; tracked non-sensitive result record added on this branch.
- Technical documentation field/architecture package closed and tagged.
- Project Control Center foundation, polish, and worker bootstrap closed and tagged.
- GridFlow Control Center v1.0 closed and tagged.
- Stage 4A library correctness fixes closed and tagged.
- P_REAL_001_MINI mini field pilot rehearsal complete; independent gate audit confirms successful shakedown; Stage 4C remains blocked pending next controlled pilot.
- Pre-pilot cleanroom audit complete: worktree/branch cleanup plan, release readiness verdict, and pre-pilot release note created; critical finding: docs 61–65 unmerged.
- P_REAL_001_MINI independent gate audit complete: verdict = PARTIAL/RE-PILOT REQUIRED (successful shakedown, 20% merge-ready, only 10 poles); Stage 4C blocked.
- Stage 4C controlled baseline pilot preparation pack complete: docs 73–75 created defining exact pole_id matching protocol and controlled pilot requirements for next 30–50 pole real baseline pilot.

## Backlog / Next Candidates

- Stage 4C controlled runtime integration, only after a controlled pilot against a real GridFlow/Trimble baseline is recorded and the go/no-go gate is approved.
- Controlled baseline pilot with exact `pole_id` matching and stronger access/closer capture.
- Accessible real baseline CSV audit refresh once Noel provides `P008/F001`, `P009/F001`, or another real Trimble export in the worktree.
- DNO-grade rulepack planning.
- PoleCAD export planning.
- Electrical asset / line / cable interaction layer.
- Lifecycle visualization follow-up enhancements.

## Operating Rule

Only one active implementation task may be open at a time. A second branch may exist only for review, audit, or emergency rollback work and must not overlap the active branch scope.
