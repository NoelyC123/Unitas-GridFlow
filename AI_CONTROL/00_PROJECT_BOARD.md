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

## Active Task

<!-- PROJECT_CONTROL:ACTIVE_TASK_START -->
- Task: Field Pilot Command Center v1
- Branch: `codex/field-pilot-command-center-v1`
- Owner: codex
- Status: ready_for_review
- Summary: Upgraded the pilot validator into an operator-facing command center with dry-run coverage, clearer reports, evidence edge-case handling, and stable JSON output
<!-- PROJECT_CONTROL:ACTIVE_TASK_END -->

## In Progress

| Task | Branch | Owner | Lane | Status |
| --- | --- | --- | --- | --- |
| Field Pilot Command Center v1 | `codex/field-pilot-command-center-v1` | codex | Stage 4 field pilot execution | ready for review |

## Review / Validation

**Mini Pilot Results (audit branch):**
- `pytest -v`: expected 1050+ passed, 1 skipped (no new tests added).
- `pre-commit run --all-files`: expected passed.
- `python3.13 scripts/repo_health.py`: expected warning-only for known numbering collisions.
- `python3.13 scripts/merge_safety_check.py claude-code/p-real-001-mini-independent-gate-audit`: expected safe to merge.
- P_REAL_001_MINI pilot validation: **PARTIAL / RE-PILOT REQUIRED** (mini pilot successful as shakedown; Stage 4C remains blocked)
- Evidence audit: 33 photos, 100% reference coverage, 0 missing/0 orphaned/0 duplicates/0 invalid patterns
- Independent audit verdict: Successful rehearsal; next controlled pilot required before Stage 4C GO

**Active Task (Field Pilot Command Center v1):**
- Ready for review/merge on `codex/field-pilot-command-center-v1`
- Browser validation: not required for this local-only Stage 4 execution system.

## Blocked

- Stage 4C runtime integration (pending next controlled pilot approval)

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
- Technical documentation field/architecture package closed and tagged.
- Project Control Center foundation, polish, and worker bootstrap closed and tagged.
- GridFlow Control Center v1.0 closed and tagged.
- Stage 4A library correctness fixes closed and tagged.
- P_REAL_001_MINI mini field pilot rehearsal complete; independent gate audit confirms successful shakedown; Stage 4C remains blocked pending next controlled pilot.

## Backlog / Next Candidates

- Stage 4C controlled runtime integration, only after a real pilot result is recorded and the go/no-go gate is approved.
- DNO-grade rulepack planning.
- PoleCAD export planning.
- Electrical asset / line / cable interaction layer.
- Lifecycle visualization follow-up enhancements.

## Operating Rule

Only one active implementation task may be open at a time. A second branch may exist only for review, audit, or emergency rollback work and must not overlap the active branch scope.
