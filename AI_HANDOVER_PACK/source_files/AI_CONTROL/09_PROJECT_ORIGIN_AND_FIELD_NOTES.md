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
