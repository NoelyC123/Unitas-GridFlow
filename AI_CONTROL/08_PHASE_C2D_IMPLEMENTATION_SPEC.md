# Phase C2/D Implementation Specification

**Owner decision:** Phase C2/D professional QA + display refinement is approved as the next implementation path.

## 1. Purpose

Phase C2/D is a controlled professional QA + display refinement pass for GridFlow's existing survey-to-design intelligence workflow.

It improves the designer-facing map and popup experience while keeping GridFlow within its current survey-to-design intelligence role. The phase should make existing evidence easier to read, make missing evidence wording more truthful by asset type, and surface a small set of design-readiness fields where they are already present, alias-supported, or safely derivable from current data.

Compatibility with current real-file intake and validation jobs is part of the acceptance criteria. This phase stays outside Stage 4 scope: no full 50-field capture model, no mobile/tablet capture build, no photo management platform, no Field Maps replacement, and no unverified PoleCAD import work.

## 2. Current Implementation Observations

### Popup sections

The map popup implementation is already asset-specific in `app/static/js/map-viewer.js`.

Current routing:

- `buildPopupHtml()` chooses a popup layout via `popupAssetKind()`.
- Current asset kinds include `existing`, `proposed`, `angle`, `stay`, `context`, and `thirdparty`.
- Existing poles currently include sections such as Identity, Physical, Equipment & pole-top, Network links, Survey metadata, Mechanical, Third-Party Attachments, Location, Evidence, Source & Confidence, Lifecycle / Design, and QA / Review.
- Proposed poles use Specification and Design Requirements sections instead of treating every missing value as a field-capture failure.
- Angle poles place Mechanical near the top and add a design-focus stay/angle warning when stay evidence is missing.
- Context/crossing records use Crossing Details instead of the pole physical/specification model.
- Third-party infrastructure has its own warning-led popup, explicitly excluding it from electric network design.

Risk: `map-viewer.js` is large and is best changed narrowly. Popup changes should mainly adjust section order, labels, row helpers, and CSS rather than rewrite the whole viewer.

### Field extraction and enrichment

Current field enrichment is split across intake, map route enrichment, and display helpers:

- `app/controller_intake.py` normalises core controller columns with `_CONTROLLER_ALIASES`.
- `app/routes/map_preview.py` backfills `POPUP_DATA_FIELDS` for generated map data and calls runtime enrichment helpers.
- `app/pole_field_schema.py` derives support role fields such as `measured_height_m`, `proposed_height_m`, `support_schema_role`, replacement status, and unresolved decisions.
- `app/electrical_schema.py` parses voltage, conductor/cable, phase, equipment, pole-top, earthing, and asset plate details.
- `app/survey_connectivity.py` derives network-link and survey metadata display fields such as support IDs, survey equipment, capture method, GNSS accuracy summary, and parsed horizontal/vertical accuracy.
- `app/field_ownership.py` keeps network electrical fields on `span_features` and `cable_features`, not point features.

Important constraint: keep voltage/conductor/phase/cable display on span/cable popups under the current field-ownership policy unless that policy is explicitly changed. Phase C2/D should avoid treating absent pole-level electrical values as pole data gaps.

### Blank/missing field wording

Current missing-value handling is partially mature:

- Existing pole missing height is treated as a design blocker/review item because clearance checks depend on measured existing height.
- Proposed pole missing height/specification is framed as a design decision, not a survey failure.
- Context records hide pole physical semantics and focus on crossing/clearance/action wording.
- Condensable popup sections already collapse all-vacuous rows into summary text for Physical, Mechanical, Specification, Equipment & pole-top, and Evidence.
- Some row-level wording is still generic (`not captured`, `not recorded`, `not specified`, `not linked`, `not applicable yet`). Phase C2/D should standardise these by asset type.

### Lifecycle display

Lifecycle is already visible through:

- Lifecycle marker classes in `lifecycleMarkerClass()`.
- Replacement link rendering through `renderLifecycleMatches()`.
- Popup lifecycle rows for replacing, being replaced by, match status, match offset, and action.
- Design-focus sections for replacement pairing where `replacement_pair_audit` is present.

