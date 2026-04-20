# Unitas GridFlow — Master Source of Truth

This is the single primary authority for this project.
Every AI tool, every session, reads this file first — no exceptions.
If this file and any other file disagree, this file wins.

Last verified: 20 April 2026

---

## 1. Project identity

**Name:** Unitas GridFlow
**Short form:** A DNO survey compliance gatekeeper.
**Identity:** A narrow pre-CAD QA and compliance tool for UK electricity network survey-to-design handoffs.

**What it does:**
- Accepts survey CSV uploads from overhead line (OHL) field surveys
- Normalises input schema automatically
- Runs DNO-specific QA checks against configurable rulepacks
- Generates `issues.csv` and `map_data.json` per job
- Renders results on a Leaflet map with colour-coded PASS/FAIL markers
- Produces PDF QA reports
- Retains all job outputs locally for review and download

**What it is NOT:**
- Not a CAD/GIS replacement
- Not a broad software platform or general utility SaaS
- Not a digital twin or full engineering system
- Not a multi-tenant enterprise product
- Not an AI-first product

**Historical naming note:**
Previously called SpanCore, EW Design Tool, SpanCore-EW-Design-Tool, ew-design-tool.
All older repos are archived on GitHub and must not be used.

---

## 2. Canonical locations and commands

| Item | Value |
|---|---|
| Local folder | `/Users/noelcollins/Unitas-GridFlow` |
| GitHub repo | `https://github.com/NoelyC123/Unitas-GridFlow` |
| Active branch | `master` |
| Python | 3.13 |
| Virtual env | `.venv312` |
| App port | 5001 |
| Activate env | `source .venv312/bin/activate` |
| Run app | `python run.py` |
| Run tests | `pytest -v` |
| Lint | `pre-commit run --all-files` |
| Commit + push | `git add -A && git commit -m "..." && git push origin master` |

**Repo boundary rule:**
Only `/Users/noelcollins/Unitas-GridFlow` is the active canonical project.
Only `https://github.com/NoelyC123/Unitas-GridFlow` is the active canonical repo.
Any other folder or repo is archive/reference only.

---

## 3. Tech stack

**App:** Python 3.13, Flask 3.1.1, pandas 2.3.1, geopandas 1.1.1, reportlab 4.2.2, shapely 2.1.1, pyproj 3.7.1
**Frontend:** Leaflet (map), Bootstrap 5 (UI)
**Quality:** pre-commit, Ruff, pytest, pytest-cov, GitHub Actions CI, Dependabot

---

## 4. Current state (verified 20 April 2026)

**Phase:** Working local MVP + rulepack architecture complete + SPEN_11kV live with full cross-checks + 25 tests passing.

**Confirmed flow:** upload CSV → save file → run QA → save outputs → view map → download PDF → browse jobs

**Working routes:**
- `GET /`, `GET /upload`, `GET /jobs/`, `GET /health/full`
- `POST /api/presign`, `PUT /api/upload/<job_id>/<filename>`
- `POST /api/import/<job_id>`, `GET /api/jobs/`, `GET /api/jobs/<id>/status`
- `GET /map/view/<job_id>`, `GET /map/data/<job_id>`, `GET /pdf/qa/<job_id>`

**QA engine — 8 check types:**
`unique`, `required`, `range`, `allowed_values`, `regex`, `paired_required`, `dependent_allowed_values`, `coord_consistency`

**Rulepacks (in `app/dno_rules.py`):**
- `DEFAULT` — generic UK-wide `BASE_RULES` (fallback)
- `SPEN_11kV` — extends `BASE_RULES` with:
  - ENA TS 43-8 height range (7–20m)
  - Pole ID regex
  - Paired coord presence checks
  - SPEN network bounds (lat 54.5–60.9, lon -6.5 to -0.7)
  - Material/structure_type cross-field consistency
  - lat/lon ↔ easting/northing coordinate consistency (100m tolerance)

