# Completion Report Template

Purpose: standard worker completion report for handoff back to Noel or the controller.

## Required Format

```text
Branch:
<branch>

Commit:
<hash or not committed>

Files changed:
- <path>

Summary:
- <what changed>
- <what did not change>

Validation:
- pytest -v: <pass/fail/not run with reason>
- pre-commit run --all-files: <pass/fail/not run with reason>
- manual/browser validation: <pass/fail/not required with reason>

Evidence:
- validation_runs report: <path or n/a>
- failures.json: <[] / path / n/a>
- screenshots: <yes/no/unknown and reason>

Scope confirmations:
- app runtime changed: <yes/no>
- archive changed: no
- Stage 4 runtime implementation changed: <yes/no>
- protected files changed: <list or none>

Open gaps:
- <none or specific remaining work>

Final git status:
<git status --short --branch summary>
```

## Standard Merge Approval Format

```text
MERGE APPROVED

Branch:
<branch>

Commit:
<hash>

Validation accepted:
- <commands and evidence>

Merge method:
<merge commit | squash | fast-forward>

Post-merge required:
- update Control Center files on master
- create or move milestone tag
- retire branch according to AI_CONTROL/11_BRANCH_RETIREMENT_PROTOCOL.md
```

## Standard Failed-Validation Format

```text
VALIDATION FAILED

Branch:
<branch>

Failed command:
<command>

Failure summary:
<short actionable summary>

Files likely involved:
- <path>

Evidence:
- logs: <path or excerpt>
- screenshots: <path or n/a>
- failures.json: <path or n/a>

Next action:
<fix, re-run, rollback, or controller decision needed>
```

## Report Rules

- Do not hide skipped validation.
- Do not claim browser validation from unit tests.
- Do not claim screenshots exist unless they were captured.
- Do not say a branch is ready if the working tree is dirty with unexplained changes.
