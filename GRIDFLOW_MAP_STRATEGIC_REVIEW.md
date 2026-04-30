# GridFlow Map Section — Comprehensive Strategic Review

**Analysis Date:** 2026-04-30
**Scope:** Current GridFlow map implementation vs. Field Maps evidence
**Purpose:** Identify gaps and prioritize Phase C improvements

---

## EXECUTIVE SUMMARY

### Current State: Good Foundation, Missing Critical Depth

GridFlow's map has made **excellent progress** in the last 4 weeks:
- ✅ Separated marker shape (feature type) from color (QA status)
- ✅ Collapsed long report sections to keep panel focused
- ✅ Added Review Focus filters
- ✅ Implemented design-chain span visualization
- ✅ Clear legend separating feature type and review status

### Critical Gap: Information Model Depth

However, GridFlow's current map **still falls short of Field Maps evidence** in one critical area:

**GridFlow shows WHAT is captured.**
**GridFlow should explain WHY each record matters for design.**

The Field Maps evidence revealed that surveyors capture 12 major feature areas. GridFlow currently shows only 5-6 of them clearly, and doesn't adequately link the raw data to design-critical requirements (stay evidence, height requirements, clearance evidence, etc.).

### Strategic Implication

**Phase C is not about more features. Phase C is about deeper meaning.**

GridFlow needs to become a **design-relevance interpreter**, not just a data visualizer.

---

## DETAILED COMPARISON: GridFlow vs. Field Maps

### 1. ASSET TYPE DISTINCTION

**Field Maps Strength:**
- Shows raw feature codes as captured (OBJECTID, Pole, Service Joint, etc.)
- Users must understand what each code means
- Very database-centric
- Lots of metadata noise

**GridFlow Current Implementation:**
```
✅ Marker shapes distinguish asset types:
  - EX (Existing pole) = Circle
  - PR (Proposed pole) = Square
  - A (Angle pole) = Rotated square
  - ST (Stay/anchor) = Triangle
  - CTX (Context/crossing) = Diamond
```

**Assessment:** GridFlow is BETTER than Field Maps for visual asset type distinction. ✅

**Gap:** Still doesn't explain *why* the asset type matters.
- Example: Angle pole shows "A" label. Surveyor sees the shape. But does the surveyor immediately know "Angles require stays, check if stay evidence exists"? Not obviously.

---

### 2. EXISTING VS. PROPOSED INFRASTRUCTURE

**Field Maps Approach:**
- Status field shows "E" (existing) or other values
- No visual distinction between existing/proposed/recovered/retained
- Raw database flag, not spatial relationship

**GridFlow Current Implementation:**
```
✅ Marker color shows QA status (Pass/Warn/Fail)
✅ Marker shape shows asset type
✅ Popup shows asset_intent field if present
⚠️ No spatial relationship visualization
⚠️ No clear "replacement pair" visual link
```

**Assessment:** GridFlow is BETTER for visual distinction, but MISSING the spatial relationship context.

**Critical Gap:** When a proposed pole is near an existing pole, GridFlow shows both separately. Field Maps also shows them separately. **But GridFlow doesn't visually link them as a replacement pair.**

Current implementation:
- Review page pairing table shows the link
- Map has a "Existing/proposed matches" filter
- But the filter is a *list* of matched records, not a *spatial* visualization

**Why this matters:**
- Designer needs to see: "This existing pole (circled) is being replaced by this proposed pole (nearby, linked)"
- Currently, designer clicks the filter, and the side panel shows them as separate records
- No line connecting them. No visual parenthesis saying "this cluster is one replacement decision"

---

### 3. LINE / SPAN / CONDUCTOR DETAILS

**Field Maps Limitation:**
- Captures conductor traces as lines
- Shows auto-calculated distances
- No semantic meaning ("Is this 11kV? Is this existing or proposed? What conductor type?")

**GridFlow Current Implementation:**
```
✅ Design chain spans visualized as blue lines
✅ Distance labels shown on hover/click
✅ "From Pole X to Pole Y" popup shows
⚠️ No conductor type shown
⚠️ No voltage level shown
⚠️ No "existing" vs "proposed" span distinction
⚠️ No anomaly highlighting (too-short or too-long spans)
```

