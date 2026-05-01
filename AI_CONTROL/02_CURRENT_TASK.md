# Current Task

## Domain Accuracy & Electrical Data Model Implementation

**Status:** PHASE 2 COMPLETE (D2-A through D2-D) — Phase 3 awaits approval
**Timeline:** Phase 1 (5-7 days) ✅ → Phase 2 (10-14 days) — started → Phase 3 (5-7 days)
**Total:** 4-5 weeks / 130-160 hours

---

## Current Priority

**PHASE 1: Emergency Domain Fixes — SHIPPED**

**Packages:**
1. ✅ D1-A: Asset Classification Fix (BT pole → third-party) — `b6dbc7c`
2. ✅ D1-B: Height Source Validation — `e618590`
3. ✅ D1-C: Source Confidence & Legacy Data Warnings — `f30ef46`
4. ✅ D1-D: Third-Party Infrastructure & Attachments — `6349ebd`

**Next:** Phase 3 integration & validation after review (see `PHASE_2_3_ROADMAP.md`).

---

## Critical Problems Being Fixed

### Problem 1: BT Pole Misclassification
**Current:** Point 72 "bt pole" classified as "EXpole being replaced"
**Impact:** Designer thinks it's part of electric network to replace
**Fix:** Classify as third-party telecoms infrastructure

### Problem 2: Height Source Missing
**Current:** "Measured Height: 6.5m" but "Height Source: not captured"
**Impact:** Can't trust height for clearance calculations
**Fix:** Enforce height_source field (measured RTK/tape/estimated/plan)

### Problem 3: Legacy Data Not Flagged
**Current:** "Source Confidence: legacy map data" shown as regular field
**Impact:** Designer doesn't know geometry is unverified
**Fix:** Add ⚠️ LEGACY MAP DATA — NOT FIELD VERIFIED warning banner

### Problem 4: Third-Party Attachments Invisible
**Current:** No tracking of BT/streetlight/customer attachments on poles
**Impact:** Construction planning misses coordination requirements
**Fix:** Parse and display third-party attachments with owner/impact

---

## Evidence Base

**Research Documents (2 weeks of work):**
- UK Electrical Grid Survey Data Capture Report (4,544 words)
- UK Electrical Grid Survey Capture Model and GridFlow Gap Analysis
- Real operational evidence (BT pole Point 72, missing conductor data)

**All specifications validated against:**
- ESQCR requirements
- ENA G81 standards
- ENWL underground record guidance
- Ofgem CNAIM condition assessment
- Esri Field Maps best practice

---

## Phase 1 Deliverables

**After Phase 1 complete:**

✅ **Asset Classification:**
- BT/Openreach poles → third-party telecoms infrastructure
- Streetlights → local authority infrastructure
- Customer poles → customer-owned
- Electric network poles → DNO structural

✅ **Height Source Validation:**
- Height source required for existing poles
- Confidence levels: survey-grade/mapping-grade/unverified
- Legacy/estimated heights flagged for field verification

✅ **Source Confidence Framework:**
- Provenance types: field_observed_rtk/gnss, dno_gis, legacy, drawing, inferred
- Geometry trust: survey-grade/mapping-grade/unverified/indicative
- Legacy data warning banner in popups

✅ **Third-Party Attachments:**
- Telecoms, streetlight, customer service, signage, CCTV detection
- Owner and coordination impact visible
- Construction planning flags

---

## Files Created/Modified This Session

**Specifications:**
- ✅ `CURSOR_DOMAIN_ACCURACY_COMPLETE_IMPLEMENTATION.md` — Complete Phase 1 implementation (15,000+ words)
- ✅ `PHASE_1_EMERGENCY_DOMAIN_FIXES.md` — Phase 1 execution guide
- ✅ `PHASE_2_3_ROADMAP.md` — Phases 2-3 summary roadmap
- ✅ `AI_CONTROL/02_CURRENT_TASK.md` — This file (updated)

**Implementation Files (will be created by Cursor in Phase 1):**
- `app/asset_classifier.py` (new)
- `app/routes/map_preview.py` (modified)
- `app/qa_engine.py` (modified)
- `app/static/js/map-viewer.js` (modified)
- `app/static/style.css` (modified)

---

## Execution Protocol

### Phase 1 Execution — COMPLETE

All four packages implemented, tested (`pytest` full suite green), committed, and pushed.

### Phase 2 Execution — COMPLETE

**Delivered:** Full electrical data model packages D2-A–D2-D (schema, equipment, connectivity QA, survey metadata).

Packages:
- ✅ D2-A: Conductor/Cable Electrical Schema (`app/electrical_schema.py`, intake/map merge, `conductor_hv_overhead` QA WARN, popup electrical rows)
- ✅ D2-B: Equipment & Pole-Top Configuration (equipment taxonomy, ratings/kVA parsing, pole-top/earthing/plate, Equipment & pole-top popup section)
- ✅ D2-C: Network Connectivity & Relationships (from/to support IDs, stay parent, cable endpoints, linkage QA; Network links popup section)
- ✅ D2-D: Survey Metadata & Provenance (GNSS/capture enrichment, survey job ref, limitations; Survey metadata popup section; INFO-level advisory QA)

### Phase 3 Execution (After Phase 2 validates)

**NOT STARTED YET** — Waiting for Phase 2 completion

Packages:
- D3-A: Backend Data Model Integration
- D3-B: Frontend Display & Forms
- D3-C: Validation Rules & QA Engine
- D3-D: Export & Handoff Quality

---

## What NOT to Do

- ❌ Do NOT skip testing after each package
- ❌ Do NOT proceed to next package without approval
- ❌ Do NOT start Phase 3 before Phase 2 scope is agreed
- ❌ Do NOT add features outside Phase 1 scope
- ❌ Do NOT modify files not listed in package spec

---

## Success Criteria

**Phase 1 complete when:**
- ✅ All 4 packages implemented (D1-A, D1-B, D1-C, D1-D)
- ✅ All 300+ tests passing
- ✅ Manual validation on Gordon, Bellsprings, P010, P011 successful
- ✅ Screenshots confirm all acceptance criteria met
- ✅ All packages committed and pushed to GitHub
- ✅ BT pole correctly classified
- ✅ Height source enforced
- ✅ Legacy data clearly flagged
- ✅ Third-party attachments visible

---

## Next Checkpoint

Update this file when:
- Package D1-A completes
- Package D1-B completes
- Package D1-C completes
- Package D1-D completes
- Phase 1 completes
- Phase 2 approved to begin
- Material change to priorities

---

**Expected next update:** Phase 3 approval or operational validation on Phase 2 popups and QA