Phase C2/D should polish wording and hierarchy while leaving lifecycle logic intact.

### Stay evidence

Stay evidence is already handled through:

- QA checks for angle poles without nearby stay evidence.
- Popup mechanical rows for stay evidence, stay type, stay bearing, anchor details, route deviation, and action.
- Design-focus warnings for angle poles where `stay_evidence_status` is `missing`.
- Record-panel indicators for angle stay evidence.

Phase C2/D should make the stay evidence wording more consistent and avoid implying a captured stay where only inferred or absent evidence exists.

### Span/crossing display

Span and crossing display already includes:

- `span_features` from `app/span_generator.py`, attached in `map_preview.py`.
- Span layer, span label modes, span list panel, and span popups in `map-viewer.js`.
- Crossing/context enrichment via `app/context_crossing.py`.
- Context/crossing popup rows for priority, label, clearance measured, distance from route, action, span corridor links, and correlation confidence.

Phase C2/D should keep span/crossing display lightweight and review-focused. Full clearance calculation stays outside this pass unless measured clearance evidence already exists.

### Map filters/layers

The map currently has:

- Layer toggles for existing, proposed, angle, stays/anchors, third-party infrastructure, context/crossings, spans, underground cables, and suggested replacement links.
- Review focus filters for design blockers, review required, missing existing heights, missing specifications, missing stay evidence, span anomalies, span crossing context, UG cable incomplete spec, clearance crossings, EX/PR matches, and records with remarks.
- Count-aware layer captions and disabled states when a layer has nothing to show.

Phase C2/D should refine grouping and readability within the current map framework and avoid a large UI restructure.

## 3. Priority Field Set

The Phase C2/D candidate field set contains the following 15 fields. The goal is professional display, not complete survey capture.

