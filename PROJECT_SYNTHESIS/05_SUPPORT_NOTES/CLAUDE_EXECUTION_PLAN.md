# SpanCore — 8-Week Proof-of-Value Execution Plan

**Created:** 16 April 2026
**Purpose:** Turn the stop/go decision framework into a week-by-week action plan
**Rule:** Nothing outside this plan gets worked on until the core proof is done

---

## Week 1: Make It Run

### Objective
Get the existing codebase to a clean, working state where you can start the dev server, load the home page without errors, and confirm all existing routes respond.

### Technical milestones
- [ ] Fix `app/__init__.py` — correct `static_folder` and `template_folder` paths (change from relative `"app/static"` to absolute or to `"static"` since `__name__` already resolves to the `app/` package directory)
- [ ] Replace `app/templates/index.html` — remove all `url_for('main.*')` references, replace with a simple nav page linking to `/upload`, `/jobs/`, `/health/full`
- [ ] Add `GET /upload` route to `app/__init__.py` — renders `upload.html`
- [ ] Verify clean startup: `python run.py` starts without errors
- [ ] Verify all 7 existing routes respond (home, health, upload page, jobs page, jobs API, rulepacks API, map data API)

### Proof-of-value milestone
None yet — this week is housekeeping only.

### What to gather this week
- [ ] Confirm you have Python 3.11+ and can create a working venv with `requirements.txt`
- [ ] Confirm you can access the live repo at `/SpanCore-EW-Design-Tool-LOCAL/`
- [ ] Locate the quarantine file `_quarantine/20251029_163204/routes.py` — you will need it as a reference in Week 2

### Pass/fail test for this week
**Pass:** You can open `http://127.0.0.1:5000/` in a browser and see the home page, click through to the upload form, and hit `/health/full` and get `{"ok": true}`.
**Fail:** The app won't start, or the home page still crashes. If this takes more than one focused day, diagnose what's blocking you before continuing.

---

## Week 2: Build the Upload Pipeline

### Objective
Create the three missing backend endpoints so that the existing frontend JavaScript can complete a full upload cycle — presign, PUT file, finalize, poll status — using local file storage.

### Technical milestones
- [ ] Create `app/routes/api_upload.py` with three endpoints:
  - `POST /api/presign` — generates a job_short (8-char hex), creates `uploads/<job_short>/` directory, writes `status.json` = `{"status": "processing"}`, returns `{"upload_type": "single", "url": "/api/upload/put/<job_short>/<filename>", "headers": {}}`
  - `PUT /api/upload/put/<job_short>/<filename>` — saves `request.data` to `uploads/<job_short>/<secure_filename>`, returns `{"ok": true}`
  - `GET /api/jobs/<job_id>/status` — reads `uploads/<job_id>/status.json`, returns its contents
- [ ] Register `api_upload_bp` in `app/__init__.py`
- [ ] Update `app/routes/api_intake.py` (`POST /api/import/<job_short>`) to do real work:
  - Find the uploaded CSV in `uploads/<job_short>/`
  - Read it with `pandas.read_csv()`
  - Call `run_qa_checks(df, DNO_RULES)` from `qa_engine.py`
  - Save results as `uploads/<job_short>/results.json`
  - Update `status.json` to `{"status": "complete"}`
  - Return `{"ok": true, "job_id": "<job_short>"}`
  - Reference: `_quarantine/20251029_163204/routes.py` lines 25–38 for how CSV loading and QA calling was previously done
- [ ] Add `GET /map/view/<job_id>` to `app/routes/map_preview.py` — renders `map_viewer.html` with `job_id` passed to template
- [ ] Update `GET /map/data/<job_id>` in `map_preview.py` to read `uploads/<job_id>/results.json` and return real issue data as GeoJSON (use placeholder `Point([0,0])` geometry for CSV-only jobs — real geometry comes later with GIS support)

