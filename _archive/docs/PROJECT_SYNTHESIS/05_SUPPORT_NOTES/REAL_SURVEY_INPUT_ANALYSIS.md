# Real Survey Input Analysis

**Created:** 21 April 2026
**Purpose:** Record findings from the first review of real Electricity Worx survey-origin files.
These findings should directly inform intake/normalisation design decisions.

---

## Files reviewed

| File | Type | Job |
|---|---|---|
| `28-14 4-474.csv` | Trimble CSV export | 4-474 (Strabane area, NI) |
| `28-14 474c.csv` | Trimble CSV export | 474c (Strabane area, NI) |
| `28-14 513 (2).csv` | Trimble CSV export | 513 (NI) |
| `28-14 474c.job` | Trimble binary .job file | 474c |
| `28-14 Strabane Main PT.3 - 4-474.png` | ArcGIS/SpatialNI design print | 4-474 |
| `Capture (1).PNG` | PoleCAD design drawing | 513/515 area |
| `img_2025-03-03-22-19-28.jpg` | Handwritten field notebook sketch | 5/474 |
| `Image 2025-03-26 15-17-01.jpeg` | Handwritten field notebook sketch | 513 |
| (additional site photos) | Field photos | various |

---

## Finding 1 — Real Trimble CSV format is structurally different from current sample schema

**This is the most important finding.**

The current sample data in the repo uses a flat named-column schema:
```
asset_id, structure_type, height_m, material, location_name, easting, northing, latitude, longitude
```

The real Trimble CSV export format is completely different. It is a variable-width, feature-coded
format. Each row is a survey point with positional data followed by feature-code attributes.

### Real format structure

**Row 1:** Job metadata header
```
Job:28-14 4-474,Version:24.00,Units:Metres
```

**Row 2:** Base station / PRS record
```
PRS485572899536,219497.298,413575.610,118.985,
```

**Subsequent rows:** Survey point records
```
point_id, easting, northing, height, feature_code, [feature_code]:STRING, string_number,
[feature_code]:TAG, tag_value, [feature_code]:REMARK, remark_text,
[feature_code]:LAND USE, land_use[, [feature_code]:HEIGHT, feature_height]
```

### Real feature codes observed

| Code | Meaning |
|---|---|
| `Pol` | Survey pole (position marker, not a structure) |
| `Angle` | Angle pole (structural — a real OHL pole at a change of direction) |
| `EXpole` | Existing pole (surveyed existing structure, height measured) |
| `Fence` | Fence crossing or constraint |
| `Wall` | Wall crossing or constraint |
| `Road` | Road crossing |
| `Track` | Track crossing |
| `Hedge` | Hedge constraint |
| `Tree` | Tree constraint / obstruction |
| `LVxing` | Low Voltage line crossing (height measured) |
| `BTxing` | British Telecom line crossing (height measured) |
| `Ignore` | Point flagged for exclusion (tag value = `I`) |

### Real remark examples (design-critical context)

- `4a-474 sect` — section identifier on an existing pole
- `4b-474 section ang` — angle pole with section reference
- `lv pole 1` — LV pole reference
- `4-474 new pos` / `4-474 ex pos` — new and existing position flags
- `474c term` — terminal pole
- `474a sect ang` — section angle designation
- `474 sect 4way` — 4-way section junction
- `513 convert to tee` — structural conversion instruction
- `new term pole pos` / `new pole` — new pole position flags
- `thin` / `thick` — informal conductor notes on BT crossings

These remarks carry critical design context. They are not structured fields — they are
free-text attached to individual points and must be preserved and surfaced, not discarded.

---

## Finding 2 — The .job file is proprietary binary and not the first parsing target

The `28-14 474c.job` file is a Trimble General Survey Journal binary file. Its header reads
`Trimble General Survey Journal` followed by binary data. It is not human-readable and cannot
be parsed without a Trimble SDK or significant reverse engineering.

**Decision:** Do not treat the .job file as an intake target. The CSV export is the practical
and realistic intake path. This is what surveyors already export and what the office already
handles. Start there.