**Assessment:** GridFlow shows the SPATIAL span route better than Field Maps, but MISSING semantic depth.

**Critical Gap:** The map shows "Surveyed route sequence" but doesn't answer:
- "Is this 11kV or LV?"
- "Is this the existing route or the proposed route?"
- "Does this span look anomalously short (possible duplicate) or long (possible missing pole)?"

---

### 4. STAY / ANCHOR INFORMATION

**Field Maps:**
- Stays captured as separate point records (code "Stay", "ST", etc.)
- Links to angle poles not explicit
- No validation that angle poles have corresponding stay records

**GridFlow Current Implementation:**
```
✅ Stay/anchor records shown with ST marker
✅ Review Focus filter exists for "Missing heights" (partially related)
❌ NO explicit "missing stay evidence at angle pole" check
❌ NO visual link between angle pole and nearby stay
❌ NO "this angle pole lacks documented stay" flag
```

**Assessment:** GridFlow shows stays exist, but MISSING the critical validation logic.

**Critical Gap:** This is a major design-readiness problem.

Currently, GridFlow doesn't answer:
- "Which angle poles have documented stay evidence?"
- "Which angle poles lack documented stay evidence (likely blocker for design)?"
- "Are there stays recorded without a linked angle pole (data quality issue)?"

**Evidence from Field Maps:** Stays are separate records. Surveyors capture them as points. But they're not inherently linked to the angle poles they support. **GridFlow should provide this link.**

---

### 5. CLEARANCES AND CROSSINGS

**Field Maps:**
- Crossing features captured as separate point records (Road, Stream, Building, etc.)
- No semantic link to the route
- No indication of measurement quality or design relevance

**GridFlow Current Implementation:**
```
✅ Context/crossing records shown with CTX diamond marker
✅ Can be filtered via "Review Focus"
⚠️ No height/clearance measurements shown
⚠️ No "missing clearance measurement" flag
⚠️ No visual indication of proximity to route
```

**Assessment:** GridFlow visualizes context records, but MISSING clearance-specific validation.

**Critical Gap:** Crossings are often the drivers of pole height or route changes.

Currently, GridFlow doesn't answer:
- "Which crossings have measured clearances?"
- "Which crossings are missing clearance measurements (blocker for design)?"
- "What is the closest crossing to each span (spatial risk)?"

---

### 6. CONTEXT / ENVIRONMENT / ACCESS FEATURES

**Field Maps:**
- Captured as point records (Hedge, Tree, Wall, Fence, Gate, Track, Stream, etc.)
- No semantic grouping by type
- Raw database dump

**GridFlow Current Implementation:**
```
✅ Context records displayed with CTX marker
✅ Grouped in popups by structure_type
⚠️ No layer-based filtering by context type
⚠️ No "show only trees" or "show only walls" filter
❌ No access/wayleave implication visualization
```

**Assessment:** GridFlow shows context exists, but MISSING context-specific filtering and implications.

**Critical Gap:** Different context types have different design implications.

Currently, designer can't easily answer:
- "Which trees are near the proposed route (clearance concern)?"
- "Which buildings are near the route (access/wayleave concern)?"
- "Which walls might block stay placement?"

---

### 7. SURVEY EVIDENCE AND MEDIA

**Field Maps:**
- Photos/attachments shown in records
- Remarks captured as text fields
- Raw form data (lots of empty/null fields)

**GridFlow Current Implementation:**
```
✅ Remarks shown in popup
✅ "Height not captured" warning shown for structural records
⚠️ No photo attachment visibility
❌ No indication of evidence quality/source
❌ No way to trace back to original field remark
```

**Assessment:** GridFlow shows remarks, but MISSING evidence-quality metadata.

**Critical Gap:** Designers need to know: "Was this height measured, estimated, or extracted from old records?"

Currently, GridFlow shows height value but doesn't indicate source confidence.

---

### 8. MAP LEGEND

**Current GridFlow Legend:**
```
Route Line: Surveyed route sequence
Feature Types: EX (existing), PR (proposed), A (angle), ST (stay), CTX (context)
Review Status: Pass (green), Review Required (yellow), Design Blocker (red)
```

