# Baseline vs Field vs DNO: Data Source Authority

## Purpose

Define authoritative data sources for each field in the GridFlow data model.

## FROM BASELINE (ENWL Map Popup / DNO GIS Data)

**Source Authority: DNO asset register via ENWL basemap**

Fields available in P_LOCAL_001:

- `support_no` — Field-visible pole number (from map popup)
- `coordinates` — Lat/Long from map marker position
- `asset_type` — Pole classification (from popup if shown)
- `circuit_reference` — Route/circuit ID (if shown in popup)
- `voltage_level` — May be indicated in popup or layer

**Certainty: HIGH** (from DNO GIS system)

**Source: ENWL basemap popups (screenshot evidence)**

## FROM FIELD CAPTURE (Surveyor Observations)

**Source Authority: Direct observation from site visit**

Fields captured in P_LOCAL_001:

- `pole_type_observed` — TIMBER/STEEL/CONCRETE from visual inspection
- `voltage_observed` — From warning signs if visible
- `equipment_observed` — Transformers, cutouts, streetlights, etc.
- `condition_observed` — Overall visual condition
- `defects_observed` — Visible damage, rot, lean, etc.
- `access_constraints` — Road/footpath/private land
- `warning_signs_present` — Yes/no + description
- `stay_present` — Yes/no
- `photo_evidence` — File references in `field_photos/`
- `survey_date` — When photos taken
- `surveyor_notes` — Free-text observations in `notes/`

**Certainty: VARIABLE** (depends on visibility, access, photo quality)

**Source: Field photos + notes files in `enwl_enrichment_clean/`**

## FROM DNO RECORDS (Engineering Truth)

**Source Authority: DNO engineering specifications**

Fields NOT available in P_LOCAL_001 (would require DNO data request):

- `voltage_carried_actual` — Certified operating voltage
- `conductor_size` — Wire specification (e.g., 70mm² Cu)
- `conductor_type` — Material specification
- `pole_class` — Strength rating (Class 5, Class 7, etc.)
- `pole_height_manufactured` — Specified height (8m, 10m, 12m)
- `transformer_rating_actual` — kVA rating from DNO records
- `asset_install_date` — When pole erected
- `last_inspection_date` — DNO inspection history
- `inspection_outcome` — DNO assessment
- `retention_category` — CNAIM health index

**Certainty: HIGH** (engineering records)

**Source: Requires formal DNO data access (not available in P_LOCAL_001)**

## REQUIRES DNO VERIFICATION

The following values must not be treated as final design inputs from P_LOCAL_001 field evidence alone:

- Certified operating voltage
- Conductor size, material, configuration, phase arrangement, and rating
- Pole class, strength, manufactured height, and structural capacity
- Transformer rating, protection settings, and connected load
- Circuit loading, network capacity, and switching state
- Asset ownership, joint-use responsibilities, and statutory inspection history

Field photos can show that equipment appears to exist. They cannot reliably determine certified voltage, conductor specification, pole strength class, asset rating, or compliance status.

## MERGE STRATEGY FOR P_LOCAL_001

### Identity Resolution

1. Baseline (map popup) provides: `support_no` + `coordinates`
2. Field capture provides: photos proving pole exists at that location
3. Match confirmed if: support number in popup matches field location
4. Edge case: Pole 08 (`NO_POLE_POPUP`) — support number inferred from route context

### Equipment Identification

1. Field capture identifies: "Transformer visible, warning sign present"
2. Map popup may indicate: HV/LV designation, equipment type
3. GridFlow displays: Field observation + map popup info combined
4. Conflict resolution: Both sources shown, designer reviews

### Voltage Determination

**Critical: P_LOCAL_001 demonstrates voltage is partially observable**

Voltage is not reliably field-observable from photos alone. Warning signs, visible equipment, and ENWL popup labels may indicate a likely voltage category, but final design must use DNO-confirmed engineering records.

Logic for this dataset:

