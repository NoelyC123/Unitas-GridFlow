# Unitas GridFlow — Project Operating Model

This document explains how the project is organised, who does what, and how
sessions run. It is written for humans and for any AI tool starting fresh on
this project.

It is a companion to `AI_CONTROL/00_MASTER_SOURCE_OF_TRUTH.md`, not a
replacement for it. If this document and the master truth file disagree on a
fact, the master truth file wins.

---

## 1. What this project is

**Unitas GridFlow** is a narrow pre-CAD QA and compliance tool for UK
electricity network survey-to-design handoffs.

Short version: a DNO survey compliance gatekeeper.

It accepts survey CSV uploads, runs DNO-specific QA checks, renders results on
a map, and produces PDF QA reports. It is a local Flask/Python app. It is not
a SaaS, not a CAD replacement, and not an AI-first product.

See `AI_CONTROL/00_MASTER_SOURCE_OF_TRUTH.md` §1 for the full identity
statement.

---

## 2. The three layers

All work on this project touches three aligned layers:

### Layer 1 — Control layer (`AI_CONTROL/`)
Defines what the project is, what state it is in, what the current task is,
and how work is done. This is the operational truth. Every session starts here.

Files:
- `00_MASTER_SOURCE_OF_TRUTH.md` — primary authority. Read this first.
- `02_CURRENT_STATE.md` — deeper technical state (routes, architecture, debt).
- `03_CURRENT_TASK.md` — immediate task with work sequence.
- `04_SESSION_HANDOFF.md` — what happened in the last session.
- `06_DEVELOPMENT_PROCESS.md` — how the development cycle works.

### Layer 2 — Strategic layer (`PROJECT_SYNTHESIS/`)
Decision memos, execution alignment, saved AI reviews. Reference only — not
operational. Does not override the control layer.

### Layer 3 — Implementation layer
The running app and tests:
- `app/` — Flask app, routes, QA engine, rulepacks, templates, static assets.
- `tests/` — pytest test suite.
- `run.py`, `requirements.txt`, `pyproject.toml` — entry point and config.

All three layers must stay aligned. When code changes, the control layer
updates. When the control layer changes, it reflects the current code.

---

## 3. Who does what

### You (Noel — CEO / final decision-maker)

**Own:**
- Project direction — what the product becomes, which users to target.
- Sequencing — which priority gets worked on next.
- Validation sign-off — you run `pytest -v` locally and confirm green.
- Go/pause/stop decisions — per `PROJECT_SYNTHESIS/03_DECISION_MEMO/`.
- Deciding when to bring in external AI review.

**Do not do:**
- Write code or edit control files directly. Delegate entirely to Claude app.
- Accept AI suggestions for DNO-specific technical values without verifying
  against primary sources (ENA documents, DNO technical standards).

### Claude app (claude.ai — this setup, with Filesystem MCP)

**Role: primary implementation tool and control-layer custodian.**

This is the default tool for all active development sessions. It has direct
read/write access to the Mac filesystem, so nothing needs to be copy-pasted.

**Own:**
- Implementing code changes directly to disk.
- Reading files before editing them (never assumes contents).
- Running verification after changes (reminds you to run `pytest -v`).
- Updating the control layer at the end of every session.
- Keeping master truth in sync with the actual code state.

**Rules:**
- Read `00_MASTER_SOURCE_OF_TRUTH.md` fresh from disk at session start.
- Never close a session without updating `04_SESSION_HANDOFF.md` and
  appending to `CHANGELOG.md`.
- Never ask the user to copy/paste code or upload files.
- One editing tool per session — if Claude app is active, Cursor is not also
  editing files.

### Claude Code

**Role: terminal-based repo reasoning only.**
Reads `CLAUDE.md` at session start.

Use when you are already at the command line and want repo-aware reasoning
without opening a browser tab. Good for tracing routes and imports, debugging
a failing test in the terminal, or understanding why a command is behaving
unexpectedly.

Do NOT use for writing new features or updating control files. That is Claude
app's job. If you find yourself editing files in Claude Code, switch to Claude
app.

### Cursor Pro

