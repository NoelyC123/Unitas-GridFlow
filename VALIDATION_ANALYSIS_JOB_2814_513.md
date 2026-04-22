
All projects
Unitas-GridFlow
Building Unitas-GridFlow — a narrow pre-CAD QA and compliance tool for UK electricity network survey-to-design handoffs. It is a local Flask/Python web app that: - ingests survey CSV data - applies DNO-specific QA validation - generates structured issues - visualises outputs on a Leaflet map - produces PDF QA reports Codebase: `/Users/noelcollins/Unitas-GridFlow/` Important: This repository was cleaned and reorganised. Active project surface: - AI_CONTROL/ - app/ - tests/ - sample_data/ - README.md - CHANGELOG.md - CLAUDE.md - root config files Archive/reference only: - _archive/ Do not use `_archive/` unless explicitly instructed. Active control layer: 1. AI_CONTROL/00_PROJECT_CANONICAL.md 2. AI_CONTROL/01_CURRENT_STATE.md 3. AI_CONTROL/02_CURRENT_TASK.md 4. AI_CONTROL/03_WORKING_RULES.md 5. AI_CONTROL/04_SESSION_HANDOFF.md 6. AI_CONTROL/05_PROJECT_REFERENCE.md At the start of a session, read: - AI_CONTROL/00_PROJECT_CANONICAL.md - AI_CONTROL/02_CURRENT_TASK.md Then read additional files only if needed: - AI_CONTROL/01_CURRENT_STATE.md - AI_CONTROL/04_SESSION_HANDOFF.md - CHANGELOG.md Do not use old control-layer names or archived files as active instruction.
Show more

You are working on Unitas-GridFlow.

Follow the active control layer only.

Read first:

- AI_CONTROL/00_PROJECT_CANONICAL.md

- AI_CONTROL/02_CURRENT_TASK.md

Then read if needed:

- AI_CONTROL/01_CURRENT_STATE.md

- AI_CONTROL/04_SESSION_HANDOFF.md

- AI_CONTROL/06_STRATEGIC_REVIEW_2026-04-22.md

- VALIDATION_ANALYSIS_JOB_2814_513.md

Do not use _archive/.

Current direction:

The project should continue, but the next phase is validation-led, not feature-led.

The first real-job validation pack showed:

- the current MVP cannot ingest the raw controller CSV format

- Irish Grid handling is required for NIE jobs

- the most useful near-term value is likely a structured summary of what the digital survey file does and does not contain for design purposes

Your task:

Implement the narrowest next development step supported by that evidence.

Scope for this task only:

1. Add support for parsing raw controller CSV exports like job 28-14 513

2. Add Irish Grid coordinate handling/detection needed for that intake

3. Add a simple completeness/capture summary from the parsed digital survey file

4. Keep scope narrow

5. Do not add OCR, plan parsing, multi-file workflow, or broad new features

6. After any code changes, run:

   - pytest -v

   - pre-commit run --all-files

7. Then commit and push

Important:

When editing files, provide the full final version of every changed file, not patches.


Start a task in Cowork
Unitas-GridFlow survey data validation analysis
Last message 28 minutes ago
Project status and alignment review
Last message 1 hour ago
Project cleanup and QA rules development workflow
Last message 5 hours ago
Repository cleanup and control layer alignment
Last message 5 hours ago
Memory
Only you
Project memory will show here after a few chats.

