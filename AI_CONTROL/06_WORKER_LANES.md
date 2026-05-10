# Worker Lanes

Purpose: define who does what so workers do not duplicate effort or cross branch scopes.

## ChatGPT Controller

ChatGPT is the controller when Noel uses it to write or refine task prompts.

Rules:

- Owns task definition, sequencing, and scope clarity.
- Reads `01_CURRENT_STATE.md`, `02_CURRENT_TASK.md`, `00_PROJECT_BOARD.md`, and `05_HANDOFF.md` before creating a task prompt.
- Must name one branch, one owner, allowed files, forbidden files, validation commands, and expected output.
- Must enforce one-task-at-a-time and no overlapping branch rules.
- Must not claim code is complete without worker evidence.
- Must not instruct any worker to merge to master unless Noel explicitly directs the merge.

## Codex Implementation Worker

Codex is the default implementation worker for bounded repo tasks.

Rules:

- Run the requested task on the named branch.
- Read the current task and board before editing.
- Keep edits inside allowed files.
- Prefer existing patterns and minimal changes.
- Run required validation before handoff.
- Commit only the task changes when asked or when the task deliverable requires a commit.
- Do not push, open PRs, merge, delete branches, or modify master unless explicitly instructed.

## Claude Code Terminal / Audit Worker

Claude Code is the terminal, audit, conflict-resolution, and broad repo inspection worker.

Rules:

- Best used for large read-only audits, rebase conflict resolution, test triage, and implementation work that needs full terminal context.
- Must preserve all worker log and validation log entries during conflict resolution.
- Must not silently resolve business/domain conflicts; report them to Noel or ChatGPT controller.
- Must not merge into master unless Noel explicitly performs or authorizes the merge.

## Claude Desktop Spec / Domain Reviewer

Claude Desktop is the spec and domain-review lane.

Rules:

- Reviews product scope, engineering truthfulness, field reality, and stage discipline.
- Should be used for ambiguous product decisions, Stage 4 scope, DNO rulepack strategy, and closeout reviews.
- Should not directly edit runtime code unless Noel explicitly chooses that path.
- Must distinguish real survey evidence from inferred, planned, or unavailable fields.

## Cursor / Local Editor Lane

Cursor may be used for small local edits and review.

Rules:

- Use only for bounded cleanup, local review, or small documentation changes.
- Must follow the same allowed-file and validation rules as other workers.
- Must not become a parallel implementation branch unless the board assigns it.

## Noel

Noel is final project owner and merge authority.

Rules:

- Approves scope, merge decisions, tags, and branch retirement.
- Provides real survey evidence and business/domain judgement.
- May override worker recommendations but should record decisions in the Control Center after merge.

## Lane Conflict Rule

If two workers are active, their lanes must not write the same files or solve the same task. If overlap is detected, all workers stop and the controller updates `00_PROJECT_BOARD.md` and `05_HANDOFF.md`.
