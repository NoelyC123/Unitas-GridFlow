# GridFlow Worker Prompt Templates

Purpose: reusable task prompts for Codex, Claude Code, Cursor, ChatGPT, and Noel when assigning scoped worker tasks.

Use these as short operational templates. Fill in the placeholders and trim anything not needed.

## 1. Codex implementation task

```text
TASK: [task name]

Branch:
[branch name]

Goal:
[specific implementation goal]

Source-of-truth files:
- AI_CONTROL/01_CURRENT_STATE.md
- AI_CONTROL/02_CURRENT_TASK.md
- AI_CONTROL/00_PROJECT_BOARD.md
- AI_CONTROL/05_HANDOFF.md
- AI_CONTROL/06_WORKER_RULES.md

Allowed files:
- [allowed file paths]

Forbidden files:
- [forbidden file paths]

Start checklist:
- Read AI_CONTROL files above
- Run python3 scripts/control_status.py
- Run python3 scripts/start_task.py for this task
- Confirm branch/task match before editing

Validation commands:
- [task-specific pytest command]
- pytest -v
- pre-commit run --all-files
- [python3 scripts/manual_review.py ... if needed]

Finish checklist:
- Run scripts/log_worker_update.py
- Run scripts/log_validation_run.py
- Update AI_CONTROL/05_HANDOFF.md
- Commit with a clear message

Output required:
- branch
- commit
- changed files
- tests and validation run
- final git status
```

## 2. Claude Code backend/support task

```text
TASK: [task name]

Branch:
[branch name]

Goal:
[backend or support goal]

Source-of-truth files:
- AI_CONTROL/01_CURRENT_STATE.md
- AI_CONTROL/02_CURRENT_TASK.md
- AI_CONTROL/00_PROJECT_BOARD.md
- AI_CONTROL/05_HANDOFF.md
- AI_CONTROL/06_WORKER_RULES.md

Allowed files:
- [backend/support files]

Forbidden files:
- [UI/runtime areas out of scope]

Start checklist:
- Run python3 scripts/control_status.py
- Confirm no branch mismatch
- Run python3 scripts/start_task.py if the task is not already started

Validation commands:
- [targeted pytest command]
- pytest -v
- pre-commit run --all-files

Finish checklist:
- Log worker update
- Log validation
- Update handoff with scope and risk notes

Output required:
- branch
- files changed
- validation results
- unresolved risks or follow-ups
```

## 3. Claude Code review task

```text
TASK: [review name]

Branch:
[branch under review]

Goal:
[bug/risk/test review scope]

Source-of-truth files:
- AI_CONTROL/01_CURRENT_STATE.md
- AI_CONTROL/00_PROJECT_BOARD.md
- AI_CONTROL/05_HANDOFF.md
- AI_CONTROL/06_WORKER_RULES.md

Allowed files:
- review notes only unless edits are explicitly requested

Forbidden files:
- any implementation files unless the prompt authorizes fixes

Start checklist:
- Run python3 scripts/control_status.py
- Confirm branch under review
- Read current handoff and validation state

Validation commands:
- [read-only or verification commands]

Finish checklist:
- Report findings first, ordered by severity
- State test gaps and assumptions
- Update control logs only if the review task requires it

Output required:
- findings with file references
- validation/test gaps
- recommendation: ready / changes required
```

## 4. Cursor frontend task

```text
TASK: [task name]

Branch:
[branch name]

Goal:
[frontend/UI goal]

Source-of-truth files:
- AI_CONTROL/01_CURRENT_STATE.md
- AI_CONTROL/02_CURRENT_TASK.md
- AI_CONTROL/00_PROJECT_BOARD.md
- AI_CONTROL/05_HANDOFF.md
- AI_CONTROL/06_WORKER_RULES.md

Allowed files:
- [frontend files]

Forbidden files:
- [backend/schema/control files if out of scope]

Start checklist:
- Run python3 scripts/control_status.py
- Confirm UI scope and manual review expectation
- Run python3 scripts/start_task.py if needed

Validation commands:
- [targeted UI tests]
- pytest -v
- pre-commit run --all-files
- python3 scripts/manual_review.py [args]

Finish checklist:
- Log worker update
- Log validation with report path
- Update handoff with manual review outcome

Output required:
- branch
- changed UI files
- tests
- manual review result
- final git status
```

## 5. Validation-only task

```text
TASK: [validation task name]

Branch:
[branch name]

Goal:
[what must be validated]

Source-of-truth files:
- AI_CONTROL/00_PROJECT_BOARD.md
- AI_CONTROL/05_HANDOFF.md
- AI_CONTROL/06_WORKER_RULES.md

Allowed files:
- AI_CONTROL/03_WORKER_LOG.md
- AI_CONTROL/04_VALIDATION_LOG.md
- AI_CONTROL/05_HANDOFF.md
- validation artifacts produced by the approved tooling

Forbidden files:
- app runtime files unless the task changes from validation-only

Start checklist:
- Run python3 scripts/control_status.py
- Confirm exact validation commands and jobs

Validation commands:
- [targeted command]
- pytest -v
- pre-commit run --all-files
- [python3 scripts/manual_review.py ... if required]

Finish checklist:
- Run scripts/log_validation_run.py
- Update handoff with verdict and next action

Output required:
- branch
- validation commands
- pass/fail summary
- report path
- final git status
```

## 6. Documentation-only task

```text
TASK: [task name]

Branch:
[branch name]

Goal:
[documentation goal]

Source-of-truth files:
- AI_CONTROL/01_CURRENT_STATE.md
- AI_CONTROL/02_CURRENT_TASK.md
- AI_CONTROL/00_PROJECT_BOARD.md
- AI_CONTROL/05_HANDOFF.md
- AI_CONTROL/06_WORKER_RULES.md

Allowed files:
- [docs/control files]

Forbidden files:
- app/, runtime logic, validators, geometry pipeline, or any other code outside the approved doc scope

Start checklist:
- Run python3 scripts/control_status.py
- Confirm the work is documentation-only

Validation commands:
- [targeted docs test if any]
- pytest -v
- pre-commit run --all-files

Finish checklist:
- Log worker update
- Log validation
- Update handoff

Output required:
- branch
- changed docs
- validation run
- remaining follow-up items
```
