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
- `scripts/start_task.py`: records the start of an active task and updates marked handoff/board sections.
- `scripts/log_worker_update.py`: appends worker progress updates.
- `scripts/log_validation_run.py`: appends validation evidence and a short worker-log entry.

## Script Examples

Start a task:

```bash
python scripts/start_task.py \
  --task "Project Control Center Foundation" \
  --owner codex \
  --branch codex/project-control-center-foundation \
  --status in_progress \
  --summary "Create markdown control files and helper scripts"
```

Log progress:

```bash
python scripts/log_worker_update.py \
  --worker codex \
  --branch codex/project-control-center-foundation \
  --summary "Created control files and helper scripts" \
  --files "AI_CONTROL/00_PROJECT_BOARD.md,scripts/start_task.py" \
  --validation "pytest pending" \
  --next-action "Run project control tests"
```

Log validation:

```bash
python scripts/log_validation_run.py \
  --branch codex/project-control-center-foundation \
  --commit abc123 \
  --status pass \
  --jobs P008/F001 P010 \
  --command "pytest -v && pre-commit run --all-files" \
  --report validation_runs/20260509_192248/validation_report.md \
  --failures "[]" \
  --screenshots no
```

## Standard Workflow

1. Create or switch to the task branch.
2. Run `scripts/start_task.py`.
3. Implement the scoped work.
4. Run tests and, after UI work, `scripts/manual_review.py`.
5. Run `scripts/log_validation_run.py`.
6. Update `AI_CONTROL/05_HANDOFF.md`.
7. Merge/tag through Noel’s control process.

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
