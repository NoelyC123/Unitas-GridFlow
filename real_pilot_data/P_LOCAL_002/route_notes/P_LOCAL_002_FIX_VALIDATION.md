# P_LOCAL_002 Pipeline Fix Validation

## Changes Made

### Bug 1: CSV Parser Support Number Fallback
- File: `gridflow/baseline/csv_parser.py`
- Change: Use `pole_id` as `support_no` fallback when no `support` / `name` column exists
- Result: All baseline poles now have support identity

### Bug 2: Matcher Pole ID Fallback
- File: `gridflow/matching/support_number_matcher.py`
- Change: Try `pole_id` when `support_no` is `None` / empty
- Result: Matching now works for generic baseline imports

### Bug 3: Blank Coordinate Handling
- File: `gridflow/baseline/csv_parser.py`
- Change: Include rows with blank coordinates, flag as `MISSING`
- Result: `903101`, `903203` now remain in baseline dataset and are warning-tracked

### Bug 4: Notes Extensions
- File: `gridflow/field/folder_scanner.py`
- Change: Added `.md` to `NOTES_EXTENSIONS`
- Result: `12/12` notes now detected

## Before Fixes (Run 2026-05-17_181047)
- Baseline parsed: `10/12`
- Matched: `0/10`
- Notes detected: `0/12`
- Status: `PASS` (false positive)

## After Fixes (Run 2026-05-17_184451)
- Baseline parsed: `12/12` ✅
- Matched: `12/12` ✅
- Notes detected: `12/12` ✅
- Status: `PARTIAL` ✅ (accurate — coordinate gaps remain)

## Validation Status
- [x] All 4 bugs fixed
- [x] Pipeline re-run successful
- [x] Matching works
- [x] Notes detected
- [x] Blank coordinates flagged

## Next Steps
1. Manual ENWL coordinate lookup (`903101`, `903203`)
2. Update baseline CSV with coordinates
3. Re-run validation (expect `12/12` matched with complete baseline)
4. Stage 4C M1 acceptance
