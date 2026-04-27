# Current Task

## Phase

**Stage 3A2 planned — run controlled remote access trial**

Stage 3A1 (Local Daily Intake MVP) is implemented and validated. It is closed.

Stage 3A2 planning is documented in `AI_CONTROL/25_STAGE_3A2_DEPLOYMENT_PLAN.md`.

The next task is a controlled Cloudflare Tunnel + Cloudflare Access trial against the existing local app.

---

## Stage 3A1 is closed

- Design brief: `AI_CONTROL/23_STAGE_3A_DESIGN_BRIEF.md`
- Validation acceptance: `AI_CONTROL/24_STAGE_3A_VALIDATION_ACCEPTANCE.md`
- Focused tests: `tests/test_project_manager.py tests/test_project_integration.py` — 41 passing
- Real-file validation: Gordon single-day intake and Strabane 474/474c multi-file intake passed
- Stage 3A2 plan: `AI_CONTROL/25_STAGE_3A2_DEPLOYMENT_PLAN.md`

---

## Next task

Proceed to **Stage 3A2 remote access trial**.

Use:

- Primary route: Cloudflare Tunnel + Cloudflare Access
- Fallback route: Tailscale trusted-device access
- Deferred: Render/Railway/full hosted deployment

The trial should prove:

- app reachable from a phone or external trusted device
- Cloudflare Access prompts for authentication before real survey data is used
- upload into an existing project works remotely
- project dashboard updates remotely
- Map/PDF/D2D/Review links work remotely

---

## What not to do before the next stage is defined

- Do not begin section boundary editing
- Do not begin Render/Railway/full hosted deployment
- Do not build app user accounts or role-based auth
- Do not redesign architecture
- Do not begin Stage 4 tablet capture
- Do not begin Stage 5 or 6 work
- Do not add new QA rules or sequencing algorithms
- Do not implement photo upload, tablet capture, or live Trimble sync in Stage 3A2

---

## Relevant files

- `AI_CONTROL/23_STAGE_3A_DESIGN_BRIEF.md`
- `AI_CONTROL/24_STAGE_3A_VALIDATION_ACCEPTANCE.md`
- `AI_CONTROL/25_STAGE_3A2_DEPLOYMENT_PLAN.md`
- `README.md`
- `app/project_manager.py`
- `app/routes/api_projects.py`
- `app/templates/project.html`
- `app/templates/upload.html`
- `app/static/js/upload-manager.js`
- `tests/test_project_manager.py`
- `tests/test_project_integration.py`
