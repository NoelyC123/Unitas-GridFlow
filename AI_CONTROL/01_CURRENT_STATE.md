# Current State

## Project phase

**Stage 3 complete + Phase B shipped + Phase C (C1-C4) shipped + Phase C2/D shipped + Phase 1 Domain Accuracy (D1-A–D1-D) shipped**

All previous stages are complete. Phase B (UI polish) shipped successfully. Phase C foundation (C1-C4) implemented and verified. Phase C2/D map/popups shipped. **Emergency domain fixes (Phase 1 packages D1-A through D1-D)** are implemented and pushed (316 tests passing).

**Current state:** Practitioner operational validation on real jobs; **Phase 2 electrical data model** (`PHASE_2_3_ROADMAP.md`) is **not started** until explicitly approved.

---

## CRITICAL: GridFlow is Additive to Field Maps

**Field Maps shows:** What records are on the map (spatial data display)

**GridFlow shows:**
1. **What records are on the map** (Field Maps parity - MUST have this)
2. **PLUS:** What this survey data means for design
3. **PLUS:** What is missing or incomplete
4. **PLUS:** What remains provisional
5. **PLUS:** What must be checked before CAD/design

**GridFlow = Field Maps functionality PLUS design-readiness interpretation layer**

**NOT:** GridFlow replaces Field Maps' record display
**YES:** GridFlow adds interpretation ON TOP OF the same record display

**Key principle:** If GridFlow doesn't show records as clearly as Field Maps, it's worse, not better. The value is the ADDITIVE interpretation layer, not replacement of basic functionality.

---

## What works right now

### MVP flow (confirmed)
upload CSV → save file → run QA → save outputs → view map → download PDF → browse jobs

### Core capabilities
- Raw Trimble GNSS controller dump intake
- CRS detection (Irish Grid TM65, ITM, OSGB27700)
- Coordinate conversion for map display
- Record-role classification (structural, context, anchor)
- Replacement pair detection
- Evidence gates (7 scoped design gates)
- Interactive Leaflet map with filters
- PDF pre-design briefing report
- DNO rulepack inference
- Column/header normalisation
- Context feature classification
- Design Chain export with evidence-quality columns
- Raw Working Audit export
- Route sequencing
- EXpole matching
- Section-aware output
- Global provisional design pole numbering
- **Phase B: Professional terminology throughout (surveyor/designer language)**
- **Phase B: Responsive pairing cards (tablet-friendly)**
- **Phase B: Dashboard clarity improvements**

### Testing and quality
- **316 tests passing** (includes Phase 1 domain packages)
- Pre-commit hooks active
- Ruff linting active
- GitHub Actions CI active
- All commits pushed to master

### Phase 1 Domain Accuracy — Emergency fixes (2026-05-01)

- **D1-A:** Third-party asset classification (e.g. BT pole remarks) — `b6dbc7c`
- **D1-B:** Height source + confidence + `height_source_existing` QA — `e618590`
- **D1-C:** `classify_source_confidence`, legacy map banner, Source & Confidence popup — `f30ef46`
- **D1-D:** `parse_attachments`, attachments in map data + Third-Party Attachments popup — `6349ebd`

### Phase C shipped (2026-05-01)
- **C1: Feature-Type Filtering + Blank Field Framework** (commit 733fd99)
  - 8 feature-type filter buttons
  - Blank field framework (existing/proposed/context)
  - Visual symbol hierarchy
  - 8-section popup organization
- **C2: Asset Lifecycle Visualization** (commit 0b5b7d0)
  - 8-state lifecycle metadata
  - EX↔PR match visualization (dashed lines)
  - Toggleable lifecycle layer
  - Lifecycle popup section
- **C3: Stay Evidence at Angle Poles** (commit 6aefa15)
  - Angle pole detection (>10° deviation OR function="Angle")
  - 20m stay evidence scanning
  - Missing stay warnings
  - "Show angle poles missing stay evidence" filter
- **C4: Span Anomaly Detection + Crossing Context** (commit da01811)
  - Span anomaly flagging (<10m duplicate / >500m missing pole)
  - Enriched crossing labels (Road/Wall/Stream with priority)
  - "Show span anomalies" and "Show crossings requiring clearance" filters