Instructions
Unitas-GridFlow — Project Instructions Project identity You are working on Unitas-GridFlow, a narrow pre-CAD QA and compliance tool for UK electricity network survey-to-design handoffs. The system currently: - ingests survey CSV data - normalises input into a working schema - applies rule-based QA validation - generates structured issues - visualises outputs on a Leaflet map - produces PDF QA reports Short identity: A narrow pre-CAD QA gatekeeper for survey-to-design workflows. ⸻ Critical context (IMPORTANT) This project is not software-first. It comes from direct real-world experience of: - survey → design handoff failures - messy data intake - designers doing hidden QA instead of design - downstream office time being wasted on input repair instead of actual design The goal is to: - catch real problems early - reduce rework - make survey data more trustworthy before CAD/design - create a structured gate between survey and design Always think like: “Would this actually help a designer trust the input data?” ⸻ Canonical locations - Local: /Users/noelcollins/Unitas-GridFlow/ - GitHub: NoelyC123/Unitas-GridFlow - Branch: master ⸻ Repository structure (CRITICAL) 1. ACTIVE PROJECT (use only this) - AI_CONTROL/ - app/ - tests/ - sample_data/ - README.md - CHANGELOG.md - CLAUDE.md - PROJECT_DEEP_CONTEXT.md 2. ARCHIVE (DO NOT USE) - _archive/ 3. LOCAL / TOOL FILES (ignore as project truth) - .env - .vscode - .claude - .venv312 - caches ⸻ Control layer (source of truth) When needed, read in this order: 1. AI_CONTROL/00_PROJECT_CANONICAL.md 2. AI_CONTROL/02_CURRENT_TASK.md 3. AI_CONTROL/01_CURRENT_STATE.md (only if needed) 4. AI_CONTROL/04_SESSION_HANDOFF.md (only if needed) 5. AI_CONTROL/06_STRATEGIC_REVIEW_2026-04-22.md (only if strategic direction is relevant) Use: - canonical = what the project is - current task = what to do next - current state = what is true right now - strategic review = why the next phase is validation-led ⸻ Session start behaviour At the start of work: 1. Read: - AI_CONTROL/00_PROJECT_CANONICAL.md - AI_CONTROL/02_CURRENT_TASK.md 2. Then optionally: - AI_CONTROL/01_CURRENT_STATE.md - AI_CONTROL/04_SESSION_HANDOFF.md - AI_CONTROL/06_STRATEGIC_REVIEW_2026-04-22.md - CHANGELOG.md - README.md - CLAUDE.md Do not read _archive/ unless explicitly asked. ⸻ Current state - MVP works end-to-end - Tests must remain green - CI is active - Phase 1 is complete - Phase 2A is complete ⸻ Current strategic position (STRICT) The project should continue, but the next phase must be validation-led. The main unresolved question is: Does the current tool provide meaningful value on real survey files for real users? That means the current focus is no longer broad rule expansion by default. The focus is now: - test the current tool against real survey files - identify what works - identify what breaks - identify what users actually care about - use that evidence to define the next development step Do not assume more features are the right next step without validation evidence. Validation-phase addendum The first real-job validation pack showed that: - real survey inputs may arrive as raw controller exports rather than clean structured CSVs - NIE jobs may require Irish Grid handling - the next useful value may come from showing what the digital survey file does and does not contain for design purposes Therefore, during this phase: - prioritise real-file intake compatibility before adding more QA rules - prefer narrow improvements supported by validation evidence - do not broaden into OCR, image parsing, plan parsing, or platform expansion unless explicitly instructed ⸻ Working style - Stay strictly narrow in scope - Make small, targeted changes - Do not redesign architecture - Do not expand scope - Always read before editing - Prioritise real-world usefulness over theoretical completeness - Prioritise validation evidence over abstract feature expansion - When a real validation analysis file exists, use it as current evidence for next-step decisions ⸻ Engineering rules After any approved code change: - Run: pytest -v - Run: pre-commit run --all-files - Commit clearly - Push to master Output rule When editing or improving files: - provide the full final version of every changed file - provide exact terminal commands separately - avoid partial patches unless explicitly asked ⸻ Key files - app/dno_rules.py - app/qa_engine.py - app/routes/api_intake.py - tests/ Strategic / control files: - AI_CONTROL/00_PROJECT_CANONICAL.md - AI_CONTROL/01_CURRENT_STATE.md - AI_CONTROL/02_CURRENT_TASK.md - AI_CONTROL/03_WORKING_RULES.md - AI_CONTROL/04_SESSION_HANDOFF.md - AI_CONTROL/06_STRATEGIC_REVIEW_2026-04-22.md ⸻ Final rule Operate strictly within the active project. Do not rely on archive or assumptions. Do not replace real-world validation with abstract feature work.

