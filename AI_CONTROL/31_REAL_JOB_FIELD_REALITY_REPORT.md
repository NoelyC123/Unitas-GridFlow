# Real Job Field Reality Report

## Purpose

Ground-truth audit of what fields actually exist in real survey files uploaded to GridFlow.
Produced from direct analysis of P001/F001 (Gordon Pt1 Original), P008/F001 (Bellsprings
Woodside Park), P010/F001 (Gordon Pt1 Original copy), and all four raw validation_data files.

---

## Source File Survey

| File | Format | Rows | Columns (raw CSV) |
|------|--------|------|-------------------|
| Gordon Pt1 - Original.csv | Trimble raw dump | 157 data records | 17 (but structured as attribute pairs, not named columns) |
| 2814_474c_raw_trimble_export.csv | Trimble raw dump | 91 data records | 3 (more compact format) |
| 2814_4-474_raw_trimble_export.csv | Trimble raw dump | 83 data records | 3 |
| 28-14 513 (2).csv | Trimble raw dump | 11 data records | 3 |
| Bellsprings_Woodside_Park_11kV.csv | Trimble raw dump | 57 data records | 15 |
| messy_test.csv | Flat CSV (manual) | 5 data records | 5 (named headers) |

---

## Trimble Raw Dump Format (F001-class files)

These are **not standard CSV with column headers**. They are positional Trimble controller
exports where each data row is:

```
point_id, easting, northing, gps_elevation, structure_code, CODE:STRING, string_num,
CODE:TAG, tag_value, CODE:REMARK, remark_text, CODE:LAND USE, land_use_value,
CODE:HEIGHT, height_value [, optional trailing annotation]
```

The GPS elevation in column 3 is **instrument/terrain elevation, not pole height**. It is
intentionally discarded by the parser. Pole height comes from the `CODE:HEIGHT` attribute
pair later in the row.

---

## What the Parser Actually Extracts

The `parse_raw_controller_dump()` function in `controller_intake.py` produces exactly **6
columns** from Trimble files:

| Field | Source in CSV | Notes |
|-------|--------------|-------|
| `pole_id` | Column 0 (survey point number) | Always present |
| `easting` | Column 1 | Always present, OSGB |
| `northing` | Column 2 | Always present, OSGB |
| `height` | `CODE:HEIGHT` attribute value | Partial — see below |
| `structure_type` | Column 4 (feature code) | Almost always present |
| `location` | `CODE:REMARK` attribute value | Partial — see below |

### What is Currently Discarded

- **`CODE:LAND USE`** attribute — present in Gordon_Pt1 and Bellsprings files (e.g. "PASTURE",
  "PASTURE.") but not extracted by the current parser. Could be added if needed.
- **GPS elevation** (column 3) — intentionally excluded; records terrain height, not pole height.
- **`CODE:TAG`** attribute — always "S" in all observed files; no value.
- **`CODE:STRING`** / string number — sequence grouping metadata; not currently used.

---

## Field Completeness Across Real Jobs

| Field | Gordon Pt1 (157 records) | 2814_474c (91) | 2814_4-474 (83) | 28-14_513 (11) | Bellsprings (57) |
|-------|--------------------------|----------------|-----------------|-----------------|------------------|
| `pole_id` | 100% | 100% | 100% | 100% | 100% |
| `easting` | 100% | 100% | 100% | 100% | 100% |
| `northing` | 100% | 100% | 100% | 100% | 100% |
| `structure_type` | ~99% | ~100% | ~100% | 100% | 100% |
| `height` | **29%** | **21%** | **27%** | **18%** | **33%** |
| `location` | **20%** | **12%** | **13%** | **27%** | **33%** |

**Key finding:** Height and location are deliberately partial. They are only recorded for
**key features** — existing poles being replaced (EXpole), angle/strain structures (Angle),
and specific crossing heights. Intermediate poles (Pol) are NOT expected to have height or
remarks. This is correct survey practice, not missing data.

---

## GeoJSON Feature Properties After Full Pipeline

After `process_job()`, each GeoJSON feature has these properties:

| Property | Source | Availability |
|----------|--------|-------------|
| `pole_id` | Parsed from CSV | Always |
| `easting` | Parsed from CSV | Always |
| `northing` | Parsed from CSV | Always |
| `height` | Parsed from CSV | Partial (see above) |
| `structure_type` | Parsed from CSV | Almost always |
| `name` | Same as `location` remark | Partial |
| `asset_intent` | **Derived** from structure_type | Present when classifiable |
| `relationship` | **Derived** from EX/PR pair detection | On paired EXpole/PRpole only |
| `record_role` | **Derived** classification | Always ('structural', 'context', etc.) |
| `qa_status` | **Derived** by QA engine | Always ('PASS', 'WARN', 'FAIL') |
| `issue_count` | **Derived** | Always |
| `warn_count` | **Derived** | Always |
| `issue_texts` | **Derived** | Always (may be empty list) |
| `warn_texts` | **Derived** | Always (may be empty list) |
| `material` | Parsed from CSV alias | **Always None in Trimble jobs** |
| `id` | Copy of `pole_id` | Always |

