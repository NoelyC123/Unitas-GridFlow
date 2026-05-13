# GridFlow Domain Reference

## Purpose

This is the authoritative technical and domain reference for GridFlow AI-assisted development sessions. It consolidates the current project state, UK overhead line domain assumptions, Stage 4B validation governance, and Stage 4C runtime architecture.

This document must be read before any major GridFlow Stage 4 or review-workspace work.

---

## 1. Project Overview

### What GridFlow Is

GridFlow is a survey-to-design workflow and design-readiness tool for UK electricity overhead line (OHL) infrastructure. It helps convert survey, baseline, and field evidence into structured review outputs that a designer can use before moving into CAD/design tools.

GridFlow focuses on:

- Field evidence capture and normalization
- DNO/Trimble baseline ingestion
- Baseline-to-field identity correlation
- Evidence quality scoring
- Verification flag generation
- Designer review preparation
- QA reporting for missing design-critical evidence

### What GridFlow Is NOT

GridFlow is not:

- An engineering design authority
- A replacement for DNO records
- A compliance certifier
- A load-calculation engine
- A PoleCAD replacement
- A tool that can infer certified voltage, conductor size, pole class, asset rating, or inspection status from photos

GridFlow can identify what evidence exists and what still needs verification. It must not claim final design readiness without DNO engineering data and designer sign-off.

### Users

Primary users include:

- ICPs (Independent Connection Providers)
- Tier-1 contractors
- Field surveyors
- Overhead line designers
- Project reviewers preparing survey-to-design handoffs

### Workflow Position

GridFlow sits between field survey and design CAD/PoleCAD workflows:

```text
DNO/Trimble baseline + field survey evidence
        -> GridFlow ingestion, matching, verification flags, QA
        -> Designer review
        -> PoleCAD / CAD / DNO design submission workflow
```

### Current Implementation Status

As of the current Stage 4C work:

- Stage 4A: Structured capture library correctness complete
- Stage 4B: Validation and evidence workflow complete for P_LOCAL_001
- Stage 4C.1: Baseline ingestion complete
- Stage 4C.2: Field evidence import in progress
- Stage 4C.3: Matching engine in progress
- Stage 4C.4: Merge engine planned and specified
- Stage 5: Designer review UI future work

Key implemented areas currently visible in the repo:

- `gridflow/baseline/`: Baseline ingestion models, CSV parser, schema validator, coordinate transformer, support number normalizer, route reconstructor
- `gridflow/field/`: Field evidence models, folder scanner, notes parser, evidence quality scorer, dataset validator
- `scripts/ingest_baseline.py`: Stage 4C.1 baseline ingestion CLI
- `scripts/import_field_evidence.py`: Stage 4C.2 field evidence import CLI
- `scripts/generate_match_register.py`: Stage 4B/4C matching register support
- `scripts/calculate_match_rate.py`: Stage 4B match-rate calculation support

---

## 2. UK DNO Landscape

### Six DNO Groups

The UK distribution network is operated by six main DNO groups:

1. ENWL - Electricity North West Limited
   - Region: North West England, including Cumbria, Lancashire, Greater Manchester, and surrounding areas
   - Relevant to P_LOCAL_001 and the ENWL Network Asset Viewer evidence workflow

2. NGED - National Grid Electricity Distribution
   - Region: Midlands, South West England, and South Wales
   - Formerly Western Power Distribution

3. SPEN - ScottishPower Energy Networks
   - Region: Central/southern Scotland, Merseyside, Cheshire, North Wales, and North Shropshire

4. SSEN - Scottish and Southern Electricity Networks
   - Region: North of Scotland and central southern England

5. UKPN - UK Power Networks
   - Region: London, South East England, and East of England

6. NPG - Northern Powergrid
   - Region: North East England, Yorkshire, and northern Lincolnshire

### Data Access Mechanisms

DNO data may be available through:

- Public/open data portals
- Web GIS/network asset viewers
- Formal data requests
- Project-specific design packs
- Trimble/controller survey exports
- ICP/Tier-1 provided baseline packs

GridFlow must preserve source provenance because each data access path has different reliability, completeness, and legal/design authority.

### ENWL Network Asset Viewer

