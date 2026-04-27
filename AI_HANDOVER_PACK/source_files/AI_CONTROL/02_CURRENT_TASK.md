# Current Task

## Phase

**Stage 3B complete — next decision pending**

Stage 3B (Designer Review & Export Readiness) is implemented and validated. It is now closed.

The next direction has not yet been decided by the project orchestrator.

---

## Stage 3B is closed

- Design brief: `AI_CONTROL/21_STAGE_3B_DESIGN_BRIEF.md`
- Implementation: commits `a9b3ee2`, `7daa5a9`
- Validation acceptance: `AI_CONTROL/22_STAGE_3B_VALIDATION_ACCEPTANCE.md`
- Tests: 273 passing, pre-commit clean

---

## Open next-direction choice

The project orchestrator must choose between:

**Option A — Stage 3B polish**

Address known caveats within the Stage 3B scope:
- Section boundary editing (confirm or move auto-detected splits)
- PDF report updated to show reviewed pairing state
- Configurable reviewer role label
- Review page accessible from project overview action buttons
- Validation warnings for stale override references after reprocess

**Option B — Stage 3A planning**

Stage 3A is the live intake platform:
- Surveyor syncs controller data daily or continuously
- Tool immediately validates and produces completeness reports
- Designer sees the job building in real-time
- Feedback loop closes while the surveyor is still on site

Neither option should begin without the orchestrator defining the scope.

---

## What not to do before the next stage is defined

- Do not begin section boundary editing
- Do not begin cloud deployment or authentication
- Do not redesign architecture
- Do not begin Stage 4, 5, or 6 work
- Do not add new QA rules or sequencing algorithms

---

## Relevant files

- `AI_CONTROL/21_STAGE_3B_DESIGN_BRIEF.md`
- `AI_CONTROL/22_STAGE_3B_VALIDATION_ACCEPTANCE.md`
- `app/review_manager.py`
- `app/routes/api_review.py`
- `app/routes/review_page.py`
- `app/templates/review.html`
- `tests/test_review_manager.py`
- `tests/test_review_integration.py`
