# Control Center User Guide

Purpose: practical guide for using the GridFlow Control Center v1.0.

## What The Control Center Controls

- Active task and branch ownership.
- Worker roles and lanes.
- Allowed and forbidden file scope.
- Handoff protocol.
- Completion report protocol.
- Validation evidence protocol.
- Merge gate checklist.
- Branch retirement.
- Open follow-ups.
- C2E2 closeout state.
- Conflict and rollback response.

## Standard Workflow

1. Noel or ChatGPT controller defines one task using `07_TASK_TEMPLATE.md`.
2. Worker creates or switches to the named branch.
3. Worker reads `01_CURRENT_STATE.md`, `02_CURRENT_TASK.md`, `00_PROJECT_BOARD.md`, `05_HANDOFF.md`, and task-specific docs.
4. Worker updates the board/task/handoff if ownership or status changes.
5. Worker implements only allowed scope.
6. Worker validates according to `10_VALIDATION_EVIDENCE_PROTOCOL.md`.
7. Worker updates `03_WORKER_LOG.md`, `04_VALIDATION_LOG.md`, and `05_HANDOFF.md`.
8. Worker reports using `08_COMPLETION_REPORT_TEMPLATE.md`.
9. Noel reviews the merge gate in `09_MERGE_GATE_CHECKLIST.md`.
10. After merge, control files are updated and the branch is retired.

## How Codex Should Use It

- Treat `02_CURRENT_TASK.md` and the user prompt as binding.
- Make scoped edits and run required validation.
- Commit when the deliverable asks for a commit.
- Do not merge, push, delete branches, or edit archive unless explicitly instructed.

## How Claude Code Should Use It

- Start with `scripts/control_status.py` if available.
- Use terminal access for audits, conflict resolution, broad tests, and evidence gathering.
- Preserve all log entries during conflict resolution.
- Report branch status before continuing if branch confusion occurs.

## How ChatGPT Should Use It

- Write task prompts from the template.
- Keep one active task.
- Assign one owner and one branch.
- Include validation and evidence requirements.
- Avoid vague "continue" prompts without branch and scope.

## How Claude Desktop Should Use It

- Review domain/spec decisions and stage boundaries.
- Use the closeout and follow-up trackers to prevent re-opening closed scope by accident.
- Record major decisions through a task prompt or handoff update.

## How Noel Should Use It

- Check `00_PROJECT_BOARD.md` first.
- Check `05_HANDOFF.md` for the latest worker state.
- Approve merge only after the merge gate is satisfied.
- After merge/tag, ensure control files record the new stable state.
