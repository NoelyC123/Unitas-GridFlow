# Unitas GridFlow - Full Project Context For AI Tools

This file combines the current authoritative project documents into one readable context pack.

Use this when an AI tool cannot access the repository directly.

## Current Update Override

This combined file includes copied source documents that may still mention earlier states. The current handover-pack update (2026-04-27) supersedes those older mentions.

Current confirmed state:

- Stage 1 is complete.
- Stage 2A, 2B, 2C implemented and validated. Stage 2 is formally closed.
- Stage 3C (Project Management / multi-file job support) is implemented and validated. Commit: `b0b5331`
- Stage 3B (Designer Review & Export Readiness) is implemented and validated. Commits: `a9b3ee2`, `7daa5a9`
- Current test count: 273 passing.
- Named project container (P001/F001 model) is in place.
- Designer review overlay (review.json) is in place. EXpole pairing reassignment, sign-off flag, reset to auto-generated all work.
- D2D exports apply reviewed pairings and show reviewed/provisional header.
- All legacy J##### routes unchanged — full backward compatibility.
- Current focus: Stage 3B is closed. Next direction (Stage 3B polish vs Stage 3A) not yet decided.

If this file conflicts with newer handover-pack notes, use the newest handover-pack notes and the latest repo state.



---

# FILE: AI_HANDOVER_PACK/00_READ_THIS_FIRST.md

# Unitas GridFlow AI Handover Pack

This pack is for updating Claude Desktop, ChatGPT, Claude Code, Cursor, Codex, Gemini, or any other AI/tool with the latest Unitas GridFlow project direction.

## Critical Instruction

Treat this handover pack as the current project context.

Do not rely on older conversations, older batch numbers, stale project assumptions, old scripts, old folders, or previous descriptions that frame Unitas GridFlow as only a CSV QA checker.

## Current Project Identity

Unitas GridFlow is a survey-to-design workflow intelligence and automation tool for UK electricity distribution overhead line work.

It is a pre-CAD QA gatekeeper and workflow automation layer that sits between field survey output and office-based design work.

Short definition:

Unitas GridFlow turns raw field survey information into structured, validated, design-ready data for electricity network design teams.

## Current Stage

Stage 1 is complete.

Current focus is Stage 2: D2D elimination / PoleCAD-ready output.

The immediate product direction is: raw Trimble/controller dump in, structured sequenced PoleCAD-ready output out, with the manual D2D spreadsheet bridge reduced or removed.

## Six-Stage Vision

1. Post-survey QA gate
2. D2D elimination / PoleCAD-ready output
3. Live intake platform
4. Structured tablet-based field capture
5. Designer workspace
6. DNO submission layer

## Tool Roles

- Human/domain owner: final authority on real-world process and decisions.
- Claude Desktop: project orchestrator, defines what gets built and why.
- Claude Code/Cursor: primary builder, edits code, runs tests, commits and pushes when instructed.
- ChatGPT: second opinion, commercial thinking, strategy review, wording/help documents.
- Codex/Gemini/others: optional bounded review or second opinion only.

## Read Order For Any AI

1. source_files/CLAUDE.md
2. source_files/WORKFLOW_SYSTEM.md
3. source_files/README.md
4. source_files/AI_CONTROL/00_PROJECT_CANONICAL.md
5. source_files/AI_CONTROL/02_CURRENT_TASK.md
6. source_files/AI_CONTROL/01_CURRENT_STATE.md
7. source_files/AI_CONTROL/04_SESSION_HANDOFF.md
8. source_files/AI_CONTROL/09_PROJECT_ORIGIN_AND_FIELD_NOTES.md
9. source_files/AI_CONTROL/08_OHL_SURVEY_OPERATIONAL_STANDARD.md
10. source_files/CHANGELOG.md

## Superseded / Do Not Treat As Current Direction

Do not use archive files as current project truth unless explicitly asked.

Do not rely on superseded control files if they conflict with current canonical files.

The active source of truth is the current AI_CONTROL files, especially 00, 01, 02, 04, 08 and 09.


---

# FILE: AI_HANDOVER_PACK/04_DEVELOPMENT_COMPLETED_SO_FAR.md

# Development Completed So Far

This file summarises the current implementation state for AI tools that need a fast project update.

## Current Product State

Unitas GridFlow currently has a working Stage 1 post-survey QA gate.

It can process raw Trimble/GNSS controller dump CSVs and produce useful pre-design intelligence before a designer opens PoleCAD.

## Completed Capabilities

- Raw Trimble GNSS/controller dump CSV parsing.
- Coordinate reference system detection.
- Support for Irish Grid TM65, ITM and OSGB27700 context.
- Coordinate conversion for map display.
- Record-role classification into structural, context and anchor-type records.
- Classification of context features such as Hedge, Fence, BTxing, LVxing, Road and Ignore.
- Detection of EX/PR replacement pairs.
- Design narrative generation for replacement pairs and design handoff context.
- Confidence-aware QA checks using PASS/WARN/FAIL severity tiers.
- Seven scoped design evidence gates:
  - Position
  - Structure Identity
  - Structural Spec
  - Stay Evidence
  - Clearance Design
  - Conductor Scope
  - Overall Handoff Status
- Interactive Leaflet map with design-readiness signals.
- PDF pre-design briefing report.
- DNO rulepack inference from geography.
- Validation against four real survey files from NIE and SPEN jobs.
- Active test suite with 175 passing tests.
- Active CI with pre-commit and pytest.

## Phase 3A Completed

Phase 3A improved real-file handling by:

- Treating crossing codes such as BTxing, LVxing, Road and Ignore as context, not structural records.
- Reducing false QA positives for height and span checks.
- Reducing the span minimum threshold from 10m to 5m to better match dense real survey jobs.
- Cleaning location field contamination from Trimble compound codes such as `Pol:LAND USE`.
- Adding targeted tests for these changes.

## Current Development Focus

Current focus is Stage 2: D2D elimination.

The next milestone is for the tool to take a raw controller dump and produce structured, sequenced, PoleCAD-ready output directly.

Stage 2 should focus on:

- Automatic pole sequencing.
- Correct pole numbering.
- Route section splitting.
- EXpole records matched to route position.
- Coordinate output shaped for PoleCAD/design use.
- Reducing or eliminating manual D2D spreadsheet cleaning.

## Important Boundary

Do not jump ahead to the tablet app, live sync, designer workspace or DNO submission layer until Stage 2 is properly validated.


---

# FILE: AI_HANDOVER_PACK/source_files/CLAUDE.md

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

### Stage 2 — D2D elimination ← CURRENT
Tool takes raw controller dump and produces structured, sequenced, PoleCAD-ready output directly. No spreadsheet bridge. Automatic pole sequencing, section splitting, coordinate formatting. The manual D2D step disappears.

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

### Claude Desktop — Project Orchestrator
- defines what gets built, why, and in what order
- reviews validation results
- manages all tools
- prevents scope drift
- holds full project context

### Claude Code (VS Code) — Primary Builder (YOU)
- reads repo, writes code, runs tests, commits, pushes
- executes tasks as defined by the orchestrator
- makes minimal, targeted changes
- keeps tests passing

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
- Stage 2 (D2D elimination) is the current work
- 175 tests passing
- CI active
- 4 real survey files validated
- Phase 3A complete: crossing codes as context, span threshold 5m, location cleanup

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


---

# FILE: AI_HANDOVER_PACK/source_files/WORKFLOW_SYSTEM.md

# Unitas-GridFlow — Workflow System

## Purpose

This document defines how the Unitas-GridFlow project is operated across all tools.

It ensures alignment between AI tools, controlled development, and real-world usefulness.

---

## 1. Core Principle

This project is **validation-led, not feature-led**.

Every step must answer:

> **"Does this improve the reliability, clarity, and design-readiness of real survey data?"**

---

## 2. The Product Vision (6 stages)

| Stage | Name | Status |
|-------|------|--------|
| 1 | Post-survey QA gate | ✅ Complete |
| 2 | D2D elimination | ← CURRENT |
| 3 | Live intake platform | Planned |
| 4 | Structured field capture | Planned |
| 5 | Designer workspace | Planned |
| 6 | DNO submission layer | Planned |

Work on the **current stage only**. The orchestrator defines when a stage is complete and when to advance.

---

## 3. Tool Roles (STRICT)

### You (Human) — Domain Authority

- provide real survey files
- define real-world problems
- make final decisions

---

### Claude Desktop — Project Orchestrator

- defines WHAT gets built, WHY, and in WHAT ORDER
- reviews validation results
- manages all tools
- prevents scope creep and stage drift
- holds full project context between sessions

This is the **control layer above all tools**.

---

### Claude Code (VS Code) — Primary Builder

- reads the full repository
- writes and edits code
- runs tests
- commits and pushes

Responsibilities:
- implement tasks exactly as defined by the orchestrator
- keep tests passing
- make minimal, targeted changes

This is the **execution engine**.

---

### ChatGPT — Second Opinion Only

- available for commercial thinking and review
- not the orchestrator
- not the primary decision-maker

---

### Codex — Optional

- second opinion on code
- use sparingly for bounded tasks

---

## 4. Source of Truth Hierarchy

