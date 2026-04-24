# 07_REAL_WORLD_SURVEY_WORKFLOW.md

# Unitas-GridFlow — Real-World Survey Workflow Reference

## Purpose of this document

This document is a **core project truth document**.

It describes how UK overhead line (OHL) survey-to-design workflows actually operate in the field and office, based on direct real-world experience. This is not theory derived from standards documents or vendor documentation.

This document exists so that:

- future development decisions are grounded in how the workflow actually behaves — not how it is supposed to behave
- future AI sessions do not lose this domain knowledge between conversations
- QA logic, QA severity thresholds, feature interpretation, and UI language in Unitas are all anchored to real operational behaviour
- the project stays useful rather than technically correct but practically wrong

Every significant engineering or product decision in Unitas should be checked against this document.

---

## 1. End-to-end workflow (real process)

The real survey-to-design workflow for a UK electricity distribution OHL project typically follows this sequence:

```
Field survey → Trimble capture
  → Raw controller export (CSV / JOB / GIS format)
  → Office D2D / spreadsheet cleaning
  → PoleCAD (structural modelling and network design)
  → AutoCAD (drawing production)
  → Design submission (DNO / client)
```

### Where problems occur

Each transition in this chain is a potential loss point:

**Field → Export**
- The raw controller file contains everything the surveyor recorded, including setup points, reference marks, and metadata rows that are not survey data.
- Information that exists in the surveyor's head (verbal notes, informal agreements, follow-up intentions) is not in the file.
- Feature codes depend on the surveyor consistently applying a company code library — which does not always happen.

**Export → D2D spreadsheet**
- The raw export requires manual cleaning before it becomes a usable design input.
- Column naming, row ordering, and attribute completeness all vary between surveyors and between surveys from the same surveyor.
- This is the primary source of office time waste in the chain.

**D2D → PoleCAD**
- PoleCAD requires structured, clean, sequenced data.
- If D2D is incomplete or ambiguous, the designer either has to resolve it themselves or return the survey for re-submission.
- Problems that should have been caught at intake are instead discovered here — at significant cost.

**PoleCAD → Design submission**
- If design-stage errors are traced back to survey data quality, the cost is high: rework, late changes, or field repeat visits.

### Where time is wasted

The majority of avoidable waste occurs at two points:

1. **The D2D stage**: manual cleaning of messy raw exports
2. **Late design discovery**: problems with survey data that only become visible inside PoleCAD or AutoCAD

Unitas is intended to intercept both of these by acting as a structured gate immediately after export — before the D2D stage.

---

## 2. Field capture reality (Trimble / GIS)

### Primary capture method

The dominant field capture method for UK distribution OHL survey work is:

- **Trimble Access** software running on a Trimble GNSS controller (TSC7 or similar)
- RTK GPS for coordinate capture (typically Irish Grid TM65 / ITM for Northern Ireland, OSGB27700 for Great Britain)
- Feature code entry against a loaded survey library

### Feature code libraries

Surveyors capture each asset or feature by applying a **feature code** from a pre-loaded library. Common codes include:

| Code | Meaning |
|---|---|
| `EXpole` | Existing pole (as-found) |
| `PRpole` or `Pol` | Proposed pole (design intent) |
| `Angle` | Angle pole (existing or proposed) |
| `Hedge` | Vegetation boundary |
| `Gate` | Access gate |
| `Track` | Access track |
| `Stream` | Watercourse |
| `Fence` | Boundary fence |
| `Tree` | Individual tree |
| `Stay` / `Staywire` | Stay wire anchorage |

Feature code libraries vary between companies. The same physical asset may be coded differently depending on who ran the survey and which company's code library was loaded.

### Inline attributes

Some codes support inline attribute capture. In raw controller exports these appear as keyword-value pairs appended to the feature code record:

- `HEIGHT: 9.5` — declared pole height (not GPS elevation)
- `REMARK: stay conflict east` — free-text note from surveyor
- `MATERIAL: Wood` — structural material

