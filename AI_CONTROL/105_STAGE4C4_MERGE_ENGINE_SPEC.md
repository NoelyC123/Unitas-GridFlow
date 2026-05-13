# Stage 4C.4: Merge Engine Technical Specification

## Purpose

The merge engine combines:

- `BaselineDataset` from Stage 4C.1
- `FieldDataset` from Stage 4C.2
- `MatchRegister` from Stage 4C.3

into a single unified `MergedDataset` ready for designer review.

The merge engine does not produce final engineering design. It combines evidence, preserves provenance, generates verification flags, and identifies design blockers.

## What the Merge Engine Produces

For each matched pole, produce a `MergedPole` record.

### FROM BASELINE (authoritative)

- `pole_id`
- `support_no` (normalized)
- `easting`, `northing` (OSGB36)
- `latitude`, `longitude` (WGS84)
- `route_id`, `pole_sequence`
- `baseline_voltage` (if available, else null)
- `baseline_asset_type`
- `baseline_status`

### FROM FIELD (current condition)

- `condition_overall`
- `condition_base`
- `condition_top`
- `defects` (list)
- `lean_present`, `lean_direction`, `lean_severity`
- `access_constraints`
- `equipment_observed` (list)
- `warning_signs_present`
- `stay_present`
- `field_photo_count`
- `photo_paths`
- `notes_content`
- `survey_date` (from file metadata where available)

### COMPUTED BY MERGE ENGINE

- `match_confidence` (from `MatchRegister`)
- `match_type` (`EXACT`, `VARIANT`, `UNMATCHED`)
- `identity_verified` (true if HIGH confidence)
- `review_required` (true if MEDIUM/LOW confidence)
- `conflict_flags` (from matching engine / conflict detector)

### VERIFICATION FLAGS (computed)

- `voltage_verification_required`: true if `baseline_voltage` is null
- `conductor_verification_required`: always true unless authoritative conductor data is present in baseline
- `pole_class_verification_required`: always true unless authoritative pole class is present in baseline
- `condition_verification_required`: true if severe defects observed
- `identity_verification_required`: true if `match_confidence != HIGH`
- `equipment_conflict_flag`: true if field equipment contradicts baseline

### DESIGN STATUS

- `design_blocked`: true if any required verification flag is set
- `design_ready`: true if HIGH confidence and no design blockers
- `designer_action_required`: list of specific actions needed

## MergedDataset Structure

`MergedDataset` fields:

- `baseline_source`: str (CSV filename)
- `field_source`: str (folder path)
- `merge_date`: str
- `total_poles_baseline`: int
- `total_poles_field`: int
- `total_matched`: int
- `total_unmatched_baseline`: int (not surveyed)
- `total_unmatched_field`: int (extra poles)
- `design_ready_count`: int
- `design_blocked_count`: int
- `review_required_count`: int
- `poles`: list[`MergedPole`]
- `unmatched_baseline`: list[`BaselinePole`]
- `unmatched_field`: list[`FieldPole`]

## QA Report Structure

The merge engine generates a QA report containing:

### SUMMARY SECTION

- Total poles in baseline
- Total poles surveyed
- Match rate
- Design ready vs design blocked breakdown
- Verification flag counts by type

### PER-POLE TABLE

```text
support_no | match_confidence | design_ready | voltage_flag | conductor_flag | pole_class_flag | condition_flag | identity_flag | actions_required
```

### DESIGN BLOCKERS SECTION

List all poles that cannot proceed to design, with specific reasons.

### UNMATCHED POLES SECTION

- Baseline poles not surveyed (need field visit)
- Field poles not in baseline (investigate: possible unlisted assets or evidence-folder error)

### ACTION ITEMS SECTION

Prioritised list of actions needed before design can proceed.

## Merge Logic (Detailed)

### Identity Resolution

1. Use baseline `support_no` as primary identifier (authoritative).
2. Use baseline coordinates (survey-grade where source provides that quality), not field GPS.
3. If `VARIANT_SUPPORT_NO`: flag for manual identity confirmation.
4. If `UNMATCHED`: create unmatched record and flag for investigation.

### Condition Data