| Field | Designer value | Current source/status | Existing pole display | Proposed pole display | Context/span display | Missing/blank wording |
| --- | --- | --- | --- | --- | --- | --- |
| Pole class / strength | Indicates structural capacity and whether assumptions are needed before loading/design. | Already present/displayable as `pole_class`; not robustly alias-supported in controller intake. | Physical: show value as evidence; missing is review. | Specification: show as design spec; missing is design decision required. | Hide for context. | Existing: `not captured - confirm from field notes/asset records`; proposed: `not specified - design decision required`. |
| Material | Supports design assumptions, asset condition review, and construction planning. | Already present as `material`; included in core schema fields. | Physical: show with condition; missing is review. | Specification: show if specified; missing is design decision required. | Hide for context except third-party notes if present. | Existing: `not captured - material unknown`; proposed: `not specified - design specification required`. |
| Condition | Indicates asset trust, replacement need, and risk to reuse/retain decisions. | Already present/displayable as `condition`; usually not captured. | Physical: show as field evidence; missing is review/info depending lifecycle. | `not applicable yet` unless proposed record carries a condition note. | Hide for context. | Existing: `not captured - condition not evidenced`; proposed: `not applicable yet`. |
| Measured/design height | Existing clearance-critical evidence or proposed design specification. | Already present as `height`; enriched to `measured_height_m` or `proposed_height_m`. | Physical/Height Evidence: measured height and source/confidence. | Specification: design/proposed height. | Hide for context unless the context record is explicitly a clearance measurement. | Existing: `not captured - clearance check impossible`; proposed: `not yet specified - design decision required`. |
| Height source / confidence | Tells designer whether height can be trusted for clearance/sag work. | Already present/derivable via `height_source` and `classify_height_confidence()`. | Height Evidence / Physical: source and confidence. | Show only if a proposed height was imported; otherwise N/A/design decision. | Hide unless relevant to a clearance measurement. | `height source not recorded - reliability unknown`. |
| Stay present / evidence | Shows whether angle/terminal support evidence exists. | Derivable from `stay_evidence_status`, nearby stay records, remarks, and `stay_present`. | Mechanical: show captured/missing/not indicated. Angle poles get prominent action. | Design Requirements: show `review angle/stay evidence` if angle/proposed angle; otherwise not indicated. | Stay/anchor records show parent/detail instead. | `not captured - check field notes/photos/plan evidence` for angle poles; `not indicated by current data` otherwise. |
| Stay type | Helps determine mechanical support interpretation. | Already present/displayable as `stay_type` or `stay_types`; partly derivable from nearby stay classification. | Mechanical: show type where captured/inferred from stay records. | Same only if relevant to proposed angle/terminal design. | Stay/anchor popup: primary detail. | `not captured - stay configuration unknown`. |
| Lean | Indicates structural condition and replacement/retention risk. | Already present/displayable as `lean_direction` and `lean_severity`; usually not captured. | Physical: show severity/direction and warning style if present. | Hide or `not applicable yet` unless explicitly supplied. | Hide for context. | Existing: `not captured - lean not assessed in digital file`; proposed: `not applicable yet`. |
| Defects | Highlights rot/split/burn/impact and review risk. | Already present/displayable as `defect_type`; not usually captured. | Physical: warning if present, review/info if absent. | Hide or `not applicable yet`. | Hide for context. | Existing: `not captured - defect evidence not supplied`; proposed: `not applicable yet`. |
| Equipment presence | Identifies transformer/switch/fuse/recloser or loading/coordination implications. | Safely derivable from `equipment`, `equipment_rating`, `structure_type`, and remarks via `parse_equipment_context()`. | Equipment & pole-top: show categories/primary/kVA/rating where inferred or captured. | Same if proposed design includes equipment. | Equipment records can use equipment popup/section if role supported. | `none inferred from current fields` rather than `none exists`. |
| Pole-top / insulator / crossarm | Supports design-readiness review without full equipment modelling. | Alias-supported/derivable in `electrical_schema.py` via `pole_top_arrangement`, `insulator_type`, `crossarm_configuration`. | Equipment & pole-top: show captured/inferred values. | Specification/Equipment section if present. | Hide for context. | `not recorded in digital file`. |
| Voltage carried | Confirms circuit class and electrical review context. | Alias-supported in `electrical_schema.py` from `voltage`, `line_voltage`, `network_voltage`; field ownership puts this on spans/cables, not points. | Keep as span/cable-owned under current field-ownership policy. Refer to span/cable electrical rows. | Same. | Span/cable popup: show line voltage. | Span/cable: `not recorded - circuit voltage not supplied`; point: avoid showing as missing pole data. |
| Conductor / cable type | Supports span review and handoff quality. | Alias-supported in `electrical_schema.py` from `conductor_type`, `conductor`, `cable_type`, `conductor_size`, `cable_size`; belongs on spans/cables. | Keep as span/cable-owned under current field-ownership policy. | Same. | Span/cable popup: show conductor/cable type, size, phase/cores. | Span/cable: `not recorded - conductor/cable specification not supplied`; point: avoid showing as missing pole data. |
| Surveyor / date / GNSS accuracy | Establishes provenance and trust in the survey evidence. | Already present/displayable; `survey_connectivity.py` parses GNSS summary and horizontal/vertical accuracy. | Survey metadata and Evidence sections. | Same. | Same for context/span/cable where carried in properties. | `not recorded in export`; accuracy: `not recorded - positional confidence unknown`. |
| Photo indicator | Tells designer whether external evidence exists without building photo management. | Already present/displayable via `photo_links`, `photo_count`, `has_full_pole_photo`, `has_pole_top_photo`, `has_defect_photo`. | Evidence: show linked refs/indicator only. | Same. | Same where relevant. | `no linked photo references in current export`. |
| Action required / access / wayleave notes | Surfaces immediate design/construction constraints. | Already present/displayable as `action_required`, `access_constraint`; wayleave may appear in remarks/location but is not robustly structured. | Design Requirements or Context/Evidence notes. | Design Requirements. | Context/crossing popup: action/access/coordination emphasis. | `not captured - check field notes/plans`; for proposed: `not specified yet`. |

Fields intentionally outside Phase C2/D:

- Full 50-field survey capture model.
- Photo upload, thumbnails, storage, or evidence workflow.
- Full condition taxonomy beyond displaying supplied condition/defect fields.
- DNO compliance verdicts beyond existing rulepack/QA cues.
- PoleCAD import fields not verified against real import requirements.