**Role: in-editor AI coding.**
Reads `.cursorrules` when the project is opened in VS Code/Cursor.

Use for inline AI assistance while actively writing in the editor —
autocomplete on new functions, multi-file refactoring suggestions.

Do NOT use as the primary session tool when Claude app is already handling the
session. One editing tool per session.

### GitHub Copilot

**Role: passive inline autocomplete only.**

Always on. Useful for boilerplate and repetitive patterns.

**Critical rule:** Never accept Copilot suggestions for DNO-specific values
(network bounds, ENA height ranges, rulepack logic) without verifying against
primary sources. Copilot will confidently fabricate technically plausible but
wrong values. This is a real risk for this project.

### ChatGPT

**Role: strategic review at genuine decision forks.**

Use when you face a real architectural or prioritisation decision that is not
answered by the existing priority list — for example, whether to add polygon
checks before or after user validation, or whether to wire the rulepacks API
before completing all DNO rulepacks.

Do NOT use for day-to-day implementation or questions Claude app can answer
with file access.

When used formally: prepare the three review bundles first (see §6 below),
ask the specific question, save the prompt and response in
`PROJECT_SYNTHESIS/05_SUPPORT_NOTES/`.

### Second-opinion AI (Gemini — default; Grok if you want a different angle)

**Role: challenger at genuine decision forks.**

Same constraint as ChatGPT — decision points only, with bundles. One per real
decision. Do not use both Gemini and Grok for the same question.

### Ollama (local)

**Role: offline/private drafting.**
Optional. Use only when cloud tools are not appropriate (offline, private
content that must not leave the machine). Do not use for DNO-specific values
or rulepack logic — it has no file access and no current project state.

### GitHub Actions

**Role: mechanical quality gate.**

Runs `pre-commit run --all-files` + `pytest -q` on every push to `master`. A
failed CI run is a hard stop — do not move to the next task until it passes.

Do not treat a green CI run as a substitute for running `pytest -v` locally
before committing.

### pytest / Ruff / pre-commit

**Role: local quality enforcement.**

Run these before every commit:
- `pytest -v` — all tests must pass.
- `pre-commit run --all-files` — formatting, whitespace, YAML/JSON checks.

`pytest-cov` is also available: `pytest --cov=app` for a coverage report.

---

## 4. Tool priority summary

For any given session, the default tool choice follows this order:

| Priority | Tool | When |
|---|---|---|
| 1 | Claude app | All active development sessions. Default. |
| 2 | Claude Code | Terminal workflow only. |
| 3 | Cursor Pro | In-editor, when actively writing in VS Code. |
| 4 | Copilot | Passive autocomplete, always on. |
| 5 | ChatGPT | Strategic decision forks only. |
| 6 | Gemini / Grok | Second opinion at decision forks. One only. |
| 7 | Ollama | Offline/private only. Optional. |

**One editing tool per session.** Do not switch mid-task.

---

## 5. How a session runs

### Start (5 minutes maximum)

1. Open Claude app in the Unitas-GridFlow project.
2. Claude app reads `00_MASTER_SOURCE_OF_TRUTH.md`, `03_CURRENT_TASK.md`,
   and `04_SESSION_HANDOFF.md` from disk.
3. Claude app states: verified live truth, what the real current task is, any
   drift between code and docs.
4. You confirm or adjust the task. Start work.

### During the session

- Claude app makes the smallest necessary change.
- You run `pytest -v` locally and confirm green.
- Repeat per change. Do not batch up multiple unverified changes.

### Deciding the next task

- Master truth §5 is the priority list. Claude app reads it and proposes the
  next item.
- You confirm or override. Your call.
- If genuinely unclear, that is when you optionally bring in ChatGPT — not
  before.

### End of session (non-negotiable)

Before the session closes:

1. Claude app updates `AI_CONTROL/00_MASTER_SOURCE_OF_TRUTH.md` §4 and §5 if
   state changed.
2. Claude app rewrites `AI_CONTROL/03_CURRENT_TASK.md` if the priority
   changed.
3. Claude app rewrites `AI_CONTROL/04_SESSION_HANDOFF.md` to record what
   happened.
