# Session Handoff

## Date: 2026-04-27

## What happened this session

### Stage 3A2: Cloudflare Access-gated remote trial — complete

The primary Stage 3A2 route was validated using a named Cloudflare Tunnel and Cloudflare Access. Stage 3A2 is closed as a controlled remote-access validation success.

Operational setup completed:

- Cloudflare zone: `unitasconnect.com`
- Tunnel name: `gridflow`
- Tunnel hostname: `gridflow.unitasconnect.com`
- Tunnel origin: local GridFlow app on `http://localhost:5001`
- Cloudflare Access application: `gridflow`
- Access policy: email allow policy for Noel
- Authentication method: Cloudflare Access email / one-time PIN

Validation evidence:

1. iPhone on mobile data opened `https://gridflow.unitasconnect.com`.
2. Cloudflare Access login screen appeared before GridFlow loaded.
3. Email one-time PIN was received and accepted.
4. GridFlow loaded after authentication.
5. `/projects/` loaded remotely.
6. `/upload` loaded remotely.
7. Non-sensitive `sample_data/mock_survey.csv` was uploaded from iPhone.
8. Project dashboard updated with project `P006` / `iPhone Test`.
9. Local stored project metadata confirms:
   - file `F001`
   - filename `mock_survey.csv`
   - status `complete`
   - uploaded by `Noel`
   - surveyor note `Testing`
   - 5 poles
   - 10 issues
   - review status `reviewed`
10. Output routes for `P006/F001` returned successfully:
    - project dashboard
    - Map
    - PDF
    - D2D Chain
    - D2D Working
    - Review

Boundary:

- No real or sensitive survey CSVs were uploaded during the Access-gated test.
- No app accounts, app-level auth, hosted deployment, cloud storage migration, photo upload, tablet capture, or live Trimble sync were built.
- Data at rest remains on the local Mac; Cloudflare provides the protected HTTPS tunnel.
- Remote availability depends on the Mac and `cloudflared tunnel run gridflow` staying online.

Recommended next decision:

- Stage 3A2 is validated for the controlled remote-access trial objective.
- A later stage/decision is needed before always-on hosted deployment, backups, app-level accounts, or wider user rollout.

---

### Stage 3A2: Temporary tunnel connectivity — validated, not accepted

Cursor/GPT installed `cloudflared`, confirmed the local GridFlow app was reachable on `127.0.0.1:5001`, and started a temporary unauthenticated Cloudflare Tunnel using:

```bash
cloudflared tunnel --url http://localhost:5001
```

Temporary URL used:

- `https://basically-movements-morgan-surname.trycloudflare.com`

Phone / external-device validation passed:

1. Home page loaded.
2. `/projects/` loaded.
3. `/upload` loaded.

Important boundary:

- No real or sensitive survey CSVs were uploaded.
- This is **temporary unauthenticated connectivity validation only**.
- This is **not full Stage 3A2 acceptance** because Cloudflare Access is not active.
- Full Stage 3A2 acceptance still requires a Cloudflare domain/zone, named tunnel, and Cloudflare Access gate before any real survey-data workflow validation.

Next proper step:

1. Add a Cloudflare domain/zone.
2. Create a named `gridflow` Cloudflare Tunnel.
3. Add a DNS route such as `gridflow.<domain>`.
4. Configure Cloudflare Access with approved email / one-time PIN.
5. Then validate authenticated remote upload, project dashboard update, Map/PDF/D2D links, and Review.

---

### Stage 3A2: Remote Access Trial — planned

Cursor/GPT converted the Claude Desktop deployment analysis and ChatGPT review into a committed Stage 3A2 plan.

Key decision:

- Use **Cloudflare Tunnel + Cloudflare Access** as the first controlled remote-access trial.
- Use **Tailscale** as the private trusted-device fallback.
- Defer **Render/Railway/full hosted deployment** until the remote workflow proves useful and data handling requirements are clearer.
- Do not build app user accounts, cloud storage migration, photo upload, tablet capture, or live Trimble sync in Stage 3A2.

Files added or changed:

| File | Change |
|------|--------|
| `AI_CONTROL/25_STAGE_3A2_DEPLOYMENT_PLAN.md` | Stage 3A2 remote-access plan |
| `README.md` | Local remote-access trial commands and validation checklist |
| `AI_CONTROL/01_CURRENT_STATE.md` | Current state updated for Stage 3A2 plan |
| `AI_CONTROL/02_CURRENT_TASK.md` | Next task set to remote-access trial |
| `CHANGELOG.md` | Planning/documentation entry |

The next practical validation is to run the existing Flask app locally, expose it through Cloudflare Tunnel + Access, and test upload/dashboard/export/review from a phone or external trusted device.

---

### Stage 3A1: Local Daily Intake MVP — implemented and validated

Cursor/GPT implemented the approved Stage 3A1 local daily intake scope from `AI_CONTROL/23_STAGE_3A_DESIGN_BRIEF.md`.

Files added or changed:

| File | Change |
|------|--------|
| `AI_CONTROL/23_STAGE_3A_DESIGN_BRIEF.md` | New — Stage 3A1 local intake scope and Stage 3A2 cloud boundary |
| `AI_CONTROL/24_STAGE_3A_VALIDATION_ACCEPTANCE.md` | New — validation evidence |
| `app/project_manager.py` | Added intake metadata, office feedback update, and review-aware intake status |
| `app/routes/api_projects.py` | Added intake capture during project presign and office feedback API |
| `app/templates/upload.html` | Added survey day / uploaded-by / surveyor note fields |
| `app/static/js/upload-manager.js` | Sends intake metadata with project uploads |
| `app/templates/project.html` | Shows intake status, survey notes, and office feedback per file |
| `tests/test_project_manager.py` | Added intake metadata and status tests |
| `tests/test_project_integration.py` | Added intake API integration tests |