## 4. Popup Layout Proposal

### Existing pole

Recommended section order:

1. Design focus banners: source confidence, height evidence, replacement pairing, stay/angle if relevant.
2. Identity: point, type, feature code, status, role, circuit/job reference if present.
3. Physical evidence: measured height, height source/confidence, pole class, material, condition, lean, defects, foundation.
4. Mechanical: stay evidence, stay type, bearing, anchor detail, route deviation, action.
5. Equipment & pole-top: equipment category, primary equipment, kVA/rating, pole-top arrangement, insulator/crossarm, earthing, asset plate.
6. Network links: from/to/parent/support links only; voltage/conductor remains span/cable-owned under current field ownership.
7. Survey metadata and evidence: surveyor, date, equipment, capture method, GNSS/accuracy, photo indicators, remarks.
8. Third-party attachments: only if present, otherwise condense.
9. Location.
10. Source & Confidence.
11. Lifecycle / Design.
12. QA / Review.
13. Raw / technical fields collapsed.

### Proposed pole

Recommended section order:

1. Design focus banners: replacement pairing/source confidence where present.
2. Identity.
3. Specification: proposed/design height, pole class, material, specification source, purpose/unresolved decisions.
4. Design requirements: action required, access constraints, stay required if angle/terminal, design note.
5. Equipment & pole-top if proposed equipment is captured.
6. Network links.
7. Survey metadata and evidence.
8. Location.
9. Lifecycle / Design.
10. QA / Review.

Missing-value rule: avoid "not captured" where the value is a future design decision. Use "not yet specified" or "design decision required".

### Stay / anchor

Recommended section order:

1. Identity.
2. Stay details: parent pole, type, direction/bearing, configuration, nearest pole.
3. Network links.
4. Survey metadata and evidence.
5. Location.
6. QA / Review.

Missing-value rule: parent links and bearing are review information, not blockers unless the parent pole cannot be identified for an angle/terminal support.

### Span / crossing / context feature

Recommended section order:

1. Design focus: crossing/context priority, designer action, span corridor links.
2. Identity.
3. Crossing details: priority, label, clearance measured, distance from route, action, correlation confidence.
4. For span/cable popups only: electrical rows for voltage, conductor/cable, size, phases/cores.
5. Survey metadata and evidence.
6. Location.
7. Source & Confidence.
8. QA / Review.

Missing-value rule: avoid implying absence of a crossing or clearance risk just because a clearance value is not recorded. Use "not measured in current export" and "review route context".

### Equipment

If equipment remains represented through point properties rather than a separate equipment layer:

1. Keep Equipment & pole-top as a section on the relevant pole popup.
2. Show "none inferred from current fields" when no equipment hint is found.
3. Use warning/review status only where the record suggests transformer/equipment but no structured equipment data is present.

If later equipment records become separate point features, treat that as a separate implementation decision outside the Phase C2/D display polish.

## 5. Map UX Refinement Proposal

These refinements are realistic for the current Leaflet + `map-viewer.js` + `map_viewer.html` structure:

- Marker sizing and hierarchy:
  - Slightly increase context and stay/anchor marker hit area while keeping visual weight lower than structural poles.
  - Keep asset type as marker shape and label.
  - Keep QA status as border/status colour.
  - Keep lifecycle as overlay treatment such as opacity, halo, dashed border, or link line.
  - Avoid relying on colour alone to communicate asset type, QA, and lifecycle simultaneously.

- Layer grouping:
  - Keep current checkbox mechanics.
  - Group labels visually into record layers, route/link layers, and infrastructure/context layers.
  - Preserve disabled-state behaviour for empty layers.
  - Keep context/crossing layer available and clearly labelled; avoid hiding it so aggressively that Field Maps parity is lost.

- Review focus grouping:
  - Keep current buttons and counters.
  - Visually group focus buttons into evidence gaps, route/span review, context/clearance review, and replacement review.
  - Keep record-panel behaviour for focused lists.

- Popup readability:
  - Keep max width around the current 460px unless mobile testing requires adjustment.
  - Reduce all-uppercase visual weight in section titles if it harms scanning.
  - Make design-focus sections visually distinct but not alarm-heavy when status is informational.
  - Condense sections where all rows are vacuous.
  - Keep raw/technical fields collapsed by default.