These attributes are not always captured. Height, in particular, is often missing or estimated for existing poles (EXpoles) because accurately measuring an existing pole in the field requires specific equipment or estimation.

### GPS instrument elevation vs declared height

The GPS controller records a terrain elevation (Z value) for every captured point. **This is not the same as pole height.** The GPS Z value is the elevation of the ground at that point above sea level, not the height of the pole above ground.

Unitas intentionally does not map GPS Z values to the height field. Only explicit `HEIGHT:` inline attributes are treated as declared pole heights. This is deliberate — treating GPS elevation as pole height would produce systematically wrong results.

### Raw export format

A raw Trimble controller dump is not a clean CSV. It typically contains:

- a metadata header row (e.g. `Job:28-14 513,Version:2.6,Units:metres`)
- setup and reference point rows (not survey data)
- variable column counts per row
- inline attribute fields appended beyond the standard columns
- blank rows and comment rows

This format cannot be directly read by a standard `pd.read_csv` call. Unitas implements a dedicated `parse_raw_controller_dump()` function that handles this format specifically.

---

## 3. Feature code meaning (critical section)

Understanding what each feature code means in the real workflow is essential for correct QA behaviour.

### EXpole — existing physical pole

An `EXpole` record represents a **physical pole that exists on site at the time of survey**.

What it tells the designer:
- there is a real pole at this location
- the coordinates are the GPS position of that existing pole
- the pole may have condition notes, defects, or attributes from the surveyor
- the pole may be retained, replaced, or removed in the design

What it does NOT tell the designer:
- anything about what happens to the pole in the proposed design (that comes from the PRpole pairing)
- the accurate height (EXpole heights are often not captured or are estimated — this is expected, not a defect)

**Unitas behaviour implication:** EXpole records should not be penalised for missing or estimated height with a hard FAIL. A WARN is appropriate. This is implemented in Batch 13 (EXpole height-below-min downgrade to WARN).

---

### PRpole / Pol — proposed pole (design intent)

A `PRpole` or `Pol` record represents a **proposed pole position** — a surveyor-identified design intent or replacement location.

What it tells the designer:
- a pole should be placed here (or is being considered here)
- this is the surveyor's interpretation of where the proposed infrastructure should go
- if near an EXpole, it likely represents a replacement or repositioning

What it does NOT tell the designer:
- whether the proposal is approved or final (that comes from the design process)
- exact structural requirements (those come from PoleCAD)

**Unitas behaviour implication:** A PRpole in proximity to an EXpole is a **replacement pair** — not a duplicate-coordinate error and not a short-span failure. This is the most critical single piece of domain knowledge in the system. Implemented in Batch 11 (EX/PR replacement cluster detection).

---

### Context features (environmental and access)

Context features describe the physical environment around the survey route. They are **not structural assets** and should not be treated as poles in QA logic.

| Code | Design relevance |
|---|---|
| `Hedge` | Access constraint, stay conflict, vegetation management |
| `Gate` | Access constraint, land boundary |
| `Track` | Access route for plant, contractor access |
| `Stream` | Crossing clearance, span constraint |
| `Fence` | Land boundary, stay conflict |
| `Tree` | Vegetation management, clearance concern |

**Unitas behaviour implication:**
- Context features must not trigger height-required FAILs (they have no height to declare)
- Context features must not be included in span-distance checks between structural records
- Context features should not be counted toward structural record tallies
- Hedge, Gate, and Track between two poles do not break the span — they bridge through

Implemented across Batches 7, 8, and 9.

---

### Anchor and control points

Anchor records are **survey setup points and grid reference marks** — they are coordinate control infrastructure, not survey data. Examples from real Northern Ireland jobs: `GB_Kelso`, `GB_Selkirk`.

**Unitas behaviour implication:**
- Anchor rows must not trigger span checks — the distance from a survey setup point to the first pole can be many kilometres
- Anchor rows must not trigger height or material FAILs
- The span-distance chain must reset when an anchor row is encountered

