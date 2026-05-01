# PHASE 1: EMERGENCY DOMAIN FIXES — COMPLETE SPECIFICATION

**Status:** READY FOR CURSOR EXECUTION
**Timeline:** 5-7 days / ~40 hours
**Priority:** CRITICAL — Fixes fundamental domain classification errors

---

## 📋 PHASE 1 PACKAGES

**Package D1-A:** Asset Classification Fix (1-2 days)
**Package D1-B:** Height Source Validation (1-2 days)
**Package D1-C:** Source Confidence & Legacy Data Warnings (1-2 days)
**Package D1-D:** Third-Party Infrastructure & Attachments (1-2 days)

---

## 🎯 WHAT PHASE 1 DELIVERS

**Before Phase 1:**
❌ BT pole classified as "EXpole being replaced"
❌ Height without source = unreliable for clearance calcs
❌ Legacy map data not flagged as unverified
❌ Third-party attachments invisible

**After Phase 1:**
✅ BT poles correctly classified as third-party telecoms infrastructure
✅ Height source enforced (measured RTK vs estimated vs not captured)
✅ Legacy data clearly flagged with ⚠️ NOT FIELD VERIFIED warnings
✅ Third-party attachments tracked (BT, streetlight, customer service)
✅ Source confidence visible (field-observed vs DNO GIS vs drawing vs inferred)

---

## PACKAGE D1-A: ASSET CLASSIFICATION FIX

**SEE:** `/Users/noelcollins/Unitas-GridFlow/CURSOR_DOMAIN_ACCURACY_COMPLETE_IMPLEMENTATION.md`
**Lines:** 1-600 (already written)

**Summary:**
- Create `app/asset_classifier.py` with telecoms/streetlight/customer detection logic
- Classify BT/Openreach poles as third-party infrastructure (not electric network)
- Add third-party popup layout with ⚠️ warnings
- Prevent third-party assets counting as structural poles
- Add infrastructure_owner, classification_confidence fields

**Acceptance Criteria:**
- ✅ BT pole shows "Third-Party Telecoms Pole (BT/Openreach)"
- ✅ Popup has warning banner: "NOT part of electric network"
- ✅ Designer Action: "EXCLUDE from electric network design"
- ✅ BT pole NOT counted in structural pole statistics

---

## PACKAGE D1-B: HEIGHT SOURCE VALIDATION

**SEE:** `/Users/noelcollins/Unitas-GridFlow/CURSOR_DOMAIN_ACCURACY_COMPLETE_IMPLEMENTATION.md`
**Lines:** 601-900 (already written)

**Summary:**
- Add height_source field (measured RTK/PPK/tape, estimated, from plan, not captured)
- Create classify_height_confidence() function (high/medium/low/unknown)
- Add Height Source and Height Confidence to popups
- Validate: existing poles with height but no source → WARNING
- Validate: existing poles with no height → BLOCKER

**Acceptance Criteria:**
- ✅ Popup shows "Height Source: measured_rtk" vs "not captured"
- ✅ Height Confidence: ✓ High confidence (survey-grade) vs ⚠ Low confidence
- ✅ Legacy/estimated heights flagged: "Field verification required"
- ✅ Missing height on existing pole = BLOCKER issue

---

## PACKAGE D1-C: SOURCE CONFIDENCE & LEGACY DATA WARNINGS

**SEE:** `/Users/noelcollins/Unitas-GridFlow/CURSOR_DOMAIN_ACCURACY_COMPLETE_IMPLEMENTATION.md`
**Lines:** 901-1200 (already written)

**Summary:**
- Create classify_source_confidence() with provenance types:
  - field_observed_rtk, field_observed_gnss, field_observed
  - dno_gis_import, legacy_map_data, digitised_from_drawing
  - proposed_by_design, inferred, unknown
- Add legacy data warning banner to popups
- Add Source & Confidence popup section
- Visual distinction for legacy data records (orange border + banner)

**Acceptance Criteria:**
- ✅ Legacy data shows ⚠️ LEGACY MAP DATA — NOT FIELD VERIFIED banner
- ✅ Popup shows: Data Provenance, Confidence Level, Geometry Trust
- ✅ Legacy poles have visual border + warning styling
- ✅ Source confidence warnings: "Field verification required before design"

---

## PACKAGE D1-D: THIRD-PARTY INFRASTRUCTURE & ATTACHMENTS

**SEE:** `/Users/noelcollins/Unitas-GridFlow/CURSOR_DOMAIN_ACCURACY_COMPLETE_IMPLEMENTATION.md`
**Lines:** 1201-1400 (already written)

