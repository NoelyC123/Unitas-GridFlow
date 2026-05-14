# Stage 5G Designer Review Script

**Date created:** 2026-05-14
**Registered job:** P_LOCAL_DESIGNER_REVIEW
**Review duration:** 25-30 minutes
**Required:** Designer with UK OHL design experience

---

## 1. Purpose

The review tests whether GridFlow clearly communicates:

- what field evidence exists
- what DNO baseline engineering records are still missing
- why design readiness is currently blocked
- what action a designer should take next

Core message under test:

> "You have survey evidence, but you still need confirmed DNO engineering
> records before design."

---

## 2. What GridFlow Is (current Stage 5 scope)

GridFlow is a survey-to-design QA and design-readiness tool for UK
electricity network overhead line workflows. It compares baseline DNO
records against field survey evidence, identifies missing or conflicting
information, and produces structured reports plus a web workspace and
map overlay to help designers decide whether they can begin design or
need additional DNO/field evidence first.

This is GridFlow's current Stage 5 value proposition. The tool may expand
in future phases to cover field capture, evidence management, mobile/tablet
survey, or design integration, but those are not part of the current scope.

---

## 3. What GridFlow Is Not (current Stage 5 scope)

- Not a PoleCAD replacement
- Not an automatic design engine
- Not a DNO compliance certification tool
- Not yet a mobile/tablet capture app
- Not yet photo-integrated in the workspace
- Currently validated end-to-end on one job (P_LOCAL_001) with three baseline variants

---

## 4. Pre-Review Setup

### 4.1 Create the registered review job

```bash
cd /Users/noelcollins/Unitas-GridFlow
source .venv312/bin/activate

python scripts/run_pipeline.py \
  --baseline tests/baseline/fixtures/enwl_sample.csv \
  --field real_pilot_data/P_LOCAL_001/enwl_enrichment_clean \
  --output /tmp/gridflow_designer_review \
  --job-id P_LOCAL_DESIGNER_REVIEW \
  --register \
  --overwrite-registration
```

### 4.2 Run pre-flight check (Claude Code is creating this)

```bash
python scripts/preflight_designer_review.py P_LOCAL_DESIGNER_REVIEW
```

The pre-flight check verifies:

- Pipeline ran successfully
- `uploads/jobs/P_LOCAL_DESIGNER_REVIEW/` exists
- All 11 reports present
- All 3 routes return 200
- `meta.json` contains correct `job_id`

### 4.3 Start Flask

```bash
export FLASK_APP=run.py
flask run
```

### 4.4 Open the one-page summary

Open `AI_CONTROL/115_DESIGNER_ONE_PAGER.html` in a browser. Print it.
Hand the printed sheet to the designer at the start of the review.

---

## 5. Review Routes

| Route | URL |
|-------|-----|
| Workspace | http://127.0.0.1:5000/workspace/view/P_LOCAL_DESIGNER_REVIEW |
| Overlay map | http://127.0.0.1:5000/map/overlay/P_LOCAL_DESIGNER_REVIEW |
| QA map | http://127.0.0.1:5000/map/view/P_LOCAL_DESIGNER_REVIEW |
| Feedback form | http://127.0.0.1:5000/feedback/P_LOCAL_DESIGNER_REVIEW |

Reports available at:
`uploads/jobs/P_LOCAL_DESIGNER_REVIEW/*.md`

---

## 6. 25-Minute Review Flow

### Minute 0-3: Orientation (no clicking yet)

Hand the designer the printed one-pager. Read the core message aloud:

> "You have survey evidence, but you still need confirmed DNO engineering
> records before design."

Ask the designer to say back what they understand the tool does in their
own words. Record this in the feedback form.

### Minute 4-7: Report 00 - Pilot Output Pack Index

Open: `uploads/jobs/P_LOCAL_DESIGNER_REVIEW/00_pilot_output_pack_index.md`

Show the executive summary, the Quick Actions section, and the report
file list. Ask:

- Is it clear what this output pack contains?
- Do the Quick Actions make sense as next steps?
- Is anything confusing or missing from the summary?

### Minute 8-12: Report 06 - DNO Data Request

Open: `uploads/jobs/P_LOCAL_DESIGNER_REVIEW/06_dno_data_request.md`

Critical question: this is the report that operationalises the core
message. Without authoritative DNO records, the designer cannot proceed.
This report tells them exactly what to request.

Ask:

- Is it obvious what data is missing?
- Would you know how to request this from the DNO?
- Is the wording professional enough to forward to a DNO contact?
- Does the report explain why each data item matters for design?

### Minute 13-18: Workspace

Open: http://127.0.0.1:5000/workspace/view/P_LOCAL_DESIGNER_REVIEW

Show the pole list. Try the filters. Click into one pole's detail page.

Ask:

- Can you see all 10 poles at a glance?
- Are the filters useful (design_ready, evidence quality, match confidence)?
- Does the pole detail page give enough context?
- What's missing that would make this immediately useful on a real job?

### Minute 19-22: Report 07 - Design Readiness Summary

Open: `uploads/jobs/P_LOCAL_DESIGNER_REVIEW/07_design_readiness_summary.md`

Critical question: does the designer understand that 0/10 is the correct
answer for this dataset, not a tool failure?

