# Claude Next Priority Review

Source: Claude App review after working local MVP checkpoint  

Date: 2026-04-19

---

I now have a clear picture of the full current state. Here is my answer.

---

## 1. Recommended next priority

**More realistic sample/input handling.**

---

## 2. Why this should come before the other two

The current MVP flow works end-to-end, but it works because `api_intake.py` contains a deliberate normalization shim that maps whatever arrives in the demo CSV to the four fields `dno_rules.py` actually checks (`pole_id`, `height`, `material`, `location`). The entire QA pipeline currently runs on top of this shim. That means:

- The QA rules are being evaluated against data that has already been silently translated, not against real field inputs.
- You cannot know whether the QA rules are correct until you know the rules are running against representative data.
- `_normalize_dataframe()` has multiple fallback candidates for `height` including `clearance_m` and `pole_spacing_m` — both clearly wrong surrogates for pole height, included explicitly as MVP demo fallbacks.
- The `mock_survey.csv` is a demo file, not a real DNO survey export schema. Any realistic job from a real client will look different.

This creates a hidden ordering problem: improving the QA rules right now means improving rules against fake-shaped data. That is low-value work. The rules you write will be tuned to the mock schema, not to what real input CSVs actually contain. If someone feeds a real export from Survitec, Leica Geosystems, or a network operator's GIS tool, the normalization shim will likely fail silently or distort the data before QA even runs.

Fixing input handling first closes this gap. Once you have a representative sample schema and the normalization logic maps it correctly, QA rule improvements become meaningful and testable. Without it, you're building on sand.

---

## 3. Why the other two should wait

**Better QA rules** should wait because `dno_rules.py` currently has four rules — unique `pole_id`, height in range 10–25m, required `material`, required `location`. These are structurally correct but placeholder-level. The right time to expand them is when you have real or realistic input data to test them against. Expanding the rule set now will require re-testing everything once the input schema is fixed anyway. You'd be doing the work twice.

**Cleanup / refactor / hardening** should wait because the code, while quick, is not broken. The `_infer_issue_rows` function is a known stub (it returns empty sets and has a comment acknowledging it), and the fallback lat/lon logic for missing coordinates is explicitly in place. These are known technical debts, not unknown risks. The app is functioning. Refactoring now, before the data and rules stabilise, risks cleaning code that is about to be substantially changed when the schema work forces changes to `_normalize_dataframe`, `run_qa_checks`, and `_build_feature_collection`. Clean up after the shape of the data is locked, not before.

---

## 4. Exact files likely to be touched next

- `app/routes/api_intake.py` — `_normalize_dataframe()` needs to map real field names, not just demo fallbacks. The `clearance_m` / `pole_spacing_m` fallbacks need to be removed or made explicit-only.
- `sample_data/mock_survey.csv` — needs to be replaced or supplemented with a CSV that has a schema representative of real DNO survey exports.
- `app/dno_rules.py` — field names in the rules need to match whatever canonical schema is agreed from the sample data work.
- Possibly `app/qa_engine.py` — if the `range` check needs to handle `NaN` more carefully when real numeric data arrives with blanks.

---

## 5. Main risks if we choose the wrong next step

**If you choose QA rules next:** You spend time writing detailed rules (e.g., span clearance checks, conductor type validation, voltage-band logic) that are tuned to a schema that does not represent real inputs. When a real CSV arrives from a client or field tool, the normalization shim produces wrong field mappings, the rules fire on bad data, and the output is unreliable. Worse, you may not notice because the app doesn't crash — it just produces wrong QA results silently.

**If you choose cleanup/refactor next:** You burn time on code organisation when the shape of the data pipeline is still about to change. The `_normalize_dataframe` function will need significant rework once a real schema is defined. Refactoring it now means refactoring it twice. Low-value use of time at this stage.

---

## 6. Final blunt recommendation

Fix the input layer first. The QA pipeline is running on invented field mappings against a demo CSV. That makes everything downstream — the rules, the map, the PDF report — cosmetically correct but actually untestable against real work. Get one real or fully representative sample CSV, map it properly through `_normalize_dataframe`, remove the demo-fallback hacks, and then the QA rule expansion will be worth doing.

---

