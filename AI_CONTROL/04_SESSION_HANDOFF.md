# Session Handoff

## Last session summary (21 April 2026 — continued)

This session had two distinct phases. The first (NIE rulepack + control layer sync) was recorded
in the previous handoff entry. This entry records the second phase.

---

## Phase 2 — Rationale document + real survey file review

### What was done

1. **Project rationale document saved permanently.**
   `PROJECT_SYNTHESIS/00_PROJECT_RATIONALE.md` now exists. It is the source-of-truth explanation
   of why the project exists, what problem it solves, and what it is not. Working instruction at
   the top: Unitas Grid-Flow is a true fresh-start project; do not assume any prior EW Design
   Tool / SpanCore build is the current product state.

2. **Real survey-origin files reviewed.**
   Three Trimble CSV exports (jobs 4-474, 474c, 513), one Trimble binary .job file, two
   ArcGIS/PoleCAD design images, and two handwritten field notebook sketches were examined.

3. **Real survey input analysis note created.**
   `PROJECT_SYNTHESIS/05_SUPPORT_NOTES/REAL_SURVEY_INPUT_ANALYSIS.md` records all findings in
   full detail.

4. **`02_CURRENT_STATE.md` updated.**
   Added a full "Real survey input — confirmed state" section covering all discoveries.

5. **`03_CURRENT_TASK.md` rewritten.**
   No longer points at ENWL rulepack as automatic next step. Now presents a clear two-path
   priority decision (intake rewrite vs rulepack continuation) with no code changes until
   the decision is confirmed.

---

## Key discoveries from real file review

### Discovery 1 — Real Trimble CSV format is completely different from current sample schema
The current intake normalisation layer assumes a flat named-column schema. Real Trimble exports
are variable-width, feature-coded format with a job header row, a PRS base station row, and
point records structured as:
`point_id, easting, northing, height, feature_code, [feature_code]:STRING, string_number,
[feature_code]:TAG, tag_value, [feature_code]:REMARK, remark_text, [feature_code]:LAND USE,
land_use[, [feature_code]:HEIGHT, feature_height]`

The tool cannot process real survey files without intake rework.

### Discovery 2 — NI coordinate projection may be wrong
Real files use TM65 Irish Grid (EPSG:29902) or ITM (EPSG:2157). The current `coord_consistency`
check uses OSGB27700 (EPSG:27700 — British National Grid). Wrong for NI. NIE_11kV rulepack
coord checks will be incorrect until this is fixed.

### Discovery 3 — Ignore-tagged rows need filtering
Trimble CSV exports include points tagged `I` (Ignore). These must be excluded before QA.

### Discovery 4 — .job file is binary, not a first intake target
Proprietary Trimble General Survey Journal binary. Not parseable without a SDK. CSV is the
practical intake path.

### Discovery 5 — Handwritten notes confirm the handoff gap is real
Field notebook sketches show stay geometry, clearance measurements, drain/hedge constraints,
and site context that is structurally absent from the CSV data. The product rationale is
confirmed by the actual files.

---

## Current priority status

**Blocked on a decision.** See `03_CURRENT_TASK.md`.

The decision is:
- **Path A:** Real Trimble CSV intake/normalisation first (recommended — enables real-data testing)
- **Path B:** Continue DNO rulepack expansion first (ENWL, NGED, UKPN)

No code changes should be made until this is confirmed.

---

## What is materially true now

- 29 tests passing.
- 8 QA check types.
- Three DNO rulepacks live: `SPEN_11kV`, `SSEN_11kV`, `NIE_11kV`.
- `PROJECT_SYNTHESIS/00_PROJECT_RATIONALE.md` now exists — permanent rationale record.
- `PROJECT_SYNTHESIS/05_SUPPORT_NOTES/REAL_SURVEY_INPUT_ANALYSIS.md` now exists — real file findings.
- Real Trimble CSV format is now understood and documented.
- Control layer reflects that intake normalisation needs rework before real-data use.

---

## Next session should

1. Confirm the priority decision (Path A or Path B).
2. Update `03_CURRENT_TASK.md` with the confirmed path.
3. Only then begin implementation work.

## Next session should NOT

- Begin any code changes before the priority decision is confirmed.
- Assume ENWL rulepack is still the automatic next step.
- Use any EW Design Tool / SpanCore codebase as current product state.
