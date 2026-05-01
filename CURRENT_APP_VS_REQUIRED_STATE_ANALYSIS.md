# Current App vs. Required State Analysis

**Date:** 2026-05-01
**Purpose:** Honest assessment of what exists now vs. what your two documents require
**Status:** Phase C (C1-C4) complete, now analyzing gaps

---

## EXECUTIVE SUMMARY

**You're absolutely right to pause.**

**Current GridFlow shows ~8-12 fields per popup.**

**Your survey research requires 35+ fields per popup.**

**The gap is 3-4x larger than current implementation.**

This is NOT a minor polish. This is a **data model expansion** that changes GridFlow from:
- **"Narrow QA gatekeeper"** (current)
- To **"Professional survey display platform"** (survey research describes)

**Both your documents are correct. But they describe different scope levels.**

---

## WHAT EXISTS NOW (Phase C Complete)

### Current Popup Fields (~8-12 fields)

**From analyzing `map-viewer.js` popups:**

**Basic Identity:**
1. Point number / Pole ID
2. Structure type (EXpole/PRpole/Pol/Angle/Stay/Context)
3. Record status (PASS/WARN/FAIL)

**Limited Physical:**
4. Height (if captured)
5. Material (if captured)

**Lifecycle/Design:**
6. Asset intent (existing/proposed)
7. Lifecycle state (being replaced, proposed replacement, etc.)
8. Relationship (replacement pair signal)

**QA/Warnings:**
9. Issue texts (design blockers)
10. Warning texts (review required)
11. Missing height warning (existing poles)
12. Missing specification warning (proposed poles)
13. Stay evidence status (angle poles only)
14. Span anomaly flags
15. Context/crossing labels

**Evidence:**
16. Remarks (name field, if different from ID)
17. Coordinates (implicit)

### Current Map UX

**What works:**
✅ 15 filter buttons (existing, proposed, angle, stays, context, etc.)
✅ Lifecycle visualization (dashed match lines, recovered styling)
✅ Stay evidence warnings at angle poles
✅ Span anomaly detection (<10m, >500m)
✅ Context/crossing meaning ("Road Crossing — Critical clearance check")
✅ Pass/Warn/Fail visual distinction
✅ Right panel with stats + filters

**What Phase C review identifies as problems:**
❌ Markers too large (visual clutter)
❌ Layers vs filters mixed (need Map Layers + Review Filters separation)
❌ EX/PR distinction weak (shape + color both needed)
❌ Angle hides lifecycle (shows "A" but not whether existing/proposed)
❌ Context records compete visually (should be secondary)
❌ Match warnings too long (should be visual + short text)
❌ **Popups lack electrical survey detail** (CRITICAL GAP)

---

## WHAT YOUR SURVEY RESEARCH REQUIRES

### Required Popup Fields (35+ fields per pole)

**From UK_Electrical_Grid_Survey_Data_Capture_Report.docx:**

**Identity (5 fields):**
1. Asset ID/pole number
2. Point number
3. Feature code
4. Asset status (existing/proposed/retained/recovered/replaced)
5. DNO area/circuit ID

**Physical Structure (12 fields):**
6. Measured height (existing) / Specification (proposed)
7. Pole class/strength
8. Material
9. Condition (good/fair/poor/unsafe)
10. Decay/rot evidence
11. Pole-top condition
12. Lean direction
13. Lean severity
14. Birthmark details
15. Defect type (rot/split/burn/impact/etc.)
16. Foundation/ground condition
17. Action required

**Electrical/Network (8 fields):**
18. Voltage carried
19. Circuit type
20. Number of phases
21. Conductor type
22. Pole-top arrangement
23. Crossarm type
24. Insulator type
25. Transformer/switch/fuse/recloser presence
26. Equipment ratings
27. Asset plate information
28. Earthing

**Mechanical Support (7 fields):**
29. Stay required (yes/no)
30. Stay existing (yes/no)
31. Stay type
32. Anchor location/bearing/direction
33. Stay condition
34. Stay insulator
35. Strut present