1. Field observation is primary source for current visual condition.
2. Parse notes for `condition_overall`, `condition_base`, `condition_top`, and `defects`.
3. If notes are unparsed: use raw `notes_content` and flag for manual extraction.
4. No DNO inspection history is available in P_LOCAL_001 context.

### Voltage Determination

Field-observed voltage is not authoritative for design.

Logic:

```text
IF baseline_voltage is not null:
    authoritative_voltage = baseline_voltage
    voltage_confidence = HIGH
    voltage_verification_required = false
ELSE IF field notes say voltage:
    observed_voltage = notes voltage
    voltage_confidence = LOW
    voltage_verification_required = true
ELSE:
    authoritative_voltage = UNKNOWN
    voltage_confidence = NONE
    voltage_verification_required = true
```

### Equipment Conflict Detection

```text
IF baseline asset_type contradicts field equipment_observed:
    equipment_conflict_flag = true
    conflict_detail = specific discrepancy description
```

Example:

- Baseline says `POLE` but field observes transformer equipment -> flag conflict.

Do not treat a broad baseline type (`POLE`) as a contradiction if field evidence simply adds visible accessories that the baseline did not enumerate. Only flag true contradictions or missing critical expected equipment.

### Design Status Computation

```text
design_blocked = (
    voltage_verification_required OR
    conductor_verification_required OR
    pole_class_verification_required OR
    identity_verification_required OR
    condition_verification_required
)
```

In P_LOCAL_001 context, all poles are expected to be `design_blocked = true` because DNO engineering specs have not yet been obtained. This is correct behaviour. The merge engine documents what is needed; it does not certify design readiness.

## Module Structure to Implement

### `gridflow/merge/__init__.py`

Export:

- `DataMerger`
- `VerificationFlagGenerator`
- `QAReportGenerator`
- `ConflictDetector`
- `MergedPole`
- `MergedDataset`

### `gridflow/merge/models.py`

Define Pydantic v2 models using `ConfigDict`.

#### `MergedPole`

Required fields:

- Baseline fields listed above
- Field fields listed above
- Computed match fields
- Verification flags
- Design status fields
- `metadata`: dict for extensibility

#### `MergedDataset`

Required fields:

- Summary/source fields listed above
- `poles`
- `unmatched_baseline`
- `unmatched_field`
- `metadata`

### `gridflow/merge/data_merger.py`

`DataMerger` class:

- `merge(baseline: BaselineDataset, field: FieldDataset, register: MatchRegister) -> MergedDataset`
- `_merge_pole(baseline_pole, field_pole, match_result) -> MergedPole`
- `_extract_condition(field_pole) -> dict`
- `_determine_design_status(merged_pole) -> dict`

Implementation notes:

- Build lookup indexes by normalized `support_no`.
- Preserve original support number and normalized support number where available.
- Do not discard unmatched baseline or field records.
- Never infer engineering values from field notes/photos.
- Preserve raw notes content for designer review.

### `gridflow/merge/verification_flag_generator.py`

`VerificationFlagGenerator` class:

- `generate_flags(merged_pole: MergedPole) -> dict`
- `_check_voltage_verification(merged_pole) -> bool`
- `_check_conductor_verification(merged_pole) -> bool`
- `_check_pole_class_verification(merged_pole) -> bool`
- `_check_condition_verification(merged_pole) -> bool`
- `_check_identity_verification(merged_pole) -> bool`
- `_detect_equipment_conflict(merged_pole) -> bool`

Rules:

- Voltage flag is false only when authoritative baseline voltage exists.
- Conductor flag is false only when authoritative baseline conductor specification exists.
- Pole class flag is false only when authoritative baseline pole class exists.
- Condition flag is true for severe defects or notes indicating urgent inspection.
- Identity flag is true for anything other than HIGH confidence.

### `gridflow/merge/qa_report_generator.py`

`QAReportGenerator` class:

- `generate(dataset: MergedDataset) -> str` (markdown report)
- `generate_summary(dataset) -> str`
- `generate_pole_table(dataset) -> str`
- `generate_design_blockers(dataset) -> str`
- `generate_unmatched_section(dataset) -> str`
- `generate_action_items(dataset) -> str`

Report requirements:

