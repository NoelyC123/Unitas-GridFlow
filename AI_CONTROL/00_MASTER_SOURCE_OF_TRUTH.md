# Unitas GridFlow — Master Source of Truth

This is the single primary authority file for the Unitas GridFlow project.
Every AI tool, every session, reads this file first — no exceptions.
If this file and any other file disagree, this file wins.
When project state changes materially, update this file first.

Last verified: 20 April 2026 | Tests: 23 passing | Port: 5001

---

## 1. Project identity

**Name:** Unitas GridFlow
**Identity:** A narrow pre-CAD QA and compliance tool for UK electricity network survey-to-design handoffs
**Short form:** A DNO survey compliance gatekeeper

**What it does:**
- Accepts survey CSV uploads from overhead line (OHL) field surveys
- Normalises input schema automatically
- Runs DNO-specific QA checks against configurable rulepacks
- Generates issues.csv and map_data.json per job
- Renders QA results on a Leaflet map with colour-coded PASS/FAIL markers
- Produces PDF QA reports per job
- Retains all job outputs locally for review and download

**What it is NOT:**
- Not a CAD/GIS replacement
- Not a broad software platform or general utility SaaS
- Not a digital twin or full engineering system
- Not a multi-tenant enterprise product
- Not an AI-first product

**Historical naming note:**
Previously called SpanCore, EW Design Tool, SpanCore-EW-Design-Tool, ew-design-tool.
All older repos with those names are archived on GitHub and must not be used.

---

## 2. Canonical locations

| Item | Value |
|---|---|
| Local folder | `/Users/noelcollins/Unitas-GridFlow` |
| GitHub repo | `https://github.com/NoelyC123/Unitas-GridFlow` |
| Active branch | `master` |
| Python | 3.13 |
| Virtual env | `.venv312` |
| App port | 5001 |
| Activate | `source .venv312/bin/activate` |
| Run app | `python run.py` |
| Run tests | `pytest -v` — 23 tests must pass |
| Lint | `pre-commit run --all-files` |
| Commit | `git add -A && git commit -m "..." && git push origin master` |

**Repo boundary rule (absolute):**
Only `/Users/noelcollins/Unitas-GridFlow` is the active canonical project.
Only `https://github.com/NoelyC123/Unitas-GridFlow` is the active canonical repo.
Any other folder or repo is archive/reference only — never active development.

---

## 3. Tech stack

**App:** Python 3.13, Flask 3.1.1, pandas 2.3.1, geopandas 1.1.1, reportlab 4.2.2, shapely 2.1.1, pyproj 3.7.1
**Frontend:** Leaflet (map), Bootstrap 5 (UI)
**Quality:** pre-commit, Ruff, pytest, GitHub Actions CI
**Dev tools:** VS Code, Cursor Pro (.cursorrules), Claude Code (CLAUDE.md), GitHub Copilot, macOS Terminal/zsh, Git/GitHub
**Review tools:** ChatGPT, Gemini, Grok — use CLAUDE_REVIEW_BUNDLES/ zips
**Local AI:** Ollama — qwen2.5:14b-instruct (main), llama3.2 (fast)

---

## 4. Current confirmed state (verified 20 April 2026)

**Phase:** Working local MVP + rulepack architecture complete + SPEN_11kV live + 23 tests passing

**Confirmed working flow:**
upload CSV → save file → run QA → save outputs → view map → download PDF → browse jobs

**Confirmed working routes:**
- GET /  |  GET /upload  |  GET /jobs/  |  GET /health/full
- POST /api/presign  |  PUT /api/upload/<job_id>/<filename>
- POST /api/import/<job_id>  |  GET /api/jobs/  |  GET /api/jobs/<id>/status
- GET /map/view/<job_id>  |  GET /map/data/<job_id>  |  GET /pdf/qa/<job_id>

**QA engine — 7 check types:**
unique, required, range, allowed_values, regex, paired_required, dependent_allowed_values

**Rulepacks (in dno_rules.py):**
- DEFAULT: generic UK-wide BASE_RULES (fallback)
- SPEN_11kV: extends BASE_RULES with real ENA TS 43-8 values
  - Height 7–20m | Pole ID regex | Paired coord checks
  - SPEN network bounds (lat 54.5–60.9, lon -6.5 to -0.7)
  - Material/structure_type cross-field consistency

**Tests:** 23 passing (5 api_intake + 9 app_routes + 9 qa_engine)
**CI:** GitHub Actions runs pre-commit + pytest on every push to master

