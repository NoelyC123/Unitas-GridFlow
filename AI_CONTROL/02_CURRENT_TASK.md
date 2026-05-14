# Current Active Phase

Conduct Designer Review - In-Person Walk-Through

## Active Priority

Run the Stage 5G designer review using the structured script and one-page summary.

Use:

- `AI_CONTROL/115_DESIGNER_REVIEW_SCRIPT.md` as the walk-through script.
- `AI_CONTROL/115_DESIGNER_ONE_PAGER.html` as the printed summary handed to the designer at the start.
- Registered job `P_LOCAL_DESIGNER_REVIEW`.
- Feedback route `http://127.0.0.1:5000/feedback/<job_id>` when available.

## Review Setup

Create the registered review job:

```bash
cd /Users/noelcollins/Unitas-GridFlow
source .venv312/bin/activate

python scripts/run_pipeline.py \
  --baseline tests/baseline/fixtures/enwl_sample.csv \
  --field real_pilot_data/P_LOCAL_001/enwl_enrichment_clean \
  --output /tmp/gridflow_designer_review \
  --job-id P_LOCAL_DESIGNER_REVIEW \
  --register \
  --overwrite-registration
```

Run the pre-flight check when available:

```bash
python scripts/preflight_designer_review.py P_LOCAL_DESIGNER_REVIEW
```

Start Flask:

```bash
export FLASK_APP=run.py
flask run
```

Review routes:

- Workspace: `http://127.0.0.1:5000/workspace/view/P_LOCAL_DESIGNER_REVIEW`
- Overlay map: `http://127.0.0.1:5000/map/overlay/P_LOCAL_DESIGNER_REVIEW`
- QA map: `http://127.0.0.1:5000/map/view/P_LOCAL_DESIGNER_REVIEW`
- Feedback form: `http://127.0.0.1:5000/feedback/P_LOCAL_DESIGNER_REVIEW`

## Core Message

Use this wording throughout the review:

> You have survey evidence, but you still need confirmed DNO engineering
> records before design.

Conductor spec and pole class/strength rating require authoritative confirmation from DNO baseline engineering records. Field evidence may suggest these attributes, but they should not be treated as authoritative design inputs unless confirmed by DNO or baseline records.

In the current readiness model, poles without confirmed conductor specification and pole class/strength rating remain design-blocked until the relevant DNO engineering records are obtained.

## Feedback Capture

Capture designer feedback through the live form where possible:

- `http://127.0.0.1:5000/feedback/P_LOCAL_DESIGNER_REVIEW`

If the live form is unavailable, use the paper backup table in `AI_CONTROL/115_DESIGNER_REVIEW_SCRIPT.md`.

Document findings in:

- `AI_CONTROL/116_DESIGNER_FEEDBACK_FINDINGS.md`

The findings document must include:

- one direct designer quote per review question where possible,
- severity per finding,
- whether the designer understands why 0/10 design-ready is correct for this dataset,
- whether Report 06 is usable for a DNO data request,
- whether the workspace and map overlay are useful enough for pilot review,
- whether photo/evidence integration is a blocker or later enhancement,
- the recommended next phase.

## Active Boundaries

Do not start Stage 6 implementation until designer feedback is captured and `AI_CONTROL/116_DESIGNER_FEEDBACK_FINDINGS.md` exists.

Do not claim:

- final engineering design capability,
- DNO data replacement,
- autonomous design authorization,
- production multi-user deployment,
- PoleCAD export,
- DNO-grade compliance verification,
- full GIS product capability.

Do preserve:

- evidence-based claims,
- source authority hierarchy,
- verification flags,
- design blocker visibility,
- designer feedback as the next decision input,
- local-data privacy boundaries.

## Acceptance Direction

The designer review should answer:

- Can a UK OHL designer explain what GridFlow does after a 25-minute walk-through?
- Does the designer understand that 0/10 design-ready is due to missing DNO engineering records, not pipeline failure?
- Is Report 06 clear enough to support a real DNO data request?
- Does the workspace help designers inspect matched poles efficiently?
- Does the map overlay help detect baseline-field alignment issues?
- What is the first practical improvement needed before a controlled pilot?
