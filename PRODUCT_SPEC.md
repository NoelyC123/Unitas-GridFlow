# GridFlow: Product Specification

## What GridFlow Is

GridFlow is a survey-to-design workflow tool for UK overhead line infrastructure. It bridges the gap between field survey and CAD design by turning baseline asset data and field evidence into a structured review package.

GridFlow helps teams:

- Ingest DNO baseline asset data such as pole locations, support numbers, route structure, and available asset metadata.
- Import structured field evidence such as photos, map screenshots, and surveyor notes.
- Correlate field evidence to baseline assets via support number matching.
- Generate a unified dataset with verification flags for designer review.
- Produce QA reports that clearly identify what DNO engineering data is still required.

GridFlow is NOT:

- An engineering design tool.
- A DNO data replacement.
- A compliance certifier.
- An automated design authorizer.
- A computer vision or AI image recognition system.

GridFlow identifies evidence, gaps, and blockers. It does not certify voltage, conductor specification, pole class, load capacity, asset health, or design compliance.

## Who Uses GridFlow

Primary users are field surveyors, infrastructure designers, ICP project managers, and Tier-1 contractors managing survey-to-design handoff across overhead line programmes.

A field surveyor uses GridFlow standards to capture evidence consistently. A designer uses GridFlow outputs to see what is ready for review and what still requires DNO records. A project manager uses the QA report to coordinate DNO data requests and reduce handoff ambiguity.

## Where GridFlow Sits in the Workflow

GridFlow sits between the field survey and formal design tooling:

```text
DNO instruction
-> baseline asset data
-> field capture
-> GridFlow processing
-> designer review
-> DNO data request / clarification
-> CAD or PoleCAD design
-> DNO submission
```

The key value is structured handoff. Instead of sending a designer a loose folder of photos, screenshots, and notes, GridFlow produces matched pole records, evidence summaries, confidence scores, and verification flags.

## Current Implementation Status (May 2026)

### Stage 4C.1: Baseline Ingestion Engine - COMPLETE

The baseline ingestion engine parses ENWL, Trimble, and generic CSV formats. It validates duplicates, invalid coordinates, missing fields, and malformed records. It transforms coordinates between OSGB36 and WGS84, normalizes support numbers, and reconstructs route sequences from spatial proximity.

Current module: `gridflow/baseline/`.

Current CLI: `scripts/ingest_baseline.py`.

Current baseline test count after audit: 61 tests.

### Stage 4C.2: Field Evidence Importer - COMPLETE CORE LIBRARY

The field evidence importer scans structured evidence folders using the `NN_SUPPORT_*` pattern. It extracts support numbers, voltage descriptors, special flags, photo counts, map screenshot counts, notes content, and evidence quality scores.

It has been validated against the P_LOCAL_001 evidence structure, including LV, HV, joint-user, variant support number, and no-pole-popup edge cases.

Current module: `gridflow/field/`.

Current CLI: `scripts/import_field_evidence.py`.

Current field test count after audit: 57 tests.

### Stage 4C.3: Matching Engine - COMPLETE CORE LIBRARY

The matching engine correlates baseline assets to field evidence using support number matching. It handles exact support matches, variant support numbers such as `903201A`, and prefix normalization such as `SP903203` to `903203`. It scores match confidence and detects support number or voltage conflicts.

P_LOCAL_001 achieved a 100% identity match rate in the Stage 4B/4C matching workflow.

Current module: `gridflow/matching/`.

Current supporting scripts: `scripts/generate_match_register.py`, `scripts/calculate_match_rate.py`.

Current matching test count after audit: 28 tests.

### Stage 4C.4: Merge Engine - IN PROGRESS

Stage 4C.4 will combine the baseline dataset, field dataset, and match register into a merged dataset. It will generate verification flags for missing engineering specifications and produce QA reports showing design blockers and required DNO actions.

This stage is specified in `AI_CONTROL/105_STAGE4C4_MERGE_ENGINE_SPEC.md`.

### Stage 5: Designer Review UI - PLANNED

Stage 5 will provide a web interface for designer review workflow, PoleCAD handoff investigation, DNO submission support, and multi-user deployment.

## Evidence Capture Methodology (Validated)

The P_LOCAL_001 field survey in May 2026 validated the practical capture workflow.

Equipment required:

- iPad or iPhone with ENWL Network Asset Viewer or equivalent DNO GIS app.
- Phone camera, acceptable for typical LV/HV timber pole evidence capture.
- Notes captured by voice memo, typed notes, or structured note template.

Per-pole process:

1. Open the DNO map app and navigate to the target pole.
2. Tap the pole marker and screenshot the popup showing support number and asset context.
3. Photograph the full pole structure.
4. Capture pole base, pole top, equipment, warning signs, access constraints, and context where safely visible.
5. Record observations such as condition, defects, equipment, access, and uncertainty.
6. Normalize evidence into the required GridFlow folder structure.

