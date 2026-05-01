# Cursor Brief — Phase B Implementation (2026-04-30)

**To:** Cursor (Implementation Tool)
**From:** Claude Desktop + Noel (Orchestration)
**Task:** Implement Phase B packages (4b, 4c, 5a) — UI polish based on real operational evidence
**Timeline:** 6-8 hours total
**Status:** ✅ Fully specified, ready to execute

---

## YOUR ROLE & CONSTRAINTS

### What You Do
- ✅ Implement code changes for Phase B packages
- ✅ Run tests after every change (pytest -v)
- ✅ Commit and push when done
- ✅ Report blockers or unexpected issues

### What You Don't Do
- ❌ Scope expansion (stick to these 3 packages only)
- ❌ Architecture changes (terminology/layout only)
- ❌ Stage 4 work (not yet — requires evidence)
- ❌ Redesign core logic (QA algorithms unchanged)

---

## PROJECT CONTEXT (Read These First)

### Required Reading (10 minutes)
1. **AI_CONTROL/00_PROJECT_CANONICAL.md** — What this project is
2. **AI_CONTROL/01_CURRENT_STATE.md** — Current state (Stage 3 complete)
3. **AI_CONTROL/02_CURRENT_TASK.md** — Your current task
4. **AI_CONTROL/03_WORKING_RULES.md** — How to work

### Reference (Optional but Useful)
- **P010_PHASE_B_PACKAGES.md** — Detailed package breakdown
- **01_QUICK_START.md** — Quick navigation guide
- **GRIDFLOW_MAP_STRATEGIC_REVIEW.md** — Why these changes matter

---

## PHASE B OVERVIEW

### What Is Phase B?

**Goal:** Reframe GridFlow UI from **internal QA language** to **survey/design workflow language**

**Why:** Real operational testing (P010/Gordon) showed designers need to see survey-relevant information, not technical debug terms.

**Evidence:** Fibrus Field Maps + real job validation (P010/Gordon)

### The Three Packages

| Package | Focus | Time | Priority |
|---------|-------|------|----------|
| **4b** | Projects/Dashboard List | 2-3 hrs | First |
| **4c** | Terminology Cleanup | 1 hr | Second |
| **5a** | Pairing Table Layout | 3-4 hrs | Third |

**Total: ~6-8 hours**

---

## PACKAGE 4b: PROJECTS LIST CLEANUP (2-3 hours)

### What This Is

The dashboard shows a list of survey files. Currently it's cramped and uses internal language.

### What Needs Fixing

1. **Dashboard layout** — Table too cramped, needs responsive card grid
2. **Top summary** — "39 Issues" is unprofessional without context
3. **"Status" column** — Ambiguous (vs. "needs review" vs. "complete")
4. **"P/W/F" abbreviation** — Unclear to new users
5. **"Rulepacks" plural** — Should be singular
6. **Action buttons** — Require horizontal scroll on some widths

### Required Changes

```
FILE: app/templates/dashboard.html

1. Replace table layout with responsive card grid
   - Cards show: Name, Record Count, QA Status, Design Readiness, Action Buttons
   - Cards stack on mobile, grid on desktop
   - No horizontal scroll needed

2. Change top summary from:
   "1 Files / 157 Poles / 39 Issues / SPEN_11kV Rulepacks"
   To:
   "Processing complete / Survey records: 157 / QA findings: 39
    (25 warnings, 4 fails) / Rulepack: SPEN 11kV"

3. Rename "Status" column to "Processing Status" with tooltip:
   "Complete = GridFlow has processed. Designer review still needed."

4. Expand "P/W/F" to "Pass / Warning / Fail":
   Display as badge counts: "126 Pass | 25 Warning | 4 Fail"

5. Change "Rulepacks" → "Rulepack" (singular)

6. Keep "Needs review" badge but add helper:
   "Raw survey intake requires office review"

7. Add design-readiness statement below summary:
   "GridFlow has processed this file. Survey is provisional and
    requires review before design export is final."
```

### Test This Package