**Attachments/Third-Party (3 fields):**
36. Telecoms attachment
37. Streetlight
38. Customer service/other utility

**Access/Environment (5 fields):**
39. Access route
40. Gate/fence issue
41. Landowner/wayleave issue
42. Vegetation/tree proximity
43. Ground condition/traffic management

**Evidence (6 fields):**
44. Full pole photo (linked)
45. Pole-top photo (linked)
46. Defect photo (linked)
47. Stay/anchor photo (linked)
48. Asset plate photo (linked)
49. Surveyor/date
50. GNSS accuracy
51. Remarks/notes

**Design Notes/QA (variable):**
- Missing measured height
- Missing specification
- Missing material/condition
- Missing stay evidence
- Unconfirmed match
- Clearance concerns
- Access constraints

**TOTAL: 50+ possible fields**

---

## THE GAP ANALYSIS

### Current vs Required

| Category | Current Fields | Required Fields | Gap |
|----------|---------------|-----------------|-----|
| Identity | 3 | 5 | +2 |
| Physical | 2 | 12 | +10 |
| Electrical | 0 | 8 | +8 |
| Mechanical | 1 (stay evidence yes/no) | 7 | +6 |
| Attachments | 0 | 3 | +3 |
| Access/Environment | 0 | 5 | +5 |
| Evidence | 1 (remarks) | 6 | +5 |
| Design/QA | 6 | ~10 | +4 |
| **TOTAL** | **~12** | **~50+** | **+38** |

**The popup data model needs to grow 4x.**

---

## WHAT YOUR PHASE C REVIEW REQUIRES (Immediate)

**From GridFlow_Phase_C_Map_Review_Detailed_Report_2026-05-01.docx:**

### Map UX Improvements (2-4 weeks):

1. **Reduce marker size** (25-40% smaller)
2. **Split right panel** into Map Layers + Review Filters
3. **Finalize symbol standard:**
   - EX = existing (square, dark grey/blue)
   - PR = proposed (circle, bright blue/green)
   - A = angle OVERLAY (not replacement)
   - ST = stay/anchor (triangle)
   - CTX = context (diamond, muted/secondary)
4. **Angle as overlay:** Existing angle = EX marker + A badge
5. **Shorten match warnings:** "Suggested replacement link — unconfirmed"
6. **Context visually secondary:** Smaller, muted, layer-controlled
7. **Update map key** with real symbol examples

### Modest Popup Expansion (add 10-15 key fields):

**Your Phase C review says existing pole popup should show:**
- Point number ✅ (have)
- Pole number/asset ID ✅ (have)
- Status ✅ (have)
- **Measured height** (add - already partly there)
- **Pole class** (add)
- **Material** (add)
- **Condition** (add - good/fair/poor/unsafe)
- **Voltage carried** (add)
- **Conductor type** (add)
- **Stay present** (add - yes/no)
- **Stay type** (add - if yes)
- **Lifecycle/design action** ✅ (have - being replaced, linked proposed pole)
- **Remarks** ✅ (have)
- **Photos** (add - link indicator)
- **Coordinates** ✅ (have)
- **Missing height/material/condition/stay warnings** (add)

**This adds ~10 fields to existing pole popup.**

---

## THE CRITICAL DECISION

### Option 1: Phase C2/D = UX Polish + Modest Expansion (2-4 weeks)

**Implement Phase C review recommendations:**
- Map UX fixes (markers, symbols, layers panel)
- **Add 10-15 key fields** from survey research
- Keep as **narrow QA gatekeeper with better display**
- Prove this level works on real jobs
- Defer full 50-field model to Stage 4

**Fields to add (10-15 priority picks from survey research):**
1. Pole class/strength
2. Material (expand current)
3. Condition (good/fair/poor/unsafe)
4. Voltage carried
5. Conductor type
6. Stay present (yes/no)
7. Stay type (if yes)
8. Lean (direction/severity)
9. Defects (rot/split/burn)
10. Equipment presence (transformer/switch/fuse)
11. Photo indicators (linked, not uploaded)
12. Surveyor/date
13. GNSS accuracy
14. Action required
15. Wayleave/access notes

