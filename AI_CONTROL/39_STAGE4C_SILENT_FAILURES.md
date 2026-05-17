# Stage 4C Pipeline Silent Failures

Date: 2026-05-17
Run: `validation_runs/P_LOCAL_002/pipeline_run_2026-05-17_181047`

## Critical Issues Identified

### Issue 1: Blank Coordinates Silently Dropped
**Severity:** HIGH
**Impact:** 2/12 baseline poles (903101, 903203) dropped without warning
**Expected:** Flag as missing, include in output with warning
**Actual:** Silently excluded from processing
**Fix Priority:** P0 (critical)
**File:** `gridflow/baseline/csv_parser.py`

### Issue 2: Notes Not Detected
**Severity:** HIGH
**Impact:** 0/12 notes detected despite 12 `pole_notes.md` files existing
**Expected:** 12/12 notes detected and parsed
**Actual:** Notes completely missed
**Fix Priority:** P1 (high)
**File:** `gridflow/field/folder_scanner.py`

### Issue 3: Evidence Quality Collapsed
**Severity:** MEDIUM
**Impact:** Complete evidence pack rated as LOW quality
**Expected:** Accurate quality assessment (HIGH/MEDIUM)
**Actual:** All poles downgraded to LOW
**Fix Priority:** P1 (high)
**File:** `gridflow/field/evidence_quality_scorer.py`

### Issue 4: Matching Failed
**Severity:** CRITICAL
**Impact:** 0/10 poles matched despite proven structural identity
**Expected:** 10/10 or 12/12 matched (depending on coordinate handling)
**Actual:** Complete matching failure
**Fix Priority:** P0 (CRITICAL - blocking)
**File:** `gridflow/matching/support_number_matcher.py` and `gridflow/baseline/csv_parser.py`

### Issue 5: Stage 5 Reports Empty
**Severity:** MEDIUM
**Impact:** Reports show 0 baseline / 0 field (used merged-only data)
**Expected:** Show baseline and field counts separately
**Actual:** Reports collapsed to 0/0
**Fix Priority:** P1 (high)
**File:** `scripts/run_pipeline.py` and `gridflow/reports/*.py`

### Issue 6: QA Report Percentage Bug
**Severity:** LOW
**Impact:** UNMATCHED = 1000.0% (display bug)
**Expected:** Sensible percentage or N/A
**Actual:** Nonsense calculation
**Fix Priority:** P2 (medium)
**File:** `gridflow/merge/qa_report_generator.py`

### Issue 7: Baseline Identity Lost
**Severity:** MEDIUM
**Impact:** Unmatched baseline poles rendered as "None" (lost support numbers)
**Expected:** Show actual support numbers
**Actual:** Identity information lost
**Fix Priority:** P1 (high)
**File:** `gridflow/baseline/csv_parser.py`, `gridflow/merge/data_merger.py`, `gridflow/merge/qa_report_generator.py`

### Issue 8: False PASS Status
**Severity:** CRITICAL
**Impact:** Pipeline reports PASS despite 0% match, 0 merged poles
**Expected:** FAIL or PARTIAL with clear warnings
**Actual:** Green light when operationally failed
**Fix Priority:** P0 (CRITICAL - misleading)
**File:** `scripts/run_pipeline.py`

## Impact Assessment

**Pipeline Usability:** BROKEN for P_LOCAL_002
**Blocker for:** Stage 4C M1 acceptance
**Must Fix:** Issues 1, 4, 8 (P0 critical)
**Should Fix:** Issues 2, 3, 5, 7 (P1 high)
**Can Defer:** Issue 6 (P2 cosmetic)

## Fix Strategy

**Phase 1 (P0 - Blocking):**
1. Fix matching engine (Issue 4)
2. Fix blank coordinate handling (Issue 1)
3. Fix false PASS status (Issue 8)

**Phase 2 (P1 - High Priority):**
4. Fix notes detection (Issue 2)
5. Fix evidence quality assessment (Issue 3)
6. Fix Stage 5 report data (Issue 5)
7. Fix baseline identity loss (Issue 7)

**Phase 3 (P2 - Polish):**
8. Fix QA report percentage (Issue 6)

## Next Actions

1. Identify affected code modules for each issue
2. Create fix tasks for P0 issues first
3. Test fixes on P_LOCAL_002
4. Re-run validation
5. Expect: 10/12 or 12/12 matched (depending on coordinate handling)

---
## FIXES APPLIED (2026-05-17)

All 4 critical bugs fixed:

1. ✅ Bug 1: CSV parser uses `pole_id` fallback
2. ✅ Bug 2: Matcher tries `pole_id` when `support_no` missing
3. ✅ Bug 3: Blank coordinate rows included with flag
4. ✅ Bug 4: `.md` added to notes extensions

Validation:
- Before: `0/10` matched, `0/12` notes
- After: `12/12` matched, `12/12` notes
- Pipeline now functional for Stage 4C M1 validation (`PARTIAL` status remains correct until the two manual coordinate lookups are completed)