**Tests:** 25 passing
**CI:** GitHub Actions runs `pre-commit` + `pytest` on every push to `master`.

**Known weaknesses:**
1. Only one DNO rulepack (SPEN_11kV) — adding others is the active priority.
2. Input schema still narrow — one representative schema supported.
3. No Playwright browser tests yet — backend tests only.
4. `app/routes/api_rulepacks.py` returns stub data — needs wiring to real `RULEPACKS` dict.
5. `Makefile` has stale port (5010 instead of 5001).

---

## 5. Current next priority

1. Add `SSEN_11kV` rulepack.
2. Add remaining DNO rulepacks (NIE, ENWL, NGED, UKPN).
3. Wire `app/routes/api_rulepacks.py` to the real `RULEPACKS` dict.
4. Fix `Makefile` port (5010 → 5001).

**What is NOT the current priority:**
- Browser E2E testing (Playwright) — later, once UI is stable.
- Deployment / hosting — later.
- UI redesign — later.
- Database integration — not planned.
- Broad feature expansion — never without proof-of-value.

---

## 6. Tool roles

### Claude app (claude.ai — in the Unitas-GridFlow Project)
**Role: live development sessions.**
Has Filesystem MCP access — reads/writes files directly on the Mac.

Use for:
- Active development sessions with direct file access.
- Implementing code changes directly to disk.
- Reviewing and improving the codebase.
- Updating the control layer after meaningful changes.
- Architecture review and structured decisions.

Rules:
- Always read this file fresh from disk at session start.
- Never ask the user to copy/paste code or upload files.
- Always remind the user to run `pytest -v` after changes.

Do NOT use for: offline/air-gapped work; sensitive content that must not leave the machine.

### Claude Code
**Role: terminal-based repo work.**
Reads `CLAUDE.md` at session start.

Use for:
- Reading the repo from a terminal workflow.
- Tracing routes/imports across files.
- Running commands and interpreting output.
- Debugging in the terminal.

Choose Claude app if the task is "edit several files and confirm they're correct"; choose Claude Code if the task is "I'm already in the terminal and want repo-aware reasoning here".

### Cursor Pro
**Role: in-editor AI coding.**
Reads `.cursorrules` when the project is opened.

Use for:
- Writing new functions and classes inside the editor.
- Multi-file refactoring with AI assistance.
- Inline suggestions while editing code.

### GitHub Copilot
**Role: passive inline autocomplete.**
Always on in VS Code.

Use for: inline completion, repetitive patterns.
Do NOT treat Copilot suggestions as authoritative — it will confidently hallucinate DNO-specific values. Always verify domain logic against rulepack source references.

### ChatGPT
**Role: strategic decisions only.**

Use for: architecture review at genuine decision points, prioritisation between competing approaches, synthesising multiple AI opinions.
Do NOT use for: day-to-day implementation, or for tasks Claude app can do with direct file access.

When used for formal review, prepare bundles per `06_DEVELOPMENT_PROCESS.md`.

### Second-opinion AI (Gemini or Grok — pick one per decision)
**Role: occasional challenger at genuine decision points.**

Use sparingly. One second opinion per real decision, not both.

### Ollama (local)
**Role: offline/private drafting only.**
Models: `qwen2.5:14b-instruct` (main), `llama3.2` (fast).

Optional. Use only when cloud tools are not appropriate (private content, offline).

### Tool priority for implementation work

1. Claude app (Filesystem MCP)
2. Claude Code
3. Cursor Pro
4. Copilot (passive)
5. ChatGPT / second-opinion AI — decision points only
6. Ollama — offline/private only

**Rule:** Pick one editing tool per session. Don't switch mid-task.

---

## 7. Hard rules

