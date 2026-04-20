# Current Task

## Immediate task

Add `SSEN_11kV` rulepack to `app/dno_rules.py`.

This proves the rulepack architecture works for multiple DNOs and extends coverage beyond SPEN.

---

## Why this is the current task

- SPEN_11kV is now solid — includes corrected height range, pole ID regex, paired coord checks, network bounds, structure/material consistency, and lat/lon ↔ easting/northing coordinate consistency.
- The control layer has just been consolidated; further refactor work has diminishing returns.
- Only one DNO is currently supported. A second one is the logical next extension.

SSEN (Scottish and Southern Electricity Networks) is the natural second choice — it covers central/southern Scotland and southern England, with similar but distinct standards to SPEN.

---

## Work sequence

1. Add `SSEN_11KV_RULES` to `app/dno_rules.py`, extending `BASE_RULES` as SPEN does.
2. Use real published values where known (height range per ENA TS 43-8 for SSEN voltage class; SSEN network coordinate bounds; relevant pole/structure standards).
3. Register it in the `RULEPACKS` dict as `"SSEN_11kV"`.
4. Add at least one test in `tests/test_qa_engine.py` or `tests/test_api_intake.py` that covers the SSEN rulepack.
5. Run `pytest -v` — all tests must pass.
6. `git add / commit / push`.
7. Update `04_SESSION_HANDOFF.md`, append to `CHANGELOG.md`, and adjust master truth §4 rulepack list + §5 priority list.

---

## After this task, next in line

1. Add remaining DNO rulepacks (NIE, ENWL, NGED, UKPN).
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