```text
IF warning_sign_visible_in_photo:
    field_voltage = sign_indication (HV vs LV)
    confidence = MEDIUM (signs indicate general category)
ELSE IF equipment_type_observed:
    field_voltage = inferred_from_equipment (transformer = HV/LV transition)
    confidence = LOW
ELSE:
    field_voltage = from_map_popup_if_available
    confidence = MEDIUM

For engineering design:
    authoritative_voltage = REQUIRES_DNO_CONFIRMATION
```

Examples from P_LOCAL_001:

- Pole 05 (902204): `HV_TRANSFORMER` — transformer visible, likely HV/LV boundary
- Pole 01 (903203): `LV_TERMINAL_STREETLIGHT` — streetlight indicates LV
- Pole 09 (900347): `HV_LINK_TEE_OFF` — map popup indicated HV

### Condition Assessment

1. Field capture is PRIMARY source for current condition
2. DNO inspection history NOT available in P_LOCAL_001
3. GridFlow displays: Field observations from `notes/` files
4. Designer reviews photos for verification

Condition observations are visual review evidence. They do not replace DNO inspection outcomes, pole test results, or structural assessment.

## DATA GAPS IN P_LOCAL_001

Items NOT available without DNO data request:

- ❌ Certified voltage specifications
- ❌ Conductor sizes and types
- ❌ Pole strength classes
- ❌ Installation dates
- ❌ Inspection history
- ❌ Asset ownership (DNO vs joint-use)
- ❌ Circuit loading data

## DESIGN BLOCKERS

The following gaps prevent final engineering design or design authorization from P_LOCAL_001 alone:

- Missing DNO-confirmed voltage specification
- Missing DNO-confirmed conductor size/type/rating
- Missing DNO-confirmed pole class, strength, and height
- Missing DNO inspection history and current asset health data
- Missing circuit loading and capacity data
- Missing formal ownership/joint-use responsibility confirmation
- Any MEDIUM/LOW identity match confidence or conflicting evidence requiring manual resolution

GridFlow may flag these blockers and route them for review. GridFlow must not resolve them by inference from field photos.

Items AVAILABLE from baseline + field:

- ✅ Support numbers (from map popups)
- ✅ Approximate coordinates (from map)
- ✅ Visual pole type (timber/steel)
- ✅ Equipment presence (transformers, streetlights)
- ✅ Current condition (from field photos)
- ✅ Access constraints (from field survey)

## VERIFICATION FLAGS FOR P_LOCAL_001

GridFlow should flag:

- `voltage_verification_required` — All poles (no DNO specs available)
- `conductor_verification_required` — All poles
- `pole_class_verification_required` — All poles
- `identity_verification_medium_confidence` — Pole 08 (no popup)
- `access_verification_required` — If restricted access noted

## TRUST HIERARCHY FOR P_LOCAL_001 CONTEXT

**AVAILABLE (MEDIUM-HIGH TRUST):**

1. Support numbers from ENWL map popups
2. Coordinates from map markers
3. Current visual condition from field photos
4. Equipment presence from field observation

**NOT AVAILABLE (REQUIRES DNO ACCESS):**

1. Engineering specifications (voltage, conductor, pole class)
2. Asset history and inspection records
3. Circuit operational data

**DESIGN IMPLICATION:**

P_LOCAL_001 dataset is suitable for:

- ✅ Demonstrating baseline-to-field correlation
- ✅ Demonstrating field capture methodology for this dataset structure
- ✅ Validating evidence structure
- ✅ Testing match confidence scoring

P_LOCAL_001 dataset is NOT suitable for:

- ❌ Final engineering design (needs DNO specs)
- ❌ Load calculations (needs conductor data)
- ❌ Compliance verification (needs inspection history)

**This is exactly what Phase 4 (same-site baseline pilot) would address.**

## Uncertainty and Limitations

- P_LOCAL_001 supports evidence workflow validation and support-number correlation, not final design.
- ENWL popup data is useful baseline context but may not contain all engineering fields required for design.
- Field observations should remain separate from DNO engineering truth.
- Any future runtime integration must preserve source provenance and verification flags for every merged value.
