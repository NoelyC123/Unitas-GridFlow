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
- Reviews validation results
- Manages all tools
- Prevents scope drift
- Holds full project context

### Claude Code (VS Code — Primary Builder)
- Reads repo, writes code, runs tests, commits, pushes
- Executes tasks as defined by the orchestrator
- Makes minimal, targeted changes
- Keeps tests passing

### ChatGPT
- Available for second opinions, commercial thinking, review
- Not the primary orchestrator

---

## Development workflow

After code changes:

1. `pytest -v` — all tests must pass
2. `pre-commit run --all-files`
3. `git add . && git commit -m "clear message" && git push`

---

## Validation-first rule

Real-world evidence takes priority over abstract feature expansion. Do not build features without validation evidence from real survey files.

---

## Stage discipline

The project has 6 stages. Work on the current stage only. Do not jump ahead.

1. Post-survey QA gate ✅
2. D2D elimination ← CURRENT
3. Live intake platform
4. Structured field capture
5. Designer workspace
6. DNO submission layer

---

## Source of truth

1. Real survey files (highest)
2. AI_CONTROL/ files
3. Repo code and tests
4. Documentation
5. AI outputs (lowest)
