# Branch Retirement Protocol

Purpose: prevent stale branches and repeated merge confusion.

## Retirement States

- `active`: branch is the current task branch.
- `review`: work is complete and waiting for review or merge.
- `merged`: branch was merged to master.
- `retired`: branch should not receive new work.
- `abandoned`: branch is intentionally not merged.

## Standard Branch Retirement Format

```text
BRANCH RETIREMENT

Branch:
<branch>

Final state:
<merged | retired | abandoned>

Final commit:
<hash>

Merged/tagged as:
<merge hash and tag, or n/a>

Validation:
<final accepted validation>

Reason:
<completed, superseded, abandoned, or conflict resolved elsewhere>

Do not reuse this branch for:
<future task description>
```

## Retirement Rules

- Do not delete branches from a worker task unless Noel explicitly instructs it.
- Do not reuse merged branches for new work.
- Do not merge stale branches without revalidation.
- Do not leave a completed branch marked active in the board.
- Tags must point to the final merge or accepted commit, not an earlier pre-merge commit unless Noel chooses that policy.

## After Merge

- Mark the task Done in `00_PROJECT_BOARD.md`.
- Update `05_HANDOFF.md` with next action.
- Add follow-ups to `12_OPEN_FOLLOWUPS.md`.
- Record branch retirement in `03_WORKER_LOG.md`.
