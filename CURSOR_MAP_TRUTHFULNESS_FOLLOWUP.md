# Cursor Command — Map Truthfulness Follow-Up Batch

Manual validation review on 2026-05-01 identified 8 remaining refinement issues after the main map truthfulness cleanup.

Read first:

1. AI_CONTROL/00_PROJECT_CANONICAL.md
2. AI_CONTROL/02_CURRENT_TASK.md
3. MAP_TRUTHFULNESS_CLEANUP_SPEC.md
4. CURSOR_MAP_TRUTHFULNESS_ALL_PRIORITIES.md

## Follow-up priorities

Implement all follow-up priorities in sequence.

### F1 — Rename generated span layer

Rename "Circuit spans" to "Provisional route spans" when spans are generated from route sequence rather than captured line/circuit records.

Only use "Circuit spans" where actual captured circuit/span data exists.

### F2 — Resolve replacement count mismatch

Manual validation showed:

- Suggested Replacement Links (0)
- EX/PR matches (11)

Clarify this mismatch.

Either generate visible replacement link geometries for confirmed/suggested matches, or change the UI wording so it is clear there are 11 EX/PR matches but 0 drawn link geometries.

### F3 — Split anomaly label modes

The current "Pin on anomaly spans only" mode is too broad because crossing/context spans can create many labels.

Add more granular options:

- Show on hover only
- Pin critical anomalies only
- Pin crossing/context spans
- Pin all review spans
- Pin all spans

### F4 — De-duplicate span popup warnings/actions

Span popups currently repeat the same conductor/phase/short-span messages in both review signals and designer actions.

Review signals should say what is wrong.

Designer actions should say what to do.

Do not repeat identical text twice.

### F5 — Improve short-span cause classification

Very short spans should be classified by likely cause where possible:

- likely replacement/co-located pair
- possible duplicate capture
- possible sequence issue
- possible genuine short span
- uncertain

### F6 — Collapse empty pole popup sections

Pole popups still show long blocks of empty fields.

Replace repeated empty fields with concise summaries, for example:

- No pole-mounted equipment captured or inferred.
- Surveyor, date and GNSS accuracy not captured in this export.
- Pole class, material and design height not specified.

Keep full raw/technical fields available in a collapsed section if needed.

### F7 — Clarify anchor/stay count mismatch

The job summary may show anchor/control records while the layer shows Stays/Anchors (0).

Distinguish:

- control/base/station anchor records
- mechanical stay/anchor assets

Do not let users confuse survey control anchors with mechanical stays.

### F8 — Disable all zero-count layers consistently

Apply the same truthfulness rule used for UG cables to all zero-count layers.

If a layer has zero records, show it disabled/greyed out or clearly unavailable.

Examples:

- Third-party infrastructure (0)
- Underground cables (0)
- Suggested replacement links (0), unless match records are drawable

## Requirements

- Stay within map truthfulness and usability only.
- Do not broaden scope.
- Keep the field ownership model:
  - pole/support popups = structure, mechanical evidence, mounted equipment, source/evidence
  - span/cable popups = route, voltage, conductor, phase, clearance/crossing data
- Run `pytest -v`.
- Run `pre-commit run --all-files`.
- Commit clearly and push to master.

Start with F1.
