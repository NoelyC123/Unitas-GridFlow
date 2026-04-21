# Working Rules

## Before you edit a file
Read it first. Never assume contents.

## Stay narrow
Do not broaden scope. Do not redesign. Focus on the current task.

## Use minimum relevant files
Only read control files you need for the current work:
- Starting a task? Read `02_CURRENT_TASK.md`
- Need context? Read `01_CURRENT_STATE.md` or `04_SESSION_HANDOFF.md`
- Need to know how to work? Read this file.

## Make targeted edits
Make small, focused changes. One thing at a time.

---

## Standard workflow

1. Identify what you're working on
2. Read the relevant file(s)
3. Make the code change
4. Run `pytest -v`
5. Run `pre-commit run --all-files`
6. Commit with a clear message
7. Push to `master`
8. Wait for CI to pass

---

## When to update control files

Update immediately after work if:

- a broken flow now works
- the MVP state changed materially
- the current task is completed
- the next priority changed
- a new development phase started

**Files to update:**
- `01_CURRENT_STATE.md` (what works, what's weak)
- `02_CURRENT_TASK.md` (what is next)
- `04_SESSION_HANDOFF.md` (what changed this session)

---

## Three aligned layers

The project lives in three places:

1. **Canonical truth** (`AI_CONTROL/`) — what is, what works, what's next
2. **Live code** (`app/` and root) — the working implementation
3. **Strategy** (`PROJECT_SYNTHESIS/`) — analysis and decisions

Keep them aligned. If code changes but control files don't, misalignment happens.

---

## Checkpoint method

Stop and checkpoint when:
- a task completes
- the priority becomes unclear
- the control files feel stale

Answer:
1. What now works?
2. What is still weak?
3. What is the next decision?
4. Do the control files match reality?

Update them if they don't.

---

## Session workflow

**Start:** Read the current task. Read control files only if needed for that task.

**During:** Make changes, test, commit/push.

**End:** If the task changed the project state, update control files.

---

## Development debt

Known items that are not urgent:
- Old test jobs in `uploads/jobs/`
- `issues.csv` is verbose
- QA rules are basic (this is the priority to improve)
- No browser automation yet

These are not blockers unless tied to the current task.

---

## Bringing in external review

Only ask for external AI review when:
1. You have a specific question or decision
2. You have current control files ready
3. You are not in the middle of active build work

Don't ask:
- broad "what should we build?" questions during MVP work
- without reading current control files
- for work another AI already did
