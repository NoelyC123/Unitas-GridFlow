# Changelog

All notable changes to Unitas GridFlow are recorded here, session by session.

This file is the rolling history of what shipped. Each entry is dated.

Format loosely follows [Keep a Changelog](https://keepachangelog.com/).

---

## 2026-04-24 (batch 20B — structured issue model)

### Added

- **`app/issue_model.py`** (new module):
  - `classify_issue(text)` — pattern-matches issue text against a priority-ordered
    lookup to return structured fields: `issue_code`, `severity`, `category`, `scope`,
    `confidence`, `is_observation`, `recommended_action`.
  - `enrich_issues(issues_df)` — adds all structured fields to an issues DataFrame
    as new columns. The existing `Issue` and `Severity` columns are preserved unchanged
    so all downstream consumers continue to work without modification.
  - Severity levels: `critical` (coordinate failures, missing columns),
    `warning` (most rule violations), `observation` (replacement pair detections).
  - Categories: `replacement_intent`, `structural_evidence`, `data_completeness`,
    `span_geometry`, `coordinate_quality`, `rulepack_validation`.
  - `is_observation: True` for replacement pair detections — separates observed
    patterns from genuine defects.
  - `recommended_action` populated for height, material, angle/stay, and span issues.

- **`app/routes/api_intake.py`**:
  - `enrich_issues()` called after `_postprocess_issues()` — structured fields now
    appear in `issues.csv` for every job.

- **`tests/test_issue_model.py`** (new file):
  - 22 tests covering: pattern matching for all issue tiers, fallback for unknown text,
    severity/category/observation correctness, `enrich_issues` column presence,
    mutation safety, and row-count invariance.

148 tests passing. Pre-commit clean. No QA logic changes.

---

## 2026-04-24 (batch 20A — trust fixes: rulepack truthfulness, span-count cleanup, controller label normalisation)

### Changed

- **`app/templates/upload.html`**:
  - Removed 6 non-existent rulepack options from the DNO dropdown:
    `NIE_LV`, `SPEN_LV`, `SSEN_LV`, `ENWL_LV`, `UKPN_LV`, `UKPN_11kV`.
  - Upload form now only offers: Auto (detect), SPEN_11kV, SSEN_11kV, NIE_11kV, ENWL_11kV.

- **`app/routes/api_rulepacks.py`**:
  - Replaced stub implementation (always returned `dno: SPEN`, empty thresholds) with
    a real implementation that derives metadata directly from the `RULEPACKS` dict in `dno_rules.py`.
  - `GET /api/rulepacks/` now returns the actual list of supported rulepack IDs (excluding DEFAULT).
  - `GET /api/rulepacks/<id>` now returns truthful `total_checks`, `check_types`, `height_range_m`,
    and `coordinate_bounds` derived from real rules. Returns 404 for unknown IDs.

- **`app/controller_intake.py`**:
  - `parse_raw_controller_dump()`: compound Trimble feature codes at col 4 (e.g. `Pol:LAND USE`,
    `EXpole:BOUNDARY`) are now normalised to their base code (`Pol`, `EXpole`).
    This prevents raw location suffixes from appearing in map popups, PDF output, and `feature_codes_found`.

- **`app/routes/api_intake.py`**:
  - Removed `"span_count": 0` from `_build_feature_collection` metadata and from `meta.update()` in `finalize()`.

- **`app/routes/map_preview.py`**:
  - Removed `"span_count": 0` from `_empty_feature_collection` fallback.

### Tests

- **`tests/test_app_routes.py`**: Added 4 new tests:
  - `test_api_rulepacks_list_returns_supported_rulepacks` — verifies correct 4 rulepacks, no DEFAULT, no unsupported
  - `test_api_rulepacks_detail_returns_real_check_data` — SPEN_11kV returns real height_range and check_types
  - `test_api_rulepacks_detail_returns_404_for_unknown` — FAKE_11kV returns 404
  - `test_upload_form_does_not_offer_unsupported_rulepacks` — HTML guard against non-existent options

- **`tests/test_controller_intake.py`**: Added 1 new test:
  - `test_parse_raw_controller_dump_normalises_compound_feature_code` — `Pol:LAND USE` → `Pol`, `EXpole:BOUNDARY` → `EXpole`

126 tests passing. Pre-commit clean.

---

## 2026-04-24 (batch 19 — field meaning and designer clarity layer)

### Changed

- **`app/controller_intake.py`**:
  - `build_circuit_summary()`: wording updated from "structural records / overhead line route"
    to "poles / support structures / surveyed route". Added `existing_count` and
    `proposed_count` to returned dict (scans structural rows for EXpole vs Pol/PRpole codes).
  - `build_top_design_risks()`: all 4 risk titles and `designer_impact` strings rewritten to
    field-aligned designer language (angle stay, height, material, short spans).
  - `build_design_readiness()`: replaced alarming "This file cannot support full design"
    headline with informative gap description stating what is absent and what is needed.

- **`app/routes/api_intake.py`**:
  - `_build_feature_collection()`: added `file_type` parameter; `file_type` now included
    in GeoJSON metadata so the JS can choose the correct ID label per file type.
  - `_build_replacement_narratives()`: added ambiguity caveat note when the same EX pole
    ID appears across multiple narratives (multi-PR/same-EX case).
  - `finalize()`: replacement cluster wording in `what_this_supports` rewritten (1 pair →
    "Proposed replacement identified near existing pole"; N pairs → "N probable replacement
    pairs detected — verify intended pairings"). Added `issue_groups` triage metadata dict
    (span_issues, replacement_clusters, missing_heights, angle_stay counts) to meta.json.
    `_build_feature_collection` call updated to pass `file_type`.

- **`app/templates/map_viewer.html`**:
  - Removed misleading "Spans: 0" stat block. Records stat centered as a single display.
  - Circuit summary section now shows sub-lines: structural/context/anchor breakdown
    and existing/proposed counts when available.
  - JS version bumped `?v=9` → `?v=10`.

- **`app/static/js/map-viewer.js`**:
  - Added `this.fileType` state, set from `meta.file_type` in `renderSummary()`.
  - Popup ID label is now contextual: "Point no." (controller file) or "Record ID" (structured).
  - Added `explainAssetType()` method mapping feature codes to plain-English descriptions
    (EXpole, PRpole, Pol, Angle, Hedge, Tree, Gate, Track, Stream).
  - Explained type shown in popup below Type line; also shown in record panel items.

- **`app/routes/pdf_reports.py`**:
  - "Issues" section renamed "Review Signals". Row data removed from main report body.
  - Added Technical Appendix (new page via `pdf.showPage()`) with full issue detail
    including raw Row data for technical reference.
  - Footer updated from "local MVP." to "Unitas GridFlow."

- **`tests/test_controller_intake.py`**:
  - Updated 3 test assertions to match new wording in `build_circuit_summary()` and
    `build_top_design_risks()`.

121 tests passing. No QA logic changes. Presentation and interpretation only.

---

## 2026-04-24 (batch 18 — real-world survey workflow reference)

### Added

- **`AI_CONTROL/07_REAL_WORLD_SURVEY_WORKFLOW.md`**: new core project truth document
  capturing how UK overhead line survey-to-design workflows actually operate.

  Sections:
  1. Purpose of this document — why this is a permanent project reference
  2. End-to-end workflow — Field survey → Trimble → export → D2D → PoleCAD → AutoCAD → submission; where problems occur and where time is wasted
  3. Field capture reality — Trimble Access + GNSS, feature-code libraries, raw export format, GPS Z vs declared height distinction
  4. Feature code meaning — EXpole (existing asset), PRpole/Pol (proposed), context features (Hedge/Gate/Track/Stream/Fence/Tree), anchor/control points; and the Unitas behaviour implication of each
  5. Replacement logic — EXpole + PRpole proximity interpretation, typical offset distances (0–5m standard replacement, 5–10m repositioned, 10–20m minor diversion, 20m+ new route), why cautious WARN is correct
  6. Survey captures vs design needs — structured gap analysis showing what CSV contains vs what PoleCAD requires; explains why D2D workload exists
  7. The D2D problem — what D2D involves, why it is error-prone, how Unitas targets this gap
  8. What designers actually care about — real acceptance/rejection signals from design experience
  9. Real-world failure points — ranked list: missing poles, short spans (duplicate vs replacement), missing structure_type, missing stay evidence, unclear connectivity, inconsistent coding
  10. What makes a survey "design-ready" — minimum requirements vs what is not required
  11. Implications for Unitas — must/must-not list grounded in sections 1–10
  12. Future direction — Phase 1 (current): post-survey validation; Phase 2: feedback loop; Phase 3: capture guidance; Phase 4: field integration

- **`CLAUDE.md`**: control layer reading order updated to include
  `07_REAL_WORLD_SURVEY_WORKFLOW.md` as item 6 (read when making QA logic or
  output language decisions).

No application code or test changes.

---

## 2026-04-24 (batch 17 — documentation alignment after audit)

### Changed

- **`AI_CONTROL/02_CURRENT_TASK.md`**: full rewrite. Removed stale Batch 2 / 67-test
  wording. Now describes current state (Batch 16 complete, 121 tests passing), lists all
  15 validation batches, frames the current task as validating the designer summary layer
  on real files, and names the likely next reference task (real-world survey workflow
  reference document).

- **`CLAUDE.md`**: updated "Current state" section to list Batches 2–16. Updated
  "Validation-phase position" to include all capabilities added through Batch 15: record-
  role classification, design readiness, EX/PR detection, angle/stay logic, asset_intent
  labels, designer summary layer.

- **`PROJECT_DEEP_CONTEXT.md`**: updated Section 1 executive summary from "narrow pre-CAD
  QA and compliance gatekeeper" to "survey-to-design workflow intelligence tool". Updated
  Section 11 framing from "pre-CAD validation and compliance layer" to "survey-to-design
  workflow intelligence layer". Added explicit "does NOT replace Trimble/PoleCAD/AutoCAD/
  designers/surveyors" constraint block to Section 8.

- **`AI_CONTROL/01_CURRENT_STATE.md`**: expanded system capabilities list to include post-
  Batch-4 features (record-role classification, design readiness, EX/PR detection,
  angle/stay, designer summary layer, interactive map). Added Batch 16 and Batch 17
  entries to "What changed recently".

- **`WORKFLOW_SYSTEM.md`**: Section 9 phase label changed from "Phase 2C complete" to
  "batches 2–16 complete — validation-led refinement active".

- **`README.md`**: "Best current framing" updated — removed "narrow productivity / QA
  layer"; added "survey-to-design workflow intelligence layer" framing and explicit "not a
  replacement for Trimble/PoleCAD/AutoCAD/designers" as a Less Realistic framing item.

- **`CHANGELOG.md`**: Batch 16 and Batch 17 entries added.

No application code or test changes.

---

## 2026-04-24 (batch 16 — project vision documentation aligned)

### Changed

- **`AI_CONTROL/00_PROJECT_CANONICAL.md`**: core identity updated from "pre-design
  validation and reliability layer" to "survey-to-design workflow intelligence tool".
  Short definition updated. IS list expanded to include record-role interpreter and design
  risk/gap identifier. "Does NOT replace" constraint block added (Trimble, PoleCAD,
  AutoCAD, designers, DNO compliance engine). System capabilities expanded with Batch 9–15
  additions. Primary users expanded (QA leads, contractors, future DNO teams). Future
  direction added (field-capture guidance, structured survey standards). Scope discipline
  section updated accordingly.

- **`README.md`**: Overview updated to "survey-to-design workflow intelligence tool". Role
  list expanded (record-role interpretation, design risks and gaps, design-readiness
  signals). "Why this project exists" section updated with multi-audience scope and
  explicit non-replacement statement.

- **`CLAUDE.md`**: project identity, short identity, and critical context updated with new
  framing and explicit "does not replace Trimble/PoleCAD/AutoCAD/designers" constraint.

- **`WORKFLOW_SYSTEM.md`**: IS list updated with record-role interpreter, design risk
  identifier; central question updated from "Can I trust this data?" to the fuller
  multi-part formulation.

No application code or test changes.

---

## 2026-04-23 (batch 15 — designer summary layer)

### Added

- **`build_circuit_summary` (controller_intake.py)**: compact job-level summary derived
  from structural count in completeness. Emits `summary_text` such as
  "15 structural records detected along a broadly continuous overhead line route."

- **`build_top_design_risks` (controller_intake.py)**: groups existing issues and
  completeness gaps into ranked risk items: angle/stay evidence missing, structural
  heights missing, material missing, short spans, proposed supports with spec gaps.
  Each item: `title`, `count`, `summary`, `designer_impact`, `severity` (WARN/FAIL).

- **`_build_replacement_narratives` (api_intake.py)**: converts each replacement-pair
  WARN into a readable sentence, e.g. "EXpole 99 is likely being replaced by nearby
  proposed support 100 (3.2m offset)." or "…at the same surveyed position."
  Uses `_REPL_OFFSET_RE` (compiled module-level regex) to extract offset from the WARN text.

- **Map side panel (map_viewer.html + map-viewer.js)**:
  - Circuit Summary block (server-side Jinja) showing the route summary sentence
  - Top Design Risks block showing up to 3 risk items with severity colouring
  - Replacement Pairs block listing individual narratives (capped at 5)
  - JS framing line: "N review signals: W warn, F fail" rendered in `#frame-summary`
  - JS cache-bust bumped to `?v=9`

- **PDF report (pdf_reports.py)**:
  - Circuit Summary section added after header, before Design Readiness
  - Top Design Risks section added after Design Readiness, before Completeness
  - Replacement Pairs section added after Completeness, before Issues

- **meta.json storage**: `circuit_summary`, `top_design_risks`, and
  `replacement_narratives` all persisted in meta.json and passed to map template.

### Tests added

- `test_build_circuit_summary_multiple_structural_returns_route_text`
- `test_build_circuit_summary_zero_structural_returns_no_structural_text`
- `test_build_top_design_risks_includes_angle_no_stay_warn`
- `test_build_top_design_risks_includes_missing_height_risk`
- `test_build_replacement_narratives_returns_readable_text_for_pair`
- `test_build_replacement_narratives_same_position_wording`
- `test_build_replacement_narratives_returns_empty_for_no_pairs`
- Test count: **121 passing** (was 114).

---

## 2026-04-23 (batch 14 — EX/PR narrative linking and warn_texts fix)

### Added

- **`asset_intent` label in GeoJSON feature properties (api_intake.py)**:
  EXpole records receive `asset_intent="Existing asset"` (derived from `structure_type`).
  Non-EXpole records that have a replacement-pair WARN receive `asset_intent="Proposed support"`.
  All other records receive `asset_intent=None`. No new engineering logic — purely presentation.

- **`warn_count` / `warn_texts` serialised into GeoJSON properties (api_intake.py)**:
  Batch 12 computed these values but never wrote them into `feature["properties"]`, making
  angle/stay WARNs invisible in the map popup. Both fields now appear in the GeoJSON output.

- **Improved replacement cluster narrative (api_intake.py `finalize` route)**:
  Cluster summary line changed from `"N replacement pairs detected — likely EX → PR design intent"`
  to `"N probable replacement pairs detected — consistent with replacement survey work"`.

- **Improved replacement-pair popup wording (map-viewer.js)**:
  `replacementLine` now reads: `"Likely replacement pair — existing asset with nearby proposed support"`.

- **`asset_intent` surfaced in popup and record panel (map-viewer.js)**:
  New `assetIntentLine` in popup (after Type row) and `intentHtml` in record panel items.

- **JS cache-bust bump**: `map-viewer.js?v=7` → `?v=8` in `map_viewer.html`.

### Tests added

- `test_build_feature_collection_expole_gets_existing_asset_intent` — EXpole → `"Existing asset"`
- `test_build_feature_collection_replacement_pair_non_expole_gets_proposed_support` — Pol with WARN → `"Proposed support"` + `relationship="replacement_pair"`
- `test_build_feature_collection_regular_pole_has_no_asset_intent` — regular Pol → `asset_intent is None`
- `test_build_feature_collection_warn_texts_populated_in_properties` — Angle WARN → `warn_count=1`, `warn_texts` populated, `issue_count=0`
- Test count: **114 passing** (was 110).

---

## 2026-04-23 (batch 13 — confidence-aware QA refinements)

### Changed

- **Short span tiers (qa_engine.py)**: short spans are no longer a flat FAIL.
  Three distance tiers now emit calibrated WARN messages:
  - `< 3m` → `"Span very short: Xm — likely duplicate or co-located pair, verify"`
  - `3–8m` → `"Span unusually short: Xm (min Ym) — verify no duplicate entry"`
  - `8–min_m` → `"Span borderline short: Xm (min Ym) — verify no missing record"`
  All tiers emit `Severity: WARN`. Replacement-pair detection is unchanged.

- **EXpole height downgrade (qa_engine.py `range` check)**: when `field="height"`,
  `structure_type` is an EXpole code, and the value is below `min_val`, the issue
  is downgraded from a standard range FAIL to:
  `"Height likely estimated / not captured (EXpole)"` with `Severity: WARN`.
  Heights above `max_val` are still emitted as standard range issues.

- **Design readiness strong summary (controller_intake.py `build_design_readiness`)**:
  when `material_pct == 0.0` (material completely absent from digital file), prepends
  `"This file cannot support full design — critical design data missing"` as the
  first reason in the design readiness output.

### Tests updated

- `test_span_distance_flags_poles_too_close` — updated to assert "Span borderline
  short" and `Severity="WARN"` (was checking "Span too short" with implicit FAIL)
- `test_span_suppression_does_not_apply_to_pol_pol` — updated to assert "Span
  unusually short" WARN (was checking "Span too short" FAIL)
- `test_span_distance_message_shows_one_decimal_precision` — updated to match new
  "Span unusually short" tier message

### Tests added

- `test_short_span_very_close_emits_warn_very_short_tier` — span < 3m → WARN
- `test_short_span_unusual_tier_emits_warn` — span 3–8m → WARN
- `test_short_span_borderline_tier_emits_warn` — span 8–min_m → WARN
- `test_expole_height_below_min_emits_warn` — EXpole height=5, min=7 → WARN
- `test_expole_height_above_max_remains_range_fail` — EXpole height=30 > max → FAIL
- `test_non_expole_height_below_min_remains_range_issue` — Pol height=5 → FAIL
- Test count: **110 passing** (was 104).

---

## 2026-04-23 (batch 12 — angle/stay evidence logic)

### Added

- **`_ANGLE_CODES` and `_STAY_EVIDENCE_CODES` frozensets in `qa_engine.py`**:
  `_ANGLE_CODES` = {"Angle", "angle", "ANGLE"}; `_STAY_EVIDENCE_CODES` covers
  "Stay", "Staywire", "Stay wire", "Stay pole" and lowercase/uppercase variants.

- **`angle_stay` check type in `qa_engine.py`**: dataset-level proximity scan.
  For each angle record, checks whether any `_STAY_EVIDENCE_CODES` record exists
  within 30m (OSGB projected), or whether the angle record's own `location`/
  remarks text contains "stay". If neither, emits a `Severity: WARN` issue with
  cautious wording: `"Angle structure with no stay evidence detected — verify
  whether stay capture is missing or not required for this job"`.

- **`angle_stay` rule added to `BASE_RULES` in `dno_rules.py`**: all four
  rulepacks now carry this rule. Files with no angle records produce no issues —
  the check silently skips.

- **`angle_no_stay_count` injected into `design_readiness`** in
  `api_intake.py`: when angle/no-stay WARNs exist, a bullet is added to
  `design_readiness.reasons` and `angle_no_stay_count` is set on the dict.

- **`warnBlock` in map popup** (`map-viewer.js`): WARN features that are not
  replacement pairs now show a "Design Notes (N):" section in amber in their
  popup, listing warn_texts from the feature properties.

- **`warnHtml` in record panel** (`map-viewer.js`): WARN feature items in the
  record panel show the first warn text (truncated to 65 chars) for non-
  replacement-pair records.

- **`[WARN]` prefix in PDF** (`pdf_reports.py`): the issues table reads the
  `Severity` column from issues.csv and prepends `[WARN] ` for WARN issues.

- **JS version bumped** (`map_viewer.html`): `?v=7` to force cache refresh.

### Tests

- `test_angle_no_stay_emits_warn` — Angle + Pol at 111m, no stay → 1 WARN
- `test_angle_with_stay_within_proximity_no_warn` — Angle + Stay at 20m → 0
- `test_angle_with_stay_beyond_proximity_emits_warn` — Stay at 67m (>30m) → 1 WARN
- `test_angle_stay_remarks_evidence_suppresses_warn` — "stay installed 3m west"
  in location → 0 issues
- `test_angle_stay_no_issue_for_pol_only_file` — Pol-only file → 0 issues
- Test count: **104 passing** (was 99).

---

## 2026-04-23 (validation batch 11 — EX/PR replacement cluster detection)

### Added

- **Replacement pair detection**: adjacent structural records where exactly one
  is an EXpole code (EXpole, expole, EXPOLE) and the distance is below the
  minimum span threshold are now classified as replacement pairs rather than
  flagged as "Span too short" FAILs. These emit a `Severity: WARN` issue:
  `"Replacement pair detected (EX → PR, X.Xm offset)"`.

- **`_is_replacement_pair()` helper in `qa_engine.py`**: XOR logic — fires when
  exactly one of the two adjacent structure_type values is an EXpole code.
  Covers both EX→PR and PR→EX orderings.

- **`_EXPOLE_CODES` constant in `qa_engine.py`**: frozenset of EXpole variants
  used by the replacement pair helper.

- **WARN severity on issues**: WARN issues carry `{"Severity": "WARN"}` in the
  issue dict. Code that doesn't know about the field defaults to FAIL treatment.

- **WARN tracking in `_collect_per_row_issues`**: WARN issues are accumulated
  separately in `warn_count`/`warn_texts` alongside the existing `count`/`texts`
  (FAIL) keys.

- **WARN marker status**: map features where only WARN (no FAIL) issues exist
  receive `qa_status = "WARN"`, shown in amber on the map.

- **`relationship` property on map features**: features involved in a replacement
  pair get `"relationship": "replacement_pair"` in their GeoJSON properties.

- **Map popup replacement line**: when `props.relationship === 'replacement_pair'`,
  the popup shows "⚠ Replacement Pair (Existing → Proposed)" in amber.

- **Design Readiness replacement bullet**: when replacement clusters are detected,
  `design_readiness.what_this_supports` gains a bullet
  `"N replacement clusters detected — likely EX → PR design intent"`, and
  `replacement_cluster_count` is set on the design readiness dict.

- **Actual `warn_count` in map metadata**: `feature_collection.metadata.warn_count`
  now reflects the real count of WARN-status features rather than always being 0.

### Tests

- `test_replacement_cluster_detection` — EXpole + Pol at 3.3m → WARN
  "Replacement pair detected", no FAIL; Severity column contains "WARN"
- `test_span_suppression_does_not_apply_to_pol_pol` — Pol + Pol at 3.3m →
  FAIL "Span too short", no replacement pair WARN
- Test count: **99 passing** (was 97).

---

## 2026-04-23 (validation batch 10 — consistency and threshold cleanup)

### Fixed

- **Record count consistency**: `meta["pole_count"]` now uses
  `completeness.total_records` (all rows in the file) rather than the count of
  map-visible features (which excluded anchor rows). The PDF header "Record
  count" and the Survey Completeness "Total records" line now show the same value.
  The structural/context/anchor composition totals sum to that same value.

- **Span threshold wording**: span distance issue messages now use `{dist:.1f}m`
  (1 decimal place) instead of `{dist:.0f}m`. A 9.6 m span previously displayed
  as "Span too short: 10m (min 10m)", which looked like a false positive. It now
  displays as "Span too short: 9.6m (min 10m)", making the threshold comparison
  unambiguous.

- **Coverage labels**: `_coverage_rating()` threshold for "Partial" changed from
  `> 20%` to `> 0%`. Any nonzero coverage is now "Partial" rather than "Missing",
  so a file where 15% of structural records have height recorded no longer shows
  the same "Missing" label as a file with 0% height data. Only truly absent data
  (0%) produces "Missing".

### Changed

- `build_design_readiness()` adds up to two more items to `what_this_supports`:
  - "identifying pole types and network roles along the route" when
    `structure_type` coverage exceeds 70%
  - "locating N environmental and crossing features along the route" when
    context records (Gate, Hedge, Track, etc.) are present in the file

### Tests

- `test_coverage_rating_partial_for_low_nonzero_coverage` — 5%, 15%, 20%, 0.1%
  all return "Partial" with the new threshold
- `test_coverage_rating_missing_only_at_zero` — 0% returns "Missing"
- `test_coverage_rating_strong_above_threshold` — >70% returns "Strong"
- `test_span_distance_message_shows_one_decimal_precision` — span issue text
  contains a decimal point, confirming `.1f` format is in effect
- `test_meta_pole_count_matches_completeness_total_records` — controller dump
  with an anchor row: meta.pole_count equals completeness.total_records (3),
  not the map-visible feature count (2)
- Updated `test_build_design_readiness_partially_ready_missing_structural`:
  assertion changed from `"Missing"` to `"Partial"` for Structural Data
  (structural_pct = 9.1% is nonzero → "Partial")
- Test count: **97 passing** (was 92).

---

## 2026-04-23 (validation batch 9 — record-role classification + anchor handling + role breakdown UI)

### Added

- `_classify_role()` and `classify_record_roles()` in `app/controller_intake.py`.
  Assigns every row one of three roles: `structural` (Pol, Angle, EXpole, etc.),
  `context` (Hedge, Tree, Gate, Track, Stream, etc.), or `anchor` (grid reference
  control points like GB_Kelso / GB_Selkirk — identified by absent structure_type and
  non-numeric pole_id).

- `_STRUCTURAL_CODES` and `_CONTEXT_CODES` frozensets in `app/controller_intake.py`,
  mirroring `app/qa_engine.py` so both modules share consistent classification.

- `_df_no_anchor` filter at the top of `run_qa_checks()` in `app/qa_engine.py`.
  Anchor rows are excluded from every QA check except `span_distance`, which needs
  them to detect chain breaks at reference locations.

- Anchor chain-reset logic in the `span_distance` handler: when an anchor row is
  encountered `prev_e / prev_n` are cleared to `None`, preventing cross-anchor span
  comparisons (e.g. the ~20 km jump from a GB_Kelso reference point to the first
  survey pole no longer fires a false span-too-long issue).

- `what_this_supports` positive list in `build_design_readiness()` output, answering
  what the file enables rather than only listing gaps.

- Structural/context/anchor counts (`structural_count`, `context_count`,
  `anchor_count`) in `build_completeness_summary()` output.

- `structural_fields` per-field coverage in completeness summary — height/material
  capture rates are now calculated against structural records only, so a Gate with
  height 1.6 m does not pollute the structural height coverage percentage.

- `#role-breakdown` div in `app/templates/map_viewer.html` showing "■ N structural
  · ■ N context · ◇ N anchor" inline in the map side panel.

- `what_this_supports` bullet list under Design Readiness in the map side panel and
  in PDF reports.

- Composition line in the Survey Completeness section of the PDF report
  (e.g. "Composition: 40 structural, 12 context, 2 anchor").

- JS cache version bumped to `?v=6` in `map_viewer.html`.

### Changed

- `_CONTEXT_FEATURE_CODES` in `app/qa_engine.py` and the `CONTEXT_FEATURE_CODES` set
  in `app/static/js/map-viewer.js` expanded to include Gate, Track, and Stream (all
  three case variants). Previously these codes were not listed, causing Gate/Track/
  Stream rows to be evaluated as unknown structural features and triggering false
  height FAILs.

- `api_intake.py` finalize route now calls `classify_record_roles(df)` after CRS
  conversion, propagates role counts into map metadata, and skips anchor rows when
  building the GeoJSON feature collection (anchor rows are not map markers).

- `build_design_readiness()` uses `structural_fields` (structural-only coverage) for
  height and material percentage calculations instead of whole-file coverage.

### Tests

- `test_anchor_row_excluded_from_required_check` — anchor row with absent height
  produces no issue; structural row with absent height is still flagged.
- `test_span_distance_resets_chain_at_anchor_row` — anchor row between two poles
  8.9 km apart breaks the chain; no span-too-long issue is raised.
- `test_gate_track_stream_no_height_range_fail` — Gate, Track, Stream below minimum
  height produce no FAIL with `structural_only: True`; Pol below minimum still flags.
- Test count: **92 passing** (was 89).

---

## 2026-04-23 (validation batch 8 — strict feature-aware QA + issue deduplication)

### Changed

- `range` check handler in `app/qa_engine.py` now respects a `structural_only: True`
  flag on rules. When set, rows where `structure_type` is a context feature (Hedge,
  Tree, Wall, Fence, Post) are skipped entirely — they never trigger height-out-of-range
  or any other structural range failure.

- `required` check handler applies the same `structural_only` gate. A Hedge or Tree
  row with no height value no longer triggers "Missing required field: height".

- All height `range` rules across BASE_RULES and all four rulepacks (SPEN, SSEN, NIE,
  ENWL) now carry `"structural_only": True`. The base generic rule (7–25m) and each
  rulepack-specific rule (7–20m) both scope to structural features only.

- `required: height` in BASE_RULES now carries `"structural_only": True`.

### Added

- `_is_context_row(row, has_structure_type)` helper in `app/qa_engine.py` — centralises
  the context-feature check used by the `structural_only` gate.

- `_deduplicate_issues(issues)` function in `app/qa_engine.py`. Normalises issue text
  by stripping the parenthesised parameter suffix (e.g. "(7-25)" from "height out of
  range (7-25)"), then deduplicates by (row_index, normalised_prefix) key. This
  collapses the duplicate height-range issues that BASE_RULES and a rulepack both fire
  for the same structural record. Applied at the end of `run_qa_checks` before
  returning the DataFrame.

- 3 new tests in `tests/test_qa_engine.py`:
  - `test_structural_only_range_skips_context_features`
  - `test_structural_only_required_skips_context_features`
  - `test_deduplication_collapses_same_logical_issue_per_row`

- Updated `test_import_finalize_returns_success_for_valid_job` expected issue count
  from 11 to 10, reflecting that the duplicate height-range issue for P-1003 (height
  28.0, which previously fired both 7–25 and 7–20 rules) is now correctly deduplicated
  to one issue.

---

## 2026-04-23 (validation batch 7 — feature-aware QA + record inspection panel)

### Changed

- `span_distance` in `app/qa_engine.py` now skips context-only feature codes (Hedge,
  Tree, Wall, Fence, Post) when measuring spans between structural records. Spans
  bridge correctly over context markers — a Hedge between two poles no longer produces
  a false "span too short" issue. Non-pole records are excluded; pole-to-pole spans
  are still checked including when a context feature sits between them.

- Span distance issue text changed from "between consecutive poles" to "between
  structural records" to reflect mixed-feature survey files accurately.

- Added `_CONTEXT_FEATURE_CODES` frozenset constant to `app/qa_engine.py` to define
  which surveyor feature codes represent environmental/contextual markers.

- Map marker popup now shows "Height: not captured" (muted style) for structural
  (non-context) features where height is absent, rather than silently omitting the
  field. This immediately surfaces height gaps without requiring the designer to open
  the issues list. Context features (Hedge etc.) do not show height at all.

### Added

- Record inspection panel in map view side panel. Clicking PASS / WARN / FAIL now
  also opens a scrollable record list below the filter note, showing each record's ID,
  feature type, status, key fields (height, material, remarks if present), and first
  issue description for FAIL records. Each list item is clickable to open that
  marker's popup and zoom to it on the map.

- "Records" stat block is now clickable (`#all-records-btn`). Clicking it clears any
  active status filter and shows all records in the inspection panel.

- `_showRecordPanel` / `_hideRecordPanel` / `bindAllRecordsButton` methods added to
  `MapViewer` class in `map-viewer.js`. `setFilter` now calls show/hide automatically.

- CSS: `.record-item` (compact list card with coloured left border by status),
  `#all-records-btn` hover style.

### Tests

- 86 passing (up from 84). Added: `test_span_distance_skips_context_feature_codes`,
  `test_span_distance_context_feature_bridges_span_to_next_structural_record`.

---

## 2026-04-23 (validation batch 6 — explain, filter, and clarify)

### Added

- `_collect_per_row_issues()` in `app/routes/api_intake.py` replaces
  `_count_issues_per_row`. Now returns `{row_index: {"count": int, "texts": list[str]}}`
  storing up to 3 issue description strings per row (truncated to 80 chars each).

- `issue_texts` property on each GeoJSON feature in `map_data.json`. Allows map
  popups to display the actual issue descriptions without any additional requests.

- Interactive pass/fail filter on map view. Each status block (PASS / WARN / FAIL)
  in the side panel is now a clickable button (`status-filter-btn`). Clicking a status
  filters the map to show only markers of that status. Clicking again resets to all.
  Active filter is highlighted with a CSS `filter-active` style.

- Overlapping marker detection in `map-viewer.js`. After rendering, detects coordinates
  that share the same position to 4 decimal places and appends a note to the issue-note
  element if any are found.

- `filter-note` element below the status grid shows the current filter state and
  record count.

### Changed

- Map view side panel: "Poles" stat label changed to "Records" (more accurate for
  mixed-feature files including angle poles, hedge markers, etc.).

- PDF QA report: "Pole count:" label changed to "Record count:".

- `build_design_readiness()` reason strings rewritten to be design-consequence-focused.
  e.g. "clearance and sag-related design checks not fully supported from this file —
  height data incomplete (18.2% coverage)" instead of "height data incomplete (18.2%)".

- Map marker popup updated to show actual issue descriptions (up to 3) with a "… and N
  more" note, replacing the previous plain issue count.

- JS version bumped: `map-viewer.js?v=3` → `?v=4`.

### Tests

- 84 passing (up from 79). Added: `test_collect_per_row_issues_returns_count_and_texts`,
  `test_collect_per_row_issues_truncates_to_three_texts`,
  `test_build_feature_collection_includes_issue_texts`,
  `test_map_view_shows_records_label_not_poles`,
  `test_import_finalize_includes_issue_texts_in_map_data`.

---

## 2026-04-23 (validation batch 5 — design readiness + survey coverage + enhanced map popups)

### Added

- `build_design_readiness(completeness)` in `app/controller_intake.py`. Derives a
  design readiness verdict (NOT READY / PARTIALLY READY / LIKELY READY) and
  per-category survey coverage ratings (Strong / Partial / Missing) entirely from
  existing completeness data. No new inputs. Categories: Position & Identity,
  Structural Data, Electrical Configuration, Stability & Safety, Clearances,
  Environment & Access. Position & Identity rating uses the best coordinate field
  (lat preferred, then easting) averaged with pole_id and structure_type coverage.
  Structural Data rating uses the mean of height and material coverage.
  Always-absent categories (Electrical etc.) are shown as Missing, reflecting what
  real survey digital files do not contain, without penalising the verdict.

- Design Readiness section in map view side panel (Jinja2 server-side). Shows
  verdict in a colour-coded label (green/amber/red), a bullet list of reasons, and
  the full Survey Coverage category breakdown with colour-coded ratings.

- Design Readiness section in PDF QA report. Shows verdict, reasons, and survey
  coverage category table; page-overflow guard included.

- `_count_issues_per_row(issues_df)` in `app/routes/api_intake.py`. Replaces
  `_infer_issue_rows` in `_build_feature_collection`; returns a dict mapping
  row_index → issue_count so each GeoJSON feature now carries an `issue_count`
  property rather than just a binary PASS/FAIL flag.

- Enhanced map marker popups in `app/static/js/map-viewer.js`. Each popup now
  shows: pole_id, structure_type / feature code, height (with "m" unit), material,
  remarks/location (if distinct from id), easting/northing (or lat/lon if no grid
  coords), and issue count (highlighted red when > 0). Fields absent from the
  record are omitted cleanly.

- `design_readiness` stored in `meta.json` and returned in the finalize route
  JSON response alongside `completeness`.

- 5 new focused tests (3 unit, 2 route-level):
  - `test_build_design_readiness_likely_ready`
  - `test_build_design_readiness_partially_ready_missing_structural`
  - `test_build_design_readiness_not_ready_missing_position`
  - `test_pdf_report_includes_design_readiness_when_present`
  - `test_map_view_includes_design_readiness_verdict`

### State at end of session

- 79 tests passing (up from 74).
- Map view and PDF both surface design readiness verdict, reasons, and survey
  coverage categories alongside existing completeness detail.
- Each map marker popup shows full record detail including issue count.
- design_readiness persisted in meta.json and returned in finalize response.

---

## 2026-04-23 (validation batch 4 — rulepack auto-detection + completeness surfacing)

### Fixed

- Wrong rulepack applied to NIE/TM65 uploads when no explicit DNO was supplied.
  `api_intake.py` finalize route now tracks `explicit_dno` separately from
  `requested_dno`. After `convert_grid_to_wgs84()` writes the `_grid_crs` column,
  if no explicit DNO was supplied and the detected CRS is `EPSG:29900` (TM65) or
  `EPSG:2157` (ITM), `requested_dno` is switched to `NIE_11kV` and
  `rulepack_inferred: true` is recorded in both `meta.json` and the JSON response.
  The SPEN_11kV default is only retained for non-Irish-grid uploads with no explicit DNO.

### Added

- Completeness summary surfaced in map view side panel. `map_preview.py` `map_view`
  route now reads `meta.json` and passes the `completeness` dict to the Jinja2
  template. `map_viewer.html` renders a "Survey Completeness" section below the
  action buttons: total records, Grid CRS (if detected), per-field coverage with
  red percentage for partial fills and green tick for 100%, and feature codes found.
  No changes to `map-viewer.js`.

- Completeness summary surfaced in PDF QA report. `pdf_reports.py` reads the
  `completeness` key from `meta.json` and renders a "Survey Completeness" section
  after the job header block: total records, position status, Grid CRS, field
  coverage table, and feature codes found. Page overflow guard added for long field
  lists.

- `rulepack_inferred` field added to `meta.json` and finalize route JSON response.

- 4 new focused tests in `tests/test_app_routes.py`:
  - `test_import_finalize_infers_nie_11kv_for_irish_grid_without_explicit_dno` —
    TM65 raw dump with no explicit DNO returns `NIE_11kV` and `rulepack_inferred: true`.
  - `test_import_finalize_preserves_explicit_dno_over_crs_inference` — explicit
    `dno: "SPEN_11kV"` in request body overrides CRS-based inference.
  - `test_pdf_report_includes_completeness_when_present` — PDF route renders
    completeness section when `meta.json` contains completeness data.
  - `test_map_view_passes_completeness_to_template` — map view route passes
    completeness dict to the template context.

### State at end of session

- 74 tests passing (up from 70).
- NIE/TM65 uploads now receive NIE_11kV rulepack automatically when no explicit DNO supplied.
- Completeness summary visible in both map view side panel and PDF QA report.
- Rulepack inference traceable via `rulepack_inferred` flag in meta.json and API response.

---

## 2026-04-23 (docs alignment — WORKFLOW_SYSTEM.md integration)

### Added

- `WORKFLOW_SYSTEM.md` — defines the operating model across all AI tools. Records
  tool roles (human domain authority, ChatGPT orchestrator, Claude Code execution
  engine, Claude Desktop verification layer), source of truth hierarchy, core
  workflow loop, and current phase context.

### Changed

- `AI_CONTROL/00_PROJECT_CANONICAL.md`: core principle statement added (trusted gate,
  reliability/clarity/design-readiness framing from WORKFLOW_SYSTEM.md); WORKFLOW_SYSTEM.md
  and `app/controller_intake.py` added to project structure and key source files;
  phase status updated to include validation batches 2 and 3; navigation pointer added.

- `README.md`: test count corrected (38 → 70); completed steps updated to include
  validation batches 2 and 3; stale limitation removed ("intake centered on structured
  CSV only" — raw controller dumps now supported); WORKFLOW_SYSTEM.md added to project
  structure section.

- `AI_CONTROL/04_SESSION_HANDOFF.md`: rewritten to reflect current state (batch 3
  complete, WORKFLOW_SYSTEM.md added, 70 tests passing).

- `CLAUDE.md`: WORKFLOW_SYSTEM.md added to optional session-start reads; core principle
  statement and tool-role clarification added to project identity section.

### State at end of session

- 70 tests passing. No code changes. All docs aligned with current repo truth.
- Control layer, README, CLAUDE.md, and WORKFLOW_SYSTEM.md consistent.

---

## 2026-04-23 (validation batch 3 — coord_consistency fix + QA noise suppression)

### Fixed

- `coord_consistency` false positives for non-OSGB grid-derived files. The check
  reprojects lat/lon to EPSG:27700 and compares against declared easting/northing;
  when `_grid_crs` is set to a non-OSGB CRS (TM65 EPSG:29900, ITM EPSG:2157),
  easting/northing are in a different coordinate space and the comparison always
  produces a large apparent mismatch. Any real NIE job would have generated a false
  positive on every pole. Guard added to `run_qa_checks` in `app/qa_engine.py`:
  if `_grid_crs` is present and is not `EPSG:27700`, the `coord_consistency` block
  is skipped entirely. Existing OSGB27700 behaviour unchanged.

### Added

- `filter_rules_for_controller(rules)` in `app/dno_rules.py`. Removes checks that
  produce noise rather than signal for raw controller dump files: `required` and
  `allowed_values` for `material` (absent from the format), `allowed_values` for
  `structure_type` (surveyor feature codes such as Angle, Pol, Hedge are valid but
  do not match schema values), and `dependent_allowed_values` (structure_type →
  material mapping is meaningless when material has no digital representation).
  Meaningful checks preserved: span distance, unique_pair, coordinate bounds, regex,
  required pole_id.

- Filter applied in `app/routes/api_intake.py` finalize route when
  `file_type == "controller"`. Structured CSV path is unchanged.

- 3 new focused tests:
  - `test_coord_consistency_skips_for_non_osgb_grid_crs` — TM65 file with
    `_grid_crs=EPSG:29900` produces no coord_consistency issues.
  - `test_coord_consistency_still_runs_for_explicit_osgb27700_grid_crs` — mismatch
    is still caught when `_grid_crs=EPSG:27700`.
  - `test_import_finalize_controller_dump_suppresses_noise_issues` — end-to-end
    route test confirming no material, structure_type, or coord mismatch issues in
    issues.csv for a TM65 raw dump through NIE_11kV.

### State at end of session

- 70 tests passing (up from 67).
- NIE real jobs no longer produce coord_consistency false positives.
- Controller dump QA output contains only meaningful signal.
- Structured CSV QA path unchanged.

---

## 2026-04-22 (validation batch 2 — raw controller intake + completeness tightening)

### Added

- `is_raw_controller_dump(first_line)` in `app/controller_intake.py`. Detects GNSS
  controller metadata-header format (`Job:X,Version:Y,Units:Z`) by inspecting the
  first line before `pd.read_csv` is called. This format cannot be detected from
  column names after a normal `read_csv` because the metadata row becomes the header.

- `parse_raw_controller_dump(path)` in `app/controller_intake.py`. Parses raw GNSS
  controller dump files using Python's `csv` module (chosen over `pd.read_csv` because
  raw dumps have variable column counts per row that the pandas C parser cannot handle).
  Maps: col 0 → pole_id, col 1 → easting, col 2 → northing, col 4 → structure_type.
  Extracts inline `FeatureCode:HEIGHT` attribute → height and `FeatureCode:REMARK`
  → location. GPS instrument elevation (col 3) is intentionally NOT mapped to height
  since it records terrain elevation, not declared pole height — ensuring the
  completeness summary correctly reports partial height coverage.

- First-line format detection in `app/routes/api_intake.py`. The finalize route now
  peeks at the first line of the uploaded file and routes to `parse_raw_controller_dump`
  before falling through to the existing `pd.read_csv` + `is_controller_csv` path.

- `feature_codes_found` field in `build_completeness_summary` output. Surfaces the
  sorted list of unique structure/feature codes present in the parsed data. For
  controller dumps these are the surveyor-assigned feature codes (Angle, Pol, Hedge,
  EXpole) — the one piece of structural context digitally available. Only included
  when at least one non-null code is present.

- 8 new unit tests in `tests/test_controller_intake.py` covering: `is_raw_controller_dump`
  detection, `parse_raw_controller_dump` record count, PRS/metadata row exclusion,
  HEIGHT attribute vs GPS elevation mapping, REMARK → location mapping, feature code
  → structure_type mapping, numeric column coercion, and `feature_codes_found` in
  completeness summary.

- 1 end-to-end integration test in `tests/test_app_routes.py` (`test_import_finalize_handles_raw_controller_dump`).
  Sends a minimal raw controller dump matching 28-14 513 format through the full `/api/import/<job_id>`
  route and confirms: `ok=True`, `file_type="controller"`, correct per-field completeness,
  `feature_codes_found`, and output files written.

### Validated

- Real-file output simulated via representative test fixture matching job 28-14 513
  format. With the raw parser in place, `build_completeness_summary` would produce:
  total_records=11, height coverage=2/11 (18.2%), location/remarks=2/11 (18.2%),
  material=0/11 (0%), structure_type=11/11 (100%), grid_crs_detected=EPSG:29900,
  feature_codes_found=[Angle, EXpole, Hedge, Pol]. This matches the VALIDATION_ANALYSIS
  intent exactly.

### State at end of session

- 67 tests passing (up from 38).
- Raw GNSS controller dump format now parseable end-to-end.
- Completeness summary surfaces record count, position status, CRS, per-field coverage,
  and feature codes found.
- No changes to QA rules, map output, or PDF generation.

---

## 2026-04-22 (strategic review)

### Added

- `AI_CONTROL/06_STRATEGIC_REVIEW_2026-04-22.md` — distilled strategic conclusions from the external AI review process.

### Changed

- `AI_CONTROL/00_PROJECT_CANONICAL.md` updated to reflect the current phase more accurately and incorporate the new validation-led direction.

- `AI_CONTROL/01_CURRENT_STATE.md` updated to reflect the main unresolved risk: lack of real-world validation.

- `AI_CONTROL/02_CURRENT_TASK.md` rewritten so the next phase is validation-led rather than feature-led.

- `AI_CONTROL/03_WORKING_RULES.md` updated to formally prioritise validation evidence over abstract feature expansion.

- `AI_CONTROL/04_SESSION_HANDOFF.md` updated to record the outcome of the external AI review process.

- `AI_CONTROL/05_PROJECT_REFERENCE.md` updated to document how the external AI review work relates to the live repo without becoming a second truth system.

### State after review

- Project remains active and worth continuing.

- Best current framing remains internal tool / consultancy leverage asset.

- Main next step is testing the current tool on real survey files from real jobs.

- Main unresolved question is now whether the current tool provides meaningful value on real survey files for real users.

---

## 2026-04-22 (Phase 2A)

### Added

- Column name normalisation in `app/routes/api_intake.py`. Headers are now stripped,

  lowercased, and have spaces replaced with underscores before alias mapping runs.

  This handles capitalised exports (`Latitude`, `Structure Type`, `Asset ID`, etc.)

  automatically without any manual reformatting.

- Extended alias lists in `_normalize_dataframe`:
  - `pole_id`: adds `id`, `pole_ref`, `asset_ref`

  - `height`: adds `ht_m`

  - `structure_type`: new — covers `pole_type`, `type`

  - `material`: adds `mat`

  - `location`: adds `site`, `site_name`, `description`

  - `lon`: adds `long`

  - `easting`: new — covers `os_easting`, `grid_easting`, `grid_e`

  - `northing`: new — covers `os_northing`, `grid_northing`, `grid_n`

- Three new tests in `tests/test_api_intake.py`: capitalised headers, common

  abbreviations, OSGB aliases.

### State at end of session

- 38 tests passing.

- Column normalisation handles the most common real-world survey CSV variants.

- No changes to QA engine or rulepacks (Phase 1 closed).

---

## 2026-04-22 (Phase 1 closed)

### Changed

- `AI_CONTROL/02_CURRENT_TASK.md` rewritten: Phase 1 formally closed, Phase 2

  (input schema breadth) defined as the current task.

- `AI_CONTROL/04_SESSION_HANDOFF.md` updated to reflect Phase 1 closure and Phase 2

  entry point.

### State

- Phase 1 complete: 10 QA check types, 4 DNO rulepacks, 35 tests passing.

- Phase 2 next: normalise incoming CSV column names in `app/routes/api_intake.py`.

---

## 2026-04-22 (continued)

### Added

- `ENWL_11KV_RULES` rulepack in `app/dno_rules.py`. Covers Electricity North West

  licence area (Lancashire, Cumbria, Cheshire, Greater Manchester): lat 53.3–55.0,

  lon -3.5 to -1.8. Uses same ENA TS 43-8 height range (7–20m), pole ID regex,

  paired-coord checks, material/structure-type consistency, and coord_consistency

  (100m) as existing rulepacks.

- `ENWL_11kV` entry in `RULEPACKS` dict.

- `unique_pair` check type in `app/qa_engine.py`. Flags rows where two or more poles

  share the same composite field values (applied as lat/lon pair in all DNO rulepacks).

  Skips rows with missing values. Added to all 4 DNO rulepacks.

- `span_distance` check type in `app/qa_engine.py`. Converts consecutive pole lat/lon

  to OSGB27700 and measures distance between adjacent rows. Flags spans below 10m

  (likely duplicate entry) or above 500m (likely GPS error or missing pole). Added to

  all 4 DNO rulepacks.

- Four new tests in `tests/test_qa_engine.py` covering unique_pair and span_distance.

### Fixed

- `test_import_finalize_returns_success_for_valid_job` hardcoded issue count updated

  9→11 to reflect the two additional issues correctly raised by the new rules on the

  existing integration test fixture.

### State at end of session

- 35 tests passing.

- 10 QA check types.

- 4 DNO rulepacks live (`SPEN_11kV`, `SSEN_11kV`, `NIE_11kV`, `ENWL_11kV`).

- Control layer in sync with code.

- CI green.

---

## 2026-04-22

### Added

- Formal `_archive/` structure introduced to separate active project from historical material.

- New `AI_CONTROL/05_PROJECT_REFERENCE.md` created to preserve historical context without bloating operational files.

- Clear three-layer model defined:
  - Active project surface

  - Archive/reference surface

  - Local/tool-specific surface

### Changed

- Repository reorganised to reflect clean separation between:
  - active code and control files

  - historical synthesis and archive material

- `CLAUDE.md` rewritten to align with cleaned control layer and new repo structure.

- `.cursorrules` rewritten to match Claude bootstrap and enforce correct working model.

- `README.md` rewritten to:
  - reflect current MVP state

  - define project structure

  - document active vs archive separation

  - clarify development priorities

### Moved

- `PROJECT_SYNTHESIS/` → `_archive/docs/PROJECT_SYNTHESIS/`

- `RUNBOOK.md` → `_archive/docs/`

- `PROJECT_OPERATING_MODEL.md` → `_archive/docs/`

- `MANIFEST.md` → `_archive/docs/`

- `FRONTEND_FINAL_IMPLEMENTATION.md` → `_archive/docs/`

- AI bundle folders:
  - `CHATGPT_UPLOAD_BUNDLES/`

  - `CLAUDE_APP_UPLOAD_BUNDLES/`

  - `CLAUDE_REVIEW_BUNDLES/`

  → `_archive/ai_bundles/`

### Removed

- Legacy control-layer entry points from active usage:
  - `MASTER_PROJECT_READ_FIRST.md`

  - `AI_CONTROL/00_READ_THIS_FIRST.md`

  - `AI_CONTROL/01_PROJECT_TRUTH.md`

### Fixed

- Eliminated ambiguity between:
  - active instructions

  - historical synthesis

  - archived code

- Prevented future AI/tool drift by enforcing single authoritative control layer.

### State at end of session

- Clean repository structure established.

- Control layer fully aligned with project direction.

- Archive separated and safe from accidental use.

- Claude + Cursor environments aligned with new structure.

- Project ready for focused Phase 1 work (QA rule improvements).

---

## 2026-04-21

### Added

- `NIE_11KV_RULES` rulepack in `app/dno_rules.py`. Uses ENA TS 43-8 height range (7–20m), pole ID regex, paired-coord checks, material/structure-type consistency, and `coord_consistency` (100m). Network bounds: Northern Ireland lat 54.0–55.3, lon -8.2 to -5.4 — single contiguous licence area, no disjoint-zone caveat.

- `NIE_11kV` entry in `RULEPACKS` dict.

- Two new tests in `tests/test_qa_engine.py`: registration check + valid NIE pole (realistic Belfast coords) passes.

- `PROJECT_OPERATING_MODEL.md` — plain-English guide to how the project is organised, who does what, and how sessions run.

### Changed

- `AI_CONTROL/00_MASTER_SOURCE_OF_TRUTH.md`: §4 updated to reflect NIE live and 29 tests; §5 priority list updated; §6 Claude app role clarified as "primary implementation tool and control-layer custodian"; §7 hard rule 9 added (never close a session without updating handoff + changelog); §9 file map updated to include `PROJECT_OPERATING_MODEL.md`.

- `AI_CONTROL/03_CURRENT_TASK.md`: Rewritten — next task is `ENWL_11kV`.

- `AI_CONTROL/04_SESSION_HANDOFF.md`: Rewritten to record this session.

### State at end of session

- 29 tests passing.

- 8 QA check types.

- 3 DNO rulepacks live (`SPEN_11kV`, `SSEN_11kV`, `NIE_11kV`).

- Control layer in sync with code.

- CI green.

---

## 2026-04-20 (continued)

### Added

- `SSEN_11KV_RULES` rulepack in `app/dno_rules.py`. Uses same ENA TS 43-8 height range (7–20m), pole ID regex, paired-coord checks, material/structure-type consistency, and `coord_consistency` (100m) as SPEN. Network bounds cover combined SEPD (southern England) + SHEPD (northern Scotland) licence areas: lat 50.0–60.9, lon -7.5 to +1.8. Documented `TODO` to tighten with polygon check — current bounds pass coordinates in non-SSEN areas between the two zones but still catch grossly wrong coordinates.

- `SSEN_11kV` entry in `RULEPACKS` dict.

- Two new tests in `tests/test_qa_engine.py`: registration check + valid SSEN pole (realistic Inverness coords) passes.

### Triaged

- Dismissed 9 Dependabot alerts (1 high geopandas, 6 moderate Werkzeug, 2 low Flask) as "vulnerable code not actually used". Tool runs locally on macOS with no PostGIS connection, no caching proxy, and no Werkzeug file-serving path — none of the CVE prerequisites apply.

### State at end of session

- 27 tests passing.

- 2 DNO rulepacks live (`SPEN_11kV`, `SSEN_11kV`).

- CI green.

- 0 open Dependabot alerts.

---

## 2026-04-20

### Added

- `coord_consistency` QA check type in `app/qa_engine.py`. Converts lat/lon to OSGB27700 via pyproj and measures distance against declared easting/northing. Configurable tolerance (default 100m). Rows with any missing coordinate values are skipped.

- `coord_consistency` rule in `SPEN_11KV_RULES` with 100m tolerance.

- Two new tests in `tests/test_qa_engine.py` covering the new check (matching and mismatched coordinate cases).

- `.github/dependabot.yml` — weekly Dependabot updates for pip + github-actions.

- `CHANGELOG.md` — this file.

- `pytest-cov` added to dev dependencies for coverage reporting (`pytest --cov=app`).

### Changed

- `app/qa_engine.py` refactored into a clean single if/elif chain. Checks that operate on multiple fields are now grouped separately from checks that operate on a single `field` key.

- Control layer consolidated:
  - `AI_CONTROL/00_MASTER_SOURCE_OF_TRUTH.md` rewritten as the single primary authority. Absorbed tool roles and hard rules from the deleted `05_AI_ROLE_RULES.md`. Added §10 "how to update this file" checklist.

  - `AI_CONTROL/02_CURRENT_STATE.md` aggressively slimmed — duplicated counts and priorities removed; only technical detail retained.

  - `AI_CONTROL/03_CURRENT_TASK.md` rewritten for post-coord_consistency state; next task is `SSEN_11kV` rulepack.

  - `AI_CONTROL/04_SESSION_HANDOFF.md` rewritten to record this session's work.

  - `AI_CONTROL/06_DEVELOPMENT_PROCESS.md` slimmed — dropped sections that duplicated master truth; kept genuinely process-only content.

  - `CLAUDE.md` and `.cursorrules` slimmed — removed hard-coded counts that drift. Now reference master truth for changing facts.

### Removed

- `MASTER_PROJECT_READ_FIRST.md` (root). Redundant pointer.

- `AI_CONTROL/00_READ_THIS_FIRST.md`. Legacy pointer superseded by master truth.

- `AI_CONTROL/01_PROJECT_TRUTH.md`. Still used old "SpanCore" identity; content absorbed into master truth §1.

- `AI_CONTROL/05_AI_ROLE_RULES.md`. Content absorbed into master truth §6.

### State at end of session

- 25 tests passing.

- 8 QA check types.

- SPEN_11kV is the only live rulepack.

- Control layer reduced from 9 files to 5 active + 2 tool bootstraps + this changelog.

- CI green.

---

## Earlier history

Earlier sessions are summarised in `AI_CONTROL/04_SESSION_HANDOFF.md` and

`_archive/docs/PROJECT_SYNTHESIS/`.

This file starts at 2026-04-20.
