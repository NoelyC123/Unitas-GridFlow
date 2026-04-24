# Current Task

## Immediate task

The immediate task is:

**Batch 20B — Structured issue model.**

Batch 20A is complete (committed 2026-04-24, pushed to master).

---

## Completed: Batch 20A — Trust fixes

Batch 20A delivered:
- Frontend rulepack dropdown cleaned to only the 4 supported rulepacks
- `api_rulepacks.py` now derives real metadata from `RULEPACKS` dict (no stub)
- Compound Trimble feature codes (`Pol:LAND USE` → `Pol`) normalised at parser intake
- `span_count: 0` removed from `api_intake.py` and `map_preview.py`
- 5 focused tests added; 126 passing

This is the first implementation step under:

**Batch 20 — Trust, Severity & Actionable Design Briefing**

---

## Why this is the current task

Batch 19 validation showed that Unitas GridFlow is now genuinely valuable as a working MVP.

The multi-AI review confirmed that the strongest current value is not broad DNO compliance automation.

The strongest current value is:

**helping a designer quickly understand what the digital survey handoff contains, what is missing, what looks risky, and what should be checked before design starts.**

However, the review also identified several trust and clarity issues that should be fixed before adding broader features.

The next phase should therefore improve:

- rulepack truthfulness
- metric consistency
- designer-facing clarity
- output trust
- actionability

It should not broaden the product.

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

## Batch 20A scope

Batch 20A is the narrow trust-fix step.

Implement only the following:

1. Ensure the frontend only offers backend-supported rulepacks.
2. Make the rulepack API truthful and auditable.
3. Fix or remove the map/sidebar span-count contradiction.
4. Clean or suppress noisy raw controller labels such as `Pol:LAND USE` in designer-facing outputs.
5. Add or update focused tests.
6. Run `pytest -v`.
7. Run `pre-commit run --all-files`.
8. Commit and push.

---

## Why Batch 20A comes first

The AI review identified several immediate trust breakers.

These include:

- unsupported rulepacks appearing selectable in the UI
- rulepack details that may not reflect actual backend rules
- span metrics showing contradictory information
- raw controller labels cluttering the designer-facing report or map

These issues can damage confidence quickly, even if the underlying analysis is useful.

Batch 20A should fix those issues before larger output restructuring begins.

---

## Files likely involved

Likely files include:

- `app/dno_rules.py`
- `app/routes/api_rulepacks.py`
- `app/routes/api_intake.py`
- `app/routes/map_preview.py`
- `app/routes/pdf_reports.py`
- `app/templates/upload.html`
- `app/templates/map_viewer.html`
- relevant JavaScript files if present
- relevant tests under `tests/`

Only edit files that are directly required for Batch 20A.

Read each file before editing it.

---

## Out of scope for Batch 20A

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
- broad SaaS/platform features
- full severity model implementation
- full PDF redesign

Severity, recommended actions, scoped readiness gates, and PDF first-page redesign are later Batch 20 steps.

---

## Batch 20B next step after Batch 20A

After Batch 20A is complete, the next planned step is:

**Batch 20B — Structured issue model**

Suggested future fields:

- `issue_code`
- `severity`
- `category`
- `scope`
- `confidence`
- `recommended_action`
- `is_observation`

Do not start Batch 20B until Batch 20A is complete and tested.

---

## Batch 20C later step

After the structured issue model exists:

**Batch 20C — Recommended designer actions**

This should add plain-English recommended actions for top design risks.

Example actions:

- request missing pole height evidence
- confirm stay specifications from field notes or plan markups
- review ambiguous EX to proposed replacement groups
- confirm whether 5.0m values are true pole heights or controller-derived values

---

## Batch 20D later step

After recommended actions:

**Batch 20D — Scoped design evidence gates**

This should replace over-broad readiness wording with scoped evidence gates such as:

- position / mapping evidence
- structure identity evidence
- structural specification evidence
- stay evidence
- clearance design evidence
- conductor scope evidence
- overall design handoff status

---

## Batch 20E later step

After evidence gates:

**Batch 20E — PDF first-page briefing redesign**

The first page should read as a professional designer briefing, showing:

- job summary
- parser used
- CRS detected
- rulepack applied
- record counts
- top blockers
- top warnings
- recommended actions
- clear statement on whether design can proceed from the digital file alone

---

## Supporting decision memo

The Batch 20 direction is recorded in:

`AI_CONTROL/07_BATCH_20_DECISION_MEMO.md`

That memo should be treated as the decision record for this phase.

---

## What success looks like for Batch 20A

Batch 20A is successful when:

- users cannot select unsupported rulepacks from the frontend
- the rulepack API only reports real backend rulepacks and real checks
- the applied rulepack is clear and truthful
- span metrics no longer contradict span warnings
- noisy raw controller labels no longer clutter designer-facing outputs
- tests pass
- pre-commit passes
- changes are committed and pushed

---

## Final rule

Keep Batch 20A narrow.

Do not broaden the project.

Do not replace validation-led improvement with speculative feature expansion.

The goal is to make Unitas GridFlow more trustworthy to a real designer within the first 60 seconds of reviewing the output.