---

## C2E2 Candidate Fields — Reality Check

The `02_CURRENT_TASK.md` proposed five field groups for popup expansion. Here is what is
actually available in real survey data:

### Group 1 — Pole / support specification
| Field | In Trimble? | Notes |
|-------|-------------|-------|
| `pole_class` | ❌ Never | Not a Trimble attribute. Would require structured capture. |
| `specification` | ❌ Never | Not a Trimble attribute. |
| `material` | ❌ Never | Property exists in GeoJSON schema but is always None for Trimble jobs. |

### Group 2 — Condition / defects
| Field | In Trimble? | Notes |
|-------|-------------|-------|
| `condition` | ❌ Never | Not recorded in controller dump format. |
| `defect_type` | ❌ Never | Not recorded in controller dump format. |
| `defect_severity` | ❌ Never | Not recorded in controller dump format. |

### Group 3 — Electrical / conductor
| Field | In Trimble? | Notes |
|-------|-------------|-------|
| `voltage_carried` | ❌ Never | Could be inferred from rulepack (job-level), not per-pole. |
| `conductor_type` | ❌ Never | Not recorded in controller dump format. |
| `conductor_size` | ❌ Never | Not recorded in controller dump format. |
| `phase_configuration` | ❌ Never | Not recorded in controller dump format. |

### Group 4 — Structural support
| Field | In Trimble? | Notes |
|-------|-------------|-------|
| `stay_present` | ❌ Direct: Never | But `stay_evidence_status` is derived by QA engine from nearby Stay records. |
| `stay_type` | ❌ Never | Not a Trimble attribute. |
| `lean_direction` | ❌ Never | Not recorded. |
| `lean_severity` | ❌ Never | Not recorded. |

### Group 5 — Equipment
| Field | In Trimble? | Notes |
|-------|-------------|-------|
| `equipment_present` | ❌ Never | Not recorded in controller dump format. |
| `equipment_type` | ❌ Never | Not recorded in controller dump format. |

### Extractable-but-not-yet-extracted
| Field | In Trimble? | Notes |
|-------|-------------|-------|
| `land_use` | ✅ **Yes** | `CODE:LAND USE` attribute. Currently discarded. Values: "PASTURE", "PASTURE.", empty. |
| `being_replaced_by` | ✅ Derivable | From sequencer `matched_expoles` result. |
| `replacing` | ✅ Derivable | From sequencer `matched_expoles` result. |

---

## Messy Test File (P011/F001)

`messy_test.csv` is a manually constructed flat CSV with named headers `E, N, Ht, Type, Remarks`.
It has whitespace issues, `m` suffix on height, blank rows, `N/A` values, and an invalid
coordinate. It is the robustness test fixture for `api_intake.py` cleaning utilities.

It does NOT represent a real survey pattern — it is a synthetic edge-case test file.

---

## Implications for C2E2 Popup Expansion

1. **Only 6 fields come from real Trimble data.** All other popup content is derived.

2. **Most C2E2 candidate fields are absent from current Trimble format.** Showing them in
   the popup requires either (a) structured field capture (Stage 4 feature), or (b) explicit
   "Not recorded in survey" labels so users understand the gap.

3. **Height on Pol records is intentionally absent.** Missing height on intermediate poles
   (`Pol`) is expected survey practice, not a data quality failure. The popup should NOT
   show "Unknown" for height on a `Pol` — it should show "Not measured" or omit the field.

4. **The `land_use` field could be added without any new field capture.** It is already in
   the raw CSV and would require only a parser change to surface it. This is a low-cost win
   if the field is useful.

5. **`stay_evidence_status`** exists in the QA output. If this were plumbed through to
   map_data.json properties it could power a stay-related popup field today.

6. **`location`/`name`** is the richest per-pole free-text field. Values like "pole 1",
   "ex pole", "4a-474 sect", "not required" are real surveyor notes. This is already shown.

---

## Recommended C2E2 Fields Based on Reality

Fields that are genuinely useful and based on real available data:

**Tier 1 — Already in GeoJSON, add/improve display:**
- `height` (with conditional label by structure_type)
- `structure_type` (already shown, improve label)
- `asset_intent` (already shown, confirm label)
- `relationship` (already shown for paired features)
- `qa_status` (already shown)
- `name` / `location` (already shown as popup name)

**Tier 2 — Derivable, not yet surfaced in popup:**
- `being_replaced_by` / `replacing` (from sequencer)
- `stay_evidence_status` (from QA output)
- `land_use` (from raw CSV, currently discarded)

**Tier 3 — Absent from Trimble, needs "not recorded" label:**
- `material` (display "Not recorded in survey" not blank)
- `pole_class` (display "Not recorded" or omit)
- `condition` (omit until Stage 4 field capture)

**Do not add to popup (absent, no display value):**
- `conductor_type`, `voltage_carried`, `phase_configuration`
- `defect_type`, `defect_severity`
- `lean_direction`, `equipment_type`

---

*Analysis date: 2026-05-09. Based on parse_raw_controller_dump() output from 5 real survey files.*
