# Merge Gate Checklist

Purpose: define the exact gate before any branch can be merged.

## Required Gate

- Branch name matches the task prompt.
- Branch has one clear owner.
- Branch scope matches allowed files.
- No forbidden files changed.
- No archive files changed.
- No unrelated feature work mixed in.
- Branch is based on current master or has been rebased/merged from current master.
- All conflict markers removed.
- Required tests passed after the final code/doc state.
- Required pre-commit hooks passed after the final code/doc state.
- Manual/browser validation completed when UI, map, popup, route, planner awareness, lifecycle, or review navigation behavior changed.
- `AI_CONTROL/03_WORKER_LOG.md` updated.
- `AI_CONTROL/04_VALIDATION_LOG.md` updated.
- `AI_CONTROL/05_HANDOFF.md` updated.
- Completion report received.
- Noel approves the merge.

## No Overlapping Branch Rule

Do not merge if another active branch changes the same runtime area, behavior, or control files and has not been reconciled. Resolve by rebasing, merging master into the branch, or closing one branch.

## No Stale Branch Merge Rule

Do not merge if:

- validation happened before the latest rebase or conflict resolution;
- master moved after validation in a way that touches the same files;
- the branch has unknown local changes;
- the completion report omits required validation.

## Post-Merge Control File Updates

After merge to master:

- Update `00_PROJECT_BOARD.md` stable milestones and Done section.
- Update `01_CURRENT_STATE.md` if product/control state changed.
- Clear or advance `02_CURRENT_TASK.md`.
- Append merge and validation entries to `03_WORKER_LOG.md` and `04_VALIDATION_LOG.md`.
- Update `05_HANDOFF.md` with the new stable state and next action.
- Update `12_OPEN_FOLLOWUPS.md` for closed or newly discovered follow-ups.
- Create or move the milestone tag only after the merge commit is final.

## Merge Authority

Only Noel merges into master or explicitly authorizes a worker to do so. AI workers may prepare branches and commits; they must not merge by default.
