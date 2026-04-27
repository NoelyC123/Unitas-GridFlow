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

---

## 9. First Controlled Field-Trial Result — Gordon Real File

## Date

2026-04-27

## Trial Setup

- Protected URL: `https://gridflow.unitasconnect.com`
- Access method: Cloudflare Access email one-time PIN
- Upload device: iPhone on mobile data
- Local origin: Mac running Flask app on `http://127.0.0.1:5001`
- Tunnel: named Cloudflare Tunnel `gridflow`
- Survey file: `Gordon_Pt1_-_Original.csv`
- Project: `P007` / `Test with actual survey data`
- File ID: `F001`
- Uploaded by: `Noel`
- Survey note: `Testing real survey CSV file`

## Processing Result

- Status: `complete`
- Intake status: `reviewed`
- Review status: `reviewed`
- Rulepack: `SPEN_11kV`
- Records / poles: `157`
- Issues: `39`
- PASS / WARN / FAIL: `126 / 25 / 4`
- Sequenced proposed supports: `102`
- Matched EXpoles: `24`
- Unmatched EXpoles: `0`
- Sections: `2`

## Routes Validated

The following routes returned successfully for `P007/F001`:

- Project dashboard
- Map viewer
- PDF report
- D2D Chain export
- D2D Working View export
- Designer Review page

## Designer Review Result

- Gordon EXpole pairings were acceptable for this validation run without manual reassignment.
- Review was marked as reviewed.
- Pairing output should remain designer-reviewable and should not be treated as automatic final truth.

## Field-Trial Answers

### Did the remote phone upload feel usable?

Yes. The remote phone upload/access trial was successful and usable for a first controlled validation. The app could be reached on mobile data, authenticated through Cloudflare Access, used to upload into a project, and used to view dashboard, map, review, and D2D outputs.

### Did the project dashboard make sense after upload?

Yes. The dashboard showed the project code, file count, pole/record count, issue count, rulepack, uploaded file, intake status, survey note, uploaded-by label, and office feedback area. This validates the daily-intake concept.

The main dashboard friction is responsive layout. On phone, the survey files table is too wide and the right-hand status/action area can be partly off-screen.

### Were EXpole pairings acceptable without changes?

Yes for this Gordon validation. The review showed 24 matched EXpoles and 0 unmatched EXpoles. This is a strong validation signal, but the pairing output must remain designer-reviewable.

### Were D2D exports good enough to reduce manual D2D spreadsheet work?

Yes. The D2D Chain and D2D Working View are good enough to reduce manual D2D preparation by supporting route sequencing, EX/PR interpretation, section review, issue triage, reviewed/provisional status, and export preparation.

They remain reviewed/provisional handoff outputs, not a verified final PoleCAD import format.

### Biggest friction or missing piece

The biggest friction is mobile usability, not the core workflow.

Observed mobile friction:

- project dashboard table is cramped
- status/action columns are partly off-screen
- designer review pairing table is hard to inspect on phone
- long map sidebar/report sections require heavy scrolling
- homepage wording still reflects early "Pre-CAD QA Tool" / "DNO compliance" framing
- navigation still feels partly legacy: Upload / Jobs / Health rather than Projects / Intake / Review / Exports

## Recommended Next Improvement

Do not jump to hosted deployment or later-stage features.

The next narrow improvement should be responsive/mobile polish for the existing Stage 3 workflow:

- mobile-friendly project file cards instead of wide tables
- clearer action buttons for Map / Review / PDF / D2D exports
- compact mobile review/export summary
- updated homepage wording to reflect project intake and D2D handoff, not only early QA/compliance language

This should be treated as a Stage 3 usability follow-on only if approved as the next task.
