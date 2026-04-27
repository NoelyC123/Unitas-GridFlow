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
| 2 | D2D elimination | ✅ Complete |
| 3C | Project management (multi-file) | ✅ Complete |
| 3B | Designer review & export readiness | ✅ Complete |
| 3A | Live intake platform | Planned |
| 4 | Structured field capture | Planned |
| 5 | Designer workspace | Planned |
| 6 | DNO submission layer | Planned |

**Stage 1** is complete: the tool parses raw controller dumps, validates their contents, and gives the designer a clear pre-design briefing before they open PoleCAD.

**Stage 2** is complete: the tool produces structured, sequenced, designer-readable D2D replacement outputs directly from raw controller dumps. Clean route-chain export and interleaved D2D working view included. Output is provisional and not a verified final PoleCAD import format.

**Stage 3C** is complete: named projects group related survey files. Multiple CSVs can be uploaded to a single project. Each file still runs through the same Stage 1/2 pipeline independently. Map, PDF, D2D chain and working view are all accessible per file from the project overview page. Legacy J##### jobs remain fully accessible.

**Stage 3B** is complete: designers can now review and sign off on auto-generated EXpole pairings before using D2D exports. A per-file review page shows all EXpole-to-proposed-pole pairings with dropdown reassignment controls. Reviewed exports carry a "Designer Reviewed" header; unreviewed exports remain "provisional". Review can be reset to auto-generated at any time. The original `sequenced_route.json` is never modified.

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
- Produces a clean D2D route-chain export (`<job_id>_d2d_chain.csv`)
- Produces an interleaved D2D working view (`<job_id>_d2d_working_view.csv`)
- Performs route sequencing, EXpole matching, span calculation and deviation-angle calculation
- Handles detached / `not required` records
- Adds section summaries, global provisional design pole numbering and sequence-confidence notes
- Groups related survey files into named projects (Stage 3C)
- Per-project map, PDF, D2D chain and working view all accessible independently per file
- Designer review page with EXpole pairing reassignment and sign-off (Stage 3B)
- D2D exports reflect reviewed pairing decisions with reviewed/provisional header

**Validated on 4 real survey files from real NIE and SPEN jobs.**

---

## Current status

- **Stage 1: complete**
- **Stage 2: complete**
- **Stage 3C: complete** (commit `b0b5331`)
- **Stage 3B: complete** (commits `a9b3ee2`, `7daa5a9`)
- **273 passing tests**
- **Gordon + NIE real files validated**
- Active CI (GitHub Actions: pre-commit + pytest)

### What was just shipped

**Stage 3B — Designer Review & Export Readiness** (commits `a9b3ee2`, `7daa5a9`):

- `review.json` overlay storage per project file — original sequenced_route.json never modified
- Per-file review page (`/review/project/<pid>/<fid>`) with EXpole pairing table and dropdown reassignment
- Designer reviewed/not-reviewed flag with review notes
- D2D Chain and D2D Working View exports apply reviewed pairing overrides
- Reviewed exports: "Designer Reviewed — <timestamp>" header; unreviewed: "provisional"
- Reset to auto-generated — single delete, no pipeline re-run
- 20 unit tests + 9 integration tests

### Earlier: Stage 3C — Project Management (commit `b0b5331`):

- Named project container (P001, P002, …) above the existing flat-job model
- Multiple survey files per project (F001, F002, …)
- `project.json` aggregates file summaries (total poles, issues, rulepacks)
- Project-aware upload flow with auto-suggested project name from filename
- Project overview page and projects list page (client-side rendered)
- Map, PDF, D2D chain and working view all routed per project file
- All legacy J##### routes unchanged — full backward compatibility
- 22 unit tests + 9 integration tests

### Earlier: Stage 2 — D2D elimination

Stage 2A / 2B / 2C delivered a validated provisional D2D replacement baseline:

- Clean chain export for route analysis
- Interleaved D2D working view for designer review
- Detached / not-required record handling
- EXpole matching and replacement references
- Section-aware output with section summaries
- Global provisional design pole numbering
- Sequence notes for high-ambiguity files
- Export polish and clearer UI labels

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
tests/              → pytest suite (244 passing)
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

Stage 3C is now in place. The next meaningful milestone is Stage 3B: the designer reviews the auto-generated outputs (pairings, section boundaries) and adjusts them before exporting.