The ENWL Network Asset Viewer has been proven as a practical evidence source in P_LOCAL_001.

P_LOCAL_001 used:

- Map popup screenshots showing support numbers and asset context
- Connected asset screenshots for conductors, sleeves, transformers, and pole records where available
- Folder-level evidence normalization in `real_pilot_data/P_LOCAL_001/enwl_enrichment_clean/`

ENWL screenshots are useful baseline evidence, but they do not replace full DNO engineering design records.

### Baseline Data Formats by DNO

Expected baseline sources vary by DNO and project:

- ENWL: ENID/support number, asset popup exports, GIS layer screenshots, CSV exports where available
- NGED: asset IDs, point/pole references, feeder/circuit references, coordinates
- SPEN: support numbers, route references, point names, design pack extracts
- SSEN: pole IDs, circuit IDs, asset type fields, GIS coordinates
- UKPN: network asset identifiers, LV/HV route/circuit references, coordinates
- NPG: support identifiers, asset classes, circuit and route metadata

GridFlow should use format detection plus manual schema mapping where DNO CSVs differ.

### ENID System

ENID refers to ENWL asset identifiers in ENWL data. In practical GridFlow use, ENWL evidence may include:

- ENID or FID values from GIS popups
- Support No values visible in pole popups
- System references such as route/asset identifiers
- Connected asset FIDs for conductors, sleeves, transformers, and links

For matching, `support_no` is the practical field identity key where available.

### Support Number Conventions

Support numbers can appear as:

- Pure numeric: `903203`
- With suffix: `903201A`
- With prefixes: `SP903203`, `EN903203`
- With separators: `90-3203`
- Embedded in folder names: `01_SUPPORT_903203_LV_TERMINAL_STREETLIGHT`

Support-number normalization must preserve suffixes where they may indicate variant records.

---

## 3. Overhead Line Infrastructure Domain Knowledge

### Pole Types

Common support materials include:

- Timber poles: common for LV/HV rural and semi-rural distribution
- Steel poles/towers: used for higher load or specialist sites
- Concrete poles: less common in some UK DNO regions but present in some networks
- Composite poles: newer/specialist installations

Field photos can usually identify broad material, but not certified pole class or strength rating.

### Pole Classes

Pole classes (often Class 1-7 or similar strength groupings) define mechanical strength and design capability. These are engineering specification values and must come from DNO records, manufacturing/birthmark data, or formal design documentation.

Do not infer pole class from photos.

### Voltage Levels

Typical UK distribution voltage categories:

- LV: 230V single phase / 400V three phase
- HV: 6.6kV, 11kV, 33kV
- EHV: 66kV and above

Field evidence may indicate likely voltage category through warning signs, equipment, or DNO map layers, but final voltage for design must come from DNO engineering records.

### Conductor Types

Common overhead conductor categories include:

- Bare overhead conductor
- AAC: All Aluminium Conductor
- ACSR: Aluminium Conductor Steel Reinforced
- Copper overhead conductor
- Covered conductor
- ABC: Aerial Bundled Cable

Do not infer conductor size, material, phase arrangement, or rating from photos unless backed by DNO data.

### Crossarms and Insulators

Visible pole-top features may include:

- Timber/steel crossarms
- Pin insulators
- Shackle/spool insulators
- Strain/tension arrangements
- Multiple circuits or tee-off arrangements
- Links, fuses, or switching equipment

Photos can document presence and arrangement but do not certify electrical specification.

### Stay Wires

Stay evidence may include:

- Stay wire / guy wire
- Stay angle and direction
- Stay anchor or screw anchor
- Anchor plate/rod where visible
- Vegetation/access constraints around anchor

Stay presence is field-observable if visible. Anchor condition and mechanical adequacy require engineering inspection.

### Equipment

Relevant OHL equipment includes:

- Pole-mounted transformers with kVA ratings from DNO records
- HV/LV transformer interfaces
- Cutouts and fuses
- Reclosers and switches
- Links and jumper arrangements
- Streetlight attachments or nearby streetlighting columns
- Cable sealing ends and overhead-to-underground transitions

Do not treat visible equipment as proof of rating, setting, or connected load.

### Warning Signs and DNO Markings

Evidence may include:

