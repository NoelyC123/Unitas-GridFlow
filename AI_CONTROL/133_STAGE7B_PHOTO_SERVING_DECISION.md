# Stage 7B — Photo Serving Decision

**Date:** 2026-05-18
**Reference:** `AI_CONTROL/131_STAGE7A_PHOTO_INTEGRATION_SPEC.md`

---

## Problem

Field photos exist in `real_pilot_data/` (gitignored, local-only). The registered job
directory (`uploads/jobs/<job_id>/`) contains only pipeline run outputs — the field
evidence folder is never copied by `gridflow/registration.py`. The workspace can detect
photo counts from `MergedPole.field_photo_count` but cannot display images.

The workspace pole detail currently shows: `Photos: 9` — a bare integer with no images.

Without a serving strategy, Stage 7B cannot be validated.

---

## Why This Matters

- Designer cannot see field photos alongside structured evidence records
- The Design Readiness card and DNO Evidence card are complete; photos are the missing
  piece for a full in-workspace review
- Stage 7B workspace photo display is blocked until one of the options below is implemented

---

## Three Options

### Option A — Flask Route Serving from Configured Path (RECOMMENDED for dev/validation)

**Approach:** Add a Flask route that serves photos from a configured base path. The
path is set in app config, never derived from the URL.

**Route:** `GET /api/photos/<survey_id>/<pole_folder>/<filename>`

**Security requirements (MANDATORY — non-negotiable before any implementation):**

- `REAL_PILOT_DATA_ROOT` is set in Flask app config (e.g., `app.config["REAL_PILOT_DATA_ROOT"]`),
  never from URL parameters or user input
- `survey_id` must match a registered survey identifier — validated against a known allowlist
  or the job's `02_field_dataset.json` `dataset_path` value
- `pole_folder` must match the `NN_SUPPORT_*` pattern and must exist under the resolved
  survey evidence path
- `filename` must pass: `re.match(r'^[\w\-]+\.(jpg|jpeg|png|JPG|JPEG|PNG)$', filename)`
- Use `flask.send_from_directory(safe_base_path, filename)` — never `send_file` with
  any component derived from user input
- Return `404` (not `500`) for all invalid, missing, or out-of-range cases
- Log all `404` responses for monitoring

**Implementation sketch:**

```python
@photos_bp.route("/api/photos/<survey_id>/<pole_folder>/<filename>")
def serve_photo(survey_id: str, pole_folder: str, filename: str):
    # 1. Validate filename extension
    if not re.match(r'^[\w\-]+\.(jpg|jpeg|png|JPG|JPEG|PNG)$', filename):
        abort(404)

    # 2. Resolve survey base from config (never from URL)
    base = current_app.config.get("REAL_PILOT_DATA_ROOT")
    if not base:
        abort(404)

    # 3. Validate pole_folder pattern
    if not re.match(r'^\d{2}_SUPPORT_[\w]+$', pole_folder):
        abort(404)

    # 4. Build and verify path stays within base
    photo_dir = Path(base) / survey_id / "enwl_enrichment_clean" / pole_folder / "field_photos"
    photo_dir = photo_dir.resolve()
    if not str(photo_dir).startswith(str(Path(base).resolve())):
        abort(404)

    return send_from_directory(photo_dir, filename)
```

**Limitations:**

- `real_pilot_data/` path is local dev only — not portable across machines
- Will not work in production or multi-user deployment without migration to Option B
- Requires `REAL_PILOT_DATA_ROOT` to be set correctly per-machine (e.g., in `.env`)

**Verdict:** Correct choice for local dev/validation phase. Fastest path to workspace
photo display. Security constraints above are non-negotiable prerequisites.

---

### Option B — Copy Photos on Job Registration (Production path)

**Approach:** When a job is registered via `scripts/run_pipeline.py --register`,
copy `enwl_enrichment_clean/*/field_photos/` into the job directory under
`uploads/jobs/<job_id>/field_photos/<pole_folder>/`.

Photos are then served from the registered job directory alongside other outputs,
using existing Flask static serving patterns.

**Pros:**

- Portable — job directory is self-contained
- No special config required per machine
- Production-safe (no reference to gitignored local paths)
- Correct long-term architecture

**Cons:**

- Storage duplication: P_LOCAL_002 has 99 photos (~15 MB); a 50-pole job with full
  photo evidence could be 100+ MB per registered job
- Slower registration step for large jobs
- Photos in `uploads/` are not gitignored by default — `.gitignore` would need updating

**Verdict:** Correct production architecture. Implement as Stage 8 migration prerequisite
after Option A proves the workspace photo display works.

---

### Option C — Symlink on Registration

**Approach:** Registration creates a symlink `uploads/jobs/<job_id>/field_evidence/ →
real_pilot_data/<survey_id>/enwl_enrichment_clean/`.

**Pros:**

- No storage duplication
- Fast registration

**Cons:**

- Breaks on Windows (symlinks require elevated permissions or Developer Mode)
- Fragile if either path moves
- Not production-safe
- Adds hidden path dependency to the registered job directory

**Verdict:** Not recommended.

---

## Decision

**Implement Option A for local dev/validation phase.**

Rationale:

- Fastest path to Stage 7B workspace validation against P_LOCAL_002 and real Unitas jobs
- Security constraints are explicit and implementable in one focused Codex task
- Does not require changes to registration or storage layout
- Option B is the documented production migration path (Stage 8 prerequisite)

---

## Stage 7B Implementation Checklist

### Backend (Codex)

- [ ] Add `REAL_PILOT_DATA_ROOT` to `app/__init__.py` or `config.py`
- [ ] Create `app/routes/photos.py` with `photos_bp` Blueprint
- [ ] Implement `GET /api/photos/<survey_id>/<pole_folder>/<filename>` with all
  security constraints above
- [ ] Register `photos_bp` in `app/__init__.py`
- [ ] Store `dataset_path` (field evidence root) in `pipeline_summary.json` during
  registration so the route can validate `survey_id` against the known path
- [ ] Return 404 for all invalid cases; log 404s
- [ ] Add route tests covering: valid photo served, invalid extension blocked,
  path traversal blocked, missing file 404

### Frontend (Claude Code)

- [ ] Add "Field Photos" section to `app/templates/workspace/pole_detail.html`
  (position: after Design Readiness card, before DNO Evidence card)
- [ ] Group photos by type (from `PhotoSet.type_summary()`)
- [ ] Show one photo per type by default; "Show all N photos" expands to grid
- [ ] Lazy-load images using Intersection Observer API
- [ ] Click thumbnail → open `/api/photos/<survey_id>/<pole_folder>/<filename>`
  in new tab
- [ ] Graceful empty state: "No photos available" when `field_photo_count == 0`
  or when photo serving is not configured
- [ ] Add readiness summary photo count to job overview table

### Note on P_LOCAL_002 photo types

All P_LOCAL_002 filenames are sequential (`IMG_0903.JPG`, etc.) — no descriptive text.
The photo type detection will classify: first file → `full_pole`, remainder → `unknown`.
The workspace should display `unknown` photos as "Field Photos" without a type badge
rather than forcing a label. This is not a bug; it is correct for sequential filenames.

---

## Config Setup for Local Dev

Add to `.env` (not committed):

```
REAL_PILOT_DATA_ROOT=/Users/noelcollins/Unitas-GridFlow/real_pilot_data
```

Add to `app/__init__.py` or config:

```python
app.config["REAL_PILOT_DATA_ROOT"] = os.environ.get("REAL_PILOT_DATA_ROOT", "")
```
