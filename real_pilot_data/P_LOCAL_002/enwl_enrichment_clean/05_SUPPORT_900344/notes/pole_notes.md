# P_LOCAL_002 — Pole 05 — Support 900344

## Survey identity

Survey ID: P_LOCAL_002
Route: Jolly’s Farm / Station Road / Carnforth area
DNO: ENWL / Electricity North West
Network type: 11kV overhead route
Pole folder: 05_SUPPORT_900344

---

## Safety note

All observations are from ground-level visual inspection, photographs, map screenshots, GPS/map pin evidence, and ENWL Network Asset Viewer records.

No pole, stay, switch, conductor, transformer, cabinet, fence, or electrical equipment was touched, opened, climbed, operated, or interfered with.

Where something cannot be confirmed from the evidence, it is marked as uncertain rather than guessed.

---

## Field status

Support number: 900344
Physical field plate / marking: 90 03 44 visible
Pole FID: 16869657
SPN: 61090H00344
Location/context: Jolly’s Farm / Station Road / Carnforth area
Access: private land / farm access
Permission: landowner permission obtained before survey

GPS/map pin:

- Latitude: 54.196464
- Longitude: -2.733156
- GPS accuracy shown: 6.4 m

Evidence status: strong / confirmed.

---

## ENWL pole record

Source: ENWL Network Asset Viewer screenshot
Record type: pole

- fid: 16869657
- orientation: 252.417
- pole_type: Intermediate
- pole_class: Single Wood Pole
- support_diameter: Stout
- support_no: 900344
- spn: 61090H00344

Evidence status: confirmed from ENWL screenshot.

Important note:

Although the ENWL pole_type is listed as Intermediate, this pole also has associated switching / ABS equipment evidence. It should not be treated as a plain through-pole only.

---

## Field photo observations

Field photo evidence shows:

- Single wood pole
- 11kV overhead conductors visible
- Pole-mounted switching / isolator style equipment visible
- ENWL warning sign visible
- ENWL emergency contact label visible
- JOLLYS FM ABS / 654678 label visible
- Physical field plate / marking visible as 90 03 44
- Pole located near farm buildings / field boundary
- Fence and farm access context visible
- Top visible: YES
- Base visible: YES / PARTIAL depending on photo angle
- Vegetation obstruction: not major from provided evidence
- Transformer visible: NO clear transformer visible in field photos
- Stay wire visible: uncertain / not clearly confirmed
- Cable down pole / UG transition: not clearly confirmed from field photos

Evidence status: strong photo evidence.

---

## ENWL switch / equipment record

Source: ENWL Network Asset Viewer screenshots
Record type: Fault Making Switch

- asset type/title: Fault Making Switch
- fid: 73189925
- orientation: 224.787
- voltage: 11kV
- switch_type: Isolator Pole Mounted Class 4
- feat_code: isolator
- fid_polestructure: 16869657
- fid_substation: 73190411
- environment: Pole Mounted
- indoors: Outdoor
- normal_status: Closed
- plant_file_ref: 6546784DI01
- spn: 6546784SW001

Important interpretation:

The ENWL switch record directly references fid_polestructure 16869657, which matches the Pole 5 pole FID. This is strong evidence that the visible pole-mounted equipment is associated with this pole.

The field label JOLLYS FM ABS / 654678 also aligns with the plant reference 654678.

Evidence status: high confidence ENWL equipment association.

---

## ENWL support-mounted plant / substation context

Source: ENWL Network Asset Viewer screenshots
Record type: Substation / support-mounted plant context

- fid: 73190411
- substation_type: Support Mounted
- infeed_voltage: 11kV
- outfeed_voltage: 11kV
- plant_file_ref: 654678

Important interpretation:

This supports the JOLLYS FM ABS / 654678 equipment context seen in the field photos and ENWL switch record.

Evidence status: high confidence DNO plant context.

---

## ENWL conductor evidence near Pole 5

### Conductor record 1

Source: ENWL Network Asset Viewer screenshot
Record type: HV Conductor