**Assessment:** Good separation of feature type and review status. Clear design. ✅

**Gap:** Legend doesn't explain WHY each marker matters.
- "What does a red EX (existing pole) mean? Why is it a design blocker?"
- "What does ST (stay) mean in the context of the route design?"

---

### 9. SELECTED RECORD POPUP

**Current GridFlow Popup Shows:**
```
Point name/ID
Status badge
Record Type
Asset Intent (if present)
Height
Material
Remarks
Coordinates
Issues (if any)
Warnings (if any)
Relationship indicator (if replacement pair)
```

**Assessment:** Excellent design-facing popup. Shows exactly what a designer needs. ✅

**Gap:** Doesn't explain design requirements.
- Example popup shows: "Type: Angle, Status: Review Required"
- But doesn't say: "Angle poles require documented stay evidence. This one is missing stay documentation. Action: Check field notes or return to field."

---

### 10. REVIEW FOCUS FILTERS

**Current GridFlow Filters:**
```
Design blockers (shows FAIL records)
Review required (shows WARN records)
Existing/proposed matches (shows replacement_pair relationships)
Missing heights (shows records without height)
```

**Assessment:** Good set of practical filters. Matches design questions. ✅

**Gap:** Missing survey-specific filters.

Field Maps evidence shows designers also need:
- "Show missing stay evidence at angle poles"
- "Show missing clearance measurements at crossings"
- "Show missing material specifications"
- "Show records with remarks (likely important)"
- "Show overlapping records (duplicate or error)"

---

### 11. MARKER OVERLAP HANDLING

**Current GridFlow Implementation:**
```
Detects overlapping coordinates to 4 decimal places
Shows note: "Note: N location(s) have overlapping markers — zoom in to separate them"
```

**Assessment:** Good awareness of the problem. ✅

**Gap:** No solution for overlapping markers.

Field Maps evidence shows overlapping records often indicate:
- Duplicate surveys
- Same location, different assets (e.g., pole + stay anchor)
- Data quality issues

GridFlow should offer:
- Expand/spiderfy visualization
- Separate list view for overlapping records
- Indicate whether overlap is expected (pole + stay) or problematic (duplicate)

---

### 12. DESIGN READINESS CONTEXT

**Current GridFlow:**
```
✅ Readiness verdict (LIKELY READY / PARTIALLY READY / NOT READY)
✅ Reasons listed
✅ Coverage breakdown (height coverage, material coverage, etc.)
✅ Evidence gates
✅ Circuit summary (structural/context/anchor counts)
```

**Assessment:** Excellent high-level readiness summary. ✅

**Gap:** Doesn't explain design implications per record.

Example: A height missing on a 1-meter context record is irrelevant. A height missing on a proposed pole is a design blocker. Currently, the popup shows "Height: not captured" for both, without context.

---

## FIELD MAPS EVIDENCE: WHAT GRIDFLOW SHOULD LEARN

### From Field Maps Evidence Review:

**Field Maps captures these feature areas:**
1. ✅ Pole/support structure identity (pole number, material, type)
2. ✅ Existing/proposed status flags
3. ✅ Conductor traces and geometry
4. ✅ Stay/anchor records as separate points
5. ✅ Crossing/context features as separate points
6. ✅ Remarks and field notes
7. ✅ Photo attachments
8. ⚠️ Design-critical relationships (poorly visualized)
9. ⚠️ Evidence quality (not tracked)
10. ❌ Design-readiness implications (not captured)

### What GridFlow Does Better:
- **Separates feature type from QA status** ✅
- **Shows design readiness verdict** ✅
- **Flags missing critical data** ✅
- **Collapses unneeded report detail** ✅

### What GridFlow Is Missing:
- **Explicit spatial relationships** (existing pole → proposed replacement)
- **Design-critical validation links** (angle pole → stay evidence)
- **Feature-type-specific filtering** (show only trees, show only walls)
- **Evidence-quality indicators** (measured vs. estimated vs. legacy)
- **Design implication explanations** (why this record matters for design)
- **Overlap handling** (visually separate and explain)
- **Span anomaly detection** (too short, too long, missing poles)

---

