# Development Process / AI Workflow / Control System

## Purpose

This file defines the operating system for building, reviewing, controlling, and evolving the **Unitas GridFlow** project.

It exists to ensure that:

- all development work follows one disciplined process
- all AI reviews are grounded in the same canonical truth
- implementation work and strategic review stay aligned
- future sessions do not drift into outdated assumptions
- the project is run in a professional, efficient, repeatable, and auditable way

This file is part of the **AI control layer** and should be treated as a live operational guide.

---

## 1. Canonical project identity

### Current active project name
**Unitas GridFlow**

### Canonical active repo
**GitHub repo:** `NoelyC123/Unitas-GridFlow`

### Canonical active local folder
`/Users/noelcollins/Unitas-GridFlow`

### Rule
This is the **only active canonical repo** for this project.

Older EW / SpanCore / design-tool repos are archived and are **not** active development repos.

If a repo is not `Unitas-GridFlow`, it is not the active project.

---

## 2. Core project aim

Unitas GridFlow is currently being developed as:

**a narrow pre-CAD QA / compliance / submission-readiness tool for electricity survey-to-design handoffs**

Short version:

**a DNO survey compliance gatekeeper**

This remains the strongest current product identity and the baseline for all development and review work.

---

## 3. Current practical MVP flow

The current local MVP flow is:

**upload CSV -> save file -> run QA -> save outputs -> view map -> download PDF -> browse jobs**

This is the current working baseline workflow that all development decisions must respect.

---

## 4. Core operating principle

This project must be run through three aligned layers:

### Layer 1 — Canonical truth layer
This is the control layer in `AI_CONTROL/`.

It defines:
- what the project is
- what state it is currently in
- what the immediate task is
- what changed in the latest session
- how AIs should behave on the project

### Layer 2 — Synthesis / reasoning layer
This is the strategic and analytical layer in `PROJECT_SYNTHESIS/`.

It contains:
- raw AI analyses
- comparison and synthesis work
- decision files
- execution alignment documents
- support notes and saved prompts/reviews

### Layer 3 — Live implementation layer
This is the running app and codebase.

It includes:
- `app/`
- `run.py`
- `requirements.txt`
- `pyproject.toml`
- `sample_data/`
- `uploads/`
- `temp_gis/`

All future work must keep these three layers aligned.

---

## 5. Confirmed real tool stack

## 5.1 Core development tools

### VS Code
Used for:
- editing project files
- reviewing repo structure
- managing markdown control/synthesis files
- editing Python, HTML, JS, CSS, YAML, and data files

### Cursor
Used for:
- AI-assisted editing inside the repo
- multi-file refactoring help
- agentic coding assistance where useful

### Claude Code
Used for:
- repo-aware terminal/codebase reasoning
- structured code review in the project context
- targeted implementation support when repo-wide awareness matters

### macOS Terminal / zsh
Used for:
- running Flask
- managing git/GitHub
- running tests and quality tools
- creating bundles
- verifying outputs
- environment control

### Python 3.13 + `.venv312`
Canonical runtime environment for the project.

### Git + GitHub
Used for:
- source control
- canonical remote repository
- push/pull history
- rollback
- CI integration

---

## 5.2 Confirmed app stack

### Flask
Used for the local app and route structure.

### pandas
Used for CSV loading, normalization, QA input handling, and issue generation support.

### ReportLab
Used for QA PDF generation.

### Leaflet
Used for map viewing.

### Bootstrap
Used for UI structure and styling.

---

## 5.3 Confirmed quality / testing stack

### pre-commit
Installed and active.

Used for:
- trailing whitespace cleanup
- end-of-file fixes
- YAML checks
- JSON checks
- large-file checks
- auto-running Ruff hooks before commits

### Ruff
Installed and active.

Used for:
- Python linting
- formatting
- keeping code style consistent

### pytest
Installed and active.

Used for:
- backend unit tests
- normalization tests
- feature collection tests
- JSON/issue handling tests

### GitHub Actions
Installed and active.

Current CI runs on push/pull request to `master` and executes:
- dependency install
- `pre-commit run --all-files`
- `pytest -q`

### Playwright
**Not yet active.**

Planned for later once UI flows are stable enough for end-to-end browser testing.

---

## 6. Confirmed AI roles

See `AI_CONTROL/05_AI_ROLE_RULES.md` for full role descriptions.
See `AI_CONTROL/00_MASTER_SOURCE_OF_TRUTH.md` Section 6 for the current tool priority summary.

