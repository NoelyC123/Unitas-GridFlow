# GridFlow Project Control Center

The Project Control Center is a lightweight repo-based coordination layer for GridFlow. It uses markdown files and small standard-library Python scripts to keep Noel, Codex, Claude Code, Cursor, and ChatGPT aligned on active task ownership, branch ownership, validation state, and handoff state.

It is not an app feature, Flask UI, database, or workflow engine.

## Why It Exists

GridFlow now has multiple AI workers, an active manual review harness, validation output folders, and several control documents. The control center gives every worker a shared operating surface before code changes begin, during validation, and at handoff.

## Relationship To Manual Review Harness

The manual review harness remains the browser validation gate after UI-facing work. The control center records when that harness was run, which jobs were tested, where the `validation_runs/` report lives, whether `failures.json` was clean, and whether screenshots were captured.

## Files

- `AI_CONTROL/00_PROJECT_BOARD.md`: high-level board for stable milestone, active task, validation state, blocked items, done items, and backlog.
- `AI_CONTROL/03_WORKER_LOG.md`: append-only worker activity log.
- `AI_CONTROL/04_VALIDATION_LOG.md`: validation evidence log for tests, pre-commit, manual review harness runs, reports, failures, and verdicts.
- `AI_CONTROL/05_HANDOFF.md`: latest operational handoff for the next worker.
- `AI_CONTROL/06_WORKER_RULES.md`: coordination rules for Codex, Claude Code, Cursor, ChatGPT, and Noel.
- `AI_CONTROL/07_WORKER_START_CHECKLIST.md`: standard pre-coding checklist for every worker.
- `AI_CONTROL/08_WORKER_FINISH_CHECKLIST.md`: standard pre-handoff checklist for every worker.
- `AI_CONTROL/09_WORKER_PROMPT_TEMPLATES.md`: reusable assignment templates for implementation, review, validation, and docs tasks.
- `scripts/start_task.py`: records the start of an active task and updates marked handoff/board sections.
- `scripts/log_worker_update.py`: appends worker progress updates.
- `scripts/log_validation_run.py`: appends validation evidence and a short worker-log entry.
- `scripts/control_status.py`: prints a concise snapshot of branch, git status, active task, handoff, validation, and worker-rule reminders.

## Script Examples

Check current control status:

```bash
python3 scripts/control_status.py
python3 scripts/control_status.py --json
```

Start a task:

```bash
python3 scripts/start_task.py \
  --task "Project Control Center Foundation" \
  --owner codex \
  --branch codex/project-control-center-foundation \
  --status in_progress \
  --summary "Create markdown control files and helper scripts"
```

Log progress:

```bash
python3 scripts/log_worker_update.py \
  --worker codex \
  --branch codex/project-control-center-foundation \
  --summary "Created control files and helper scripts" \
  --files "AI_CONTROL/00_PROJECT_BOARD.md,scripts/start_task.py" \
  --validation "pytest pending" \
  --next-action "Run project control tests"
```

Log validation:

```bash
python3 scripts/log_validation_run.py \
  --branch codex/project-control-center-foundation \
  --commit abc123 \
  --status pass \
  --jobs P008/F001 P010 \
  --command "pytest -v && pre-commit run --all-files" \
  --report validation_runs/20260509_192248/validation_report.md \
  --failures "[]" \
  --screenshots no
```

## Worker Bootstrap Workflow

Every worker should enter through the same control path so branch ownership, validation expectations, and handoff state are visible to the next person.

## Before Coding

1. Create or switch to the task branch.
2. Read `AI_CONTROL/01_CURRENT_STATE.md`, `AI_CONTROL/02_CURRENT_TASK.md`, `AI_CONTROL/00_PROJECT_BOARD.md`, `AI_CONTROL/05_HANDOFF.md`, and `AI_CONTROL/06_WORKER_RULES.md`.
3. Read `AI_CONTROL/07_WORKER_START_CHECKLIST.md`.
4. Run `python3 scripts/control_status.py` to confirm branch, active task, handoff, validation, and warnings.
5. Run `python3 scripts/start_task.py` when taking ownership of a new task on the branch.
6. Confirm allowed files, forbidden files, and whether `python3 scripts/manual_review.py` is required.

## After Coding

1. Read `AI_CONTROL/08_WORKER_FINISH_CHECKLIST.md`.
2. Run task-specific tests, then `pytest -v`, then `pre-commit run --all-files`.
3. Run `python3 scripts/manual_review.py` if UI, map, popup, or review workflow changed.
4. Run `python3 scripts/log_worker_update.py` to record implementation progress.
5. Run `python3 scripts/log_validation_run.py` to record the validation evidence.
6. Update `AI_CONTROL/05_HANDOFF.md` with branch, status, validation, and next action.
7. Hand the branch back through Noel’s review and merge process.

## Script Responsibilities

- `scripts/start_task.py`: use at task start to update the visible active-task markers on the board and handoff.
- `scripts/log_worker_update.py`: use after meaningful implementation or documentation progress.
- `scripts/log_validation_run.py`: use after tests, pre-commit, or manual review runs so validation evidence is captured separately from general progress notes.
- `scripts/control_status.py`: use at the start of work, and again before handoff if branch/task state looks uncertain.

## Multi-Worker Support

The control center supports multiple workers by separating responsibilities:

- the board shows the visible active task
- the worker log preserves append-only progress history
- the validation log captures objective evidence
- the handoff file tells the next worker what to do next
- the start/finish checklists keep the entry and exit process consistent across Codex, Claude Code, Cursor, ChatGPT, and Noel

## Worker Rules

- Read `AI_CONTROL/01_CURRENT_STATE.md` and `AI_CONTROL/02_CURRENT_TASK.md` before coding. These are pre-existing active source-of-truth files.
- Read `AI_CONTROL/00_PROJECT_BOARD.md` before starting a new branch.
- Treat the Project Control Center files as coordination helpers that complement the source-of-truth files; they do not replace them.
- Update `AI_CONTROL/03_WORKER_LOG.md` after meaningful work.
- Update `AI_CONTROL/04_VALIDATION_LOG.md` after validation.
- Update `AI_CONTROL/05_HANDOFF.md` before stopping or handing back.
- Never mix unrelated feature work into the active branch.
- Never modify archive files.
- Keep app runtime untouched unless the task explicitly allows runtime changes.
- If branch confusion occurs, stop and report `git status --short --branch`.

## Worker Examples

Codex should use the scripts during implementation turns and commit only scoped control-layer changes.

Claude Code should read the board, task, rules, and handoff before taking ownership of a branch.

Cursor should log implementation progress when it makes meaningful file changes.

ChatGPT should use the control files as context for review, planning, and coordination rather than treating older phase documents as current.
