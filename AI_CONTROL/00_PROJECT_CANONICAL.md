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

### Stage 1 — Post-survey QA gate (COMPLETE)
Raw controller dump arrives → tool parses it → reports what's there and what's missing → designer knows what they're working with before opening PoleCAD.

### Stage 2 — D2D elimination (COMPLETE)
Tool takes raw controller dump and produces structured, sequenced, designer-readable D2D replacement outputs directly. It now provides a clean route-chain export and an interleaved D2D working view. Final PoleCAD import format remains out of scope until verified with additional evidence.

### Stage 3 — Live intake platform (COMPLETE)
Instead of processing files after the fact, the tool becomes what the surveyor sends data to in real-time. Surveyor syncs controller data at end of each day (or continuously). Tool immediately validates, runs QA, produces completeness report. Designer sees job building up in real-time. Feedback loop closes while surveyor is still on site or nearby.

### Stage 4 — Structured field capture (FUTURE)
Surveyor uses a tablet/iPad alongside Trimble/GNSS and GIS data. Trimble remains the coordinate/source-of-position authority; Unitas GridFlow becomes the structured engineering capture layer around those records. Instead of writing design-critical evidence only in a notebook, the surveyor enters structured data such as pole type, stay type/quantity/dimensions, clearance measurements, crossing details, access/private-land notes, and photos linked to point records. 80% of what currently goes on paper moves into structured digital capture.

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
- Produces clean D2D route-chain export (`<job_id>_d2d_chain.csv`)
- Produces interleaved D2D working view (`<job_id>_d2d_working_view.csv`)
- Handles detached / not-required records
- Produces section-aware output and global provisional design pole numbering
- Supports named projects, project file intake metadata, designer review, reviewed/provisional exports, and controlled remote mobile access
- Provides a repeatable validation evidence-pack utility for raw input, generated outputs, review state, screenshots, notes, and AI review prompts
- Classifies real-world route context / crossing records such as `Pline`, `110xing`, `33xing`, `11xing`, and `HVxing` as context rather than structural poles
- 287 passing tests, active CI

Validated on Gordon, NIE, and Bellsprings/SPEN real survey files, including raw Gordon data, manual PR1/PR2 split evidence, a protected iPhone/mobile Gordon field-trial run, and a Bellsprings before/after package with real pole schedule, route map, profile, and technical information sheet.

---

## Current phase

**Operational use after Stage 3 closure**

Stages 1, 2 and 3 are complete for the current evidence set. The immediate priority is using GridFlow on a real operational job and letting real survey-to-design friction define the next build. Stage 4 structured field capture, tablet/iPad use, photo evidence, and richer Trimble/GIS integration remain the future roadmap but are not current implementation work.

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
- `AI_CONTROL/16_STAGE_2_COMPLETION_REVIEW.md` — Stage 2 completion decision document
- `OHL_SURVEY_OPERATIONAL_STANDARD.md` — full operational standard document
- `VALIDATION_ANALYSIS_JOB_2814_513.md` — first real-file validation findings

---

## Repository

- **GitHub:** `https://github.com/NoelyC123/Unitas-GridFlow`
- **Branch:** `master`
- **Local:** `/Users/noelcollins/Unitas-GridFlow`
