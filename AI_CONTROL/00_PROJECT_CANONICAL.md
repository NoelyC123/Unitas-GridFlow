# Unitas GridFlow — Project Canonical

## What this project is

**Unitas GridFlow** is a survey-to-design workflow intelligence and automation tool for UK electricity distribution overhead line work.

It is a **pre-CAD QA gatekeeper** that sits between field survey output and office-based design work, replacing the manual, fragmented, outdated process that currently exists.

---

## The problem this solves

The current survey-to-design workflow in UK overhead line work is fundamentally outdated:

- Surveyors capture precise GNSS coordinates digitally but record critical engineering information (stay specs, clearances, materials, obstructions, crossing details) in handwritten notebooks
- Survey data is handed over on a physical USB drive at the end of the week
- A designer manually cleans and reformats the raw controller export in a D2D spreadsheet before it can be used in PoleCAD
- CAD is used as an error detector rather than a clean production stage
- Quality depends on individuals compensating for weak systems

This project exists because the project owner has done both the survey job on site and the D2D/PoleCAD design job in the office, and knows from direct experience that the entire process can be made dramatically better.

---

## The full vision (6 stages)

### Stage 1 — Post-survey QA gate (CURRENT — mostly built)
Raw controller dump arrives → tool parses it → reports what's there and what's missing → designer knows what they're working with before opening PoleCAD.

### Stage 2 — D2D elimination (NEXT)
Tool takes raw controller dump and produces structured, sequenced, PoleCAD-ready output directly. No spreadsheet bridge. Automatic pole sequencing, section splitting, coordinate formatting. The manual D2D step disappears.

### Stage 3 — Live intake platform
Instead of processing files after the fact, the tool becomes what the surveyor sends data to in real-time. Surveyor syncs controller data at end of each day (or continuously). Tool immediately validates, runs QA, produces completeness report. Designer sees job building up in real-time. Feedback loop closes while surveyor is still on site or nearby.

### Stage 4 — Structured field capture
Surveyor uses a tablet/iPad alongside Trimble with GIS integration. Instead of writing in a notebook, they enter structured data: pole type, stay type/quantity/dimensions, clearance measurements, crossing details, photos geotagged to point records. 80% of what currently goes on paper moves into structured digital capture.

### Stage 5 — Designer workspace
Tool presents the complete job to the designer: route on map, every pole with full attributes, replacement pairs identified, stay requirements flagged, clearance issues highlighted, photos linked. Designer reviews, approves/amends, exports directly to PoleCAD. The "open the CSV and figure out what it means" step is gone.

### Stage 6 — DNO submission layer
Tool generates submission-ready packs: route maps, clearance schedules, compliance reports, photo evidence, QA audit trails. Formatted to DNO requirements.

---

## Commercial trajectory

- **Stages 1-2:** Internal tool / consultancy asset. Saves time on every job.
- **Stage 3:** Sellable to other OHL contractors doing D2D work.
- **Stage 4:** Sellable to survey teams directly. Changes how fieldwork is done.
- **Stages 5-6:** Potentially valuable to DNOs themselves.

---

## What exists right now

The tool currently:
- Parses raw Trimble GNSS controller dump CSVs
- Detects coordinate reference systems (Irish Grid TM65, ITM, OSGB27700)
- Converts coordinates for map display
- Classifies records by role (structural, context, anchor)
- Detects EXpole-to-Pol replacement pairs
- Produces confidence-aware severity tiers
- Generates 7 scoped design evidence gates
- Renders interactive Leaflet map
- Generates PDF pre-design briefing
- Infers correct DNO rulepack from geography
- 175 passing tests, active CI

Validated on 4 real survey files from real NIE and SPEN jobs.

---

## Current phase

**Stage 1 complete → entering Stage 2 (D2D elimination)**

The immediate priority is making the tool produce PoleCAD-ready output from raw controller dumps, eliminating the manual D2D spreadsheet step.

---

## Core principle

This project is **validation-led, not feature-led**.

Every step must answer: **Does this improve the reliability, clarity, and design-readiness of real survey data?**

---

## Source of truth

1. Real survey files and validation evidence (highest)
2. Control layer files in AI_CONTROL/
3. Current repo implementation and tests
4. Documentation
5. AI summaries / assumptions

---

## Tool roles

- **Claude Desktop:** Project orchestrator — defines what gets built, why, and in what order. Reviews results. Manages all tools.
- **Claude Code (VS Code):** Primary builder — implements code, runs tests, commits, pushes.
- **ChatGPT:** Available for second opinions, commercial thinking, and review.

---

## Key reference documents

- `AI_CONTROL/09_PROJECT_ORIGIN_AND_FIELD_NOTES.md` — why this project exists, the real workflow observed
- `AI_CONTROL/08_OHL_SURVEY_OPERATIONAL_STANDARD.md` — domain standard for survey data
- `OHL_SURVEY_OPERATIONAL_STANDARD.md` — full operational standard document
- `VALIDATION_ANALYSIS_JOB_2814_513.md` — first real-file validation findings

---

## Repository

- **GitHub:** `https://github.com/NoelyC123/Unitas-GridFlow`
- **Branch:** `master`
- **Local:** `/Users/noelcollins/Unitas-GridFlow`
