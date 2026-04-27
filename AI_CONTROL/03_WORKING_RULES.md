# Working Rules

## Core principles

- Always read a file before editing it.
- Never assume file contents.
- Stay within the current stage.
- Do not broaden scope beyond the current stage.
- Prefer simple, clear, deterministic logic.
- Every step must answer: "Does this improve the reliability, clarity, and design-readiness of real survey data?"

---

## Tool roles

### Claude Desktop (Project Orchestrator)
- Defines what gets built, why, and in what order
- Reviews validation results for major stage gates or ambiguous decisions
- Prevents scope drift
- Holds full project context
- Use selectively; not required for every small documentation or closure step

### Claude Code (VS Code — Primary Builder)
- Reads repo, writes code, runs tests, commits, pushes
- Executes tasks as defined by the orchestrator
- Makes minimal, targeted changes
- Keeps tests passing
- Use mainly for code, tests, and complex repo-wide changes; avoid spending Claude Code usage on routine admin-only docs

### ChatGPT
- Available for second opinions, commercial thinking, review
- Not the primary orchestrator

---

## Development workflow

After code changes:

1. `pytest -v` — all tests must pass
2. `pre-commit run --all-files`
3. `git add . && git commit -m "clear message" && git push`

Documentation-only changes should be lightweight:

- Major stage closure: update only the minimum control docs needed.
- Small polish/bugfix: changelog only if useful.
- Do not create closure/review/planning documents for every small task.
- Prefer Cursor/GPT for routine admin updates to preserve Claude usage.

---

## Validation-first rule

Real-world evidence takes priority over abstract feature expansion. Do not build features without validation evidence from real survey files.

---

## Stage discipline

The project has 6 stages. Work on the current stage only. Do not jump ahead.

1. Post-survey QA gate ✅
2. Survey-to-design direct handoff / D2D elimination ✅
3. Live intake platform ✅
4. Structured field capture ← FUTURE
5. Designer workspace
6. DNO submission layer

Current operating mode: use the completed Stage 3 tool on real survey-to-design work. Do not begin Stage 4 implementation until operational evidence identifies the first field-capture requirement worth building.

---

## Source of truth

1. Real survey files (highest)
2. AI_CONTROL/ files
3. Repo code and tests
4. Documentation
5. AI outputs (lowest)
