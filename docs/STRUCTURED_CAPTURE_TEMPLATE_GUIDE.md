# Stage 4 Structured Capture — Template Guide

This guide explains how to generate the Stage 4 structured-capture CSV
template, how to fill it in, and how the validators interpret each value.
The template itself is **not yet wired into any GridFlow upload route** —
see [STAGE4_STRUCTURED_CAPTURE.md](STAGE4_STRUCTURED_CAPTURE.md) for the
full context.

## Generating the Template

From the repository root:

```bash
# Default: writes templates/structured_capture_template.csv
python scripts/generate_structured_capture_template.py

# Custom output path
python scripts/generate_structured_capture_template.py \
  --output /tmp/stage4_template.csv

# Include descriptive comment header rows
python scripts/generate_structured_capture_template.py \
  --include-descriptions

# Print to stdout (useful for piping)
python scripts/generate_structured_capture_template.py --stdout
```

The script depends only on the Python standard library and the schema
module. It does **not** start the Flask app and is safe to re-run; each
invocation overwrites the target file with the current schema.

## Filling It In

Each row in the CSV represents the structured-capture record for **one
pole**, keyed against the existing GridFlow `pole_id`.

### Required Fields

| Field | Notes |
|---|---|
| `capture_source` | Where the row came from. Allowed: `surveyor_tablet`, `surveyor_paper`, `office_audit`, `designer_input`, `historical_record`, `unknown`. |
| `captured_by` | Free-text name or identifier of the capturer. |
| `capture_date` | ISO 8601 date `YYYY-MM-DD`. |

A row missing any required field is rejected by `validate_stage4_row`.

### Optional Fields by Group

#### Pole specification

| Field | Allowed values |
|---|---|
| `pole_class` | free text |
| `pole_strength` | free text |
| `pole_material` | `wood` / `concrete` / `steel` / `composite` / `unknown` |
| `specification` | free text |

#### Condition / defects

| Field | Allowed values |
|---|---|
| `condition` | `good` / `fair` / `poor` / `unsafe` / `unknown` |
| `defect_type` | free text |
| `defect_severity` | `low` / `medium` / `high` / `critical` / `unknown` |
| `defect_notes` | free text |

#### Electrical / conductor

| Field | Allowed values |
|---|---|
| `voltage_carried` | `LV` / `11kV` / `33kV` / `110kV` / `unknown` |
| `conductor_type` | `bare` / `covered` / `abc` / `underground` / `unknown` |
| `conductor_size` | free text (mm² or DNO size code) |
| `phase_configuration` | `single` / `three` / `split` / `unknown` |

#### Structural support

| Field | Allowed values |
|---|---|
| `stay_present` | `yes` / `no` / `unknown` |
| `stay_type` | `down` / `flying` / `strut` / `none` / `unknown` |
| `stay_condition` | `good` / `fair` / `poor` / `unsafe` / `unknown` |
| `lean_direction` | `none` / `north` / `south` / `east` / `west` / `unknown` |
| `lean_severity` | `none` / `slight` / `moderate` / `severe` / `unknown` |

#### Equipment / pole-top

| Field | Allowed values |
|---|---|
| `equipment_present` | `yes` / `no` / `unknown` |
| `equipment_type` | `transformer` / `switchgear` / `regulator` / `recloser` / `fuse` / `isolator` / `none` / `unknown` |
| `equipment_condition` | `good` / `fair` / `poor` / `unsafe` / `unknown` |
| `equipment_notes` | free text |

#### Capture metadata

| Field | Allowed values |
|---|---|
| `capture_source` | required (see above) |
| `captured_by` | required |
| `capture_date` | required ISO date |
| `confidence_level` | `high` / `medium` / `low` / `unknown` |
| `verification_required` | `yes` / `no` / `unknown` |

## How Blank, Unknown, and Not Applicable Are Interpreted

The validator treats these tokens as "blank" (case-insensitive):

```
"" "n/a" "na" "none" "null" "tbc" "?"
```

Practical consequences:

- **Blank** in an enum field is **valid**; it means "not captured for this
  row" rather than "captured as zero". Required fields still fail when
  blank.
- **`unknown`** is a *captured* value — it tells the designer the
  surveyor looked but could not assess. This is different from blank.
- **`none`** is reserved for fields where "no such item exists" is a
  meaningful answer (e.g. `equipment_type: none` = nothing on the pole).

When the spec is intentionally unobservable from the ground, prefer
`unknown` plus a `defect_notes` / `equipment_notes` explanation over
inventing a value.

## Examples

### Minimum Valid Row

```csv
capture_source,captured_by,capture_date
office_audit,N. Collins,2026-05-09
```

This row passes validation (all required fields filled) but
`classify_stage4_completeness` returns `minimum` — useful as a placeholder,
not yet evidence-bearing.

### Substantive Designer-Input Row

```csv
pole_class,pole_material,condition,defect_type,defect_severity,voltage_carried,conductor_type,phase_configuration,stay_present,stay_type,equipment_present,capture_source,captured_by,capture_date,confidence_level,verification_required
medium,wood,fair,split,medium,11kV,covered,three,yes,down,no,office_audit,N. Collins,2026-05-09,medium,no
```

`classify_stage4_completeness` returns `complete` for this row.

## How This Supports Surveyors and Designers

- Surveyors can pre-fill obvious values (presence flags, condition) on
  site without paper forms.
- Designers can complete or correct values from the office before
  PoleCAD work begins.
- Capture metadata makes the source visible everywhere downstream so a
  popup or report can label "captured by" and "captured on" rather than
  attributing structured values to the original Trimble file.
