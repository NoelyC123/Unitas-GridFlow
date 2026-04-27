# Stage 3A2 Planning Brief — Remote Access Trial

## Prepared by: Claude Desktop (Project Orchestrator)
## Date: April 2026
## Status: Planning brief — no deployment until approved

---

## Executive Summary

Stage 3A2 makes the existing Stage 3A1 daily-intake workflow reachable from outside the local machine so a surveyor in the field can upload files and a designer in the office can see them without a USB handoff. The central question is not "which cloud provider" — it is "can the current intake workflow work remotely without turning the project into a cloud platform too early?"

The recommended next step is a controlled remote-access trial:

1. Run the existing Flask app on the office Mac.
2. Expose it with **Cloudflare Tunnel**.
3. Protect it with **Cloudflare Access** email / one-time PIN.
4. Test from a phone or external device using real project upload/review/export flows.

Tailscale remains the private fallback if a closed trusted-device network is preferred. Render/Railway/full hosted deployment is deferred until the remote workflow proves useful and data handling requirements are clearer.

---

## 1. Should Stage 3A2 be plan only, or include implementation?

**Planning plus a working remote-access trial.**

Stage 3A2 should include documentation and a zero/near-zero-code proof that the app can be reached from a trusted remote device. The first implementation is operational setup, not app development.

Do now:

- Create and commit this remote-access plan.
- Add README instructions for a local remote-access trial.
- Run the app locally and expose it through Cloudflare Tunnel.
- Validate upload, project dashboard, Review, Map/PDF/D2D exports from a phone or external device.

Do later only if the trial proves useful:

- Decide whether the tool needs an always-on hosted deployment.
- Consider Docker/gunicorn/app-level auth.
- Consider persistent hosted storage and backup.

---

## 2. What should the first remote/cloud access version include?

The first remote version should include:

- Remote HTTPS access to the current Flask app.
- Cloudflare Access in front of the URL, limited to approved email addresses.
- Upload into an existing named project from a phone/tablet.
- Survey day / visit label, uploaded-by, and surveyor note fields working remotely.
- Project dashboard showing intake status and office feedback remotely.
- Existing Map, PDF, D2D Chain, D2D Working, and Review links working remotely.
- Short validation notes recording what worked, what failed, and what felt awkward.

What it does NOT need:
- User accounts or login pages
- Database backend
- S3/MinIO object storage
- Multi-tenant isolation
- Mobile-optimised UI (the existing Bootstrap UI is reasonably responsive)
- Photo upload, tablet forms, or live Trimble sync

---

## 3. Which route makes most sense first?

### Option analysis

| Option | Code changes | Time to working | Remote access | Persistence | Cost | Risk |
|--------|-------------|----------------|---------------|-------------|------|------|
| **A. Local network (0.0.0.0)** | 1 line (bind address) | 5 minutes | Same WiFi only | Local disk | Free | Very low |
| **B. Tailscale** | Zero | 30 minutes | Anywhere (private mesh) | Local disk | Free (personal) | Very low |
| **C. Cloudflare Tunnel + Access** | Zero | 30 minutes | Anywhere (HTTPS URL with access gate) | Local disk | Free tier | Low |
| **D. Render/Railway** | Dockerfile + gunicorn | 2-4 hours | Anywhere (public URL) | Persistent volume | ~$7-15/month | Medium |
| **E. VPS (DigitalOcean)** | Dockerfile + nginx + SSL | 1-2 days | Anywhere (public URL) | Disk | ~$5-12/month | Medium-High |

### Recommendation: **Option C (Cloudflare Tunnel + Access) first, Option B (Tailscale) as fallback**

**Why Cloudflare Tunnel first:**

Tailscale requires both the server machine and the surveyor's device to have Tailscale installed. That is excellent for a closed trusted network, but it adds friction for a field trial. Cloudflare Tunnel gives a normal HTTPS browser URL protected by Cloudflare Access. The surveyor opens a URL on their phone, authenticates by approved email / one-time PIN, uploads the CSV, and the office sees it.

**Why not go straight to Render/Railway:**

The app currently uses filesystem storage (`uploads/projects/P001/files/F001/`). Render's free tier uses ephemeral storage — files vanish on redeploy. Render's paid tier has persistent disks, but you'd need to restructure file paths or add volume mounting. That's unnecessary complexity before proving remote access actually changes the workflow. Running on your Mac with a tunnel gives you persistent storage for free.

**When hosted deployment becomes relevant:**

Your Mac has to be running for the tunnel to work. If the remote workflow proves useful and the tool needs to be always-on, then a separate hosted deployment decision is justified. That later step must address persistent storage, backups, authentication, and data handling before code is written.

---

## 4. What authentication/access control should we use?

