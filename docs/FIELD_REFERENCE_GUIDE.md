# GridFlow Field Reference Guide

This guide is the authoritative reference for **what each per-pole field
in GridFlow actually means** and **where it comes from**. It is grounded
in the C2E2 Field Reality Audit ([AI_CONTROL/31_REAL_JOB_FIELD_REALITY_REPORT.md](../AI_CONTROL/31_REAL_JOB_FIELD_REALITY_REPORT.md)),
the C2E2 popup spec ([AI_CONTROL/11_C2E2_POPUP_EXPANSION_SPEC.md](../AI_CONTROL/11_C2E2_POPUP_EXPANSION_SPEC.md)),
and the live schema modules `app/field_reference.py` and
`app/structured_capture_schema.py`.

## Truth Categories

Every field belongs to exactly one of four categories. Future code
changes must preserve this separation — designers downstream rely on the
distinction between *captured*, *derived*, and *not-yet-implemented*.

| Category | Meaning | Where to find it |
|---|---|---|
| **Trimble / survey export** | Recorded by the surveyor on the controller. Real-world evidence. | `parse_raw_controller_dump()` in `app/controller_intake.py` |
| **GridFlow-derived** | Produced by GridFlow's pipeline (sequencer, QA engine, replacement-pair detection). | `process_job()` in `app/routes/api_intake.py`, plus `app/qa_engine.py` |
| **Stage 4 structured capture** | Future structured input. Not collected today. | `app/structured_capture_schema.py` |
| **Not truthful today** | Theoretical fields that must NOT be shown as captured until Stage 4 integration lands. | this document |

---

## 1. Current Trimble / Survey Export Fields

These are the only six fields the parser extracts from a real Trimble
controller dump:

| Field | Source in CSV | Always present? | Notes |
|---|---|---|---|
| `pole_id` | column 0 (survey point number) | yes | identity primary key |
| `easting` | column 1 | yes | OSGB / Irish Grid; CRS auto-detected |
| `northing` | column 2 | yes | OSGB / Irish Grid; CRS auto-detected |
| `height` | `CODE:HEIGHT` attribute pair | **partial — by design** | see below |
| `structure_type` | column 4 (feature code) | almost always | `Pol`, `EXpole`, `PRpole`, `Angle`, `Stay`, `T2`, `T1`, etc. |
| `location` (a.k.a. `name`, `remarks`) | `CODE:REMARK` attribute pair | partial | surveyor free-text — pole names, crossing notes, etc. |

### `height` is partial by design

The audit confirmed:

| File | Height present % |
|---|---|
| Gordon Pt1 (157 records) | 29% |
| 2814_474c (91) | 21% |
| 2814_4-474 (83) | 27% |
| 28-14_513 (11) | 18% |
| Bellsprings (57) | 33% |

Height is **only** recorded for key features:

- **`Pol`** (intermediate poles) → height absent is expected practice.
  Display "Not measured" or omit the field. **Never** display "Unknown"
  here.
- **`EXpole`** (existing pole being replaced) → height absent **is** a
  design risk. Surface it as a review item, not silent missing data.
- **`Angle`**, strain structures, `T2` crossing heights → height absent
  is also a review item.

### `material` is not in current Trimble format

`material` is not a Trimble attribute. The GeoJSON property exists
(some upload paths copy it from aliases) but it is **always None for
Trimble jobs**. The popup must label it `Not recorded in survey`
rather than blank.

### Discarded but extractable

- **`CODE:LAND USE`** (e.g. `PASTURE`) is currently parsed-and-discarded.
  Could be surfaced with a parser change.
- **GPS elevation** in column 3 is intentionally excluded — it is
  terrain elevation, not pole height.
- **`CODE:STRING`** / **`CODE:TAG`** are not currently used.

### Aliases

