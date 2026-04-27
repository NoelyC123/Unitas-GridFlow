# Stage 3A Operational Runbook and Field-Trial Checklist

## Status

Stage 3A2 is closed. This runbook supports controlled remote trials using the existing local GridFlow app and the named Cloudflare Tunnel.

This is an operational document only. It does not approve hosted deployment, app accounts, cloud storage migration, photo upload, tablet capture, or live Trimble sync.

---

## 1. What This Setup Is

The current remote setup is:

- Local app origin: `http://127.0.0.1:5001`
- Protected external URL: `https://gridflow.unitasconnect.com`
- Tunnel name: `gridflow`
- Access control: Cloudflare Access email one-time PIN
- Data at rest: local Mac filesystem under `uploads/`

The Mac must stay awake, connected to the internet, and running both the Flask app and the tunnel.

---

## 2. Start The Local App

From the repo root:

```bash
cd /Users/noelcollins/Unitas-GridFlow
source .venv312/bin/activate
python run.py
```

Expected local URL:

```text
http://127.0.0.1:5001
```

Quick local check:

```bash
curl -I http://127.0.0.1:5001/
```

Expected result:

```text
HTTP/1.1 200 OK
```

---

## 3. Start The Named Cloudflare Tunnel

In a second terminal:

```bash
cloudflared tunnel run gridflow
```

Expected protected URL:

```text
https://gridflow.unitasconnect.com
```

Quick tunnel check:

```bash
cloudflared tunnel info gridflow
```

Expected result:

- Tunnel name: `gridflow`
- At least one connector listed
- Edge locations listed

---

## 4. Access Test

Use a phone on mobile data or another trusted external device.

1. Open `https://gridflow.unitasconnect.com`.
2. Confirm Cloudflare Access appears before GridFlow.
3. Enter the approved email address.
4. Enter the one-time PIN.
5. Confirm GridFlow loads after authentication.

If the phone works but Mac Chrome shows `DNS_PROBE_FINISHED_NXDOMAIN`, this is usually local WiFi/router DNS caching. The local desktop app remains available at `http://127.0.0.1:5001`.

Mac DNS cache reset:

```bash
sudo dscacheutil -flushcache; sudo killall -HUP mDNSResponder
```

Then fully quit and reopen Chrome.

---

## 5. Stop The Trial

Stop the Flask app:

- Press `Ctrl+C` in the terminal running `python run.py`.

Stop the tunnel:

- Press `Ctrl+C` in the terminal running `cloudflared tunnel run gridflow`.

When the tunnel is stopped, `https://gridflow.unitasconnect.com` should no longer reach the local app.

---

## 6. Recovery Checklist

If remote access fails:

1. Confirm the local app works at `http://127.0.0.1:5001`.
2. Confirm the tunnel is running with `cloudflared tunnel info gridflow`.
3. Confirm the Mac is awake and connected to the internet.
4. Confirm Cloudflare Access still has the approved user email.
5. Try from phone mobile data to rule out WiFi DNS caching.
6. If Mac browser shows `NXDOMAIN`, flush Mac DNS cache and retry.

Do not bypass Cloudflare Access for real or sensitive survey data.

---

## 7. First Controlled Field-Trial Checklist

The next validation should test the workflow with a real surveyor/designer pattern, not new features.

### Pre-trial

Record:

- Job / file to use:
- Surveyor:
- Designer:
- Date/time:
- Device used for upload:
- Network used for upload:
- Approved Cloudflare Access email:

Prepare:

- Start local Flask app.
- Start named Cloudflare Tunnel.
- Confirm `https://gridflow.unitasconnect.com` prompts for Access login.
- Create or identify the project to upload into.
- Confirm the file is approved for this controlled trial.

### Surveyor upload steps

1. Open `https://gridflow.unitasconnect.com` from phone or external trusted device.
2. Authenticate through Cloudflare Access.
3. Open `/upload`.
4. Select or create the project.
5. Upload the CSV.
6. Enter survey day / visit label, uploaded-by, and surveyor note.
7. Confirm the project dashboard shows the uploaded file as processed.
8. Record any friction:
   - confusing screen
   - slow upload
   - login issue
   - unclear project selection
   - mobile layout problem

### Designer review steps

1. Open the project dashboard on desktop.
2. Review the map.
3. Review evidence gates and issue summary.
4. Open the Review page.
5. Check EXpole pairings.
6. Correct pairings if needed.
7. Add review notes.
8. Mark the file reviewed.
9. Download:
   - D2D Chain
   - D2D Working View
   - PDF
10. Compare the D2D output against the manual D2D process.

### Success criteria

The field trial is successful if:

- The surveyor can upload without a USB handoff.
- The designer can see the project immediately.
- The processed output is understandable without opening the raw CSV first.
- The review page is usable for intended pairing checks.
- The D2D exports are close enough to reduce or replace manual D2D spreadsheet preparation.
- Any gaps are specific enough to define the next narrow improvement.

### Post-trial notes

Record:

- What worked:
- What failed:
- What was confusing:
- What saved time:
- What still required manual D2D work:
- Whether reviewed exports were useful:
- Whether the next improvement should be:
  - operational/documentation only
  - Stage 3B follow-on
  - another Stage 3 field-trial pass
  - later hosted deployment planning
  - deferred later-stage work

---

## 8. Boundaries

Do not expand scope during the field trial.

Specifically do not build:

- app user accounts
- role-based permissions
- Render/Railway/full hosted deployment
- cloud storage migration
- automated backup system
- photo upload
- tablet capture forms
- live or semi-live Trimble sync
- Stage 4, Stage 5, or Stage 6 features

Field-trial findings should define the next task. They should not trigger feature work automatically.