Files
2% of project capacity used

VALIDATION_ANALYSIS_JOB_2814_513.md
306 lines

md



README.md
292 lines

md



CLAUDE.md
152 lines

md



CHANGELOG.md
374 lines

md



PROJECT_DEEP_CONTEXT.md
468 lines

md



06_STRATEGIC_REVIEW_2026-04-22.md
98 lines

md



05_PROJECT_REFERENCE.md
269 lines

md



03_WORKING_RULES.md
231 lines

md



04_SESSION_HANDOFF.md
127 lines

md



02_CURRENT_TASK.md
111 lines

md



00_PROJECT_CANONICAL.md
290 lines

md



01_CURRENT_STATE.md
214 lines

md



2814 513 2.csv
csv


Capture 1.PNG

2814 Strabane Main PT.3  4474.png

Image 20250326 151712.jpeg

img_20250303221912.jpg


VALIDATION_ANALYSIS_JOB_2814_513.md
12.60 KB •306 lines
Formatting may be inconsistent from source

# Validation Analysis — Job 28-14 513

## Purpose

This document records the findings from the first real-job validation test of Unitas GridFlow.

It answers the three questions that matter right now:

1. What is the narrowest useful thing this tool should do on a real survey pack?
2. What does the real input model actually look like?
3. What is the narrowest next development step supported by this evidence?

---

## The validation pack

The test used a real NIE Networks job (28-14 513) in the Strabane area, Northern Ireland.

Materials provided:

- Raw survey CSV exported from a GNSS controller
- Marked-up plan drawing showing proposed line work, stay specifications, conductor scope, pole repositioning, and recovery notes
- Aerial/ArcGIS map image annotated with stay types and counts at each pole position
- Two pages of handwritten field notebook showing clearance measurements, material observations, obstruction context, and pole-specific design notes

This is a representative survey-to-design handoff package for a real 11kV overhead line refurbishment job.

---

## What the CSV actually contains

The file is a raw controller dump in the following format:

```
Job:28-14 513,Version:24.00,Units:Metres
PRS485572899536,219497.298,413575.610,118.985,
1,242186.075,402362.807,99.505,Angle,Angle:STRING,1,...
```

Key characteristics:

- Row 1 is a job metadata header, not column names
- Row 2 is a base station reference (PRS), not a survey point
- Subsequent rows contain: point number, Irish Grid easting, Irish Grid northing, elevation, feature code, then inline key-value attribute pairs
- Feature codes include: Angle, Pol, Hedge, EXpole
- Attributes are embedded as `FeatureCode:ATTRIBUTE,value` pairs (STRING, TAG, REMARK, LAND USE, HEIGHT)
- Coordinates are Irish Grid (TM65), not WGS84 lat/lon
- There are 11 surveyed points total

This format is completely unlike the structured column-header CSV the current MVP expects. The tool cannot currently ingest this file at all.

---

## What exists outside the CSV

This is the critical finding. The overwhelming majority of design-relevant information is not in the CSV.

### Stay specifications (plan + aerial + notebook)

- Pole 515: fit X1 new additional T-Off stay; replace X1 existing T-off stay in new position
- Pole 2/515: fit X2 new additional terminal stays; recover X2 existing terminal stays
- Aerial shows: X1 angle stays, X2 angle stays, X2 angle stays + X2 T-off stays at different poles
- Notebook: fit x2 new anglestays at 7+4m in tandem; fit x2 new t-acoff stays at 6+4m in tandem; replace x1 anglestays

None of this appears in the CSV.

### Conductor scope (plan only)

- Lay, hang & connect approx. 115m of 3X95 WF to LV Pole 1 and connect to existing service at the top of the pole

Not in the CSV.

### Clearance and obstruction measurements (notebook only)

- 6m up wall, 4m to connection, 13m to house, 5m clearance
- House found, shed, 2m gap, 7m distance, 22m measurement
- Hedge height 2m (one location), hedge height 6m (another), hedge height 13m (another)
- Post (soil) noted at specific locations

Not in the CSV.

### Material and condition observations (notebook only)