- fid: 73190266
- voltage: 11kV
- material: Aluminium Alloy Stranded
- cable_class: HV Overhead
- cable_size: 50mm2
- installation_medium: Overhead
- insulation: Uninsulated
- no_core_wires: 3
- phases_connected: Three Phase
- reduced_neutral: No
- operating_voltage_colour: #FF0000
- text_map: 3x 50 Al 11

### Conductor record 2

Source: ENWL Network Asset Viewer screenshot
Record type: HV Conductor

- fid: 73190215
- voltage: 11kV
- material: Aluminium Alloy Stranded
- cable_class: HV Overhead
- cable_size: 50mm2
- installation_medium: Overhead
- insulation: Uninsulated

### Nearby route label evidence

Map screenshots show nearby route labels including:

- 3x 50 Al 11 on the main overhead route
- 3x .025 Cu 11 on a nearby branch/span
- 3c 185 SAC XC TP on nearby underground / transition route context around Jolly’s Farm / Station Road

Important caution:

Do not automatically apply every nearby conductor record to every pole or span.

ENWL conductor evidence is DNO network evidence/provenance only until the exact conductor FID to span/pole relationship is proven.

---

## Route / map context

Map screenshots show Pole 5 / support 900344 on the red 11kV overhead route near Jolly’s Farm.

Nearby route context includes:

- support 900343 upstream / nearby
- support 900345 downstream / nearby
- farm buildings / field boundary
- Jolly’s Farm ABS / 654678 equipment context
- 11kV overhead route continuing through open field/farm land

GPS/map pin evidence:

- 54.196464, -2.733156
- GPS accuracy shown: 6.4 m

Evidence status: strong.

---

## Access observations

Access type: private land / farm field
Permission required: YES
Permission obtained: YES
Viewed from: field / farm boundary area
Safe access: YES from ground only
Base visible: YES / PARTIAL
Top visible: YES
Blocked by hedge/trees: NO major blockage visible
Livestock/farm context: farm environment nearby
Hazards: normal farm field hazards, fences, uneven/wet ground possible

---

## GridFlow interpretation

Pole 05 is a high-value evidence case because it links:

- field photo evidence
- visible support plate / marking 90 03 44
- visible JOLLYS FM ABS / 654678 field label
- ENWL pole record
- ENWL switch / isolator record
- ENWL support-mounted plant / substation context
- ENWL conductor records
- GPS/map pin evidence
- route map context

This pole should be treated as an equipment-bearing 11kV pole record, not a simple intermediate through-pole only.

This is an important Stage 6 test case because GridFlow must handle poles with associated switching / ABS equipment, not just ordinary through poles.

---

## Evidence quality

Identity evidence: HIGH
Field photo evidence: HIGH
ENWL pole evidence: HIGH
ENWL switch / plant evidence: HIGH
Map / GPS evidence: HIGH
Conductor context: HIGH, but exact span linking still needs review
Access/context evidence: HIGH

---

## Current uncertainties

- Confirm exact span direction to Pole 04 and Pole 06.
- Confirm whether any stay wire is present from full-resolution field photos.
- Confirm exact conductor FID-to-span relationship before using conductor data in readiness logic.
- Operational switch status should be treated as time-specific ENWL record evidence.
- Do not mark this pole design-ready from ENWL evidence alone.

---

## Design-readiness caution

This ENWL evidence is DNO network evidence/provenance. It should not automatically clear design-readiness until the linking chain is proven:

ENWL trace/conductor FID
→ span/baseline asset
→ pole/support
→ GridFlow merged pole record
→ design-readiness decision

---

## Summary

Pole 05 / Support 900344 is a strong matched evidence record.

Confirmed items:

- support number 900344
- physical field plate / marking 90 03 44
- pole FID 16869657
- SPN 61090H00344
- GPS/map pin 54.196464, -2.733156
- 11kV overhead context
- main nearby conductor evidence: 3x 50 Al 11
- pole-mounted switch / ABS-style equipment visible
- JOLLYS FM ABS / 654678 label visible
- ENWL switch record linked to pole structure FID 16869657
- support-mounted plant / substation context FID 73190411

GridFlow use:

Use this as field + ENWL evidence/provenance for P_LOCAL_002.

Do not use it to automatically mark the pole design-ready until the conductor/span/pole linking process is proven and tested.