**Known weaknesses:**
1. Only one DNO rulepack (SPEN_11kV) — more DNOs are the next priority
2. No coordinate consistency cross-check yet (lat/lon vs easting/northing)
3. Input schema still narrow — one representative schema supported
4. No Playwright browser tests yet — backend tests only

---

## 5. Current next priority

1. Add coordinate consistency cross-check (lat/lon vs easting/northing)
2. Add SSEN_11kV rulepack (data available in SpanCore-CLEAN/rules/ — archive/reference only)
3. Add NIE, ENWL, NGED, UKPN rulepacks from same source
4. Fix Makefile stale port (APP?=http://127.0.0.1:5010 → 5001)
5. Wire api_rulepacks.py to real RULEPACKS data (currently returns stub)

**What is NOT the current priority:**
- Browser E2E testing (Playwright) — later
- Deployment/hosting — later
- UI redesign — later
- Database integration — not planned
- Broad feature expansion — never without proof-of-value

---

## 6. Tool roles

| Tool | Role | When to use |
|---|---|---|
| Claude app (Filesystem MCP) | Live dev sessions — reads/writes files directly on Mac | Every active dev session |
| Claude Code | Terminal-based repo work — reads CLAUDE.md | Terminal work, debugging |
| Cursor Pro | In-editor coding — reads .cursorrules | Active code editing |
| GitHub Copilot | Passive inline autocomplete | Always on in VS Code |
| ChatGPT | Strategic decisions only | Genuine decision points |
| Gemini | Structured challenger | Genuine decision points |
| Grok | Trade-off enforcer | Genuine decision points |
| Ollama | Offline/private drafting | Offline or sensitive content |

**Tool priority for implementation work:**
1. Claude app (Filesystem MCP)
2. Claude Code
3. Cursor Pro
4. Copilot (passive)
5. ChatGPT/Gemini/Grok (decision points only)
6. Ollama (offline only)

---

## 7. Hard rules — all tools must follow these

1. Read this file first — every session, every tool, no exceptions
2. Never use non-canonical repos or folders as current truth
3. Never broaden scope beyond the narrow MVP
4. Never add features not tied to the current task
5. Always read a file before editing it — never assume contents
6. Always run `pytest -v` after any code change — 23 tests must pass
7. Always `git add/commit/push` after confirmed passing tests
8. Always update this file and supporting control files when state changes materially
9. Never restore from `_quarantine/` blindly
10. Never let different tools work from different project states

---

## 8. Session start rule

**Every session, every tool:**
1. Read this file: `AI_CONTROL/00_MASTER_SOURCE_OF_TRUTH.md`
2. Read current task: `AI_CONTROL/03_CURRENT_TASK.md`
3. Read last handoff: `AI_CONTROL/04_SESSION_HANDOFF.md`
4. Then start work

**For implementation work also read:**
- `AI_CONTROL/02_CURRENT_STATE.md` — full technical state detail

**For strategic decisions also read:**
- `PROJECT_SYNTHESIS/03_DECISION_MEMO/FINAL_DECISION_MEMO.md`
- `PROJECT_SYNTHESIS/04_EXECUTION_ALIGNMENT/EXECUTION_ALIGNMENT_PLAN.md`

---

## 9. File map

### Active — update when state changes
- `AI_CONTROL/00_MASTER_SOURCE_OF_TRUTH.md` — THIS FILE — primary authority
- `AI_CONTROL/02_CURRENT_STATE.md` — full technical state detail
- `AI_CONTROL/03_CURRENT_TASK.md` — immediate task detail
- `AI_CONTROL/04_SESSION_HANDOFF.md` — last session handoff

### Tool bootstrap — update when roles or tech stack change
- `CLAUDE.md` — Claude Code session bootstrap
- `.cursorrules` — Cursor Pro session bootstrap

### Reference only — do not update routinely
- `AI_CONTROL/01_PROJECT_TRUTH.md` — project identity narrative
- `AI_CONTROL/05_AI_ROLE_RULES.md` — detailed role descriptions
- `AI_CONTROL/06_DEVELOPMENT_PROCESS.md` — process documentation
- `MASTER_PROJECT_READ_FIRST.md` — top-level pointer (kept for legacy)
- `PROJECT_SYNTHESIS/` — all strategic synthesis, decision memos, analyses

### Live code
- `app/` — Flask app factory, routes, templates, static
- `tests/` — pytest suite
- `run.py`, `requirements.txt`, `pyproject.toml` — entry point and config
