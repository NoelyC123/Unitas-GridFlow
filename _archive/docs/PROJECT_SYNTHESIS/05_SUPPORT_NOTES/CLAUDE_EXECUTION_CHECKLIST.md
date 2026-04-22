# SpanCore — Execution Checklist

---

## WEEK 1: Make It Run

### Before you start
- [ ] Python 3.11+ installed
- [ ] Access to repo at `/SpanCore-EW-Design-Tool-LOCAL/`
- [ ] Can create venv and install `requirements.txt`

### Tasks
- [ ] Create venv: `python3 -m venv .venv312 && pip install -r requirements.txt`
- [ ] Fix `app/__init__.py` line 6: change `static_folder="app/static"` to `static_folder="static"` and `template_folder="app/templates"` to `template_folder="templates"` (Flask resolves these relative to the package directory, which is already `app/`)
- [ ] Replace `app/templates/index.html` entirely — remove all `url_for('main.*')` references, replace with simple Bootstrap nav linking to `/upload`, `/jobs/`, `/health/full`
- [ ] Add route to `app/__init__.py`: `@app.route("/upload") def upload(): return render_template("upload.html")`
- [ ] Run `python run.py`
- [ ] Test every route in browser:
  - `GET /` → home page loads without error
  - `GET /health/full` → returns `{"ok": true}`
  - `GET /upload` → upload form renders
  - `GET /jobs/` → jobs table renders
  - `GET /api/jobs/` → returns `{"jobs": []}`
  - `GET /api/rulepacks/SPEN_11kV` → returns template JSON
  - `GET /map/data/test123` → returns empty GeoJSON

### Deliverable
App starts cleanly, all 7 routes respond, no errors in terminal.

### Pass/fail
**Pass:** Every route above returns a response without a 500 error or traceback.
**Fail:** App won't start, or any route crashes. Fix before moving to Week 2.

### Do not touch
- api_intake.py logic
- Upload pipeline
- Any new endpoints
- Frontend JS files
- Docker/nginx
- S3/MinIO
- Database

---

## WEEK 2: Build the Upload Pipeline

### Before you start
- [ ] Week 1 complete — app runs, all routes respond
- [ ] `_quarantine/20251029_163204/routes.py` located — read lines 25–38 for CSV/QA reference

### Tasks

**Create `app/routes/api_upload.py`:**
- [ ] `POST /api/presign`
  - Generate `job_short = uuid4().hex[:8]`
  - Create directory `uploads/<job_short>/`
  - Write `uploads/<job_short>/status.json` → `{"status": "processing"}`
  - Return `{"upload_type": "single", "url": "/api/upload/put/<job_short>/<filename>", "headers": {}}`
  - Extract filename from request JSON `key` field
- [ ] `PUT /api/upload/put/<job_short>/<filename>`
  - Save `request.data` to `uploads/<job_short>/<secure_filename(filename)>`
  - Return `{"ok": true}`
- [ ] `GET /api/jobs/<job_id>/status`
  - Read `uploads/<job_id>/status.json`
  - Return its contents
  - If file not found, return `{"status": "processing"}`

**Register in `app/__init__.py`:**
- [ ] `from app.routes.api_upload import api_upload_bp`
- [ ] `app.register_blueprint(api_upload_bp, url_prefix="/api")`

**Update `app/routes/api_intake.py` — make `POST /api/import/<job_short>` do real work:**
- [ ] Find uploaded file: `glob.glob(f"uploads/{job_short}/*")` (exclude status.json)
- [ ] Read CSV: `pd.read_csv(filepath)`
- [ ] Import and call: `from app.qa_engine import run_qa_checks` and `from app.dno_rules import DNO_RULES`
- [ ] Run: `issues = run_qa_checks(df, DNO_RULES)`
- [ ] Save: `issues.to_json(f"uploads/{job_short}/results.json", orient="records")`
- [ ] Update: write `{"status": "complete"}` to `status.json`
- [ ] Return: `{"ok": true, "job_id": job_short}`
- [ ] Wrap in try/except — on failure write `{"status": "error", "error": str(e)}` to `status.json`

