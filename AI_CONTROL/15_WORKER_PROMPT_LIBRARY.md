# Worker Prompt Library

Purpose: reusable prompts for common GridFlow worker actions.

## Codex Implementation Prompt

```text
TASK: <task>

Branch:
codex/<task-slug>

Use:
- AI_CONTROL/01_CURRENT_STATE.md
- AI_CONTROL/02_CURRENT_TASK.md
- AI_CONTROL/00_PROJECT_BOARD.md
- AI_CONTROL/05_HANDOFF.md

Allowed files:
- <paths>

Forbidden:
- app/ unless explicitly allowed
- archive/
- unrelated docs/tests

Do the scoped implementation, run validation, update control logs, commit, and report branch, commit, files changed, checks, and final status.
```

## Claude Code Audit Prompt

```text
TASK: Audit <branch/task>

Branch/worktree:
<branch or path>

Do not modify files unless explicitly asked.

Inspect:
- branch status
- changed files
- validation evidence
- conflicts or stale master state
- forbidden-file changes

Return findings first, then recommended next action.
```

## Claude Code Conflict Prompt

```text
TASK: Resolve conflicts for <branch>

Rules:
- Do not abort unless impossible.
- Do not skip the task commit unless Noel approves.
- Preserve all worker log and validation log entries.
- Remove conflict markers.
- Continue rebase/merge only after inspecting conflicts.
- Rerun required validation after conflict resolution.
```

## Claude Desktop Spec Review Prompt

```text
TASK: Domain/spec review for <topic>

Use:
- AI_CONTROL/01_CURRENT_STATE.md
- AI_CONTROL/13_C2E2_CLOSEOUT.md
- task-specific docs

Review for:
- scope drift
- field truthfulness
- stage boundary violations
- validation gaps
- product/domain risk

Return decisions, open questions, and recommended task prompt if implementation is needed.
```

## Failed Validation Prompt

```text
TASK: Fix failed validation on <branch>

Failure:
<command and summary>

Rules:
- Fix only the failure.
- Do not broaden feature scope.
- Preserve unrelated user changes.
- Rerun the failed command and required gate.
- Update validation log and handoff.
```

## Merge Approval Prompt

```text
TASK: Merge review for <branch>

Check:
- AI_CONTROL/09_MERGE_GATE_CHECKLIST.md
- completion report
- changed files
- validation evidence
- final git status

Return:
- approve or block
- required post-merge control updates
- tag name
- branch retirement note
```
