# GridFlow Worker Start Checklist

Purpose: standard entry checklist every worker follows before making code changes.

## Before coding

### Mandatory safety checks (run these first)

1. Run `python3 scripts/worker_safety_check.py --branch <branch> --task "<task>"`.
   - If it exits non-zero, resolve all BLOCK items before proceeding.
   - Warnings may be accepted with documented justification.
2. Run `git status --short --branch` — working tree must be clean before `start_task.py`.
3. Run `git rev-parse HEAD` — record the master baseline SHA for this task.
4. Run `python3 scripts/control_status.py` from the repo root.
5. Confirm the chosen branch name does not collide: `git branch -a | grep <name>`.
6. If this task creates a new AI_CONTROL doc, confirm the slot is free: `ls AI_CONTROL/<N>_*`.
   Prefer a namespace prefix (`PCS_`, `PRD_`, `DOM_`, `STG_`, `AUD_`) over a bare number.
7. If touching `app/static/js/map-viewer.js`, confirm no other unmerged branch has
   competing changes: `git log --all --source -- app/static/js/map-viewer.js | head`.
   Or pass `--forbid-map-viewer` to `worker_safety_check.py` if the task forbids it.
8. Read `AI_CONTROL/05_HANDOFF.md` — confirm no parallel active-task marker exists
   for the same scope on a different branch.

### Required reading

1. Read `AI_CONTROL/01_CURRENT_STATE.md`.
2. Read `AI_CONTROL/02_CURRENT_TASK.md`.
3. Read `AI_CONTROL/00_PROJECT_BOARD.md`.
4. Read `AI_CONTROL/06_WORKER_RULES.md`.

### Task registration

1. Run `python3 scripts/start_task.py` for the assigned task unless Noel has explicitly
   said the task is already started. (`start_task.py` will refuse if AI_CONTROL files
   are dirty — that means step 2 was skipped or step 1 was ignored.)

### Scope confirmation

1. Confirm the task's allowed files and forbidden files before editing anything.
2. Confirm whether `python3 scripts/manual_review.py` is required for this task.
   It is required after UI, map, popup, or review-workflow changes.
3. Stop and report immediately if the branch, active task, handoff, or prompt disagree.

## Stop Conditions

- Branch in the repo does not match the branch in the prompt.
- `control_status.py` reports a different active task than the prompt and the mismatch is not clearly intentional.
- Uncommitted changes exist and their purpose is unclear.
- The requested work touches forbidden files or app runtime areas that the task says must stay untouched.