**Remote trial: Cloudflare Access**

Cloudflare Tunnel includes Cloudflare Access, which can add a login gate in front of the tunnel. Options:
- One-time PIN sent to an email address (no password to remember)
- Shared secret / service token
- Simple email allowlist

This is built into Cloudflare's free tier and requires zero code changes to the Flask app. The auth happens at the tunnel level before requests reach your app.

**Fallback if Cloudflare Access is not available: Tailscale or temporary local-only testing**

If Cloudflare Access is awkward for the first test, use Tailscale with trusted devices. Do not build app-level accounts or roles for Stage 3A2.

**What NOT to build:**
- User accounts or registration
- Role-based access (admin vs surveyor vs designer)
- OAuth / SSO
- Session management beyond basic cookie
- Password reset flow

---

## 5. What data/privacy issues matter for UK DNO survey data?

This is the most important non-technical question.

**What the data contains:**
- Precise GNSS coordinates of UK electricity distribution infrastructure (pole positions, exact eastings/northings)
- DNO job references (e.g. "28-14 513" which references a real NIE Networks job number)
- Route geometry showing where overhead lines run
- Surveyor names / uploaded-by labels
- Designer review notes

**Regulatory context:**
- UK GDPR applies to personal data (surveyor names, uploaded-by labels)
- Infrastructure coordinates may be commercially sensitive to the DNO (not classified, but not public)
- Some DNO contracts may have data handling clauses restricting where survey data can be stored

**Practical implications for Stage 3A2:**

| Concern | Phase 1 (Tunnel) | Phase 2 (Render) |
|---------|-----------------|-----------------|
| Data location | Your Mac — UK, your control | Render EU region — Frankfurt or similar |
| Data in transit | HTTPS via Cloudflare — encrypted | HTTPS via Render — encrypted |
| Data at rest | Your Mac's disk — your responsibility | Render persistent volume — Render's responsibility |
| Access control | Cloudflare Access gate | Flask basic auth |
| DNO contract compliance | Data stays on your hardware — likely fine | Data on cloud provider — check contract terms |

**Recommendation:** The tunnel trial avoids cloud-storage questions because data at rest remains on the office Mac. Traffic still passes through Cloudflare for the tunnel and access layer, so describe the trial accurately as "local data storage with protected HTTPS tunnel access," not as a full offline/private network. Hosted deployment requires checking whether employer or DNO contracts restrict storing survey data on third-party cloud infrastructure.

**Action for you:** Before deploying to Render, check with your employer whether survey data (specifically coordinates and job references) can be stored on a managed cloud service in the EU. If the answer is no or uncertain, the tunnel approach is your permanent solution until that's resolved.

---

## 6. What should stay out of scope?

Stage 3A2 will NOT implement:
- User accounts, registration, or role-based access
- Database backend (Postgres, SQLite, etc.)
- S3/MinIO object storage migration
- Automated backups
- Mobile-specific UI redesign
- Notification system (email/SMS when surveyor uploads)
- Multi-tenant isolation (multiple companies sharing one instance)
- CI/CD pipeline for automatic deployment
- Custom domain + DNS management (Cloudflare provides this automatically with the tunnel)
- Load balancing or horizontal scaling
- Photo/image upload capability
- Tablet capture forms
- PoleCAD-specific export
- New QA rules or sequencing changes

Deferred from Stage 3A2 but retained in the roadmap:

- Photo upload linked to survey files / pole records
- Tablet-based structured field capture
- Live or semi-live Trimble/controller sync

---

## 7. What files or docs should be updated?

Update now:

- `AI_CONTROL/25_STAGE_3A2_DEPLOYMENT_PLAN.md` — this document, committed as the Stage 3A2 plan
- `AI_CONTROL/01_CURRENT_STATE.md` — reflect Stage 3A2 planned / awaiting remote trial
- `AI_CONTROL/02_CURRENT_TASK.md` — make the next task the controlled tunnel trial
- `AI_CONTROL/04_SESSION_HANDOFF.md` — record the decision and next steps
- `CHANGELOG.md` — record the planning/documentation update
- `README.md` — add a short local remote-access trial section

---

## 8. Should Claude Code be used, or Cursor/GPT?

**Stage 3A2 planning/docs: Cursor/GPT.** This is a documentation and workflow-definition step.

**Tunnel trial: user + Cursor/GPT guidance.** This is mostly local setup and validation.

**Future hosted deployment/auth code: Claude Code if needed.** Use Claude Code only if the next step becomes a real code task such as Docker/gunicorn/auth middleware/persistent storage work.

---

## Recommended Option

**Stage 3A2: Cloudflare Tunnel + Cloudflare Access remote trial.**