### Proof-of-value milestone
- [ ] End-to-end smoke test via curl (commands provided in the recovery plan, section 1.5)
- [ ] End-to-end browser test: open `/upload`, select any DNO, upload `sample_data/mock_survey.csv`, wait for redirect, see results on map view page

### What to gather this week
Nothing external — this week uses only existing project files and mock data.

### Pass/fail test for this week
**Pass:** You can upload `mock_survey.csv` through the browser upload form and be redirected to a map view page showing QA results (even if the map itself shows placeholder geometry).
**Fail:** The upload flow breaks at any step. If the pipeline is not working end-to-end by end of Week 2, stop and assess whether the technical execution approach is working. Consider whether you need a different developer, a different tool (e.g. Claude Code for the implementation), or a different time commitment.

---

## Week 3: Get Real Data

### Objective
Obtain one real survey data file from an actual overhead line job and test the pipeline against it. Discover what breaks.

### Technical milestones
- [ ] Load the real survey CSV into the tool
- [ ] Document every failure: wrong column names, unexpected data types, missing fields, encoding issues, coordinate format problems
- [ ] Adapt the CSV ingestion to handle the real file's actual structure (column mapping, type coercion, error handling for malformed rows)
- [ ] Add basic error handling to the finalize endpoint — if the CSV can't be parsed, write `{"status": "error", "error": "..."}` to status.json (the frontend already handles error states)

### Proof-of-value milestone
- [ ] The real survey file uploads, parses, and produces a QA result — even if the QA checks are still generic placeholders and most fields don't match

### What to gather this week
This is the critical external dependency:

- [ ] **One real survey CSV file.** This is the single most important thing you need from outside the codebase. Options for obtaining it:
  - A file from your own past work (if you have overhead line design experience)
  - An anonymised file from a colleague or contact in the industry
  - A sample export from Trimble or similar survey equipment documentation
  - A synthetic file you construct based on real column schemas from DNO submission templates
  - As a last resort: a detailed description of what real survey CSVs look like (column names, data types, typical values) from someone who works with them — then build a realistic synthetic file
- [ ] **The column schema.** At minimum, you need to know: what columns appear in a real SPEN overhead line survey CSV, what data types each contains, what units are used, and what a "good" row looks like versus a "bad" one

### Pass/fail test for this week
**Pass:** A real (or realistic) survey file uploads and produces output, even if the QA checks are not yet meaningful.
**Fail:** You cannot obtain any real survey data or realistic schema information. If this happens, you have a domain access problem. Pause and assess: do you have (or can you build) the domain connections needed to make this product real? Without real data, everything that follows is hypothetical.

---

## Week 4–5: Build a Real SPEN Rulepack

### Objective
Replace the 4 generic placeholder rules with a real, substantive SPEN 11kV overhead line rulepack containing at least 15–20 rules drawn from actual published standards.

### Technical milestones
- [ ] Create `app/rulepack_store.py` with a structured `RULEPACKS` dictionary (as described in recovery plan Phase 5)
- [ ] Build the SPEN 11kV rulepack with rules in these categories:
  - **Required fields** (5+ rules): pole_id, easting, northing, pole_height, material, line_voltage, span_length, ground_clearance — whatever fields the real survey CSV contains that must be present
  - **Range checks** (5+ rules): pole height within allowable range for voltage/material, span length within limits, ground clearance above minimum, conductor sag within tolerance
  - **Allowed value checks** (3+ rules): material must be one of [Wood, Steel, Concrete, ...], voltage must be one of [LV, 11kV, 33kV, ...], pole class within valid set
  - **Uniqueness checks** (1+ rules): pole_id must be unique
  - **Cross-field checks** (if the QA engine supports them — if not, extend it): e.g., minimum ground clearance depends on voltage level
- [ ] Update `api_rulepacks.py` to return real data from `RULEPACKS`
- [ ] Update `api_intake.py` to look up the correct rulepack based on the DNO/voltage selection from the frontend
- [ ] Run the real survey file against the real rulepack

