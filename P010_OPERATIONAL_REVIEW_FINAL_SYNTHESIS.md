# P010 Final Operational Review — Prioritized Improvements

**Date:** 2026-04-30
**Evidence:** Real user (domain expert) operational review of P010/Gordon after Packages 1-3
**Status:** Packages 1-3 complete and validated. Dashboard, Review page, and Map improvements shipped.

---

## Executive Summary

**Overall Assessment:** Packages 1-3 significantly improved the UI from technical/internal language to professional engineering language. The app now feels like a design-readiness tool, not a software debug panel.

**Remaining Work:** Two focused improvement areas remain:
1. **Dashboard layout** — Projects list and Survey Files table need responsive redesign
2. **Map markers and filters** — Need clearer asset type distinction and better overlap handling

**Strategic Recommendation:** Implement Package 4 (dashboard layout) immediately. Defer Package 5 (advanced map features) pending Field Maps evidence and operational use.

---

## What Packages 1-3 Achieved

### ✅ Package 1: Dashboard Terminology
- Expanded "P/W/F" to "Pass / Warning / Fail"
- Changed "Issues" to "QA findings"
- Added provisional warning banner
- Clear processing vs. design-readiness separation

### ✅ Package 2: Map Asset Symbols
- **Critical improvement:** Markers now expose asset type visually
- Marker shape = feature type (EX/PR/A/ST/CTX/etc.)
- Color = QA status (Pass/Warning/Fail)
- Legend separates feature type from review status
- Commit: `ab535a9`

### ✅ Package 3: Map Panel Focus
- Long report sections collapsed behind "Report details" disclosure
- Map panel stays inspection-focused
- Key readiness verdict kept visible
- Commit: `9eb1720`

---

## Outstanding Issues Identified

### TIER 1: Important (Should Fix Soon)

#### 1. Dashboard Table Too Wide
**Issue:** Survey Files row/action buttons clipped or squeezed
**Impact:** Users can't see status and actions clearly after upload
**Root Cause:** Wide table layout doesn't adapt to screen size

**Improvement:**
- Use responsive file-card layout instead of wide table
- Show key info (name, records, status) on each card
- Actions visible without horizontal scroll
- Works on desktop and tablet

**Effort:** 4-6 hours (Cursor can do this)

---

#### 2. Projects List Too Text-Heavy
**Issue:** Long project descriptions clutter the Projects page
**Impact:** Page is hard to scan; users can't quickly see project list

**Improvement:**
- Keep only short summary in list (1-2 lines)
- Move detailed notes into project page itself
- Quick visual scan of all projects

**Effort:** 2-3 hours

---

#### 3. "Auto-matched existing poles" Sounds Too Certain
**Issue:** Wording implies match is confirmed
**Impact:** Users may trust proximity matches more than they should

**Change:**
- "Auto-matched" → "Suggested existing/proposed matches"
- Or: "Proximity-suggested matches"
- Emphasize these are signals only, not proven

**Effort:** 1 hour (text-only change)

---

#### 4. "Existing/proposed proximity signals" Too Technical
**Issue:** Sounds like algorithm language, not practical engineering
**Impact:** Surveyors/designers need clear language

**Change:**
- "Proximity signals" → "Suggested matches" or "Potential replacement matches"
- Use "distance matches" in some contexts

**Effort:** 1 hour (text-only change)

---

#### 5. Pairing Table Action Column Clipped
**Issue:** Right-hand confirmation column partly cut off
**Impact:** Main review action is obscured

**Improvement:**
- Wider layout for pairing table
- Sticky action column (stays visible while scrolling)
- Or card layout instead of table
- Clear horizontal scroll indicator

**Effort:** 3-4 hours

---

### TIER 2: Important, Can Be Deferred

#### 6. Pairing Rows Need Match Reason/Confidence
**Issue:** Rows show distance but not confidence or why match was chosen
**Impact:** 1.5m match and 8.8m match feel equally reliable

**Improvement:**
- Add "nearest proposed pole" indicator
- Confidence level (High/Medium/Low)
- "View on map" link per row
- Distance alone is not enough evidence

**Effort:** 4-5 hours (requires pairing logic inspection)

---

#### 7. "Section break point" Needs Explanation
**Issue:** Unclear what number means or why route is split
**Impact:** Unexplained route sections may confuse users

**Improvement:**
- Add helper text explaining what "section break" means
- Or hide if not essential to workflow
- Or rename to "Route section" with context

**Effort:** 2-3 hours (if kept) or minimal (if hidden)

---

#### 8. Pairing Review Needs Evidence Reminder
**Issue:** Reviewer can mark pairings reviewed without checklist
**Impact:** May skip checking against map/notes/field evidence