`app/field_reference.py` resolves common alternative column names. See
[API_REFERENCE.md](API_REFERENCE.md#fieldreferencepy) for `resolve_alias()`,
`get_field_definition()`, and `get_display_label()`.

---

## 2. GridFlow-Derived Fields

These appear on the GeoJSON feature `properties` after the full pipeline
runs. They are computed — never claim they were measured by the surveyor.

| Field | Producer | Always present? | Purpose |
|---|---|---|---|
| `asset_intent` | `controller_intake._classify_role()` + structure-type rules | when classifiable | "structural", "context", etc. |
| `relationship` | replacement-pair sequencer | only on paired EXpole/PRpole | which pole replaces which |
| `record_role` | `classify_record_roles()` | always | structural / context / anchor |
| `qa_status` | `qa_engine.run_qa_checks()` | always | `PASS` / `WARN` / `FAIL` |
| `issue_count` | QA aggregator | always | number of FAIL items |
| `warn_count` | QA aggregator | always | number of WARN items |
| `issue_texts` | QA aggregator | always (may be empty list) | human-readable FAIL strings |
| `warn_texts` | QA aggregator | always (may be empty list) | human-readable WARN strings |
| `being_replaced_by` / `replacing` | replacement-pair sequencer | on matched pairs | per-pole lifecycle relationship |
| `stay_evidence_status` | QA engine, derived from nearby Stay records | when computable | indirect evidence a stay exists |
| `geometry_trust` | `qa_engine.classify_source_confidence()` | always | `high` / `medium` / `low` per-feature confidence label |

### Important rule

> Derived ≠ field-captured.

Anything in this section is GridFlow inferring from what the surveyor
did record. Do not present these as "captured by survey" in popups,
reports, or PDFs. The popup deliberately uses different label wording
for these.

---

## 3. Stage 4 Structured Capture Fields

Defined in `app/structured_capture_schema.py`. Every field carries:

```
current_status: "stage4_future_capture"
source: "structured_capture"
```

These fields are **not collected today**. Validators and a CSV template
generator exist; nothing is wired into the upload, QA, or popup flow.
See [STAGE4_STRUCTURED_CAPTURE.md](STAGE4_STRUCTURED_CAPTURE.md) for the
full rationale.

### Pole specification

| Field | Type | Allowed values |
|---|---|---|
| `pole_class` | string | free text (light / medium / heavy / DNO code) |
| `pole_strength` | string | free text |
| `pole_material` | enum | `wood` / `concrete` / `steel` / `composite` / `unknown` |
| `specification` | string | free text |

### Condition / defects

| Field | Type | Allowed values |
|---|---|---|
| `condition` | enum | `good` / `fair` / `poor` / `unsafe` / `unknown` |
| `defect_type` | string | free text (rot / split / lean / woodpecker / corrosion) |
| `defect_severity` | enum | `low` / `medium` / `high` / `critical` / `unknown` |
| `defect_notes` | string | free text |

### Electrical / conductor

| Field | Type | Allowed values |
|---|---|---|
| `voltage_carried` | enum | `LV` / `11kV` / `33kV` / `110kV` / `unknown` |
| `conductor_type` | enum | `bare` / `covered` / `abc` / `underground` / `unknown` |
| `conductor_size` | string | free text (mm² or DNO code) |
| `phase_configuration` | enum | `single` / `three` / `split` / `unknown` |

### Structural support

| Field | Type | Allowed values |
|---|---|---|
| `stay_present` | boolean_enum | `yes` / `no` / `unknown` |
| `stay_type` | enum | `down` / `flying` / `strut` / `none` / `unknown` |
| `stay_condition` | enum | `good` / `fair` / `poor` / `unsafe` / `unknown` |
| `lean_direction` | enum | `none` / `north` / `south` / `east` / `west` / `unknown` |
| `lean_severity` | enum | `none` / `slight` / `moderate` / `severe` / `unknown` |

### Equipment / pole-top

| Field | Type | Allowed values |
|---|---|---|
| `equipment_present` | boolean_enum | `yes` / `no` / `unknown` |
| `equipment_type` | enum | `transformer` / `switchgear` / `regulator` / `recloser` / `fuse` / `isolator` / `none` / `unknown` |
| `equipment_condition` | enum | `good` / `fair` / `poor` / `unsafe` / `unknown` |
| `equipment_notes` | string | free text |

### Capture metadata (the only **required** Stage 4 fields)

| Field | Type | Allowed values |
|---|---|---|
| `capture_source` | enum (required) | `surveyor_tablet` / `surveyor_paper` / `office_audit` / `designer_input` / `historical_record` / `unknown` |
| `captured_by` | string (required) | free text |
| `capture_date` | date (required) | ISO 8601 `YYYY-MM-DD` |
| `confidence_level` | enum | `high` / `medium` / `low` / `unknown` |
| `verification_required` | boolean_enum | `yes` / `no` / `unknown` |

---

## 4. Fields Explicitly Not Truthful Today

The following must **not** be displayed as captured survey values until
Stage 4 integration is built:

- pole class
- pole strength / pole specification
- condition
- defect type, defect severity
- voltage carried
- conductor type, conductor size, phase configuration
- stay type, stay condition, lean direction, lean severity
- equipment type, equipment condition

If your code path needs to surface any of these, do one of:

1. Show the schema label with the wording **"Not recorded in survey"**
   (or **"Not measured"** for `Pol` height).
2. Hide the row entirely.
3. Wait for Stage 4 integration so the value can be sourced from a
   structured capture row.

Inventing a value is the failure mode this guide exists to prevent.

---

## Helper Functions

### Trimble / GridFlow-derived field metadata

`app/field_reference.py`:

- `get_field_definition(name)` → dict with label, group, aliases, missing-value wording
- `get_display_label(name)` → human-friendly label string
- `get_missing_wording(name, structure_type=None)` → context-aware "missing" text (e.g. "Not measured" for Pol height vs "Not recorded in survey" for material)
- `resolve_alias(column_name)` → canonical field name or None
- `get_field_unit(name)` → unit string or None
- `get_fields_for_group(group)` → list of canonical field names

### Field display + truthfulness

`app/field_validators.py`:

- `is_measured(value)` → True if value is real measurement evidence
- `is_missing_legitimate(field, structure_type, value)` → True if the missing value is *expected* (e.g. Pol with no height)
- `validate_field_value(...)` / `validate_height_value(...)` → return validation results
- `format_field_display(...)` / `get_popup_display_value(...)` → final label + value pair the popup should render
- `classify_field_completeness(...)` → completeness category for the field

### Stage 4 schema + validators

`app/structured_capture_schema.py`:

- `get_stage4_field_definition(name)` → dict (resolves aliases)
- `get_stage4_fields()` / `get_stage4_fields_by_group(group)` / `get_stage4_required_fields()` / `get_stage4_template_headers()`
- `is_stage4_field(name)` → bool

`app/structured_capture_validators.py`:

- `is_blank(value)` / `normalise_bool(value)`
- `validate_allowed_value(field, value)` / `validate_required_fields(row)`
- `validate_stage4_row(row)` / `validate_stage4_rows(rows)`
- `classify_stage4_completeness(row)` → `empty` / `partial` / `minimum` / `complete`
- `normalise_stage4_row(row)` → row with values normalised

---

## Cross-References

- [ARCHITECTURE.md](ARCHITECTURE.md) — where each module sits in the pipeline.
- [API_REFERENCE.md](API_REFERENCE.md) — function signatures and side effects.
- [STAGE4_STRUCTURED_CAPTURE.md](STAGE4_STRUCTURED_CAPTURE.md) — Stage 4 rationale and integration plan.
- [STRUCTURED_CAPTURE_TEMPLATE_GUIDE.md](STRUCTURED_CAPTURE_TEMPLATE_GUIDE.md) — how to fill the Stage 4 template.
- [AI_CONTROL/31_REAL_JOB_FIELD_REALITY_REPORT.md](../AI_CONTROL/31_REAL_JOB_FIELD_REALITY_REPORT.md) — the underlying audit data.