### Proof-of-value milestone
- [ ] The tool produces a meaningful QA result from a real file with real rules — issues that correspond to actual compliance requirements, not placeholder checks
- [ ] At least some of the issues found are ones that a designer would recognise as genuine problems or checks they currently perform manually

### What to gather during these weeks
- [ ] **SPEN overhead line design standards.** Look for:
  - ENA Technical Specification 43-8 (overhead line clearances) — this is the primary clearance standard across all DNOs
  - ENA EREC G81 (design and planning of overhead lines on wood poles) — the ICP/IDP design approval standard
  - ESQCR 2002 (Electricity Safety, Quality and Continuity Regulations) — the legal safety baseline
  - SPEN-specific policy documents (their variants on the above, any SPEN-specific pole schedules, material specifications, or design guidelines)
  - ENWL's EPD473 (their overhead line standards policy) is publicly available and can serve as a reference for the kind of rules that apply, even if the specific values differ from SPEN
- [ ] **Conversations with a domain expert.** If you are not yourself an OHL designer, you need access to someone who is — even informally. The question to ask them: "When you get a survey CSV for a SPEN 11kV job, what are the first 15 things you check before you open PLS-CADD?" Their answer is your rulepack.

### Pass/fail test for these weeks
**Pass:** The tool runs a real file against 15+ real rules and produces output that you believe (based on your own knowledge or expert input) corresponds to genuine compliance checks.
**Fail — domain access problem:** You cannot find or interpret the relevant standards. The rules you build are guesses rather than grounded in published specifications. If this happens, you need a domain partner before proceeding — someone with OHL design experience who can define what the rules should be.
**Fail — trivial rules:** The real rulepack turns out to contain fewer than 10 rules, all of which are obvious and simple enough that any designer would spot them in seconds. If the automated checks don't add value beyond what a quick manual scan provides, the product concept is weaker than assumed.

---

## Week 6: Show It to a Real User

### Objective
Demonstrate the working tool — real data, real rules, real output — to one person who designs overhead lines, and get their honest reaction.

### Technical milestones
None new. The tool should be stable enough to demo without crashes. Fix any remaining rough edges from Weeks 4–5.

### User-validation milestone
- [ ] Identify one real overhead line designer to show the tool to. This person should be:
  - Someone who actually works with survey data and PLS-CADD (not a manager who used to, not a general engineer)
  - Someone who will give you an honest reaction (not a friend who will be polite)
  - Ideally someone at an IDP, ICP, or framework contractor (these are the first-tier buyers)
- [ ] Show them: upload a file, select SPEN 11kV, see the QA results
- [ ] Ask exactly two questions:
  1. "Would this have caught errors you've seen on real jobs?"
  2. "Would you use this at the start of a job if it were available?"
- [ ] Record their exact answers, including any caveats, objections, or feature requests

### What to gather this week
- [ ] **One honest user reaction.** This is the entire point of the 8-week plan. Everything else was preparation for this moment.
- [ ] **Their specific feedback** on: which rules were useful, which were wrong or irrelevant, what rules were missing, what file formats they actually use, what would need to change for them to actually use it

### Pass/fail test for this week
**Strong pass:** They say something equivalent to "yes, this catches real problems" and ask when they can use it, or ask for specific additions (more rules, different DNO, GIS support). Unprompted enthusiasm is the strongest signal.
**Moderate pass:** They say "this is interesting, it catches some things, but it would need X and Y to be useful." This means the concept holds but the implementation needs work. Continue with adjustments.
**Fail:** They say "I already do this faster in Excel" or "these checks aren't the ones that matter" or they are visibly uninterested. If this happens, probe deeper — is the problem the rules (fixable), the UX (fixable), or the fundamental concept (not fixable)?

---

## Week 7–8: Decide and Act

### Objective
Based on the Week 6 reaction, make the go/no-go decision and either commit to the next phase or pause.

