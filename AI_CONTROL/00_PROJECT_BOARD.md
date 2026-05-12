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
- `existing-survey-baseline-candidate-audit-complete`
- `controlled-pilot-field-pack-v1-complete`
- `p-controlled-001-readiness-gate-complete`
- `stage4-real-survey-pack-readiness-review-complete`

## Active Task

<!-- PROJECT_CONTROL:ACTIVE_TASK_START -->
- Task: Stage 4 Real Survey Pack Readiness Review (docs 87–88)
- Branch: `claude-code/stage4-real-survey-pack-readiness-review`
- Owner: claude-code
- Status: ready_for_review
- Summary: Created Real Survey Pack Readiness Review (doc 87) classifying Bellsprings/Gordon baselines as baseline-conversion evidence (not field-photo evidence or automatic Stage 4C approval). Created Baseline vs. Field Evidence Decision Memo (doc 88) explaining why baseline alone and field evidence alone are insufficient; only combined baseline+field pilot (Phase 4) authorizes Stage 4C. Documented recommended 4-phase sequencing: Phase 1 (baseline extraction), Phase 2 (field-capture learning), Phase 3 (baseline-field analysis), Phase 4 (full controlled pilot). Updated 6 control files. Stage 4C remains blocked until Phase 4 is complete with signed verdict.
<!-- PROJECT_CONTROL:ACTIVE_TASK_END -->

## In Progress

| Task | Branch | Owner | Lane | Status |
| --- | --- | --- | --- | --- |
| Stage 4 Real Survey Pack Readiness Review (docs 87–88) | `claude-code/stage4-real-survey-pack-readiness-review` | claude-code | Stage 4 field pilot execution | ready for review |

## Review / Validation

**Existing baseline candidate audit (doc 79):**

- `AI_CONTROL/79_EXISTING_SURVEY_BASELINE_CANDIDATE_AUDIT.md` preserved the clean-audit result from a separate worktree
- That audit found no tracked candidate files under `uploads/projects/`, `uploads/jobs/`, or `validation_data/` in the clean audit worktree
- That result remains valid as provenance for the earlier control-only branch

**Current local main checkout reality:**

- Candidate upload and baseline CSVs do exist locally in this checkout
- Those local CSVs remain excluded from governance commits and must not be added during control-layer merges
- `P_REAL_001_MINI` remains only a successful workflow shakedown, not Stage 4C approval evidence

**Controlled baseline helper v1:**

- `scripts/prepare_stage4_controlled_pilot.py` now supports prepare mode and exact-match compare mode
- Prepare mode extracted `40` candidate support rows from the local `P_CONTROLLED_001` baseline after scanning `57` raw controller rows
- Exact match rules are strict: only whitespace and case normalisation are allowed; duplicates and missing/unsafe `pole_id` values are blocking
- Starter output uses the current Stage 4 header set and leaves unconfirmed technical fields blank or `unknown`

**Controlled Pilot Field Pack v1 (docs 80–82):**

- Documents 80–82 are now present: field-day procedure, photo/evidence rules, and operator decision notes
- These docs are ready for Noel once the local baseline CSV for `P_CONTROLLED_001` is selected
- Browser validation is not required; this is control/docs only

## Blocked

- Stage 4C runtime integration (pending controlled baseline pilot approval)
- Stage 4C controlled baseline pilot execution (blocked until Noel uses the extracted baseline set, completes the controlled pilot capture, validates it, and records the exact-match decision outcome)

## In Review / Audit

| Task | Branch | Owner | Status |
| --- | --- | --- | --- |
| Stage 4 Real Survey Pack Readiness Review (docs 87–88) | `claude-code/stage4-real-survey-pack-readiness-review` | claude-code | ready for review |

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
- Existing survey baseline candidate audit complete: doc 79 recorded that the separate clean audit worktree did not contain tracked candidate baseline files.
- Controlled pilot field pack v1 complete: docs 80–82 created providing Noel with simple field-day procedure, photo/evidence rules, and post-pilot decision notes for execution after baseline selection.
- P_CONTROLLED_001 Readiness Gate complete: docs 83–85 created providing Noel with baseline readiness verdict (READY FOR FIELD WORK), per-pole field targets with 34-row full and 15-row fallback options, and post-field acceptance criteria (≥80% exact match, ≥90% valid, ≥50% merge-ready). Stage 4C remains blocked pending field execution and signed verdict.
- Stage 4 Real Survey Pack Readiness Review complete: docs 87–88 classifying real Bellsprings/Gordon baselines as baseline-conversion evidence (not field-photo evidence or automatic Stage 4C approval). Documented 4-phase sequencing: baseline extraction, field-capture learning, baseline-field analysis, full controlled pilot. Only Phase 4 (full controlled pilot with validator pass + signed verdict) authorizes Stage 4C implementation. Stage 4C remains blocked until Phase 4 complete.

## Backlog / Next Candidates

- Run the new controlled baseline helper against Noel's local `P_CONTROLLED_001` field capture and produce the exact-match decision report.
- Controlled baseline pilot with exact `pole_id` matching and stronger access/closer capture.
- Stage 4C controlled runtime integration, only after a controlled pilot against a real GridFlow/Trimble baseline is recorded and the go/no-go gate is approved.
- DNO-grade rulepack planning.
- PoleCAD export planning.
- Electrical asset / line / cable interaction layer.
- Lifecycle visualization follow-up enhancements.

## Operating Rule

Only one active implementation task may be open at a time. A second branch may exist only for review, audit, or emergency rollback work and must not overlap the active branch scope.