Focused validation:

- `tests/test_project_manager.py tests/test_project_integration.py` — 41 passing
- Real-file temporary-root validation passed for Gordon and Strabane 474/474c intake flows

Stage 3A1 remains local-only by design. Cloud/remote access is now a Stage 3A2 planning task, not an active implementation task.

---

### Stage 3B: Designer Review & Export Readiness — implemented and validated

Claude Code implemented the Stage 3B MVP across two commits in one work session, following the approved brief at `AI_CONTROL/21_STAGE_3B_DESIGN_BRIEF.md`.

**Commit `a9b3ee2`:** Add Stage 3B design brief

**Commit `7daa5a9`:** Add Stage 3B designer review overlay

Files added or changed:

| File | Change |
|------|--------|
| `app/review_manager.py` | New — review data layer |
| `app/routes/api_review.py` | New — review REST API |
| `app/routes/review_page.py` | New — review page route |
| `app/templates/review.html` | New — Bootstrap 5 review UI |
| `app/routes/d2d_export.py` | Modified — project exports apply review overlay |
| `app/routes/api_intake.py` | Modified — reprocessing clears stale review |
| `app/__init__.py` | Modified — blueprint registration |
| `tests/test_review_manager.py` | New — 20 unit tests |
| `tests/test_review_integration.py` | New — 9 integration tests |

**Test count:** 273 passing (up from 244)

**Pre-commit:** clean

---

### What Stage 3B delivers

A designer can now:

1. Navigate to `/review/project/<project_id>/<file_id>` to see the review page for a processed file.
2. View all auto-detected EXpole pairings in a table.
3. Reassign any EXpole to a different proposed pole using a dropdown, or mark it as unmatched.
4. Enter review notes and mark the file as "Reviewed".
5. Download D2D Chain or D2D Working View exports — reviewed exports show "Designer Reviewed — <timestamp>" in the header; unreviewed exports remain "provisional".
6. Reset the review at any time — deletes `review.json`, exports revert to auto-generated state.

The original `sequenced_route.json` is never modified. The review overlay is applied at export time on a deep copy.

---

### Previous session (Stage 3C — recorded for continuity)

Stage 3C (Project Management / multi-file job support) was implemented and validated in the prior session.

- Commit: `b0b5331`
- Test count at close of 3C: 244

---

## Current state

- Stage 3A1 local daily intake implemented and validated
- Stage 3A2 Cloudflare Tunnel + Access trial complete
- Temporary unauthenticated tunnel page reachability validated from phone/external device
- Access-gated remote upload/dashboard/export/review smoke test passed with non-sensitive data
- Stage 1 complete
- Stage 2A, 2B, 2C implemented and closed
- Stage 3C implemented and validated — commit `b0b5331`
- Stage 3B implemented and validated — commits `a9b3ee2`, `7daa5a9`
- Branch is up to date with `origin/master`

---

## Known caveats (by design — not bugs)

- EXpole pairing review only — section boundary editing deferred
- No route sequence editing, no pole attribute editing, no map-based editing
- No cross-file review — each file is reviewed independently
- Reviewed state affects D2D CSV exports only; PDF update deferred
- `reviewed_by` hardcoded to "Designer" — configurable later
- No multi-user conflict resolution — last-write-wins (single-user local use)
- Sequential P### IDs are not concurrent-safe (acceptable for single-user local use)
- Legacy J##### jobs not auto-migrated into projects

---

## Next steps

1. Use `AI_CONTROL/26_STAGE_3A_OPERATIONAL_RUNBOOK.md` to run the local app and named tunnel safely.
2. Prepare the first controlled field trial using the checklist in that document.
3. Keep using the named tunnel only for controlled trials while the Mac is online.
4. Do not begin Render/Railway/full hosted deployment, app accounts, Stage 4 tablet capture, Stage 5 designer workspace expansion, or Stage 6 submission packs yet.

---

## Tool usage instructions for next chat

Use Cursor/GPT as the default working agent for routine repo work:

- documentation updates
- validation notes
- small scoped implementation
- test/check runs
- commits for agreed, narrow changes
- operational guidance such as starting the app or tunnel

Use Claude Desktop selectively as the project orchestrator:

- stage closure decisions
- next-stage scope decisions
- ambiguous product direction
- commercial/strategic tradeoffs
- deciding whether to move from controlled tunnel trial to broader field trial, hosted deployment, or later-stage work

Do not use Claude Desktop for routine admin, small doc edits, or obvious mechanical updates.

Use Claude Code only when the task is code-heavy, risky, or benefits from autonomous repo-wide implementation:

- multi-file feature implementation
- complex refactors
- substantial test additions
- debugging failures that require broad code inspection
- infrastructure/code changes beyond simple operational setup

Do not use Claude Code for routine docs, small validation records, or simple command guidance.

Use ChatGPT as a second-opinion / analysis tool when useful:

- reviewing strategic options
- challenging assumptions
- commercial framing
- comparing deployment/access approaches
- drafting questions for orchestrator review

Do not treat ChatGPT output as project truth unless it is reviewed and folded into the active control layer.

Source-of-truth order remains:

1. Real validation evidence
2. `AI_CONTROL/` active control files
3. Repo code and tests
4. Documentation
5. AI outputs

Current hard boundary:

- Do not build app accounts, hosted deployment, cloud storage migration, photo upload, tablet capture, live Trimble sync, Stage 4, Stage 5, or Stage 6 work unless explicitly approved as a new stage/task.
