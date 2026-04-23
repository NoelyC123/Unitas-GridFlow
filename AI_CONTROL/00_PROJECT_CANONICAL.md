# Project Canonical

## What this project is

**Unitas GridFlow** is a narrow pre-CAD QA and compliance tool for UK electricity network survey-to-design handoffs.

**Identity:** A survey-to-design QA gatekeeper for structured pre-CAD validation.

**Core principle:** Act as the trusted gate between survey and design — improving the reliability, clarity, and design-readiness of real survey data before office work begins.

Every step must answer: *"Does this improve the reliability, clarity, and design-readiness of real survey data?"*

---

## Why this project exists

This project comes from repeated real-world friction in the handoff between field survey and office design for UK electricity network work.

The idea did not begin software-first. It came from direct exposure to:

- how survey data is captured in the field
- how it is transferred to office teams
- how it is interpreted and converted into design and CAD outputs
- how hidden QA and clarification work often gets pushed downstream into design time

The key insight is:

**The biggest inefficiency often sits in the survey-to-design handoff, not in the engineering design itself.**

Unitas GridFlow exists to act as a structured gate between survey and design by:

- validating incoming survey data
- checking for missing or inconsistent information
- applying practical workflow and DNO-style rules
- flagging issues early
- producing cleaner, design-ready outputs before office time is wasted

---

## Core function

The system currently:

- ingests survey CSV data
- normalises it into a working schema
- applies rule-based QA validation
- generates structured issues
- visualises outputs on a Leaflet map
- produces PDF QA reports

Important qualification:

The current system is a **working MVP**, not a fully mature DNO-grade compliance engine.

It is best understood as:

- a narrow pre-CAD validation tool
- a workflow QA layer
- a proof-of-value system that still needs real-world validation on actual survey files

---

## Canonical locations

### GitHub

- Repo: `https://github.com/NoelyC123/Unitas-GridFlow`
- Branch: `master`

### Local

- Folder: `/Users/noelcollins/Unitas-GridFlow`
- Environment: `.venv312`

**Rule:** This is the only active repository. Older SpanCore / EW Design Tool repos are archived.

---

## Project structure (authoritative)

The repository is intentionally split into three layers:

### 1. ACTIVE PROJECT (used for development)

- `AI_CONTROL/`
- `app/`
- `tests/`
- `sample_data/`
- `README.md`
- `CHANGELOG.md`
- `CLAUDE.md`
- `WORKFLOW_SYSTEM.md`
- `PROJECT_DEEP_CONTEXT.md`
- root config/runtime files

This is the only surface used for active development.

---

### 2. ARCHIVE / REFERENCE (do not use for development)

- `_archive/`

Contains:

- old control layers
- project synthesis
- AI bundles
- quarantine code
- legacy documentation

These are **historical only**.

---

### 3. LOCAL / TOOL FILES (not project truth)

- `.env`
- `.vscode/`
- `.claude/`
- `.venv312/`
- caches / coverage

These are environment-specific and not part of the shared project truth.

---

## Current MVP status

### Working flow

    upload CSV → save file → run QA → save outputs → view map → download PDF → browse jobs

### Working routes

- `/upload`
- `/api/presign`
- `/api/import/<job_id>`
- `/map/view/<job_id>`
- `/pdf/qa/<job_id>`
- `/jobs/`
- `/health/full`

### Job outputs

- `uploads/jobs/<job_id>/meta.json`
- `uploads/jobs/<job_id>/<uploaded_csv>.csv`
- `uploads/jobs/<job_id>/issues.csv`
- `uploads/jobs/<job_id>/map_data.json`

---

## Tech stack

### Runtime

- Python 3.13
- Flask
- pandas, geopandas, shapely, pyproj
- ReportLab
- Leaflet, Bootstrap 5

### Quality

- pytest
- Ruff
- pre-commit
- GitHub Actions CI

---

## Current phase

**Working MVP + Phase 1 complete + Phase 2A complete + Validation batch 2 complete + Validation batch 3 complete + current: validation-led proof-of-value work (Phase 2C)**

This means:

- the MVP exists and works
- rule quality has improved meaningfully from the earliest placeholder stage
- intake/schema normalisation has improved
- the next major uncertainty is no longer “can this be built?”
- the next major uncertainty is “does this provide meaningful value on real survey files for real users?”

---

## Strategic status

An external strategic review was completed on 2026-04-22.

The distilled conclusion was:

- continue the project
- keep the scope narrow
- treat the strongest near-term framing as internal tool / consultancy leverage asset
- shift the next phase toward validation-led development rather than feature-led expansion

This strategic conclusion is recorded in:

- `AI_CONTROL/06_STRATEGIC_REVIEW_2026-04-22.md`

---

## Best current framing

Best current framing:

- internal workflow tool
- consultancy leverage asset
- narrow productivity and QA layer

Less realistic current framing at this stage:

- broad SaaS platform
- major standalone utility software business
- fully mature DNO compliance product

---

## Main current weakness

The main current weakness is now:

**lack of real-world validation**

More specifically:

- the tool has not yet been properly tested against one or more real survey files from real jobs
- the project still needs proof that the current outputs catch issues real users actually care about
- further development should now be guided by real usage evidence, not just internal logic

Important secondary weakness:

- the current rules are meaningful for an MVP, but are not yet deeply differentiated or truly DNO-grade

---

## Key source files

### QA logic

- `app/dno_rules.py`
- `app/qa_engine.py`

### Intake / pipeline

- `app/controller_intake.py`
- `app/routes/api_intake.py`
- `app/routes/api_upload.py`
- `app/routes/map_preview.py`
- `app/routes/pdf_reports.py`

### Tests

- `tests/`

### Strategic / control truth

- `AI_CONTROL/00_PROJECT_CANONICAL.md`
- `AI_CONTROL/01_CURRENT_STATE.md`
- `AI_CONTROL/02_CURRENT_TASK.md`
- `AI_CONTROL/03_WORKING_RULES.md`
- `AI_CONTROL/04_SESSION_HANDOFF.md`
- `AI_CONTROL/05_PROJECT_REFERENCE.md`
- `AI_CONTROL/06_STRATEGIC_REVIEW_2026-04-22.md`

---

## Development principles

- Keep scope narrow (pre-CAD QA only)
- Focus on real-world usefulness
- Prioritise validation and proof-of-value over abstract expansion
- Treat rules as first-class logic
- Avoid turning this into a general platform too early
- Do not assume more features are the right next step without real survey-file evidence

---

## Useful commands

    source .venv312/bin/activate
    python run.py
    pytest -v
    pre-commit run --all-files
    git add . && git commit -m "..." && git push origin master

---

## Navigation

- What should I work on? → `02_CURRENT_TASK.md`
- What works right now? → `01_CURRENT_STATE.md`
- How do I work? → `03_WORKING_RULES.md`
- What changed last session? → `04_SESSION_HANDOFF.md`
- What did the strategic review conclude? → `06_STRATEGIC_REVIEW_2026-04-22.md`
- How does the project operate across all tools? → `WORKFLOW_SYSTEM.md`