**Add map view route to `app/routes/map_preview.py`:**
- [ ] `@map_preview_bp.get("/view/<job_id>")`
- [ ] `return render_template("map_viewer.html", job_id=job_id)`

**Update `GET /map/data/<job_id>` in `map_preview.py`:**
- [ ] Read `uploads/<job_id>/results.json`
- [ ] Convert each issue to a GeoJSON Feature with `Point([0, 0])` geometry
- [ ] Return FeatureCollection with metadata: `pole_count`, `issue_count`, etc.

**Test — command line:**
- [ ] `curl -X POST http://127.0.0.1:5000/api/presign -H 'Content-Type: application/json' -d '{"key":"mock.csv","size":100,"content_type":"text/csv","multipart":false}'`
- [ ] `curl -X PUT http://127.0.0.1:5000/api/upload/put/<job_short>/mock.csv --data-binary @sample_data/mock_survey.csv`
- [ ] `curl -X POST http://127.0.0.1:5000/api/import/<job_short>`
- [ ] `curl http://127.0.0.1:5000/api/jobs/<job_short>/status` → `{"status": "complete"}`
- [ ] `curl http://127.0.0.1:5000/map/data/<job_short>` → GeoJSON with real issue data
- [ ] `open http://127.0.0.1:5000/map/view/<job_short>` → page loads

**Test — browser:**
- [ ] Open `/upload`
- [ ] Select any DNO
- [ ] Upload `sample_data/mock_survey.csv`
- [ ] Observe: presign succeeds, file uploads, finalize completes, status polls to complete, browser redirects to map view
- [ ] Map view page renders with QA results displayed

### Deliverable
Full end-to-end upload pipeline working with mock data. Browser upload → QA results on screen.

### Pass/fail
**Pass:** Browser upload of `mock_survey.csv` completes without manual intervention and results appear on map view page.
**Fail:** Pipeline breaks at any step. Debug and fix. If not working by end of Week 2, stop and reassess approach (consider using Claude Code for implementation, or getting a second developer).

### Do not touch
- GIS/shapefile support
- Real rulepack data
- PDF export
- Job persistence/listing
- S3/MinIO
- Docker
- Frontend redesign
- Any feature not in the upload→QA→result path

---

## WEEK 3: Get Real Data

### Before you start
- [ ] Week 2 complete — end-to-end pipeline works with mock data
- [ ] You have identified a source for real survey data (your own files, a colleague, a DNO template, Trimble sample docs)

### Tasks

**Obtain the file:**
- [ ] Get one real overhead line survey CSV (or the closest realistic substitute you can find)
- [ ] If you can't get an actual file, construct a synthetic one based on real column schemas — but document that it's synthetic and note that Week 6 validation will require a real file

**Test the file against the tool:**
- [ ] Upload the real file through the browser
- [ ] Record every failure in a simple list:
  - Column names the tool doesn't recognise
  - Data types that break the parser (dates, mixed types, encoding)
  - Missing fields the QA rules expect
  - Extra fields the tool ignores
  - Row formatting issues (blank rows, headers in wrong position, merged cells)