The current tool priority is:
1. Claude app (Filesystem MCP) — live development sessions, reads/writes files directly
2. Claude Code — terminal-based repo work
3. Cursor Pro — in-editor coding
4. GitHub Copilot — passive autocomplete
5. ChatGPT / Gemini / Grok — strategic decisions only, at genuine decision points
6. Ollama — offline/private drafting only

---

## 7. Canonical project file map

## 7.1 Top-level orientation file
- `MASTER_PROJECT_READ_FIRST.md`

## 7.2 AI control layer
- `AI_CONTROL/00_MASTER_SOURCE_OF_TRUTH.md` — PRIMARY AUTHORITY (read first)
- `AI_CONTROL/00_READ_THIS_FIRST.md`
- `AI_CONTROL/01_PROJECT_TRUTH.md`
- `AI_CONTROL/02_CURRENT_STATE.md`
- `AI_CONTROL/03_CURRENT_TASK.md`
- `AI_CONTROL/04_SESSION_HANDOFF.md`
- `AI_CONTROL/05_AI_ROLE_RULES.md`
- `AI_CONTROL/06_DEVELOPMENT_PROCESS.md`

## 7.3 Synthesis layer
- `PROJECT_SYNTHESIS/00_RAW_AI_RESPONSES/`
- `PROJECT_SYNTHESIS/01_COMPARISON/`
- `PROJECT_SYNTHESIS/02_FINAL_SYNTHESIS/`
- `PROJECT_SYNTHESIS/03_DECISION_MEMO/`
- `PROJECT_SYNTHESIS/04_EXECUTION_ALIGNMENT/`
- `PROJECT_SYNTHESIS/05_SUPPORT_NOTES/`
- `PROJECT_SYNTHESIS/SPANCORE_SYNTHESIS_READ_FIRST.md`

## 7.4 Live implementation layer
- `app/`
- `run.py`
- `requirements.txt`
- `pyproject.toml`
- `README.md`
- `RUNBOOK.md`
- `sample_data/`
- `uploads/`
- `temp_gis/`

## 7.5 GitHub administration / repo records
- `GITHUB_ADMIN/`

---

## 8. How AI reviews must be done

AI reviews must always be grounded in the **same canonical baseline**.

That means any serious AI review should be grounded in:

1. the current `AI_CONTROL/` files
2. the current `PROJECT_SYNTHESIS/` files
3. the current live app bundle or relevant live code files

### Rule
No AI should be asked to review the project from partial context if the review is important enough to influence direction.

### Why
If an AI only sees the app code, it may reason from stale assumptions.

If an AI only sees the synthesis files, it may ignore implementation truth.

If an AI only sees the control files, it may miss technical reality.

So meaningful reviews must include all three layers together.

---

## 9. Review bundle method

Whenever an external AI review is needed, prepare review bundles from the current canonical state.

### Standard review bundle set

#### Bundle 1 — AI control
Contains:
- all files in `AI_CONTROL/`

#### Bundle 2 — Project synthesis
Contains:
- all files in `PROJECT_SYNTHESIS/`

#### Bundle 3 — Live app review
Contains:
- current live app files
- current key root project files
- current templates/static files
- current active route files

### Bundle naming convention
Use numbered review bundles, for example:
- `01_AI_CONTROL.zip`
- `02_PROJECT_SYNTHESIS.zip`
- `03_LIVE_APP_REVIEW.zip`

### Important rule
Do not build ad hoc bundles with missing layers for major review questions.

---

## 10. Where prompts and AI reviews are saved

All prompt/review support documents should be saved in:

**`PROJECT_SYNTHESIS/05_SUPPORT_NOTES/`**

This includes:
- prompts sent to Claude / Gemini / Grok
- saved AI replies
- checkpoint review notes
- follow-up implementation-spec notes

### Naming convention
Use clear descriptive names, for example:
- `CLAUDE_NEXT_PRIORITY_PROMPT.md`
- `CLAUDE_NEXT_PRIORITY_REVIEW.md`
- `CLAUDE_INPUT_SCHEMA_FOLLOWUP.md`

Follow the same structure for other AIs when used.

---

## 11. Development cycle workflow

Every development cycle should follow this sequence.

### Step 1 — Build
Make the smallest necessary code or file change.

### Step 2 — Test locally
Run the relevant local checks.

Examples:
- Flask run test
- route/output check
- `pre-commit run --all-files`
- `pytest -q`

### Step 3 — Evaluate whether current truth changed
Ask:

**Did this change materially alter the current project state, workflow, or next priority?**

If no:
- continue to the next implementation step

If yes:
- update the relevant control files before doing anything more strategic

