# Stage 4C M1 Fix Implementation Plan

## P0 Fixes (Blocking - Must Complete)

### Fix 1: Matching Engine Failure
**Issue:** 0/10 matched despite structural identity proven
**Root cause:** Generic baseline import preserves `pole_id` but leaves `support_no = None`, while `SupportNumberMatcher` only matches on `support_no`.
**Fix approach:**
- Update generic baseline parsing so support identity is preserved in `support_no` when no dedicated support column exists.
- Add matcher fallback so `pole_id` can be used conservatively when `support_no` is absent.
- Re-test variant handling for `900342A`.
**Test:** Re-run pipeline, expect 10/12 or 12/12 matched
**Timeline:** same day

### Fix 2: Blank Coordinate Handling
**Issue:** 903101, 903203 silently dropped
**Root cause:** Baseline parser skips rows with missing `easting` or `northing` using `continue`.
**Fix approach:**
- Preserve rows with missing coordinates in `BaselineDataset`.
- Surface explicit warning metadata / validation flags instead of dropping them.
- Ensure downstream code tolerates missing coordinates without crashing.
**Test:** Poles appear in reports with `coordinate missing` flag
**Timeline:** same day

### Fix 3: False PASS Status
**Issue:** Pipeline reports PASS with 0% match
**Root cause:** `run_pipeline.py` marks `overall_status = PASS` unless an exception occurs.
**Fix approach:**
- Add post-stage health gates for:
  - zero matched poles on non-empty datasets
  - zero merged poles after successful matching stage
  - baseline rows dropped vs source rows
  - notes parsed zero when note files exist
- Emit `PARTIAL` or `FAILED` status with clear summary text.
**Test:** Pipeline reports FAIL or PARTIAL with 0% match
**Timeline:** same day

## P1 Fixes (High Priority)

### Fix 4: Notes Detection
**Issue:** 0/12 notes detected
**Root cause:** `FolderScanner` only recognises `.txt`, but the survey pack uses `pole_notes.md`.
**Fix approach:** Accept `.md` note files alongside `.txt`.
**Test:** `notes_present = 12/12`, notes parsed > 0
**Timeline:** same day

### Fix 5: Evidence Quality Assessment
**Issue:** Complete pack rated `12 LOW`
**Root cause:** Evidence scoring depends on `notes_present`, which is false because notes were not detected.
**Fix approach:** Fix note detection first, then confirm scoring thresholds on P_LOCAL_002.
**Test:** Quality distribution moves off `12 LOW`
**Timeline:** same day

### Fix 6: Stage 5 Report Data Roll-up
**Issue:** Reports 00/07 collapsed to `0 baseline / 0 field`
**Root cause:** Stage 5 report generation receives merged poles only, so failed merge collapses report context.
**Fix approach:** Pass baseline/field/matching metadata into report generation context and show upstream counts separately.
**Test:** Reports still show real input counts even when merged result is empty
**Timeline:** 1 day

### Fix 7: Baseline Identity Loss
**Issue:** Unmatched baseline poles rendered as `None`
**Root cause:** Report rendering uses `support_no` only; generic baseline parse left it empty.
**Fix approach:** Preserve support identity in baseline parse and fall back to `pole_id` in QA rendering.
**Test:** Unmatched baseline section shows actual support IDs
**Timeline:** same day

## P2 Fix (Polish)

### Fix 8: QA Report Percentage Bug
**Issue:** `UNMATCHED = 1000.0%`
**Root cause:** Confidence table divides unmatched by `dataset.total_matched or 1`.
**Fix approach:** Use baseline total or explicit N/A logic when matched count is zero.
**Test:** Percentages remain in `0–100%`
**Timeline:** same day

## Implementation Sequence

1. Code analysis complete
2. Fix generic baseline parsing identity + blank-coordinate preservation
3. Fix matching engine fallback
4. Fix overall status logic
5. Test all P0 fixes together
6. Fix notes detection and evidence quality
7. Fix report roll-up and QA display bugs
8. Re-run P_LOCAL_002 validation
9. Expected outcome: 10/12 or 12/12 matched, accurate status

## Acceptance Criteria

- [ ] Matching engine finds 10+ matches (not 0)
- [ ] Blank coordinates flagged (not dropped)
- [ ] Pipeline status accurate (FAIL/PARTIAL if broken)
- [ ] Notes detected (12/12 not 0/12)
- [ ] Evidence quality accurate (not all LOW)
- [ ] Re-run shows improvement