Implemented in Batch 9 (anchor chain-reset in span checks).

---

## 4. Replacement logic (very important)

When a survey contains an EXpole and a PRpole in close proximity, this almost always represents a **replacement pair**: the existing pole is being replaced or repositioned.

### Typical offset distances

| Offset | Most likely interpretation |
|---|---|
| < 0.5m | Same surveyed position — surveyor captured both in the same spot |
| 0.5m – 5m | Standard replacement — like-for-like or minor repositioning |
| 5m – 10m | Repositioned — slight route adjustment or clearance move |
| 10m – 20m | Possible minor diversion |
| 20m+ | Likely new route or significant change |

### Why the tool must be cautious

Not every EXpole + PRpole pair is definitely a replacement. Exceptions exist:

- A surveyed PRpole without a nearby EXpole indicates new infrastructure (no replacement)
- An EXpole with no nearby PRpole indicates the existing pole is being retained or removed without replacement
- At very short offsets, it is possible two separate records were accidentally captured at the same position

For this reason, Unitas emits a **WARN (not FAIL)** for replacement pairs, with wording that describes a likely relationship rather than a definite one.

The phrase "probable replacement pair" or "likely being replaced" is deliberate and correct. The tool surfaces the interpretation; the designer confirms it.

---

## 5. What survey actually captures vs what design needs

There is a structural gap between what a digital survey file contains and what a designer needs to proceed with confidence.

### What the digital survey file typically captures

- GPS coordinates for each feature
- Feature codes (from the loaded library)
- Partial inline attributes (height sometimes, material rarely, remarks occasionally)
- Photos (attached separately, not in the CSV)
- Some free-text notes via REMARK fields

### What design actually needs

| Design requirement | Available in digital survey file? |
|---|---|
| Pole coordinates | Yes (GPS) |
| Feature codes / pole types | Usually yes |
| Route connectivity and sequencing | Partially — implied by ordering |
| Angle poles identified | Sometimes (Angle code) |
| Terminal poles identified | Rarely explicit |
| Stay wire requirements | Rarely explicit |
| Clearance measurements | No — field measurement or calculation required |
| Material specification | Rarely captured |
| Height of existing poles | Often missing or estimated |
| Proposed structure specifications | No — determined in design |
| Access constraints | Partially (Gate, Track, Hedge) |
| Photos / field observations | Not in CSV |

### The consequence

This gap creates the **D2D workload**: the manual office stage where survey data is interpreted, reordered, completed, and made design-usable.

Unitas's role is not to fill this gap — it is to **surface the gap clearly** so that a designer knows exactly what is present, what is missing, and whether the file is ready to proceed from.

---

## 6. The D2D problem

D2D (Data-to-Design or Drawing-to-Design, depending on context) refers to the **manual spreadsheet and cleaning stage** between raw survey export and PoleCAD entry.

### What D2D involves in practice

- Sorting and reordering pole records to reflect actual route sequence
- Renaming or standardising feature codes to match PoleCAD expectations
- Resolving ambiguous EX/PR pairings
- Inferring pole roles (angle, terminal, intermediate) from geometry and notes
- Filling missing fields (material, height) from field notes or standard assumptions
- Cross-referencing photos and handwritten notes to add context
- Removing non-structural rows (metadata, setup points) from the working data

### Why D2D is problematic

- It is manual and slow
- It depends on individual knowledge and interpretation
- The same file processed by two different people may produce different D2D outputs
- Errors introduced at D2D survive into PoleCAD and can reach design submission
- There is no audit trail of what was interpreted vs what was captured

### Unitas as the D2D gate

Unitas is not intended to replace D2D. It is intended to act as the gate **before** D2D — ensuring that the raw survey file is at a sufficient quality level before the manual D2D process begins.

A survey file that passes Unitas QA should still need D2D work. But it should not contain:

