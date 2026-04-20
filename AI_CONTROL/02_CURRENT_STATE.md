# Current State — Deeper Technical Reference

This file holds technical detail that doesn't belong in the master truth file.
It does NOT repeat facts that change often (test counts, check-type counts, priorities) — those live in `00_MASTER_SOURCE_OF_TRUTH.md`.

---

## MVP flow

**upload CSV → save file → run QA → save outputs → view map → download PDF → browse jobs**

### Working parts
- `/upload` page
- `/api/presign`
- CSV upload/save to job folder
- `/api/import/<job_id>` — selects rulepack by DNO, runs QA, writes outputs
- `issues.csv` output
- `map_data.json` output
- `/map/view/<job_id>`
- `/pdf/qa/<job_id>`
- `/jobs/`
- `/health/full`

### Job output contract

Successful jobs create:
- `uploads/jobs/<job_id>/meta.json`
- `uploads/jobs/<job_id>/<uploaded_csv>.csv`
- `uploads/jobs/<job_id>/issues.csv`
- `uploads/jobs/<job_id>/map_data.json`

---

## QA architecture

### `app/dno_rules.py`
- `BASE_RULES` — generic UK-wide rules used as fallback.
- `DNO_RULES` — backwards-compatible alias for `BASE_RULES`.
- `SPEN_11KV_RULES` — extends `BASE_RULES` with SPEN-specific checks.
- `RULEPACKS` dict — `{"DEFAULT": BASE_RULES, "SPEN_11kV": SPEN_11KV_RULES}`.

### `app/qa_engine.py`
Each check returns issues as DataFrame rows with `{Issue, Row}` columns.
See master truth §4 for the current list of check types.

The engine uses a single if/elif chain. Checks fall into two groups:
- Checks that operate on a single `field` key (`unique`, `required`, `range`, `allowed_values`, `regex`).
- Checks that operate on multiple fields (`paired_required`, `dependent_allowed_values`, `coord_consistency`).

### `app/routes/api_intake.py`
Rulepack selection chain:
`RULEPACKS[requested_dno]` → fallback to `RULEPACKS["DEFAULT"]` → fallback to `DNO_RULES`.

---

## Testing

Test layout (see master truth §4 for current total):
- `tests/test_api_intake.py` — normalization, post-processing, sanitization, feature collection.
- `tests/test_app_routes.py` — route behaviour, health, jobs API, PDF, import/finalize paths.
- `tests/test_qa_engine.py` — per-check-type behaviour.

Quality stack:
- `pre-commit` — trailing whitespace, EOF fix, YAML/JSON/large-file checks, Ruff hooks.
- `Ruff` — lint + format.
- `pytest` — backend unit and integration tests.
- `pytest-cov` — coverage reporting (`pytest --cov=app`).
- `GitHub Actions` — runs `pre-commit run --all-files` and `pytest -q` on every push/PR to `master`.
- `Dependabot` — weekly dependency updates via `.github/dependabot.yml`.

---

## Non-blocking technical debt

Known items that don't block the current priority but should be addressed when next relevant:

- Historical test jobs linger in `uploads/jobs/` (stale paths fixed 20 April 2026).
- `issues.csv` payloads are still verbose.
- `app/routes/api_rulepacks.py` returns stub data — needs wiring to real `RULEPACKS` dict.
- `Makefile` has a stale port (5010 instead of 5001).
- GitHub Actions shows a non-blocking Node.js deprecation warning for upstream actions.
- No automated browser tests (Playwright not yet active).
- `docker-compose.yml` exists at root but isn't used by current dev flow.

---

## Known weaknesses

See master truth §4 for the canonical list. This file does not duplicate it.