**Summary:**
- Create parse_attachments() function
- Detect telecoms, streetlight, customer service, signage, CCTV
- Add Third-Party Attachments popup section
- Show owner, impact, coordination requirements
- Flag coordination_required for construction planning

**Acceptance Criteria:**
- ✅ Pole with "streetlight" in remarks shows attachment
- ✅ Popup shows: 💡 streetlight, Owner: Local Authority
- ✅ Impact: "LA coordination required if pole replacement planned"
- ✅ Coordination Required: Yes flag visible

---

## 🧪 PHASE 1 TESTING PROTOCOL

**After each package:**

1. Run `pytest -v` — all tests must pass
2. Load real job (Gordon, Bellsprings, P010, P011)
3. Manually verify package acceptance criteria
4. Take screenshots showing fixes working
5. Commit with clear message
6. Report completion before next package

**After all Phase 1 packages:**

1. Load job with BT pole (Point 72)
2. Verify BT pole correctly classified
3. Load pole with legacy map data
4. Verify legacy warning banner visible
5. Load pole with height but no source
6. Verify height source warning
7. Load pole with streetlight attachment
8. Verify attachment section visible
9. Run full test suite
10. Take comprehensive screenshots
11. Commit Phase 1 complete

---

## 📝 PHASE 1 COMMIT MESSAGES

**D1-A:**
```
D1-A: Asset classification fix

- Create asset_classifier.py with telecoms/streetlight/customer detection
- Classify BT/Openreach poles as third-party infrastructure
- Add third-party popup layout with clear warnings
- Prevent third-party assets counting as structural poles

Fixes critical BT pole misclassification issue.
All tests passing.
```

**D1-B:**
```
D1-B: Height source validation

- Add height_source field to map_data properties
- Create classify_height_confidence() function
- Add Height Source and Height Confidence to popups
- Validate height source for existing poles
- Flag legacy/plan heights for field verification

Enforces height source reliability for clearance calculations.
All tests passing.
```

**D1-C:**
```
D1-C: Source confidence & legacy data warnings

- Create classify_source_confidence() with provenance types
- Add legacy data warning banner (⚠️ NOT FIELD VERIFIED)
- Add Source & Confidence popup section
- Visual distinction for legacy data records

Makes data provenance visible to designers.
All tests passing.
```

**D1-D:**
```
D1-D: Third-party attachments handling

- Add parse_attachments() function
- Detect telecoms/streetlight/customer/signage/CCTV
- Add Third-Party Attachments popup section
- Show owner, impact, coordination requirements

Makes third-party dependencies visible.
All tests passing.
```

**Phase 1 Complete:**
```
Phase 1 complete: Emergency domain fixes

DELIVERABLES:
✅ D1-A: Asset classification (BT pole fixed)
✅ D1-B: Height source validation
✅ D1-C: Source confidence & legacy warnings
✅ D1-D: Third-party attachments

RESULTS:
- BT poles correctly classified as third-party infrastructure
- Height source enforced (measured vs estimated vs legacy)
- Legacy data flagged with clear warnings
- Third-party attachments tracked and visible

VALIDATION:
- Tested on Gordon, Bellsprings, P010, P011
- All 300+ tests passing
- Screenshots confirm fixes working

Phase 1 timeline: 5-7 days
Ready for Phase 2: Complete Electrical Data Model
```

---

## 🚀 CURSOR START COMMAND FOR PHASE 1

**Copy this exact command to Cursor:**

```
Phase 1 Emergency Domain Fixes approved for immediate execution.

Read complete specification:
/Users/noelcollins/Unitas-GridFlow/PHASE_1_EMERGENCY_DOMAIN_FIXES.md

AND read detailed implementation instructions:
/Users/noelcollins/Unitas-GridFlow/CURSOR_DOMAIN_ACCURACY_COMPLETE_IMPLEMENTATION.md
(Focus on lines 1-1400 for Phase 1 packages)

CRITICAL EXECUTION RULES:
1. Execute packages in exact order: D1-A, D1-B, D1-C, D1-D
2. Test after EACH package (pytest -v must pass)
3. Manually verify acceptance criteria after each package
4. Take screenshots showing fixes working
5. Commit after each package with provided message
6. Report completion with screenshots after each package
7. WAIT for approval before proceeding to next package

START NOW with Package D1-A: Asset Classification Fix

Timeline: 1-2 days for D1-A
Goal: Fix BT pole misclassification to third-party infrastructure

All code examples, logic, and testing steps are in the specifications.
Begin implementation immediately.
```

---

**END OF PHASE 1 SPECIFICATION**