### If GO (positive user validation):
- [ ] Immediately fix or add whatever the user said was missing — their feedback is your product roadmap
- [ ] Begin building a second rulepack (likely SSEN or ENWL, based on where your contacts are)
- [ ] Add GIS shapefile support (recovery plan Phase 2) — this is the highest-value technical addition after the core path
- [ ] Show the updated tool to a second user at a different organisation
- [ ] Begin thinking about packaging: hosted demo, pricing page, simple landing site

### If PAUSE (ambiguous or negative validation):
- [ ] Write down exactly what went wrong — was it the rules, the data handling, the UX, or the concept?
- [ ] If rules: find a domain partner who can define them properly, then try again
- [ ] If data handling: the tool doesn't handle real file formats well enough — this is a solvable engineering problem, retry with better parsing
- [ ] If concept: the pain point is not severe enough to change behaviour — park the project and revisit if circumstances change (e.g., a DNO starts mandating pre-submission validation)

---

## What to Gather — Complete Checklist

| Item | When needed | Priority | How to get it |
|---|---|---|---|
| Working Python 3.11+ environment with venv | Week 1 | Critical | Local setup |
| Access to live repo | Week 1 | Critical | Already exists at `/SpanCore-EW-Design-Tool-LOCAL/` |
| One real survey CSV (or realistic synthetic) | Week 3 | Critical | Your own files, a colleague, a DNO submission template, or Trimble sample exports |
| Real survey CSV column schema | Week 3 | Critical | From the file itself, or from a designer who uses them |
| ENA TS 43-8 (clearance specifications) | Week 4 | High | ENA Engineering publications, your employer's library, or an IDP contact |
| ESQCR 2002 clearance tables | Week 4 | High | UK legislation (publicly available) |
| ENA EREC G81 (OHL on wood poles) | Week 4 | High | ENA publications |
| SPEN-specific design standards/policies | Week 4 | High | SPEN's ICP/IDP portal, or a SPEN-framework contractor |
| One honest OHL designer to demo to | Week 6 | Critical | Your professional network |
| Their unfiltered feedback | Week 6 | Critical | Ask the two questions, record the answers |

---

## What to Ignore Completely Until Core Proof Is Done

Do not work on any of the following before Week 6 user validation is complete:

- S3/MinIO integration
- PDF report generation
- DXF export
- Job tracking or state machine
- Database persistence (postgres)
- User authentication or multi-tenancy
- Multiple DNO rulepacks (beyond the first SPEN one)
- CI/CD or deployment automation
- Landing pages, pricing, or marketing
- Naming, branding, or logo
- Additional frontend features or redesign
- Performance optimisation
- Any form of investor or partner conversation

These are all legitimate future work. None of them matter until one real user has confirmed that the core concept is useful.

---

## The Exact "Go" Deliverable

By end of Week 8, you have:

1. A working web app that accepts a survey CSV upload
2. A real SPEN 11kV rulepack with 15+ rules from published standards
3. QA results displayed in the browser showing real issues from real data
4. Written confirmation from at least one practising OHL designer that the tool catches genuine problems and would be useful in their work

If all four exist, the project is a go. Proceed to second rulepack, GIS support, and first commercial conversations.

---

## The Exact "Pause/Stop" Outcomes

**Hard stop — reconsider the project entirely:**
- Week 6 user says the concept is wrong (the checks don't match what matters in practice, or the pain isn't severe enough to justify a new tool)
- You discover the pre-CAD validation gap doesn't actually exist the way you assumed (designers already have adequate tools or processes)

**Pause — fix the identified blocker, then retry:**
- You can't get the pipeline running by end of Week 2 (execution/technical problem)
- You can't obtain real survey data by end of Week 3 (domain access problem)
- You can't build a substantive rulepack by end of Week 5 (domain knowledge problem)
- You can't find anyone to show it to by Week 6 (network/credibility problem)
- User says "interesting but not useful yet" with specific fixable objections (product iteration needed)

**Each pause trigger has a different remedy.** Don't treat them all the same. A technical execution problem (Week 2) is very different from a domain access problem (Week 3) or a product-market fit problem (Week 6). Diagnose which one you hit before deciding what to do about it.