1. Read this file first — every session, every tool, no exceptions.
2. Never use non-canonical repos or folders as current truth.
3. Never broaden scope beyond the narrow MVP.
4. Never add features not tied to the current task.
5. Always read a file before editing it — never assume contents.
6. Always run `pytest -v` after any code change.
7. Always `git add / commit / push` after confirmed passing tests.
8. Always update this file and supporting control files when state changes materially.
9. Never restore from `_quarantine/` blindly.
10. Never let different tools work from different project states.
11. Never treat Copilot or autocomplete suggestions as authoritative for DNO-specific values.

---

## 8. Session start rule

**Every session, every tool:**

1. Read `AI_CONTROL/00_MASTER_SOURCE_OF_TRUTH.md` (this file).
2. Read `AI_CONTROL/03_CURRENT_TASK.md`.
3. Read `AI_CONTROL/04_SESSION_HANDOFF.md`.
4. Then start work.

**Also read when relevant:**
- `AI_CONTROL/02_CURRENT_STATE.md` — deeper technical state (routes, rulepack internals, tech debt).
- `AI_CONTROL/06_DEVELOPMENT_PROCESS.md` — process, checkpoint method, review bundle method.
- `CHANGELOG.md` — rolling history of what shipped, session by session.
- `PROJECT_SYNTHESIS/03_DECISION_MEMO/FINAL_DECISION_MEMO.md` — strategic context at decision points.
- `PROJECT_SYNTHESIS/04_EXECUTION_ALIGNMENT/EXECUTION_ALIGNMENT_PLAN.md` — execution alignment.

---

## 9. File map

### Control layer (define how work is done)
- `AI_CONTROL/00_MASTER_SOURCE_OF_TRUTH.md` — this file. Primary authority.
- `AI_CONTROL/02_CURRENT_STATE.md` — deeper technical state reference.
- `AI_CONTROL/03_CURRENT_TASK.md` — immediate task.
- `AI_CONTROL/04_SESSION_HANDOFF.md` — most recent session handoff.
- `AI_CONTROL/06_DEVELOPMENT_PROCESS.md` — process and workflow.

### Tool bootstrap (read automatically by tools)
- `CLAUDE.md` — Claude Code bootstrap.
- `.cursorrules` — Cursor Pro bootstrap.

### Project record
- `CHANGELOG.md` — rolling record of what shipped, session by session.

### Live implementation
- `app/` — Flask app, routes, templates, static.
- `tests/` — pytest suite.
- `run.py`, `requirements.txt`, `pyproject.toml` — entry point and config.
- `sample_data/`, `uploads/`, `temp_gis/` — data directories.

### Strategic / analytical (reference, not operational)
- `PROJECT_SYNTHESIS/` — strategic synthesis, decision memos, execution alignment.

### Archive / non-canonical
- `_quarantine/`, `_archive/`, `GITHUB_ADMIN/`, bundle directories — reference/archive only.

---

## 10. How to update this file

When project state changes materially, update this file **first** — then propagate to other files only where genuinely needed.

### Update checklist by trigger

| Trigger | Update in this file |
|---|---|
| Test count changes | §4 "Tests:" line |
| New QA check type added | §4 "QA engine" list |
| New rulepack added | §4 "Rulepacks" list; §5 if it completes a priority |
| Priority shipped | §5 remove + renumber; §4 weaknesses if applicable |
| New weakness discovered | §4 weaknesses |
| Tech stack change | §3 |
| New tool / role change | §6 |
| Control-layer file added/removed | §9 |

### Rule about secondary files

**No other control file should hard-code test counts, check-type counts, or priority lists.** If you find stale facts elsewhere, fix the other file by *removing* the hard-coded fact, not by updating both places.

The only secondary files that legitimately need synchronised rewrites:
- `AI_CONTROL/03_CURRENT_TASK.md` — rewrite when the priority changes.
- `AI_CONTROL/04_SESSION_HANDOFF.md` — rewrite per session.
- `AI_CONTROL/02_CURRENT_STATE.md` — update only when technical detail (routes, rulepack internals, tech debt) changes.
- `CHANGELOG.md` — append per session.
