# Stage 4C Architecture Fix Recommendation

**Date:** 2026-05-17
**Reference:** `AI_CONTROL/42_MATCHING_ENGINE_ANALYSIS.md`,
`AI_CONTROL/43_VALIDATOR_COMPARISON.md`

---

## Current Problem

- `validate_phase4_matching.py` → **12/12 matched** (structural gate, works)
- `run_pipeline.py` → **0/10 matched** (full pipeline, broken on P_LOCAL_002)
- Same inputs, completely different outcomes

The full pipeline fails because it cannot match any baseline pole to a field folder —
despite both sides having the right data. The support number is present in the CSV, and the
folder names parse it correctly, but the data model layer loses the value during format
detection.

---

## Root Cause (Summary)

Four bugs, two critical:

**Bug 1 (Critical):** `CSVParser._parse_generic()` cannot find the support number column
in `P_LOCAL_002_baseline.csv`. The column is `pole_id`, which contains no word "support"
or "name". Result: `support_no = None` for all baseline poles.

**Bug 2 (Critical):** `SupportNumberMatcher._try_match()` only tries to match on
`bp.support_no`. When `support_no` is `None`, `b_key = ""` and no match is possible.
The `bp.pole_id` value (which contains the correct support number) is never tried.

**Bug 3 (Medium):** Both CSV parser paths (`_parse_enwl` and `_parse_generic`) skip rows
with blank easting/northing. Poles 903101 and 903203 vanish from the baseline dataset
entirely, so they can never receive `baseline_coordinate_missing` flags.

**Bug 4 (Medium):** `FolderScanner.NOTES_EXTENSIONS = {".txt", ".TXT"}` misses `.md` files.
All P_LOCAL_002 notes are `.md`. Notes content never reaches the merged output.

---

## Options

### Option A: Fix `run_pipeline.py` Matching (Recommended)

**Approach:** Surgical fixes to two existing modules.

**Fix 1 — `gridflow/baseline/csv_parser.py`, `_parse_generic()`:**

```python
# After the existing support_col search fails:
if not support_col:
    # Fall back: if pole_id values look like support numbers, use that column
    if id_col and all(
        any(c.isdigit() for c in str(v).strip())
        for v in df[id_col].dropna().head(3)
    ):
        support_col = id_col
```

This teaches the GENERIC parser to recognise `pole_id` as a support number when no
better column is found.

**Fix 2 — `gridflow/matching/support_number_matcher.py`, `_try_match()`:**

Add a third attempt after the existing two:

```python
# Attempt 3: fall back to pole_id when support_no was absent
if not (bp.support_no or "").strip():
    pid_key = self._normalize(baseline_pole.pole_id)
    if pid_key and pid_key in field_by_normalized:
        fp = field_by_normalized[pid_key]
        return MatchResult(
            baseline_pole_id=baseline_pole.pole_id,
            baseline_support_no=baseline_pole.pole_id,
            field_folder=fp.folder_name,
            field_support_no=fp.support_no,
            match_type="EXACT",
            confidence_reasons=["POLE_ID_USED_AS_SUPPORT_NO"],
        )
```

This ensures the matcher can find poles even when `support_no` was not populated.

**Fix 3 — `gridflow/baseline/csv_parser.py`, both `_parse_enwl` and `_parse_generic`:**

Remove the `continue` for blank coordinates:

```python
# Before (drops the pole):
if easting is None or northing is None:
    continue

# After (includes the pole with a flag):
if easting is None or northing is None:
    # Include pole but mark as coordinate-incomplete
    # verification_flag_generator will surface this as baseline_coordinate_missing
    pass
```

**Fix 4 — `gridflow/field/folder_scanner.py`:**

```python
NOTES_EXTENSIONS = {".txt", ".TXT", ".md", ".MD"}
```

**Timeline:** 1 day per fix. All four can be done independently. Fixes 1 and 2 are
blocking; Fixes 3 and 4 are recommended alongside.

**Risk:** LOW. These are targeted changes to two well-tested modules. Each fix has a
clear test case (P_LOCAL_002 as regression test).

