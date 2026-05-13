# Evidence Normalization Standard

## Purpose

Define consistent folder structure, file naming, and evidence requirements for field-captured pole data.

## Folder Structure Standard

### Top-Level Organization

```text
enwl_enrichment_clean/
├── 01_SUPPORT_903203_LV_TERMINAL_STREETLIGHT/
├── 02_SUPPORT_903202_LV_TEE_OFF/
└── 10_SUPPORT_902206_HV_TRANSFORMER/
```

### Folder Naming Convention

Format: `NN_SUPPORT_{number}_{descriptors}`

- `NN`: Sequence number (01, 02, 03...)
- `{number}`: DNO support number from map popup
- `{descriptors}`: Voltage/equipment type (optional, descriptive)

Examples:

- `01_SUPPORT_903203_LV_TERMINAL_STREETLIGHT`
- `05_SUPPORT_902204_HV_TRANSFORMER`
- `08_SUPPORT_900346_HV_LINK_NO_POLE_POPUP`

### Pole Folder Contents (Standard)

Each pole folder must contain three subdirectories:

```text
NN_SUPPORT_XXXXXX/
├── field_photos/          # 3+ photos minimum
├── map_screenshots/       # 1+ screenshots
└── notes/                 # 1+ txt files
```

## File Naming Standards

### Field Photos

Format: `{subject}_{sequence}.jpg` or `{subject}_{sequence}.heic`

Valid subjects:

- `pole_full` — complete pole in frame
- `pole_base` — ground level, rot check visible
- `pole_top` — crossarms, insulators, conductors
- `equipment` — transformers, cutouts, warning signs
- `stay` — stay wire and anchor
- `context` — surrounding area, access route
- `defect` — specific damage, lean, cracks
- `warning_sign` — close-up of warning signage
- `transformer` — transformer equipment detail

Sequence: `001`, `002`, `003` (zero-padded) or `01`, `02`, `03`

### Map Screenshots

Format: `map_popup_{identifier}.png` or `screenshot_{description}.png`

- Must show ENWL basemap popup with asset details
- Must show pole location marker clearly
- Should include support number in popup if visible

### Notes Files

Format: `notes.txt` or `{pole_identifier}_notes.txt`

Plain text, UTF-8 encoding.

## Notes Structure Standard

Recommended sections (flexible structure):

```text
POLE IDENTITY
Support No: [from map popup]
Type: [from observation or map]
Voltage: [from warning signs or map]

LOCATION
Grid Ref: [from map popup if available]
Address/Landmark: [nearest identifiable location]
Access: [road/footpath/private land]

CONDITION
Overall: [GOOD/FAIR/POOR or descriptive]
Base: [observed condition]
Top: [observed condition]
Defects: [list or "none observed"]

EQUIPMENT OBSERVED
Warning Signs: [present/absent, description]
Transformer: [yes/no, details if visible]
Other: [cutouts, stays, etc.]

NOTES
[Free-text observations, survey context, constraints]
```

**Note:** Actual notes format may vary — flexibility allowed as long as key observations are captured.

## Evidence Minimum Requirements

For pole to be **validation-eligible**:

- ✅ At least 3 field photos (minimum: pole visible in frame)
- ✅ At least 1 map screenshot showing pole location
- ✅ At least 1 notes file with observations

For pole to be **HIGH confidence match** (additional criteria):

- ✅ All minimum requirements met
- ✅ Support number verified (map popup clearly shows it)
- ✅ Field photos show pole top, base, and equipment
- ✅ Notes document key identifying features

## Uncertainty Documentation

When support number unclear:

- Document in notes: "Support number not clearly visible in map popup"
- Use descriptive folder naming based on location/equipment
- Flag for identity verification

When voltage unclear:

- Document in notes: "No warning signs visible" or "Warning sign unclear"
- Use available evidence (equipment type, map data)
- Flag for voltage verification

When access restricted:

- Document in notes: "Access constraints: [describe]"
- Photo from public vantage point only
- Note limitations in survey coverage

## Actual P_LOCAL_001 Dataset Compliance

Current `enwl_enrichment_clean` dataset (10 poles):

- ✅ All follow `NN_SUPPORT_XXXXXX` naming pattern
- ✅ All have `field_photos/`, `map_screenshots/`, `notes/` subdirectories
- ✅ All have 3+ field photos (range: 3-11 photos)
- ✅ All have 1+ map screenshots (range: 1-7 screenshots)
- ✅ All have 1 notes file
- ✅ Folder names include descriptive identifiers (`LV_TERMINAL`, `HV_TRANSFORMER`, etc.)
- ✅ Mix of LV and HV poles
- ✅ Include edge cases (`NO_POLE_POPUP`, `JOINT_USER`)
- ✅ **100% compliance with minimum evidence requirements**

This dataset demonstrates the evidence standard in practice.

## Uncertainty and Limitations

The evidence standard makes field capture consistent and reviewable. It does not certify engineering design values.

- A compliant evidence folder proves that minimum evidence is present, not that final design data is complete.
- Photo coverage may be limited by access, vegetation, distance, weather, lighting, or safety constraints.
- Warning signs and visible equipment support review context, but they do not replace DNO voltage, conductor, pole class, load, or inspection records.
- Folder descriptors are descriptive labels for evidence organization; they are not engineering classifications unless backed by DNO data.
- P_LOCAL_001 shows the standard is workable for this dataset. Future datasets with different capture quality or asset types may require expanded validation.

## Assumptions and Untested Edge Cases

This standard assumes one evidence folder maps to one reviewed support or pole structure. Additional rules may be needed for:

- Underground-only records with no visible pole
- H-frame or multi-support structures
- Multiple supports sharing one equipment assembly
- EHV/transmission assets
- Complex multi-circuit poles where route context is ambiguous
- Sites where no safe public vantage point captures pole top or base

## Prohibited Practices

❌ DO NOT:

- Fabricate support numbers
- Edit photos to remove defects
- Omit observed defects
- Mix evidence from multiple poles in one folder
- Guess at technical specifications

✅ DO:

- Document uncertainty explicitly
- Flag items requiring verification
- Preserve original photo metadata where possible
- Note survey limitations honestly
- Use descriptive folder names when support number unclear