## PHASE C: RECOMMENDED PRIORITY

Based on this analysis, **Phase C should prioritize these improvements in this order:**

### Tier 1: Critical Design Logic (Should implement in Phase C)

1. **Existing/Proposed Replacement Pairs — Visual Link**
   - Difficulty: Medium
   - Value: High
   - Implementation: Draw light line between matching existing/proposed poles when "Existing/proposed matches" filter active
   - Why: Designers need to see the replacement decision spatially, not in a side panel

2. **Stay Evidence at Angle Poles — Design-Relevance Linking**
   - Difficulty: Medium
   - Value: High
   - Implementation: Highlight angle poles without nearby stay records as "WARN: Missing stay evidence"
   - Why: Critical for mechanical design. Stay placement is often a blocker

3. **Feature-Type-Specific Filtering**
   - Difficulty: Low
   - Value: Medium
   - Implementation: Add filters for: Existing poles, Proposed poles, Angle poles, Stays/anchors, Trees, Walls, Tracks, Streams, Buildings, Gates
   - Why: Designers need to inspect specific asset categories without noise

4. **Span Anomaly Detection**
   - Difficulty: Medium
   - Value: Medium
   - Implementation: Flag spans >500m (possible missing pole) or <10m (possible duplicate) in "Review Focus" filter
   - Why: Surveyors may have missed intermediate poles or captured duplicates

### Tier 2: Designer Experience (Should implement in Phase C if time)

5. **Evidence Quality Metadata**
   - Difficulty: Low
   - Value: Medium
   - Implementation: Add "Source: Measured / Estimated / Legacy" indicator in popups
   - Why: Designers need to know confidence level of captured data

6. **Overlap Handling — Expand/Spiderfy**
   - Difficulty: Medium
   - Value: Low
   - Implementation: Expand overlapping markers into visible cluster when zoomed
   - Why: Currently overlapping markers hide real data

### Tier 3: Future (Beyond Phase C)

7. **Design Implication Explanations**
   - Difficulty: Medium
   - Value: Medium
   - Implementation: Popup should explain "Why this record matters: [...]"
   - Why: Helps less-experienced designers understand survey meaning
   - Defer: Requires more context/configuration

8. **Traversal Links** (Existing pole → popups linked stay records)
   - Difficulty: High
   - Value: Low
   - Implementation: Allow clicking "angle pole" to show nearby stays
   - Defer: Nice-to-have, not critical for current workflow

---

## IMPLEMENTATION ROADMAP FOR PHASE C

### If Starting Phase C Now:

**Package C1: Existing/Proposed Replacement Pair Visual Link** (3-4 hours)
- When "Existing/proposed matches" filter is active, draw light connecting line between matched pairs
- Update legend to show "Replacement pair link"
- Test with P010 and P011

**Package C2: Stay Evidence at Angle Poles** (4-5 hours)
- Detect angle poles within 20m of no stay records
- Flag with "WARN: Missing stay evidence at this angle pole"
- Add to "Review Focus" filters
- Test with jobs that have angle poles

**Package C3: Feature-Type Filtering** (3-4 hours)
- Add filter buttons for: Existing poles, Proposed poles, Angle poles, Stays, Trees, Walls, Tracks, Streams
- Keep current pass/warn/fail filters
- Test filtering combination

**Total Phase C Research + Implementation:** ~24-30 hours

---

## VERDICT

**GridFlow's map is architecturally sound, visually clear, and already better than Field Maps for design review.**

**But GridFlow is missing the logical connectors that make survey data actionable for design.**

The next phase should focus on making these connections explicit:
- Existing pole → Proposed replacement (visual link)
- Angle pole → Stay evidence (validation check)
- Route span → Anomaly indicator (quality gate)

**This transforms GridFlow from "here's your data visualized" to "here's what your data means for design."**

---

## FIELD MAPS EVIDENCE SUMMARY

Field Maps taught us:
✅ Raw data is captured granularly (asset by asset, point by point)
✅ Relationships are implicit, not explicit (angle pole + stay are separate records)
✅ Designers must mentally link these records to design meaning
❌ Field Maps doesn't help with that mental linking

GridFlow should fill this gap.
