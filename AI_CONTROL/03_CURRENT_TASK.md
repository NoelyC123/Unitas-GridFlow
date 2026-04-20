# Current Task

## Immediate task

Add `NIE_11kV` rulepack to `app/dno_rules.py`.

NIE (Northern Ireland Electricity Networks) is the DNO for Northern Ireland. Adding it continues the pattern established by SPEN_11kV and SSEN_11kV and gives the tool coverage of a third UK region.

---

## Why this is the current task

- SPEN_11kV and SSEN_11kV are live with full cross-checks. The rulepack architecture is proven to scale.
- The remaining DNOs are the active priority per master truth §5.
- NIE is the natural next step — it covers a geographically distinct area (Northern Ireland) so network bounds are easy to define without the SEPD+SHEPD disjoint-area complication SSEN had.

---

## Work sequence

1. Add `NIE_11KV_RULES` to `app/dno_rules.py`, extending `BASE_RULES` as SPEN and SSEN do.
2. Use real published values where known (height range per ENA TS 43-8 for 11kV; NIE network bounds — Northern Ireland roughly lat 54.0–55.3, lon -8.2 to -5.4).
3. Register it in the `RULEPACKS` dict as `"NIE_11kV"`.
4. Add at least one test in `tests/test_qa_engine.py` covering the NIE rulepack (registration + valid NI pole).
5. Run `pytest -v` — all tests must pass.
6. `git add / commit / push`.
7. Update `04_SESSION_HANDOFF.md`, append to `CHANGELOG.md`, and adjust master truth §4 rulepack list + §5 priority list.

---

## After this task, next in line

1. Add ENWL, NGED, UKPN rulepacks (the three remaining UK DNOs).
2. Wire `app/routes/api_rulepacks.py` to the real `RULEPACKS` dict.
3. Fix `Makefile` stale port (5010 → 5001).

See master truth §5 for the full current priority list.

---

## Not in scope

- Broad feature expansion.
- Browser E2E testing (Playwright) — later.
- Deployment / hosting — later.
- UI redesign — later.
- Database integration — not planned.
