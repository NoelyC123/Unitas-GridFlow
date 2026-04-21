# Current Task

## Immediate task

The immediate task is:

**Improve QA rules so the tool becomes genuinely useful**

This means making `app/dno_rules.py` do real, meaningful validation work.

---

## Why this is the current task

The project has moved past baseline/setup work. It now has:

- ✅ working local MVP
- ✅ clean canonical repo
- ✅ tests passing
- ✅ CI/CD active
- ✅ professional baseline

The project's main remaining weakness is no longer infrastructure or process.

The project's main remaining weakness is now **product value**.

The tool doesn't yet catch real problems meaningfully. That's because the QA rules are placeholder-level.

So the current task is to fix that.

---

## What "improve QA rules" means

This does NOT mean: "add 100 rules" or "redesign the entire QA engine"

This DOES mean: "add 5-10 *real, useful* rules that catch meaningful problems"

Examples of real rules:
- Check that heights are physically realistic (not -5000m or 99999m)
- Check that coordinates are actually in the UK
- Check that asset types match DNO standards
- Check for missing critical fields
- Check for coordinate/geometry inconsistencies
- Flag suspicious data patterns

The point: **after this task, someone using the tool can say "this catches real problems in my survey data"**

---

## This is Phase 1 of 3

### Phase 1 (current): Better QA rules
**Timeline:** 1-3 weeks
**Effort:** 10-20 hours
**Files to change:** `app/dno_rules.py` (primarily)
**Success:** Tool catches meaningful validation problems

### Phase 2 (after Phase 1): Broader input handling
**Timeline:** 2-4 weeks
**Effort:** 20-40 hours
**Files to change:** `app/routes/api_intake.py` (primarily)
**Success:** Works with multiple real data formats

### Phase 3 (after Phase 2): Browser automation
**Timeline:** 1-2 weeks
**Effort:** 10-20 hours
**Files to change:** Add Playwright tests
**Success:** All flows have automated tests

---

## How to start this task

1. **Read** `PROJECT_OVERVIEW_AND_NEXT_STEPS.md` Phase 1 section (for full context)

2. **Define** what "good" rules should be
   - What does a valid DNO survey look like?
   - What are the most common problems in your data?
   - What would actually help your team?

3. **Edit** `app/dno_rules.py`
   - Add realistic validation checks
   - Add meaningful issue messages
   - Keep logic simple and clear

4. **Test locally**
   - `python run.py` (start app)
   - Upload a CSV
   - Verify rules catch what they should

5. **Commit and push**
   - `pytest -v` (run tests)
   - `pre-commit run --all-files` (lint)
   - `git commit -m "Add real validation rules"`
   - `git push origin master`

6. **Checkpoint**
   - 2-3 rules working? Read `03_WORKING_RULES.md` checkpoint section
   - Update control files if needed

---

## What not to do during this task

Do NOT:
- Broaden scope (stay focused on QA rules)
- Redesign the QA engine (keep the current architecture)
- Try to handle all edge cases (catch the common ones)
- Add browser tests yet (Phase 3)
- Make schema changes (Phase 2)

---

## Success condition

This task is complete when:

**The tool catches 5-10 meaningful validation problems and you can say "this is genuinely useful"**

Not: "100 rules implemented"
But: "Real problems caught meaningfully"

---

## Next control file update

Update `02_CURRENT_TASK.md` again when:
- Phase 1 is complete (move to Phase 2)
- The priority changes
- A blocker emerges that changes the approach

Otherwise, keep this task as-is.
