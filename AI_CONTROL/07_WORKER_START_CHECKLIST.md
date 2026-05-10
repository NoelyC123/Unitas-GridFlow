# GridFlow Worker Start Checklist

Purpose: standard entry checklist every worker follows before making code changes.

## Before coding

1. Confirm the current git branch matches the assigned task.
2. Run `git status --short --branch` and confirm the working tree is clean or that any existing changes are understood.
3. Read `AI_CONTROL/01_CURRENT_STATE.md`.
4. Read `AI_CONTROL/02_CURRENT_TASK.md`.
5. Read `AI_CONTROL/00_PROJECT_BOARD.md`.
6. Read `AI_CONTROL/05_HANDOFF.md`.
7. Read `AI_CONTROL/06_WORKER_RULES.md`.
8. Run `python3 scripts/control_status.py` from the repo root.
9. Run `python3 scripts/start_task.py` for the assigned task unless Noel has explicitly said the task is already started.
10. Confirm the task's allowed files and forbidden files before editing anything.
11. Confirm whether `python3 scripts/manual_review.py` is required for this task. It is required after UI, map, popup, or review-workflow changes.
12. Stop and report immediately if the branch, active task, handoff, or prompt disagree.

## Stop Conditions

- Branch in the repo does not match the branch in the prompt.
- `control_status.py` reports a different active task than the prompt and the mismatch is not clearly intentional.
- Uncommitted changes exist and their purpose is unclear.
- The requested work touches forbidden files or app runtime areas that the task says must stay untouched.
