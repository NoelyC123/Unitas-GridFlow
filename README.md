# Unitas GridFlow

**Survey-to-design workflow intelligence and automation for UK electricity distribution overhead line work.**

---

## What this is

Unitas GridFlow is a pre-CAD QA gatekeeper and workflow automation tool that sits between field survey output and office-based design work.

It exists because the project owner has done both the survey job on site and the D2D/PoleCAD design job in the office, and knows from direct experience that the entire survey-to-design handoff can be made dramatically better.

**No competing product exists in this space.** All existing tools sit upstream (field capture) or downstream (design/CAD). The survey-to-design handoff gap is unserved.

---

## The problem

The current survey-to-design workflow in UK overhead line work is fundamentally outdated:

- Surveyors capture precise GNSS coordinates digitally, but record critical engineering information (stay specs, clearances, materials, obstructions, crossing details) in handwritten notebooks
- Survey data is handed over on a physical USB drive at the end of the week
- A designer manually cleans and reformats the raw controller export in a D2D spreadsheet before it can be used in PoleCAD
- CAD is used as an error detector rather than a clean production stage
- Quality depends on individuals compensating for weak systems

---

## The vision (6 stages)

| Stage | Name | Status |
|-------|------|--------|
| 1 | Post-survey QA gate | ✅ Complete |
| 2 | D2D elimination | ← Current |
| 3 | Live intake platform | Planned |
| 4 | Structured field capture | Planned |
| 5 | Designer workspace | Planned |
| 6 | DNO submission layer | Planned |

**Stage 1** is complete: the tool parses raw controller dumps, validates their contents, and gives the designer a clear pre-design briefing before they open PoleCAD.

**Stage 2** (current): the tool produces structured, sequenced, PoleCAD-ready output directly from the raw controller dump, eliminating the manual D2D spreadsheet step.

---

## What the tool does right now

- Parses raw Trimble GNSS controller dump CSVs
- Detects coordinate reference systems (Irish Grid TM65, ITM, OSGB27700) and converts to WGS84
- Classifies records by role: structural, context (Hedge, Fence, BTxing, LVxing, Road, etc.), anchor
- Detects EX/PR replacement pairs and produces design narratives
- Applies confidence-aware QA checks with PASS/WARN/FAIL severity tiers
- Generates 7 scoped design evidence gates (Position, Structure Identity, Structural Spec, Stay Evidence, Clearance Design, Conductor Scope, Overall Handoff Status)
- Renders an interactive Leaflet map with design-readiness signals
- Produces a PDF pre-design briefing report
- Infers the correct DNO rulepack from geography (SPEN, SSEN, NIE, ENWL)

**Validated on 4 real survey files from real NIE and SPEN jobs.**

---

## Current status

- **Stage 1: complete**
- **Stage 2: in progress**
- **175 passing tests**
- **4 real files validated**
- Active CI (GitHub Actions: pre-commit + pytest)

### What was just shipped (Phase 3A)

- Crossing codes (BTxing, LVxing, Road, Ignore) classified as context, not structural — eliminates false QA positives for height and span checks
- Span minimum threshold reduced from 10m to 5m — matches real survey density on dense jobs
- Location field contamination cleaned (Trimble compound codes like `Pol:LAND USE` stripped)
- 6 targeted tests added covering all three changes

---

## Why this will succeed

- Real domain expertise: the project owner has done both the survey and design sides of the workflow
- Real validation: tested against actual NIE and SPEN survey files, not synthetic data
- Clear gap: no product exists for this workflow segment
- Defined commercial trajectory: internal tool → contractor tool → survey-team tool → DNO layer

---

## Project structure

```
AI_CONTROL/         → control layer (project truth + direction)
app/                → Flask application
tests/              → pytest suite (175 passing)
sample_data/        → example inputs
README.md
CHANGELOG.md
CLAUDE.md           → Claude Code working instructions
WORKFLOW_SYSTEM.md  → how the project operates across all tools
_archive/           → historical only — do not use for development
```

---

## Control layer

Project direction is controlled by:

- `AI_CONTROL/00_PROJECT_CANONICAL.md` — full product vision and 6-stage roadmap
- `AI_CONTROL/01_CURRENT_STATE.md` — what is true right now
- `AI_CONTROL/02_CURRENT_TASK.md` — what to build next
- `AI_CONTROL/03_WORKING_RULES.md` — development discipline
- `AI_CONTROL/04_SESSION_HANDOFF.md` — session continuity
- `AI_CONTROL/08_OHL_SURVEY_OPERATIONAL_STANDARD.md` — domain standard reference
- `AI_CONTROL/09_PROJECT_ORIGIN_AND_FIELD_NOTES.md` — project origin and real workflow notes

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

## Key files

- `app/controller_intake.py` — raw controller dump parsing, CRS detection, record-role classification
- `app/qa_engine.py` — QA check engine
- `app/issue_model.py` — structured issue model, evidence gates, designer summary
- `app/dno_rules.py` — DNO rulepacks
- `app/routes/api_intake.py` — intake pipeline
- `app/routes/map_preview.py` — map logic
- `app/routes/pdf_reports.py` — PDF generation
- `tests/` — must remain green

---

## After any code change

```
pytest -v
pre-commit run --all-files
git add .
git commit -m "clear message"
git push
```

---

## Final note

This is not a general platform.

It is a specialist pre-CAD workflow tool for the survey-to-design gap in UK electricity network overhead line work, built by someone who has worked both sides of that gap.

The next meaningful milestone is Stage 2: a raw controller dump goes in, and a PoleCAD-ready structured output comes out — no spreadsheet required.
