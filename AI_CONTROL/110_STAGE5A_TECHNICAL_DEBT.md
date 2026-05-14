# Stage 5A Technical Debt

## Evidence Quality Logic Duplication

**Location:**

- `gridflow/reports/dno_request_reporter.py` lines 178-181
- `gridflow/reports/design_readiness_reporter.py` lines 129-136

**Issue:**

Both reporters contain embedded evidence quality scoring logic:

- Field photo count >= 3
- Notes content present
- NO_POLE_POPUP flag -> MEDIUM

This duplicates `EvidenceQualityScorer` from `gridflow/field/evidence_quality_scorer.py`
and diverges slightly by not checking `map_screenshot_count`.

**Current Impact:**

For P_LOCAL_001, numbers match: 9 HIGH, 1 MEDIUM, 0 LOW. There is no immediate
pilot output problem.

**Future Risk:**

If `EvidenceQualityScorer` logic changes, reporters may silently diverge and
show incorrect statistics.

**Resolution Options:**

1. **Import and reuse:** Reporters should import `EvidenceQualityScorer` instead
   of reimplementing.
2. **Accept divergence:** If reports need different quality criteria than the
   pipeline, document why.
3. **Centralize:** Extract quality scoring to a `MergedPole.evidence_quality_summary`
   property or equivalent report helper.

**Priority:** LOW. This does not block Stage 5A.1 merge, but should be tracked
for Stage 5A.2 or Stage 5B refactor.

**Discovered:** 2026-05-14, Claude Code review of Stage 5A.1.
