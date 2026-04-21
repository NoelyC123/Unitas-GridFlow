# Current Task

## Immediate task

Add `ENWL_11kV` rulepack to `app/dno_rules.py`.

ENWL (Electricity North West Limited) is the DNO for North West England. Adding it continues the pattern established by SPEN_11kV, SSEN_11kV, and NIE_11kV.

---

## Why this is the current task

- NIE_11kV is now live (committed 21 April 2026). Three rulepacks proven.
- ENWL, NGED, and UKPN are the remaining UK DNOs per master truth §5.
- ENWL covers a geographically distinct area (North West England) with a clean contiguous bounding box.

---

## Work sequence

1. Add `ENWL_11KV_RULES` to `app/dno_rules.py`, extending `BASE_RULES` as the existing rulepacks do.
2. Use real published values: height range per ENA TS 43-8 for 11kV (7–20m); ENWL network bounds — North West England roughly lat 53.3–54.7, lon -3.4 to -1.8.
3. Include: Pole ID regex, paired coord checks, material/structure_type consistency, coord_consistency (100m) — same pattern as existing rulepacks.
4. Register it in the `RULEPACKS` dict as `"ENWL_11kV"`.
5. Add two tests in `tests/test_qa_engine.py`: registration check + valid ENWL pole passes (realistic NW England coords).
6. Run `pytest -v` — all tests must pass.
7. `git add / commit / push`.
8. Update `04_SESSION_HANDOFF.md`, append to `CHANGELOG.md`, and adjust master truth §4 rulepack list + §5 priority list.

---

## After this task, next in line

1. Add NGED_11kV (National Grid Electricity Distribution — Midlands, SW England, S Wales).
2. Add UKPN_11kV (UK Power Networks — London, SE England, East Anglia).
3. Wire `app/routes/api_rulepacks.py` to the real `RULEPACKS` dict.
4. Fix `Makefile` stale port (5010 → 5001).

See master truth §5 for the full current priority list.

---

## Not in scope

- Broad feature expansion.
- Browser E2E testing (Playwright) — later.
- Deployment / hosting — later.
- UI redesign — later.
- Database integration — not planned.
