# CLAUDE.md

# Unitas-GridFlow — Claude Working File

## Project identity

You are working on **Unitas-GridFlow**, a survey-to-design workflow intelligence tool for UK electricity network projects.

The system currently:

- ingests survey data (CSV, raw controller exports, Trimble dumps)
- interprets record roles (structural, context, anchor, existing/proposed)
- normalises input into a working schema
- applies rule-based QA validation
- identifies design risks and gaps in the survey handoff
- generates structured issues with design-context explanations
- visualises outputs on a Leaflet map with design-readiness signals
- produces PDF pre-design briefing reports

Short identity:

**A survey-to-design workflow intelligence tool that interprets, validates, and explains digital survey data for UK electricity network design handoffs.**

---

## Core principle

This project is **validation-led, not feature-led**.

Its purpose is to act as the trusted gate between survey and design — turning raw, inconsistent, incomplete survey data into something a designer can confidently assess and use.

Every step must answer:

> **Does this improve the reliability, clarity, and design-readiness of real survey data?**

---

## Critical context

This project is not software-first.

It comes from direct real-world experience of:

- survey → design handoff failures
- messy data intake
- designers doing hidden QA instead of design
- downstream office time being wasted on input repair instead of actual design

The project is not just for surveyors.

It is useful across the survey, planning, and design workflow — surveyors handing over better-evidenced data, designers receiving a clearer picture of the handoff, QA leads checking data quality before design release.

**This tool does not replace Trimble, PoleCAD, AutoCAD, or engineering designers. It is not yet a full DNO compliance engine. It is a pre-design intelligence layer — the trusted gate between survey and design.**

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
- `PROJECT_DEEP_CONTEXT.md`
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

1. `AI_CONTROL/00_PROJECT_CANONICAL.md`
2. `AI_CONTROL/02_CURRENT_TASK.md`
3. `AI_CONTROL/01_CURRENT_STATE.md` (only if needed)
4. `AI_CONTROL/04_SESSION_HANDOFF.md` (only if needed)
5. `AI_CONTROL/06_STRATEGIC_REVIEW_2026-04-22.md` (only if strategic direction is relevant)

Use:

- canonical = what the project is
- current task = what to do next
- current state = what is true right now
- strategic review = why the next phase is validation-led

---

## Session start behaviour

At the start of work:

1. Read:
   - `AI_CONTROL/00_PROJECT_CANONICAL.md`
   - `AI_CONTROL/02_CURRENT_TASK.md`

2. Then optionally:
   - `AI_CONTROL/01_CURRENT_STATE.md`
   - `AI_CONTROL/04_SESSION_HANDOFF.md`
   - `AI_CONTROL/06_STRATEGIC_REVIEW_2026-04-22.md`
   - `CHANGELOG.md`
   - `README.md`
   - `WORKFLOW_SYSTEM.md`

Do not read `_archive/` unless explicitly asked.

---

## Current state

- MVP works end-to-end
- Tests must remain green (121 passing)
- CI is active
- Phase 1 is complete
- Phase 2A is complete
- Phase 2B is complete
- Validation batches 2–15 complete (raw intake → completeness → design readiness → record roles → EX/PR detection → angle/stay evidence → designer summary layer)
- Batch 16 complete (project vision documentation aligned)
- Validation-led refinement is active

---

## Current strategic position (STRICT)

The project should continue, but the next phase must be validation-led.

The main unresolved question is:

> **Does the current tool provide meaningful value on real survey files for real users?**

That means the current focus is no longer broad rule expansion by default.

The focus is now:

- test the current tool against real survey files
- identify what works
- identify what breaks
- identify what users actually care about
- use that evidence to define the next development step

Do not assume more features are the right next step without validation evidence.

---

## Validation-phase position

The first real-job validation pack showed that:

- real survey inputs may arrive as raw controller exports rather than clean structured CSVs
- NIE jobs may require Irish Grid handling
- value comes from interpreting what the digital survey file contains for design purposes

The project has now implemented through Batches 2–15:

- raw controller dump intake support
- Irish Grid handling (TM65/ITM detection and WGS84 conversion)
- completeness/capture summary generation
- record-role classification (structural, context, anchor)
- design readiness verdict with per-category survey coverage
- EX/PR replacement-pair detection and narrative linking
- angle/stay evidence logic (proximity scan, cautious WARN)
- confidence-aware QA severity tiers (WARN vs FAIL calibration)
- asset_intent labels (Existing asset / Proposed support) in GeoJSON and UI
- designer summary layer: circuit summary, top design risks, replacement narratives
- PDF and map outputs now present a pre-design briefing, not a raw QA dump

The current phase is about validating whether this designer-facing output is genuinely useful on real files.

---

## Working style

- stay strictly narrow in scope
- make small, targeted changes
- do not redesign architecture
- do not expand scope
- always read before editing
- prioritise real-world usefulness over theoretical completeness
- prioritise validation evidence over abstract feature expansion
- when a real validation analysis file exists, use it as current evidence for next-step decisions

---

## Tooling / workflow role

Use the current workflow model in `WORKFLOW_SYSTEM.md`.

In practice:

- GitHub-connected repository = current code source of truth
- Claude Code / VS Code = live implementation, tests, commit, push
- Claude Desktop / project context = stable context, control layer, workflow, and validation evidence
- ChatGPT = project orchestration, review, prioritisation, and next-step planning
- Codex = optional secondary coding/review agent for bounded tasks

Do not assume that uploaded project snapshots are always fresher than the connected repo.

Prefer:

- control files for direction
- repo truth for implementation
- real validation evidence for product decisions

---

## Engineering rules

After any approved code change:

- run `pytest -v`
- run `pre-commit run --all-files`
- commit clearly
- push to `master`

---

## Output rule

When editing or improving files:

- provide the full final version of every changed file
- provide exact terminal commands separately
- avoid partial patches unless explicitly asked

---

## Key files

- `app/controller_intake.py`
- `app/routes/api_intake.py`
- `app/qa_engine.py`
- `app/dno_rules.py`
- `tests/`

Strategic / control files:

- `AI_CONTROL/00_PROJECT_CANONICAL.md`
- `AI_CONTROL/01_CURRENT_STATE.md`
- `AI_CONTROL/02_CURRENT_TASK.md`
- `AI_CONTROL/03_WORKING_RULES.md`
- `AI_CONTROL/04_SESSION_HANDOFF.md`
- `AI_CONTROL/06_STRATEGIC_REVIEW_2026-04-22.md`

---

## Final rule

Operate strictly within the active project.

Do not rely on archive or assumptions.

Do not replace real-world validation with abstract feature work.