- Explain that design blockers are expected when DNO engineering data is missing.
- Avoid implying that `design_ready` means DNO-approved.
- Make action items specific enough for a designer/project lead.

### `gridflow/merge/conflict_detector.py`

`ConflictDetector` class:

- `detect(baseline_pole, field_pole) -> list[str]`
- `_check_voltage_conflict(baseline_pole, field_pole) -> str | None`
- `_check_equipment_conflict(baseline_pole, field_pole) -> str | None`
- `_check_support_no_conflict(baseline_pole, field_pole) -> str | None`

Conflict examples:

- Baseline support number differs from field folder support number after normalization.
- Baseline voltage category says LV but field notes repeatedly describe HV transformer evidence, or vice versa.
- Baseline expected transformer but field notes/photos identify no transformer and photo coverage is sufficient.

### `scripts/run_merge.py`

CLI tool:

```bash
python scripts/run_merge.py \
  --baseline path/to/baseline_dataset.json \
  --field path/to/field_dataset.json \
  --register path/to/match_register.json \
  --output path/to/merged_dataset.json \
  --report path/to/qa_report.md \
  --csv path/to/per_pole_summary.csv
```

Arguments:

- `--baseline`: BaselineDataset JSON path
- `--field`: FieldDataset JSON path
- `--register`: MatchRegister JSON path
- `--output`: MergedDataset JSON output path
- `--report`: QA report markdown path
- `--csv`: Export per-pole summary CSV

CLI behaviour:

- Load all three inputs.
- Validate required schema keys.
- Run merge.
- Write JSON, markdown report, and optional CSV.
- Exit non-zero if inputs cannot be parsed or merge fails.
- Do not write to live job outputs.

## Test Requirements

Create `tests/merge/` with full pytest suite:

- `test_data_merger.py`: merge logic, condition extraction, design status
- `test_verification_flag_generator.py`: all flag types, edge cases
- `test_qa_report_generator.py`: report structure, content accuracy
- `test_conflict_detector.py`: voltage/equipment/support conflicts

Minimum test scenarios:

- HIGH confidence exact match produces merged pole.
- MEDIUM confidence match sets `review_required` and `identity_verification_required`.
- Missing baseline voltage sets `voltage_verification_required`.
- Missing conductor spec sets `conductor_verification_required`.
- Missing pole class sets `pole_class_verification_required`.
- Severe defect note sets `condition_verification_required`.
- Equipment contradiction sets `equipment_conflict_flag`.
- Unmatched baseline pole appears in `unmatched_baseline`.
- Unmatched field pole appears in `unmatched_field`.
- QA report includes summary, per-pole table, design blockers, unmatched sections, and action items.
- CLI writes JSON/report/CSV without touching live job outputs.

## Expected P_LOCAL_001 Merge Results

When run against P_LOCAL_001:

- 10 poles merged (assuming ENWL sample/baseline CSV as baseline)
- 10 poles matched (100% identity match rate)
- 0 unmatched baseline, 0 unmatched field
- All 10 poles: `design_blocked = true` because DNO engineering specs are not yet obtained
- All 10 poles: `voltage_verification_required = true` if baseline voltage is not authoritative in the input
- All 10 poles: `conductor_verification_required = true` unless authoritative conductor spec is present in baseline
- All 10 poles: `pole_class_verification_required = true` unless authoritative pole class is present in baseline
- Pole 08 may require `identity_verification_required = true` if represented as MEDIUM confidence due to `NO_POLE_POPUP`
- 0 poles: `condition_verification_required` unless severe defects are explicitly parsed from notes

This is correct and expected. The QA report must identify what the designer needs to obtain from ENWL/DNO records before final design proceeds.

## Acceptance Criteria

Stage 4C.4 is complete when:

- `DataMerger` produces `MergedDataset` from all three inputs.
- All verification flags are correctly generated.
- QA report clearly identifies design blockers.
- Designer action items are specific and actionable.
- All tests pass with >=80% coverage for the merge package.
- CLI runs end-to-end on P_LOCAL_001-style data.
- Output confirms P_LOCAL_001 poles are design-blocked where DNO engineering specifications are missing.
- Runtime/app UI remains unchanged unless a later task explicitly authorizes integration.