- Danger of Death plates
- Voltage warning triangles
- DNO tags or markings
- Inspection plates
- Carved/painted support numbers
- Birthmarks and pole markings

Warning signs support field context but can be outdated, damaged, missing, or non-specific.

### Joint User Poles

Joint user poles can include telecoms, street lighting, private apparatus, or other third-party equipment. GridFlow must separate DNO infrastructure evidence from non-DNO equipment and flag ownership/joint-use uncertainty for review.

### Pole Markings

Useful field identity evidence includes:

- Carved support numbers
- Painted support numbers
- Inspection plates
- Manufacturer/birthmark data
- DNO tags

Support numbers from map popups and visible pole markings are identity evidence, not final engineering design data.

### Overhead-to-Underground Transitions

OH/UG transition evidence may include:

- Cable sealing ends
- Cable guards/downleads
- Pole-mounted termination equipment
- Underground cable records in DNO GIS
- Laid-direct or ducted cable notes from baseline data

Physical transition details may be obscured by vegetation or private land access constraints.

### CNAIM Health Index

CNAIM (Common Network Asset Indices Methodology) is a framework used by UK network operators for asset health and risk indices. CNAIM values require DNO asset history and inspection records. GridFlow must not infer CNAIM health index from photos.

### ENA TS 43-88

ENA TS 43-88 is an Engineering Networks Association technical specification relevant to new overhead line infrastructure, including pole/birthmark standards. Field photos may capture birthmark markings, but interpretation for design must be handled by qualified designers/DNO records.

### NGED OH8B

NGED OH8B is a retention/replacement policy context for overhead line poles. It informs asset retention/replacement decisions within NGED workflows but does not directly authorize decisions from GridFlow field photos.

### PoleCAD Context

PoleCAD is specialist overhead line design software. GridFlow prepares structured evidence and verification flags that can support design preparation, but PoleCAD and design calculations still require authoritative engineering inputs such as conductor data, spans, pole class, loading, stays, and DNO specifications.

---

## 4. Field Survey Methodology (P_LOCAL_001 Proven)

### Equipment

P_LOCAL_001 demonstrated a practical field workflow using:

- iPad/iPhone
- ENWL Network Asset Viewer or map popup source
- Device camera for field photos
- Notes for access, condition, equipment, and uncertainty

### Evidence Capture Process

Recommended process:

1. Open the DNO map/GIS viewer for the target pole.
2. Capture map popup screenshot showing support number and location marker.
3. Capture field photos from safe public or permitted vantage points.
4. Capture notes separating observations from assumptions.
5. Normalize evidence into `enwl_enrichment_clean/` folder structure.
6. Run validation/import/matching workflows.

### Photo Requirements

Minimum validation-eligible evidence:

- At least 3 field photos
- Pole visible in frame
- At least 1 map screenshot
- At least 1 notes file

Recommended photo set:

- Full pole/context
- Pole base / ground context where safely visible
- Pole top / crossarm / conductor attachment where safely visible
- Equipment detail if present
- Warning signs / support markings if visible
- Access route / restrictions
- Defects or constraints where present

### Map Screenshot Requirements

Map screenshots should show:

- Support number if available
- Map marker / location context
- Relevant asset popup details
- Connected asset popups where useful
- FID/asset identifiers where shown

### Notes Structure

Recommended notes sections:

- POLE IDENTITY
- LOCATION
- CONDITION
- EQUIPMENT OBSERVED
- ACCESS CONSTRAINTS
- VERIFICATION REQUIRED
- UNCERTAINTY / LIMITATIONS

### Observable vs DNO-Required

Field-observable:

- Pole material appearance
- Visible equipment presence
- Warning signs
- Access constraints
- Visible defects/condition indicators
- Stay presence where visible
- Field-photo coverage quality

Requires DNO records:

- Certified voltage
- Conductor size/type/rating
- Pole class/strength/height
- Transformer rating/settings/load
- Circuit loading and switching state
- Inspection history/CNAIM
- Ownership/joint-use responsibility

### Access Considerations

Document access constraints honestly:

- Roadside/public footpath
- Private land
- Garden boundary
- Field/agricultural access
- Hedge/vegetation obstruction
- Distance-limited view
- Traffic constraints
- Unsafe or inaccessible vantage points

