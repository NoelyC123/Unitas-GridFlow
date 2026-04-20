# AI Control — Read This First

This folder is the active coordination layer for the **Unitas GridFlow** project.

It exists so all AI tools — Claude app, Claude Code, Cursor, ChatGPT, Gemini, Grok —
work from the same current truth and do not drift from each other.

## Required read order for any AI — every session

1. `AI_CONTROL/00_READ_THIS_FIRST.md` ← you are here
2. `AI_CONTROL/01_PROJECT_TRUTH.md`
3. `AI_CONTROL/02_CURRENT_STATE.md`
4. `AI_CONTROL/03_CURRENT_TASK.md`
5. `AI_CONTROL/04_SESSION_HANDOFF.md`
6. `AI_CONTROL/05_AI_ROLE_RULES.md`
7. `AI_CONTROL/06_DEVELOPMENT_PROCESS.md`

Do not skip any of these. Do not assume the project state from memory.
Always read fresh from disk.

## Deep reference documents

After reading the AI_CONTROL files, the strategic synthesis is here:

- `PROJECT_SYNTHESIS/SPANCORE_SYNTHESIS_READ_FIRST.md` — read this first for synthesis context
- `PROJECT_SYNTHESIS/02_FINAL_SYNTHESIS/SPANCORE_MASTER_SYNTHESIS.md` — full strategic analysis
- `PROJECT_SYNTHESIS/03_DECISION_MEMO/FINAL_DECISION_MEMO.md` — what was decided and why

Note: These synthesis documents use the old name "SpanCore" in historical context.
The canonical active name is **Unitas GridFlow**. That context is correct and intentional.

## Canonical code locations

- **Live code** = project root + `app/`
- **Tests** = `tests/`
- **Control layer** = `AI_CONTROL/`
- **Synthesis/strategy** = `PROJECT_SYNTHESIS/`
- **Quarantine** = `_quarantine/` — legacy reference only, do not restore blindly

## Current development rules

- Do not broaden scope
- Do not redesign the product
- Do not invent new platform goals
- Stay narrow MVP focused
- Always run `pytest -v` after any code change
- Always commit and push after confirmed passing tests