---

## Major evidence gathered (2026-04-30)

### 1. Live operational feedback
**Source:** Real map review (P011-style operational test)

**6 critical issues identified:**
1. Context features invisible (blocker)
2. Proposed pole "height not captured" misleading (blocker)
3. Symbols not distinct enough
4. Stay evidence missing (blocker)
5. Electrical data insufficient
6. Existing pole data unclear

**All 6 issues map directly to Phase C packages C1-C4.**

### 2. Engineering analysis #1
**Source:** GridFlow_Electrical_Survey_Review.docx (15 pages, 17 sources)

**Key findings:**
- Height vs. Specification problem identified and specified
- 8 asset lifecycle states defined
- Shape ≠ Color visual paradigm specified
- ESQCR, PLS-CADD, NIE schema referenced
- Complete electrical information model defined

**Validates Phase C C1-C4 independently.**

### 3. Field Maps + NIE validation
**Source:** NIE_Fibrus_enhanced_Review_for_GridFlow_.docx

**Key findings:**
- Field Maps UX benchmarks analyzed
- NIE Networks production schema (19 fields)
- 15 review focus filters specified
- Popup layout requirements defined
- What GridFlow should do better than Field Maps

**Validates Phase C C1-C4 independently.**

### 4. Final consolidated specification
**Source:** Pro_GridFlow_Electrical_Survey_Review_Final_Detailed_.docx (8,604 words, 782 lines)

**Key findings:**
- Consolidates all previous evidence
- 19 sections + 2 appendices
- Complete product specification
- Clear Stage 3 vs Stage 4 separation
- Domain validation questions identified
- Safe wording throughout

**This is the definitive GridFlow technical specification.**

---

## Phase C validation status

**ALL EVIDENCE SOURCES INDEPENDENTLY VALIDATE PHASE C C1-C4:**

| Operational Issue | Engineering Spec | Field Maps Evidence | Final Spec | Phase C Package |
|-------------------|------------------|---------------------|------------|-----------------|
| Context invisible | Secondary visual weight | Diamond symbols, muted colors | Context/access/crossing records | C1 ✅ |
| Height misleading | Measured vs. Specification | Existing/Proposed distinction | Proposed pole specification framework | C1 ✅ |
| Symbols unclear | Shape ≠ Color | Feature type decoupled from QA | Visual hierarchy system | C1+C2 ✅ |
| Stay missing | Angle poles without stays | Mechanical support validation | Stay evidence at angle poles | C3 ✅ |
| Span unclear | Anomaly detection | Route sequence confidence | Span anomaly detection | C4 ✅ |
| Data insufficient | Curated popups | Design-critical fields first | Popup organization | C1 ✅ |

**Status:** All 4 Phase C packages validated by 4 independent evidence sources.

---

## Phase C packages (ready to implement)

### C1: Feature-Type Filtering + Blank Field Framework (3-4 hours)
**Validates:** Context invisible, Height misleading, Symbols unclear, Data insufficient

**Scope:**
1. Feature-type filter buttons (existing/proposed/angle/stays/context/missing heights/missing specs/records with remarks)
2. Blank field framework (existing = measured height missing; proposed = specification missing; context = hide height)
3. Visual symbol overhaul (Shape = asset type, Color = QA status)
4. Popup reorganization (Identity → Physical → Electrical → Mechanical → Context → QA)

### C2: Asset Lifecycle Visualization (4-5 hours)
**Validates:** Symbols unclear (lifecycle states)

**Scope:**
1. 11 lifecycle states (existing/proposed/retained/recovered/replacement/repositioned/unmatched/suggested/confirmed)
2. Existing↔Proposed match visualization (dashed provisional lines)
3. Toggle layer on/off
4. Popup lifecycle section

### C3: Stay Evidence at Angle Poles (4-5 hours)
**Validates:** Stay missing

**Scope:**
1. Detect angle poles (>10° deviation OR function = "Angle")
2. Scan for stay records within 20m
3. Flag if missing: "⚠️ Angle pole — stay evidence not captured"
4. Show stay types where captured
5. Add filter: "Show angle poles missing stay evidence"

