# GridFlow Surveyor Guide

## What You Are Capturing

GridFlow uses your field evidence to help a designer understand which overhead line poles have been surveyed, how confidently each pole matches the DNO baseline record, and what engineering data still needs to be requested from the DNO before design.

For each pole, you are capturing three things:

- A map screenshot that shows the DNO support number and pole location.
- Field photos that show the pole, base, top, equipment, and visible condition.
- Notes that explain what you saw, what you could not confirm, and any access or safety constraints.

The support number is the critical identifier. It links your field evidence to the DNO baseline record. Your photos and notes do not replace DNO engineering records, but they give the designer a structured, auditable survey record instead of an unorganised photo set.

## Equipment Required

- Device with ENWL Network Asset Viewer, or equivalent DNO map/GIS viewer for the area.
- Camera. A phone camera is acceptable if images are clear.
- This guide, printed or saved on your device.
- Project list or route map showing the poles to survey.
- Battery pack if the survey will take more than a few hours.
- Standard PPE and site safety equipment required by your employer.

## Before You Start

- Confirm the survey area and target pole list before leaving site base.
- Download or preload pole locations in the ENWL app, or equivalent map app, where possible.
- Create a folder for today's survey on your device.
- Note the date, weather, visibility, and access conditions.
- Check whether any poles are on private land, near traffic, behind vegetation, or otherwise difficult to access.
- Do not enter private land or restricted areas unless you have explicit permission and the required safety controls.

## For Each Pole

### Step 1: Open the Map App

Navigate to the target pole in the map app.

Tap the pole marker to open the popup. The popup should show the support number. This is the critical identifier used to match your field evidence to the DNO baseline record.

If several poles are close together, check the map carefully before photographing. Use nearby landmarks, road position, route direction, and pole sequence to avoid mixing evidence from different poles.

### Step 2: Screenshot the Popup

Take a screenshot showing:

- The support number clearly visible.
- The pole marker on the map.
- Any asset details shown in the popup.

Save the screenshot in the pole folder under `map_screenshots/`.

If the pole has no popup:

- Screenshot the map showing the approximate location and marker context.
- Note in your observations: `No popup available - location approximate`.
- The system can still process this pole, but it will normally be treated as lower confidence and will require manual review.

### Step 3: Photograph the Pole

Minimum photos required for each pole:

1. Full pole: stand back far enough to see the whole pole in frame.
2. Base: close-up of ground level. Look for rot, damage, buried base, or access restrictions.
3. Top: photograph crossarms, insulators, conductors, and any pole-mounted equipment from a safe position.

Additional photos if present:

4. Equipment: transformers, cutouts, switches, cable terminations, or other apparatus.
5. Warning signs: close-up of danger plates, voltage signs, or DNO markings.
6. Defects: cracks, lean, splits, rot pockets, woodpecker holes, damaged stays, or other visible problems.
7. Context: access route, vegetation, road position, nearby structures, or anything that explains survey limitations.

Do not climb poles. Do not touch conductors, stays, equipment, or exposed apparatus. Use safe public vantage points unless authorised access has been arranged.

### Step 4: Record Observations

Use this standard notes template. Write `unknown` where something cannot be confirmed.

```text
POLE IDENTITY
Support No: [from map popup]
Type: TIMBER / STEEL / CONCRETE / UNKNOWN
Voltage: LV / HV / UNKNOWN
Note: Record voltage only from visible signs or DNO map information. Do not guess.

LOCATION
Address/Landmark: [nearest house number, road name, field gate, junction, or landmark]
Access: ROADSIDE / FOOTPATH / RESTRICTED / PRIVATE LAND / VEGETATION LIMITED

CONDITION
Overall: GOOD / FAIR / POOR / UNKNOWN
Base: Sound / Rot present / Damage visible / Cannot see / Buried / Vegetation obscured
Top: Intact / Weathered / Damaged / Partly visible / Not visible
Lean: None / Slight / Moderate / Severe / Unknown
Lean direction: N / S / E / W / NE / NW / SE / SW / Unknown
Defects: [list unusual items, or write "None observed"]

EQUIPMENT OBSERVED
Warning Signs: Present / Absent / Not visible - [describe if present]
Transformer: Yes / No / Unknown - [describe if visible]
Stay wire: Yes / No / Unknown - [describe anchor type if visible]
Street light: Yes / No / Nearby separate column / Unknown
Other: [cutouts, switchgear, telecoms, cable terminations, joint user equipment]

VERIFICATION REQUIRED
[List anything you could not confirm: voltage, conductor type, pole class, height, equipment rating, identity, access]

SPECIAL NOTES
[Anything unusual about this pole, access, weather, visibility, or survey conditions]
```

