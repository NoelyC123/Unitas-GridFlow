# C2E2 Pre-Implementation Guide

## Purpose

This guide defines everything Cursor needs before writing popup rendering code.
It is grounded in the real-job field audit (31_REAL_JOB_FIELD_REALITY_REPORT.md)
and uses the modules in `app/field_reference.py` and `app/field_validators.py`.

Do not modify `app/routes/map_preview.py`, `app/static/js/map-viewer.js`, or
any backend processing files without reading this guide first.

---

## Selected Fields for C2E2 Popup Expansion

### Tier 1 — Improve display of existing GeoJSON properties

These fields are already in every feature's `properties` dict. The goal is to
improve how they are displayed (better labels, missing-value wording, grouping).

| Field | Current label | Proposed label | Notes |
|-------|--------------|----------------|-------|
| `pole_id` | shown as heading | Point ID | No change needed |
| `structure_type` | Feature Code | Feature Code | Show in identity group |
| `asset_intent` | Asset Intent | Asset Intent | "Not classified" when None |
| `height` | Height | Measured Height | Conditional wording by structure_type |
| `qa_status` | Status | QA Status | Already shown |
| `name` | (popup title) | Survey Note | Show as a field, not just title |

### Tier 2 — Surface derived fields not yet in popup

These exist in the processed data but are not displayed in the current popup.

| Field | Source | Display rule |
|-------|--------|-------------|
| `record_role` | derived | Show as badge: structural / context |
| `relationship` | derived | Show only when non-null: "Replacement pair" |
| `being_replaced_by` | from sequencer JSON | Show for EXpole when present |
| `replacing` | from sequencer JSON | Show for PRpole/Angle when present |

### Tier 3 — Show with "Not recorded" label

These fields are defined in the schema but absent from all Trimble jobs.

| Field | Label | Display rule |
|-------|-------|-------------|
| `material` | Material | Show "Not recorded in survey" — never blank |

### Do NOT add to popup

The following have no available data and no legitimate "not recorded" display:
- `conductor_type`, `voltage_carried`, `phase_configuration`
- `defect_type`, `defect_severity`, `condition`
- `lean_direction`, `equipment_type`
- `pole_class`, `specification`

---

## Field Groups

Use `POPUP_FIELD_GROUPS` from `app/field_reference.py` for popup layout:

```python
from app.field_reference import POPUP_FIELD_GROUPS, POPUP_GROUP_ORDER
```

Render groups in `POPUP_GROUP_ORDER` sequence:
1. **identity** — `pole_id`, `structure_type`, `asset_intent`, `record_role`
2. **geometry** — `easting`, `northing`, `height`
3. **quality** — `qa_status`, `issue_count`, `warn_count`
4. **survey_context** — `name`, `material`, `land_use`
5. **relationship** — `relationship`, `being_replaced_by`, `replacing`

---

## Missing-Value Rules

**Never show a blank cell.** Always show the appropriate wording from
`get_missing_wording(field_name, structure_type)`.

Critical distinctions:

| Situation | Display |
|-----------|---------|
| `height` on `Pol` | "Not measured (intermediate pole)" |
| `height` on `EXpole` | "Not measured — check survey notes" |
| `height` on `Angle` | "Not measured — check survey notes" |
| `height` (no type) | "Not measured" |
| `material` on any type | "Not recorded in survey" |
| `name`/`location` absent | "—" (em dash) |
| `relationship` absent | "—" (em dash) |

---

## Alias Resolution

Column names in uploaded CSVs may not match canonical field names.
Use `resolve_alias(column_name)` to map any known alias to the canonical field name.

Key aliases to know:
- `ht`, `Ht`, `HT` → `height`
- `location`, `remark`, `remarks`, `desc` → `name`
- `e`, `E`, `osgb_e` → `easting`
- `n`, `N`, `osgb_n` → `northing`

---

## Conditional Display Rules

### Height display
```python
from app.field_validators import format_field_display

height_str = format_field_display(props.get("height"), "height", props.get("structure_type"))
```

### Completeness classification
```python
from app.field_validators import classify_field_completeness

status = classify_field_completeness(props, ["height", "material", "name"])
# status["height"] → "present" | "absent_ok" | "absent_warn"
```

Use `absent_warn` to optionally show a ⚠ indicator on height for EXpole/Angle.
Do NOT use `absent_warn` to trigger a QA FAIL — that is handled by the QA engine.

---

## Safety Checklist

Before writing any popup rendering code:

- [ ] Read `app/field_reference.py` — understand FIELD_DEFINITIONS structure
- [ ] Read `app/field_validators.py` — understand format_field_display signature
- [ ] Run `pytest tests/test_c2e2_popup_fields.py -v` — all 94 should pass
- [ ] Do NOT modify `app/routes/map_preview.py`
- [ ] Do NOT modify validation semantics in `app/qa_engine.py`
- [ ] Do NOT change span generation or geometry pipeline
- [ ] Confirm popup change does not affect: span hover, route highlight, filter panel

---

## Testing Gates for Implementation

After each popup change:

1. `pytest tests/test_c2e2_popup_fields.py -v` — all pass
2. `pytest tests/test_review_navigation_layer.py -v` — all pass
3. `pytest -v` — full suite passes (810+)
4. Manual: open P008/F001 (Bellsprings) — verify popup shows correct wording
5. Manual: open P010/F001 — verify EXpole popup shows height, Pol shows "Not measured"
6. Manual: click span → span popup not broken
7. Manual: review navigation (prev/next buttons) still works

---

## Key Python API

```python
# field_reference.py
from app.field_reference import (
    POPUP_FIELD_GROUPS,       # dict of group → [field_names]
    POPUP_GROUP_ORDER,        # ordered list of groups
    FIELD_DEFINITIONS,        # full field catalogue
    get_field_definition(field_name)       # → dict | None
    get_all_aliases(field_name)            # → list[str]
    get_display_label(field_name)          # → str
    get_missing_wording(field_name, structure_type=None)  # → str
    get_fields_for_group(group_name)       # → list[str]
    get_field_unit(field_name)             # → str | None
    resolve_alias(column_name)             # → canonical name | None
)

# field_validators.py
from app.field_validators import (
    is_measured(value)                     # → bool
    is_missing_legitimate(field, type)     # → bool
    validate_field_value(value, field)     # → (bool, err | None)
    validate_height_value(height, type)    # → (bool, advisory | None)
    format_field_display(value, field, type)  # → str (with unit, missing wording)
    get_popup_display_value(field, props, type=None)  # → str (alias-aware)
    classify_field_completeness(props, fields)  # → {field: 'present'|'absent_ok'|'absent_warn'}
)
```

---

*Produced by Claude Code claude-code/c2e2-support-suite on 2026-05-09.*
*Paired with: 31_REAL_JOB_FIELD_REALITY_REPORT.md, app/field_reference.py, app/field_validators.py*
