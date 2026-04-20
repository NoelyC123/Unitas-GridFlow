# SpanCore / EW Design Tool — Full Strategic Analysis

**Date:** 16 April 2026
**Analyst:** Claude (Opus 4.6)
**Source base:** Full project handover pack uploaded to Claude Project — forensic audit files, master project report, long-form project-history document, handover notes, file structure/code dump/context exports, live route map snapshot, live code reference files, and current established understanding of the live repository. Market analysis conducted via web research on 16 April 2026.

**Convention used throughout:** Where a claim is drawn from a specific file, I cite it. Where I am interpreting or giving opinion, I say so explicitly.

---

## 1. Executive Judgment

This project is worth continuing. That is not encouragement for the sake of it — it is a conclusion drawn from three independent lines of evidence.

First, the problem is real. UK overhead line design currently relies on manual, spreadsheet-based QA between field survey and CAD. No dedicated pre-CAD validation tool exists. Every DNO, framework contractor, and independent design provider doing overhead line work is exposed to the same workflow friction: bad data entering PLS-CADD, late-stage rework, and DNO rejection cycles. This is confirmed by industry research, not just by the project's own documents.

Second, the product concept is well-aimed. The project has correctly identified the highest-leverage intervention point in the entire survey-to-design chain: the gap between raw survey data and design-tool input. This is the point where errors enter and multiply. A tool that validates data at this stage would prevent rework downstream, not just catch it.

Third, the codebase — while unfinished — is structurally sound and recoverable. The forensic audit confirms that the architecture is correct, the QA engine works, the frontend is substantially complete, and the gaps are specific, well-defined, and completable. This is not a project that needs to be thrown away and restarted.

However, the project also has real weaknesses. It has been in development since at least October 2025 and has never run end-to-end. The scope has at times drifted toward over-ambition. The codebase was left in a mid-refactor state with critical endpoints missing. And turning a working prototype into a commercially viable product requires more than just finishing the code — it requires domain-specific rule data, real-world testing with actual survey files, and a credible route to market.

**My overall judgment:** Continue, but narrowed, disciplined, and with a clear milestone — one working end-to-end path (upload CSV → QA check → results on map) within the next two weeks — before making any further investment decisions.

---

## 2. What This Project Really Is

### Confirmed (from WHAT_THIS_PROJECT_IS.md, MASTER_PROJECT_OVERVIEW.md)

SpanCore / EW Design Tool is a pre-CAD QA, compliance, and workflow automation layer for electricity network survey-to-design handoffs. It is a Flask/Python web application that sits between raw field survey data (CSV, shapefile) and final CAD/design output (PLS-CADD, DXF).

It is not a CAD tool. It is not a full design platform. It is not a replacement for engineering judgement. Its purpose is to validate, check, and standardise data before it enters the design environment.

The narrowest practical scope, stated in the project files, is: **SPEN-first, pre-CAD validation and workflow improvement for electricity network survey/design work.**

### Interpretation (my reading of the full project history)

At its core, this is a **quality gate**. The product's fundamental value proposition is: "If your survey data goes through this tool before it goes into PLS-CADD, you will catch errors earlier, reduce rework, and get cleaner designs submitted to the DNO first time."

This is a narrow, clear, and defensible product identity. The project documents sometimes drift toward a broader vision — full workflow platform, job tracking, CAD export, reporting hub — but the strongest version of this product is the narrow one: a focused pre-CAD validation engine.

### The workflow it sits inside

The overhead line design workflow in UK electricity distribution follows this chain:

1. **Field survey** — surveyors capture pole positions, ground profiles, conductor sag, obstacles using GPS/GNSS, total stations, or LiDAR
2. **Data processing** — raw data is cleaned, formatted, converted to design-tool-compatible formats (CSV, shapefile, DXF)
3. **Pre-CAD validation** ← **THIS IS WHERE SPANCORE SITS**
4. **CAD design** — data enters PLS-CADD (the dominant tool), designers build terrain models, check clearances, run structural calculations
5. **QA review** — senior engineer checks design against DNO-specific standards
6. **Submission** — design pack submitted to DNO for approval
7. **Approval/rejection cycle** — if rejected, loop back to steps 3–6

