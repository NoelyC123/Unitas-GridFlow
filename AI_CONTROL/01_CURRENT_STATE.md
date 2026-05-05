# Current State

## Project phase

**Phase C complete; Phase C2/D professional QA + display refinement active.**

GridFlow has evolved from an MVP into an operational survey-to-design intelligence and design-readiness workspace for electricity network handoffs. It is currently strongest around UK OHL / 11kV / real controller survey workflows.

The May 2026 source-of-truth references describe the current state as:

- Stage 1 post-survey QA gate: complete for the current evidence set
- Stage 2 design-ready handoff / Design Chain: complete for the current evidence set
- Stage 3 live intake platform: complete for the current evidence set
- Phase C map intelligence: complete
- Current status: Phase C2/D professional QA + display refinement is the active implementation path

---

## Latest completed package

- **C2D-AA review workspace polish/package**
- Merged as `0106904 Merge C2D review workspace polish`
- Tests at merge: `pytest -v` passed, **514 passed**; `pre-commit` passed

---

## Current product framing

GridFlow is a validation-led survey-to-design intelligence and design-readiness tool.

It is an enhanced pre-CAD QA and engineering review workspace that interprets survey/controller outputs for design readiness.

It is not currently:

- A full CAD replacement
- A full GIS platform
- A full DNO compliance engine
- A full field-survey platform
- A Field Maps replacement
- A commercial multi-user SaaS product

GridFlow should complement Field Maps/basic spatial display by showing the same records clearly and adding design-readiness interpretation on top.

---

## What works right now

Core capabilities described by the May 2026 references:

- Multi-format CSV intake for Trimble/controller and structured exports
- Column/header normalisation
- Coordinate system handling for OSGB36, Irish Grid/TM65, and WGS84-derived data
- Electrical/context schema parsing across poles, spans, stays, cables, equipment, and context features
- EX/PR replacement relationship detection
- Route/design-chain sequencing
- QA/design-readiness checks for missing, risky, inferred, or provisional evidence
- Feature-type filtering on the map
- Asset lifecycle visualisation
- Stay evidence detection at angle poles
- Span anomaly detection
- Crossing/context enrichment
- Professional popup organisation with conditional display for existing, proposed, and context records
- PDF QA/design-readiness handoff reports
- Design Chain and Raw Working Audit style handoff outputs

---

## Validation and quality status

The May 2026 source-of-truth references report:

- 300+ tests passing
- Active CI / pre-commit quality controls
- Real operational validation integrated from P011, Gordon/NIE, and Bellsprings/SPEN
- Consistent issue patterns across real jobs, including EX/PR replacement relationships, span anomalies, angle poles without stay evidence, estimated existing-pole heights, and height plausibility issues

No new test run is implied by this state file; this is a documentation/control-layer summary of the referenced state.

---

## What is not built yet

Stage 4/full survey-platform scope is not built or not production-ready:

- Full 50-field electrical survey data model
- Tablet/mobile field capture as the primary survey workflow
- Photo upload and evidence management
- Offline workflows
- Complete asset relationship model for commercial field survey use
- Multi-user collaboration and authentication
- GIS/DNO system integration
- Field Maps replacement capability
- Direct PoleCAD import confirmed against verified import requirements
- Commercial deployment infrastructure

These remain future scope and must not be treated as current implementation reality.

---

## Strategic position

GridFlow currently has:

- Proven real-survey intake and normalisation
- Design-readiness QA and issue reporting
- Map-based engineering review tools
- Real operational validation
- Strongest fit as an internal/consultancy productivity and QA tool for survey-to-design handoff

GridFlow does not yet have enough validated commercial evidence to justify jumping directly into a full Stage 4 survey-platform build.

---

## Current C2/D checkpoint

Next explicit task:

- **C2D-AB popup field truthfulness / evidence-status pass**

C2D-AB was previously inferred from the review workspace polish work and is now recorded as the next task.

---

## Current operating instruction

No implementation scope should be started from stale Phase C-pending, Phase 1, Phase 2, or Phase 3 wording.

Use the May 2026 references and this refreshed control layer for current state. Stage 4 remains out of scope unless Noel records a new decision gate.