### Step 4 — Commit and push
Use git properly:
- stage changes
- commit with a clear message
- push to `origin/master`

### Step 5 — Let CI validate
GitHub Actions should then run:
- `pre-commit`
- `pytest`

### Step 6 — Checkpoint if needed
At meaningful milestones, stop and confirm:
- what now works
- what remains weak
- what is no longer the immediate priority
- what the next decision actually is

### Step 7 — External AI review only if needed
Bring in Claude / Gemini / Grok only when there is a real decision to make.

### Step 8 — Save the review
Save prompt and response in:
- `PROJECT_SYNTHESIS/05_SUPPORT_NOTES/`

### Step 9 — Convert conclusion into exact work
Use the review result to define:
- specific files to edit
- exact sequence of work
- exact tests to run

---

## 12. Checkpoint method

A checkpoint should happen whenever one of these becomes true:

- a previously broken flow now works
- the MVP changes state materially
- a current priority is completed
- the next development decision becomes ambiguous
- another AI is about to be asked to review the project

At a checkpoint, answer:

1. What now works?
2. What is still weak?
3. What is the immediate next decision?
4. Has the current task changed?
5. Do the AI control files still reflect the live truth?

If not, update them first.

---

## 13. When control files must be updated

Update the control files whenever:

- the working MVP materially changes
- a blocker is removed
- a priority is completed
- the immediate task changes
- a session ends after meaningful work
- the project moves into a new development phase

### Minimum file update rule
If project truth changed materially, review these first:
- `AI_CONTROL/02_CURRENT_STATE.md`
- `AI_CONTROL/03_CURRENT_TASK.md`
- `AI_CONTROL/04_SESSION_HANDOFF.md`

---

## 14. Current non-blocking technical debt log

These items are known and should be kept in view for later work:

- historical old test jobs still remain in `uploads/jobs/` (stale paths fixed 20 Apr 2026)
- `issues.csv` payloads are still verbose
- Only one DNO rulepack exists (SPEN_11kV) — more DNOs are the active next priority
- No coordinate consistency cross-check yet (lat/lon vs easting/northing)
- No automated browser tests yet (Playwright not yet active)
- `api_rulepacks.py` still returns stub data — needs wiring to real RULEPACKS dict
- Makefile has stale port (5010 instead of 5001)
- GitHub Actions shows a non-blocking Node.js deprecation warning for upstream actions

These are not blockers unless they become tied to the active next priority.

---

## 15. Efficiency / professionalism rules

To keep the process professional and productive:

- always work from the current canonical truth
- do not ask broad AI questions without current bundles
- do not mix outdated assumptions with current implementation state
- prefer one clear next step over broad roadmap drift
- save prompts and reviews properly
- only use multiple AIs at genuine decision points
- avoid duplicate thinking and repeated re-analysis
- keep product scope narrow unless the decision memo changes
- implementation truth always overrides stale speculation

---

## 16. What not to do

Do not:
- let different AIs work from different project states
- ask for broad startup brainstorming during active MVP build work
- broaden scope because a tool suggests interesting possibilities
- skip control-layer updates after meaningful state changes
- treat synthesis docs as live truth if the app has moved on
- treat old archived repos as active project context
- treat old uploaded files or old assumptions as current without checking

---

## 17. Current next-step logic

As of the current state (verified 20 April 2026):

- the canonical repo, naming, and development stack are fully established
- pre-commit, Ruff, pytest, and GitHub Actions are active and passing
- the complete rename to Unitas GridFlow is done across all files
- the rulepack architecture is in place with SPEN_11kV live
- the immediate next priorities are:
  1. coordinate consistency cross-check (lat/lon vs easting/northing)
  2. SSEN_11kV rulepack
  3. remaining DNO rulepacks (NIE, ENWL, NGED, UKPN)
  4. wire api_rulepacks.py to real RULEPACKS data
  5. fix Makefile port (5010 → 5001)
- Playwright browser tests should come later, once UI is stable

---

## 18. Session start workflow

At the start of any future session, the working order should be:

1. read `AI_CONTROL/00_MASTER_SOURCE_OF_TRUTH.md` — PRIMARY AUTHORITY
2. read `AI_CONTROL/03_CURRENT_TASK.md`
3. read `AI_CONTROL/04_SESSION_HANDOFF.md`
4. only then inspect the implementation files relevant to the current task

This is the required session bootstrap.

---

## 19. Final operating rule

The project should be run like this:

**current truth -> live implementation -> local checks -> commit/push -> CI -> checkpoint -> controlled review -> exact next step**

That sequence governs all future work.
