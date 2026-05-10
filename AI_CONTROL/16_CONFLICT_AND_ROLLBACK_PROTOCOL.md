# Conflict And Rollback Protocol

Purpose: emergency rules for branch confusion, rebase conflicts, bad merges, and failed validation.

## Stop Conditions

Stop and report before continuing if:

- current branch does not match the task prompt;
- unrelated dirty files exist in the worktree;
- conflict markers are present;
- app runtime files changed on a docs/control branch;
- archive files changed;
- validation fails and the fix is outside task scope;
- two active branches overlap.

## Conflict Resolution Rules

- Do not abort a rebase or merge unless continuing would destroy work or Noel approves.
- Do not skip commits unless Noel approves.
- Preserve both sides of worker logs and validation logs.
- For `05_HANDOFF.md`, the newest active task should be current after resolution.
- Remove all `<<<<<<<`, `=======`, and `>>>>>>>` markers.
- Run validation after resolving conflicts.

## Emergency Rollback Rules

Rollback is a controller/Noel decision unless a worker is explicitly tasked with it.

Allowed rollback actions only when explicitly instructed:

- revert a named commit with `git revert`;
- create an emergency branch from master;
- restore a file from a named commit;
- move a tag after merge correction.

Forbidden by default:

- `git reset --hard`
- deleting branches
- deleting tags
- force pushing
- rewriting master history
- modifying archive to hide mistakes

## Failed Validation Response

1. Capture the failing command and summary.
2. Check whether the failure is in scope.
3. If in scope, fix narrowly and rerun validation.
4. If out of scope, stop and report.
5. Record the failure and final result in `04_VALIDATION_LOG.md`.

## Branch Confusion Response

Run:

```bash
git status --short --branch
git branch --show-current
git diff --name-only
```

Then report:

- current branch;
- dirty files;
- whether files are allowed by task;
- proposed next action.