```bash
pytest -v tests/test_routes_dashboard.py
# All tests must pass

# Browser check:
# - Open http://localhost:5000/
# - Check P010/F001 loads without horizontal scroll
# - Verify all fields visible on tablet width
```

### Success Criteria
- ✅ No horizontal scroll on dashboard
- ✅ "39 Issues" is contextualized professionally
- ✅ "P/W/F" is clear to new users
- ✅ All tests pass
- ✅ P010/F001 renders cleanly on desktop + tablet

---

## PACKAGE 4c: TERMINOLOGY CLEANUP (1 hour)

### What This Is

Find and replace internal GridFlow jargon with survey/design workflow language throughout the app.

### Required Changes

**Find/Replace (Global Search)**

| Find | Replace With | Where | Why |
|------|---|---|---|
| "Design Chain" | "Proposed route" or "Surveyed route sequence" | Map overlay labels, summary text | Designer language, not internal jargon |
| "Design Handoff Sign-off" | "Pairing Review Status" | Review page section titles | Clearer purpose |
| "QA Status / Reviewed Link" | "Reviewer-confirmed relationship" | Table column headers | Designer-facing language |
| "Proximity QA" | "Likely pole matches" | Filter/legend labels | Survey language |
| "Evidence Gates" | "Design readiness checks" | Dashboard/report language | User-facing language |
| "code" (pole ID column) | "Existing survey record" | Table headers | Clarity |
| "Nearby Proposed Pole" | "Likely proposed match" | Table headers | Clarity |

### Files to Update

```
app/templates/dashboard.html        (summary, terminology)
app/templates/review.html           (section titles, labels)
app/templates/map_viewer.html       (legend, overlay labels)
app/routes/dashboard.py             (flash messages, helper text)
app/routes/review.py                (page descriptions)
app/routes/map_preview.py           (layer descriptions)
```

### Test This Package

```bash
pytest -v
# All tests must pass (297 tests)

# Manual check:
# - Open each page in browser
# - Verify terminology is professional, not technical
# - No incomplete replacements (check for context)
```

### Success Criteria
- ✅ All terminology replaced consistently
- ✅ No technical jargon remains
- ✅ All tests still pass
- ✅ Pages feel design-ready, not admin/technical

---

## PACKAGE 5a: PAIRING TABLE LAYOUT (3-4 hours)

### What This Is

The "Pairing Review" section (existing/proposed pole matches) has unclear purpose and poor layout.

### Current Problem

1. **Section title confusing** — "Existing / Proposed Pole Proximity QA" is technical
2. **No guidance text** — Designers don't know whether distance alone confirms matches
3. **Dropdown unclear** — What does "confirm match" actually do?
4. **Table headers cryptic** — "Code", "Nearby Proposed Pole" are not clear
5. **Wrong position** — "Design Handoff Sign-off" appears before Review/Map/PDF review

### Required Changes

```
FILE: app/templates/review.html

1. Rename section:
   From: "Existing / Proposed Pole Proximity QA"
   To:   "Likely Existing-to-Proposed Pole Matches"

   Add guidance text below title:
   "These are possible replacement/repositioning links based on proximity.
    Do not confirm based on distance alone. Check map position, Field Maps
    attributes, survey notes, and design judgment."

2. Improve table column headers:
   "Code" → "Existing survey record"
   "Nearby Proposed Pole" → "Likely proposed match"
   "QA Status / Reviewed Link" → "Reviewer-confirmed relationship"

3. Clarify dropdown action labels:
   Option A: "Confirm suggested match"
   Option B: "Choose different proposed pole"
   Option C: "No proposed replacement / unmatched"

   (Keep the logic same, just clearer labels)

4. Rename "Design Handoff Sign-off" section to:
   "Pairing Review Status"

   Change wording from:
   "Ready to export"
   To:
   "Pairings reviewed - existing/proposed relationships checked"

5. Add note:
   "Final design handoff sign-off happens after Review/Map/PDF/Exports
    all checked"
```

### Test This Package

```bash
pytest -v tests/test_routes_review.py
# All tests must pass

# Browser check:
# - Open review page for P010/F001
# - Verify table renders without scroll
# - Test dropdown actions (confirm/change/unmatched)
# - Check that pairing status is clear
```

