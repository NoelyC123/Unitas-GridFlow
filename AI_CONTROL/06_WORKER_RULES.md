# GridFlow Worker Rules

Purpose: operating rules for Codex, Claude Code, Cursor, ChatGPT, and Noel when coordinating work in this repository.

## Required Reading

- Read `AI_CONTROL/01_CURRENT_STATE.md` and `AI_CONTROL/02_CURRENT_TASK.md` before coding. These are pre-existing active source-of-truth files.
- Read `AI_CONTROL/00_PROJECT_BOARD.md` before starting a new branch.
- Read `AI_CONTROL/07_WORKER_START_CHECKLIST.md` before coding.
- Treat the new Project Control Center files as coordination helpers that complement the source-of-truth files; they do not replace them.
- Run `python3 scripts/control_status.py` at the start of work.
- If `control_status.py` conflicts with the user prompt, stop and confirm before coding.

## Logging Rules

- Update `AI_CONTROL/03_WORKER_LOG.md` after meaningful work.
- Update `AI_CONTROL/04_VALIDATION_LOG.md` after validation.
- Update `AI_CONTROL/05_HANDOFF.md` before stopping or handing back.
- Follow `AI_CONTROL/08_WORKER_FINISH_CHECKLIST.md` before handoff.

## Branch And Scope Rules

- Never mix unrelated feature work into the active branch.
- Never modify archive files.
- Keep app runtime untouched unless the task explicitly says app runtime changes are allowed.
- If branch confusion occurs, stop and report `git status --short --branch` before continuing.

## Validation Rules

- The manual review harness is the standard validation gate after UI work.
- `python3 scripts/manual_review.py` is required after UI, map, popup, or review-workflow changes.
- Record validation command, jobs, report path, failures status, and verdict in `AI_CONTROL/04_VALIDATION_LOG.md`.
- Do not claim branch readiness without recording validation state.

## Worker Coordination

- Treat the project board as the visible coordination surface.
- Treat the worker log as append-only operational history.
- Treat the handoff file as the latest working instruction for the next worker.
- Noel remains the merge and product-control point.
