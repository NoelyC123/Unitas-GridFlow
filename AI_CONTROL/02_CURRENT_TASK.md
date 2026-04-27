# Current Task

## Phase

**Stage 3A1 complete — next step is Stage 3A2 cloud/remote access planning**

Stage 3A1 (Local Daily Intake MVP) is implemented and validated. It is now closed.

The next direction is Stage 3A2 planning: define the smallest safe cloud/remote access path without beginning deployment work prematurely.

---

## Stage 3A1 is closed

- Design brief: `AI_CONTROL/23_STAGE_3A_DESIGN_BRIEF.md`
- Validation acceptance: `AI_CONTROL/24_STAGE_3A_VALIDATION_ACCEPTANCE.md`
- Focused tests: `tests/test_project_manager.py tests/test_project_integration.py` — 41 passing
- Real-file validation: Gordon single-day intake and Strabane 474/474c multi-file intake passed

---

## Next-direction choice

Proceed to **Stage 3A2 cloud/remote access planning**.

The plan should cover:

- simple managed hosting options
- shared-password/basic access control
- upload storage and backup
- mobile upload constraints
- UK/EU data sensitivity and hosting preference
- what remains local-only until product value is proven

---

## What not to do before the next stage is defined

- Do not begin section boundary editing
- Do not begin cloud deployment or authentication before Stage 3A2 plan approval
- Do not redesign architecture
- Do not begin Stage 4 tablet capture
- Do not begin Stage 5 or 6 work
- Do not add new QA rules or sequencing algorithms

---

## Relevant files

- `AI_CONTROL/23_STAGE_3A_DESIGN_BRIEF.md`
- `AI_CONTROL/24_STAGE_3A_VALIDATION_ACCEPTANCE.md`
- `app/project_manager.py`
- `app/routes/api_projects.py`
- `app/templates/project.html`
- `app/templates/upload.html`
- `app/static/js/upload-manager.js`
- `tests/test_project_manager.py`
- `tests/test_project_integration.py`
