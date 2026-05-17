# P_LOCAL_002 Coordinate Extraction Attempt

**Date:** 2026-05-17
**Scope:** Supports `903101` and `903203` only
**Purpose:** Attempt conservative extraction of missing baseline coordinates from existing ENWL screenshots, map screenshots, and pole notes.

---

## Result Summary

| Support | FID | Coordinate extracted? | Confidence | Baseline CSV updated? | Next action |
| --- | --- | --- | --- | --- | --- |
| 903101 | 16788439 | No | Low | No | Manual ENWL lookup required |
| 903203 | 16938106 | No | Low | No | Manual ENWL lookup required |

The current evidence pack does not expose a defensible exact easting/northing or exact
lat/lon readout for either support. The baseline CSV was not updated.

---

## Files Checked

### Pole 10 — Support 903101

**ENWL screenshots checked**

- `10_SUPPORT_903101/enwl_screenshots/IMG_1012.jpg`
- `10_SUPPORT_903101/enwl_screenshots/IMG_1013.jpg`
- `10_SUPPORT_903101/enwl_screenshots/IMG_1014.jpg`
- `10_SUPPORT_903101/enwl_screenshots/IMG_1015.jpg`
- `10_SUPPORT_903101/enwl_screenshots/IMG_1016.jpg`

**Map screenshots checked**

- `10_SUPPORT_903101/map_screenshots/IMG_1003.jpg`

**Notes checked**

- `10_SUPPORT_903101/notes/pole_notes.md`

### Pole 12 — Support 903203

**ENWL screenshots checked**

- `12_SUPPORT_903203_LV_TERMINAL_STREET_LIGHT/enwl_screenshots/Image 17-05-2026 at 15.13.jpg`
- `12_SUPPORT_903203_LV_TERMINAL_STREET_LIGHT/enwl_screenshots/Screenshot 2026-05-17 at 15.10.53.png`
- `12_SUPPORT_903203_LV_TERMINAL_STREET_LIGHT/enwl_screenshots/Screenshot 2026-05-17 at 15.11.19.png`
- `12_SUPPORT_903203_LV_TERMINAL_STREET_LIGHT/enwl_screenshots/Screenshot 2026-05-17 at 15.11.37.png`
- `12_SUPPORT_903203_LV_TERMINAL_STREET_LIGHT/enwl_screenshots/Screenshot 2026-05-17 at 15.11.51.png`

**Map screenshots checked**

- `12_SUPPORT_903203_LV_TERMINAL_STREET_LIGHT/map_screenshots/IMG_1022 2.jpg`
- `12_SUPPORT_903203_LV_TERMINAL_STREET_LIGHT/map_screenshots/IMG_1026.jpg`
- `12_SUPPORT_903203_LV_TERMINAL_STREET_LIGHT/map_screenshots/IMG_1027.jpg`

**Notes checked**

- `12_SUPPORT_903203_LV_TERMINAL_STREET_LIGHT/notes/pole_notes.md`

---

## Pole 10 Findings — Support 903101 / FID 16788439

### Confirmed from ENWL screenshots

- Support number: `903101`
- FID: `16788439`
- SPN: `61090L03101`
- Pole type: `Section`
- Pole class text: `Single Wood Pole`
- Voltage context visible in nearby screenshots: `415V` LV route context

### Coordinate search result

- No screenshot displayed a readable easting/northing pair.
- No screenshot displayed a readable decimal latitude/longitude pair.
- The map screenshot `IMG_1003.jpg` shows the route context and OCR captured only
  `accuracy 2.9m`, not a location coordinate.
- Notes already state: `exact coordinates should be taken from ENWL baseline export if required`.

### Extraction confidence

**Low / insufficient for baseline update**

There is no defensible exact coordinate value visible in the checked evidence.

---

## Pole 12 Findings — Support 903203 / FID 16938106

### Confirmed from ENWL screenshots

- Support number: `903203`
- FID: `16938106`
- SPN: `61090L03203`
- Pole type: `Terminal`
- Pole class text: `Single Wood Pole`
- Nearby conductor context visible: `240V` LV conductor
- Nearby sleeve/termination context visible: `415V` sleeve_lv

### Coordinate search result

- No screenshot displayed a readable easting/northing pair.
- No screenshot displayed a readable decimal latitude/longitude pair.
- The new ENWL screenshots captured 2026-05-17 confirm identity and nearby network
  context, but they do not expose a defensible exact coordinate readout.
- The map screenshots show route position and annotated circles, not extractable coordinates.

### Extraction confidence

**Low / insufficient for baseline update**

There is no defensible exact coordinate value visible in the checked evidence.

---

## Baseline CSV Outcome

File checked:

- `real_pilot_data/P_LOCAL_002/csv/P_LOCAL_002_baseline.csv`

Rows remain unchanged:

- `903101,,,LV,overhead line support/pole,existing`
- `903203,,,LV,overhead line support/pole,existing`

**Baseline CSV updated:** No

Reason: conservative methodology applied; no coordinates were inserted without a readable source.

---

## Methodology Note

Only clearly readable, defensible coordinate values should be inserted into the baseline.
Adjacent route geometry, nearby labels, OCR fragments, or visual estimation from map screenshots
are not sufficient for baseline truth data.

---

## Required Manual Follow-up

Manual ENWL lookup required for:

- Support `903101` / FID `16788439`
- Support `903203` / FID `16938106`

Recommended source:

- ENWL Network Asset Viewer pole popup or direct baseline export that shows exact coordinates

Once readable coordinates are obtained from that authoritative source, update:

- `real_pilot_data/P_LOCAL_002/csv/P_LOCAL_002_baseline.csv`
- relevant `pole_notes.md`