**Improvement:**
- Add short evidence checklist before marking reviewed
- Prompt: "Have you checked: map position, Field Maps, survey notes, design judgment?"
- Optional but encouraged

**Effort:** 2-3 hours (can be deferred to later phase)

---

### TIER 3: Map Improvements (Requires Field Maps Evidence Validation)

#### 9. Asset Types Still Need Clearer Distinction
**Issue:** EX and PR labels improved, but existing/proposed still blend when markers overlap
**Impact:** Designers must click every marker to see what is existing vs. proposed

**Improvement:**
- Make asset types more visually distinct
- Marker shapes clear for: EX (existing), PR (proposed), A (angle), ST (stay/anchor), CTX (context)
- Easy visual scan without clicking

**Validation Needed:** Field Maps evidence review first
**Effort:** 6-8 hours (after Field Maps validation)

---

#### 10. Marker Overlap Handling
**Issue:** Many records overlap along route
**Impact:** Overlaps are where replacement/proposed relationships matter most, but hard to inspect

**Improvement:**
- Expand/spiderfy markers on overlap
- "Overlapping records" filter
- Selected-location list view
- Link pairing table to map location

**Validation Needed:** Field Maps evidence review first
**Effort:** 8-12 hours (complex feature, requires Field Maps validation)

---

#### 11. Map Legend and Filter Expansion
**Issue:** Current filters useful but limited
**Impact:** Survey/design users can't isolate specific field categories

**Improvement:**
- Add filters for: existing poles, proposed poles, angle poles, stays, context/crossing, overlapping records, records with remarks, missing heights
- Separate feature-type filters from QA-status filters

**Validation Needed:** Field Maps evidence review first
**Effort:** 4-6 hours

---

#### 12. Route/Electrical Meaning
**Issue:** Blue line doesn't state if it's proposed 11kV, LV, OHL, or just record sequence
**Impact:** Electrical route meaning matters for design

**Improvement:**
- Label as "Proposed OHL route" only where data supports it
- Otherwise: "Surveyed route sequence — conductor type not captured"
- Only label if evidence is present

**Effort:** 2-3 hours (text + conditional logic)

---

### TIER 4: Minor (Polish, Lower Priority)

#### 13. "EXpole" Should Be Explained
**Issue:** Raw code appears without plain-English meaning
**Impact:** Designer-facing pages should explain survey codes

**Change:**
- Show "Existing pole (EXpole)" instead of just "EXpole"
- Or "EX" for short with tooltip

**Effort:** 1 hour

---

#### 14. Popups Could Be More Design-Facing
**Issue:** Show useful data but could better explain design relevance
**Impact:** Clicked marker should tell user what it is and what action is needed

**Improvement:**
- Plain-English feature type
- Raw code in brackets for reference
- Asset role/function
- Height/remarks
- QA finding
- Suggested action
- Likely match if relevant

**Effort:** 3-4 hours

---

#### 15. "Surveyed route sequence" Caveat
**Issue:** Route line may look like confirmed design route
**Impact:** If generated from survey order, users need to know it's provisional

**Improvement:**
- Add helper text: "Generated from ordered survey records — check against route evidence"

**Effort:** 1 hour

---

## Implementation Sequence

### Phase A: Dashboard Layout Fixes (Next - Highest ROI)

**Batch 4a: Dashboard Table Responsiveness**
- Convert Survey Files table to responsive file-card layout
- Show: name, records count, QA status, action buttons
- Visible without horizontal scroll
- Effort: 4-6 hours

**Batch 4b: Projects List Cleanup**
- Shorten project descriptions in list
- Move details to project page
- Effort: 2-3 hours

**Batch 4c: Terminology Cleanup**
- "Auto-matched" → "Suggested"
- "Proximity signals" → "Suggested matches"
- "EXpole" → "Existing pole (EXpole)"
- Effort: 1 hour

**Why First:**
- High visibility (dashboard is first page users see)
- High impact on usability
- Quick wins (responsive design improves multiple issues)
- No complex logic changes needed

---

### Phase B: Pairing Table Improvements (After Phase A)

**Batch 5a: Pairing Table Layout Fix**
- Fix clipped action column
- Make table responsive or convert to card layout
- Effort: 3-4 hours

**Batch 5b: Pairing Evidence Checklist (Optional)**
- Add reminder checklist before marking reviewed
- Low complexity, high value
- Can be deferred
- Effort: 2-3 hours

---

### Phase C: Map Advanced Features (After Field Maps Evidence Review)

**Batch 6: Field Maps Alignment Research** (Research Only)
- Review Field Maps evidence for feature categories
- Identify how existing/proposed/angle/stay/context are shown in Field Maps
- Validate terminology choices
- Document findings

**Only proceed to implementation after research complete.**

---

## Success Criteria