### C4: Span Anomaly Detection + Crossing Context (3-4 hours)
**Validates:** Span unclear

**Scope:**
1. Calculate 3D span distance
2. Flag <10m (probable duplicate/GPS error)
3. Flag >500m for 11kV/33kV (probable missing pole)
4. Better crossing labels ("Road Crossing — Critical clearance check required")
5. Add filters: "Show span anomalies" / "Show crossings requiring clearance"

**Total estimated time:** ~24 hours (Cursor work)

---

## Current counts

- **Tests passing:** 298 (up from 297)
- **DNO rulepacks:** 4 (SPEN, SSEN, NIE, ENWL)
- **Real files validated:** Gordon, 4-474, 513, 474c, Bellsprings EWM285
- **Evidence documents:** 4 comprehensive technical specifications
- **Phase C packages validated:** 4 (C1-C4)

---

## What changed recently

### Phase B implementation completed (2026-04-30)
- Package 4b: Dashboard cleanup (responsive layout, professional wording) ✅
- Package 4c: Terminology cleanup (survey-facing language) ✅
- Package 5a: Pairing cards (tablet-friendly responsive design) ✅
- 298 tests passing (up from 297)
- All commits pushed to master
- Pre-commit passing

### Evidence gathering completed (2026-04-30)
- Live operational feedback collected (6 critical map issues)
- Engineering analysis #1 received (15 pages, 17 sources)
- Field Maps + NIE validation received
- Final consolidated specification received (8,604 words)
- All evidence validates Phase C C1-C4 independently

### Repository organization completed (2026-04-30)
- 00_MASTER_ORGANIZATION.md created
- 01_QUICK_START.md created
- 02_REFERENCE_LIBRARY.md created
- 16 obsolete files archived to _archive/deprecated_docs_2026-04-30/
- All important files preserved and indexed

---

## Strategic position

**GridFlow now has:**
- ✅ Working MVP (Stage 3 complete)
- ✅ Professional terminology (Phase B complete)
- ✅ Complete technical specification (8,604 words)
- ✅ Independent validation (4 evidence sources)
- ✅ Clear Phase C scope (C1-C4 ready)
- ✅ Clear Stage 4 scope (structured capture deferred)

**Best current framing:**
- Internal workflow tool ✅
- Consultancy leverage asset ✅
- Narrow pre-CAD QA layer ✅

**Not yet:**
- Broad SaaS platform
- Major standalone utility business
- Fully mature DNO compliance product

---

## Main current decision point

**Phase C path choice:**

**Path 1 (Safe):** C1-C2 first → validate → then C3-C4 (6-8 weeks)
**Path 2 (Fast):** All C1-C4 together (4-5 weeks) ⭐ **RECOMMENDED**
**Path 3 (Conservative):** Minimal warnings → more evidence → full C1-C4 (6-7 weeks)

**Recommendation:** Path 2 (Fast)

**Rationale:**
- All 4 evidence sources validate all 4 packages
- Operational issues are design blockers, not polish
- Total work: ~24 hours (manageable for Cursor)
- No interdependencies preventing parallel work

---

## Known remaining issues

1. Phase C not yet implemented (waiting for approval)
2. P011 operational test not yet run (can validate Phase B + inform Phase C)
3. Stage 4 structured capture (planned but deferred until Phase C complete)
4. No cross-file chain merging within projects
5. No combined project-level map overlay
6. Stage 2 output still provisional (PoleCAD import schema not verified)
7. Advanced topology controls not yet built
8. Stage 4 tablet/photo workflows remain future roadmap

**These are correctly deferred or awaiting approval.**

---

## What is NOT blocked

- ✅ Phase C approval (all evidence gathered)
- ✅ Phase C implementation (Cursor ready, spec complete)
- ✅ P011 operational test (can run anytime)
- ✅ Stage 4 planning (after Phase C complete)

---

## Next checkpoint trigger

Update this file when:

- Phase C approval decision made
- Phase C implementation begins
- Phase C implementation completes
- P011 operational test completes
- Material change to project direction

---

## Expected next update

This file should next be updated when:

**Phase C approval is given and implementation begins**