### GNSS Limitations

Mobile GNSS is typically around +/-5m or worse depending on environment. It is useful for context but not sufficient for pole positioning where DNO/baseline coordinates are available.

Always prefer baseline coordinates over field GPS for matching and design preparation.

### Survey Safety

Field capture must avoid unsafe proximity to live overhead lines and electrical equipment. Surveyors should maintain safe distances, avoid climbing or touching assets, and account for traffic, private land, livestock, vegetation, and weather.

---

## 5. Data Authority Hierarchy

### Highest Trust: Engineering Truth

Source: DNO engineering records and formal design data.

Includes:

- Certified voltage
- Conductor specification
- Pole class/strength/height
- Transformer ratings/settings
- DNO baseline coordinates where survey-grade
- DNO inspection history and CNAIM scores
- Circuit loading and operational constraints

Use for final design inputs.

### Medium Trust: Current Condition Evidence

Source: Field photos, surveyor notes, and DNO map popup context.

Includes:

- Field-observed current condition
- Field-observed equipment presence
- Field-observed warning signs and markings
- Access constraints
- Support numbers from ENWL map popups
- Map marker context

Use for survey-to-design review, identity correlation, and verification planning.

### Lowest Trust: Field Inferences

Source: Visual or contextual inference from photos.

Examples:

- Voltage inferred from warning signs or equipment type
- Pole height estimated from photos
- Conductor type inferred visually
- Equipment rating inferred from visible form
- Structural condition inferred from distant/partial photos

Use only as tentative review notes. Do not use as final design inputs.

### Design Blockers

Final design cannot proceed without:

- DNO-confirmed voltage
- DNO-confirmed conductor specification
- DNO-confirmed pole class/strength/height where relevant
- DNO-confirmed transformer/rating/load data where relevant
- Designer review and sign-off
- Resolution of identity conflicts or MEDIUM/LOW confidence matches

---

## 6. GridFlow Pipeline Architecture

### Stage 4C.1 - Baseline Ingestion (COMPLETE)

Input:

- DNO/Trimble CSV

Processing:

```text
Parse -> Validate -> Normalize coordinates -> Normalize support numbers -> Reconstruct routes
```

Output:

- `BaselineDataset` JSON

Module:

- `gridflow/baseline/`

CLI:

- `scripts/ingest_baseline.py`

Key components:

- `csv_parser.py`
- `schema_validator.py`
- `coordinate_transformer.py`
- `support_number_normalizer.py`
- `route_reconstructor.py`
- `models.py`

### Stage 4C.2 - Field Evidence Import (IN PROGRESS)

Input:

- `enwl_enrichment_clean/` folder structure

Processing:

```text
Scan folders -> Extract metadata -> Parse notes -> Score evidence quality
```

Output:

- `FieldDataset` JSON

Module:

- `gridflow/field/`

CLI:

- `scripts/import_field_evidence.py`

Key components:

- `folder_scanner.py`
- `notes_parser.py`
- `evidence_quality_scorer.py`
- `dataset_validator.py`
- `models.py`

### Stage 4C.3 - Matching Engine (IN PROGRESS)

Input:

- `BaselineDataset` JSON
- `FieldDataset` JSON or normalized evidence dataset

Processing:

```text
Support number matching -> Confidence scoring -> Conflict detection -> Register building
```

Output:

- `MatchRegister` JSON/CSV

Module:

- `gridflow/matching/` (planned/in progress)

Current supporting CLIs:

- `scripts/generate_match_register.py`
- `scripts/calculate_match_rate.py`

Future CLI:

- `scripts/run_matching.py`

### Stage 4C.4 - Merge Engine (PLANNED)

Input:

- `MatchRegister`
- `BaselineDataset`
- `FieldDataset`

Processing:

```text
Data merge -> Verification flag generation -> QA reporting
```

Output:

- Merged dataset
- Designer review workspace feed
- QA report

Module:

- `gridflow/merge/` (to be built)

Planned CLI:

- `scripts/run_merge.py`

### Stage 5 - Designer Review UI (FUTURE)

Planned scope:

- Web interface for designer review
- Design blocker review
- Verification workflow
- PoleCAD/design handoff support
- DNO submission workflow support

---

