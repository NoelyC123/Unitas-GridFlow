# Development Process

This file defines **how work is done** on the project. Identity, state, tool roles, and hard rules all live in `00_MASTER_SOURCE_OF_TRUTH.md` — this file does not duplicate them.

---

## 1. Three layers

Work touches three aligned layers:

1. **Control layer** (`AI_CONTROL/`) — what the project is, current state, current task, last handoff, process (this file).
2. **Strategic layer** (`PROJECT_SYNTHESIS/`) — decision memos, execution alignment, saved reviews. Reference, not operational.
3. **Implementation layer** — `app/`, `tests/`, `run.py`, `pyproject.toml`, `requirements.txt`, `sample_data/`, `uploads/`, `temp_gis/`.

All future work must keep these three layers aligned.

---

## 2. Development cycle

Every development cycle follows this sequence.

### Step 1 — Build
Make the smallest necessary change.

### Step 2 — Test locally
- `pytest -v`
- `pre-commit run --all-files`
- Flask / route / output check if relevant.

### Step 3 — Did material truth change?
If yes — update the master truth file **first**, then:
- `AI_CONTROL/02_CURRENT_STATE.md` if technical detail changed.
- `AI_CONTROL/03_CURRENT_TASK.md` if the priority changed.

If no — continue.

### Step 4 — Commit and push
- `git add -A`
- clear commit message
- `git push origin master`

### Step 5 — Let CI validate
GitHub Actions runs `pre-commit` + `pytest` on every push to `master`.

### Step 6 — End-of-session
- Update `AI_CONTROL/04_SESSION_HANDOFF.md`.
- Append a dated entry to `CHANGELOG.md`.

---

## 3. Checkpoint method

Stop and checkpoint whenever:
- A previously broken flow now works.
- The MVP changes state materially.
- A current priority is completed.
- The next decision becomes ambiguous.
- Another AI is about to be asked to review the project.

At a checkpoint, answer:

1. What now works?
2. What is still weak?
3. What is the immediate next decision?
4. Has the current task changed?
5. Does the master truth file still reflect live truth? If not, update it first.

---

## 4. When control files must be updated

Update control files whenever:
- The working MVP materially changes.
- A blocker is removed.
- A priority is completed.
- The immediate task changes.
- A session ends after meaningful work.
- The project enters a new development phase.

**Minimum update rule.** If project truth changed materially, master truth (§4 and §5) is always first. Everything else follows.

---

## 5. Review bundle method

When an external AI review is genuinely needed (not for every question), prepare bundles from the current canonical state.

### Bundle set
1. **Control layer** — everything in `AI_CONTROL/` + `CHANGELOG.md`.
2. **Project synthesis** — everything in `PROJECT_SYNTHESIS/`.
3. **Live app** — current live `app/` + key root files + templates/static + active routes.

### Naming
`01_AI_CONTROL.zip`, `02_PROJECT_SYNTHESIS.zip`, `03_LIVE_APP_REVIEW.zip`.

### Rule
Do not build ad hoc bundles with missing layers for major review questions.

---

## 6. Where reviews and prompts are saved

All prompt/review support documents go in:

`PROJECT_SYNTHESIS/05_SUPPORT_NOTES/`

Naming: `<AI>_<TOPIC>_<PROMPT_or_REVIEW>.md`. Example:

- `CLAUDE_NEXT_PRIORITY_PROMPT.md`
- `CLAUDE_NEXT_PRIORITY_REVIEW.md`

---

## 7. What not to do

- Don't let different tools work from different project states.
- Don't broad-brainstorm during active MVP build work.
- Don't broaden scope because a tool suggests interesting possibilities.
- Don't skip control-layer updates after meaningful state changes.
- Don't treat synthesis docs as live truth if the app has moved on.
- Don't treat archived repos or old uploaded files as active context.
- Don't ask for AI reviews without current bundles when the decision matters.

---

## 8. Final operating rule

**current truth → live implementation → local checks → commit/push → CI → checkpoint → controlled review → exact next step**

That sequence governs all future work.
