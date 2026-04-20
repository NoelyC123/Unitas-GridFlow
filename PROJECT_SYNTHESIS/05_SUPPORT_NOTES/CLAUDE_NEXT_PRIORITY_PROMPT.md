## Follow-up prompt



---

## 1. Smallest best next step

**Replace `sample_data/mock_survey.csv` with a new CSV whose schema matches what a real DNO overhead line survey export actually looks like — and update `_normalize_dataframe()` in `api_intake.py` to map that schema cleanly without needing the demo fallback hacks.**

Specifically: define one canonical column set that represents a plausible real field export (e.g. `asset_id`, `structure_type`, `height_m`, `material`, `easting`, `northing`, `latitude`, `longitude`, `location_name`), write the sample CSV to use those exact column names, and rewrite the normalization mapping in `_normalize_dataframe()` to handle that schema correctly. Remove the `clearance_m` and `pole_spacing_m` fallbacks entirely.

---

## 2. Why this exact step should come first

The current `_normalize_dataframe()` function contains this comment in its own code — `clearance_m` is labelled a "sample_data fallback for MVP demo" and `pole_spacing_m` is labelled a "secondary fallback". These are not normalization logic. They are workarounds for the fact that the demo CSV does not have a real `height` column. Every job run so far has been QA'd using a surrogate for pole height, not pole height itself.

This means the current end-to-end test of the MVP is testing the wrong thing. The map, the PDF, the issue counts — all of it has been produced by QA rules running against a field that does not represent what it is supposed to represent. You cannot trust the QA output until the sample data has the right columns and the normalization maps them correctly.

This is a single contained fix. It does not require new routes, new rules, or new UI. It only touches two things: the sample CSV and the mapping function that reads it.

---

## 3. Exact files to change first

- `sample_data/mock_survey.csv` — replace with a new file using a realistic column schema
- `app/routes/api_intake.py` — update `_normalize_dataframe()` to map the new schema and delete the `clearance_m` / `pole_spacing_m` fallback candidates

No other files need to change for this step.

---

## 4. What a "good result" looks like

After this step:

- You upload the new `mock_survey.csv` through the existing upload page
- `_normalize_dataframe()` maps it to `pole_id`, `height`, `material`, `location`, `lat`, `lon` without any fallback substitution firing
- The `auto_normalized` flag in `meta.json` is `true` (because column renaming happened), but no surrogate fields are used
- The QA engine runs range checks against actual `height_m` values from the CSV, not against clearance or spacing values
- The `issues.csv` output reflects realistic pole height failures (e.g. poles below 10m or above 25m in the sample data)
- You can read the sample CSV and the `issues.csv` side-by-side and confirm the issues are correct

---

## 5. What to avoid doing yet

- Do not expand `dno_rules.py` to add new rule types during this step — that comes after the schema is stable
- Do not add a second sample CSV or multiple schema variants — one realistic schema first
- Do not change the upload UI, the map viewer, or the PDF template
- Do not touch `qa_engine.py` — the existing `unique`, `range`, and `required` checks are sufficient to validate this step
- Do not introduce any schema auto-detection logic or dynamic column discovery — the mapping stays explicit and manual in `_normalize_dataframe()`
- Do not attempt to handle real client exports yet — one controlled representative schema only