- broken coordinate sequences
- duplicate position entries
- ambiguous or uncoded features
- obvious missing structural records
- replacement pairs that were misread as errors

If those problems are surfaced at intake, D2D becomes less costly and less risky.

---

## 7. What designers actually care about

Based on real-world experience of what causes a survey to be rejected or queried by a designer:

### Acceptance signals (a designer trusts this file)

- Route geometry looks continuous and plausible on the map
- Pole ordering is clear — a clear sequence from start to end of route
- EXpoles and PRpoles are clearly distinguishable
- Spans between structural records look reasonable (not 2m, not 800m)
- Notes are present where the surveyor flagged something unusual
- Angle poles are identified (either by Angle code or clear geometry)
- Stay wire evidence is present for angle structures
- There are no unexplained gaps in the pole sequence

### Rejection signals (a designer queries or returns this file)

- Missing poles — gaps in the route sequence that do not correspond to any feature
- Very short spans — likely duplicates or replacement clusters that have not been interpreted
- Unclear EX/PR intent — EXpoles and PRpoles that cannot be clearly paired or distinguished
- Poor or absent notes at critical locations (crossings, constraints, unusual conditions)
- Coordinates that look wrong — inconsistent with the expected geography or route
- Inconsistent coding — same physical asset coded differently across the same job
- No stay evidence for angle poles

### What designers do NOT typically check

- Whether field names exactly match a schema
- Whether material is recorded for every pole (material is often omitted from digital survey)
- Whether height is present for every EXpole (height for existing poles is expected to be partial)

**Unitas implication:** The tool should calibrate its FAIL/WARN severity to match what designers actually treat as blocking vs non-blocking. Missing material for all poles on a job is a genuine design concern; missing height for some EXpoles is expected and should not be treated as a hard failure.

---

## 8. Real-world failure points

The most common survey data quality failures observed in real jobs, in approximate order of impact on design:

### 1. Missing intermediate poles

The route sequence has an implausible gap — a span that is far too long (e.g. 400m) where intermediate poles should exist. This may mean:

- poles were not captured in the field
- poles exist but were recorded under a different job
- coordinates are wrong and pulled a pole far from its real position

This is the most serious failure type — it means the survey is structurally incomplete.

### 2. Very short spans (duplicate positions / replacement clusters)

Two records at almost the same position. This is either:

- a duplicate capture (surveyor recorded the same pole twice)
- a replacement pair (EXpole + PRpole at the same or very close position)

Without interpretation, a designer cannot tell which case applies. Unitas distinguishes between these using the EX/PR classification.

### 3. Incorrect or missing structure_type

Feature codes are absent or wrong. Without knowing whether a record is Pol, Angle, EXpole, or Hedge, the designer cannot determine the structural role of each point.

### 4. Missing stay evidence

Angle poles with no proximate Stay or Staywire records — and no REMARK text indicating stay assessment. This may mean:

- stays were not captured
- stays are not required (which the designer needs to confirm)
- the angle is mild enough that the surveyor did not flag it

Without evidence either way, a designer cannot proceed with stay design.

### 5. Unclear connectivity

The route sequence cannot be determined from the data — either because ordering is inconsistent or because there are branching records with no branch indicators.

### 6. Inconsistent coding

The same type of asset is coded differently across the same survey (e.g. `EXpole`, `expole`, `EXPOLE` used interchangeably, or `Pol` used for both existing and proposed records). This creates ambiguity about design intent.

---

## 9. What makes a survey "design-ready"

A survey file is design-ready when it is sufficiently complete, consistent, and interpretable for a designer to proceed with PoleCAD modelling without needing to query the surveyor or return the file.

### Minimum requirements for design-readiness

