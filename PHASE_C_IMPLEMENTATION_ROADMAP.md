# Phase C Implementation Roadmap — Your Specification + My Analysis

**Status:** Ready to brief Cursor
**Source:** Your Field_Maps_Evidence_Led_GridFlow_Specification.docx + GRIDFLOW_MAP_STRATEGIC_REVIEW.md
**Duration:** ~24 hours of focused implementation
**Testing Ground:** P010/P011 + operational evidence

---

## PHASE C: 4 FOCUSED PACKAGES

### Package C1: Feature-Type Classification & Filtering (3-4 hours)
**Goal:** Let designers filter by what asset type they want to review

**What to build:**
- Add 8 feature-type filter buttons: Existing poles, Proposed poles, Angle poles, Stays, Context/crossings, Missing heights, Missing stays (new), Missing clearance (new)
- Per feature type, hide irrelevant blank fields in popups
- Show design-critical blanks prominently with explanation (e.g., "Height: Not captured - required for design")
- Your 4-category blank field framework (applicable/not applicable/missing/unclear)

**Acceptance:**
- All 8 filters work and show/hide correct records
- Popup shows design-relevant fields only
- Missing critical data has clear flag

---

### Package C2: Asset Lifecycle Visualization (4-5 hours)
**Goal:** Show designers the lifecycle of each asset (existing → proposed → retained/replaced/recovered)

**What to build:**
- Update map markers to show your 7 asset states:
  - Existing pole (current symbol: circle)
  - Proposed pole (current symbol: square)
  - Retained pole (existing symbol + subtle badge?)
  - Replaced/recovered pole (existing symbol + "replacement" badge)
  - Failed/decayed pole (existing symbol + "condition" badge)
  - Repositioned pole (existing symbol + "moved" badge)
  - Suggested match (provisional label)
- Draw light connecting line between existing ↔ proposed replacement pairs when viewing them
- Popup shows asset lifecycle state clearly
- Add filter: "Existing/proposed matches" (already exists, but enhance with line visualization)
- Add filter: "Unmatched existing poles" (ready for designer review)

**Acceptance:**
- Visual distinction between all 7 states in popups
- Replacement pairs have connecting line when highlighted
- "Provisional" vs. "Confirmed" status is clear

---

### Package C3: Stay Evidence at Angle Poles (4-5 hours)
**Goal:** Flag angle poles lacking documented stay evidence (critical for mechanical design)

**What to build:**
- Detect angle poles within 20m of no stay records → flag as "WARN: Missing stay evidence"
- Popup text for angle poles without stays: "Stay evidence not captured in digital survey file. Check field notes, photos or plan evidence."
- Add filter button: "Missing stay evidence"
- Your stay types (angle, terminal, T-off, heavy duty, double, tandem) — show where captured
- Show stay direction/bearing in popup when present
- Detect stays without linked angle pole (data quality flag)

**Acceptance:**
- Angle poles without stays show warning
- Filter isolates all angle poles lacking stay evidence
- Popup explains what to do (check field notes)
- Test against P010 (Gordon has angle poles)

---

### Package C4: Span & Crossing Context Enrichment (3-4 hours)
**Goal:** Make span anomalies and crossing evidence visible to designers

**What to build:**
- Span anomaly detection:
  - Flag spans > 500m (possible missing intermediate pole)
  - Flag spans < 10m (possible duplicate)
  - Add filter: "Span anomalies"
- Crossing/clearance context:
  - Better labels for context types (Road, Stream, Building, Tree, Wall, etc.)
  - Show in popup: crossing type + distance from route
  - Flag: "Clearance measurement not captured" on context records near span
  - Add filter: "Missing clearance evidence at crossings"
- Route proximity analysis:
  - Identify crossings within 5m of span (design-critical proximity)

**Acceptance:**
- Anomalous spans are flagged in filter
- Crossing types are clear in popup and legend
- Missing clearance measurements are highlighted
- Test against real route data

---

## IMPLEMENTATION ORDER

### Option A: Sequential (Safe Path)
1. **Weeks 1-2:** Cursor implements C1 + C2 (foundation, testing with P010)
2. **Week 3:** Real job operational test (P011 or similar)
3. **Weeks 4-5:** Cursor implements C3 + C4 based on operational feedback

### Option B: Concurrent (Fast Path)
1. **Weeks 1-3:** Cursor implements C1 + C2 + C3 in parallel
2. **Week 4:** Operational test
3. **Week 5:** C4 + polish

### Option C: Minimal First (Conservative Path)
1. **Week 1:** Just strengthen popup warnings (your "Minimal Next Improvement")
2. **Weeks 2-4:** Operational evidence gathering
3. **Weeks 5+:** Full C1-C4 based on validated evidence

---

## WHAT TO TELL CURSOR

```
Read these in order:
1. NOEL_NOTES_ANALYSIS_SYNTHESIS.md (strategic overview)
2. Field_Maps_Evidence_Led_GridFlow_Specification.docx (your spec — this IS the product definition)
3. GRIDFLOW_MAP_STRATEGIC_REVIEW.md (my code gap analysis)
4. PHASE_C_IMPLEMENTATION_ROADMAP.md (this file — implementation tasks)

Your job: Implement C1 + C2 first (~7-8 hours)

C1 = Feature-type filtering (3-4 hrs)
C2 = Asset lifecycle visualization (4-5 hrs)

Test against:
- P010/F001 (Gordon_Pt1) — check angle poles, replacement pairs, span distances
- Local UI inspection — filters work, popups show correct fields, warnings appear

Do NOT start C3 or C4 until Noel reviews C1+C2 output and confirms against P010/P011 operational evidence.
```

---

## SUCCESS CRITERIA FOR PHASE C

✅ C1 complete: 8 feature-type filters work, popups show design-relevant fields
✅ C2 complete: All 7 asset states visible in popups, replacement pairs have visual link
✅ Tested: P010 and at least one other job reviewed through new filters
✅ Ready for C3: Designer feedback collected on which filters are most useful

**Phase C is done when:** Designers can answer these questions using the map alone:
1. "Which assets are existing? Proposed? Being replaced?"
2. "Which angle poles lack documented stays?"
3. "Which crossings lack clearance measurements?"
4. "Which spans look anomalously long or short?"

---

## KEY PRINCIPLE (From Your Specification)

> "Field Maps captures field reality. GridFlow should interpret that field reality for office/design review."

**Phase C's job:** Make that interpretation explicit in every filter, popup, and layer.

Not "here's your data visualized."
Instead: "Here's what your data means for design, and here's what's missing."

---

## SCHEDULE RECOMMENDATION

**Given that Phase B (Projects/Pairing) is ready to go:**

- **Option 1 (Recommended):** Finish Phase B first (~1-2 weeks), then do Phase C with fresher evidence
- **Option 2 (If evidence-driven now):** Pause Phase B, do Phase C foundation (C1-C2) immediately, re-evaluate with P011 before C3-C4

**My recommendation:** **Option 1**
- Finish Phase B (Projects cleanup, terminology fixes)
- Get P011 through the pipeline
- Start Phase C with that operational evidence in hand
- Total timeline: ~4-5 weeks to Phase C completion

**Your call:** Which would you prefer? 🚀
