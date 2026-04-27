# Stage 3B Validation Acceptance

## Stage: 3B — Designer Review & Export Readiness

## Date: 2026-04-27

## Implementation commits

| Commit | Description |
|--------|-------------|
| `a9b3ee2` | Add Stage 3B design brief (`AI_CONTROL/21_STAGE_3B_DESIGN_BRIEF.md`) |
| `7daa5a9` | Add Stage 3B designer review overlay |

## Test count: 273 passing (up from 244)

## New tests

### `tests/test_review_manager.py` — 20 unit tests
- `TestLoadSaveDelete` — load/save/delete review.json roundtrip
- `TestBuildReview` — version increment, reviewed_at set/clear, notes stripped
- `TestCalcDistance` — basic Euclidean, None input guard
- `TestEnrichOverrides` — distance fill from seq coordinates, null reviewed_match
- `TestApplyPairingOverrides` — no-op when no review, no-op when no overrides, original seq not mutated, reassign matched expole, chain replaces updated, mark unmatched, interleaved_view updated

### `tests/test_review_integration.py` — 9 integration tests
1. Creating review.json via POST
2. Saving a pairing override (with server-enriched distances)
3. Marking EXpole unmatched — appears in unmatched section of export
4. Reviewed export header — "Designer Reviewed" present
5. Provisional export header before review — "provisional" present
6. Reviewed D2D export uses override — chain row shows reassigned replacement
7. sequenced_route.json unchanged after override
8. Reset review (DELETE) removes review.json, export reverts to provisional
9. Existing exports work without review.json (backward compat)

---

## What was implemented

### Data layer — `app/review_manager.py`

- `load_review(file_dir)` — loads `review.json` or returns None
- `save_review(file_dir, review)` — writes `review.json`
- `delete_review(file_dir)` — removes `review.json`; returns bool
- `build_review(file_id, review_status, review_notes, pairing_overrides, existing_review)` — constructs the review dict with version counter and reviewed_at timestamp
- `calc_distance(e1, n1, e2, n2)` — Euclidean distance in grid space
- `enrich_overrides_with_distances(overrides, seq)` — fills `original_distance_m` and `reviewed_distance_m` from sequenced_route.json coordinates
- `apply_pairing_overrides(seq, review)` — deep copies seq, applies each override: moves EXpoles between matched/unmatched lists, updates chain `replaces_point_id`/`replaces_distance_m`, updates `interleaved_view` EXpole rows. Never mutates the original seq.

### REST API — `app/routes/api_review.py`

- `GET /api/project/<project_id>/file/<file_id>/review` — returns current review state
- `POST /api/project/<project_id>/file/<file_id>/review` — saves review with enriched overrides
- `DELETE /api/project/<project_id>/file/<file_id>/review` — deletes review.json (reset to auto-generated)

### Review page — `app/routes/review_page.py` + `app/templates/review.html`

- `GET /review/project/<project_id>/<file_id>` — server-rendered review page
- Bootstrap 5 table showing all EXpoles (matched + unmatched) with dropdown reassignment
- Designer sign-off section: reviewed/not-reviewed radio, review notes textarea
- Save Review and Reset to Auto-Generated buttons (vanilla JS fetch())
- Toast notifications on save/reset

### D2D export integration — `app/routes/d2d_export.py`

- Project chain and interleaved export routes now load `review.json`, apply `apply_pairing_overrides`, and build `reviewed_label` from `review_status`/`reviewed_at`
- `_render_chain_export` and `_render_interleaved_export` accept `reviewed_label: str | None`; when set, header shows "Designer Reviewed — <timestamp>" instead of "provisional"

### Reprocessing clears review — `app/routes/api_intake.py`

- `process_job` calls `delete_review(job_dir)` at the start. If a file is reprocessed, the stale review is removed before the new pipeline run.

### Blueprint registration — `app/__init__.py`

- `api_review_bp` registered at `/api`
- `review_page_bp` registered (no prefix)

---

## Design principles preserved

- `sequenced_route.json` is never modified — the review overlay is always applied at export time on a deep copy
- "Reset to auto-generated" is a single `review.json` delete — no pipeline re-run required
- Review state is version-counted; `build_review` increments version on each save
- `reviewed_by` field records "Designer" (configurable later per design brief decision 6)

---

## Known caveats (by design — not bugs)

- EXpole pairing review only; section boundary editing deferred (Stage 3B+ scope)
- No route sequence editing, no pole attribute editing, no map-based editing
- No cross-file review — each file is reviewed independently
- Reviewed state affects D2D CSV exports only; PDF report update deferred
- `reviewed_by` is hardcoded to "Designer" — configurable role label deferred
- No multi-user conflict resolution — last-write-wins (single-user local use)

---

## Acceptance conclusion

Stage 3B MVP is implemented. All 9 specified integration scenarios pass. All 273 tests pass. Pre-commit clean.

The tool can now produce D2D exports that reflect reviewed designer decisions. The export header distinguishes "Designer Reviewed" from "provisional." Reviewed state can be reset to auto-generated without touching the original processing output.

Stage 3B is closed. The next decision is: Stage 3B polish vs Stage 3A planning.
