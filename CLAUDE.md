# CLAUDE.md

# Unitas-GridFlow — Claude Working File

## Project identity

You are working on **Unitas-GridFlow**, a narrow pre-CAD QA and compliance tool for UK electricity network survey-to-design handoffs.

The system currently:

- ingests survey CSV and raw controller survey data
- normalises input into a working schema
- applies rule-based QA validation
- generates structured issues
- visualises outputs on a Leaflet map
- produces PDF QA reports

Short identity:

**A survey-to-design validation system and pre-CAD QA gatekeeper for electrical infrastructure workflows.**

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

It is useful across the survey, planning, and design workflow because it improves the quality and trustworthiness of the digital handoff that downstream engineering decisions depend on.

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
- Tests must remain green
- CI is active
- Phase 1 is complete
- Phase 2A is complete
- Phase 2B is complete
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
- the next useful value may come from showing what the digital survey file does and does not contain for design purposes

The project has now already implemented:

- raw controller dump intake support
- Irish Grid handling
- completeness/capture summary generation
- initial controller-file QA refinement
- user-facing completeness visibility
- corrected Irish/NIE rulepack inference for relevant uploads

The current phase is now about proving usefulness, clarifying design readiness, and refining outputs from real evidence.

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
