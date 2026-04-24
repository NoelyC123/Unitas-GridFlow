# Current Task

## Immediate task

The immediate task is:

**Batch 20B — Structured issue model.**

Batch 20A is complete and pushed to `master`.

---

## Completed previous step: Batch 20A

Batch 20A fixed the immediate trust issues identified by the April 2026 multi-AI review.

Completed Batch 20A changes:

- frontend rulepack dropdown now only shows backend-supported rulepacks
- `api_rulepacks.py` now derives real metadata from backend `RULEPACKS`
- unknown rulepack IDs return a clear error instead of misleading stub data
- compound Trimble/controller feature codes are normalised at parser intake
  - `Pol:LAND USE` becomes `Pol`
  - `EXpole:BOUNDARY` becomes `EXpole`
- misleading `span_count: 0` metadata was removed
- focused tests were added
- 126 tests passing

Batch 20A is closed.

Do not redo Batch 20A unless a regression is found.

---

## Why Batch 20B is now the current task

Batch 19 validation showed that Unitas GridFlow is genuinely valuable as a working MVP.

Batch 20A improved immediate trust issues.

The next weakness is that findings are still too flat and noisy.

The tool needs to distinguish between:

- design blockers
- warnings requiring review
- useful observations
- completeness gaps

This will allow the PDF, map, and designer summary to become more actionable without broadening the product.

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

## Batch 20B goal

Introduce a structured issue model that supports clearer grouping, severity, and future recommended actions.

The goal is to improve the output from:

**"Here are many issues"**

to:

**"Here are the blockers, warnings, and observations, each with clear meaning."**

---

## Batch 20B scope

Implement a narrow structured issue model.

Suggested fields:

- `issue_code`
- `severity`
- `category`
- `scope`
- `confidence`
- `recommended_action`
- `is_observation`

Start simple.

Do not over-engineer the model.

---

## Initial severity levels

Use a small practical severity set:

- `critical`
- `warning`
- `observation`

Suggested meaning:

- `critical` — likely blocks design or requires clarification before design proceeds
- `warning` — requires review or confirmation
- `observation` — useful detected pattern, not necessarily a defect

---

## Likely issue categories

Possible categories include:

- `data_completeness`
- `structural_evidence`
- `replacement_intent`
- `span_geometry`
- `coordinate_quality`
- `rulepack_validation`
- `controller_parsing`

Only add categories that are actually needed by current checks.

---

## Important examples

Replacement pair detections should usually be observations unless ambiguous.

Ambiguous replacement pairings should be warnings.

Missing structural evidence across many records should be critical or warning depending on context.

Short spans caused by likely existing-to-proposed replacement pairs should not automatically be treated as design failures.

---

## Files likely involved

Likely files include:

- `app/qa_engine.py`
- `app/controller_intake.py`
- `app/routes/api_intake.py`
- `app/routes/pdf_reports.py`
- `app/templates/map_viewer.html`
- relevant tests under `tests/`

Only edit files needed for Batch 20B.

Read files before editing.

---

## Out of scope for Batch 20B

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

Do not start Batch 20C until Batch 20B is complete.

Recommended actions may be included only if simple and directly tied to the structured model, but the full designer action section belongs to Batch 20C.

---

## What success looks like

Batch 20B is successful when:

- issues have stable structured fields
- existing tests still pass
- new tests cover severity/category/observation behaviour
- existing CSV/PDF/map outputs still work
- replacement observations can be separated from true problems
- the output is ready for Batch 20C recommended actions

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

Keep Batch 20B narrow.

The goal is not to add more features.

The goal is to make current findings more structured, less noisy, and easier to act on.
