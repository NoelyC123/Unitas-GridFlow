# CLAUDE.md

# Unitas-GridFlow — Claude Code Working File

## Project identity

You are working on **Unitas-GridFlow**, a survey-to-design workflow intelligence and automation tool for UK electricity distribution overhead line work.

It is a **pre-CAD QA gatekeeper and workflow automation layer** that sits between field survey output and office-based design work.

The system currently:

- parses raw Trimble GNSS controller dump CSVs
- detects coordinate reference systems (Irish Grid TM65, ITM, OSGB27700)
- converts coordinates for map display
- classifies records by role (structural, context, anchor)
- detects EX/PR replacement pairs and produces design narratives
- applies confidence-aware QA checks (PASS/WARN/FAIL severity tiers)
- generates 7 scoped design evidence gates
- renders an interactive Leaflet map with design-readiness signals
- produces a PDF pre-design briefing report
- infers the correct DNO rulepack from geography
- validated on 4 real survey files from real NIE and SPEN jobs

Short identity:

**A survey-to-design workflow intelligence tool that interprets, validates, and explains digital survey data for UK electricity network design handoffs.**

---

## The full vision (6 stages)

### Stage 1 — Post-survey QA gate ✅ COMPLETE
Raw controller dump → parse → report completeness and design risks → designer knows what they have before opening PoleCAD.

### Stage 2 — Design-ready handoff / Design Chain ✅ COMPLETE
Tool takes raw controller dump and produces structured, sequenced, designer-readable handoff outputs directly. The old manual D2D spreadsheet is the workaround being eliminated, not the product model. Current outputs are a Design Chain export and secondary Raw Working Audit; final PoleCAD import format remains out of scope until verified.

### Stage 3 — Live intake platform
Surveyor syncs controller data daily (or continuously). Tool immediately validates and produces completeness reports. Designer sees the job building in real-time. Feedback loop closes while surveyor is still on site.

### Stage 4 — Structured field capture
Surveyor uses a tablet alongside Trimble. Structured digital entry for pole type, stay type, clearances, crossings, photos geotagged to point records. 80% of what currently goes on paper moves into structured digital capture.

### Stage 5 — Designer workspace
Complete job presented to designer: route on map, every pole with full attributes, replacement pairs identified, stay flags, clearance issues, photos linked. Designer reviews and exports directly to PoleCAD.

### Stage 6 — DNO submission layer
Submission-ready packs: route maps, clearance schedules, compliance reports, photo evidence, QA audit trails formatted to DNO requirements.

---

## Core principle

This project is **validation-led, not feature-led**.

Every step must answer:

> **Does this improve the reliability, clarity, and design-readiness of real survey data?**

---

## Critical context

This project is not software-first.

It comes from direct real-world experience of both the survey job on site and the D2D/PoleCAD design job in the office. The project owner knows from direct experience that the entire process can be made dramatically better.

**This tool does not replace Trimble, PoleCAD, AutoCAD, or engineering designers. It is a pre-design intelligence layer and workflow automation tool, not a substitute for any of these.**

---

## Tool roles (STRICT)

### Claude Desktop — Project Orchestrator (use selectively)
- defines what gets built, why, and in what order for major stage decisions
- reviews validation results when the decision is high-impact or ambiguous
- prevents scope drift
- should not be used for every routine documentation update or small closure step

### Claude Code (VS Code) — Primary Builder (YOU)
- reads repo, writes code, runs tests, commits, pushes
- executes tasks as defined by the orchestrator
- makes minimal, targeted changes
- keeps tests passing
- should be used mainly for code changes, complex repo-wide edits, and high-risk implementation work
- should not be used for routine admin-only updates when Cursor can safely make the small documentation change

### ChatGPT — Available for second opinions and commercial thinking only

---

## Canonical locations

- Local: `/Users/noelcollins/Unitas-GridFlow/`
- GitHub: `NoelyC123/Unitas-GridFlow`
- Branch: `master`

---

## Repository structure (CRITICAL)

### ACTIVE PROJECT (use only this)

