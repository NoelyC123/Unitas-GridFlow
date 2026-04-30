# Phase B Packages — Field Maps-Informed Improvements

**Status:** Ready for Cursor Implementation
**Context:** Field Maps evidence validates terminology and feature prioritization
**Tests:** 297 passing (baseline)

---

## Package 4b: Projects List Cleanup

### Goal
Make the Projects page quick to scan. Long project descriptions clutter the view.

### Changes

**In `/projects/` list view:**

1. Shorten project descriptions to 1-2 lines maximum
   - Current: Long text (several lines)
   - New: Short summary only
   - Example: "Gordon Overhead Route — Survey and Design Review" (one line)

2. Show only essential info per project:
   - Project name
   - File count
   - Last modified date
   - Status badge

3. Move longer descriptions and details to the individual project page
   - Users click project → see full details there
   - List view stays scannable

### Validation

- Test `/projects/` with both desktop and mobile widths
- Confirm you can quickly see all projects at a glance
- All 297 tests passing

### Effort
**2-3 hours**

### Why This Matters (Field Maps Connection)

Field Maps evidence shows surveyors need to quickly scan available data. GridFlow's Projects list should support the same pattern — quick overview, detailed inspection on demand.

---

## Package 4c: Terminology Cleanup

### Goal
Ensure consistent, design-facing language across all user-facing surfaces.

### Changes

**Replace these terms wherever they appear to users:**

| Current Term | Replacement | Why |
|---|---|---|
| "Auto-matched existing poles" | "Suggested existing/proposed matches" | Avoids implying confirmation |
| "Existing/proposed proximity signals" | "Suggested matches" or "Potential replacement matches" | More practical engineering language |
| "EXpole" (raw code) | "Existing pole (EXpole)" | Explain code, don't expose it alone |
| "Proximity signals" (in summaries) | "Distance matches" or "Suggested matches" | Clearer practical meaning |
| Any remaining "QA" jargon | Survey/design equivalent | Match Field Maps terminology |

**Affected surfaces:**
- Dashboard
- Review page
- Map labels and filters
- Popups
- PDF exports
- Design Chain/Working View exports

### Validation

- Test against P010/F001 to confirm terminology is consistent
- Run pytest: 297 should still pass
- Browser smoke check across all pages

### Effort
**1 hour** (text-only changes)

### Why This Matters (Field Maps Connection)

Field Maps uses practical engineering terminology (existing pole, proposed pole, angle pole, stay, context, etc.). GridFlow should align with this terminology for designer trust.

---

## Package 5a: Pairing Table Layout Fix

### Goal
Fix the pairing table action column that is clipped or squeezed.

### Problem
The Review page pairing table's right-hand confirmation column is partly cut off, especially on smaller screens. This is the main review action — it must be fully visible.

### Solutions (Choose Best Approach)

**Option 1: Wider responsive table**
- Use full page width
- Reduce column padding
- Use horizontal scroll with clear indicator if needed
- Test at multiple widths

**Option 2: Card layout (Recommended)**
- Convert table to card grid (similar to Batch 4a dashboard)
- Each card shows: existing pole, proposed match, distance, action button
- Cards stack responsively
- All actions always visible

**Option 3: Sticky action column**
- Keep action column visible while horizontal scroll happens
- May work well if other columns scroll

### Changes

**At minimum:**
1. Pairing table action column must be fully visible without clipping
2. Works on desktop (1200px+), tablet (768px), and mobile widths
3. All pairing functionality preserved (confirm/choose/unmatched dropdown works)
4. Confirm button/dropdown always accessible

### Validation

- Test Review page at multiple widths (desktop, tablet, mobile)
- Confirm pairing actions work correctly
- Run pytest: 297 should pass
- Browser smoke check on `/review/project/P010/F001`

### Effort
**3-4 hours** (responsive design work)

### Why This Matters (Field Maps Connection)

Field Maps requires quick interaction with records. GridFlow's pairing review — the most important designer action — must be immediately accessible without difficulty or clicking through layers.

---

## Execution Sequence

### Phase B Order (Recommended)

**Day 1:**
1. Give Cursor Package 4b (Projects cleanup)
2. Test P010
3. Commit when done

**Day 2:**
4. Give Cursor Package 4c (Terminology cleanup)
5. Test P010
6. Commit when done

**Day 3:**
7. Give Cursor Package 5a (Pairing table layout)
8. Test P010
9. Test with P011 (another real job) if available
10. Commit when done

---

## After Phase B Complete

### Field Maps Validation Phase (Research Only)

Once Phase B is complete and committed:

**Step 1: Review Field Maps Evidence**
- Read the Field Maps screenshots and evidence
- Identify actual feature categories (pole types, stays, context, crossings, etc.)
- Note how existing/proposed/recovered/context are distinguished in Field Maps

**Step 2: Validate Terminology Choices**
- Do our Phase 4c terminology changes align with Field Maps?
- Are there Field Maps terms we should adopt or adapt?
- Any conflicts or alignment opportunities?

**Step 3: Identify Phase C Candidates**
From the 12 feature areas, prioritize:
1. Which are most important for current operational use?
2. Which are missing from current app?
3. Which can be added within Stage 3 boundaries?
4. Which require Stage 4/5/6 work?

**Step 4: Create Phase C Package Definitions**
- Based on Field Maps evidence + P010 findings
- Prioritized by operational impact
- Clear success criteria

### Phase C Timeline
- Research: 2-4 hours
- Implementation: 10-16 hours (spread across multiple batches)
- Testing: Continuous with real jobs (P011, P012, etc.)

---

## Success Criteria

### After Package 4b
- ✅ Projects list is quick to scan
- ✅ Project names, file counts, dates visible at a glance
- ✅ Detailed notes move to project detail page

### After Package 4c
- ✅ Terminology consistent across all surfaces
- ✅ "Suggested" replaces "auto-matched"
- ✅ "Existing pole (EXpole)" format used
- ✅ No raw codes exposed without explanation

### After Package 5a
- ✅ Pairing table action column fully visible
- ✅ All actions accessible without clipping
- ✅ Works at multiple screen widths
- ✅ Pairing functionality preserved

### After Full Phase B
- ✅ Dashboard responsive (4a) ✅
- ✅ Projects list scannable (4b) ✅
- ✅ Terminology consistent (4c) ✅
- ✅ Pairing review actions accessible (5a) ✅
- ✅ 297 tests passing
- ✅ P010 and P011 both test cleanly

---

## Command Template For Cursor

When you're ready, give Cursor:

```
Read /Users/noelcollins/Unitas-GridFlow/P010_PHASE_B_PACKAGES.md

Implement Package [NUMBER]: [TITLE]

(See full package definition in the document above)
```

---

## Field Maps Integration Note

These packages are designed to work **with** Field Maps evidence, not replace it.

After Phase B is complete, we'll use Field Maps evidence to inform Phase C improvements.

The goal is not to copy Field Maps, but to use Field Maps as evidence of:
- Real feature categories surveyors capture
- How existing/proposed/context assets are actually distinguished
- What terminology designers expect
- What information matters most for design

This evidence-driven approach ensures GridFlow becomes genuinely useful for survey-to-design handoff, not just a generic GIS viewer.