## 7. Evidence Quality Scoring System

Confidence scores describe baseline-to-field identity correlation only.

### HIGH Confidence Identity Match

Criteria:

- Support number visible from ENWL map popup or clear evidence source
- 3+ field photos covering full pole and key visible context
- Field photos include pole top, base, and equipment where safely visible
- 1+ map screenshot with popup or location marker evidence
- Notes file with key observations
- No conflicting evidence

HIGH confidence does not mean design-ready.

### MEDIUM Confidence Identity Match

Criteria:

- Support number likely correct but minor uncertainty remains
- Evidence partially complete
- `NO_POLE_POPUP` scenario where support is inferred from route context
- Variant support number, such as `903201A`, where context is strong
- Map popup exists but field verification is incomplete

MEDIUM confidence requires designer/manual review before design workflow reliance.

### LOW Confidence Identity Match

Criteria:

- Support number unclear or missing
- Insufficient photo coverage
- Conflicting evidence
- Multiple nearby candidates
- Critical identifiers missing

LOW confidence requires manual resolution and possibly additional field evidence.

---

## 8. Support Number Reference

### Known Formats

ENWL pure numeric:

```text
903203
```

With suffix:

```text
903201A
```

With prefix:

```text
SP903203
EN903203
```

With separators:

```text
90-3203
```

### Normalization Rules

1. Strip leading/trailing whitespace.
2. Uppercase all letters.
3. Remove known prefixes such as `SP` and `EN` where they are not part of the true support identifier.
4. Remove separators such as hyphens and spaces for normalized matching.
5. Preserve letter suffixes (`A`, `B`, etc.) because they may indicate variant records.
6. Extract numeric core only for fallback matching or review support, not as the primary identity if suffix matters.

### Matching Guidance

- Exact normalized support number match is preferred.
- Variant suffix match should be flagged or recorded as variant if baseline/field disagree.
- Support-number conflict overrides coordinate proximity and requires manual review.

---

## 9. DNO Baseline CSV Formats

### ENWL Network Asset Viewer Export

Known/expected mappings:

- `ENID` -> `pole_id`
- `Support No` -> `support_no`
- `Easting` -> `easting` (OSGB36)
- `Northing` -> `northing` (OSGB36)
- `Latitude` -> `latitude` (WGS84, optional)
- `Longitude` -> `longitude` (WGS84, optional)
- `Feature` -> `feature_code`
- `Voltage` -> `voltage_level`
- `Structure Type` -> `asset_type`
- `Status` -> `status`

### Trimble Survey Export

Known/expected mappings:

- `Feature Code` -> `feature_code`
- `Point ID` -> `pole_id`
- `Point Name` -> `support_no`
- `Easting` -> `easting`
- `Northing` -> `northing`
- `Elevation` -> `elevation` (optional)

### Format Handling Rules

- Preserve unknown columns in metadata.
- Do not discard source columns without traceability.
- Validate coordinates and support numbers.
- Flag duplicates, missing identifiers, and malformed rows.
- Treat DNO-specific mappings as configurable where possible.

---

## 10. Coordinate Systems

### OSGB36 / British National Grid

OSGB36 uses easting/northing coordinates and is common in UK DNO and survey data.

GridFlow UK bounds check:

- Easting: `0` to `700000`
- Northing: `0` to `1300000`

### WGS84 / GPS

WGS84 uses latitude/longitude and is common in mobile mapping applications and GPS/GNSS data.

### Transformation

GridFlow uses coordinate transformation logic in `gridflow/baseline/coordinate_transformer.py`. The intended library is `pyproj` where available.

Transformation tolerance depends on source quality and configuration. Do not treat transformed or mobile coordinates as stronger than DNO baseline coordinates.

### GNSS Field Capture Limitations

Mobile GNSS can be around +/-5m or worse. It is not suitable as the primary pole position source when DNO baseline coordinates exist.

Always prefer baseline coordinates over field GPS for matching and design preparation.

---

## 11. Validation Results Record

### P_LOCAL_001 Canonical Validation Reference

P_LOCAL_001 is the canonical Stage 4B field evidence validation dataset.