1. **Real survey files** (highest truth)
2. **AI_CONTROL/** files
3. **Codebase (GitHub)**
4. **Documentation**
5. **AI outputs** (lowest)

If anything conflicts: real data wins, control layer overrides assumptions.

---

## 5. The Core Workflow Loop

**Step 1 — Real Input (Human)**
Provide real survey file or real-world issue.

**Step 2 — Task Definition (Claude Desktop)**
Claude Desktop defines the exact problem, narrow solution, and constraints. Updates `AI_CONTROL/02_CURRENT_TASK.md`.

**Step 3 — Implementation (Claude Code)**
Claude Code implements, runs tests, commits, pushes.

**Step 4 — Verification (Claude Desktop)**
Claude Desktop reviews the result, checks alignment with intent, identifies gaps.

**Step 5 — Decision (Claude Desktop)**
Claude Desktop decides: next step, refine, stop, or advance to next stage.

---

## 6. Development Rules

**Always:**
- stay within the current stage
- validate against real files before advancing
- keep tests passing
- make small, targeted changes

**Never:**
- build features without validation evidence
- jump ahead to later stages
- redesign architecture unnecessarily
- allow tools to drift out of sync

---

## 7. Repository Strategy

**GitHub (PRIMARY):** Single source of truth for code, tests, and control files.

**Claude Desktop:** Reads control layer files and implementation files. Does not hold a separate copy of the codebase.

**Local:** `/Users/noelcollins/Unitas-GridFlow/`

---

## 8. Engineering Workflow

After any code change:

1. `pytest -v` — all tests must pass
2. `pre-commit run --all-files`
3. `git add . && git commit -m "clear message" && git push`

---

## 9. Current Stage Context

**Stage 2 — D2D Elimination**

Goal: tool takes raw controller dump → produces structured, sequenced, PoleCAD-ready output. The manual D2D spreadsheet step is eliminated.

What this means:
- automatic pole sequencing (spatial route order, not file order)
- correct pole numbering
- section splitting at sensible points
- coordinate output in PoleCAD-compatible format
- EXpole records matched to their route position

See `AI_CONTROL/02_CURRENT_TASK.md` for the immediate next step.

---

## 10. Success Criteria

The system is working correctly when:
- all tools agree on current state
- changes are small and targeted
- real files produce meaningful outputs
- a designer reviewing output saves measurable time

---

## Final Statement

This is a controlled system for building a real, valuable product.

The goal is not feature completeness. The goal is that the tool produces genuinely useful output for real survey-to-design workflows, at each stage in sequence.


---

# FILE: AI_HANDOVER_PACK/source_files/README.md

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


---

# FILE: AI_HANDOVER_PACK/source_files/OHL_SURVEY_OPERATIONAL_STANDARD.md

OPERATIONAL STANDARD
OVERHEAD LINE (OHL) SURVEY & DATA ACQUISITION
Draft Company Specification / Master Explanation
Reference: OPS-SUR-001
Version: Draft consolidated master standard
Scope: UK distribution overhead networks, typically LV, 11 kV and 33 kV wood-pole and associated support systems
Language: UK English
Prepared as a consolidated working standard combining statutory context, common field practice and company-standard survey requirements.

Introduction
This document sets out a practical and technically grounded explanation of what an overhead line electrical surveyor in the UK is expected to do, what information they must collect, why that information matters, and how it supports the wider field-to-office design process. Its purpose is to define the surveyor's role clearly enough that survey staff, designers, planners and managers all understand what a complete and design-usable overhead line survey should contain.

The document is built around a simple principle: the surveyor is the starting point of the entire overhead line workflow. The field team captures the physical reality of the network, the land, the structures, the crossings, the clearances, the condition of the assets and the practical site constraints. That information is then used by the office-based design team to carry out engineering checks, clearance assessments, route validation and construction planning in software and design systems. In other words, the survey is not just a record of where assets are located; it is the foundation for safe, compliant and buildable overhead line design.

This standard brings together three things in one place: first, the legal and safety framework that applies to overhead line work in the UK; second, the common operational practices used by surveyors and DNO contractors in the field; and third, the full range of technical and practical information that may need to be captured during survey. The overall purpose is to define what 'good' looks like in overhead line surveying: a survey that captures enough detail, context and accuracy that the design team can make sound engineering decisions without relying on guesswork, unsafe assumptions or unnecessary repeat visits.

Not every requirement in this document should be read as universal UK law. Some items are statutory or safety-driven, while others reflect common industry practice or sensible company standards developed by DNOs, contractors and engineering teams. For example, the use of a particular device model, a fixed offset distance for rebuilds, or a company rule on when specialist decay testing must be used may be entirely valid as operational standards, but they are not all universal legal requirements in the same way as duties under the Electricity Safety, Quality and Continuity Regulations 2002 and associated HSE guidance. This document therefore separates, as clearly as possible, what is regulatory, what is normal field practice, and what may be adopted as a company-specific survey standard.

1. Purpose of the surveyor's role
The overhead line surveyor is the primary field-data originator. Their job is to capture a sufficiently complete and reliable picture of the existing network, surrounding environment and proposed route so that the design team can carry out structural design, sag-and-tension assessment, statutory clearance checks, construction planning and cost estimation without needing to revisit the site unless something genuinely new emerges.

In plain English, the surveyor's job is not just to 'take points'. It is to capture the physical truth of the route so the office team can understand:
- what is there now,
- what condition it is in,
- what can stay,
- what must go,
- what can be built,
- what cannot be built, and
- what the designer cannot safely infer from coordinates alone.

That matters because UK overhead-line safety is governed by duties to avoid danger, maintain proper clearances and position overhead lines so they do not create foreseeable risk to people, property, vegetation or nearby structures.

2. Core objective of the survey
The survey must produce a field record good enough to support:
- route selection and route validation,
- asset replacement or refurbishment planning,
- statutory clearance assessment,
- structural assessment of poles and stays,
- conductor and hardware specification review,
- land and access planning,
- environmental and third-party constraint review,
- safe construction planning, and
- a clean handoff into design software, CAD and construction packs.

For higher-voltage projects and larger routeing exercises, route selection may also need to take account of wider planning and environmental constraints such as ecology, designated sites and land-use impact.

3. Division of labour: field vs office
The field surveyor captures:
- exact location and geometry,
- existing asset type and arrangement,
- visible condition and obvious defects,
- terrain and route constraints,
- crossing context,
- access and construction practicality,
- landownership / wayleave / boundary context where visible or known, and
- proposed intent for new or replacement infrastructure.

The design team then applies:
- structural loading,
- wind and ice cases,
- sag-and-tension modelling,
- uplift / downforce effects,
- pole utilisation and support checks,
- statutory clearance validation, and
- final design optimisation in software such as PLS-CADD and other design packages.

That is why a good survey is not merely descriptive. It is a design-enabling evidence set.

4. What an OHL surveyor in the UK actually does
In operational terms, an overhead-line surveyor may be asked to do any combination of the following:
- locate and identify existing poles and associated assets,
- propose new pole positions,
- measure spans and route geometry,
- identify line type, voltage and circuit arrangement,
- check the visible condition of poles, crossarms, insulators, stays and hardware,
- record clearance risks over roads, tracks, water, buildings and vegetation,
- note access issues and ground conditions,
- capture route constraints such as bog, steep slopes, walls, ditches, fences, trees and third-party structures,
- identify whether structures are straight, angle, terminal, tee-off, transformer or service-related,
- note whether stays are present, missing, damaged or required,
- record crossing details that cannot be derived from coordinates alone,
- identify parent poles and spur opportunities, and
- produce the field record needed for re-build, diversion, reinforcement, refurbishment or extension work.

5. Statutory and safety context
At UK level, the most important legal and safety background for overhead-line work includes the following:
- Part V of ESQCR covers overhead lines.
- Regulation 17 deals with minimum heights of overhead lines, wires and cables.
- Regulation 18 includes duties about position, insulation, guarding and avoiding danger, including the requirement that overhead lines should not, so far as reasonably practicable, come so close to buildings, trees or structures as to cause danger.
- HSE's GS6 gives practical safety guidance for work near overhead power lines and covers risk assessment, safe distances, barriers, goalposts, vehicles, material stacking and general precautions.

Accordingly, the surveyor's role is to collect the information required for compliance checking and engineering design, not personally to sign off the final statutory design.

6. Field survey scenarios

A. Greenfield planning
This is where a line is being designed from scratch across open land or largely undeveloped terrain. The surveyor's practical goal is usually to find the most buildable, lowest-risk, lowest-complication alignment. In practice that often means:
- avoiding bogs, peat, marsh, steep banks or unstable ground,
- avoiding environmentally sensitive areas where possible,
- avoiding unnecessary deviation angles,
- seeking longer straight runs where feasible,
- identifying places where construction access is realistic, and
- capturing enough terrain/profile information for later clearance modelling.

B. Brownfield / refurbishment / replacement
This is where an old line is being rebuilt, refurbished or replaced. Typical field tasks include:
- identifying poles to retain, recover, replace or relocate,
- proposing new alignments adjacent to existing live lines where that is the chosen build strategy,
- checking whether offsetting will create boundary, access or safety issues,
- identifying whether the existing route is still viable,
- checking visible condition defects and priority failures, and
- noting any construction problems that would affect the replacement sequence.

Parallel offsetting is common field practice because it can help maintain supply continuity during rebuilds, but the exact offset distance is generally a project, DNO or constructability decision rather than a universal UK rule.

C. Deviations and diversions
This is where a line must move around a new obstacle such as a barn, road alteration, new entrance, development plot or landowner restriction. The surveyor must:
- plot the new path,
- measure the angle change,
- identify whether an angle structure, terminal arrangement or stay will be required,
- confirm ground suitability for stay anchors if needed, and
- note all affected crossings, clearances and third-party interfaces.

On wood-pole systems, angle structures commonly require back-staying, but the specific angle rules and structure limits should be stated as design-standard or company-standard requirements unless tied to the relevant network specification.

D. Tee-offs and service extensions
This is where an existing line is used as the source for a new spur or branch. The surveyor should identify the parent structure, phase arrangement, physical arrangement of the existing top-set, whether the support appears suitable for altered loading, the proposed outgoing route, and any customer-specific plant, crossings or access issues.

7. Survey equipment and tools
The exact approved kit varies by employer and DNO, so the safest wording is "approved company equipment" rather than implying one manufacturer is mandatory across the UK. The main tool classes are set out below.

Primary digital survey equipment:
- GNSS / controller equipment for point logging,
- total station or equivalent where GNSS is unsuitable,
- laser rangefinding for remote dimensions,
- clinometers / slope measurement,
- digital photography, and
- sometimes LiDAR-derived context where available.

Common field tool types:
- GNSS controller / receiver for pole points and route geometry
- laser rangefinder for spans, remote heights and missing dimensions
- clinometer for slopes and relative geometry
- measuring rod / height stick / tapes for manual confirmation
- camera or tablet for photo evidence
- marking paint / pegs for proposed positions
- spade or trenching tools for collar and below-ground inspection where required
- hammer / prod tools for wood pole assessment
- phase identification tools where permitted and required
- PPE and live-line proximity controls under relevant safety rules

Pole condition testing tools:
Hammer sounding, excavation around ground line and internal testing methods are well grounded in utility practice. A Resistograph or similar internal density tool is a credible specialist inspection method where required by company policy, but should not be described as a universal legal requirement unless mandated by the relevant network or company standard.

8. The full master list of data an OHL surveyor may need to capture

8.1 Identification and administrative data
- Asset ID / pole number / point number / SAP or GIS reference
- Existing / proposed / recovered / replaced / relocated / new status
- Survey date and surveyor
- Job number / scheme reference
- DNO / client / project name
- Feature code / layer code / controller code
- Easting
- Northing
- Latitude / longitude where required
- Elevation / reduced level / AOD where captured
- Coordinate reference system / grid system used
- Remarks / notes / red flags
- Photo set references
- Sketch references
- Whether data is verified, estimated or inferred

8.2 Structural asset data
- Pole type: straight / intermediate / angle / terminal / tee-off / transformer / service / H-pole
- Pole material: wood / steel / concrete / composite
- Pole class / strength / grade
- Pole height or estimated installed height
- Pole diameter / circumference at ground line where relevant
- Effective above-ground height where relevant
- Manufacture year / birthmark / branding
- Timber species where known
- Lean / verticality / inclination and direction
- Sinking / uplift / instability evidence
- Ground-line condition
- Shelling
- Necking
- Surface cracks / splits
- Internal decay evidence
- Corrosion on steelwork
- Woodpecker or biological damage
- Top rot / collar rot / below-ground decay evidence
- Pole safe-to-climb / unsafe / defective status where applicable
- Defective label / danger tag presence

8.3 Top-set, fittings and structure configuration
- Crossarm type and material
- Pole top arrangement
- Brackets / steelwork
- Pins / shackles / dead-end fittings
- Insulator type
- Insulator material
- Insulator condition
- Signs of flashover, burning, cracking or contamination
- Number and arrangement of conductors
- Circuit orientation / configuration
- Tee-off configuration
- Terminal arrangement
- Hardware condition / looseness / missing items

8.4 Electrical configuration
- Voltage class: LV / 11 kV / 33 kV / other
- Circuit type
- Single phase / split phase / three phase
- Number of wires
- Phase arrangement
- Phase identification: L1 / L2 / L3 where needed
- Conductor type: bare / covered / ABC
- Conductor material: copper / aluminium / AAAC / ACSR etc.
- Conductor size / cross-sectional area
- Approximate span lengths to adjacent supports
- Neutral / earth arrangement where present
- Transformers and rating
- Fuses / cut-outs
- Air-break switch / ABS
- Recloser / sectionaliser where present
- Surge arrestors
- Street-light or service attachments
- Fibre / telecoms attachments where authorised and relevant

8.5 Stability and stay system data
- Presence of stay / guy wire
- Stay quantity
- Stay location and orientation
- Stay type and material
- Stay anchor location
- Stay spread / angle
- Stay make-off / anchorage condition
- Stay tension condition if visible or assessed
- Corrosion / strand damage
- Stay insulator present or absent
- Stay insulator condition
- Cow guard / visibility sleeve present or absent
- Agricultural protection measures
- Any evidence of livestock rubbing or mechanical damage

8.6 Earthing and safety features
- Earth wire presence where applicable
- Earth conductor condition
- Earth guard / moulding / protective cover
- Earthing rod visible / not visible
- Bonding condition where visible
- Anti-climbing devices
- Danger / warning signage
- Public safety guarding
- Condition of safety plates or notices

8.7 Span, route and network relationship data
- Previous support reference
- Next support reference
- Parent pole reference
- Spur / tee-off destination
- Approximate route direction
- Straight run / angle point / termination
- Deviation angle
- Whether line route is suitable for rebuild in same corridor
- Whether diversion is required
- Whether the structure is part of a section gap, terminal bay or cable transition

8.8 Clearance and crossing data
- Lowest conductor point where measurable
- Ground clearance over road
- Ground clearance over track
- Ground clearance over footpath
- Ground clearance over field / yard / entrance
- Clearance to buildings
- Clearance to sheds / balconies / walls / fences
- Clearance to trees / hedges / strike zone vegetation
- Crossings of roads
- Crossings of rail
- Crossings of watercourses
- Crossings of telecoms
- Crossings of foreign power lines
- Street furniture conflicts
- Streetlight / sign proximity
- Bank height and road camber at crossings where needed

8.9 Environmental, land and site context
- Land use: pasture / arable / domestic / industrial / roadside / moorland etc.
- Boundary lines and fences
- Gates and access points
- Wayleave or easement notes where visible or known
- Third-party encroachment
- Bog / peat / soft ground
- Ditches / drains / waterlogging
- Slopes / embankments / unstable banks
- Watercourses
- Trees and hedgerows
- Protected / sensitive habitat notes where identified in scope
- Livestock presence
- Public interface risk
- Construction access constraints
- 4x4 only / tracked access / pedestrian only / crane needed / no safe access

8.10 Construction and designer-support notes
- Proposed pole position marked
- Whether the proposed position is physically buildable
- Need for temporary outages or sequencing constraints
- Offset from existing line where relevant
- Whether safe separation from live plant appears achievable
- Special plant requirement
- Foundation / digging concern
- Landowner comment or access restriction
- "Do not dig here" or buried-service warning
- Any site fact the office cannot infer later from GIS or coordinates alone

9. Critical "missing links" that must be in the standard
These are exactly the things novices often miss and which should be captured explicitly in a proper operational standard.

Crossing sketches: For road, rail, river and other critical crossings, coordinates alone are not enough. A crossing sketch or profile record should capture carriageway level, verge and bank level, crown / camber, nearby signs and columns, unusual topography, and anything affecting worst-case sag or vehicle clearance.

Phase identification: Mandatory wherever a tee-off, spur or reconnection depends on correct phase continuity. Misidentification can create serious operational consequences for customers and plant.

Stay insulators and livestock protection: These should be in the standard because they sit at the junction of electrical safety, mechanical integrity and agricultural risk.

Pole condition around ground line: Ground-line inspection is a critical control point. Excavation and probing around the pole base may be necessary because below-ground decay is a major failure risk.

10. What should be classed as universal, common, or company-specific

Universal / regulatory backbone:
- ESQCR overhead-line duties
- minimum-height / clearance obligations
- avoiding dangerous proximity to trees, buildings and structures
- safe working near live overhead lines
- risk-based surveying sufficient for design and safety assessment

Common UK / DNO / contractor practice:
- GNSS-based point capture
- laser-assisted remote measurements
- route notes and crossing sketches
- pole condition checks
- stay and angle assessment
- parallel rebuild / offset concepts
- detailed photos of full height, base and top-set
- access and environmental notes
- data capture for CAD / design modelling

Company- or project-specific rules:
- exact approved device models
- "all poles over X years must have Resistograph"
- fixed offset distances
- fixed angle thresholds for stays on all projects
- mandatory capture interval such as every 10 m on all profile surveys
- internal controller feature-code schemas
- exact photo schedule and naming conventions

These may be excellent internal rules, but they should be described as company-standard requirements rather than UK-wide law unless tied to a cited design standard, DNO policy or contract requirement.

11. Recommended final wording for the role
The OHL Surveyor is responsible for capturing complete, accurate and design-usable field data describing the existing overhead-line network, surrounding environment, proposed works and all safety-critical constraints necessary for engineering design, statutory clearance checking, construction planning and asset replacement decision-making.

12. Final consolidated master list
For quick reference, the role can be summarised as requiring capture of the following categories of information:
- Asset ID / point number / SAP-GIS reference
- Existing / proposed / recover / replace / relocate / new status
- Pole type, material, class/grade, height/effective height
- Diameter / circumference at ground line where needed
- Manufacture year / birthmark / species where known
- Easting / northing, latitude / longitude where needed
- Elevation / ground level, CRS / grid system
- Feature code, survey notes / remarks / red flags
- Full-height / top-set / base / asset-tag photos
- Previous and next span relationship
- Parent pole / spur relationship
- Deviation angle, lean / verticality / direction
- Sinking / instability evidence
- Shelling / necking / cracking / external rot
- Internal decay / hammer / probe / specialist test result
- Woodpecker / pest / fungal damage
- Crossarm type and condition
- Brackets / fittings / hardware condition
- Insulator type and condition
- Voltage class, phase configuration, phase identification where needed
- Conductor type / material / size
- Number of wires / arrangement
- Transformer / ABS / fuses / recloser / surge arrestor details
- Earthing / earth wire / guarding where applicable
- Telecom / fibre / third-party attachments
- Stay presence / number / position / type
- Stay anchor condition
- Stay insulator presence and condition
- Cow guard / visibility sleeve presence
- Anti-climbing devices, warning signs / safety plates
- Ground clearance over roads / tracks / paths / yards
- Clearance to buildings / sheds / balconies / walls
- Tree and hedge proximity, strike-zone vegetation
- Road / rail / river / telecom / foreign-line crossing context
- Crossing sketch and profile notes
- Bank height / road camber / street furniture at crossings
- Land use, property boundaries / gates / fences
- Wayleave / easement notes where visible or known
- Access restrictions, 4x4 / plant / crane / pedestrian-only access notes
- Bog / peat / water / slope / embankment / unstable ground notes
- Livestock / public / third-party hazards
- Proposed pole location mark-out
- Construction sequencing concerns
- Live-line proximity concerns
- Any field fact the design team cannot safely infer later from coordinates alone

Bottom line: An OHL surveyor in the UK is effectively building a field-based digital model of the line, the ground, the constraints and the buildability of the route. The survey is not just about asset logging. It is about collecting enough structured evidence that designers can run clearance, strength, sag, angle, stay and replacement decisions properly and safely.


---

# FILE: AI_HANDOVER_PACK/source_files/AI_CONTROL/00_PROJECT_CANONICAL.md

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


---

# FILE: AI_HANDOVER_PACK/source_files/AI_CONTROL/01_CURRENT_STATE.md

# Current State

## Project phase

**Stage 1 complete → entering Stage 2 (D2D elimination)**

---

## What works

- Raw Trimble controller dump intake (tested on 4 real files)
- CRS detection: Irish Grid TM65, ITM, OSGB27700
- Coordinate conversion to WGS84 for map display
- Record-role classification (structural, context, anchor)
- Replacement pair detection (EXpole to Pol matching)
- Evidence gates (7 scoped design gates)
- Confidence-aware severity tiers (PASS/WARN/FAIL)
- Interactive Leaflet map with filtering
- PDF pre-design briefing report
- DNO rulepack inference from geography
- Column/header normalisation for structured CSVs
- Context feature classification (Hedge, Fence, Wall, Gate, Track, Road, Tree, Stream, BTxing, LVxing, Ignore)

## Counts

- **Tests passing:** 175
- **DNO rulepacks:** 4 (SPEN, SSEN, NIE, ENWL)
- **Real files validated:** 4

## What was just fixed (Phase 3A)

- Crossing codes (BTxing, LVxing) classified as context, not structural
- Road and Ignore codes classified as context
- Span minimum threshold reduced from 10m to 5m (fixes dense survey noise)
- Location field contamination cleaned (Pol:LAND USE → empty)

## Known remaining issues

1. File order treated as route order — EXpoles captured at end of file break span calculations
2. Replacement pair narratives can be 1-to-many (noisy)
3. No PoleCAD-ready output format yet (Stage 2 goal)
4. PDF report needs redesign for designer usability
5. No multi-file job support yet (474 + 474c are same job area)

## Strategic position

- No competing product exists in this space
- Tool validated on real NIE and SPEN survey files
- Project owner has direct survey and design experience
- Full 6-stage vision defined (see 00_PROJECT_CANONICAL.md)


---

# FILE: AI_HANDOVER_PACK/source_files/AI_CONTROL/02_CURRENT_TASK.md

# Current Task

## Phase

**Stage 2 — D2D Elimination**

We are entering Stage 2 of the product vision.

---

## Immediate next step

**Run all 4 real validation files through the tool after Phase 3A fixes and verify output quality.**

Files to test:
- 28-14 513 (NIE, small job, 11 points)
- 2814_4-474_raw_trimble_export.csv (NIE, dense survey, 83 points)
- 2814_474c_raw_trimble_export.csv (NIE, separate section same area, 91 points)
- Gordon Pt1 Original (SPEN, large job, 157 points)

What to check:
- Span noise reduced (474 should drop from 42 to much fewer)
- BTxing/LVxing classified as context (not structural)
- Location field clean (no "Pol:LAND USE" contamination)
- Overall output quality — would this save a designer time?

---

## After validation confirms Phase 3A

Begin Stage 2 work: **D2D elimination.**

The goal is to make the tool produce PoleCAD-ready output directly from a raw controller dump, eliminating the manual D2D spreadsheet step.

This means:
- Automatic pole sequencing (spatial route order, not file order)
- Correct pole numbering
- Section splitting at sensible points (the Gordon PR1/PR2 split done automatically)
- Coordinate output in the format PoleCAD expects
- EXpole records matched to their route position, not left at the end of the file

---

## What not to do

- Do not add features without validation evidence
- Do not build tablet/field capture (Stage 4) yet
- Do not build commercial packaging
- Do not expand rulepacks without real-file evidence
- Do not redesign architecture

---

## Files likely involved for Stage 2

- `app/controller_intake.py` — route sequencing logic
- `app/qa_engine.py` — span calculations on spatial sequence
- `app/routes/api_intake.py` — output formatting
- New export module for PoleCAD-ready output
- Tests

---

## Success criteria for Stage 2

A raw controller dump goes in. A structured, sequenced, section-split output comes out that a designer could feed into PoleCAD without manually creating a D2D spreadsheet first.


---

# FILE: AI_HANDOVER_PACK/source_files/AI_CONTROL/03_WORKING_RULES.md

# Working Rules

## Core principles

- Always read a file before editing it.
- Never assume file contents.
- Stay within the current stage.
- Do not broaden scope beyond the current stage.
- Prefer simple, clear, deterministic logic.
- Every step must answer: "Does this improve the reliability, clarity, and design-readiness of real survey data?"

---

## Tool roles

### Claude Desktop (Project Orchestrator)
- Defines what gets built, why, and in what order
- Reviews validation results
- Manages all tools
- Prevents scope drift
- Holds full project context

### Claude Code (VS Code — Primary Builder)
- Reads repo, writes code, runs tests, commits, pushes
- Executes tasks as defined by the orchestrator
- Makes minimal, targeted changes
- Keeps tests passing

### ChatGPT
- Available for second opinions, commercial thinking, review
- Not the primary orchestrator

---

## Development workflow

After code changes:

1. `pytest -v` — all tests must pass
2. `pre-commit run --all-files`
3. `git add . && git commit -m "clear message" && git push`

---

## Validation-first rule

Real-world evidence takes priority over abstract feature expansion. Do not build features without validation evidence from real survey files.

---

## Stage discipline

The project has 6 stages. Work on the current stage only. Do not jump ahead.

1. Post-survey QA gate ✅
2. D2D elimination ← CURRENT
3. Live intake platform
4. Structured field capture
5. Designer workspace
6. DNO submission layer

---

## Source of truth

1. Real survey files (highest)
2. AI_CONTROL/ files
3. Repo code and tests
4. Documentation
5. AI outputs (lowest)


---

# FILE: AI_HANDOVER_PACK/source_files/AI_CONTROL/04_SESSION_HANDOFF.md

# Session Handoff

## Date: April 2026

## What happened this session

### Project vision fully defined

The complete 6-stage product vision was articulated and agreed:

1. Post-survey QA gate (mostly built)
2. D2D elimination (next)
3. Live intake platform
4. Structured field capture (tablet/GIS)
5. Designer workspace
6. DNO submission layer

### Phase 3A completed

Claude Code implemented real-file noise fixes:
- Crossing codes (BTxing, LVxing, Road, Ignore) classified as context
- Span threshold reduced from 10m to 5m
- Location field contamination cleaned
- 6 new tests added
- 175 tests passing, pushed to master (commit 9030274)

### Control layer restructured

Project orchestration moved to Claude Desktop. Control files updated to reflect:
- Full 6-stage vision
- Current phase (entering Stage 2)
- Tool roles clarified
- Domain reference documents saved (OHL operational standard, project origin notes)

### New reference documents added

- `AI_CONTROL/08_OHL_SURVEY_OPERATIONAL_STANDARD.md` — domain standard summary
- `AI_CONTROL/09_PROJECT_ORIGIN_AND_FIELD_NOTES.md` — full project origin and field workflow notes
- `OHL_SURVEY_OPERATIONAL_STANDARD.md` — complete OHL survey operational standard

### Competitive analysis completed

No competing product exists for the survey-to-design handoff gap. All existing tools sit upstream (field capture) or downstream (design/CAD).

---

## Current state

- 175 tests passing
- Phase 3A fixes pushed
- 4 real files need re-testing after Phase 3A
- Ready to enter Stage 2 (D2D elimination)

---

## Next steps

1. Run all 4 validation files through the tool, verify Phase 3A output quality
2. Begin Stage 2 design: route sequencing, pole numbering, section splitting, PoleCAD-ready output


---

# FILE: AI_HANDOVER_PACK/source_files/AI_CONTROL/05_PROJECT_REFERENCE.md

# Project Reference

**Purpose:** Preserve historical context and wider project documentation without bloading day-to-day control files.

**This file is reference only.** It is not part of the active operational control layer.

---

## Project evolution

The project has evolved through multiple iterations and naming conventions:

### SpanCore (original phase)

- Initial DNO compliance / QA tool concept
- Early design and problem definition
- Decision memos and initial architecture work
- Archived but still useful for historical understanding

### EW Design Tool (middle phase)

- Secondary naming convention during development
- Broader design-tool exploration
- Later deprecated in favour of the narrow MVP approach
- Historical only, not for active development

### Unitas GridFlow (current phase)

- Final, canonical name for the project
- Narrow pre-CAD QA and compliance tool
- Current active repository and development branch
- All future work happens here

---

## Active repository locations

### Active development

- **GitHub:** `https://github.com/NoelyC123/Unitas-GridFlow`
- **Local:** `/Users/noelcollins/Unitas-GridFlow`
- **Branch:** `master`

### Archive/reference

- `_archive/` contains historical materials, previous control-layer files, old exports, synthesis documents, and quarantined code
- `_archive/` is reference-only unless explicitly needed

Do not treat archived material as active instruction.

---

## Current structural model

The repository is deliberately organised into three categories:

### 1. Active project surface

These are the live files and folders used for current development:

- `AI_CONTROL/`
- `app/`
- `tests/`
- `sample_data/`
- `README.md`
- `CHANGELOG.md`
- `CLAUDE.md`
- `PROJECT_DEEP_CONTEXT.md`
- root config/runtime files

These define the current working system.

### 2. Archive/reference surface

Historical, archived, or non-active materials live under:

- `_archive/control_layer/old_ai_control/`
- `_archive/docs/PROJECT_SYNTHESIS/`
- `_archive/docs/FRONTEND_FINAL_IMPLEMENTATION.md`
- `_archive/docs/MANIFEST.md`
- `_archive/docs/PROJECT_OPERATING_MODEL.md`
- `_archive/docs/RUNBOOK.md`
- `_archive/admin/GITHUB_ADMIN/`
- `_archive/quarantine/old_quarantine/`
- `_archive/ai_bundles/`

These are preserved for historical understanding, not active development.

### 3. Local/tool-specific surface

These exist in the working repo but are not part of the shared project truth:

- `.env`
- `.vscode/`
- `.claude/`
- `.venv312/`
- caches / coverage files

---

## Active control layer

The active operational control layer is:

- `AI_CONTROL/00_PROJECT_CANONICAL.md`
- `AI_CONTROL/01_CURRENT_STATE.md`
- `AI_CONTROL/02_CURRENT_TASK.md`
- `AI_CONTROL/03_WORKING_RULES.md`
- `AI_CONTROL/04_SESSION_HANDOFF.md`
- `AI_CONTROL/05_PROJECT_REFERENCE.md`
- `AI_CONTROL/06_STRATEGIC_REVIEW_2026-04-22.md`

### Purpose of each file

- `00_PROJECT_CANONICAL.md` — project identity and canonical model
- `01_CURRENT_STATE.md` — current state of the live system
- `02_CURRENT_TASK.md` — immediate next work
- `03_WORKING_RULES.md` — how to work on the project
- `04_SESSION_HANDOFF.md` — latest session continuity
- `05_PROJECT_REFERENCE.md` — this file, for historical/reference context
- `06_STRATEGIC_REVIEW_2026-04-22.md` — distilled conclusions from the external AI strategic review

---

## Historical synthesis and strategy documents

The deeper strategic and historical reasoning for the project is preserved under:

- `_archive/docs/PROJECT_SYNTHESIS/`

This includes:

- `00_RAW_AI_RESPONSES/` — raw AI analyses and exploratory thinking
- `01_COMPARISON/` — comparison and evaluation work
- `02_FINAL_SYNTHESIS/` — consolidated synthesis documents
- `03_DECISION_MEMO/` — strategic decision records
- `04_EXECUTION_ALIGNMENT/` — execution planning
- `05_SUPPORT_NOTES/` — prompts, notes, reviews, follow-up context

### Purpose

These explain **why** past decisions were made.

### Rule

Do not treat these as daily operational instructions. Use them only when strategic history or rationale is needed.

---

## External AI review process (2026-04-22)

A separate external AI review process was completed outside the repo using a dedicated review pack.

That process gathered analysis from multiple AI systems and produced:

- raw review responses
- a comparison document
- a decision memo
- a final synthesis

These external review artefacts were intentionally kept **outside the live repo**.

### Reason

The live repository should contain only the distilled strategic conclusions, not the full raw review archive.

### Result

The important conclusions from that review were folded back into the live project truth via:

- `AI_CONTROL/01_CURRENT_STATE.md`
- `AI_CONTROL/02_CURRENT_TASK.md`
- `AI_CONTROL/04_SESSION_HANDOFF.md`
- `AI_CONTROL/06_STRATEGIC_REVIEW_2026-04-22.md`
- `CHANGELOG.md`

---

## Multi-AI workflow background

The project has used multiple AI systems across its earlier strategic phases.

### Purpose of that workflow

- challenge assumptions
- compare options
- preserve decision reasoning
- avoid rediscovering the project from scratch

### Result

The strongest conclusions from those earlier phases were consolidated into:

- the active control layer
- the live repo structure
- the current narrow MVP direction

The old raw and synthesis materials are now historical context, not active instruction.

---

## Archive locations and meaning

### `_archive/control_layer/old_ai_control/`

Older control-layer files that were superseded by the cleaned active control layer.

### `_archive/docs/PROJECT_SYNTHESIS/`

Historical strategic reasoning, AI analysis, and project synthesis.

### `_archive/admin/GITHUB_ADMIN/`

Archived GitHub/admin planning material.

### `_archive/quarantine/old_quarantine/`

Legacy or reference-only code and materials that were intentionally removed from the active project surface.

### `_archive/ai_bundles/`

Old upload/export bundles used for earlier AI workflows and handoffs.

---

## How to use this file

Read this file when you need to understand:

- how the project evolved
- what older naming conventions meant
- where archived materials now live
- how historical reasoning is organised
- what kinds of materials exist outside the active control layer
- how the external AI review work relates to the live repo

Do **not** use this file to decide the current task or current live status.

For that, use:

- `AI_CONTROL/01_CURRENT_STATE.md`
- `AI_CONTROL/02_CURRENT_TASK.md`
- `AI_CONTROL/06_STRATEGIC_REVIEW_2026-04-22.md`

---

## Important reminders

- Do not broaden scope based on historical material alone.
- Do not restore archived or quarantined code blindly.
- Do not treat old repo names as current project identity.
- Do preserve archive material, because it explains earlier decisions.
- Do keep raw external review artefacts outside the live repo unless there is a specific reason to import them.
- Do rely on the active control layer for current truth.

---

## Summary

This file exists to preserve continuity without polluting the active operational layer.

It helps future sessions, tools, and AIs understand:

- where the project came from
- how it changed
- where old materials were moved
- how to distinguish live files from historical ones
- how the external AI review relates to the live project without becoming a second truth system


---

# FILE: AI_HANDOVER_PACK/source_files/AI_CONTROL/08_OHL_SURVEY_OPERATIONAL_STANDARD.md

# OHL Survey & Data Acquisition — Operational Standard

## Reference: OPS-SUR-001 | Status: Draft consolidated master standard

## Scope

UK distribution overhead networks, typically LV, 11kV and 33kV wood-pole and associated support systems.

## Source

This document was provided by the project owner based on direct field and office experience of UK OHL survey-to-design workflows. It is a consolidated working standard combining statutory context, common field practice and company-standard survey requirements.

## Purpose in this project

This document is the domain authority for what a complete survey should contain and what the tool should check for. All QA logic, evidence gates, completeness assessments, and severity decisions should be grounded in this standard.

## Key sections for tool development

- Section 1: Purpose of the surveyor's role — the surveyor captures the physical truth of the route
- Section 2: Core objective — the survey must support route validation, clearance assessment, structural assessment, stay checks, conductor specification, access planning, and clean handoff into design software
- Section 3: Division of labour — field captures location/geometry/condition/constraints/proposed intent; office applies structural loading, sag-tension, clearance validation, design optimisation
- Section 8: Master data list — the full list of what may need to be captured (8.1 through 8.10)
- Section 9: Critical missing links — crossing sketches, phase identification, stay insulators, ground-line condition
- Section 12: Final consolidated master list — quick reference for all capture categories

## Critical principle

"The survey is not just about asset logging. It is about collecting enough structured evidence that designers can run clearance, strength, sag, angle, stay and replacement decisions properly and safely."

## Full document

The complete operational standard text is maintained separately. This control file records its existence and purpose within the project.


---

# FILE: AI_HANDOVER_PACK/source_files/AI_CONTROL/09_PROJECT_ORIGIN_AND_FIELD_NOTES.md

# Project Origin — Executive Summary and Field Notes

## Purpose

This document preserves the original reasoning, real-world observations, and workflow documentation that explain why Unitas GridFlow exists. It was written by the project owner based on direct experience of both the survey and design sides of UK overhead line work.

This is a primary source document. All product decisions should be checked against it.

---

## Executive Summary

This project exists because repeated real operational observation showed a gap in UK electricity network overhead line work: the point where field survey information becomes office design input.

The current workflow delivers designs, but it does so in a fragmented, manual, and inconsistent way, relying on:

- Handwritten notes/sketches that contain critical design context but are not tied to structured records
- Excel/spreadsheet "bridge" steps (D2D) to clean and reshape survey exports
- Delayed handovers (weekly cadence, USB-style physical transfer)
- Manual QA that happens late in the process
- CAD being used as an error detector rather than a clean production stage

The project is a fresh-start workflow modernisation effort: create a structured gate between survey and design that improves input quality early, reduces rework, and produces cleaner downstream outputs.

**One-line definition:** A survey-to-design validation, QA, compliance, and workflow automation layer for electricity network design (pre-CAD).

---

## 1. How the idea started

Direct exposure to the survey/planning/design chain while working in the field made one thing clear: the biggest friction often is not engineering difficulty — it is the handoff and interpretation layer between field capture and office design.

The same pattern repeats:

- Site reality is captured partly as coordinates/measurements
- But much of the meaning is captured as informal notes, sketches, photos, and memory
- Office teams then spend time re-interpreting and repairing inputs before design can begin

That repeated waste and risk is the core reason this project exists.

---

## 2. The current real-world workflow

### Pipeline

```
Field Survey → Data Cleaning / D2D → Engineering Design (PoleCAD) → CAD Finalisation (AutoCAD) → Submission
```

This project targets the weak link: **Field Survey → Design-ready inputs** (and the D2D bridge).

### Stage 1 — Field Survey

**Equipment observed:**
- Trimble GNSS/GPS (R10 receiver, TSC3 controller)
- Leica kit (mentioned in broader workflow)
- Paper maps, handwritten notes, sketches, photos

**What gets captured:**
- Pole locations (easting/northing or lat/lon)
- Span distances
- Heights
- Ground clearance observations
- Conductor details
- Obstacles (trees, roads, buildings)
- Access notes
- Sketches and photos

**SPEN planned route input:**
- Start/end points (substation to connection site)
- Route points/coordinates
- Angle points (direction changes)
- Sometimes extra context (proposed pole types, existing BT infrastructure) but not consistently

**Field-stage issues repeatedly observed:**
- Incomplete first-pass capture
- Missing poles / intermediate poles
- Inconsistent formatting between jobs/surveyors
- Wrong sequencing
- Notes not linked to structured geometry/records
- Multiple site visits caused by incomplete initial capture
- Weekly rather than daily transfer cadence

### Stage 2 — D2D (the spreadsheet bridge)

A spreadsheet-heavy intermediate stage acting as data cleaning and pre-QA between raw survey outputs and PoleCAD.

**What D2D does:**
- Clean raw survey exports
- Reorder pole sequences
- Convert coordinates / angles
- Standardise formatting
- Identify missing values
- Flag inconsistencies before design
- Prepare structured data for PoleCAD

**Why it exists:** Because raw field output is often not design-ready, so office time gets burned on interpretation and repair.

### Stage 3 — Engineering Design (PoleCAD)

**Tools:** PoleCAD (via MicroStation environment)

**Tasks:**
- Span length validation
- Ground clearance review
- Pole height suitability
- Angle severity and stay requirement logic
- Manual adjustment based on terrain and site notes
- Structural/loading checks
- Routing interpretation

**Key boundary:** Engineering judgement remains human-led. The tool removes avoidable ambiguity and repetitive manual QA caused by poor inputs.

### Stage 4 — CAD Finalisation

After Stevie completes PoleCAD design, it goes to Kristina for AutoCAD work:
- Adding mapping layers (utilities, access paths, vegetation)
- Layering, map overlays, title blocks, layout sheets
- Roads/boundaries/watercourses/base plan alignment
- Formatting for submission

**Why this stage suffers:** Poor upstream data quality forces CAD finalisation to become a cleanup stage.

### Stage 5 — Submission

**Outputs:** PDF design packs, CAD drawings, forms/schedules, route maps, compliance reports, potentially DNO-specific submission packs.

**What goes wrong:** Late discovery of upstream issues, rework due to inconsistent data, missing information, submission packs needing amendment.

---

## 3. The real workflow as directly observed

**The USB handover:** Surveyors physically hand over a USB drive with CSV data to the designer. This happens weekly. There is no cloud sync or remote upload. This was described as "mental and really out of date."

**The physical notebook:** Surveyors provide a physical notepad with hand-drawn sketches and notes for complex areas. These are not digital.

**The D2D step:** The designer opens the CSV, manually copies key fields into a D2D spreadsheet, formats and restructures data, assigns pole numbers and angles, cleans coordinate input, then imports to PoleCAD.

**The design chain:** D2D output → MicroStation/PoleCAD (structural design) → AutoCAD (layers, mapping, presentation) → PDF/shapefile submission to Scottish Power.

**Surveyor field process observed:**
- Angles first
- Plan poles (Pol)
- EXpole (existing pole positions)
- Then export CSV from Trimble controller

---

## 4. Core pain points

- **Manual handoffs:** weekly USB handovers, notepads/sketches, spreadsheet cleanup, ad-hoc comms
- **Repeated data re-entry:** same info rewritten/rechecked across tools, causing errors and drift
- **Late QA:** expensive downstream stages detect upstream defects
- **Weak audit trail:** inconsistent checks, fragmented notes, poor traceability
- **Multiple site visits:** incomplete initial capture forces repeats
- **Presentation-stage friction:** CAD burden grows because upstream quality is weak
- **No strong automated QA layer:** issues discovered manually, late, inconsistently
- **Quality depends on individuals:** if the experienced person is off sick, nobody else can interpret the handoff

---

## 5. What the tool must do

1. **Ingest:** Accept real survey/design tabular and geospatial data, create clear job records, preserve originals
2. **Preview gate:** Fast intake check — what is in the data, completeness, obvious anomalies, coordinate sanity, sample rows + map preview
3. **QA + compliance:** Required fields, duplicate detection, coordinate sanity, span/clearance checks, angle/stay flags, DNO-specific rule logic
4. **Outputs:** Cleaned/normalised data, issue lists with severity, audit trail, design-ready exports

---

## 6. Why this will succeed

The deeper rationale: "There is a real niche operational problem here. The industry still relies on messy, semi-manual workflows. If I can build a tool that improves quality, reduces rework, speeds up design prep, and makes survey data more usable, that could become genuinely useful internally and potentially commercially."

The project serves several purposes:
- Solve a real operational pain point
- Modernise a workflow that is genuinely outdated
- Create leverage beyond ordinary employment
- Build something with niche value in a specialist infrastructure space
- Turn domain knowledge into a product or consultancy asset


---

# FILE: AI_HANDOVER_PACK/source_files/CHANGELOG.md

# Changelog

All notable changes to Unitas GridFlow are recorded here, session by session.

This file is the rolling history of what shipped. Each entry is dated.

Format loosely follows [Keep a Changelog](https://keepachangelog.com/).

---

## 2026-04-26 — Project vision defined; Phase 3A complete; control layer restructured

### Added

- **Full 6-stage product vision** documented in `AI_CONTROL/00_PROJECT_CANONICAL.md`:
  Stage 1 (QA gate), Stage 2 (D2D elimination), Stage 3 (live intake), Stage 4 (structured
  field capture), Stage 5 (designer workspace), Stage 6 (DNO submission layer).

- **`AI_CONTROL/08_OHL_SURVEY_OPERATIONAL_STANDARD.md`** — domain standard reference
  for OHL survey data fields, feature codes, and operational context.

- **`AI_CONTROL/09_PROJECT_ORIGIN_AND_FIELD_NOTES.md`** — full project origin document:
  real-world workflow observations, field-to-design chain, D2D stage analysis, core pain
  points. Primary source for all product decisions.

- **`OHL_SURVEY_OPERATIONAL_STANDARD.md`** — complete OHL survey operational standard
  document.

- **Phase 3A: real-file noise fixes** (committed `9030274`):
  - BTxing, LVxing, Road, Ignore classified as context feature codes in both
    `app/qa_engine.py` and `app/controller_intake.py` — eliminates false height
    and span QA positives for crossing/environmental observations
  - Span minimum threshold reduced 10m → 5m in all 4 DNO rulepacks — matches
    real survey density on dense NIE/SPEN jobs
  - Location field contamination cleaned in `parse_raw_controller_dump()` —
    Trimble compound codes like `Pol:LAND USE` stripped from remark/location field
  - 6 focused tests added covering all three changes
  - 175 tests passing (up from 169)

### Changed

- **Claude Desktop** is now project orchestrator (previously ChatGPT). Claude Desktop
  defines what gets built, reviews results, and manages all tools. ChatGPT is available
  for second opinions only.

- **`CLAUDE.md`** rewritten: 6-stage vision, current stage (Stage 2), tool roles
  clarified, stale batch numbering removed, superseded control files flagged.

- **`WORKFLOW_SYSTEM.md`** rewritten: Claude Desktop as orchestrator, 6-stage table,
  Stage 2 context, simplified tool role section.

- **`README.md`** rewritten: full vision framing, 175 tests, 4 real files validated,
  competitive gap statement, Stage 2 as current milestone.

### Competitive analysis

No competing product exists for the survey-to-design handoff gap in UK OHL work.
Existing tools sit upstream (field capture: Trimble, Leica) or downstream (design/CAD:
PoleCAD, MicroStation, AutoCAD). The D2D bridge layer is entirely unserved.

### Tests

- 175 passing

---

## 2026-04-24 (batch 20D — scoped design evidence gates)

### Added

- **`app/issue_model.py`**:
  - `_count_issue_codes(issues_df, codes)` — private helper counting issue codes against a set.
  - `build_evidence_gates(completeness, issues_df)` — returns 7 deterministic evidence gates:
    Position/Mapping, Structure Identity, Structural Specification, Stay Evidence,
    Clearance Design, Conductor Scope, Overall Handoff Status. Each gate has `label`,
    `status` (Strong/Partial/Weak/Missing/N/A/Blocked), and `explanation`.
  - All four span-tier `recommended_action` texts unified to one grouped string so they
    naturally deduplicate into a single actionable item in the sidebar.

- **`app/routes/api_intake.py`**:
  - `build_evidence_gates()` called after `enrich_issues()`.
  - `"evidence_gates"` stored in `meta.json` for every completed job.

- **`app/routes/map_preview.py`**:
  - `evidence_gates` read from `meta.json` and passed to the map template.

- **`app/templates/map_viewer.html`**:
  - New "Evidence Gates" section in the sidebar (after Design Readiness).
    Each gate shown as a label/status row with colour-coded status badge
    (green=Strong, amber=Partial, red=Weak/Missing, gray=N/A, dark-red=Blocked)
    and a one-line explanation below.

- **`app/routes/pdf_reports.py`**:
  - New "Evidence Gates" section in the PDF (after Design Readiness, before Top Design Risks).
    Each gate printed as bold `Label: Status` with the explanation on the next line.

- **`tests/test_issue_model.py`**:
  - 9 new tests for `build_evidence_gates` covering: gate count, required keys,
    position Missing/Strong, stay N/A and Weak, structural spec Missing,
    overall Blocked, and conductor scope Partial with span issues.

### Changed

- Span-related `recommended_action` texts (SPAN_VERY_SHORT, SPAN_SHORT,
  SPAN_BORDERLINE, SPAN_LONG) now all share one unified action text to prevent
  duplicate wording in the sidebar and PDF action list.

### Tests

- 165 passing (up from 156 at start of Batch 20D).

---

## 2026-04-24 (batch 20C — recommended designer actions)

### Added

- **`app/issue_model.py`**:
  - `build_recommended_actions(issues_df)` — groups and deduplicates `recommended_action`
    values from an enriched issues DataFrame. Returns `[{"action": str, "severity": str}, ...]`
    ordered: critical → warning → observation. Issues with no action text are excluded.
    Each unique action text appears once.

- **`app/routes/api_intake.py`**:
  - `build_recommended_actions()` called after `enrich_issues()`.
  - `"recommended_actions"` stored in `meta.json` for every completed job.

- **`app/routes/map_preview.py`**:
  - `recommended_actions` read from `meta.json` and passed to the map template.

- **`app/templates/map_viewer.html`**:
  - New "Recommended Actions" section in the sidebar (between Top Design Risks and
    Survey Completeness). Critical actions shown with red left border, warnings with amber.

- **`app/routes/pdf_reports.py`**:
  - New "Recommended Actions" section in the QA report (after Top Design Risks, before
    Replacement Pairs). Prefix `[!]` for critical, `[ ]` for warning actions.

- **`tests/test_issue_model.py`**: 8 new tests covering `build_recommended_actions`:
  - empty DataFrame
  - null action exclusion
  - output dict keys
  - deduplication of repeated action text
  - critical-before-warning ordering
  - observation-after-warning ordering
  - missing column guard
  - integration with `enrich_issues()`

156 tests passing. Pre-commit clean. No QA logic changes.

---

## 2026-04-24 (batch 20B — structured issue model)

### Added

- **`app/issue_model.py`** (new module):
  - `classify_issue(text)` — pattern-matches issue text against a priority-ordered
    lookup to return structured fields: `issue_code`, `severity`, `category`, `scope`,
    `confidence`, `is_observation`, `recommended_action`.
  - `enrich_issues(issues_df)` — adds all structured fields to an issues DataFrame
    as new columns. The existing `Issue` and `Severity` columns are preserved unchanged
    so all downstream consumers continue to work without modification.
  - Severity levels: `critical` (coordinate failures, missing columns),
    `warning` (most rule violations), `observation` (replacement pair detections).
  - Categories: `replacement_intent`, `structural_evidence`, `data_completeness`,
    `span_geometry`, `coordinate_quality`, `rulepack_validation`.
  - `is_observation: True` for replacement pair detections — separates observed
    patterns from genuine defects.
  - `recommended_action` populated for height, material, angle/stay, and span issues.

- **`app/routes/api_intake.py`**:
  - `enrich_issues()` called after `_postprocess_issues()` — structured fields now
    appear in `issues.csv` for every job.

- **`tests/test_issue_model.py`** (new file):
  - 22 tests covering: pattern matching for all issue tiers, fallback for unknown text,
    severity/category/observation correctness, `enrich_issues` column presence,
    mutation safety, and row-count invariance.

148 tests passing. Pre-commit clean. No QA logic changes.

---

## 2026-04-24 (batch 20A — trust fixes: rulepack truthfulness, span-count cleanup, controller label normalisation)

### Changed

- **`app/templates/upload.html`**:
  - Removed 6 non-existent rulepack options from the DNO dropdown:
    `NIE_LV`, `SPEN_LV`, `SSEN_LV`, `ENWL_LV`, `UKPN_LV`, `UKPN_11kV`.
  - Upload form now only offers: Auto (detect), SPEN_11kV, SSEN_11kV, NIE_11kV, ENWL_11kV.

- **`app/routes/api_rulepacks.py`**:
  - Replaced stub implementation (always returned `dno: SPEN`, empty thresholds) with
    a real implementation that derives metadata directly from the `RULEPACKS` dict in `dno_rules.py`.
  - `GET /api/rulepacks/` now returns the actual list of supported rulepack IDs (excluding DEFAULT).
  - `GET /api/rulepacks/<id>` now returns truthful `total_checks`, `check_types`, `height_range_m`,
    and `coordinate_bounds` derived from real rules. Returns 404 for unknown IDs.

- **`app/controller_intake.py`**:
  - `parse_raw_controller_dump()`: compound Trimble feature codes at col 4 (e.g. `Pol:LAND USE`,
    `EXpole:BOUNDARY`) are now normalised to their base code (`Pol`, `EXpole`).
    This prevents raw location suffixes from appearing in map popups, PDF output, and `feature_codes_found`.

- **`app/routes/api_intake.py`**:
  - Removed `"span_count": 0` from `_build_feature_collection` metadata and from `meta.update()` in `finalize()`.

- **`app/routes/map_preview.py`**:
  - Removed `"span_count": 0` from `_empty_feature_collection` fallback.

### Tests

- **`tests/test_app_routes.py`**: Added 4 new tests:
  - `test_api_rulepacks_list_returns_supported_rulepacks` — verifies correct 4 rulepacks, no DEFAULT, no unsupported
  - `test_api_rulepacks_detail_returns_real_check_data` — SPEN_11kV returns real height_range and check_types
  - `test_api_rulepacks_detail_returns_404_for_unknown` — FAKE_11kV returns 404
  - `test_upload_form_does_not_offer_unsupported_rulepacks` — HTML guard against non-existent options

- **`tests/test_controller_intake.py`**: Added 1 new test:
  - `test_parse_raw_controller_dump_normalises_compound_feature_code` — `Pol:LAND USE` → `Pol`, `EXpole:BOUNDARY` → `EXpole`

126 tests passing. Pre-commit clean.

---

## 2026-04-24 (batch 19 — field meaning and designer clarity layer)

### Changed

- **`app/controller_intake.py`**:
  - `build_circuit_summary()`: wording updated from "structural records / overhead line route"
    to "poles / support structures / surveyed route". Added `existing_count` and
    `proposed_count` to returned dict (scans structural rows for EXpole vs Pol/PRpole codes).
  - `build_top_design_risks()`: all 4 risk titles and `designer_impact` strings rewritten to
    field-aligned designer language (angle stay, height, material, short spans).
  - `build_design_readiness()`: replaced alarming "This file cannot support full design"
    headline with informative gap description stating what is absent and what is needed.

- **`app/routes/api_intake.py`**:
  - `_build_feature_collection()`: added `file_type` parameter; `file_type` now included
    in GeoJSON metadata so the JS can choose the correct ID label per file type.
  - `_build_replacement_narratives()`: added ambiguity caveat note when the same EX pole
    ID appears across multiple narratives (multi-PR/same-EX case).
  - `finalize()`: replacement cluster wording in `what_this_supports` rewritten (1 pair →
    "Proposed replacement identified near existing pole"; N pairs → "N probable replacement
    pairs detected — verify intended pairings"). Added `issue_groups` triage metadata dict
    (span_issues, replacement_clusters, missing_heights, angle_stay counts) to meta.json.
    `_build_feature_collection` call updated to pass `file_type`.

- **`app/templates/map_viewer.html`**:
  - Removed misleading "Spans: 0" stat block. Records stat centered as a single display.
  - Circuit summary section now shows sub-lines: structural/context/anchor breakdown
    and existing/proposed counts when available.
  - JS version bumped `?v=9` → `?v=10`.

- **`app/static/js/map-viewer.js`**:
  - Added `this.fileType` state, set from `meta.file_type` in `renderSummary()`.
  - Popup ID label is now contextual: "Point no." (controller file) or "Record ID" (structured).
  - Added `explainAssetType()` method mapping feature codes to plain-English descriptions
    (EXpole, PRpole, Pol, Angle, Hedge, Tree, Gate, Track, Stream).
  - Explained type shown in popup below Type line; also shown in record panel items.

- **`app/routes/pdf_reports.py`**:
  - "Issues" section renamed "Review Signals". Row data removed from main report body.
  - Added Technical Appendix (new page via `pdf.showPage()`) with full issue detail
    including raw Row data for technical reference.
  - Footer updated from "local MVP." to "Unitas GridFlow."

- **`tests/test_controller_intake.py`**:
  - Updated 3 test assertions to match new wording in `build_circuit_summary()` and
    `build_top_design_risks()`.

121 tests passing. No QA logic changes. Presentation and interpretation only.

---

## 2026-04-24 (batch 18 — real-world survey workflow reference)

### Added

- **`AI_CONTROL/07_REAL_WORLD_SURVEY_WORKFLOW.md`**: new core project truth document
  capturing how UK overhead line survey-to-design workflows actually operate.

  Sections:
  1. Purpose of this document — why this is a permanent project reference
  2. End-to-end workflow — Field survey → Trimble → export → D2D → PoleCAD → AutoCAD → submission; where problems occur and where time is wasted
  3. Field capture reality — Trimble Access + GNSS, feature-code libraries, raw export format, GPS Z vs declared height distinction
  4. Feature code meaning — EXpole (existing asset), PRpole/Pol (proposed), context features (Hedge/Gate/Track/Stream/Fence/Tree), anchor/control points; and the Unitas behaviour implication of each
  5. Replacement logic — EXpole + PRpole proximity interpretation, typical offset distances (0–5m standard replacement, 5–10m repositioned, 10–20m minor diversion, 20m+ new route), why cautious WARN is correct
  6. Survey captures vs design needs — structured gap analysis showing what CSV contains vs what PoleCAD requires; explains why D2D workload exists
  7. The D2D problem — what D2D involves, why it is error-prone, how Unitas targets this gap
  8. What designers actually care about — real acceptance/rejection signals from design experience
  9. Real-world failure points — ranked list: missing poles, short spans (duplicate vs replacement), missing structure_type, missing stay evidence, unclear connectivity, inconsistent coding
  10. What makes a survey "design-ready" — minimum requirements vs what is not required
  11. Implications for Unitas — must/must-not list grounded in sections 1–10
  12. Future direction — Phase 1 (current): post-survey validation; Phase 2: feedback loop; Phase 3: capture guidance; Phase 4: field integration

- **`CLAUDE.md`**: control layer reading order updated to include
  `07_REAL_WORLD_SURVEY_WORKFLOW.md` as item 6 (read when making QA logic or
  output language decisions).

No application code or test changes.

---

## 2026-04-24 (batch 17 — documentation alignment after audit)

### Changed

- **`AI_CONTROL/02_CURRENT_TASK.md`**: full rewrite. Removed stale Batch 2 / 67-test
  wording. Now describes current state (Batch 16 complete, 121 tests passing), lists all
  15 validation batches, frames the current task as validating the designer summary layer
  on real files, and names the likely next reference task (real-world survey workflow
  reference document).

- **`CLAUDE.md`**: updated "Current state" section to list Batches 2–16. Updated
  "Validation-phase position" to include all capabilities added through Batch 15: record-
  role classification, design readiness, EX/PR detection, angle/stay logic, asset_intent
  labels, designer summary layer.

- **`PROJECT_DEEP_CONTEXT.md`**: updated Section 1 executive summary from "narrow pre-CAD
  QA and compliance gatekeeper" to "survey-to-design workflow intelligence tool". Updated
  Section 11 framing from "pre-CAD validation and compliance layer" to "survey-to-design
  workflow intelligence layer". Added explicit "does NOT replace Trimble/PoleCAD/AutoCAD/
  designers/surveyors" constraint block to Section 8.

- **`AI_CONTROL/01_CURRENT_STATE.md`**: expanded system capabilities list to include post-
  Batch-4 features (record-role classification, design readiness, EX/PR detection,
  angle/stay, designer summary layer, interactive map). Added Batch 16 and Batch 17
  entries to "What changed recently".

- **`WORKFLOW_SYSTEM.md`**: Section 9 phase label changed from "Phase 2C complete" to
  "batches 2–16 complete — validation-led refinement active".

- **`README.md`**: "Best current framing" updated — removed "narrow productivity / QA
  layer"; added "survey-to-design workflow intelligence layer" framing and explicit "not a
  replacement for Trimble/PoleCAD/AutoCAD/designers" as a Less Realistic framing item.

- **`CHANGELOG.md`**: Batch 16 and Batch 17 entries added.

No application code or test changes.

---

## 2026-04-24 (batch 16 — project vision documentation aligned)

### Changed

- **`AI_CONTROL/00_PROJECT_CANONICAL.md`**: core identity updated from "pre-design
  validation and reliability layer" to "survey-to-design workflow intelligence tool".
  Short definition updated. IS list expanded to include record-role interpreter and design
  risk/gap identifier. "Does NOT replace" constraint block added (Trimble, PoleCAD,
  AutoCAD, designers, DNO compliance engine). System capabilities expanded with Batch 9–15
  additions. Primary users expanded (QA leads, contractors, future DNO teams). Future
  direction added (field-capture guidance, structured survey standards). Scope discipline
  section updated accordingly.

- **`README.md`**: Overview updated to "survey-to-design workflow intelligence tool". Role
  list expanded (record-role interpretation, design risks and gaps, design-readiness
  signals). "Why this project exists" section updated with multi-audience scope and
  explicit non-replacement statement.

- **`CLAUDE.md`**: project identity, short identity, and critical context updated with new
  framing and explicit "does not replace Trimble/PoleCAD/AutoCAD/designers" constraint.

- **`WORKFLOW_SYSTEM.md`**: IS list updated with record-role interpreter, design risk
  identifier; central question updated from "Can I trust this data?" to the fuller
  multi-part formulation.

No application code or test changes.

---

## 2026-04-23 (batch 15 — designer summary layer)

### Added

- **`build_circuit_summary` (controller_intake.py)**: compact job-level summary derived
  from structural count in completeness. Emits `summary_text` such as
  "15 structural records detected along a broadly continuous overhead line route."

- **`build_top_design_risks` (controller_intake.py)**: groups existing issues and
  completeness gaps into ranked risk items: angle/stay evidence missing, structural
  heights missing, material missing, short spans, proposed supports with spec gaps.
  Each item: `title`, `count`, `summary`, `designer_impact`, `severity` (WARN/FAIL).

- **`_build_replacement_narratives` (api_intake.py)**: converts each replacement-pair
  WARN into a readable sentence, e.g. "EXpole 99 is likely being replaced by nearby
  proposed support 100 (3.2m offset)." or "…at the same surveyed position."
  Uses `_REPL_OFFSET_RE` (compiled module-level regex) to extract offset from the WARN text.

- **Map side panel (map_viewer.html + map-viewer.js)**:
  - Circuit Summary block (server-side Jinja) showing the route summary sentence
  - Top Design Risks block showing up to 3 risk items with severity colouring
  - Replacement Pairs block listing individual narratives (capped at 5)
  - JS framing line: "N review signals: W warn, F fail" rendered in `#frame-summary`
  - JS cache-bust bumped to `?v=9`

- **PDF report (pdf_reports.py)**:
  - Circuit Summary section added after header, before Design Readiness
  - Top Design Risks section added after Design Readiness, before Completeness
  - Replacement Pairs section added after Completeness, before Issues

- **meta.json storage**: `circuit_summary`, `top_design_risks`, and
  `replacement_narratives` all persisted in meta.json and passed to map template.

### Tests added

- `test_build_circuit_summary_multiple_structural_returns_route_text`
- `test_build_circuit_summary_zero_structural_returns_no_structural_text`
- `test_build_top_design_risks_includes_angle_no_stay_warn`
- `test_build_top_design_risks_includes_missing_height_risk`
- `test_build_replacement_narratives_returns_readable_text_for_pair`
- `test_build_replacement_narratives_same_position_wording`
- `test_build_replacement_narratives_returns_empty_for_no_pairs`
- Test count: **121 passing** (was 114).

---

## 2026-04-23 (batch 14 — EX/PR narrative linking and warn_texts fix)

### Added

- **`asset_intent` label in GeoJSON feature properties (api_intake.py)**:
  EXpole records receive `asset_intent="Existing asset"` (derived from `structure_type`).
  Non-EXpole records that have a replacement-pair WARN receive `asset_intent="Proposed support"`.
  All other records receive `asset_intent=None`. No new engineering logic — purely presentation.

- **`warn_count` / `warn_texts` serialised into GeoJSON properties (api_intake.py)**:
  Batch 12 computed these values but never wrote them into `feature["properties"]`, making
  angle/stay WARNs invisible in the map popup. Both fields now appear in the GeoJSON output.

- **Improved replacement cluster narrative (api_intake.py `finalize` route)**:
  Cluster summary line changed from `"N replacement pairs detected — likely EX → PR design intent"`
  to `"N probable replacement pairs detected — consistent with replacement survey work"`.

- **Improved replacement-pair popup wording (map-viewer.js)**:
  `replacementLine` now reads: `"Likely replacement pair — existing asset with nearby proposed support"`.

- **`asset_intent` surfaced in popup and record panel (map-viewer.js)**:
  New `assetIntentLine` in popup (after Type row) and `intentHtml` in record panel items.

- **JS cache-bust bump**: `map-viewer.js?v=7` → `?v=8` in `map_viewer.html`.

### Tests added

- `test_build_feature_collection_expole_gets_existing_asset_intent` — EXpole → `"Existing asset"`
- `test_build_feature_collection_replacement_pair_non_expole_gets_proposed_support` — Pol with WARN → `"Proposed support"` + `relationship="replacement_pair"`
- `test_build_feature_collection_regular_pole_has_no_asset_intent` — regular Pol → `asset_intent is None`
- `test_build_feature_collection_warn_texts_populated_in_properties` — Angle WARN → `warn_count=1`, `warn_texts` populated, `issue_count=0`
- Test count: **114 passing** (was 110).

---

## 2026-04-23 (batch 13 — confidence-aware QA refinements)

### Changed

- **Short span tiers (qa_engine.py)**: short spans are no longer a flat FAIL.
  Three distance tiers now emit calibrated WARN messages:
  - `< 3m` → `"Span very short: Xm — likely duplicate or co-located pair, verify"`
  - `3–8m` → `"Span unusually short: Xm (min Ym) — verify no duplicate entry"`
  - `8–min_m` → `"Span borderline short: Xm (min Ym) — verify no missing record"`
  All tiers emit `Severity: WARN`. Replacement-pair detection is unchanged.

- **EXpole height downgrade (qa_engine.py `range` check)**: when `field="height"`,
  `structure_type` is an EXpole code, and the value is below `min_val`, the issue
  is downgraded from a standard range FAIL to:
  `"Height likely estimated / not captured (EXpole)"` with `Severity: WARN`.
  Heights above `max_val` are still emitted as standard range issues.

- **Design readiness strong summary (controller_intake.py `build_design_readiness`)**:
  when `material_pct == 0.0` (material completely absent from digital file), prepends
  `"This file cannot support full design — critical design data missing"` as the
  first reason in the design readiness output.

### Tests updated

- `test_span_distance_flags_poles_too_close` — updated to assert "Span borderline
  short" and `Severity="WARN"` (was checking "Span too short" with implicit FAIL)
- `test_span_suppression_does_not_apply_to_pol_pol` — updated to assert "Span
  unusually short" WARN (was checking "Span too short" FAIL)
- `test_span_distance_message_shows_one_decimal_precision` — updated to match new
  "Span unusually short" tier message

### Tests added

- `test_short_span_very_close_emits_warn_very_short_tier` — span < 3m → WARN
- `test_short_span_unusual_tier_emits_warn` — span 3–8m → WARN
- `test_short_span_borderline_tier_emits_warn` — span 8–min_m → WARN
- `test_expole_height_below_min_emits_warn` — EXpole height=5, min=7 → WARN
- `test_expole_height_above_max_remains_range_fail` — EXpole height=30 > max → FAIL
- `test_non_expole_height_below_min_remains_range_issue` — Pol height=5 → FAIL
- Test count: **110 passing** (was 104).

---

## 2026-04-23 (batch 12 — angle/stay evidence logic)

### Added

- **`_ANGLE_CODES` and `_STAY_EVIDENCE_CODES` frozensets in `qa_engine.py`**:
  `_ANGLE_CODES` = {"Angle", "angle", "ANGLE"}; `_STAY_EVIDENCE_CODES` covers
  "Stay", "Staywire", "Stay wire", "Stay pole" and lowercase/uppercase variants.

- **`angle_stay` check type in `qa_engine.py`**: dataset-level proximity scan.
  For each angle record, checks whether any `_STAY_EVIDENCE_CODES` record exists
  within 30m (OSGB projected), or whether the angle record's own `location`/
  remarks text contains "stay". If neither, emits a `Severity: WARN` issue with
  cautious wording: `"Angle structure with no stay evidence detected — verify
  whether stay capture is missing or not required for this job"`.

- **`angle_stay` rule added to `BASE_RULES` in `dno_rules.py`**: all four
  rulepacks now carry this rule. Files with no angle records produce no issues —
  the check silently skips.

- **`angle_no_stay_count` injected into `design_readiness`** in
  `api_intake.py`: when angle/no-stay WARNs exist, a bullet is added to
  `design_readiness.reasons` and `angle_no_stay_count` is set on the dict.

- **`warnBlock` in map popup** (`map-viewer.js`): WARN features that are not
  replacement pairs now show a "Design Notes (N):" section in amber in their
  popup, listing warn_texts from the feature properties.

- **`warnHtml` in record panel** (`map-viewer.js`): WARN feature items in the
  record panel show the first warn text (truncated to 65 chars) for non-
  replacement-pair records.

- **`[WARN]` prefix in PDF** (`pdf_reports.py`): the issues table reads the
  `Severity` column from issues.csv and prepends `[WARN] ` for WARN issues.

- **JS version bumped** (`map_viewer.html`): `?v=7` to force cache refresh.

### Tests

- `test_angle_no_stay_emits_warn` — Angle + Pol at 111m, no stay → 1 WARN
- `test_angle_with_stay_within_proximity_no_warn` — Angle + Stay at 20m → 0
- `test_angle_with_stay_beyond_proximity_emits_warn` — Stay at 67m (>30m) → 1 WARN
- `test_angle_stay_remarks_evidence_suppresses_warn` — "stay installed 3m west"
  in location → 0 issues
- `test_angle_stay_no_issue_for_pol_only_file` — Pol-only file → 0 issues
- Test count: **104 passing** (was 99).

---

## 2026-04-23 (validation batch 11 — EX/PR replacement cluster detection)

### Added

- **Replacement pair detection**: adjacent structural records where exactly one
  is an EXpole code (EXpole, expole, EXPOLE) and the distance is below the
  minimum span threshold are now classified as replacement pairs rather than
  flagged as "Span too short" FAILs. These emit a `Severity: WARN` issue:
  `"Replacement pair detected (EX → PR, X.Xm offset)"`.

- **`_is_replacement_pair()` helper in `qa_engine.py`**: XOR logic — fires when
  exactly one of the two adjacent structure_type values is an EXpole code.
  Covers both EX→PR and PR→EX orderings.

- **`_EXPOLE_CODES` constant in `qa_engine.py`**: frozenset of EXpole variants
  used by the replacement pair helper.

- **WARN severity on issues**: WARN issues carry `{"Severity": "WARN"}` in the
  issue dict. Code that doesn't know about the field defaults to FAIL treatment.

- **WARN tracking in `_collect_per_row_issues`**: WARN issues are accumulated
  separately in `warn_count`/`warn_texts` alongside the existing `count`/`texts`
  (FAIL) keys.

- **WARN marker status**: map features where only WARN (no FAIL) issues exist
  receive `qa_status = "WARN"`, shown in amber on the map.

- **`relationship` property on map features**: features involved in a replacement
  pair get `"relationship": "replacement_pair"` in their GeoJSON properties.

- **Map popup replacement line**: when `props.relationship === 'replacement_pair'`,
  the popup shows "⚠ Replacement Pair (Existing → Proposed)" in amber.

- **Design Readiness replacement bullet**: when replacement clusters are detected,
  `design_readiness.what_this_supports` gains a bullet
  `"N replacement clusters detected — likely EX → PR design intent"`, and
  `replacement_cluster_count` is set on the design readiness dict.

- **Actual `warn_count` in map metadata**: `feature_collection.metadata.warn_count`
  now reflects the real count of WARN-status features rather than always being 0.

### Tests

- `test_replacement_cluster_detection` — EXpole + Pol at 3.3m → WARN
  "Replacement pair detected", no FAIL; Severity column contains "WARN"
- `test_span_suppression_does_not_apply_to_pol_pol` — Pol + Pol at 3.3m →
  FAIL "Span too short", no replacement pair WARN
- Test count: **99 passing** (was 97).

---

## 2026-04-23 (validation batch 10 — consistency and threshold cleanup)

### Fixed

- **Record count consistency**: `meta["pole_count"]` now uses
  `completeness.total_records` (all rows in the file) rather than the count of
  map-visible features (which excluded anchor rows). The PDF header "Record
  count" and the Survey Completeness "Total records" line now show the same value.
  The structural/context/anchor composition totals sum to that same value.

- **Span threshold wording**: span distance issue messages now use `{dist:.1f}m`
  (1 decimal place) instead of `{dist:.0f}m`. A 9.6 m span previously displayed
  as "Span too short: 10m (min 10m)", which looked like a false positive. It now
  displays as "Span too short: 9.6m (min 10m)", making the threshold comparison
  unambiguous.

- **Coverage labels**: `_coverage_rating()` threshold for "Partial" changed from
  `> 20%` to `> 0%`. Any nonzero coverage is now "Partial" rather than "Missing",
  so a file where 15% of structural records have height recorded no longer shows
  the same "Missing" label as a file with 0% height data. Only truly absent data
  (0%) produces "Missing".

### Changed

- `build_design_readiness()` adds up to two more items to `what_this_supports`:
  - "identifying pole types and network roles along the route" when
    `structure_type` coverage exceeds 70%
  - "locating N environmental and crossing features along the route" when
    context records (Gate, Hedge, Track, etc.) are present in the file

### Tests

- `test_coverage_rating_partial_for_low_nonzero_coverage` — 5%, 15%, 20%, 0.1%
  all return "Partial" with the new threshold
- `test_coverage_rating_missing_only_at_zero` — 0% returns "Missing"
- `test_coverage_rating_strong_above_threshold` — >70% returns "Strong"
- `test_span_distance_message_shows_one_decimal_precision` — span issue text
  contains a decimal point, confirming `.1f` format is in effect
- `test_meta_pole_count_matches_completeness_total_records` — controller dump
  with an anchor row: meta.pole_count equals completeness.total_records (3),
  not the map-visible feature count (2)
- Updated `test_build_design_readiness_partially_ready_missing_structural`:
  assertion changed from `"Missing"` to `"Partial"` for Structural Data
  (structural_pct = 9.1% is nonzero → "Partial")
- Test count: **97 passing** (was 92).

---

## 2026-04-23 (validation batch 9 — record-role classification + anchor handling + role breakdown UI)

### Added

- `_classify_role()` and `classify_record_roles()` in `app/controller_intake.py`.
  Assigns every row one of three roles: `structural` (Pol, Angle, EXpole, etc.),
  `context` (Hedge, Tree, Gate, Track, Stream, etc.), or `anchor` (grid reference
  control points like GB_Kelso / GB_Selkirk — identified by absent structure_type and
  non-numeric pole_id).

- `_STRUCTURAL_CODES` and `_CONTEXT_CODES` frozensets in `app/controller_intake.py`,
  mirroring `app/qa_engine.py` so both modules share consistent classification.

- `_df_no_anchor` filter at the top of `run_qa_checks()` in `app/qa_engine.py`.
  Anchor rows are excluded from every QA check except `span_distance`, which needs
  them to detect chain breaks at reference locations.

- Anchor chain-reset logic in the `span_distance` handler: when an anchor row is
  encountered `prev_e / prev_n` are cleared to `None`, preventing cross-anchor span
  comparisons (e.g. the ~20 km jump from a GB_Kelso reference point to the first
  survey pole no longer fires a false span-too-long issue).

- `what_this_supports` positive list in `build_design_readiness()` output, answering
  what the file enables rather than only listing gaps.

- Structural/context/anchor counts (`structural_count`, `context_count`,
  `anchor_count`) in `build_completeness_summary()` output.

- `structural_fields` per-field coverage in completeness summary — height/material
  capture rates are now calculated against structural records only, so a Gate with
  height 1.6 m does not pollute the structural height coverage percentage.

- `#role-breakdown` div in `app/templates/map_viewer.html` showing "■ N structural
  · ■ N context · ◇ N anchor" inline in the map side panel.

- `what_this_supports` bullet list under Design Readiness in the map side panel and
  in PDF reports.

- Composition line in the Survey Completeness section of the PDF report
  (e.g. "Composition: 40 structural, 12 context, 2 anchor").

- JS cache version bumped to `?v=6` in `map_viewer.html`.

### Changed

- `_CONTEXT_FEATURE_CODES` in `app/qa_engine.py` and the `CONTEXT_FEATURE_CODES` set
  in `app/static/js/map-viewer.js` expanded to include Gate, Track, and Stream (all
  three case variants). Previously these codes were not listed, causing Gate/Track/
  Stream rows to be evaluated as unknown structural features and triggering false
  height FAILs.

- `api_intake.py` finalize route now calls `classify_record_roles(df)` after CRS
  conversion, propagates role counts into map metadata, and skips anchor rows when
  building the GeoJSON feature collection (anchor rows are not map markers).

- `build_design_readiness()` uses `structural_fields` (structural-only coverage) for
  height and material percentage calculations instead of whole-file coverage.

### Tests

- `test_anchor_row_excluded_from_required_check` — anchor row with absent height
  produces no issue; structural row with absent height is still flagged.
- `test_span_distance_resets_chain_at_anchor_row` — anchor row between two poles
  8.9 km apart breaks the chain; no span-too-long issue is raised.
- `test_gate_track_stream_no_height_range_fail` — Gate, Track, Stream below minimum
  height produce no FAIL with `structural_only: True`; Pol below minimum still flags.
- Test count: **92 passing** (was 89).

---

## 2026-04-23 (validation batch 8 — strict feature-aware QA + issue deduplication)

### Changed

- `range` check handler in `app/qa_engine.py` now respects a `structural_only: True`
  flag on rules. When set, rows where `structure_type` is a context feature (Hedge,
  Tree, Wall, Fence, Post) are skipped entirely — they never trigger height-out-of-range
  or any other structural range failure.

- `required` check handler applies the same `structural_only` gate. A Hedge or Tree
  row with no height value no longer triggers "Missing required field: height".

- All height `range` rules across BASE_RULES and all four rulepacks (SPEN, SSEN, NIE,
  ENWL) now carry `"structural_only": True`. The base generic rule (7–25m) and each
  rulepack-specific rule (7–20m) both scope to structural features only.

- `required: height` in BASE_RULES now carries `"structural_only": True`.

### Added

- `_is_context_row(row, has_structure_type)` helper in `app/qa_engine.py` — centralises
  the context-feature check used by the `structural_only` gate.

- `_deduplicate_issues(issues)` function in `app/qa_engine.py`. Normalises issue text
  by stripping the parenthesised parameter suffix (e.g. "(7-25)" from "height out of
  range (7-25)"), then deduplicates by (row_index, normalised_prefix) key. This
  collapses the duplicate height-range issues that BASE_RULES and a rulepack both fire
  for the same structural record. Applied at the end of `run_qa_checks` before
  returning the DataFrame.

- 3 new tests in `tests/test_qa_engine.py`:
  - `test_structural_only_range_skips_context_features`
  - `test_structural_only_required_skips_context_features`
  - `test_deduplication_collapses_same_logical_issue_per_row`

- Updated `test_import_finalize_returns_success_for_valid_job` expected issue count
  from 11 to 10, reflecting that the duplicate height-range issue for P-1003 (height
  28.0, which previously fired both 7–25 and 7–20 rules) is now correctly deduplicated
  to one issue.

---

## 2026-04-23 (validation batch 7 — feature-aware QA + record inspection panel)

### Changed

- `span_distance` in `app/qa_engine.py` now skips context-only feature codes (Hedge,
  Tree, Wall, Fence, Post) when measuring spans between structural records. Spans
  bridge correctly over context markers — a Hedge between two poles no longer produces
  a false "span too short" issue. Non-pole records are excluded; pole-to-pole spans
  are still checked including when a context feature sits between them.

- Span distance issue text changed from "between consecutive poles" to "between
  structural records" to reflect mixed-feature survey files accurately.

- Added `_CONTEXT_FEATURE_CODES` frozenset constant to `app/qa_engine.py` to define
  which surveyor feature codes represent environmental/contextual markers.

- Map marker popup now shows "Height: not captured" (muted style) for structural
  (non-context) features where height is absent, rather than silently omitting the
  field. This immediately surfaces height gaps without requiring the designer to open
  the issues list. Context features (Hedge etc.) do not show height at all.

### Added

- Record inspection panel in map view side panel. Clicking PASS / WARN / FAIL now
  also opens a scrollable record list below the filter note, showing each record's ID,
  feature type, status, key fields (height, material, remarks if present), and first
  issue description for FAIL records. Each list item is clickable to open that
  marker's popup and zoom to it on the map.

- "Records" stat block is now clickable (`#all-records-btn`). Clicking it clears any
  active status filter and shows all records in the inspection panel.

- `_showRecordPanel` / `_hideRecordPanel` / `bindAllRecordsButton` methods added to
  `MapViewer` class in `map-viewer.js`. `setFilter` now calls show/hide automatically.

- CSS: `.record-item` (compact list card with coloured left border by status),
  `#all-records-btn` hover style.

### Tests

- 86 passing (up from 84). Added: `test_span_distance_skips_context_feature_codes`,
  `test_span_distance_context_feature_bridges_span_to_next_structural_record`.

---

## 2026-04-23 (validation batch 6 — explain, filter, and clarify)

### Added

- `_collect_per_row_issues()` in `app/routes/api_intake.py` replaces
  `_count_issues_per_row`. Now returns `{row_index: {"count": int, "texts": list[str]}}`
  storing up to 3 issue description strings per row (truncated to 80 chars each).

- `issue_texts` property on each GeoJSON feature in `map_data.json`. Allows map
  popups to display the actual issue descriptions without any additional requests.

- Interactive pass/fail filter on map view. Each status block (PASS / WARN / FAIL)
  in the side panel is now a clickable button (`status-filter-btn`). Clicking a status
  filters the map to show only markers of that status. Clicking again resets to all.
  Active filter is highlighted with a CSS `filter-active` style.

- Overlapping marker detection in `map-viewer.js`. After rendering, detects coordinates
  that share the same position to 4 decimal places and appends a note to the issue-note
  element if any are found.

- `filter-note` element below the status grid shows the current filter state and
  record count.

### Changed

- Map view side panel: "Poles" stat label changed to "Records" (more accurate for
  mixed-feature files including angle poles, hedge markers, etc.).

- PDF QA report: "Pole count:" label changed to "Record count:".

- `build_design_readiness()` reason strings rewritten to be design-consequence-focused.
  e.g. "clearance and sag-related design checks not fully supported from this file —
  height data incomplete (18.2% coverage)" instead of "height data incomplete (18.2%)".

- Map marker popup updated to show actual issue descriptions (up to 3) with a "… and N
  more" note, replacing the previous plain issue count.

- JS version bumped: `map-viewer.js?v=3` → `?v=4`.

### Tests

- 84 passing (up from 79). Added: `test_collect_per_row_issues_returns_count_and_texts`,
  `test_collect_per_row_issues_truncates_to_three_texts`,
  `test_build_feature_collection_includes_issue_texts`,
  `test_map_view_shows_records_label_not_poles`,
  `test_import_finalize_includes_issue_texts_in_map_data`.

---

## 2026-04-23 (validation batch 5 — design readiness + survey coverage + enhanced map popups)

### Added

- `build_design_readiness(completeness)` in `app/controller_intake.py`. Derives a
  design readiness verdict (NOT READY / PARTIALLY READY / LIKELY READY) and
  per-category survey coverage ratings (Strong / Partial / Missing) entirely from
  existing completeness data. No new inputs. Categories: Position & Identity,
  Structural Data, Electrical Configuration, Stability & Safety, Clearances,
  Environment & Access. Position & Identity rating uses the best coordinate field
  (lat preferred, then easting) averaged with pole_id and structure_type coverage.
  Structural Data rating uses the mean of height and material coverage.
  Always-absent categories (Electrical etc.) are shown as Missing, reflecting what
  real survey digital files do not contain, without penalising the verdict.

- Design Readiness section in map view side panel (Jinja2 server-side). Shows
  verdict in a colour-coded label (green/amber/red), a bullet list of reasons, and
  the full Survey Coverage category breakdown with colour-coded ratings.

- Design Readiness section in PDF QA report. Shows verdict, reasons, and survey
  coverage category table; page-overflow guard included.

- `_count_issues_per_row(issues_df)` in `app/routes/api_intake.py`. Replaces
  `_infer_issue_rows` in `_build_feature_collection`; returns a dict mapping
  row_index → issue_count so each GeoJSON feature now carries an `issue_count`
  property rather than just a binary PASS/FAIL flag.

- Enhanced map marker popups in `app/static/js/map-viewer.js`. Each popup now
  shows: pole_id, structure_type / feature code, height (with "m" unit), material,
  remarks/location (if distinct from id), easting/northing (or lat/lon if no grid
  coords), and issue count (highlighted red when > 0). Fields absent from the
  record are omitted cleanly.

- `design_readiness` stored in `meta.json` and returned in the finalize route
  JSON response alongside `completeness`.

- 5 new focused tests (3 unit, 2 route-level):
  - `test_build_design_readiness_likely_ready`
  - `test_build_design_readiness_partially_ready_missing_structural`
  - `test_build_design_readiness_not_ready_missing_position`
  - `test_pdf_report_includes_design_readiness_when_present`
  - `test_map_view_includes_design_readiness_verdict`

### State at end of session

- 79 tests passing (up from 74).
- Map view and PDF both surface design readiness verdict, reasons, and survey
  coverage categories alongside existing completeness detail.
- Each map marker popup shows full record detail including issue count.
- design_readiness persisted in meta.json and returned in finalize response.

---

## 2026-04-23 (validation batch 4 — rulepack auto-detection + completeness surfacing)

### Fixed

- Wrong rulepack applied to NIE/TM65 uploads when no explicit DNO was supplied.
  `api_intake.py` finalize route now tracks `explicit_dno` separately from
  `requested_dno`. After `convert_grid_to_wgs84()` writes the `_grid_crs` column,
  if no explicit DNO was supplied and the detected CRS is `EPSG:29900` (TM65) or
  `EPSG:2157` (ITM), `requested_dno` is switched to `NIE_11kV` and
  `rulepack_inferred: true` is recorded in both `meta.json` and the JSON response.
  The SPEN_11kV default is only retained for non-Irish-grid uploads with no explicit DNO.

### Added

- Completeness summary surfaced in map view side panel. `map_preview.py` `map_view`
  route now reads `meta.json` and passes the `completeness` dict to the Jinja2
  template. `map_viewer.html` renders a "Survey Completeness" section below the
  action buttons: total records, Grid CRS (if detected), per-field coverage with
  red percentage for partial fills and green tick for 100%, and feature codes found.
  No changes to `map-viewer.js`.

- Completeness summary surfaced in PDF QA report. `pdf_reports.py` reads the
  `completeness` key from `meta.json` and renders a "Survey Completeness" section
  after the job header block: total records, position status, Grid CRS, field
  coverage table, and feature codes found. Page overflow guard added for long field
  lists.

- `rulepack_inferred` field added to `meta.json` and finalize route JSON response.

- 4 new focused tests in `tests/test_app_routes.py`:
  - `test_import_finalize_infers_nie_11kv_for_irish_grid_without_explicit_dno` —
    TM65 raw dump with no explicit DNO returns `NIE_11kV` and `rulepack_inferred: true`.
  - `test_import_finalize_preserves_explicit_dno_over_crs_inference` — explicit
    `dno: "SPEN_11kV"` in request body overrides CRS-based inference.
  - `test_pdf_report_includes_completeness_when_present` — PDF route renders
    completeness section when `meta.json` contains completeness data.
  - `test_map_view_passes_completeness_to_template` — map view route passes
    completeness dict to the template context.

### State at end of session

- 74 tests passing (up from 70).
- NIE/TM65 uploads now receive NIE_11kV rulepack automatically when no explicit DNO supplied.
- Completeness summary visible in both map view side panel and PDF QA report.
- Rulepack inference traceable via `rulepack_inferred` flag in meta.json and API response.

---

## 2026-04-23 (docs alignment — WORKFLOW_SYSTEM.md integration)

### Added

- `WORKFLOW_SYSTEM.md` — defines the operating model across all AI tools. Records
  tool roles (human domain authority, ChatGPT orchestrator, Claude Code execution
  engine, Claude Desktop verification layer), source of truth hierarchy, core
  workflow loop, and current phase context.

### Changed

- `AI_CONTROL/00_PROJECT_CANONICAL.md`: core principle statement added (trusted gate,
  reliability/clarity/design-readiness framing from WORKFLOW_SYSTEM.md); WORKFLOW_SYSTEM.md
  and `app/controller_intake.py` added to project structure and key source files;
  phase status updated to include validation batches 2 and 3; navigation pointer added.

- `README.md`: test count corrected (38 → 70); completed steps updated to include
  validation batches 2 and 3; stale limitation removed ("intake centered on structured
  CSV only" — raw controller dumps now supported); WORKFLOW_SYSTEM.md added to project
  structure section.

- `AI_CONTROL/04_SESSION_HANDOFF.md`: rewritten to reflect current state (batch 3
  complete, WORKFLOW_SYSTEM.md added, 70 tests passing).

- `CLAUDE.md`: WORKFLOW_SYSTEM.md added to optional session-start reads; core principle
  statement and tool-role clarification added to project identity section.

### State at end of session

- 70 tests passing. No code changes. All docs aligned with current repo truth.
- Control layer, README, CLAUDE.md, and WORKFLOW_SYSTEM.md consistent.

---

## 2026-04-23 (validation batch 3 — coord_consistency fix + QA noise suppression)

### Fixed

- `coord_consistency` false positives for non-OSGB grid-derived files. The check
  reprojects lat/lon to EPSG:27700 and compares against declared easting/northing;
  when `_grid_crs` is set to a non-OSGB CRS (TM65 EPSG:29900, ITM EPSG:2157),
  easting/northing are in a different coordinate space and the comparison always
  produces a large apparent mismatch. Any real NIE job would have generated a false
  positive on every pole. Guard added to `run_qa_checks` in `app/qa_engine.py`:
  if `_grid_crs` is present and is not `EPSG:27700`, the `coord_consistency` block
  is skipped entirely. Existing OSGB27700 behaviour unchanged.

### Added

- `filter_rules_for_controller(rules)` in `app/dno_rules.py`. Removes checks that
  produce noise rather than signal for raw controller dump files: `required` and
  `allowed_values` for `material` (absent from the format), `allowed_values` for
  `structure_type` (surveyor feature codes such as Angle, Pol, Hedge are valid but
  do not match schema values), and `dependent_allowed_values` (structure_type →
  material mapping is meaningless when material has no digital representation).
  Meaningful checks preserved: span distance, unique_pair, coordinate bounds, regex,
  required pole_id.

- Filter applied in `app/routes/api_intake.py` finalize route when
  `file_type == "controller"`. Structured CSV path is unchanged.

- 3 new focused tests:
  - `test_coord_consistency_skips_for_non_osgb_grid_crs` — TM65 file with
    `_grid_crs=EPSG:29900` produces no coord_consistency issues.
  - `test_coord_consistency_still_runs_for_explicit_osgb27700_grid_crs` — mismatch
    is still caught when `_grid_crs=EPSG:27700`.
  - `test_import_finalize_controller_dump_suppresses_noise_issues` — end-to-end
    route test confirming no material, structure_type, or coord mismatch issues in
    issues.csv for a TM65 raw dump through NIE_11kV.

### State at end of session

- 70 tests passing (up from 67).
- NIE real jobs no longer produce coord_consistency false positives.
- Controller dump QA output contains only meaningful signal.
- Structured CSV QA path unchanged.

---

## 2026-04-22 (validation batch 2 — raw controller intake + completeness tightening)

### Added

- `is_raw_controller_dump(first_line)` in `app/controller_intake.py`. Detects GNSS
  controller metadata-header format (`Job:X,Version:Y,Units:Z`) by inspecting the
  first line before `pd.read_csv` is called. This format cannot be detected from
  column names after a normal `read_csv` because the metadata row becomes the header.

- `parse_raw_controller_dump(path)` in `app/controller_intake.py`. Parses raw GNSS
  controller dump files using Python's `csv` module (chosen over `pd.read_csv` because
  raw dumps have variable column counts per row that the pandas C parser cannot handle).
  Maps: col 0 → pole_id, col 1 → easting, col 2 → northing, col 4 → structure_type.
  Extracts inline `FeatureCode:HEIGHT` attribute → height and `FeatureCode:REMARK`
  → location. GPS instrument elevation (col 3) is intentionally NOT mapped to height
  since it records terrain elevation, not declared pole height — ensuring the
  completeness summary correctly reports partial height coverage.

- First-line format detection in `app/routes/api_intake.py`. The finalize route now
  peeks at the first line of the uploaded file and routes to `parse_raw_controller_dump`
  before falling through to the existing `pd.read_csv` + `is_controller_csv` path.

- `feature_codes_found` field in `build_completeness_summary` output. Surfaces the
  sorted list of unique structure/feature codes present in the parsed data. For
  controller dumps these are the surveyor-assigned feature codes (Angle, Pol, Hedge,
  EXpole) — the one piece of structural context digitally available. Only included
  when at least one non-null code is present.

- 8 new unit tests in `tests/test_controller_intake.py` covering: `is_raw_controller_dump`
  detection, `parse_raw_controller_dump` record count, PRS/metadata row exclusion,
  HEIGHT attribute vs GPS elevation mapping, REMARK → location mapping, feature code
  → structure_type mapping, numeric column coercion, and `feature_codes_found` in
  completeness summary.

- 1 end-to-end integration test in `tests/test_app_routes.py` (`test_import_finalize_handles_raw_controller_dump`).
  Sends a minimal raw controller dump matching 28-14 513 format through the full `/api/import/<job_id>`
  route and confirms: `ok=True`, `file_type="controller"`, correct per-field completeness,
  `feature_codes_found`, and output files written.

### Validated

- Real-file output simulated via representative test fixture matching job 28-14 513
  format. With the raw parser in place, `build_completeness_summary` would produce:
  total_records=11, height coverage=2/11 (18.2%), location/remarks=2/11 (18.2%),
  material=0/11 (0%), structure_type=11/11 (100%), grid_crs_detected=EPSG:29900,
  feature_codes_found=[Angle, EXpole, Hedge, Pol]. This matches the VALIDATION_ANALYSIS
  intent exactly.

### State at end of session

- 67 tests passing (up from 38).
- Raw GNSS controller dump format now parseable end-to-end.
- Completeness summary surfaces record count, position status, CRS, per-field coverage,
  and feature codes found.
- No changes to QA rules, map output, or PDF generation.

---

## 2026-04-22 (strategic review)

### Added

- `AI_CONTROL/06_STRATEGIC_REVIEW_2026-04-22.md` — distilled strategic conclusions from the external AI review process.

### Changed

- `AI_CONTROL/00_PROJECT_CANONICAL.md` updated to reflect the current phase more accurately and incorporate the new validation-led direction.

- `AI_CONTROL/01_CURRENT_STATE.md` updated to reflect the main unresolved risk: lack of real-world validation.

- `AI_CONTROL/02_CURRENT_TASK.md` rewritten so the next phase is validation-led rather than feature-led.

- `AI_CONTROL/03_WORKING_RULES.md` updated to formally prioritise validation evidence over abstract feature expansion.

- `AI_CONTROL/04_SESSION_HANDOFF.md` updated to record the outcome of the external AI review process.

- `AI_CONTROL/05_PROJECT_REFERENCE.md` updated to document how the external AI review work relates to the live repo without becoming a second truth system.

### State after review

- Project remains active and worth continuing.

- Best current framing remains internal tool / consultancy leverage asset.

- Main next step is testing the current tool on real survey files from real jobs.

- Main unresolved question is now whether the current tool provides meaningful value on real survey files for real users.

---

## 2026-04-22 (Phase 2A)

### Added

- Column name normalisation in `app/routes/api_intake.py`. Headers are now stripped,

  lowercased, and have spaces replaced with underscores before alias mapping runs.

  This handles capitalised exports (`Latitude`, `Structure Type`, `Asset ID`, etc.)

  automatically without any manual reformatting.

- Extended alias lists in `_normalize_dataframe`:
  - `pole_id`: adds `id`, `pole_ref`, `asset_ref`

  - `height`: adds `ht_m`

  - `structure_type`: new — covers `pole_type`, `type`

  - `material`: adds `mat`

  - `location`: adds `site`, `site_name`, `description`

  - `lon`: adds `long`

  - `easting`: new — covers `os_easting`, `grid_easting`, `grid_e`

  - `northing`: new — covers `os_northing`, `grid_northing`, `grid_n`

- Three new tests in `tests/test_api_intake.py`: capitalised headers, common

  abbreviations, OSGB aliases.

### State at end of session

- 38 tests passing.

- Column normalisation handles the most common real-world survey CSV variants.

- No changes to QA engine or rulepacks (Phase 1 closed).

---

## 2026-04-22 (Phase 1 closed)

### Changed

- `AI_CONTROL/02_CURRENT_TASK.md` rewritten: Phase 1 formally closed, Phase 2

  (input schema breadth) defined as the current task.

- `AI_CONTROL/04_SESSION_HANDOFF.md` updated to reflect Phase 1 closure and Phase 2

  entry point.

### State

- Phase 1 complete: 10 QA check types, 4 DNO rulepacks, 35 tests passing.

- Phase 2 next: normalise incoming CSV column names in `app/routes/api_intake.py`.

---

## 2026-04-22 (continued)

### Added

- `ENWL_11KV_RULES` rulepack in `app/dno_rules.py`. Covers Electricity North West

  licence area (Lancashire, Cumbria, Cheshire, Greater Manchester): lat 53.3–55.0,

  lon -3.5 to -1.8. Uses same ENA TS 43-8 height range (7–20m), pole ID regex,

  paired-coord checks, material/structure-type consistency, and coord_consistency

  (100m) as existing rulepacks.

- `ENWL_11kV` entry in `RULEPACKS` dict.

- `unique_pair` check type in `app/qa_engine.py`. Flags rows where two or more poles

  share the same composite field values (applied as lat/lon pair in all DNO rulepacks).

  Skips rows with missing values. Added to all 4 DNO rulepacks.

- `span_distance` check type in `app/qa_engine.py`. Converts consecutive pole lat/lon

  to OSGB27700 and measures distance between adjacent rows. Flags spans below 10m

  (likely duplicate entry) or above 500m (likely GPS error or missing pole). Added to

  all 4 DNO rulepacks.

- Four new tests in `tests/test_qa_engine.py` covering unique_pair and span_distance.

### Fixed

- `test_import_finalize_returns_success_for_valid_job` hardcoded issue count updated

  9→11 to reflect the two additional issues correctly raised by the new rules on the

  existing integration test fixture.

### State at end of session

- 35 tests passing.

- 10 QA check types.

- 4 DNO rulepacks live (`SPEN_11kV`, `SSEN_11kV`, `NIE_11kV`, `ENWL_11kV`).

- Control layer in sync with code.

- CI green.

---

## 2026-04-22

### Added

- Formal `_archive/` structure introduced to separate active project from historical material.

- New `AI_CONTROL/05_PROJECT_REFERENCE.md` created to preserve historical context without bloating operational files.

- Clear three-layer model defined:
  - Active project surface

  - Archive/reference surface

  - Local/tool-specific surface

### Changed

- Repository reorganised to reflect clean separation between:
  - active code and control files

  - historical synthesis and archive material

- `CLAUDE.md` rewritten to align with cleaned control layer and new repo structure.

- `.cursorrules` rewritten to match Claude bootstrap and enforce correct working model.

- `README.md` rewritten to:
  - reflect current MVP state

  - define project structure

  - document active vs archive separation

  - clarify development priorities

### Moved

- `PROJECT_SYNTHESIS/` → `_archive/docs/PROJECT_SYNTHESIS/`

- `RUNBOOK.md` → `_archive/docs/`

- `PROJECT_OPERATING_MODEL.md` → `_archive/docs/`

- `MANIFEST.md` → `_archive/docs/`

- `FRONTEND_FINAL_IMPLEMENTATION.md` → `_archive/docs/`

- AI bundle folders:
  - `CHATGPT_UPLOAD_BUNDLES/`

  - `CLAUDE_APP_UPLOAD_BUNDLES/`

  - `CLAUDE_REVIEW_BUNDLES/`

  → `_archive/ai_bundles/`

### Removed

- Legacy control-layer entry points from active usage:
  - `MASTER_PROJECT_READ_FIRST.md`

  - `AI_CONTROL/00_READ_THIS_FIRST.md`

  - `AI_CONTROL/01_PROJECT_TRUTH.md`

### Fixed

- Eliminated ambiguity between:
  - active instructions

  - historical synthesis

  - archived code

- Prevented future AI/tool drift by enforcing single authoritative control layer.

### State at end of session

- Clean repository structure established.

- Control layer fully aligned with project direction.

- Archive separated and safe from accidental use.

- Claude + Cursor environments aligned with new structure.

- Project ready for focused Phase 1 work (QA rule improvements).

---

## 2026-04-21

### Added

- `NIE_11KV_RULES` rulepack in `app/dno_rules.py`. Uses ENA TS 43-8 height range (7–20m), pole ID regex, paired-coord checks, material/structure-type consistency, and `coord_consistency` (100m). Network bounds: Northern Ireland lat 54.0–55.3, lon -8.2 to -5.4 — single contiguous licence area, no disjoint-zone caveat.

- `NIE_11kV` entry in `RULEPACKS` dict.

- Two new tests in `tests/test_qa_engine.py`: registration check + valid NIE pole (realistic Belfast coords) passes.

- `PROJECT_OPERATING_MODEL.md` — plain-English guide to how the project is organised, who does what, and how sessions run.

### Changed

- `AI_CONTROL/00_MASTER_SOURCE_OF_TRUTH.md`: §4 updated to reflect NIE live and 29 tests; §5 priority list updated; §6 Claude app role clarified as "primary implementation tool and control-layer custodian"; §7 hard rule 9 added (never close a session without updating handoff + changelog); §9 file map updated to include `PROJECT_OPERATING_MODEL.md`.

- `AI_CONTROL/03_CURRENT_TASK.md`: Rewritten — next task is `ENWL_11kV`.

- `AI_CONTROL/04_SESSION_HANDOFF.md`: Rewritten to record this session.

### State at end of session

- 29 tests passing.

- 8 QA check types.

- 3 DNO rulepacks live (`SPEN_11kV`, `SSEN_11kV`, `NIE_11kV`).

- Control layer in sync with code.

- CI green.

---

## 2026-04-20 (continued)

### Added

- `SSEN_11KV_RULES` rulepack in `app/dno_rules.py`. Uses same ENA TS 43-8 height range (7–20m), pole ID regex, paired-coord checks, material/structure-type consistency, and `coord_consistency` (100m) as SPEN. Network bounds cover combined SEPD (southern England) + SHEPD (northern Scotland) licence areas: lat 50.0–60.9, lon -7.5 to +1.8. Documented `TODO` to tighten with polygon check — current bounds pass coordinates in non-SSEN areas between the two zones but still catch grossly wrong coordinates.

- `SSEN_11kV` entry in `RULEPACKS` dict.

- Two new tests in `tests/test_qa_engine.py`: registration check + valid SSEN pole (realistic Inverness coords) passes.

### Triaged

- Dismissed 9 Dependabot alerts (1 high geopandas, 6 moderate Werkzeug, 2 low Flask) as "vulnerable code not actually used". Tool runs locally on macOS with no PostGIS connection, no caching proxy, and no Werkzeug file-serving path — none of the CVE prerequisites apply.

### State at end of session

- 27 tests passing.

- 2 DNO rulepacks live (`SPEN_11kV`, `SSEN_11kV`).

- CI green.

- 0 open Dependabot alerts.

---

## 2026-04-20

### Added

- `coord_consistency` QA check type in `app/qa_engine.py`. Converts lat/lon to OSGB27700 via pyproj and measures distance against declared easting/northing. Configurable tolerance (default 100m). Rows with any missing coordinate values are skipped.

- `coord_consistency` rule in `SPEN_11KV_RULES` with 100m tolerance.

- Two new tests in `tests/test_qa_engine.py` covering the new check (matching and mismatched coordinate cases).

- `.github/dependabot.yml` — weekly Dependabot updates for pip + github-actions.

- `CHANGELOG.md` — this file.

- `pytest-cov` added to dev dependencies for coverage reporting (`pytest --cov=app`).

### Changed

- `app/qa_engine.py` refactored into a clean single if/elif chain. Checks that operate on multiple fields are now grouped separately from checks that operate on a single `field` key.

- Control layer consolidated:
  - `AI_CONTROL/00_MASTER_SOURCE_OF_TRUTH.md` rewritten as the single primary authority. Absorbed tool roles and hard rules from the deleted `05_AI_ROLE_RULES.md`. Added §10 "how to update this file" checklist.

  - `AI_CONTROL/02_CURRENT_STATE.md` aggressively slimmed — duplicated counts and priorities removed; only technical detail retained.

  - `AI_CONTROL/03_CURRENT_TASK.md` rewritten for post-coord_consistency state; next task is `SSEN_11kV` rulepack.

  - `AI_CONTROL/04_SESSION_HANDOFF.md` rewritten to record this session's work.

  - `AI_CONTROL/06_DEVELOPMENT_PROCESS.md` slimmed — dropped sections that duplicated master truth; kept genuinely process-only content.

  - `CLAUDE.md` and `.cursorrules` slimmed — removed hard-coded counts that drift. Now reference master truth for changing facts.

### Removed

- `MASTER_PROJECT_READ_FIRST.md` (root). Redundant pointer.

- `AI_CONTROL/00_READ_THIS_FIRST.md`. Legacy pointer superseded by master truth.

- `AI_CONTROL/01_PROJECT_TRUTH.md`. Still used old "SpanCore" identity; content absorbed into master truth §1.

- `AI_CONTROL/05_AI_ROLE_RULES.md`. Content absorbed into master truth §6.

### State at end of session

- 25 tests passing.

- 8 QA check types.

- SPEN_11kV is the only live rulepack.

- Control layer reduced from 9 files to 5 active + 2 tool bootstraps + this changelog.

- CI green.

---

## Earlier history

Earlier sessions are summarised in `AI_CONTROL/04_SESSION_HANDOFF.md` and

`_archive/docs/PROJECT_SYNTHESIS/`.

This file starts at 2026-04-20.
