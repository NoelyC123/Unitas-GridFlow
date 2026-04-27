# Current Task

## Phase

**Stage 3 mobile intake polish implemented — validate on phone**

Stage 3A1 (Local Daily Intake MVP) is implemented and validated. It is closed.

Stage 3A2 planning is documented in `AI_CONTROL/25_STAGE_3A2_DEPLOYMENT_PLAN.md`.

The Cloudflare Tunnel + Access route has been validated from a phone on mobile data. Stage 3A2 is closed as a controlled remote-access trial. The first controlled field trial has now been run with the real Gordon file through the protected remote workflow. Claude Desktop approved a narrow Stage 3 mobile usability follow-on, and the scoped homepage/navigation/project-file-card polish has been implemented.

Validation completed:

- Home page loaded through a temporary `trycloudflare.com` tunnel.
- `/projects/` loaded remotely.
- `/upload` loaded remotely.
- No real or sensitive survey CSVs were uploaded.
- Named tunnel `gridflow` created for `gridflow.unitasconnect.com`.
- Cloudflare Access email one-time PIN prompt appeared before app access.
- iPhone on mobile data authenticated successfully through Access.
- Non-sensitive `mock_survey.csv` uploaded remotely into project `P006` / `iPhone Test`.
- Project dashboard updated remotely.
- Map, PDF, D2D Chain, D2D Working, and Review routes responded successfully for `P006/F001`.
- Real Gordon file uploaded remotely as project `P007` / `F001`.
- Gordon processed successfully: 157 records, 39 issues, 126 PASS, 25 WARN, 4 FAIL.
- Gordon review marked reviewed with 24 matched EXpoles and 0 unmatched EXpoles.
- Gordon Map/PDF/D2D Chain/D2D Working/Review routes all worked.
- Field-trial finding: core workflow passed; biggest friction is mobile table/review layout and outdated homepage wording.
- Homepage wording updated from Stage 1 QA/compliance framing to survey-to-design project intake and D2D handoff framing.
- Navigation updated so Projects and New Upload are primary, with Legacy Jobs secondary.
- Project detail page now renders mobile file cards with status, intake context, key counts, office feedback, and Map/Review/PDF/D2D actions.

---

## Stage 3A1 is closed

- Design brief: `AI_CONTROL/23_STAGE_3A_DESIGN_BRIEF.md`
- Validation acceptance: `AI_CONTROL/24_STAGE_3A_VALIDATION_ACCEPTANCE.md`
- Focused tests: `tests/test_project_manager.py tests/test_project_integration.py` — 41 passing
- Real-file validation: Gordon single-day intake and Strabane 474/474c multi-file intake passed
- Stage 3A2 plan: `AI_CONTROL/25_STAGE_3A2_DEPLOYMENT_PLAN.md`

---

## Next task

Proceed to **phone validation of Stage 3 mobile intake polish**.

Use:

- Primary route: Cloudflare Tunnel + Cloudflare Access
- Fallback route: Tailscale trusted-device access
- Deferred: Render/Railway/full hosted deployment

Stage 3A2 proved:

- app reachable from a phone or external trusted device
- Cloudflare Access prompts for authentication before app access
- upload into a project works remotely with non-sensitive test data
- project dashboard updates remotely
- Map/PDF/D2D/Review links work remotely

Next validation:

- Open `https://gridflow.unitasconnect.com` from iPhone/mobile data once the local app reloads the updated templates.
- Confirm homepage wording and primary links now reflect Projects / New Upload / Legacy Jobs.
- Open project `P007` and confirm the survey file appears as a mobile card instead of a cramped table.
- Confirm Map / Review / PDF / D2D Chain / D2D Working actions are visible and tappable from the mobile card.
- Do not begin hosted deployment, app accounts, cloud storage, photo upload, tablet capture, or live Trimble sync.
- Defer always-on hosting, app accounts, cloud storage, photo upload, tablet capture, and live Trimble sync until explicitly approved.

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
- `AI_CONTROL/26_STAGE_3A_OPERATIONAL_RUNBOOK.md`
- `README.md`
- `app/project_manager.py`
- `app/routes/api_projects.py`
- `app/templates/project.html`
- `app/templates/upload.html`
- `app/static/js/upload-manager.js`
- `tests/test_project_manager.py`
- `tests/test_project_integration.py`