### After Phase A (Dashboard)
- ✅ Survey Files table/cards visible without horizontal scroll
- ✅ Projects list quick to scan
- ✅ Terminology consistent and professional
- ✅ P010 dashboard feels clean and organized

### After Phase B (Pairing Table)
- ✅ Pairing action column fully visible
- ✅ All pairing data accessible
- ✅ Workflow clear and efficient

### After Phase C (Map Features)
- ✅ Asset types clearly distinguishable visually
- ✅ Overlapping records handled well
- ✅ Filters support real survey/design workflows
- ✅ Map feels like an engineering inspection tool

---

## What NOT To Do

### ❌ Don't Build These Yet

- ❌ Photo upload / tablet capture (Stage 4)
- ❌ PoleCAD export (not validated yet)
- ❌ Advanced map editing (section boundaries, sequencing)
- ❌ User accounts / role-based access (Stage 6)
- ❌ Hosted deployment (not operational yet)

### ❌ Don't Change These

- ❌ QA algorithms or sequencing logic
- ❌ Data model or export structure
- ❌ Core pairing detection algorithm

---

## Cursor-Ready Work Packages

### Phase A: Dashboard Layout Fixes

**Package 4a Command:**
```
Read /Users/noelcollins/Unitas-GridFlow/P010_OPERATIONAL_REVIEW_FINAL_SYNTHESIS.md

Implement Phase A → Batch 4a: Dashboard Table Responsiveness

The goal is to make the Survey Files section visible without horizontal scrolling.

Current: Wide table that requires scrolling to see action buttons
Target: Responsive file-card layout that shows all key info at a glance

Cards should show: file name, records count, QA status (Pass/Warning/Fail counts), action buttons (Review/Map/PDF/Design Chain/Working View)

Keep all functionality - this is layout and responsiveness only.

Test against P010/F001. Make sure the layout works on both desktop and tablet widths.
```

**Package 4b Command:**
```
Read /Users/noelcollins/Unitas-GridFlow/P010_OPERATIONAL_REVIEW_FINAL_SYNTHESIS.md

Implement Phase A → Batch 4b: Projects List Cleanup

The goal is to make the Projects page quick to scan.

Current: Long project descriptions clutter the view
Target: Short summaries in the list, full details available on project page

For each project, show only: project name, file count, last modified date, status
Move longer descriptions into the project detail page.

Keep all functionality - this is presentation only.

Test the Projects page to make sure you can quickly see all projects at a glance.
```

**Package 4c Command:**
```
Read /Users/noelcollins/Unitas-GridFlow/P010_OPERATIONAL_REVIEW_FINAL_SYNTHESIS.md

Implement Phase A → Batch 4c: Terminology Cleanup

Replace these terms throughout the app (dashboard, review page, map, exports):

1. "Auto-matched existing poles" → "Suggested existing/proposed matches"
2. "Existing/proposed proximity signals" → "Suggested matches" (or "Potential replacement matches")
3. "EXpole" → "Existing pole (EXpole)" when shown to users
4. "proximity signals" → "distance matches" where appropriate

Keep all functionality - this is wording only.

Test against P010/F001 to confirm terminology is consistent across pages.
```

---

## Next Decision Points

### After Phase A Complete
**Ask:** Does P010 dashboard feel clean and professional now? Test with another real job (P011).

### After Phase B Complete
**Ask:** Is pairing review workflow smooth and all controls visible?

### Before Phase C Implementation
**Ask Claude Desktop:** Review Field Maps evidence and validate map improvement approaches before implementing Phase C features.

### After Operational Use With Multiple Jobs
**Ask Claude Desktop:** Based on 5-10 real jobs, is Stage 3 operationally solid, or more polish needed?

---

## Overall Strategic Position

**Stage 3 Status:**
- ✅ Functionally complete (intake, QA, review, map, exports all working)
- ✅ Packages 1-3 shipped (terminology, asset symbols, panel focus improved)
- ⏳ Packages 4-5 pending (dashboard layout, pairing table, terminology)
- ⏳ Phase C deferred pending Field Maps evidence review

**Operational Readiness:**
- After Phase A+B: Ready for operational use on real jobs
- After Phase C: Map becomes powerful spatial inspection tool

**Timeline:**
- Phase A: 7-10 hours total (can be done in 1-2 Cursor sessions)
- Phase B: 5-7 hours (can follow immediately after Phase A)
- Phase C: 2-4 hours research + 10-16 hours implementation (after evidence review)

---

## Immediate Recommendation

**Proceed with Phase A (Dashboard) immediately:**

1. Give Cursor Packages 4a, 4b, 4c one at a time
2. Test P010 after each package
3. Test with another real job (P011) when Phase A complete
4. Then decide: continue with Phase B, or pause for operational use feedback?

**This keeps momentum while staying within Stage 3 boundary and evidence-driven development.**
