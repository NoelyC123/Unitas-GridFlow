# Current Task

## Immediate task

The immediate task is:

**Batch 20D — Scoped design evidence gates.**

Batches 20A, 20B, and 20C are complete and pushed to `master`.

---

## Completed previous steps

### Batch 20A — Trust fixes

Batch 20A fixed immediate trust issues identified by the April 2026 multi-AI review.

Completed Batch 20A changes:

- frontend rulepack dropdown now only shows backend-supported rulepacks
- `api_rulepacks.py` now derives real metadata from backend `RULEPACKS`
- unknown rulepack IDs return a clear error instead of misleading stub data
- compound Trimble/controller feature codes are normalised at parser intake
  - `Pol:LAND USE` becomes `Pol`
  - `EXpole:BOUNDARY` becomes `EXpole`
- misleading `span_count: 0` metadata was removed
- focused tests were added

### Batch 20B — Structured issue model

Batch 20B introduced structured issue fields:

- `issue_code`
- `severity`
- `category`
- `scope`
- `confidence`
- `recommended_action`
- `is_observation`

This allows the tool to separate design blockers, warnings, and observations.

Batch 20A and Batch 20B are closed.

Do not redo them unless a regression is found.

---

## Why Batch 20C is now the current task

The April 2026 multi-AI review showed that Unitas GridFlow is valuable, but the output must become more actionable.

Batch 20B added structured `recommended_action` fields to individual issues.

The next step is to turn those issue-level actions into a clear designer-facing action summary.

The goal is to help a designer or QA lead answer:

**What do I need to do next before design can safely proceed?**

---

## Current Batch 20 direction

Batch 20 is:

**Trust, Severity & Actionable Design Briefing**

Goal:

Improve the Batch 19 output from:

**"Here are many warnings"**

to:

**"Here is what matters, why it matters, and what action should happen next."**

---

## Batch 20C goal

Add a concise recommended designer actions summary derived from structured issue data.

The output should move from:

**"Here are classified issues."**

to:

**"Here are the practical actions required before design."**

---

## Batch 20C scope

Implement a narrow recommended actions layer.

Suggested behaviour:

1. Group issue-level `recommended_action` values.
2. Deduplicate repeated actions.
3. Prioritise actions by severity:
   - critical first
   - warning second
   - observation last only if useful
4. Show the actions in designer-facing outputs where practical.
5. Keep the implementation simple and deterministic.

---

## Recommended action examples

Examples of useful actions:

- request missing pole height evidence before clearance/design checks
- confirm material evidence for structures where material is missing
- review coordinate mismatches before relying on map output
- verify ambiguous EX to proposed replacement groups against field notes or plan markups
- confirm stay evidence for angle structures before structural review

---

## Files likely involved

Likely files include:

- `app/issue_model.py`
- `app/routes/api_intake.py`
- `app/routes/pdf_reports.py`
- `app/templates/map_viewer.html`
- relevant tests under `tests/`

Only edit files needed for Batch 20C.

Read files before editing.

---

## Out of scope for Batch 20C

Do not add:

- OCR
- handwritten note parsing
- plan parsing
- LiDAR processing
- UAV imagery processing
- point-cloud processing
- vegetation AI
- broad CAD automation
- PoleCAD replacement
- commercial packaging
- pricing pages
- new superficial rulepacks
- full PDF redesign
- large UI redesign
- broad provenance/audit systems

Do not start Batch 20D until Batch 20C is complete.

Scoped readiness gates and PDF first-page redesign belong to later Batch 20D / 20E steps.

---

## What success looks like

Batch 20C is successful when:

- repeated issue-level recommended actions are grouped and deduplicated
- top actions are ordered by severity
- designer-facing output includes a concise recommended action list
- existing CSV/PDF/map outputs still work
- tests cover action grouping and prioritisation
- tests pass
- pre-commit passes

---

## Required workflow

After changes:

- run `pytest -v`
- run `pre-commit run --all-files`
- commit clearly
- push to `master`

---

## Supporting decision memo

The Batch 20 direction is recorded in:

`AI_CONTROL/07_BATCH_20_DECISION_MEMO.md`

That memo should be treated as the decision record for this phase.

---

## Final rule

Keep Batch 20C narrow.

The goal is not to add more features.

The goal is to turn structured findings into practical next actions for a real designer.