**This brings popups from 12 → 25 fields** (still professional, not overwhelming)

---

### Option 2: Full Survey Research Implementation (6-12 months)

**Implement complete 50-field data model:**
- All identity, physical, electrical, mechanical, attachments, environment, evidence fields
- Asset-specific popup layouts (existing vs proposed vs angle vs stay vs context)
- Evidence management (photo linking, sketches)
- Asset relationships (parent pole, from/to spans, stay anchors)
- GIS/Field Maps parity
- **This is Stage 4/5 work**

**Timeline:** 6-12 months

**This changes GridFlow from narrow QA to professional survey platform.**

---

## MY HONEST ASSESSMENT

### What Your Two Documents Tell Me:

**Phase C Review (3,924 words):**
- Says: "Phase C intelligence good, map cluttered, popups too thin"
- Wants: Better UX + modest expansion (10-15 more fields)
- Timeline: 2-4 weeks
- **This is Stage 3 polish**

**Survey Research (4,544 words):**
- Says: "Here's everything an electrical survey captures"
- Shows: Complete 50-field data model
- Timeline: 6-12 months to implement fully
- **This is Stage 4/5/6 specification**

### Both Are Correct, But Different Scopes

**Your Phase C review** recommends **Phase C2/D refinement** (2-4 weeks):
- Map UX improvements
- Add 10-15 key fields
- Prove narrow QA + professional display works

**Your survey research** specifies **Stage 4/5** (6-12 months):
- Full 50-field model
- Evidence management
- Asset relationships
- GIS parity

---

## MY RECOMMENDATION

### Do Phase C2/D (Phase C Review Scope) First:

**2-4 weeks of work:**

1. **Map UX improvements** (from Phase C review):
   - Reduce marker size
   - Map Layers + Review Filters panel split
   - Better EX/PR symbols (shape + color)
   - Angle as overlay
   - Context visually secondary
   - Shorter match warnings

2. **Modest popup expansion** (pick 10-15 from survey research):
   - Add: class, material, condition, voltage, conductor, stay presence, stay type, lean, defects, equipment, photos, surveyor, accuracy, action, wayleave
   - **Brings popups from 12 → 25 fields**
   - **Professional but not overwhelming**

3. **Validate on real jobs:**
   - Test on P010, P011, Gordon, Bellsprings
   - Collect designer feedback
   - **Prove Stage 3 + professional display works**

### Then Decide Stage 4:

**After Phase C2/D validates:**
- If works well → plan Stage 4 (full 50-field model, 6-12 months)
- If gaps found → more Phase C refinement
- If good enough → polish + document, stay narrow QA

---

## BOTTOM LINE

**Current state:**
- Phase C (C1-C4) complete ✅
- 300 tests passing ✅
- Popups show ~12 fields ✅
- Map UX needs improvement ❌
- **Missing 38 fields from survey research** ❌

**Your Phase C review:**
- Wants map UX fixes + modest expansion (10-15 fields)
- **This is 2-4 weeks of work**
- **This keeps GridFlow as narrow QA + professional display**

**Your survey research:**
- Specifies complete 50-field model
- **This is 6-12 months of work**
- **This makes GridFlow a survey platform**

**My strong recommendation:**
1. **Do Phase C2/D first** (2-4 weeks - Phase C review scope)
2. **Validate on real jobs**
3. **Then decide Stage 4** (6-12 months - survey research scope)

**Don't jump to full survey platform without proving professional display works first.**

---

## NEXT STEP

**If you agree with Phase C2/D approach:**

1. I create **Phase C2/D Specification** combining:
   - Map UX improvements (Phase C review)
   - 10-15 priority fields to add (from survey research)
   - Asset-specific popup layouts
   - Timeline + implementation plan

2. You review spec

3. Cursor implements Phase C2/D

4. Validate on real jobs

5. Then decide Stage 4

**Waiting for your decision.** 🎯