**Tests required:**
- Fix 1: `test_parse_generic_uses_pole_id_as_support_no_when_no_support_col()`
- Fix 2: `test_matcher_falls_back_to_pole_id_when_support_no_is_none()`
- Fix 3: `test_parse_includes_poles_with_blank_coordinates()`
- Fix 4: `test_folder_scanner_reads_md_notes_files()`

---

### Option B: Use `validate_phase4_matching.py` as Primary Validator

**Approach:** Declare `validate_phase4_matching.py` the official Stage 4C validator
and do not use `run_pipeline.py` for P_LOCAL_002.

**Timeline:** Immediate — it already works.

**Risk:** LOW for short-term validation. HIGH for longer term because:
- Does not produce merged records or QA reports
- Does not score evidence quality
- Does not generate the 10 standard output files
- Does not detect verification flags
- Does not feed the workspace (`04_merged_dataset.json` is never written)

This option is viable as a temporary gate while Option A fixes are implemented, but
it is not a permanent solution. The full pipeline is the product.

---

### Option C: Unify Pipelines (Not Recommended for Stage 4C)

**Approach:** Refactor `run_pipeline.py` to use the same simple CSV reading and field
index logic as `validate_phase4_matching.py`.

**Timeline:** 1–2 weeks minimum.

**Risk:** HIGH. The `gridflow/` module stack is tested and serves multiple functions
(matching, merge, reports, workspace, ENWL evidence integration). Replacing the underlying
data models to use a simpler approach would break the workspace, the report generators, and
the Stage 6A–6E ENWL integration layer. This is architectural scope creep for a bug that
can be fixed surgically.

---

## Recommendation

**Use Option A (fix the two critical bugs) with Option B as an immediate workaround.**

**Immediate actions:**
1. Use `validate_phase4_matching.py` to confirm 12/12 structural match for Stage 4C Task 1
   (validation run). This unblocks M1 immediately.

2. Assign Fix 1 and Fix 2 (CSV parser + matcher) to Codex as Stage 4C Task 2.5 before M2.

3. Add Fix 4 (`.md` notes) alongside Fix 2 — it is a one-line change with high value.

4. Add Fix 3 (coordinate gaps → include not skip) alongside Fix 1 — this enables the
   `baseline_coordinate_missing` flag that Task 2 in the plan requires.

**After fixes:**
- Re-run `run_pipeline.py` on P_LOCAL_002
- Confirm 12/12 matched (or 10/12 if coordinate poles are still absent pending Fix 3)
- Confirm all 10 reports generated
- Confirm 903101 and 903203 show `baseline_coordinate_missing` in the QA report

---

## Implementation Order

| Priority | Fix | File | Effort | Blocking |
|---|---|---|---|---|
| 1 | CSV parser: GENERIC recognises `pole_id` as support_no | `gridflow/baseline/csv_parser.py` | 2 hours | Yes — matching fails without it |
| 2 | Matcher: `pole_id` fallback when `support_no` is None | `gridflow/matching/support_number_matcher.py` | 2 hours | Yes — matching fails without it |
| 3 | Notes scanner: add `.md` to extensions | `gridflow/field/folder_scanner.py` | 30 min | No — but high value |
| 4 | CSV parser: include coordinate-blank rows with flag | `gridflow/baseline/csv_parser.py` | 2 hours | No — needed for `baseline_coordinate_missing` |

Fixes 1 and 3 can be done in the same PR. Fixes 2 and 4 can be done in the same PR.
All four tests should be added together.

---

## Validation After Fix

```bash
python scripts/run_pipeline.py \
  --baseline real_pilot_data/P_LOCAL_002/csv/P_LOCAL_002_baseline.csv \
  --field real_pilot_data/P_LOCAL_002/enwl_enrichment_clean \
  --output /tmp/plocal002_fixed \
  --job-id P_LOCAL_002_FIXED \
  --register \
  --overwrite-registration
```

**Expected results after all four fixes:**
- Stage 1: 12 poles parsed (not 10) — 903101 and 903203 included with coordinate gaps
- Stage 2: 12 poles scanned with `notes_present = True` (not False)
- Stage 3: 12/12 matched (not 0/10)
- Stage 4: 12 merged poles, all `design_blocked = True`
- QA report: 903101 and 903203 flagged with `baseline_coordinate_missing`
- QA report: Pole 06 structural conflict flagged (pending Task 3 from plan)
- All 10 standard reports generated
