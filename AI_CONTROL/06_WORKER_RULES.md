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

## Coordination Protocol (from AI_CONTROL/41 — mandatory)

**Single-writer marked sections.**
The `<!-- PROJECT_CONTROL:HANDOFF_ACTIVE_START -->` and
`<!-- PROJECT_CONTROL:ACTIVE_TASK_START -->` marker blocks are
single-writer per master baseline. Two agents must not both hold those
blocks at the same time — the second agent rebases first.

**Dirty-tree before start.**
`start_task.py` will refuse to run if `git status` has uncommitted edits
to AI_CONTROL files. Run `git restore AI_CONTROL/` or commit those
changes before starting a new task. Run
`python3 scripts/worker_safety_check.py --branch <branch>` before
calling `start_task.py`.

**File-numbering check.**
Before creating a new AI_CONTROL document, confirm the numeric slot is
free: `ls AI_CONTROL/<N>_*`. Better: use the namespace prefix scheme
(`PCS_`, `PRD_`, `DOM_`, `STG_`, `AUD_`) for all new docs to avoid
collisions entirely.

**Pre-merge baseline check.**
Any merge into master must include this summary in the merge commit
message so the reviewer can see which side advanced where:

```sh
git rev-list --left-right --count master...<branch>
git log master..<branch> --oneline | head
git log <branch>..master --oneline | head
```

Run `python3 scripts/merge_safety_check.py <branch>` before any merge.

**Map-viewer guard.**
Any task whose spec says "do not change `app/static/js/map-viewer.js`"
must verify pre-commit:
`git diff master -- app/static/js/map-viewer.js | wc -l` must be `0`.
Or use: `python3 scripts/worker_safety_check.py --forbid-map-viewer`