- Low-risk CSS/layout improvements:
  - Move repeated popup styling out of inline template CSS only if it can be done without changing behaviour.
  - Improve row spacing and status colours for review/warning/blocker.
  - Make long values wrap cleanly (`overflow-wrap: anywhere`) for IDs, remarks, and technical fields.
  - Keep cards and controls compact; this is an operational review tool, not a marketing surface.

## 6. Implementation Task Breakdown

### C2D-1: Field inventory + alias/display mapping

Likely files touched:

- `app/routes/map_preview.py`
- `app/controller_intake.py`
- `app/pole_field_schema.py`
- `app/survey_connectivity.py`
- `app/electrical_schema.py` only if an alias is clearly missing and already supported by current model
- Tests: `tests/test_map_preview.py`, `tests/test_controller_intake.py`, `tests/test_pole_field_schema.py`, `tests/test_electrical_schema.py`

Expected tests:

- Focused tests for any new alias or backfilled popup field.
- Existing map enrichment tests should continue to pass.

Acceptance criteria:

- The 10-15 Phase C2/D fields have an explicit source/status decision.
- Existing generated `map_data.json` files are backfilled safely through `POPUP_DATA_FIELDS` where appropriate.
- Point features stay clean of span/cable-owned network electrical fields after enrichment.
- Missing fields remain display-only gaps unless current QA rules already treat them as warnings/blockers.

Risk notes:

- Keep controller aliases conservative so terrain/instrument elevation does not become pole height.
- Keep voltage/conductor data off point popups under the current field-ownership policy.

### C2D-2: Popup section refinement

Likely files touched:

- `app/static/js/map-viewer.js`
- Possibly `app/static/style.css` or `app/templates/map_viewer.html` for small style support
- Tests: `tests/test_map_preview.py`; consider adding static truthfulness checks if existing patterns support it

Expected tests:

- Static or endpoint tests confirming popup support fields still exist in map data.
- No visual test is required by unit tests, but manual validation should be done on real jobs.

Acceptance criteria:

- Existing, proposed, angle, stay, context, third-party, span, and cable popup layouts remain asset-specific.
- Design-focus sections remain first where there is a meaningful designer action.
- Physical/Specification/Evidence sections condense gracefully when all rows are unavailable.
- Raw/technical details remain collapsed.

Risk notes:

- `map-viewer.js` is sensitive; avoid a rewrite.
- Keep row helpers simple and avoid duplicating display logic across asset kinds.

### C2D-3: Asset-specific missing-value wording

Likely files touched:

- `app/static/js/map-viewer.js`
- Tests: static tests or targeted JavaScript-free checks only if practical; otherwise cover via map data enrichment and manual validation

Expected tests:

- Existing Python tests should remain green.
- Add lightweight tests only if wording can be asserted through rendered template/static content without browser automation.

Acceptance criteria:

- Existing poles use measured-evidence wording for missing height/material/condition.
- Proposed poles use design-decision wording for missing specification/design height.
- Context records avoid irrelevant pole physical gaps.
- Span/cable popups use "not recorded" wording for missing voltage/conductor/cable details without implying the line is electrically absent.
- Equipment absence is worded as "none inferred from current fields" unless a record suggests equipment should exist.

Risk notes:

- Over-warning missing optional fields will reduce trust. Only height/stay/critical crossing evidence should feel like design blockers where current rules justify it.

### C2D-4: Map UX/layer panel polish

Likely files touched:

- `app/templates/map_viewer.html`
- `app/static/js/map-viewer.js`
- `app/static/css/map-viewer.css`
- `app/static/style.css` only if shared popup styles are actually used by this view
- Tests: `tests/test_map_preview.py`, `tests/test_map_static_truthfulness.py`

Expected tests:

- Template/static tests for controls that are expected to remain present.
- Manual browser review on representative jobs.

Acceptance criteria:

- Layer controls remain functional and count-aware.
- Review focus controls remain functional.
- Marker hierarchy is clearer without changing asset classification logic.
- Context/crossing records remain discoverable.
- Popup rows wrap and scan cleanly on desktop and mobile widths.

