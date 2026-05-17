# P_LOCAL_002 Coordinate Completeness Review

**Date:** 2026-05-17
**Survey:** P_LOCAL_002
**Reviewer:** GridFlow evidence review
**Scope:** Baseline coordinate completeness for supports 903101 and 903203

---

## Summary Verdict

**CONDITIONAL COMPLETE**

10 of 12 baseline records contain easting and northing coordinates.
2 gaps remain: supports 903101 and 903203.
No readable coordinate value has been found in any current structured text source for either gap.
P_LOCAL_002 cannot be marked 12/12 coordinate complete at this time.

---

## Evidence Files Checked

| File | Purpose | Coordinate data found? |
|---|---|---|
| `csv/P_LOCAL_002_baseline.csv` | Authoritative baseline — easting/northing per support | Yes for 10/12; 903101 and 903203 rows are blank |
| `enwl_enrichment_clean/10_SUPPORT_903101/notes/pole_notes.md` | Pole notes — Pole 10 identity and evidence record | No numeric coordinate; defers to ENWL baseline export |
| `enwl_enrichment_clean/12_SUPPORT_903203_LV_TERMINAL_STREET_LIGHT/notes/pole_notes.md` | Pole notes — Pole 12 identity and evidence record | Explicitly states no legible coordinate in current screenshot set |
| `csv/P_LOCAL_002_field_capture.csv` | Field capture quality index | No GPS coordinates recorded per pole |
| `route_notes/P_LOCAL_002_ROUTE_NOTES.md` | Route-level context notes | Coordinates for Pole 01 (902202) only; no 903101 or 903203 data |
| `route_notes/P_LOCAL_002_POLE_REMAP_REGISTER.md` | Pole identity remap register | All rows TBD — not populated |
| `route_notes/P_LOCAL_002_EVIDENCE_AUDIT.md` | Automated folder/evidence audit (run 2026-05-17 17:31:53) | Evidence structure only; no coordinates |

---

## Coordinate Status — Support 903101 (Pole 10)

**Baseline CSV row:**

```
903101,,,LV,overhead line support/pole,existing
```

Easting: **blank**
Northing: **blank**

**Pole notes statement (line 7 of `10_SUPPORT_903101/notes/pole_notes.md`):**

> "Coordinates: ENWL pole popup/map evidence present; exact coordinates should be
> taken from ENWL baseline export if required."

This statement defers coordinate authority to the ENWL baseline export. The ENWL baseline
export is represented by `P_LOCAL_002_baseline.csv`, which has no value for this row.
No numeric lat/lon, BNG easting, or BNG northing value is recorded in any current
structured text file for support 903101.

**ENWL FID and SPN confirmed:** FID 16788439, SPN 61090L03101 (from pole notes).
The FID could be used to query the ENWL Network Asset Viewer or a future ENWL API export
to retrieve a definitive coordinate for this support.

**Status: UNRESOLVED — coordinate not available from current evidence**

---

## Coordinate Status — Support 903202 (Pole 11) — FOR COMPLETENESS

**Baseline CSV row:**

```
903202,352591.794,478368.481,LV,overhead line support/pole,existing
```

Easting: **352591.794** (BNG)
Northing: **478368.481** (BNG)

**Pole notes also record:** `Coordinates from map screenshot: 54.198866, -2.728193`
(WGS84 lat/lon from map screenshot OCR)

Support 903202 is coordinate-complete in the baseline CSV and additionally has a WGS84
reference in the notes. No gap exists for this support.

**Status: COMPLETE**

---

## Coordinate Status — Support 903203 (Pole 12)

**Baseline CSV row:**

```
903203,,,LV,overhead line support/pole,existing
```

Easting: **blank**
Northing: **blank**

**Pole notes statement (line 8 of
`12_SUPPORT_903203_LV_TERMINAL_STREET_LIGHT/notes/pole_notes.md`):**

> "Coordinates: ENWL screenshots reviewed, including the 2026-05-17 captures; no exact
> lat/lon or BNG coordinate text is legible in the current screenshot set."

