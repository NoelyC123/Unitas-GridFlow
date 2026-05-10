# GridFlow Worker Finish Checklist

Purpose: standard exit checklist every worker follows before handing the branch back.

## Before handoff

1. Run the task-specific tests.
2. Run `pytest -v`.
3. Run `pre-commit run --all-files`.
4. Run `python3 scripts/manual_review.py` if UI, map, popup, or review workflow changed.
5. Inspect `git diff --stat`.
6. Confirm no forbidden files changed.
7. Run the merge baseline summary and include it in the commit message or handoff report:
   `git rev-list --left-right --count master...<branch>`
   Or use: `python3 scripts/merge_safety_check.py <branch>`
8. Run `python3 scripts/log_worker_update.py` with a concise summary, changed files, and validation state.
9. Run `python3 scripts/log_validation_run.py` after validation completes.
10. Update `AI_CONTROL/05_HANDOFF.md` with branch, status, what changed, validation state, and next action.
11. Commit with a clear message once the branch is ready for review.
12. Push the branch when the task or Noel's instructions require publication.
13. Report branch, commit, files changed, tests, validation, merge baseline summary, and final git status in the handoff response.

## Review Gate

- If `manual_review.py` was required, do not claim readiness without recording its report path and result.
- If `pytest -v` or `pre-commit run --all-files` fails, keep the branch in progress and document the failure.
- If forbidden files changed, stop and fix scope before handoff.