Risk notes:

- Avoid changing Leaflet layer mechanics unless necessary.
- Avoid visual changes that make QA status, lifecycle state, and asset type compete with each other.

### C2D-5: Tests and validation corpus check

Likely files touched:

- Tests only, as needed:
  - `tests/test_map_preview.py`
  - `tests/test_field_ownership.py`
  - `tests/test_pole_field_schema.py`
  - `tests/test_electrical_schema.py`
  - `tests/test_controller_intake.py`
  - `tests/test_qa_engine.py`
  - `tests/test_map_static_truthfulness.py`

Expected tests:

- `pytest -v`
- `pre-commit run --all-files`

Acceptance criteria:

- Full test suite passes.
- Field ownership remains clean.
- Existing real-job map enrichment paths still return valid feature collections.
- No regression to controller intake for Gordon, Bellsprings, 2814_474, or 2814_513 style files.

Risk notes:

- Some real validation jobs may be local-only. Tests should skip gracefully where fixtures are absent, following current patterns.

### C2D-6: Documentation/changelog update

Likely files touched:

- `AI_CONTROL/02_CURRENT_TASK.md` after implementation starts or completes
- `CHANGELOG.md`
- Possibly `README.md` only if the user-facing capability description changes materially

Expected tests:

- Documentation-only change may not need tests by itself, but should be included after the implementation test run.

Acceptance criteria:

- Documentation records Phase C2/D as professional QA + display refinement, not Stage 4.
- Any test count or validation claim is backed by an actual run.
- Source-of-truth hierarchy remains consistent with `AI_CONTROL/00_PROJECT_CANONICAL.md`.

Risk notes:

- Leave README/CHANGELOG completion wording until implementation is validated.

## 7. Validation Plan

### Automated validation

Expected commands after implementation:

```bash
pytest -v
pre-commit run --all-files
```

Additional targeted tests during development may include:

```bash
pytest -v tests/test_map_preview.py tests/test_field_ownership.py tests/test_pole_field_schema.py
pytest -v tests/test_electrical_schema.py tests/test_controller_intake.py tests/test_qa_engine.py
pytest -v tests/test_map_static_truthfulness.py
```

### Real-job validation targets

Validate against currently available real job families and skip gracefully where local data is absent:

- P011, if present: operational map review blockers and popup trust/readability.
- Gordon/NIE: Irish Grid/TM65 handling, EX/PR matching, split-file evidence, angle/stay review.
- Bellsprings/SPEN: OSGB handling, SPEN rulepack, real 11kV OHL refurbishment context.
- 2814_474 family: regression baseline for route sequencing and map popup display.
- 2814_513 family: raw controller dump and completeness reporting baseline.
- Existing local regression fixtures referenced by current tests.

### Manual acceptance checks

For at least one representative job:

- Existing pole popup shows measured height evidence, material/condition gaps, lifecycle, source confidence, survey metadata, and QA review clearly.
- Proposed pole popup uses design-specification wording rather than field-capture failure wording.
- Context/crossing popup avoids irrelevant pole fields and shows clearance/action context.
- Stay/anchor popup shows parent/direction/configuration evidence where present.
- Span/cable popup owns voltage/conductor/cable display.
- Layer toggles and focus filters still work.
- Marker hierarchy distinguishes asset type, QA status, and lifecycle without relying on a single colour cue.

## 8. Controller Decisions For Implementation

1. Use all 15 fields as the Phase C2/D candidate set, but implement in priority order. If the first implementation pass becomes too large, stop after the strongest 10-12 and record the remainder as follow-up.

2. Keep voltage/conductor/cable fields span/cable-owned under the current field-ownership policy. A related circuit summary can be considered later, but it is not part of the first implementation pass.

3. Keep context/crossing records clearly discoverable with good labelling and counts. They do not need to be all-on by default if that creates clutter.

4. Update `AI_CONTROL/02_CURRENT_TASK.md` before coding starts to mark Phase C2/D as active. Leave README/CHANGELOG completion wording until implementation and validation are done.