This explicitly states that the reviewer checked all available screenshots, including the
fresh 2026-05-17 captures, and found no readable coordinate value. No numeric lat/lon, BNG
easting, or BNG northing appears in any current structured text file for support 903203.

**ENWL FID and SPN confirmed:** FID 16938106, SPN 61090L03203 (from pole notes).
As with 903101, the FID can be used to query ENWL directly for a definitive coordinate.

**Status: UNRESOLVED — coordinate not available from current evidence**

---

## Is P_LOCAL_002 12/12 Coordinate Complete?

**No.**

| Support | Baseline easting | Baseline northing | Status |
|---|---|---|---|
| 902202 | 352320.762 | 478329.889 | ✅ Complete |
| 902201 | 352221.727 | 478286.517 | ✅ Complete |
| 900343 | 352167.633 | 478191.938 | ✅ Complete |
| 900342A | 352091.574 | 478262.612 | ✅ Complete |
| 900344 | 352265.248 | 478104.573 | ✅ Complete |
| 900345 | 352264.657 | 478104.134 | ✅ Complete |
| 903104 | 352466.531 | 478154.454 | ✅ Complete |
| 903103 | 352457.034 | 478213.974 | ✅ Complete |
| 903102 | 352442.689 | 478259.078 | ✅ Complete |
| **903101** | **blank** | **blank** | ❌ Gap |
| 903202 | 352591.794 | 478368.481 | ✅ Complete |
| **903203** | **blank** | **blank** | ❌ Gap |

**Coordinate completeness: 10 / 12 = 83%**

---

## Conservative Limitations

1. Coordinate values have not been invented, inferred from proximity, or estimated from
   adjacent poles. Only values readable from the baseline CSV or structured text in notes
   have been counted.

2. The pole notes for 903101 reference ENWL popup evidence as the source of coordinates,
   but no numeric value was transcribed into those notes. The screenshots for 903101
   may contain a readable coordinate — but screenshots are image files and were not read
   as part of this review. The notes are the structured text interface; they show no value.

3. The pole notes for 903203 explicitly confirm that the reviewer examined the 2026-05-17
   ENWL screenshots and found no legible coordinate text. This review accepts that
   finding as accurate.

4. The ENWL FIDs for both poles (16788439 for 903101; 16938106 for 903203) are confirmed
   and could be used to look up definitive coordinates from the ENWL Network Asset Viewer
   or API. That lookup has not been performed as part of this text-only review.

---

## Audit Script Result

```
python3 scripts/audit_plocal002_evidence.py --root real_pilot_data/P_LOCAL_002 --verbose
```

Output:

- Scanned pole folders: 12
- Draft notes created/updated: 0
- All 12 existing notes files kept intact
- Audit written: `real_pilot_data/P_LOCAL_002/route_notes/P_LOCAL_002_EVIDENCE_AUDIT.md`

The audit script confirms 12/12 support numbers known and 12/12 notes present. It does not
check baseline coordinate completeness — that is the scope of this review document.

---

## Next Action

To close the coordinate gap for supports 903101 and 903203, one of the following must
be completed before claiming 12/12 baseline coordinate completeness:

1. **Option A — ENWL viewer lookup:** Open the ENWL Network Asset Viewer for FID 16788439
   (903101) and FID 16938106 (903203). Read the coordinate values from the pole popup.
   Transcribe them into the baseline CSV and update the respective pole notes.

2. **Option B — Screenshot review:** Open the existing ENWL screenshots for poles 10 and
   12 and check whether any screenshot shows a readable lat/lon or BNG coordinate value
   that was not transcribed into the notes. If found, transcribe and update baseline CSV.

3. **Option C — GPS capture:** If a field revisit is planned, capture a GPS pin for each
   pole using the same method used for poles 01–09.

Until one of these options is executed, the baseline CSV rows for 903101 and 903203 must
remain blank. The coordinate gap does not affect evidence quality or pole identity — both
poles have confirmed ENWL FID, SPN, and support number. It is a baseline completeness
gap only.