The critical insight — confirmed by both the project documents and the market research — is that **steps 2–3 are currently done manually using spreadsheets and institutional knowledge**. There is no dedicated tool. PLS-CADD's built-in validation operates during and after design (step 4 onwards), not upstream. Errors that enter at step 2 propagate through the entire chain.

---

## 3. What Has Actually Been Built So Far

This section draws entirely from the forensic audit (CLAUDE_FORENSIC_AUDIT.md), which was produced by direct Claude Code inspection of the live repository, and from the selected live code files uploaded to this project.

### Genuinely built and working

**Application infrastructure:**
- `run.py` (7 lines) — real entry point, calls `create_app()`, runs dev server on port 5000
- `app/__init__.py` (54 lines) — Flask app factory, registers 5 blueprints with try/except, defines health check and home routes
- Docker stack — docker-compose.yml with 4 services (minio, postgres, app, nginx), nginx reverse proxy with basic auth, Makefile with build/test targets
- `requirements.txt` — 19 packages, clean and correct (Flask 3.1.1, geopandas 1.1.1, pandas 2.3.1, shapely 2.1.1)
- `pyproject.toml` — Poetry project config, Python ^3.11

**QA engine — fully implemented:**
- `app/qa_engine.py` (36 lines) — `run_qa_checks(df, rules)` function, supports `unique`, `range`, `required` check types, returns DataFrame of issues. This is real, working, testable code.

**DNO rules — minimal but correct:**
- `app/dno_rules.py` (6 lines) — 4 generic rules (pole_id unique, height range, material required, location required). Placeholder data, not real DNO specifications.

**Frontend — two complete, well-built templates:**
- `upload.html` — Bootstrap 5, DNO/voltage selector, rulepack modal, upload button, result display
- `map_viewer.html` — Leaflet map, summary cards, QA status display, PDF download button

**Frontend JavaScript — three complete, correct modules:**
- `upload-manager.js` — full presign → PUT → finalize → poll workflow
- `map-viewer.js` — GeoJSON rendering with colour-coded QA status markers
- `rulepack-selector.js` — dynamic rulepack loading on DNO change
- `toast.js` — notification display

**Sample data:**
- `sample_data/mock_survey.csv` (5 rows), `sample_data/mock_shapefile.zip` (5 points)

### Partially built (structurally present, no real logic)

Five blueprint endpoints are registered and responding but return only hardcoded stub data:

| File | Endpoint | Returns |
|---|---|---|
| `api_intake.py` | `POST /api/import/<job_short>` | Static JSON, no file processing |
| `api_jobs.py` | `GET /api/jobs/` | `{"jobs": []}` always |
| `api_rulepacks.py` | `GET /api/rulepacks/<id>` | Template JSON, empty thresholds |
| `map_preview.py` | `GET /map/data/<job_id>` | Empty GeoJSON, zeroed metadata |
| `jobs_page.py` | `GET /jobs/` | Inline HTML, one hardcoded row |

The upload workflow is complete on the frontend but blocked on the backend. Three of the four upload steps have no backend endpoint at all.

### Not built — only planned or discussed

The following are described in the context documents but confirmed absent from code by the forensic audit:

- Real DNO-specific rulepack data (only 4 generic placeholders exist)
- Database persistence (postgres runs in Docker but nothing connects to it)
- S3/MinIO file storage (MinIO in docker-compose, no application code uses it)
- Trimble CSV normalisation
- Real DXF export
- PDF QA report generation
- Job tracking / state machine
- Any real file processing behind the finalize endpoint
- User authentication beyond nginx basic auth
- Any working end-to-end path from upload to result

### Current actual state

The project is frozen at commit `6c27a31` ("Pre-audit snapshot 20251029_170500", 29 October 2025). It has been untouched for approximately 6 months.