Ask:

- Does it make sense that 0 of 10 poles are design-ready?
- Are the blockers (conductor spec, pole class) legitimate in your workflow?
- Would you challenge any of these as overly strict?

### Minute 23-25: Map Overlay

Open: http://127.0.0.1:5000/map/overlay/P_LOCAL_DESIGNER_REVIEW

Show baseline poles (blue) vs field poles (green). Click a match line.

Ask:

- Is the visual distinction clear?
- Are the match confidence colours meaningful?
- Would this help spot GPS errors or wrong-pole matches?

---

## 7. Core Designer Questions (post-review)

After the walk-through, ask these in order. Use the live feedback form.

1. After reviewing this, can you explain in your own words what GridFlow does?
2. Does 0/10 design-ready make sense once you see the missing DNO data?
3. Is it clear what data must be requested from the DNO?
4. Would this save time compared with your current workflow?
5. Do you trust the blockers identified, or would you challenge any of them?
6. Is match confidence understandable and useful?
7. Is the map overlay useful?
8. How important is photo/evidence integration before you'd use this on a real job?
9. What would stop you from using GridFlow on a real project right now?
10. If you could change one thing first, what would it be?

---

## 8. Feedback Capture

Two methods, use whichever fits the conversation:

**Live form (preferred):**
http://127.0.0.1:5000/feedback/P_LOCAL_DESIGNER_REVIEW

Feedback is saved to `uploads/jobs/P_LOCAL_DESIGNER_REVIEW/feedback.json`
and viewable after the session.

**Paper backup:**

| Topic | Designer Feedback | Severity | Action Needed | Stage 6 Implication |
|-------|-------------------|----------|---------------|---------------------|
| Q1: What GridFlow does | | | | |
| Q2: Blockers make sense | | | | |
| Q3: DNO request clarity | | | | |
| Q4: Time savings | | | | |
| Q5: Trust in blockers | | | | |
| Q6: Match confidence | | | | |
| Q7: Map overlay | | | | |
| Q8: Photo integration priority | | | | |
| Q9: Use-on-real-job blockers | | | | |
| Q10: First change | | | | |

Severity scale:

- **BLOCKER** - Cannot pilot without this
- **HIGH** - Significant impact on usefulness
- **MEDIUM** - Worth doing but not blocking
- **LOW** - Future enhancement

---

## 9. Decision Matrix

After the review, classify the outcome:

### A. Ready for Controlled Pilot

Designer trusts output, understands blockers, would use on a real job
with minor adjustments.

**Next action:** Identify one real job, prepare pilot pack, iterate based
on use.

### B. Needs Report Wording Improvements

Designer is confused about why blockers exist or what to do about them.

**Next action:** Stage 5H - improve Report 06 and 07 wording. Re-review.

### C. Needs Workspace Improvements

Designer cannot find what they need in the workspace UI.

**Next action:** Stage 5H - workspace UX improvements (filters, pole detail
page, navigation).

### D. Needs Photo/Evidence Integration Before Pilot

Designer cannot trust results without seeing field photos and evidence.

**Next action:** Stage 6 photo integration becomes the top priority.

### E. Needs More Validation Jobs Before Pilot

Designer feedback is positive but they want to see it work on more diverse
data before trusting it on real work.

**Next action:** Stage 5H - create Stage 4C-compatible packs for Gordon
and Bellsprings.

### F. Not Useful in Current Form

Designer does not see value even after the walk-through.

**Next action:** Strategic review - revisit value proposition and core
assumptions. Stage 6 should not start.

---

## 10. Post-Review Actions

1. **Save the feedback** - JSON form output goes to `uploads/jobs/P_LOCAL_DESIGNER_REVIEW/feedback.json`
2. **Create findings document** - `AI_CONTROL/116_DESIGNER_FEEDBACK_FINDINGS.md`
3. **Quote the designer** - at least one direct quote per question
4. **Mark severity** - for each finding
5. **Decide Stage 6** - based on the decision matrix outcome
6. **Update control layer** - `01_CURRENT_STATE.md` and `02_CURRENT_TASK.md`

Do not start Stage 6 implementation until the findings document is complete
and the next phase is explicitly chosen.

---

## 11. Success Criteria

The review is successful, regardless of outcome, if:

- Designer understands the core value proposition
- Designer can articulate why design is blocked
- Designer identifies clear improvement priorities
- Designer sees realistic time-saving potential

The review reveals a problem, which is also useful, if:

- Designer cannot articulate what GridFlow does after 25 minutes
- Designer thinks 0/10 is a tool bug
- Designer would not trust results on any real job
- Designer cannot see how this saves time

Both outcomes inform the next correct decision.

---

## 12. Risks and Mitigations

| Risk | Mitigation |
|------|------------|
| Designer assumes 0/10 is a bug | Explain in orientation: it is the correct answer for this data |
| Designer expects PoleCAD-style features | Use Section 3 (What GridFlow Is Not) upfront |
| Designer wants photo integration immediately | Capture severity; this informs Stage 6 priority |
| Designer challenges all the conductor/pole class assumptions | Listen - this could reveal a real domain assumption gap |
| Designer is too polite to give negative feedback | Use the feedback form anonymously if needed |
