# Unitas GridFlow — Project Canonical

## What this project is

**Unitas GridFlow** is a validation-led survey-to-design intelligence and design-readiness tool for electricity network handoffs.

It sits between field survey/controller outputs and office-based design work. Its job is to turn raw survey exports into clearer design-readiness evidence by parsing records, normalising coordinates and attributes, classifying assets, checking completeness and trust, visualising route context, and surfacing what is missing, risky, inferred, or provisional before CAD/design work begins.

GridFlow is currently strongest around **UK overhead line survey-to-design workflows**, especially **11kV OHL**, real Trimble/controller CSV exports, and the handoff from survey evidence to designer review.

GridFlow is **not** a full CAD replacement, full GIS platform, full DNO compliance engine, full field-survey platform, or general infrastructure software suite unless Noel/Goss explicitly changes scope.

---

## The problem this solves

The core problem is the survey-to-design handoff.

Survey data often reaches designers as a fragmented mixture of controller exports, sparse attributes, notebook evidence, photos, marked-up plans, and assumptions. Designers then spend time interpreting and checking survey evidence instead of starting from a trusted design-ready package.

GridFlow exists to reduce that handoff uncertainty by answering:

- What records are present?
- What do those records mean for design?
- What evidence is missing or incomplete?
- What appears inferred, legacy, provisional, or untrusted?
- What must be checked before CAD/design progresses?

---

## Current product identity

GridFlow is an operational **pre-CAD survey interpretation and design-readiness workspace**.

It provides:

- Survey/controller intake
- Coordinate system detection and conversion
- Electrical asset/context classification
- EX/PR replacement and lifecycle interpretation
- Route/design-chain sequencing
- QA and evidence-quality checks
- Map-based review filters and popups
- Design-readiness reports and handoff artefacts

It complements Field Maps/basic GIS display by adding design-readiness interpretation. If GridFlow does not show the underlying survey records clearly, it loses value; the value is the interpretation layer on top of clear record display.

---

## Current phase

As of the May 2026 source-of-truth references:

- Stage 1 post-survey QA gate: complete for the current evidence set
- Stage 2 design-ready handoff / Design Chain: complete for the current evidence set
- Stage 3 live intake platform: complete for the current evidence set
- Phase C map intelligence: complete
- Current status: strategic scope decision pending

Phase C delivered feature-type filtering, asset lifecycle visualisation, stay evidence detection at angle poles, span anomaly analysis, crossing/context enrichment, and professional popup organisation. The project has real operational validation from P011, Gordon/NIE, and Bellsprings/SPEN evidence.

The next decision is not primarily technical. It is whether to proceed with a lower-risk Phase C2/D professional QA + display refinement path before any Stage 4/full survey-platform expansion.

---

## What exists right now

The tool currently:

- Ingests raw Trimble/controller and structured CSV survey exports
- Handles multiple coordinate systems including OSGB36, Irish Grid/TM65, and WGS84-derived data
- Normalises inconsistent survey/controller columns
- Classifies electrical and context records across poles, spans, stays, cables, equipment, and crossings/context
- Detects EX/PR replacement relationships and route/design-chain sequencing
- Flags design-readiness issues such as missing heights, missing stay evidence, span anomalies, legacy/unverified evidence, and unclear replacement relationships
- Renders a Leaflet map with feature filters, lifecycle display, span lines, crossing context, and review-oriented popups
- Produces QA/design-readiness outputs including issue registers, map data, route/design-chain data, and PDF handoff reports
- Has 300+ tests passing according to the May 2026 control references
- Has been validated on real operational survey evidence including P011, Gordon/NIE, and Bellsprings/SPEN

---

## What is not built yet

GridFlow is not currently a full Stage 4 survey platform.

Not built or not production-ready:

- Full 50-field electrical survey data model
- Tablet/mobile structured field capture as the primary survey workflow
- Photo upload and evidence management
- Offline field workflow
- Full asset relationship model for a commercial survey platform
- Field Maps replacement capability
- Direct PoleCAD import/export confirmed against verified import requirements
- Full GIS/DNO asset-system integration
- Multi-user commercial deployment, authentication, and role-based collaboration

---

## Strategic direction

The May 2026 source-of-truth references define the live strategic fork:

### Path A — Phase C2/D professional QA + display refinement

- Lower-risk path
- 2-4 week scale
- Add 10-15 priority survey fields
- Improve map UX and popup organisation
- Keep GridFlow as an enhanced pre-CAD QA/design-readiness workspace
- Validate immediately on the existing real job corpus

### Path B — Stage 4/full electrical survey platform

- Higher-risk path
- 6-12 month scale
- Full 50-field data model
- Evidence/photo workflows
- Mobile/tablet capture
- Asset relationships, GIS parity, and commercial platform features
- Must not begin without customer/commercial validation

Recommended framing from the May 2026 references: proceed with the lower-risk Phase C2/D professional QA + display refinement first, validate customer/commercial demand, and only then decide whether Stage 4 is justified.

---

## Core principle

This project is **validation-led, not feature-led**.

Every step must answer: **Does this improve the reliability, clarity, and design-readiness of real survey data?**

---

## Source of truth hierarchy

1. Real survey files and validation evidence
2. May 2026 source-of-truth references in `AI_CONTROL/reference/`
3. Current control-layer files in `AI_CONTROL/`
4. Current repo implementation and tests
5. Project documentation
6. AI summaries and assumptions

For current strategic state and decision framing, use:

- `AI_CONTROL/reference/GridFlow_Project-Control_Review_May_2026.txt`
- `AI_CONTROL/reference/Complete_Knowledge_GridFlow_May_2026.txt`

---

## Files/directories not to use as active project truth

Do not use these as active project truth:

- `_archive/`
- Deprecated documents
- Old strategic reviews superseded by the May 2026 review
- Full `uploads/` tree as general context
- Bulk validation evidence unless a specific job requires it
- `.venv312/`, `.env`, and local environment files
- Stale control-file statements contradicted by the May 2026 references

---

## Repository

- **GitHub:** `https://github.com/NoelyC123/Unitas-GridFlow`
- **Branch:** `master`
- **Local:** `/Users/noelcollins/Unitas-GridFlow`