The live route map snapshot confirms exactly 7 registered routes. The `static_folder` path resolves incorrectly to a non-existent directory. The home page crashes on every request due to broken template references.

**In plain terms:** This is a well-structured skeleton with a working QA engine and a polished frontend, but no working data pipeline connecting them. You cannot currently upload a file and get a result.

---

## 4. Technical Assessment

### Architecture — good decisions, incomplete execution

**Confirmed fact:** The project uses a Flask app factory pattern with blueprint-based route separation. This is the correct architectural choice for a modular web application of this scope. The decision to refactor from a monolithic `routes.py` to separate blueprints was the right call.

**My assessment:** The architecture is clean and appropriate. Flask is a reasonable choice for a tool of this size — it's lightweight, well-documented, and the team (or individual) clearly knows how to use it. The blueprint pattern allows each feature area (upload, jobs, map, rulepacks) to grow independently. The Docker stack with nginx and MinIO shows realistic deployment thinking.

The refactor was left unfinished, which is the single biggest technical problem. But the *direction* of the refactor was correct. The old monolithic `routes.py` had a shell injection vulnerability (`os.system("unzip...")`), and the new structure correctly separates concerns.

### QA engine — the real technical asset

**Confirmed fact:** `qa_engine.py` is 36 lines of working Python that takes a pandas DataFrame and a rule list and returns a DataFrame of issues. It supports three check types and handles missing columns gracefully.

**My assessment:** This is small but genuinely valuable. It is the one piece of code in the entire project that does something real and domain-specific. It is also correctly designed for extension — adding new check types (regex patterns, cross-field validation, range warnings vs failures, lookup tables) is straightforward.

