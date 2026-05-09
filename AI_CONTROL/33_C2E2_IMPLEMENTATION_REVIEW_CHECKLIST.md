# C2E2 Implementation Review Checklist

## Purpose

Sign-off gates for reviewing Cursor's popup rendering implementation.
Use this after Cursor writes popup code against the C2E2 spec.

---

## Pre-Review: Scope Verification

Confirm Cursor's implementation only touched allowed files:

- [ ] `app/static/js/map-viewer.js` — popup rendering changes only
- [ ] `app/static/css/map-viewer.css` — popup styling only
- [ ] `app/templates/map_viewer.html` — optional template changes only
- [ ] NO changes to `app/routes/map_preview.py`
- [ ] NO changes to `app/qa_engine.py`
- [ ] NO changes to `app/span_generator.py`
- [ ] NO changes to `app/geometry_pipeline.py`
- [ ] NO changes to `app/controller_intake.py`
- [ ] New test files only in `tests/`

---

## Code Review Gates

### Gate 1 — Field Reference Used Correctly

- [ ] Popup renderer imports from `app/field_reference.py` (or reads via API endpoint)
- [ ] `get_missing_wording()` called with `structure_type` for height fields
- [ ] Missing values never shown as blank — always the wording from field_reference
- [ ] `format_field_display()` or equivalent used for numeric fields with units

### Gate 2 — Missing Value Wording Correctness

Run these manual checks against P001/F001 (Gordon Pt1):

- [ ] Pol popup → height shows "Not measured (intermediate pole)" or omitted, NOT blank
- [ ] EXpole popup with height → shows e.g. "9.2m"
- [ ] EXpole popup without height → shows "Not measured — check survey notes"
- [ ] Any popup → material shows "Not recorded in survey", NOT blank or "None"
- [ ] Relationship absent → shows "—", NOT blank or "null"

### Gate 3 — Field Groups Correct

- [ ] Identity fields shown first (pole_id, structure_type, asset_intent)
- [ ] Geometry fields in one group (easting, northing, height)
- [ ] Quality fields grouped (qa_status, issue/warn counts)
- [ ] Survey context grouped (name, material)
- [ ] Relationship fields only shown when relevant (non-null)

### Gate 4 — No Regression in Existing Behaviour

- [ ] Span popup still opens on span hover/click
- [ ] Route highlight still works (click span → group highlights)
- [ ] Review navigation (prev/next buttons) still works
- [ ] Map filter panel still works
- [ ] Geometry trust banner still shows for unverified spans
- [ ] Design blocker reasons still render in span popup

---

## Automated Test Gates

Run these before sign-off:

```bash
pytest tests/test_c2e2_popup_fields.py -v      # Must: all 94 pass
pytest tests/test_review_navigation_layer.py -v  # Must: all pass
pytest tests/test_route_highlight_layer.py -v    # Must: all pass
pytest tests/test_ux_truthfulness.py -v         # Must: all pass
pytest -v                                         # Must: all 810+ pass
pre-commit run --all-files                        # Must: all pass
```

---

## Manual Validation Steps

### Step 1 — P001/F001 (Gordon Pt1 — SPEN area)

1. Upload P001/F001 or open existing job
2. Click a `Pol` point → check popup
   - Height field: "Not measured (intermediate pole)" or not shown
   - Material: "Not recorded in survey"
3. Click an `EXpole` point with height → check popup
   - Height: shows "X.Xm"
   - Asset Intent: "Existing asset"
4. Click an `EXpole` without height → check popup
   - Height: "Not measured — check survey notes"
5. Click a replacement-pair EXpole → check popup
   - Relationship: "replacement_pair" (or "Replacement pair")

### Step 2 — P008/F001 (Bellsprings — NIE area)

1. Open P008/F001
2. Check same field wording as Step 1
3. Confirm QA WARN popups still show warning texts

### Step 3 — Review Navigation

1. Enter review mode
2. Prev/next buttons: confirm they still step through structural features
3. Active feature highlight: confirm still works
4. No JavaScript console errors from popup field changes

### Step 4 — Span Hover

1. Hover a span line → span popup opens
2. Span popup shows correct design_status, geometry_trust
3. Span popup `design_blocker_reasons` renders correctly (list of objects)

---

## Sign-off Criteria

All automated tests pass AND all manual checks pass.

| Gate | Status |
|------|--------|
| Scope check — no forbidden files changed | [ ] |
| All 810+ automated tests pass | [ ] |
| Missing value wording correct on Pol | [ ] |
| Missing value wording correct on EXpole | [ ] |
| Material shows "Not recorded in survey" | [ ] |
| Span popup not broken | [ ] |
| Review navigation not broken | [ ] |

Sign-off by: ___________  Date: ___________

---

*Produced by Claude Code claude-code/c2e2-support-suite on 2026-05-09.*
*Paired with: 32_C2E2_PRE_IMPLEMENTATION_GUIDE.md*
