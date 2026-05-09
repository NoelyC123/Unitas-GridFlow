# GridFlow Worker Finish Checklist

Purpose: standard exit checklist every worker follows before handing the branch back.

## Before handoff

1. Run the task-specific tests.
2. Run `pytest -v`.
3. Run `pre-commit run --all-files`.
4. Run `python3 scripts/manual_review.py` if UI, map, popup, or review workflow changed.
5. Inspect `git diff --stat`.
6. Confirm no forbidden files changed.
7. Run `python3 scripts/log_worker_update.py` with a concise summary, changed files, and validation state.
8. Run `python3 scripts/log_validation_run.py` after validation completes.
9. Update `AI_CONTROL/05_HANDOFF.md` with branch, status, what changed, validation state, and next action.
10. Commit with a clear message once the branch is ready for review.
11. Push the branch when the task or Noel's instructions require publication.
12. Report branch, commit, files changed, tests, validation, and final git status in the handoff response.

## Review Gate

- If `manual_review.py` was required, do not claim readiness without recording its report path and result.
- If `pytest -v` or `pre-commit run --all-files` fails, keep the branch in progress and document the failure.
- If forbidden files changed, stop and fix scope before handoff.
