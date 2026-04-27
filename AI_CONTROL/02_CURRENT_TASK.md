# Current Task

## Phase

**Stage 3C closure → Stage 3B planning**

Stage 3C (Project Management / multi-file job support) is implemented and manually validated. It is now closed.

The next task is for the project orchestrator (Claude Desktop) to define the Stage 3B brief before any code work begins.

---

## Stage 3C is closed

- Implementation: commit `b0b5331`
- Validation: passed across Gordon, 474 + 474c (multi-file), 513, and legacy J##### jobs
- Validation acceptance: `AI_CONTROL/20_STAGE_3C_VALIDATION_ACCEPTANCE.md`
- Tests: 244 passing, pre-commit clean

---

## What Stage 3B is (planned, not started)

**Stage 3B — Designer Review & Export Readiness**

Stage 3B will allow a designer to review and adjust the auto-generated processing outputs before exporting:

- EXpole pairing reassignment (confirm or override auto-detected pairs)
- Section boundary selection (confirm or move auto-detected splits)

Stage 3B must not begin until the project orchestrator defines the exact scope and success criteria. The scope above is indicative only.

---

## What not to do before Stage 3B is defined

- Do not begin any designer review or editing UI
- Do not add combined project-level maps or exports
- Do not begin cloud deployment (Stage 3A)
- Do not add new QA rules or sequencing algorithms
- Do not redesign architecture
- Do not begin Stage 4, 5, or 6 work

---

## Handoff criteria: Stage 3C → Stage 3B

All criteria are now met:

1. Named projects work ✅
2. Multi-file projects work ✅
3. Project overview is usable ✅
4. All existing outputs accessible from project page ✅
5. Real multi-file project validated (474 + 474c) ✅

---

## Relevant files

- `AI_CONTROL/20_STAGE_3C_VALIDATION_ACCEPTANCE.md`
- `AI_CONTROL/19_STAGE_3_EXECUTION_PLAN.md` (Stage 3B scope notes in section B)
- `app/project_manager.py`
- `app/routes/api_projects.py`
- `app/routes/projects_page.py`
- `tests/test_project_manager.py`
- `tests/test_project_integration.py`
