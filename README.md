# Unitas GridFlow

**Pre-CAD QA, validation, and workflow support for UK electricity network survey-to-design handoffs.**

---

## Overview

Unitas GridFlow is a survey-to-design workflow intelligence tool for UK electricity network projects.

Its role is to:

- ingest survey data (CSV, raw controller exports, Trimble dumps)
- interpret record roles — structural, context, anchor, existing/proposed
- normalise input into a consistent internal schema
- apply rule-based QA validation
- identify design risks and gaps in the survey handoff
- generate structured issues with design-context explanations
- render mapped outputs with design-readiness signals
- produce a PDF pre-design briefing report
- retain job outputs locally for review

Short version:

**A survey-to-design workflow intelligence tool for UK electricity network projects**

---

## Why this project exists

Unitas GridFlow exists because repeated real-world friction was observed in the handoff between field survey and office design.

The main problem is not usually the engineering calculation itself.

The main problem is often that incoming survey information is:

- inconsistent
- incomplete
- awkward to interpret
- mixed in quality
- discovered to be defective too late in the process

In practice, designers are often forced to perform hidden QA before they can begin actual design work — wasting time and increasing the risk of poor assumptions entering the design process.

The project is intended to act as a structured gate between survey and design by:

- validating incoming data early
- interpreting what record types are present (structural, context, anchor, existing/proposed)
- catching missing or inconsistent information
- applying practical workflow / DNO-style checks
- surfacing design risks before office time is wasted downstream
- producing a clear design-readiness signal for PoleCAD/CAD/design teams

It is useful across the survey, planning, and design workflow — not only for surveyors. Its value is in improving the trustworthiness of the digital handoff that downstream engineering decisions depend on.

**This tool does not replace Trimble, PoleCAD, AutoCAD, or engineering designers. It is a pre-design intelligence layer, not a substitute for any of these.**

---

## Current MVP Status

The project currently has a working local MVP.

### Working flow

```
upload CSV → save file → run QA → save outputs → view map → download PDF → browse jobs
```

### Confirmed working components

- upload page
- upload / presign flow
- CSV save to job folder
- intake / finalise route
- QA processing
- `issues.csv` generation
- `map_data.json` generation
- PDF QA report route
- jobs listing page
- representative input schema with header normalisation
- pytest coverage
- GitHub Actions CI (`pre-commit` + `pytest`)

---

## Current status

The project has moved beyond setup and baseline scaffolding.

### Completed so far

- working local MVP
- 4 live regional rulepacks
- 10 QA check types
- Phase 1 complete: QA rule improvements
- Phase 2A complete: input/header normalisation improvements
- Validation batch 2 complete: raw GNSS controller dump intake + completeness reporting
- Validation batch 3 complete: coord_consistency fix for non-OSGB grids + QA noise suppression for controller files
- Validation batch 4 complete: NIE_11kV rulepack auto-detection from Irish Grid CRS + completeness surfacing in map view and PDF
- Validation batch 5 complete: design readiness verdict + survey coverage categories + enhanced map popups
- Validation batch 6 complete: issue-text popup explanation + interactive pass/fail filter + Records label + design-readiness wording + overlap detection
- Validation batch 7 complete: feature-aware QA (Hedge skipped in span checks) + record inspection panel + "not captured" height in popups
- Validation batch 8 complete: strict structural_only scoping for height rules + issue deduplication (no duplicate height FAILs per record)
- Validation batch 9 complete: record-role classification (structural/context/anchor), anchor chain-reset in span checks, Gate/Track/Stream as context, role breakdown in map UI and PDF
- Validation batch 10 complete: record count consistency, span threshold decimal precision, coverage label fix (any data → Partial), expanded what_this_supports
- Validation batch 11 complete: EX/PR replacement cluster detection — EXpole + nearby structural emits WARN instead of false span-too-short FAIL; relationship metadata in map popup and design readiness
- Batch 12 complete: angle/stay evidence logic — angle structures with no proximate stay evidence emit a cautious WARN; surfaced in popup, record panel, PDF, and design readiness
- Batch 13 complete: confidence-aware QA refinements — short span tiers (very short/unusual/borderline, all WARN); EXpole height-below-min downgrades to WARN; design readiness strong summary when material absent
- Batch 14 complete: EX/PR narrative linking — asset_intent labels (Existing asset / Proposed support) in GeoJSON and map UI; warn_count/warn_texts now correctly serialised to GeoJSON (Batch 12 gap fixed); improved replacement-pair popup/panel wording
- Batch 15 complete: designer summary layer — circuit summary, top design risks (grouped), replacement narratives; map side panel and PDF report now present a pre-design briefing rather than a raw QA dump
- 121 passing tests
- active control layer for project truth and direction

