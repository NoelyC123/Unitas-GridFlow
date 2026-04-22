# Working Rules

## Core principles

- Always read a file before editing it.
- Never assume file contents.
- Stay strictly within the current task.
- Do not broaden scope.
- Prefer simple, clear, deterministic logic.

---

## Project structure awareness (CRITICAL)

The repository has three layers:

### 1. Active project (use this)
- `AI_CONTROL/`
- `app/`
- `tests/`
- `sample_data/`
- root config files

### 2. Archive (reference only — do not use)
- `_archive/`

Contains:
- old control layer
- synthesis documents
- AI bundles
- quarantined code
- legacy documentation

**Rule:**
Do NOT use `_archive/` for implementation or decision-making unless explicitly instructed.

---

### 3. Local/tool files (ignore as project truth)
- `.env`
- `.vscode/`
- `.claude/`
- `.venv312/`
- caches / coverage

---

## Use minimum necessary context

Only read what you need:

- Starting work → `02_CURRENT_TASK.md`
- Need state → `01_CURRENT_STATE.md`
- Need session context → `04_SESSION_HANDOFF.md`
- Need working rules → this file

Avoid reading everything by default.

---

## Make targeted changes

- One change at a time
- Small, focused edits
- Avoid large rewrites
- Keep logic simple and traceable

---

## Standard development workflow

1. Identify the task
2. Read relevant file(s)
3. Make the change
4. Run:
   ```bash
   pytest -v
   ```
5. Run:
   ```bash
   pre-commit run --all-files
   ```
6. Commit:
   ```bash
   git add .
   git commit -m "clear, specific message"
   git push
   ```
7. Wait for CI to pass

---

## Control layer alignment

The project must stay aligned across:

1. `AI_CONTROL/` → truth and direction
2. `app/` → implementation
3. `_archive/` → history (reference only)

If code changes but control files don’t → misalignment.

---

## When to update control files

Update immediately if:

- a flow starts working
- project behaviour changes
- the current task is completed
- the next priority changes
- a new phase begins

Files to update:
- `01_CURRENT_STATE.md`
- `02_CURRENT_TASK.md`
- `04_SESSION_HANDOFF.md`
- `CHANGELOG.md` (if something shipped)

---

## Checkpoint method

Stop and reassess when:

- a task completes
- direction becomes unclear
- control files feel outdated

Ask:

1. What now works?
2. What is still weak?
3. What is the next priority?
4. Do control files reflect reality?

Update them if not.

---

## Session workflow

### Start
- Read `02_CURRENT_TASK.md`
- Read additional files only if needed

### During
- Implement changes
- test → commit → push

### End
- Update control files if state changed

---

## Development constraints

- This is a narrow MVP tool
- Do not expand scope
- Do not redesign architecture during feature work
- Do not introduce unrelated improvements

---

## Known non-urgent items

These are not priorities unless directly relevant:

- old job files in `uploads/`
- verbose `issues.csv`
- limited input schema support
- lack of browser automation

---

## External AI usage

Only bring in external AI when:

- you have a specific question
- you have read current control files
- you are not mid-implementation

Do NOT:

- ask broad open-ended questions
- ask for work already defined
- skip reading current task/state

---

## Final rule

**Always follow the control layer.
Never rely on memory.
Never rely on archive.**
