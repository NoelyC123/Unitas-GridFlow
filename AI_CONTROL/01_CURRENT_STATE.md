# Current State

## Project phase

**Stage 1 complete → entering Stage 2 (D2D elimination)**

---

## What works

- Raw Trimble controller dump intake (tested on 4 real files)
- CRS detection: Irish Grid TM65, ITM, OSGB27700
- Coordinate conversion to WGS84 for map display
- Record-role classification (structural, context, anchor)
- Replacement pair detection (EXpole to Pol matching)
- Evidence gates (7 scoped design gates)
- Confidence-aware severity tiers (PASS/WARN/FAIL)
- Interactive Leaflet map with filtering
- PDF pre-design briefing report
- DNO rulepack inference from geography
- Column/header normalisation for structured CSVs
- Context feature classification (Hedge, Fence, Wall, Gate, Track, Road, Tree, Stream, BTxing, LVxing, Ignore)

## Counts

- **Tests passing:** 175
- **DNO rulepacks:** 4 (SPEN, SSEN, NIE, ENWL)
- **Real files validated:** 4

## What was just fixed (Phase 3A)

- Crossing codes (BTxing, LVxing) classified as context, not structural
- Road and Ignore codes classified as context
- Span minimum threshold reduced from 10m to 5m (fixes dense survey noise)
- Location field contamination cleaned (Pol:LAND USE → empty)

## Known remaining issues

1. File order treated as route order — EXpoles captured at end of file break span calculations
2. Replacement pair narratives can be 1-to-many (noisy)
3. No PoleCAD-ready output format yet (Stage 2 goal)
4. PDF report needs redesign for designer usability
5. No multi-file job support yet (474 + 474c are same job area)

## Strategic position

- No competing product exists in this space
- Tool validated on real NIE and SPEN survey files
- Project owner has direct survey and design experience
- Full 6-stage vision defined (see 00_PROJECT_CANONICAL.md)
