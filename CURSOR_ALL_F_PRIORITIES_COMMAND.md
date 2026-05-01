# Cursor Command — Map Truthfulness Cleanup All 8 F-Priorities

## Read first

1. AI_CONTROL/00_PROJECT_CANONICAL.md
2. AI_CONTROL/02_CURRENT_TASK.md
3. MAP_TRUTHFULNESS_CLEANUP_SPEC.md
4. CURSOR_MAP_TRUTHFULNESS_FOLLOWUP.md

## Objective

Implement the full map truthfulness follow-up batch in strict sequence.

The previous truthfulness priorities P1-P8 are already implemented. This follow-up batch handles the remaining validation refinements from manual review.

## F-priorities

### F1 — Rename "Circuit spans" to "Provisional route spans"

Use "Provisional route spans" where spans are generated from route sequence rather than captured circuit/line records.

Only use "Circuit spans" where actual captured line/circuit span data exists.

### F2 — Resolve replacement count mismatch

Manual validation showed:

- Suggested Replacement Links (0)
- EX/PR matches (11)

Clarify this mismatch.

Either generate visible replacement link geometries for the matches, or update UI wording so it is clear there are 11 EX/PR matches but 0 drawn link geometries.

### F3 — Split anomaly label modes

Replace the broad anomaly label mode with more granular options:

- Show on hover only
- Pin critical anomalies only
- Pin crossing/context spans
- Pin all review spans
- Pin all spans

### F4 — De-duplicate span popup warnings/actions

Review signals should say what is wrong.

Designer actions should say what to do.

Do not repeat identical conductor/phase/short-span messages in both sections.

### F5 — Classify short-span causes

Very short spans should be classified where possible as:

- likely replacement/co-located pair
- possible duplicate capture
- possible sequence issue
- possible genuine short span
- uncertain

### F6 — Collapse empty pole popup sections

Replace repeated blank field blocks with concise summaries.

Examples:

- No pole-mounted equipment captured or inferred.
- Surveyor, date and GNSS accuracy not captured in this export.
- Pole class, material and design height not specified.

Keep raw/technical fields available in a collapsed section if needed.

### F7 — Clarify anchor/stay count mismatch

Distinguish survey/control/base anchor records from mechanical stay/anchor assets.

Do not let users confuse control anchors with mechanical stays.

### F8 — Disable all zero-count layers consistently

Apply the UG cable truthfulness rule to all zero-count layers.

If a layer has zero records, show it disabled/greyed out or clearly unavailable.

Examples:

- Third-party infrastructure (0)
- Underground cables (0)
- Suggested replacement links (0), unless match records are drawable

## Requirements

- Implement F1 to F8 in strict order.
- Do not broaden scope.
- Frontend/map truthfulness and usability only.
- Preserve correct field ownership:
  - Pole/support popups = structure, mechanical evidence, mounted equipment, source/evidence.
  - Span/cable popups = route, voltage, conductor, phase, clearance/crossing data.
- After each implementation batch, run:

pytest -v
pre-commit run --all-files

- Commit clearly and push to master.
- Report completion after each F-priority before moving to the next.

Start with F1.