### Current main unresolved issue

The biggest remaining uncertainty is now:

**real-world validation**

The project still needs proof that the current tool provides meaningful value on real survey files for real users.

---

## Current development focus

Primary priority:

**Validation-led next phase**

This means the next important step is to:

- test the current tool against one or more real survey files from real jobs
- identify what works
- identify what breaks
- identify what real users actually care about
- refine the next development phase from that evidence

This is now more important than abstract feature expansion.

---

## Current limitations

- real-world validation still missing
- rules are meaningful for an MVP but not yet deeply differentiated or truly DNO-grade
- issue modelling is still lightweight
- browser E2E coverage not yet implemented
- output model is still MVP-level, not production-grade

---

## Best current framing

At this stage, the strongest realistic framing is:

- internal workflow tool and consultancy leverage asset
- survey-to-design workflow intelligence layer for UK electricity network projects
- trusted pre-CAD gate that interprets, validates, and explains survey handoffs

Less realistic framing right now:

- broad SaaS platform
- major standalone utility software business
- fully mature DNO compliance product
- replacement for Trimble, PoleCAD, AutoCAD, or engineering designers

---

## Project structure

The repository is intentionally split into three layers:

### 1. ACTIVE PROJECT (used for development)

- `AI_CONTROL/` → control layer (project truth + direction)
- `app/` → Flask application
- `tests/` → pytest suite
- `sample_data/` → example inputs
- `README.md`
- `CHANGELOG.md`
- `CLAUDE.md`
- `WORKFLOW_SYSTEM.md` → how the project operates across all tools
- `PROJECT_DEEP_CONTEXT.md`
- root config files

### 2. ARCHIVE (reference only — do not use for development)

- `_archive/`

Contains:

- old control layers
- AI synthesis outputs
- legacy documentation
- quarantined code
- upload bundles

These are historical only.

### 3. LOCAL / TOOL FILES (not project truth)

- `.env`
- `.vscode/`
- `.claude/`
- `.venv312/`
- caches / coverage

---

## Control layer (important)

Project direction is controlled by:

- `AI_CONTROL/00_PROJECT_CANONICAL.md`
- `AI_CONTROL/01_CURRENT_STATE.md`
- `AI_CONTROL/02_CURRENT_TASK.md`
- `AI_CONTROL/03_WORKING_RULES.md`
- `AI_CONTROL/04_SESSION_HANDOFF.md`
- `AI_CONTROL/05_PROJECT_REFERENCE.md`
- `AI_CONTROL/06_STRATEGIC_REVIEW_2026-04-22.md`

These define:

- what the project is
- current state
- current task
- development rules
- session continuity
- strategic conclusions

---

## Quick start

### Create and activate environment

```
python3.13 -m venv .venv312
source .venv312/bin/activate
python -m pip install --upgrade pip setuptools wheel
python -m pip install -r requirements.txt
python -m pip install pre-commit ruff pytest
```

### Run the app

```
python run.py
```

### Run tests

```
pytest -v
```

### Run linting

```
pre-commit run --all-files
```

---

## Tech stack

- Python 3.13
- Flask
- pandas / geopandas
- shapely / pyproj
- reportlab
- Leaflet
- Bootstrap 5
- pytest
- Ruff
- pre-commit
- GitHub Actions CI

---

## Development principles

- Stay strictly narrow in scope
- Work one task at a time
- Prefer small, targeted changes
- Avoid unnecessary rewrites
- Do not introduce features outside current scope
- Do not assume more features are the right next step without validation evidence

---

## Key files

- `app/dno_rules.py` — QA rulepacks
- `app/qa_engine.py` — QA engine
- `app/routes/api_intake.py` — CSV intake and normalisation
- `app/routes/api_upload.py` — upload handling
- `app/routes/map_preview.py` — map logic
- `app/routes/pdf_reports.py` — PDF generation
- `tests/` — must remain green

---

## After any code change

Always run:

```
pytest -v
pre-commit run --all-files
```

Then:

```
git add .
git commit -m "clear message"
git push
```

---

## Final note

This project is intentionally narrow.

It is not a general platform.

It is a specialist pre-CAD QA layer for survey-to-design workflows, and the next meaningful step is proving that it provides real-world value on real survey files.