The limitation is that it currently only has 4 generic placeholder rules. The engine is a working machine with no real fuel. Real commercial value requires populating it with actual DNO-specific rules — pole height ranges per voltage and material, clearance thresholds per crossing type, conductor sag limits, material specifications, and so on. This is not a coding task — it is a domain knowledge task that requires access to DNO technical specifications (ENA TS 43-8, ESQCR 2002, each DNO's own policies).

### Frontend — surprisingly complete

**Confirmed fact:** The upload form and map viewer are both well-built Bootstrap 5 / Leaflet interfaces. The JavaScript modules implement a full client-side workflow including presigned upload, polling, and GeoJSON map rendering with colour-coded QA status.

**My assessment:** The frontend is the most complete part of the project and represents genuine development effort. It is also pragmatically designed — using Bootstrap and Leaflet (both CDN-loaded) means no build toolchain, no npm dependency nightmare, and easy deployment. The DNO/voltage dropdown in the upload form shows domain awareness.

The risk is that the frontend was built ahead of the backend, meaning it calls endpoints that don't exist. But its design assumptions (presign → PUT → finalize → poll → redirect to map) are sound and the backend can be built to match.

### Recovery recommendation — I agree with the audit

**Confirmed fact:** The forensic audit recommends targeted recovery over rebuild, with a phased plan starting from housekeeping through to full pipeline.

**My assessment:** This is the correct recommendation. The arguments for it are strong:

1. The architecture is right — throwing it away would mean re-making the same decisions
2. The QA engine works — it just needs to be wired into the data flow
3. The frontend is complete — rebuilding it would be pure waste
4. The gaps are specific and well-defined — they are listed endpoint by endpoint in the audit
5. The quarantine contains a working reference for how CSV/GIS processing was previously done

A full rebuild would take longer, produce roughly the same architecture, and waste the frontend and QA engine work. The recovery path is clearly faster.

### Is the codebase worth continuing from?

**My honest answer: Yes, but with a caveat.**

The codebase is worth continuing from because the working parts are genuinely good and the missing parts are well-understood. The recovery plan (Phases 0–1) would realistically take one focused developer 2–5 days to produce a working end-to-end path.

The caveat is that "continuing from the codebase" is only the first step. Turning this into a useful product also requires real DNO rule data, real survey file formats, and real-world testing — none of which are code problems. The codebase gets you to a working skeleton. The hard work after that is domain-specific.

---

## 5. Product Assessment

### What is the strongest product identity?

Having read everything — the project history, the audit, the context documents, and the market research — I believe the strongest and clearest product identity is:

**A pre-CAD data validation engine for UK overhead line design.**

Not a workflow platform. Not a job tracker. Not a CAD tool. Not a reporting hub. A focused validation engine that answers one question: "Is this survey data ready to go into PLS-CADD, and if not, what's wrong with it?"

This is the product that:
- has the clearest single value proposition
- solves the most specific pain point
- is achievable with the existing codebase
- is easiest to demonstrate to a potential buyer
- has no direct competitor

The broader vision (workflow management, DXF export, PDF reporting, job tracking) is all reasonable future scope, but it should not be the launch identity. Every feature beyond core validation dilutes focus, extends timeline, and increases the chance of never shipping.

### Where does it sit in the product landscape?

The market research found:
- **PLS-CADD** (Bentley) — dominant design tool, assumes clean input, validates during/after design
- **Neara** ($1.1B valuation) — network-wide digital twin, strategic-level, not job-level
- **IQGeo** — general-purpose utility GIS, not OHL-specific
- **Excel spreadsheets** — the actual current "tool" for pre-CAD QA

SpanCore would sit in a gap that no existing product fills: between the raw survey data output and the PLS-CADD input. It is not competing with PLS-CADD — it is complementary to it.

---

## 6. Real-World Usefulness

### Would this actually be useful?

**My honest view: Yes — if it contains real rules and handles real file formats.**

The pain point is genuine. Every overhead line designer in the UK currently validates survey data manually before loading it into PLS-CADD. They check column names, verify coordinate systems, look for missing fields, compare pole heights against allowable ranges, confirm material types against DNO-approved lists, and flag obvious data errors. They do this using spreadsheets, institutional knowledge, and experience.

A tool that automates even a subset of these checks would:
- Save time on every job (estimated 30–60 minutes per job for basic checks)
- Catch errors that manual review misses (especially under time pressure or with junior staff)
- Reduce DNO design rejection rates
- Allow less experienced designers to produce compliant data with less senior oversight

### Who would use it?

1. **Overhead line designers** at framework contractors and IDPs — the people who currently do this checking manually
2. **Design managers** — who want consistency and quality assurance across their teams
3. **ICP design teams** — who submit designs to multiple DNOs with different standards and need to get it right first time
4. **DNO design approval teams** — who could use it to pre-screen incoming submissions

### What pain would it remove?

The most immediate pain is **late-stage design rejection**. When a designer spends hours or days building a PLS-CADD model only to discover that the input survey data was wrong — missing fields, incorrect coordinate system, pole heights outside range — the rework cost is significant. The frustration is even higher when the error would have been trivially catchable if anyone had checked.

The second pain is **inconsistency**. Different designers on the same team apply different levels of checking rigour. A standardised tool enforces a minimum quality bar.

### Conditions for real-world usefulness

The tool becomes genuinely useful only when it:
1. Can ingest actual survey file formats used in the industry (Trimble CSV exports, specific shapefile schemas, PLS-CADD-compatible formats)
2. Contains real DNO-specific rules — not 4 generic placeholders, but the actual clearance thresholds, material specifications, and compliance requirements from each DNO's published standards
3. Has been tested against real survey data from actual jobs
4. Produces output that a designer can immediately act on (clear issue descriptions, row/field references, pass/warn/fail classification)

None of these are in place yet. The engine is built, but the fuel is not.

---

## 7. Commercial and Profitability Assessment

### Could this become commercially useful?

**My honest view: Yes, but it is a niche product with a modest ceiling.**

The market research identifies 50–80 potential buyer organisations in the UK, with 500–2,000 potential individual users. At a realistic SaaS price of £5,000–20,000 per organisation per year, the mature-market revenue ceiling is approximately **£400,000–1,600,000 ARR**. That is a viable small software business, not a venture-scale opportunity.

### Would people pay for it?

People would pay for it if it demonstrably reduces their rework rate. The decision-maker is typically a design team lead or operations director at a framework contractor, IDP, or ICP. They care about:
- Design rejection rate (directly affects contract margin)
- Time per job (directly affects throughput)
- Junior designer productivity (directly affects team scalability)
- Compliance risk (directly affects their reputation with DNOs)

If the tool can demonstrate a measurable reduction in any of these, there is a real purchase conversation.

### What kind of product would it be?

In order of likelihood of success:

1. **Internal team tool / consultancy tool** — highest probability of first use. You or a small team use it internally to improve your own design workflow, then offer it as part of a service offering ("we use our own QA tool, which is why our designs pass first time")
2. **Licensed tool sold to IDPs/ICPs** — these are small firms (5–30 people) who buy specialist tools with short procurement cycles. Price: £5,000–10,000/year
3. **SaaS product sold to framework contractors** — larger firms with longer sales cycles but higher per-seat value. Price: £10,000–20,000/year
4. **DNO-adopted standard tool** — highest value, longest sales cycle, most political. Would require NIA funding or formal procurement

### Biggest commercial risks

1. **Rule data is the moat, not the code.** The Flask app and QA engine are technically achievable by any competent developer. The commercial value lies in having comprehensive, accurate, up-to-date DNO-specific rule data. If you don't build this moat, the product is easily replicable.

2. **The market is small.** 50–80 organisations is not a large addressable market. Customer acquisition cost must be kept very low — direct sales, word of mouth, conference demos, not paid marketing.

3. **DNO standards change.** Each DNO periodically updates its technical specifications. The tool must be maintained as a living product, not shipped once.

4. **Competitor risk from adjacent platforms.** Neara ($1.1B), IQGeo, or even Bentley (PLS-CADD's owner) could build this capability as a feature. If they did, a small startup would struggle to compete. The window of opportunity is open now but may not stay open indefinitely.

5. **Sales cycle friction.** Even in the IDP/ICP segment, tool adoption requires trust. Designers are conservative — they will not trust an automated QA tool until they have manually verified its output on several real jobs. Adoption will be slow initially.

---

## 8. Strengths

These are the things that are genuinely strong, original, or valuable about this project:

**1. Correct problem identification.**
The project has identified a real, specific, unaddressed gap in a professional workflow. This is not a solution looking for a problem. The market research confirms: no dedicated pre-CAD validation tool exists for UK overhead line design. Every designer is doing this work manually. This is the single strongest asset the project has.

**2. Correct architectural scope.**
The decision to build a web-based validation tool (not a CAD plugin, not a desktop app, not a full platform) is pragmatically right. Web deployment means no installation friction, multi-user access, and potential for cloud/SaaS delivery. Flask is appropriately lightweight for the tool's scope.

**3. Working QA engine.**
The `qa_engine.py` module is small, clean, tested logic that does the core thing the product needs to do. It is correctly designed for extension. This is the nucleus of the product.

**4. Complete frontend.**
The upload form and map viewer are genuinely well-built. They show domain awareness (DNO/voltage selector, rulepack concept, QA status colour coding on map). This is not throwaway work.

**5. Detailed, honest self-awareness.**
The handover pack is unusually rigorous. The forensic audit, the canonical-vs-reference distinction, the explicit separation of confirmed-vs-planned — this level of self-documentation is rare and valuable. It means a new developer (or AI) can pick up this project and understand it quickly, which is itself a form of asset.

**6. Regulatory timing.**
RIIO-ED2's £22.2B investment cycle, Ofgem's digitalisation mandates, and the net zero connection surge are all creating real demand for tools that improve design workflow efficiency. The timing is genuinely good.

---

## 9. Weaknesses and Risks

These are the real problems, not softened:

**1. The project has never run end-to-end.**
Six months after the last commit, there is still no path from "upload a file" to "see a result." The frontend calls endpoints that don't exist. The QA engine has never processed a real upload. The map viewer has never displayed real data. Until this is fixed, the project is a collection of parts, not a product.

**2. The rule data is the product, and it doesn't exist yet.**
Four generic placeholder rules do not constitute a DNO compliance tool. Building real rulepack data for even one DNO (SPEN) requires access to their published technical specifications, understanding of ENA standards (TS 43-8, EREC G81), and domain knowledge of what actually gets checked in practice. This is not something that can be approximated by a developer without electricity network design experience.

**3. Scope drift is a persistent risk.**
The project history documents show a pattern of expanding vision — DXF export, PDF reports, job tracking, map preview, multi-DNO support, S3 storage, Trimble integration. Each of these is individually reasonable, but together they represent months of work. The danger is that no single feature gets finished because attention keeps moving to the next one. The recovery plan correctly identifies this risk and prescribes narrow focus.

**4. Solo developer fragility.**
This appears to be a solo or very small team project. The codebase reflects this — one development burst in October 2025, then nothing. Solo projects are vulnerable to interruption, loss of momentum, and the absence of second opinions. The refactor was started but not finished, likely because of exactly this dynamic.

**5. No real-world validation.**
The mock data (5-row CSV, 5-point shapefile) is useful for development but tells you nothing about whether the tool handles real survey files. Real Trimble exports, real shapefile schemas from actual jobs, real edge cases (missing columns, mixed coordinate systems, partial data) — none of this has been tested.

**6. The market is niche and conservative.**
Electricity network designers are not early adopters of new software tools. They trust PLS-CADD because they have used it for years. Persuading them to add another tool to their workflow — even one that saves time — requires patient, relationship-based sales. This is not a "build it and they will come" market.

**7. The codebase has real bugs.**
Beyond the missing endpoints, the app factory has a confirmed path resolution bug (`static_folder` resolves to a non-existent directory), the home page crashes on every request, and the Makefile smoke test calls a non-existent endpoint. These are all fixable, but they mean the project cannot even be demo'd in its current state.

**8. No competitive moat beyond domain knowledge.**
The Flask app, QA engine, and frontend are all technically reproducible by a competent developer in a few weeks. The defensibility of this product depends entirely on the quality and completeness of its rule data — which is currently empty.

---

## 10. Whether It Is Worth Continuing

**My honest answer: Yes, but only under specific conditions.**

The project should continue if:

1. **You can get it running end-to-end within two weeks.** The recovery plan's Phase 0 and Phase 1 are the test. If you (or an AI/developer) can complete the local upload pipeline — presign, PUT, finalize with real QA processing, status poll, map view — within a focused sprint, the project is viable. If this doesn't happen, the pattern of starting-but-not-finishing will repeat.

2. **You have access to real DNO rule data.** This means either personal domain expertise in overhead line design, access to someone who has it, or access to published DNO technical specifications. Without real rules, the tool has no commercial value.

3. **You narrow the scope ruthlessly.** The product is: upload a CSV, validate it against a rulepack, see the results. That's it. No DXF export, no PDF reports, no S3 integration, no job tracking — not until the core path works, is tested with real data, and has been shown to someone in the industry who confirms it is useful.

4. **You define a clear first user.** Not "DNOs and ICPs and IDPs and contractors." One specific person, ideally someone you know or can reach, who does overhead line design and would try the tool on a real job.

The project should be seriously reconsidered if:

- You cannot commit focused time to the recovery sprint
- You have no access to domain expertise or real rule data
- You find yourself adding new features before the core path works
- Six months from now, it still has not been tested on a real survey file

The project should **not** be abandoned outright, because:
- The problem is real and confirmed by market research
- The technical foundation is sound
- The competitive landscape is genuinely open
- The regulatory timing is favourable
- The existing work (QA engine, frontend, architecture) has real value

---

## 11. Best Path Forward

### Technical path

**Weeks 1–2: Recovery sprint (Phases 0–1 from the recovery plan)**
- Fix the home page (replace broken `index.html`)
- Fix the `static_folder` / `template_folder` path bug
- Create `api_upload.py` with presign, PUT, and status endpoints
- Wire real QA processing into `api_intake.py` (read CSV, run `run_qa_checks`, save results)
- Add `GET /map/view/<job_id>` to render the map template
- Implement real `GET /map/data/<job_id>` to return actual QA results as GeoJSON
- Run a complete end-to-end test with `sample_data/mock_survey.csv`
- Deliverable: one working path from upload to map view

**Weeks 3–4: Real data validation**
- Obtain a real survey CSV from an actual overhead line job (even an anonymised/simplified one)
- Test the upload pipeline against it — discover what breaks
- Adapt the CSV parsing to handle real column names, data types, and edge cases
- Begin building a real SPEN rulepack with actual rule values from published specifications

**Weeks 5–8: First useful version**
- GIS shapefile upload path (Phase 2)
- File-based job persistence (Phase 3)
- One complete, accurate SPEN rulepack
- Error handling and edge cases
- A version you could demo to a real designer

### Strategic path

**Months 1–2: Prove the concept to yourself.**
Get the tool running. Test it on real data. Confirm that the QA checks it performs are actually the checks designers perform manually. If the answer is yes, you have something. If not, adjust before going further.

**Months 3–4: Prove the concept to one real user.**
Find one overhead line designer — at an IDP, ICP, or framework contractor — and show them the tool. Ask them: "Would this have caught errors you've seen? Would this save you time?" Their answer determines everything.

**Months 5–6: Decide the commercial model.**
Based on feedback, choose one of:
- **Internal tool** — use it in your own work, offer it as part of a consultancy service
- **Licensed tool** — sell subscriptions to IDPs/ICPs at £5K–10K/year
- **Pilot programme** — approach a DNO about an NIA-funded trial

### Commercial path

The lowest-risk commercial path is:

1. **Start as an internal/consultancy tool.** Use it in your own work. Build credibility and case studies.
2. **Sell to IDPs/ICPs first.** Small firms, short procurement cycles, acute pain point (right-first-time design submission). Price at £5,000–10,000/year.
3. **Expand to framework contractors.** Higher value, longer sales cycle. Use IDP/ICP reference customers as credibility.
4. **Approach DNOs last.** Longest sales cycle, highest political complexity. Use NIA funding as an entry point. Position as a design quality improvement tool that reduces their approval workload.

---

## 12. Final Brutally Honest Verdict

Here is what I think, stated plainly.

**The good news:** You have identified a real gap in a real market. The pre-CAD QA space for UK overhead line design is genuinely unoccupied. The problem is confirmed by industry evidence, not just your own belief. The regulatory environment (RIIO-ED2, Ofgem digitalisation mandates, net zero volume surge) is actively creating demand for tools like this. The codebase you have is architecturally sound and recoverable. The QA engine works. The frontend is polished. No one else appears to be building this.

**The bad news:** You have been working on this since at least October 2025 and it has never run end-to-end. The most critical part of the product — real DNO rule data — does not exist. The codebase has been left in a broken mid-refactor state for six months. The market, while real, is small (50–80 organisations) and conservative. And the project shows signs of scope creep — too many features planned, not enough features finished.

**The honest question you need to answer:** Can you finish the core path in the next two weeks, build a real rulepack with actual DNO rules, and show it to one real designer within two months? If yes, this project has a genuine chance. If not — if the pattern of starting, expanding, pausing, and restarting continues — the window will close. Not because someone else will build it (they probably won't, for a while), but because the project will never reach the point where it proves its own value.

**The core tension is this:** The market opportunity is real but modest. The technical work remaining is achievable but requires focused execution. The commercial path is viable but demands domain credibility. None of these things are impossible, but all of them require finishing what has been started before starting anything new.

**My recommendation:** Continue. But set a hard deadline. If the tool cannot upload a real survey file, validate it against a real SPEN rulepack, and display the results on a map within 8 weeks, it is time to make a different decision. Not because the idea was wrong, but because execution is where ideas become products.