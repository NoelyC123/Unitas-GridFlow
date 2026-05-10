# Standard Task Template

Purpose: exact prompt format for assigning work to any AI worker.

Use this template for every implementation, documentation, validation, audit, or conflict task.

```text
TASK: <short task name>

Branch:
<branch-name>

Owner:
<chatgpt-controller | codex | claude-code | claude-desktop | cursor | noel>

Lane:
<control | docs | frontend | backend | validation | audit | conflict | release>

Goal:
<one paragraph describing the outcome>

Source-of-truth files:
- AI_CONTROL/01_CURRENT_STATE.md
- AI_CONTROL/02_CURRENT_TASK.md
- AI_CONTROL/00_PROJECT_BOARD.md
- AI_CONTROL/05_HANDOFF.md
- <task-specific docs>

Allowed files:
- <exact paths or globs>

Forbidden files:
- app/
- archive/
- <task-specific forbidden files>

Rules:
- One-task-at-a-time rule applies.
- No overlapping branch work.
- Do not merge or delete branches.
- Do not modify archive.
- Preserve C2E2 truthfulness unless explicitly changing that scope.
- Preserve Stage 4 boundaries unless explicitly changing Stage 4 planning.

Implementation requirements:
- <specific behavior or docs to create>

Validation:
- pytest -v
- pre-commit run --all-files
- <manual review command if UI/map/popup/review behavior changes>

Control logging:
- Update AI_CONTROL/03_WORKER_LOG.md.
- Update AI_CONTROL/04_VALIDATION_LOG.md after validation.
- Update AI_CONTROL/05_HANDOFF.md before stopping.

Output required:
- branch
- commit hash, if committed
- files changed
- summary
- validation result
- browser/manual review result, if required
- final git status
```

## Branch Naming Rules

- Codex branches: `codex/<task-slug>`.
- Claude Code branches: `claude-code/<task-slug>`.
- Cursor branches: `cursor/<task-slug>`.
- Emergency branches: `<worker>/emergency-<issue-slug>`.
- Use lowercase slugs with hyphens.
- Do not reuse a branch name for a new task after merge.
- Do not start a branch if another active branch owns the same files or behavior.

## Task Ownership Rules

- Every task has exactly one owner.
- A reviewer may comment but does not become owner.
- A validation worker may run tests but does not change scope.
- If ownership changes, update `00_PROJECT_BOARD.md`, `02_CURRENT_TASK.md`, and `05_HANDOFF.md`.

## No Stale Branch Merge Rule

A branch is stale if master has moved after the branch validation or if the branch has unresolved conflicts. Stale branches must be rebased or merged from current master, then validation rerun, before merge approval.