- T/cut (conc) — concrete T-cut pole
- Post (soil) — soil-embedded post
- "recover ex LV" — existing LV asset to be recovered

Not in the CSV (except two HEIGHT values embedded as inline attributes).

### Pole function and repositioning (plan + notebook)

- 1/515 marked as "Reposition Pole"
- Pole 513 remark: "convert to tee"
- Point 2: "new term pole pos"
- Various pole sub-positions (1/515, 2/515, S13B)

Partially in the CSV as REMARK values, but only for two of eleven points.

### Recovery/removal scope (plan + notebook)

- Recover X2 existing terminal stays
- Recover existing LV
- Replace X1 existing T-off stay

Not in the CSV.

---

## What the current MVP would do with this job

### Intake: would fail

The file cannot be ingested by the current pipeline. The current intake expects a CSV with recognisable column headers (pole_id, lat, lon, height, etc.). This file has:

- A metadata first row instead of headers
- Irish Grid coordinates instead of lat/lon
- Inline attribute pairs instead of separate columns
- Feature codes embedded in a completely different structure

The tool would either error on upload or produce meaningless results.

### QA rules: not reached

Because intake would fail, no QA rules would run. Even if the file were manually restructured:

- Coordinate validation could work (NIE bounds check exists for Irish Grid after conversion)
- Span distance checks could work for the 11 sequential points
- Duplicate coordinate check could work
- Height range checks would apply to the two rows that have HEIGHT values
- The remaining 9 rows have no height — these would be flagged as missing, which is technically correct but not very useful since the heights are often recorded elsewhere (notebook, controller attributes)

### Useful output: essentially none in current state

The tool cannot currently add meaningful value to this job as received.

---

## Revised core value proposition

### What the validation showed

The original MVP assumption was that the main value would come from validating structured CSV fields — checking heights, coordinates, materials, span distances within a clean tabular dataset.

The real job showed that:

1. The structured digital file (CSV) contains only the bare spatial skeleton — point positions and a few attributes
2. The actual engineering content — stays, clearances, conductor scope, materials, recovery scope — lives in handwritten notes, marked-up plans, and aerial annotations
3. A designer receiving this job package does not primarily need someone to check whether the coordinates are valid; they need to know whether the survey package is *complete enough to design from*

### Narrowest useful thing the tool should do

The narrowest useful thing this tool should do on a real survey pack is:

**Parse the digital survey export, extract what it contains, and clearly report what is present versus what is missing or incomplete for design purposes.**

This is a shift from "validate the data you have" to "tell the designer what the data does and does not contain."

Concretely, for this job, the most useful output would be something like:

- 11 points surveyed
- Coordinate system: Irish Grid (TM65)
- Points with height recorded: 2 of 11
- Points with remarks/notes: 2 of 11 ("convert to tee", "new term pole pos")
- Stay data present: no
- Clearance data present: no
- Conductor scope present: no
- Material data present: no (except feature codes Angle, Pol, Hedge, EXpole)
- Obstruction/land use data present: no

A designer seeing this would immediately understand: "the digital file gives me positions, but I need the notebook and plans for everything else." That is genuinely useful. It is much more useful than validating coordinate precision on a file the designer already trusts spatially.

### What the value proposition is NOT

The tool should not try to:

- Read handwritten notebook pages (image OCR / AI interpretation is a different product)
- Parse marked-up plan drawings
- Replace the surveyor's judgment about what to record
- Become a general document management system

The tool should remain a narrow gate that inspects what arrives digitally and reports on its design-readiness.

---

## Real input model

### What the current MVP assumes

The current intake assumes:

- A CSV file with column headers in the first row
- Columns mapping to known field names (pole_id, lat, lon, height, material, structure_type, etc.)
- WGS84 lat/lon coordinates
- One row per asset/pole

### What real files actually look like

Based on this job and general knowledge of survey workflows:

