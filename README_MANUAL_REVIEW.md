# GridFlow Manual Review Harness

A reusable browser validation harness for the GridFlow map-review workflow.
Use it after **any** feature task — not only the C2E2 popup work that
motivated it — to confirm the app still loads, navigates, and surfaces
review signals correctly across the real survey jobs.

The harness is **validation-led, not feature-led**: every check answers
"does this still work for a real designer reviewing a real job?".

---

## What it runs

### 1. Baseline review suite (always runs)

| # | Check | Question it answers |
|---|---|---|
| 1 | App loads | Does the GridFlow shell render at all? |
| 2 | Target job/map loads | Does the chosen job's map data fully populate? |
| 3 | Console clean | Did the page log any JS errors during the run? |
| 4 | Review navigation works | Can a review group be selected? |
| 5 | Next / Previous works | Do the per-target navigation arrows advance and rewind? |
| 6 | Route highlight works | Does clicking a span produce a highlighted route group? |
| 7 | Release Map works | Does the "release map" path unlock review and show its note? |
| 8 | Planner Awareness toggle works | Does toggling planner awareness flip the layer state? |
| 9 | Popups open without crashing | Does the first marker popup render without throwing? |
| 10 | Popup remains readable | Is the popup constrained to the viewport and scrollable? |

### 2. Optional checklists (task-specific)

Each feature task can layer on a YAML checklist of extra checks. Three
canonical ones live in [validation_checklists/](validation_checklists/):

- `c2e2_popup.yml` — popup section/field assertions for the C2E2 model
- `planner_awareness.yml` — planner-awareness layer presence
- `route_highlight.yml` — route highlight and DOM class

Supported checklist `type` values:

| type | Description |
|---|---|
| `selector_visible` | Wait until a CSS selector is visible |
| `text_present` | Wait until visible text matches |
| `popup_text_contains` | First marker popup must contain each item in `contains:` |
| `click_selector` | Click a selector; optionally wait for `expect_selector` / `expect_text` |
| `route_highlight_active` | Highlight the first route span and assert the DOM class |
| `planner_awareness_visible` | Assert at least one planner-awareness marker exists |

---

## Install

```bash
pip install selenium pyyaml
```

Selenium 4.10+ ships with **Selenium Manager**, which auto-resolves the
matching `chromedriver` on first run — you do not need to `brew install`
anything separately. Chrome itself must be installed.

---

## Run

The harness boots its own local Flask server (via `werkzeug.serving`) on a
free port, drives a headless Chrome, and writes a timestamped run folder.

```bash
# baseline only (recommended after any task)
python scripts/manual_review.py --jobs P008/F001 --suite baseline

# baseline + a task-specific checklist
python scripts/manual_review.py \
  --jobs P008/F001 P010 \
  --suite baseline \
  --checklist validation_checklists/c2e2_popup.yml

# multiple jobs and multiple checklists
python scripts/manual_review.py \
  --jobs P008/F001 P010 P005/F001 Gordon Bellsprings \
  --suite baseline \
  --checklist validation_checklists/c2e2_popup.yml \
  --checklist validation_checklists/route_highlight.yml
```

### Job argument forms

| Form | Resolves to |
|---|---|
| `P010/F001` | Project file `uploads/projects/P010/files/F001` |
| `P010` | First file under project `P010` |
| `J12345` | Legacy job at `uploads/jobs/J12345` |
| `Gordon` | Alias → `P010/F001` |
| `Bellsprings` | Alias → `P008/F001` |
| Any other text | Searches every project's `project.json` / `meta.json` |

### Useful flags

| Flag | Effect |
|---|---|
| `--base-url URL` | Drive an existing GridFlow server instead of starting a local one |
| `--evidence-screenshot` | Capture screenshots for **passed** checks too |
| `--overview-screenshot` | Capture one final viewport screenshot per job |
| `--timeout-ms N` | Override the per-check timeout (default 15000 ms) |

---

## Outputs

Each run produces `validation_runs/<UTC-timestamp>/`:

```
validation_runs/20260509_201530/
├── validation_report.md   # human-readable summary, one row per check
├── console_log.txt        # every browser console entry observed
├── failures.json          # array of failed CheckResult dicts
└── screenshots/           # only failed checks (unless --evidence-screenshot)
```

Exit codes:

| Code | Meaning |
|---|---|
| `0` | All checks passed |
| `1` | At least one check failed |
| `2` | Setup error (bad job arg, missing checklist, missing Selenium) |

---

## When to run it

- After any change to the map viewer, popups, planner-awareness layer, or
  review navigation
- Before opening a PR that touches `app/static/js/map-viewer.js` or related
  templates
- After any DNO rulepack or QA-engine change that could surface different
  popup content

The harness is intentionally additive: existing pytest unit tests still
cover the deterministic Python core. This harness covers the parts that
only fail in a real browser.

---

## Adding a new task-specific checklist

1. Drop a YAML file in `validation_checklists/`.
2. Use existing files as templates — top-level `name:` plus a `checks:` list.
3. Each item needs at least `id` and `type`; descriptions are recommended.
4. Reference the file with one or more `--checklist` flags.

Keep checklists narrow: one file per feature surface, only the checks that
catch real regressions.