### Step 5: Organise Your Files

Name the pole folder using this pattern:

```text
NN_SUPPORT_{support_number}_{short_descriptor}
```

Example:

```text
01_SUPPORT_903203_LV_TERMINAL_STREETLIGHT
```

Inside the folder, create three subfolders:

```text
NN_SUPPORT_903203_LV_TERMINAL_STREETLIGHT/
  field_photos/
  map_screenshots/
  notes/
```

Place all pole photos in `field_photos/`, all map screenshots in `map_screenshots/`, and save your notes as `notes/identity_notes.txt`.

## Common Situations

### Joint User Poles

If telecoms, street lighting, private apparatus, or other non-DNO equipment is present, note it clearly:

```text
Joint user - telecoms equipment present.
```

Photograph the non-DNO apparatus separately if it is safe and visible. Do not assume ownership unless it is labelled.

### HV Poles Without Warning Signs

Do not guess voltage from height or equipment alone. Use cautious wording:

```text
Voltage unknown - no warning sign visible. Equipment suggests possible HV, requires DNO verification.
```

The designer must still obtain certified voltage from DNO records.

### Restricted Access Poles

Photograph from the nearest safe public vantage point. Do not trespass.

Record:

```text
Access restricted - photographed from public road/footpath at approximately [distance] metres.
```

Add what was not visible, such as base, pole plate, stay anchor, or top equipment.

### Vegetation or Distance Limits

If vegetation, hedges, fencing, or distance limits the view, record this as a valid survey constraint:

```text
Vegetation limits inspection access. Pole top partly visible. Base not visible.
```

Do not fill technical fields from guesswork.

### Poles With Severe Defects

If a pole appears structurally unsafe, do not approach. Photograph from a safe distance and report it through your normal safety process.

Use direct wording:

```text
SAFETY CONCERN - severe visible defect. Photographed from safe distance. Requires supervisor/DNO review.
```

## File Naming Reference

Field photos can use descriptive names:

```text
pole_full_001.jpg
pole_base_001.jpg
pole_top_001.jpg
equipment_001.jpg
warning_sign_001.jpg
defect_001.jpg
context_001.jpg
```

Map screenshots should identify the support number where possible:

```text
map_popup_903203.png
map_location_no_popup_001.png
```

Notes file:

```text
identity_notes.txt
```

## Quality Checklist

Before moving to the next pole, check:

- [ ] Map popup screenshot taken.
- [ ] Support number visible, or no-popup issue recorded.
- [ ] At least three field photos taken: full pole, base, top.
- [ ] Equipment and warning signs photographed if present.
- [ ] Notes completed for identity, condition, access, equipment, and unknowns.
- [ ] Files saved in the correct pole folder.
- [ ] Any access, visibility, or safety limitation recorded honestly.

## What Happens to Your Data

GridFlow will use your evidence to:

1. Match field evidence to DNO baseline records.
2. Score the confidence of each baseline-to-field identity match.
3. Identify missing or weak evidence.
4. Produce a QA report for the designer.
5. List the DNO engineering data still required before design.

Your field evidence helps the designer prepare a structured data request and reduces uncertainty during survey-to-design handoff. It does not certify voltage, conductor size, pole class, or design suitability. Those items still require DNO engineering records and designer review.