- Raw GNSS controller exports use the format seen here: metadata header, base station row, then point rows with feature codes and inline attribute pairs
- Coordinate systems vary by region: WGS84, OSGB36, Irish Grid (TM65/ETRS89)
- Column structure is not standardised — different controller software (Leica, Trimble, TopCon) exports differently
- Some surveyors restructure the data into a clean spreadsheet before handover; others send the raw file
- The raw file may be a CSV, a Leica GSI file, a Trimble JXL, or similar

### Minimum realistic input model for the next iteration

The tool does not need to handle every possible format. But it needs to handle at least:

1. **Raw controller CSV dumps** in the format seen in this job (metadata header, inline attributes, feature codes)
2. **Irish Grid coordinates** as well as OSGB and WGS84
3. **Structured spreadsheet CSVs** (the format the current MVP already handles)

The first two are the immediate gap. The third already works.

---

## Narrowest next development step

Based on what this validation showed, the narrowest next step that would produce real value is:

### Step 1: Parse raw controller CSV format

Add a secondary intake parser that can recognise and handle the raw controller export format:

- Detect the metadata header row (Job:, Version:, Units:)
- Skip the PRS/base station row
- Parse point rows into: point_number, easting, northing, elevation, feature_code
- Extract inline attributes (REMARK, HEIGHT, LAND USE, STRING, TAG) into separate fields
- Normalise into the existing internal schema

This is the front door fix. Without this, the tool cannot work on real files at all.

### Step 2: Support Irish Grid coordinates

Add coordinate system detection and handling:

- If coordinates are in Irish Grid range (eastings ~100000–400000, northings ~0–500000), treat as Irish Grid
- Convert to WGS84 for map display and existing QA checks
- Store original coordinate system in job metadata

This is needed for NIE area jobs and is a realistic extension of the existing pyproj usage.

### Step 3: Add a completeness report

After parsing, produce a simple completeness summary alongside the existing QA issue output:

- Total points surveyed
- Points with height data
- Points with remarks/notes
- Whether any stay data is present in the digital file
- Whether any clearance data is present
- Whether any material/condition data is present
- An overall "design-readiness" indicator (not a score — just a clear statement of what is and is not digitally captured)

This is where the real new value sits. It shifts the tool from "your coordinates are valid" to "here is what your survey file does and does not contain for design purposes."

### What not to do yet

- Do not try to OCR notebook images
- Do not try to parse plan drawings
- Do not build a multi-file upload workflow yet
- Do not expand the rulepack library further until the intake can handle real files
- Do not add commercial packaging

---

## Does this strengthen or weaken the project?

### Strengthens substantially

This validation test confirmed exactly the problem described in PROJECT_DEEP_CONTEXT:

- Critical information split across digital files, handwritten notes, and marked-up plans
- No single artefact is design-ready on its own
- The gap between "data off the instrument" and "data a designer can work from" is real and expensive
- Someone bridges that gap manually every time

The tool has a clear place in this workflow. The real job proves the problem exists.

### Honest challenge

The current implementation is pointed at the wrong layer. It validates within a structured dataset, but the real problem is what is missing from the structured dataset entirely.

That is not a fatal issue. It is a redirect. The tool's framing remains correct: narrow pre-CAD QA gatekeeper. But the most useful gatekeeping for real jobs turns out to be completeness assessment rather than field-level data validation.

### Net assessment

The project idea is stronger after this test than before. The implementation needs to shift, but the shift is narrow and well-defined. The three steps above (raw format parsing, Irish Grid support, completeness reporting) would move the tool from "cannot process a real file" to "can tell a designer what they have and what they are missing."

That is a genuine, practical, useful capability for an internal tool or consultancy asset.

---

## Summary

| Question | Answer |
|----------|--------|
| Did the tool work on the real file? | No — format mismatch prevented intake |
| What would be most useful? | Completeness reporting: what is and is not in the digital survey file |
| What is the input gap? | Raw controller format + Irish Grid coordinates |
| What is the value gap? | Tool checks data quality; real need is data completeness |
| Does the idea hold up? | Yes — the problem is confirmed and the tool has a clear role |
| What is the next step? | Parse raw format, support Irish Grid, add completeness report |
| What should not happen? | No broad expansion, no OCR, no platform features, no commercial packaging |