---

## Finding 3 — Ignore-tagged rows must be excluded during normalisation

Point 10000 in `28-14 474c.csv` is tagged with `Ignore:TAG, I`. This is the Trimble mechanism
for marking a point as excluded from output. The normalisation layer must detect and drop these
rows before QA processing.

Ignore detection rule: if the `TAG` field for a point equals `I`, exclude the row entirely.

---

## Finding 4 — NI coordinate system is TM65 Irish Grid / ITM, not OSGB36

The coordinates in all three CSVs are in Irish Grid (TM65 / EPSG:29902 or ITM / EPSG:2157):
- Eastings: ~242,000–245,000
- Northings: ~402,000–413,000

The ArcGIS design print confirms: "Coordinate System: TM65 Irish Grid"

The current `coord_consistency` check in `app/qa_engine.py` converts lat/lon to OSGB27700
(EPSG:27700 — British National Grid). **This projection is wrong for Northern Ireland data.**
For NI jobs, the correct target CRS is either EPSG:29902 (TM65 Irish Grid) or EPSG:2157 (ITM).

This means:
- The current `coord_consistency` check will produce incorrect results for any NI job.
- The NIE_11kV rulepack's coord_consistency rule is currently using the wrong projection.
- The fix requires either: (a) detecting NI coordinates and switching CRS, or (b) making the
  target CRS configurable per rulepack.

---

## Finding 5 — Handwritten notes confirm the real handoff gap

Two handwritten field notebook sketches were reviewed:

**Job 5/474:** Shows an angle pole with stay geometry hand-drawn. Annotated: "Fit1 new ang stay
at 6m", position markers, "3m" offset, "ex pos" (existing position). This geometric and
positional detail is absent from the CSV entirely.

**Job 513:** Shows a pole with "0.5m" and "2m" offset annotations, a hedge, a drain, and a
"Post" reference. Annotated: "Fit x2 new toff stays at 6+4 mtendum." The drain clearance,
hedge proximity, and stay anchor offset are structurally absent from the CSV.

**Implication:** The tool cannot ingest handwritten context — but it can and should flag that
certain types of constraint context (stays, crossings, clearances) are likely to exist and may
not be in the structured data. QA checks that surface "no stay/crossing context recorded for
angle pole" are valuable precisely because of this gap.

---

## Finding 6 — The design images confirm the product identity

The ArcGIS print and PoleCAD drawing show exactly the kind of output that sits downstream of
the intake process. The design print has stay positions, route lines, and junction annotations.
The PoleCAD drawing has annotated work instructions per pole.

These are what designers produce after they have trusted the survey input. The tool sits one
step before this — validating the input so that this design work starts from a clean base.

---

## Implications for next development priorities

1. **Real Trimble CSV intake/normalisation is now a higher-priority concern than further
   rulepack expansion.** The current normalisation layer cannot process real survey files.
   Without this, the tool cannot be demonstrated on real data to any user.

2. **The coord_consistency check needs CRS-awareness.** At minimum, the NIE_11kV rulepack
   should use ITM/TM65 as its target CRS, not OSGB27700.

3. **The Ignore-row filter must be implemented before any real-data processing is attempted.**

4. **Feature code mapping is the core normalisation challenge.** The real intake requires
   mapping Trimble feature codes (Angle, EXpole, LVxing, etc.) to the internal schema used
   by the QA engine. This is non-trivial and will require careful design.

5. **Remark text must be preserved.** It carries design-critical context that should be
   surfaced in the issue report and map view, not silently dropped.

---

## What this does NOT change

- The project rationale and narrow scope remain correct.
- The rulepack architecture (SPEN, SSEN, NIE, etc.) is still the right approach.
- The QA engine check types are still the right pattern.
- The overall MVP flow (upload → QA → map → PDF → jobs) is still correct.

What changes is the **input layer** — the normalisation step must be rebuilt around the real
Trimble format rather than the assumed flat schema. Everything downstream of that can stay.
