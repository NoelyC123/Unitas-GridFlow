# GridFlow Workflow System

Purpose: root pointer to the GridFlow Control Center v1.0.

The active operating system for AI workers is the markdown control layer in `AI_CONTROL/`. Use it instead of copy/paste coordination between ChatGPT, Codex, Claude Code, Claude Desktop, Cursor, and Noel.

## Control Center Entry Points

- `AI_CONTROL/01_CURRENT_STATE.md` - canonical current project state.
- `AI_CONTROL/02_CURRENT_TASK.md` - active task tracker.
- `AI_CONTROL/00_PROJECT_BOARD.md` - board, branch ownership, validation state, and backlog.
- `AI_CONTROL/05_HANDOFF.md` - latest handoff for the next worker.
- `AI_CONTROL/06_WORKER_LANES.md` - role rules for ChatGPT, Codex, Claude Code, Claude Desktop, Cursor, and Noel.
- `AI_CONTROL/14_CONTROL_CENTER_USER_GUIDE.md` - practical usage guide.

## Core Rules

- One active task at a time.
- One owner per task.
- One branch per task.
- No overlapping branch work.
- No stale branch merge.
- No archive edits.
- No app runtime edits unless the task explicitly allows them.
- No Stage 4 implementation unless a task explicitly starts Stage 4 runtime integration.
- Noel remains merge authority.

## Standard Loop

1. Define the task with `AI_CONTROL/07_TASK_TEMPLATE.md`.
2. Assign one owner and one branch.
3. Worker reads current state, task, board, and handoff.
4. Worker edits only allowed files.
5. Worker validates according to `AI_CONTROL/10_VALIDATION_EVIDENCE_PROTOCOL.md`.
6. Worker reports with `AI_CONTROL/08_COMPLETION_REPORT_TEMPLATE.md`.
7. Noel applies `AI_CONTROL/09_MERGE_GATE_CHECKLIST.md`.
8. After merge, update board, state, task, logs, handoff, follow-ups, and tag/branch retirement state.

## Validation Principle

GridFlow is validation-led, not feature-led. Work is not complete until the required evidence exists and is recorded.

## Historical Note

Earlier workflow guidance in this file has been superseded by Control Center v1.0. Historical docs may still provide background but must not override the active `AI_CONTROL/` v1 files.
