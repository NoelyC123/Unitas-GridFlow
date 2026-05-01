# CURSOR: Critical Product Framing Fix + Evidence Integration

**URGENT:** Critical product positioning error must be fixed across all project files.

**Task Duration:** 30-45 minutes
**Files to Update:** ~8 control/analysis files
**Tests Required:** NO code changes, documentation only

---

## CRITICAL FIX REQUIRED

### ❌ INCORRECT FRAMING (being corrected):

> Field Maps record visibility was treated as separate from GridFlow design interpretation.

**PROBLEM:** This implies GridFlow REPLACES Field Maps' basic functionality.

### ✅ CORRECT FRAMING (must be everywhere):

> "Field Maps answers: 'What records are on the map?'
> GridFlow answers: 'What records are on the map?' **AND** 'What does this survey data mean for design, what is missing, what remains provisional, and what must be checked before CAD/design?'"

**KEY POINT:** GridFlow = Field Maps functionality **PLUS** design-readiness interpretation layer.

**NOT replacement. ADDITIVE.**

---

## WHY THIS MATTERS

If GridFlow doesn't show "what records are on the map" as clearly as Field Maps, it's **worse** than Field Maps, not better.

The value proposition is:
- Show all the same records Field Maps shows ✅
- PLUS add design interpretation on top ✅

**This is non-negotiable product positioning.**

---

## FILES TO UPDATE

Search for old either/or Field Maps vs. GridFlow wording.

Then replace with the correct additive framing shown above.

### Likely locations:

1. `AI_CONTROL/01_CURRENT_STATE.md`
2. `AI_CONTROL/04_SESSION_HANDOFF.md`
3. `NOEL_FINAL_SPEC_ANALYSIS_2026-04-30.md`
4. `COMPLETE_OPERATIONAL_VALIDATION_2026-04-30.md`
5. `COMPLETE_FIELD_MAPS_VALIDATION_FOR_PHASE_C.md`
6. `PROJECT_SYNC_COMPLETE_2026-04-30.md`
7. `SESSION_END_SUMMARY_2026-04-30.md`
8. `CURSOR_HANDOFF_2026-04-30_FINAL.md`

### How to fix:

1. Search entire `/Users/noelcollins/Unitas-GridFlow/` for old either/or Field Maps vs. GridFlow wording
2. For EACH occurrence, verify it's the old either/or framing
3. Replace with the additive BOTH/AND framing
4. Preserve surrounding context
5. Verify the fix makes sense in that document's context

---

## SECOND TASK: Evidence Integration Reminder

Add this section to `AI_CONTROL/02_CURRENT_TASK.md` under "Phase C packages":

```markdown
---

## Evidence Base for Phase C (MUST USE)

All Phase C development MUST reference these 4 comprehensive specifications:

1. **Live operational feedback** (P011_OPERATIONAL_FEEDBACK_2026-04-30.md)
   - 6 critical map issues from real designer use
   - All issues map to Phase C C1-C4

2. **Engineering analysis** (GridFlow_Electrical_Survey_Review.docx)
   - 15 pages, 17 cited sources
   - ESQCR, PLS-CADD, NIE schema
   - Height vs. Specification problem
   - Shape ≠ Color paradigm

3. **Field Maps + NIE validation** (NIE_Fibrus_enhanced_Review_for_GridFlow_.docx)
   - Production Field Maps benchmarks
   - NIE 19-field MV_Poles schema
   - 15 review focus filters
   - Popup layout requirements

4. **Final consolidated specification** (Pro_GridFlow_Electrical_Survey_Review_Final_Detailed_.docx)
   - 8,604 words, 19 sections + 2 appendices
   - Complete technical blueprint
   - THIS IS THE DEFINITIVE SPEC FOR PHASE C

**Before implementing ANY Phase C package:**
- Read the relevant section from the 8,604-word spec
- Cross-reference with engineering analysis
- Verify against Field Maps evidence
- Use exact wording from specifications

**Do NOT:**
- Implement Phase C from memory
- Guess at requirements
- Skip reading the evidence
- Invent features outside C1-C4 scope
```

---

## VERIFICATION CHECKLIST

After making changes, verify:

- [ ] All Field Maps/GridFlow positioning uses ADDITIVE framing
- [ ] No files still have REPLACEMENT framing
- [ ] Evidence integration section added to 02_CURRENT_TASK.md
- [ ] All changes are documentation-only (no code changes)
- [ ] Git diff shows only the intended changes
- [ ] No unintended modifications

---

## COMMIT MESSAGE

```
Fix critical product framing: GridFlow = Field Maps PLUS interpretation

BREAKING: Changed product positioning from replacement to additive model.

GridFlow must show "what records are on the map" (like Field Maps)
PLUS add design-readiness interpretation layer on top.

Updated 8 documentation files to reflect correct additive framing.
Added evidence integration requirements to Phase C task file.

No code changes. Documentation only.
```

---

## REPORT FORMAT

After completion, report:

```
CRITICAL FIX COMPLETE

Files updated: [count]
Instances fixed: [count]

Changed files:
- AI_CONTROL/01_CURRENT_STATE.md
- AI_CONTROL/04_SESSION_HANDOFF.md
- [list all changed files]

Evidence integration section added to:
- AI_CONTROL/02_CURRENT_TASK.md

All changes committed: [commit hash]

Verification: All Field Maps/GridFlow positioning now uses
additive BOTH/AND framing, not replacement either/or framing.
```

---

## IMPORTANT NOTES

1. **This is a critical product positioning fix**, not a minor wording change
2. **Every file matters** — inconsistent framing confuses future development
3. **No code changes** — this is documentation-only
4. **Fast turnaround** — should take 30-45 minutes max
5. **Commit separately** — don't mix with other changes

---

## NEXT STEPS (DO NOT START YET)

After this fix is complete and committed:
- Noel will approve Phase C path
- Cursor will receive Phase C implementation brief
- Phase C C1-C4 implementation begins

**Wait for approval before starting Phase C work.**