### Success Criteria
- ✅ Section purpose is obvious to designer
- ✅ Guidance text present (check with notes)
- ✅ Dropdown actions unambiguous
- ✅ Table headers clear
- ✅ Pairing review is appropriately positioned in workflow
- ✅ All tests pass

---

## WORKING PROCEDURE FOR CURSOR

### Start Each Package

1. **Read the package specification** (above)
2. **Open the files** listed in "Files to Update"
3. **Make the changes** specified (code, layout, text)
4. **Run tests:** `pytest -v`
5. **Check browser:** Open http://localhost:5000/ and test manually
6. **Commit:** `git add . && git commit -m "Package X: description" && git push`

### If Tests Fail

1. **Read the error** carefully
2. **Check if it's your change** or a pre-existing issue
3. **Fix the code** or **revert the change**
4. **Run tests again**
5. **If stuck:** Report the error and we'll debug

### If Unsure About Implementation

1. **Check the specification** above (most questions are answered)
2. **Look at existing code** for patterns
3. **Test in browser** to see if it looks right
4. **If still unsure:** Ask before committing

---

## IMPORTANT REMINDERS

### ✅ Do This
- Read the spec carefully before implementing
- Run `pytest -v` after **every** change
- Test in browser on different widths (desktop, tablet, mobile)
- Commit frequently (don't batch huge changes)
- Keep git history clean (good commit messages)

### ❌ Don't Do This
- Add new features not in the spec
- Change core logic (QA algorithms, pairing detection)
- Redesign more than specified
- Skip testing
- Commit without green tests
- Work on Stage 4 (field capture, photos, GPS)

---

## NEXT AFTER PHASE B

**Do NOT start Phase C yet.**

After Phase B is complete:

1. **Test with real job** (P011 operational run-through)
2. **Collect feedback** (does it feel more professional?)
3. **Report findings** to Noel
4. **Wait for decision** on Phase C path + timing

Phase C is **4 packages** (C1-C4) for map enhancements. Fully specified in **PHASE_C_IMPLEMENTATION_ROADMAP.md** but doesn't start until P011 validation is done.

---

## FILES YOU'LL TOUCH

### Dashboard (Package 4b)
```
app/templates/dashboard.html
app/routes/dashboard.py
tests/test_routes_dashboard.py (check, don't break)
```

### Terminology (Package 4c)
```
app/templates/dashboard.html
app/templates/review.html
app/templates/map_viewer.html
app/routes/dashboard.py
app/routes/review.py
app/routes/map_preview.py
```

### Pairing Review (Package 5a)
```
app/templates/review.html
app/routes/review.py
tests/test_routes_review.py (check, don't break)
```

---

## PROJECT CONTEXT YOU NEED

### What GridFlow Does
- Takes survey CSV data (poles, crossings, context)
- Validates it against DNO rulepacks
- Flags QA issues (height missing, spans too long, etc.)
- Shows map visualization
- Generates design-readiness report

### Current Stage
- **Stage 3:** Multi-file projects, designer review, remote access (COMPLETE)
- **Phase B:** UI terminology polish (YOU ARE HERE)
- **Phase C:** Map enhancements (depends on P011 evidence)
- **Stage 4:** Structured field capture (future, needs evidence)

### Why Phase B Matters
Real job validation (P010/Gordon) showed:
- Designers need survey language, not QA language
- Dashboard feels technical, not professional
- Pairing review purpose is unclear
- These fixes are **pure UX**, no logic changes

---

## SUCCESS = DONE WHEN

✅ All 3 packages implemented
✅ pytest -v shows 297 tests passing
✅ Dashboard feels professional
✅ Terminology is survey-facing, not technical
✅ Pairing review is clear
✅ Code is committed and pushed
✅ You report completion

---

## QUESTIONS?

**For task clarification:** Read the package section above (most answers are there)

**For code patterns:** Look at existing code in app/templates/ and app/routes/

**For blockers:** Report the issue + error message + what you tried

---

## Go! 🚀

You have everything you need. Start with **Package 4b** (dashboard cleanup).

Good luck, and commit often!