**Fix the ingestion:**
- [ ] Add column mapping if real column names differ from what QA rules expect
- [ ] Add type coercion (strings to numbers, date parsing, whitespace stripping)
- [ ] Add error handling for malformed rows (skip and log, don't crash)
- [ ] Add encoding detection if the file isn't UTF-8
- [ ] Re-test: real file uploads and produces a QA result (even if the checks are still the 4 generic placeholders)

**Document what you've learned:**
- [ ] Write a short note (10 lines max) listing: actual column names in real survey files, data types, common issues found, and what a real rulepack would need to check

### Deliverable
Real survey file uploads and produces QA output. You have a documented list of what real survey data actually looks like.

### Pass/fail
**Pass:** Real file uploads, parses, and produces results without crashing. You now know what real data looks like.
**Fail — can't get data:** You cannot obtain any real survey data or schema. This is a domain access problem. Pause and find a domain contact before continuing.
**Fail — data is fundamentally incompatible:** Real survey data is structured so differently from the tool's expectations that adapting would require a major rewrite (not column mapping, but a completely different data model). Reassess whether the tool's input assumptions are correct.

### Do not touch
- Building real rulepacks yet (that's Week 4)
- GIS support
- Anything cosmetic
- Any second file format

---

## WEEK 4–5: Build a Real SPEN Rulepack

### Before you start
- [ ] Week 3 complete — real data uploads and parses
- [ ] You have the documented column schema from Week 3
- [ ] You have obtained at least one of:
  - ENA TS 43-8 (clearance specifications)
  - ESQCR 2002 clearance tables
  - ENA EREC G81
  - SPEN-specific overhead line policy documents
  - Alternatively: detailed input from an experienced OHL designer on "what do you check before opening PLS-CADD?"

### Tasks

**Create `app/rulepack_store.py`:**
- [ ] Define `RULEPACKS` dictionary keyed by DNO/voltage string (e.g., `"SPEN_11kV"`)
- [ ] Each rulepack contains a list of rule dicts compatible with `qa_engine.py`

**Build the SPEN 11kV rulepack — minimum 15 rules across these categories:**

Required field checks (target: 5+):
- [ ] pole_id present and non-empty
- [ ] easting present and numeric
- [ ] northing present and numeric
- [ ] pole_height present and numeric
- [ ] material present and non-empty
- [ ] (add others based on real column schema from Week 3)

Range checks (target: 5+):
- [ ] pole_height within allowable range for 11kV wood pole (typically 8m–14m, confirm from standards)
- [ ] span_length within limits (typically <80m for 11kV, confirm)
- [ ] ground_clearance above minimum (5.2m for 11kV per ESQCR, confirm)
- [ ] easting/northing within plausible UK coordinate range (if using BNG: easting 0–700000, northing 0–1300000)
- [ ] (add others from standards)

Allowed value checks (target: 3+):
- [ ] material in [Wood, Steel, Concrete, ...] (confirm allowed set from DNO)
- [ ] pole_class in valid set (e.g., Light, Medium, Heavy, Stout — confirm)
- [ ] conductor_type in allowed set (confirm from SPEN specifications)

Uniqueness checks (target: 1+):
- [ ] pole_id is unique across all rows

**Extend `qa_engine.py` if needed:**
- [ ] Add `allowed_values` check type if not already supported (check field value against a list)
- [ ] Add `min_value` / `max_value` individual checks if the existing `range` type doesn't cover them adequately
- [ ] Keep extensions minimal — only what the rules above require

**Wire the rulepack into the pipeline:**
- [ ] Update `api_intake.py` to read the DNO selection from the frontend request
- [ ] Look up `RULEPACKS[dno]` and pass those rules to `run_qa_checks` instead of the generic `DNO_RULES`
- [ ] Fall back to `DNO_RULES` if the selected DNO doesn't have a rulepack yet

**Update `api_rulepacks.py`:**
- [ ] Return real rulepack metadata from `RULEPACKS` instead of template JSON

**Test:**
- [ ] Upload the real survey file with SPEN 11kV selected
- [ ] Review every issue found — is it a genuine compliance problem or a false positive?
- [ ] Adjust thresholds and rules until the output is credible
- [ ] Count: how many of the issues would a designer recognise as real problems?

### Deliverable
A working SPEN 11kV rulepack with 15+ real rules. The tool produces meaningful QA output from real data — issues that correspond to actual compliance requirements.

### Pass/fail
**Pass:** The tool finds issues in real data that are genuine compliance or data quality problems. At least some of them are things that would matter in practice.
**Fail — can't access standards:** You cannot find or interpret the DNO specifications needed to define real rules. You need a domain partner. Pause and find one.
**Fail — rules are trivial:** Fewer than 10 meaningful rules exist, all obvious. The tool doesn't add value over a quick manual scan. Reassess whether the product concept is strong enough.
**Fail — too many false positives:** The rules flag everything and the output is noise. Adjust thresholds — but if the underlying data model doesn't support accurate checking, reassess the input assumptions.

### Do not touch
- Second DNO rulepack
- GIS support
- PDF export
- Job persistence
- UI redesign
- Any feature outside the core upload→check→result path

---

## WEEK 6: Show It to a Real User

### Before you start
- [ ] Weeks 4–5 complete — real data, real rules, meaningful output
- [ ] You have identified one OHL designer to demo to
- [ ] The tool runs without crashes on the real dataset
- [ ] You can complete a full demo in under 5 minutes

### Tasks

**Prepare:**
- [ ] Run through the full demo yourself twice — upload, wait, view results
- [ ] Fix any remaining crashes or confusing UI behaviour
- [ ] Prepare a brief verbal intro: "This checks your survey data against SPEN rules before you open PLS-CADD. Upload a CSV, pick the DNO, see what's wrong."
- [ ] Have the real survey file ready to upload during the demo

**Demo:**
- [ ] Show the tool to the designer — let them watch you upload the file and see the results
- [ ] If possible, let them upload a file of their own
- [ ] Ask question 1: "Would this have caught errors you've seen on real jobs?"
- [ ] Ask question 2: "Would you use this at the start of a job if it were available?"
- [ ] Shut up and listen. Do not sell or explain further. Let them react.

**Record:**
- [ ] Write down their exact words (not your interpretation)
- [ ] Note which issues they recognised as real problems
- [ ] Note which issues they dismissed as irrelevant or wrong
- [ ] Note any rules or checks they said were missing
- [ ] Note any objections or concerns about adopting it
- [ ] Note their overall energy level: excited, interested, polite, indifferent, sceptical

### Deliverable
Written record of one real designer's honest reaction to the working tool with real data.

### Pass/fail
**Strong pass:** They confirm it catches real problems. They ask when they can use it, or what it would cost to get it. They suggest specific additions. They offer to test it on another job.
**Moderate pass:** They say it's interesting and catches some things, but list specific gaps or problems. The gaps are fixable (missing rules, wrong thresholds, needs GIS). Continue with adjustments.
**Fail:** They say it doesn't catch the things that matter, or that they already handle this adequately. Probe: is it the rules (fixable) or the concept (not fixable)?
**Fail — no demo happened:** You couldn't find or schedule a designer. This is a network/access problem. You need industry connections to build this product. Pause and build them.

### Do not touch
- Writing code during this week (unless fixing a crash for the demo)
- Adding features they haven't asked for
- Building anything new before processing their feedback

---

## WEEK 7–8: Decide and Act

### Before you start
- [ ] Week 6 complete — you have a written record of the user's reaction
- [ ] You have an honest self-assessment of whether the reaction was a pass or fail

### If STRONG PASS — commit and accelerate:
- [ ] Fix or add the top 3 things the user said were missing
- [ ] Begin building second rulepack (choose DNO based on user feedback or your next contact)
- [ ] Add GIS shapefile upload support (recovery plan Phase 2 — use `zipfile.ZipFile`, read with geopandas, convert to GeoJSON)
- [ ] Add file-based job persistence (recovery plan Phase 3 — `meta.json` per job, real jobs listing)
- [ ] Identify a second designer at a different organisation to show the updated version to
- [ ] Begin thinking about: hosted demo, simple pricing, landing page

### If MODERATE PASS — iterate and retest:
- [ ] List every specific objection or gap from the user feedback
- [ ] Fix the top 3 gaps (likely: missing rules, wrong thresholds, missing file format support)
- [ ] Re-test with the same user or a new one
- [ ] Set a second deadline: re-demo within 3 weeks. If the second demo is also a moderate pass or worse, seriously consider whether the product will ever cross the line from "interesting" to "useful."

### If FAIL — diagnose honestly:
- [ ] Was the problem the rules? → Find a domain partner, rebuild the rulepack, retry
- [ ] Was the problem the data handling? → The tool doesn't handle real formats well enough → engineering fix, retry
- [ ] Was the problem the concept? → Designers don't need this, or already have adequate processes → park the project
- [ ] Was the problem that no demo happened? → You lack the industry access to build this product → either build those connections or park it

### Deliverable
A written decision: GO (with specific next actions), ITERATE (with specific fixes and a re-test date), or PAUSE (with honest diagnosis of why).

### Pass/fail
**Pass for the entire 8-week plan:** You have a working tool, real rules, real data, and at least one confirmed "yes this is useful" from a real designer. The project has earned the right to continue.
**Fail for the entire 8-week plan:** You do not have all four of those things. Identify which one is missing and decide whether the gap is closeable.