Typical time per straightforward pole is approximately 3-5 minutes. P_LOCAL_001 captured 10 poles in one field session and achieved a 100% baseline identity match rate.

## What GridFlow Can Determine From Field Evidence

GridFlow can populate or support review of:

- Support number from ENWL map popup or visible markings.
- Approximate location from map marker.
- Current visual condition from photos and notes.
- Visible defects such as rot, cracks, lean, splits, and access obstructions.
- Equipment presence such as transformers, streetlights, stays, warning signs, and visible cutouts.
- Warning sign presence and wording where readable.
- Access constraints such as roadside, footpath, private land, vegetation, and restricted visibility.
- Broad pole material from visual review, such as timber, steel, or concrete.

These are survey evidence fields, not engineering certification.

## What GridFlow Cannot Determine Without DNO Data

The following require formal DNO engineering records:

- Certified voltage specification.
- Conductor size, material, configuration, and rating.
- Pole class, strength rating, and manufactured height.
- Transformer ratings and protection settings.
- Asset installation date.
- DNO inspection history and CNAIM health index.
- Circuit loading data.
- Retention category and replacement priority.

Warning signs and field photographs are not reliable substitutes for DNO engineering data.

## DNO Data Requirements for Design

Before final design can proceed, the designer must obtain from the DNO:

1. Certified voltage for each pole on route.
2. Conductor specification: size, type, material, and rating.
3. Pole class/strength for retained poles.
4. Transformer ratings where applicable.
5. DNO inspection history where observed defects or age markers raise concern.
6. Special engineering constraints, ownership, joint-use, and access requirements.

GridFlow generates a QA report listing which poles need which data items. This becomes a structured DNO data request aid, not a replacement for the DNO response.

## Validation Evidence

P_LOCAL_001 validation, May 2026:

- ENWL rural network in the Lancashire/Cumbria border area.
- 10 poles surveyed.
- 60 field photos.
- 38 map screenshots.
- 10 notes files.
- 100% evidence compliance: every pole met minimum evidence requirements.
- 100% baseline identity match rate for the tested dataset.

Edge cases validated:

- `NO_POLE_POPUP` scenario.
- Joint-user pole.
- Variant support number, including `903201A`.
- Overhead-to-underground transition context.
- HV transformer poles.
- LV terminal/streetlight context.

Validation verdict: methodology is viable for controlled ICP survey-to-design workflows where evidence quality matches P_LOCAL_001. Caveat: this is a single controlled validation dataset. Broader validation across multiple sites, DNO regions, voltage levels, and evidence quality conditions is required before production deployment at scale.

## Limitations and Caveats

1. The primary validation dataset contains 10 poles only.
2. ENWL evidence has been validated most deeply; NGED, SPEN, SSEN, UKPN, and NPG formats need broader testing.
3. Current matching is support-number-led; coordinate fallback matching is not yet the core production path.
4. GridFlow does not perform image analysis. Evidence quality is based on file counts, folder structure, flags, and notes, not photo content recognition.
5. Notes parsing is heuristic. Free text may not parse consistently.
6. DNO data remains required for final design.
7. The toolchain is currently CLI/core-library oriented; the designer review UI is planned, not complete.

## Technical Stack

- Python 3.12+.
- Pydantic v2 for data validation and serialization.
- pyproj for coordinate transformation.
- pandas for CSV processing.
- pytest for validation.
- CLI interfaces for pipeline stages.

After the Stage 4C coverage audit, the baseline/field/matching target suite contains 146 tests and measured package coverage is 90% across `gridflow.baseline`, `gridflow.field`, and `gridflow.matching`.

## Roadmap

### Near Term (1-3 months)

- Complete Stage 4C.4 Merge Engine.
- Harden P_LOCAL_001 end-to-end CLI workflow.
- Broaden DNO format testing for NGED and SPEN.
- Validate on larger datasets of 100+ poles.

### Medium Term (3-6 months)

- Build Stage 5 Designer Review UI.
- Investigate PoleCAD integration points.
- Run ICP pilot with one or two contractors.
- Automate structured DNO data request reports.

### Long Term (6-12 months)

- Multi-user deployment.
- DNO API/GIS integration where legally and technically available.
- CNAIM/inspection data integration where supplied by DNO.
- DNO submission workflow support.

## Intellectual Property and Data Governance

GridFlow code is held in the private `NoelyC123/Unitas-GridFlow` repository.

Field evidence data is local only and excluded from git. Real pilot photos, real survey CSVs, uploaded baselines, and validation outputs must not be committed unless explicitly approved and anonymised.

DNO baseline data is subject to DNO access terms. Surveyor notes and photos are client confidential and must be treated as project evidence, not public documentation.