- **Consistent structure**: every record has a feature code; codes are applied consistently
- **Plausible geometry**: no obviously wrong coordinates; spans between poles in a reasonable range
- **Clear EX/PR intent**: it is possible to determine which poles are existing assets and which are proposed
- **Correct sequencing**: the route can be followed from start to end without ambiguous gaps
- **Sufficient context notes**: critical issues (crossings, constraints, access, unusual conditions) are noted at the relevant records
- **No major ambiguity in route or replacement pairs**: a designer can make engineering decisions without needing additional field information

### Not required for design-readiness

- Height for every record (especially EXpoles — partial height coverage is accepted)
- Material for every record (material is rarely captured in controller dumps)
- Stay records for every angle pole (absence is flagged as a concern but not always a hard blocker)
- Perfect field naming (column normalisation handles this at intake)

---

## 10. Implications for Unitas

This section defines how real-world behaviour should translate directly into Unitas logic and language.

### What Unitas must do

**Interpret messy raw data correctly:**
- Parse raw controller dump format (variable columns, metadata rows, inline attributes)
- Handle multiple coordinate systems (OSGB, TM65/ITM) correctly
- Normalise inconsistent field names and feature code casing

**Detect structural vs context vs anchor records:**
- Classify every record into the correct role before applying any QA check
- Never apply structural QA (height required, span distance) to context or anchor records

**Infer EX/PR relationships:**
- Identify replacement pairs (EXpole + PRpole/Pol in proximity) using proximity and code logic
- Emit a cautious WARN (not FAIL) — "likely replacement pair" not "confirmed replacement"

**Detect replacement clusters:**
- When multiple EX/PR pairs appear close together, surface this as a design intent signal

**Flag missing design evidence:**
- Height missing for structural records (WARN for EXpoles, stronger signal for PRpoles)
- Stay evidence absent for angle poles (WARN — may or may not be required)
- Material completely absent (flag as design limitation, not individual-record failure)

**Explain findings in designer language:**
- Issue text should say what it means for design, not what field value is wrong
- "Height likely estimated / not captured (EXpole)" is better than "height out of range"
- "Angle structure with no stay evidence detected — verify whether stay capture is missing or not required" is better than "angle pole flagged"

**Produce a pre-design briefing, not a raw QA dump:**
- Circuit summary (what this route looks like)
- Top design risks (what a designer needs to check before proceeding)
- Replacement narratives (what the EX/PR pairs appear to mean)

### What Unitas must NOT do

- Assume the data is well-formed — it will often not be
- Assume all required logic is present in the file — it will often not be
- Behave like a strict CAD engine that requires complete structured data to function
- Penalise field capture realities (missing EXpole heights, absent material) with hard FAILs
- Treat every short span as an error — some short spans are replacement pairs
- Treat every long span as an error — some long spans are correct route geometry
- Apply structural QA rules to non-structural features

---

## 11. Future direction (aligned with project vision)

Unitas is currently a post-survey validation and interpretation tool. The intended long-term direction follows a natural maturation path:

### Phase 1 — Post-survey validation (current state)

The tool receives a completed survey export, interprets it, runs QA checks, and produces a design-readiness assessment.

The designer sees: what the file contains, what is missing, what is risky.

### Phase 2 — Feedback loop to surveyors

Validation findings are structured and communicated back to the surveyor before the design process begins, enabling targeted re-survey or annotation without requiring a full repeat visit.

The surveyor sees: what information was missing or ambiguous, what the designer needs.

### Phase 3 — Capture guidance

Before or during the field survey, the tool provides guidance on what to capture for a specific job type, DNO, or route complexity level.

The surveyor receives: a pre-survey checklist or field capture standard for this job.

### Phase 4 — Field integration (long-term potential)

Structured connectivity between field capture software and the validation layer — closer to real-time feedback on data quality during capture.

---

## Note on scope

This document is a real-world reference, not a product specification.

The phases above describe the natural evolution of a survey-to-design workflow intelligence tool grounded in real operational experience. They are not commitments to a product roadmap.

Every phase transition should be driven by validation evidence from real survey files and real users — not by assumption.

The project remains **validation-led, not feature-led**.