Steps:
1. Install `cloudflared` on the Mac.
2. Authenticate with Cloudflare.
3. Start the Flask app locally.
4. Expose `http://localhost:5001` through a tunnel.
5. Add Cloudflare Access for approved email / one-time PIN before any real survey data is uploaded.
6. Test from a phone or external device.
7. Validate upload, project dashboard, Map/PDF/D2D exports, and Review page.

Total time: ~30 minutes. Zero code changes. Data stays on your Mac. HTTPS automatic. Access control via Cloudflare.

**Future hosted deployment:** Defer until the tunnel trial proves the remote intake workflow is valuable.

---

## Reasoning

1. The whole point of Stage 3A is closing the feedback loop while the surveyor is still on site. That requires remote access. A tunnel gives you remote access in 30 minutes with zero risk.

2. Cloud deployment (Render/VPS) is only needed when the tool needs to run independently of your Mac. You're currently validating workflow value. Your Mac being on during a controlled trial is acceptable.

3. The data sensitivity question is real. Survey coordinates of DNO infrastructure should not be casually put on a cloud server without checking contract terms. The tunnel approach keeps data at rest on your machine.

4. The existing docker-compose.yml is over-engineered for current needs (Minio, Postgres, nginx — none of which the app actually uses). Phase 2 should create a simpler Dockerfile that matches what the app actually needs, not what was speculatively configured.

---

## Risks

| # | Risk | Severity | Mitigation |
|---|------|----------|------------|
| 1 | **Mac must be running for tunnel to work.** Close laptop = surveyor can't upload. | Medium | Acceptable for Stage 3A2. Always-on hosting can be considered after validation. |
| 2 | **Cloudflare proxies the traffic.** The data is not hosted in Cloudflare, but traffic passes through Cloudflare services. | Low-Medium | Use Cloudflare Access and test with non-sensitive or approved survey files. Use Tailscale if a closed trusted-device network is preferred. |
| 3 | **Surveyor's mobile data in rural areas.** CSV uploads are small (~15KB for Gordon file) but mobile signal may be weak. | Low | CSV files are tiny. Even 2G can handle 15KB. If upload fails, retry later. |
| 4 | **No automated backup.** If your Mac dies, project data is lost. | Medium | You already make desktop backups manually. Phase 2 can add a backup script. |
| 5 | **DNO contract restrictions on remote data access.** Even with tunnel, the fact that survey data is accessible from the internet may concern some DNOs. | Low-Medium | The data stays on your machine. Only authenticated users can access it. Document this for any compliance conversations. |

---

## Acceptance Criteria

**Stage 3A2 is successful when:**
1. You can open the tunnel URL on your phone (not on your Mac's WiFi)
2. Cloudflare Access prompts for authentication
3. After authenticating, you can upload a CSV to a project
4. The project overview shows the uploaded file with correct processing results
5. Map, PDF, D2D exports all work through the tunnel
6. The designer review page works through the tunnel
7. Setup and data/access limitations are documented
8. No app user accounts, SaaS deployment, photo upload, tablet capture, or live Trimble sync are implemented

---

## Exact Next Task

**For the remote trial:**

```bash
# 1. Install cloudflared
brew install cloudflared

# 2. Authenticate with Cloudflare
cloudflared tunnel login

# 3. Create a tunnel
cloudflared tunnel create gridflow

# 4. Create config file
mkdir -p ~/.cloudflared
cat > ~/.cloudflared/config.yml << 'EOF'
tunnel: gridflow
credentials-file: /Users/noelcollins/.cloudflared/<TUNNEL_ID>.json

ingress:
  - hostname: gridflow.yourdomain.com
    service: http://localhost:5001
  - service: http_status:404
EOF

# 5. Add DNS route
cloudflared tunnel route dns gridflow gridflow.yourdomain.com

# 6. Start the app in one terminal
cd /Users/noelcollins/Unitas-GridFlow
source .venv312/bin/activate
python run.py

# 7. Start the tunnel in another terminal
cloudflared tunnel run gridflow

# 8. Set up Cloudflare Access before using real survey data
#    - Go to Zero Trust > Access > Applications
#    - Add application for gridflow.yourdomain.com
#    - Policy: require one-time PIN to allowed email addresses
```

If you do not have a domain on Cloudflare yet, use `cloudflared tunnel --url http://localhost:5001` for a quick temporary connectivity test only. Do not use real or sensitive survey data through a temporary unauthenticated URL.

After the trial, record whether phone upload, dashboard review, Map/PDF/D2D exports, and Review worked remotely. Then decide whether Stage 3A2 is complete or whether an always-on deployment plan is needed.

---

Come back after the tunnel trial and record: did it work, could you upload from your phone, did the office dashboard update, and did outputs/review work remotely?