4. Claude app appends a dated entry to `CHANGELOG.md`.
5. `git add -A && git commit -m "chore: update control files post-[feature]"
   && git push origin master`.
6. CI runs. Confirm green.

**A session without these steps is unfinished, not complete.**

---

## 6. When to bring in external AI review

External AI review (ChatGPT, Gemini, Grok) is for genuine forks — situations
where the priority list does not answer the question and a real architectural
or sequencing decision must be made.

When you reach that point:

1. Prepare three zip bundles from the current canonical state:
   - `01_AI_CONTROL.zip` — everything in `AI_CONTROL/` + `CHANGELOG.md`.
   - `02_PROJECT_SYNTHESIS.zip` — everything in `PROJECT_SYNTHESIS/`.
   - `03_LIVE_APP_REVIEW.zip` — `app/`, `tests/`, key root files.
2. Ask the specific question. Do not describe the project from memory.
3. Save the prompt and response in `PROJECT_SYNTHESIS/05_SUPPORT_NOTES/`
   using the naming convention `<AI>_<TOPIC>_<PROMPT_or_REVIEW>.md`.

Do not build ad hoc partial bundles for major questions.

---

## 7. How to prevent drift

The main drift risk is a session ending with code committed but control files
not updated. Everything else follows from that.

**The seven rules that prevent drift:**

1. **Never close a session without the four-file update.**
   Master truth, current task (if changed), session handoff, changelog.
   This is the single most important rule.

2. **Master truth §4 and §5 are the only place counts and priorities live.**
   No other file hard-codes test counts, rulepack counts, or priority lists.
   If another file contains these, delete them and point to master truth.

3. **One editing tool per session.**
   If Claude app is editing files, Cursor is not. Mixing tools mid-session
   creates conflicting versions.

4. **Every session starts with a fresh disk read.**
   Not from memory. Not from a previous conversation. Not from a bundle
   that might be stale. From disk, right now.

5. **Non-canonical repos are non-canonical.**
   Only `NoelyC123/Unitas-GridFlow` is active. Any reference to SpanCore,
   EW Design Tool, or older naming as current authority means the session
   is starting from wrong context. Stop it.

6. **External AI reviews use current bundles, not memory.**
   Describing the project from memory to ChatGPT or Gemini creates a stale
   second-opinion problem. Prepare bundles.

7. **Copilot suggestions in `dno_rules.py` are drafts, not facts.**
   Always verify DNO-specific values against primary sources before
   accepting them.

---

## 8. Current forward plan

The project is currently in:

**Working MVP + three DNO rulepacks live + rulepack architecture proven.**

### Immediate next steps (in order)

1. Add `ENWL_11kV` rulepack (Electricity North West — NW England).
2. Add `NGED_11kV` rulepack (National Grid Electricity Distribution —
   Midlands, SW England, S Wales).
3. Add `UKPN_11kV` rulepack (UK Power Networks — London, SE, East Anglia).
4. Wire `app/routes/api_rulepacks.py` to the real `RULEPACKS` dict.
5. Fix `Makefile` stale port (5010 → 5001).

### After DNO coverage is complete

Per `PROJECT_SYNTHESIS/04_EXECUTION_ALIGNMENT/EXECUTION_ALIGNMENT_PLAN.md`:

- Identify one real user / design team / buyer champion.
- Run one real validation conversation or demo.
- Write one proof-of-value note.

No major new features before proof-of-value. No deployment work. No UI
redesign. Strict scope discipline.

### What is deliberately not being built now

- Browser E2E tests (Playwright) — later, once UI is stable.
- Deployment / hosting — later.
- Database integration — not planned.
- Broad new features — not until proof-of-value is demonstrated.

---

## 9. Canonical boundary

Only one repo and one folder are active:

- **Local:** `/Users/noelcollins/Unitas-GridFlow`
- **GitHub:** `https://github.com/NoelyC123/Unitas-GridFlow`

Everything else (SpanCore, EW Design Tool, any other folder or repo) is
archive/reference only. If a session accidentally references these as current
authority, stop and restart from the master truth file.