- `AI_CONTROL/`
- `app/`
- `tests/`
- `sample_data/`
- `README.md`
- `CHANGELOG.md`
- `CLAUDE.md`
- `WORKFLOW_SYSTEM.md`

### ARCHIVE (DO NOT USE)

- `_archive/`

### LOCAL / TOOL FILES (ignore as project truth)

- `.env`
- `.vscode`
- `.claude`
- `.venv312`
- caches

---

## Control layer (source of truth for project direction)

Read in this order when needed:

1. `AI_CONTROL/00_PROJECT_CANONICAL.md` — what the project is and the full 6-stage vision
2. `AI_CONTROL/02_CURRENT_TASK.md` — what to do next
3. `AI_CONTROL/01_CURRENT_STATE.md` — what is true right now
4. `AI_CONTROL/04_SESSION_HANDOFF.md` — continuity between sessions
5. `AI_CONTROL/09_PROJECT_ORIGIN_AND_FIELD_NOTES.md` — domain context; read when making QA logic or output language decisions
6. `AI_CONTROL/08_OHL_SURVEY_OPERATIONAL_STANDARD.md` — survey domain standard reference

Do not read `_archive/` unless explicitly asked.

Do not rely on `AI_CONTROL/06_STRATEGIC_REVIEW_2026-04-22.md` or `AI_CONTROL/07_REAL_WORLD_SURVEY_WORKFLOW.md` — superseded by 08 and 09.

---

## Session start behaviour

At the start of work:

1. Read:
   - `AI_CONTROL/00_PROJECT_CANONICAL.md`
   - `AI_CONTROL/02_CURRENT_TASK.md`

2. Then optionally:
   - `AI_CONTROL/01_CURRENT_STATE.md`
   - `AI_CONTROL/04_SESSION_HANDOFF.md`
   - `CHANGELOG.md`

Do not read `_archive/` unless explicitly asked.

---

## Current state

- Stage 1 complete
- Stage 3 is complete; current work is practitioner-review remediation
- 287 tests passing
- CI active
- 4 real survey files validated
- Practitioner review remediation is focused on terminology, Design Chain framing, EX/PR proximity QA, map span rendering, and PDF issue presentation

---

## Working style

- stay strictly narrow in scope — work on the current stage only
- make small, targeted changes
- do not redesign architecture
- always read before editing
- prioritise real-world usefulness over theoretical completeness
- prioritise validation evidence over abstract feature expansion

---

## Engineering rules

After any approved code change:

1. `pytest -v` — all tests must pass
2. `pre-commit run --all-files`
3. commit clearly
4. push to `master`

Documentation-only changes should be proportionate:

- Major stage closure: update only the minimum control docs needed to keep the project state clear.
- Small polish/bugfix: update `CHANGELOG.md` only if useful.
- Do not create a new closure/review/planning document for every small task.
- Avoid spending Claude Desktop or Claude Code usage on routine admin if Cursor can safely do it.

---

## Source of truth hierarchy

1. Real survey files (highest)
2. `AI_CONTROL/` files
3. Repo code and tests
4. Documentation
5. AI outputs (lowest)

---

## Key files

- `app/controller_intake.py`
- `app/qa_engine.py`
- `app/issue_model.py`
- `app/routes/api_intake.py`
- `app/dno_rules.py`
- `tests/`

Strategic / control files:

- `AI_CONTROL/00_PROJECT_CANONICAL.md`
- `AI_CONTROL/01_CURRENT_STATE.md`
- `AI_CONTROL/02_CURRENT_TASK.md`
- `AI_CONTROL/03_WORKING_RULES.md`
- `AI_CONTROL/04_SESSION_HANDOFF.md`
- `AI_CONTROL/08_OHL_SURVEY_OPERATIONAL_STANDARD.md`
- `AI_CONTROL/09_PROJECT_ORIGIN_AND_FIELD_NOTES.md`

---

## Final rule

Operate strictly within the active stage.

Do not rely on archive or assumptions.

Do not replace real-world validation with abstract feature work.

Do not jump ahead to later stages without the orchestrator defining the next task.