- Date: May 2026
- Location: Rural ENWL network, Lancashire/Cumbria border area
- Poles surveyed: 10
- Dataset: `real_pilot_data/P_LOCAL_001/enwl_enrichment_clean/`
- Evidence compliance: 100% (all poles meet minimum requirements)
- Field photos: 60 total
- Map screenshots: 38 total
- Notes files: 10
- Match rate: 100% for identity correlation in the Stage 4B register
- Governance verdict: GO for Stage 4C controlled implementation planning, not final design authorization

### Edge Cases Validated

1. Pole 08: `900346` - `NO_POLE_POPUP`
   - Map popup was incomplete/uncertain.
   - Support identity was handled as an edge case requiring caution.

2. Pole 03: `903201A` - variant support number
   - A suffix preserved.
   - Demonstrates need to preserve variant support identifiers.

3. Pole 07: `903503` - joint user pole
   - Telecoms/joint-use context noted.
   - DNO infrastructure and non-DNO equipment must remain distinguishable.

4. Pole 06: `903101` - LV overhead/underground transition
   - ENWL evidence included overhead and underground LV context.
   - Transition details still require DNO/design verification.

5. Pole 05: `902204` and Pole 10: `902206` - HV transformer poles
   - Transformers documented from ENWL and field evidence.
   - Ratings and design implications remain DNO engineering data.

6. Pole 01: `903203` - LV terminal/streetlight context
   - Streetlight and LV terminal evidence handled.
   - Streetlighting/joint-use ownership remains a verification concern where applicable.

### Critical Limitation

P_LOCAL_001 is not design-ready data. It proves the evidence workflow and support-number correlation approach for this dataset structure. Final design still requires DNO-confirmed engineering values.

---

## 12. AI Tooling Strategy

### Tool Roles

Claude Desktop:

- Project orchestrator
- Planning and architecture
- Task design
- Domain/spec review

Codex / Cursor:

- Documentation
- Governance
- Domain knowledge consolidation
- Specification work
- Focused implementation when assigned

Claude Code / VS Code:

- Code implementation
- Testing
- Script execution
- Repository operations in controlled worktrees

Claude Code reserved for:

- Separate repos/worktrees
- Read-only review tasks
- Focused implementation/testing branches

### Prompt Engineering Notes

Future AI sessions should:

- Provide full file paths for code changes.
- Specify real dataset paths for integration tests.
- Reference AI_CONTROL document numbers when discussing methodology.
- State whether runtime/app files are allowed or forbidden.
- State whether real_pilot_data, uploads, and validation_runs must remain uncommitted.
- Treat pre-commit E501 warnings as cosmetic only if explicitly approved; otherwise fix or report them.
- Never infer technical engineering values from photos unless DNO records support them.

---

## 13. Glossary

ABC: Aerial Bundled Cable.

AAC: All Aluminium Conductor.

ACSR: Aluminium Conductor Steel Reinforced.

Baseline: DNO asset register or survey baseline data containing coordinates and identifiers.

CNAIM: Common Network Asset Indices Methodology, used for asset health/risk indexing.

DNO: Distribution Network Operator.

EHV: Extra High Voltage, generally 66kV and above.

ENA TS 43-88: Engineering Networks Association technical specification relevant to overhead line infrastructure and pole/birthmark standards.

ENID: ENWL asset identifier.

Field evidence: Surveyor-captured photos and notes.

GNSS: Global Navigation Satellite System, commonly device GPS/location.

HV: High Voltage, commonly 6.6kV, 11kV, or 33kV in UK distribution.

ICP: Independent Connection Provider.

LV: Low Voltage, generally 230V single phase or 400V three phase.

Match confidence: Reliability of baseline-to-field identity correlation.

NGED: National Grid Electricity Distribution.

NPG: Northern Powergrid.

OH: Overhead line.

OSGB36: Ordnance Survey Great Britain 1936 coordinate system, used for British National Grid easting/northing.

PoleCAD: Specialist overhead line design software.

SPEN: ScottishPower Energy Networks.

SSEN: Scottish and Southern Electricity Networks.

Support No: DNO field identifier for individual poles/supports.

UG: Underground cable.

UKPN: UK Power Networks.

Verification flag: Marker indicating data requires DNO confirmation or designer review before design use.

WGS84: World Geodetic System 1984, used for GPS latitude/longitude.
