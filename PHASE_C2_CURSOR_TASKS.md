# PHASE C2/D — CURSOR IMPLEMENTATION TASKS

**Status:** READY FOR CURSOR
**Updated:** 2026-05-01
**Evidence:** Phase C review (3,924 words) + Survey research (4,544 words) + Operational feedback (P011)

---

## CRITICAL UNDERSTANDING

**What Cursor Already Did (Phase C C1-C4):**
- ✅ Basic feature filters exist
- ✅ Basic lifecycle visualization exists
- ✅ Basic stay warnings exist
- ✅ Basic span lines exist
- ✅ 300 tests passing

**What's Still Needed (Phase C2/D):**
- ❌ Map UX professional quality (markers too large, symbols unclear, panels mixed)
- ❌ Popup data model professional quality (12 fields → 25+ fields)
- ❌ Asset-specific layouts (existing vs proposed vs angle vs stay vs context)
- ❌ Field Maps display parity

**This is NOT new scope. This is completing Phase C to professional survey-display standards.**

---

## IMPLEMENTATION PACKAGES

### Package C2-1: Map UX Refinement (1 week / ~8-10 hours)

**Problems:**
- Markers too large (visual clutter)
- Layers and filters mixed in one panel
- EX/PR distinction weak
- Angle function hides lifecycle state
- Context records compete with poles visually
- Match warnings too long
- Map key lacks real symbol examples

**Required Changes:**

#### 1.1 Reduce Marker Size (25-40% smaller)

**Current:** Markers likely 12-15px radius
**Target:** 8-10px radius for standard markers

**Files to modify:**
- `app/static/js/map-viewer.js` — Reduce icon size in marker creation
- `app/static/css/map-viewer.css` — Update marker styles

**Implementation:**
```javascript
// Reduce all marker sizes by ~30%
const MARKER_SIZES = {
  existing: 8,      // was ~12
  proposed: 8,      // was ~12
  angle: 10,        // was ~14
  stay: 6,          // was ~9
  context: 5        // was ~8
};
```

#### 1.2 Split Panel: Map Layers + Review Filters

**Current:** Single right panel with all controls mixed
**Target:** Two distinct sections with clear headings

**Implementation:**
```html
<!-- In map_viewer.html -->
<div class="map-controls-panel">

  <!-- Section 1: Map Layers (What to show) -->
  <div class="map-layers-section">
    <h4>Map Layers</h4>
    <div class="layer-toggles">
      <!-- Asset type layers -->
      <label><input type="checkbox" id="layer-existing" checked> Existing Poles</label>
      <label><input type="checkbox" id="layer-proposed" checked> Proposed Poles</label>
      <label><input type="checkbox" id="layer-angle" checked> Angle Poles</label>
      <label><input type="checkbox" id="layer-stays" checked> Stays/Anchors</label>
      <label><input type="checkbox" id="layer-context"> Context/Crossings</label>
      <label><input type="checkbox" id="layer-spans" checked> Design Chain Spans</label>
    </div>
  </div>

  <!-- Section 2: Review Filters (What needs attention) -->
  <div class="review-filters-section">
    <h4>Review Focus</h4>
    <div class="filter-buttons">
      <button class="filter-btn" data-filter="blockers">Design Blockers</button>
      <button class="filter-btn" data-filter="warnings">Review Required</button>
      <button class="filter-btn" data-filter="missing-heights">Missing Heights</button>
      <button class="filter-btn" data-filter="missing-stays">Missing Stay Evidence</button>
      <button class="filter-btn" data-filter="span-anomalies">Span Anomalies</button>
      <button class="filter-btn" data-filter="ex-pr-matches">EX/PR Matches</button>
    </div>
  </div>

</div>
```

#### 1.3 Better EX/PR Symbol Distinction

**Current:** Shape + color both encode different info
**Problem:** Confusing at a glance

**Target:** Shape = asset type, Fill color = lifecycle, Stroke color = QA status

**Implementation:**
```javascript
function createMarkerIcon(feature) {
  const type = feature.properties.record_type;
  const lifecycle = feature.properties.lifecycle_state;
  const qaStatus = feature.properties.qa_status;

  // Shape by asset type (NEVER CHANGES)
  const shapes = {
    'existing': 'square',
    'proposed': 'circle',
    'angle': 'diamond',
    'stay': 'triangle',
    'context': 'small-diamond'
  };

  // Fill color by lifecycle state
  const fillColors = {
    'existing': '#ffffff',        // white
    'proposed': '#bfdbfe',        // light blue
    'retained': '#bbf7d0',        // light green
    'recovered': '#fecaca',       // light red
    'replacement': '#bfdbfe',     // light blue
    'repositioned': '#fef3c7'     // light yellow
  };

  // Stroke color by QA status
  const strokeColors = {
    'pass': '#10b981',      // green
    'warning': '#f59e0b',   // amber
    'fail': '#ef4444'       // red
  };

  return createSVGMarker(
    shapes[type],
    fillColors[lifecycle] || '#ffffff',
    strokeColors[qaStatus] || '#6b7280',
    MARKER_SIZES[type]
  );
}
```

#### 1.4 Angle as Overlay (Not Lifecycle Replacement)

**Current:** Angle poles show as separate "A" marker type
**Problem:** Hides whether it's an existing angle or proposed angle

**Target:** Angle is a FUNCTION badge on top of existing/proposed markers

**Implementation:**
```javascript
function createMarkerIcon(feature) {
  const baseIcon = createBaseMarker(feature);  // EX/PR/ST/CTX

  // Add angle badge if pole has angle function
  if (feature.properties.function === 'Angle' || feature.properties.is_angle_pole) {
    return addAngleBadge(baseIcon);
  }

  return baseIcon;
}

function addAngleBadge(icon) {
  // Add small "A" badge in top-right corner of marker
  // Visual: EX marker (square) with tiny "A" overlay
}
```

#### 1.5 Context Records Visually Secondary

**Current:** Context records same visual weight as poles
**Problem:** Noise competes with design-critical poles

**Target:** Muted colors, smaller size, off by default

**Implementation:**
```javascript
// Context markers
const CONTEXT_STYLE = {
  fillColor: '#f3f4f6',      // very light gray
  strokeColor: '#9ca3af',    // muted gray
  size: 5,                   // smallest
  opacity: 0.6,              // semi-transparent
  defaultVisible: false       // hidden by default
};
```

#### 1.6 Shorten Match Warnings + Visual Links

**Current:** Long text warnings in popups
**Target:** Visual dashed line + short popup text

**Implementation:**
```javascript
// Draw dashed line between EX/PR matches
function renderMatchLinks(features) {
  const matchPairs = features.filter(f => f.properties.match_status === 'suggested');

  matchPairs.forEach(pair => {
    L.polyline(
      [[pair.ex.lat, pair.ex.lng], [pair.pr.lat, pair.pr.lng]],
      {
        color: '#94a3b8',
        weight: 1,
        dashArray: '5, 5',
        opacity: 0.5
      }
    ).bindTooltip(`Suggested replacement link — unconfirmed (${pair.distance.toFixed(1)}m)`);
  });
}
```

**Popup text change:**
```
OLD: "This existing pole appears to have a nearby proposed pole at 15.2m distance. Review to confirm this is an intended replacement pair or reassign if needed."

NEW: "Suggested replacement link — unconfirmed. Review pairing page to confirm."
```

#### 1.7 Update Map Key with Real Symbol Examples

**Current:** Text-only legend
**Target:** Visual symbol examples matching actual markers

**Implementation:**
```html
<div class="map-legend">
  <h4>Map Key</h4>

  <div class="legend-section">
    <h5>Asset Types (by shape)</h5>
    <div class="legend-item">
      <span class="symbol">■</span> Existing Pole
    </div>
    <div class="legend-item">
      <span class="symbol">●</span> Proposed Pole
    </div>
    <div class="legend-item">
      <span class="symbol">◆</span> Angle Pole (overlay badge)
    </div>
    <div class="legend-item">
      <span class="symbol">▲</span> Stay/Anchor
    </div>
    <div class="legend-item">
      <span class="symbol">◊</span> Context/Crossing
    </div>
  </div>

  <div class="legend-section">
    <h5>QA Status (by stroke color)</h5>
    <div class="legend-item">
      <span class="symbol stroke-green">■</span> Pass
    </div>
    <div class="legend-item">
      <span class="symbol stroke-amber">■</span> Review Required
    </div>
    <div class="legend-item">
      <span class="symbol stroke-red">■</span> Design Blocker
    </div>
  </div>

  <div class="legend-section">
    <h5>Route Elements</h5>
    <div class="legend-item">
      <span class="line solid-blue"></span> Design Chain Span
    </div>
    <div class="legend-item">
      <span class="line dashed-gray"></span> Suggested Replacement Link
    </div>
  </div>
</div>
```

**Files to modify:**
- `app/templates/map_viewer.html`
- `app/static/js/map-viewer.js`
- `app/static/css/map-viewer.css`

**Testing:**
- Load Gordon or Bellsprings job
- Verify markers 30% smaller
- Check panel split clear
- Verify EX squares, PR circles visible
- Check angle poles show base type + A badge
- Verify context muted/hidden by default
- Check map key matches actual symbols

---

### Package C2-2: Popup Data Model Expansion (1-2 weeks / ~12-16 hours)

**Current state:** ~12 fields per popup
**Target state:** 25-35 fields per popup (asset-specific)

**Evidence sources:**
- Survey research doc (50-field complete model)
- Field Maps evidence (19-field MV_Poles schema)
- Phase C review (10-15 priority fields identified)

**Priority fields to add (15-20 total):**

#### 2.1 Physical Structure Fields

**Add to existing pole popups:**
1. **Pole class/strength** (e.g., "Class 9 Medium")
2. **Material** (expand current: wood/concrete/steel + condition)
3. **Condition** (good/fair/poor/unsafe - CRITICAL for design)
4. **Lean direction** (if measured: "2° west")
5. **Lean severity** (minor/moderate/severe)
6. **Defect type** (rot/split/burn/impact/none)
7. **Foundation type** (if known)

**Implementation:**
```python
# In app/routes/map_preview.py or popup builder
def build_physical_section(record):
    fields = []

    # Height (already exists, improve)
    if record.get('height'):
        fields.append({
            'label': 'Measured Height',
            'value': f"{record['height']}m",
            'status': 'ok',
            'icon': '✓'
        })
    else:
        if record['record_type'] == 'existing':
            fields.append({
                'label': 'Height',
                'value': 'not captured',
                'status': 'review',
                'icon': '⚠️',
                'tooltip': 'Existing pole height should have been measured'
            })

    # NEW: Pole class
    if record.get('pole_class'):
        fields.append({
            'label': 'Pole Class',
            'value': record['pole_class'],
            'status': 'ok'
        })

    # NEW: Material + condition combined
    material = record.get('material', 'not captured')
    condition = record.get('condition', 'not captured')
    fields.append({
        'label': 'Material / Condition',
        'value': f"{material} / {condition}",
        'status': 'review' if material == 'not captured' else 'ok'
    })

    # NEW: Lean
    if record.get('lean_direction') or record.get('lean_severity'):
        lean_text = f"{record.get('lean_severity', 'unknown')} lean {record.get('lean_direction', '')}"
        fields.append({
            'label': 'Lean',
            'value': lean_text,
            'status': 'warning' if 'severe' in lean_text else 'info'
        })

    # NEW: Defects
    if record.get('defect_type'):
        fields.append({
            'label': 'Defects',
            'value': record['defect_type'],
            'status': 'warning',
            'icon': '⚠️'
        })

    return fields
```

#### 2.2 Electrical/Network Fields

**Add to pole popups:**
8. **Voltage carried** (11kV/33kV/LV/mixed)
9. **Conductor type** (AAC/AAAC/Cu/unknown)
10. **Number of phases** (single/3-phase)
11. **Equipment presence** (transformer/switch/fuse/recloser/none)
12. **Equipment rating** (if transformer: "50kVA")

**Implementation:**
```python
def build_electrical_section(record):
    fields = []

    # NEW: Voltage
    voltage = record.get('voltage', 'not recorded')
    fields.append({
        'label': 'Line Voltage',
        'value': voltage,
        'status': 'info' if voltage == 'not recorded' else 'ok'
    })

    # NEW: Conductor
    conductor = record.get('conductor_type', 'not recorded')
    fields.append({
        'label': 'Conductor Type',
        'value': conductor,
        'status': 'info'
    })

    # NEW: Equipment
    equipment = record.get('equipment', [])
    if equipment:
        equipment_str = ', '.join(equipment)
        fields.append({
            'label': 'Mounted Equipment',
            'value': equipment_str,
            'status': 'ok',
            'icon': '⚡'
        })

    return fields
```

#### 2.3 Mechanical Support Fields

**Add to angle pole popups:**
13. **Stay present** (yes/no - not just warning)
14. **Stay type** (terminal/angle/tee-off/tandem)
15. **Stay direction/bearing** (e.g., "215° southwest")
16. **Anchor details** (if linked)

**Implementation:**
```python
def build_mechanical_section(record):
    fields = []

    # For angle poles
    if record.get('is_angle_pole'):
        stay_evidence = record.get('stay_evidence', {})

        if stay_evidence.get('has_stay_evidence'):
            # Stay present
            fields.append({
                'label': 'Stay Evidence',
                'value': f"✓ {stay_evidence['stay_type']}",
                'status': 'ok',
                'details': f"@ {stay_evidence['distance']}m, bearing {stay_evidence['bearing']}°"
            })
        else:
            # Missing stay evidence
            fields.append({
                'label': 'Stay Evidence',
                'value': 'not captured',
                'status': 'warning',
                'icon': '⚠️',
                'tooltip': 'Angle pole — stay evidence not captured. Check field notes, photos or plan evidence.'
            })

    return fields
```

#### 2.4 Evidence Quality Fields

**Add to all poles:**
17. **Surveyor/date** (who captured, when)
18. **GNSS accuracy** (RTK/PPK/standalone)
19. **Photo indicators** (has full pole photo, pole-top photo, defect photo)
20. **Source confidence** (measured/estimated/legacy)

**Implementation:**
```python
def build_evidence_section(record):
    fields = []

    # NEW: Surveyor/date
    if record.get('surveyor') or record.get('survey_date'):
        fields.append({
            'label': 'Surveyed By',
            'value': f"{record.get('surveyor', 'unknown')} on {record.get('survey_date', 'unknown date')}",
            'status': 'info'
        })

    # NEW: GNSS accuracy
    if record.get('gnss_accuracy'):
        fields.append({
            'label': 'Position Accuracy',
            'value': record['gnss_accuracy'],
            'status': 'ok' if 'RTK' in record['gnss_accuracy'] else 'info'
        })

    # NEW: Photo indicators
    photos = []
    if record.get('has_full_pole_photo'): photos.append('Full pole')
    if record.get('has_pole_top_photo'): photos.append('Pole top')
    if record.get('has_defect_photo'): photos.append('Defect')

    if photos:
        fields.append({
            'label': 'Photo Evidence',
            'value': ', '.join(photos),
            'status': 'ok',
            'icon': '📷'
        })
    else:
        fields.append({
            'label': 'Photo Evidence',
            'value': 'no linked photos',
            'status': 'info'
        })

    return fields
```

#### 2.5 Asset-Specific Popup Layouts

**Different layouts for different asset types:**

**Existing Pole Popup:**
```
┌─────────────────────────────────────┐
│ Identity                            │
│ • Point: 47                         │
│ • Type: Existing Pole               │
│ • Status: Pass                      │
├─────────────────────────────────────┤
│ Physical                            │
│ • Measured Height: 9.2m ✓           │
│ • Pole Class: Class 9 Medium        │
│ • Material / Condition: Wood / Fair │
│ • Lean: Minor lean 2° west          │
│ • Defects: Rot at base ⚠️            │
├─────────────────────────────────────┤
│ Electrical                          │
│ • Line Voltage: 11kV                │
│ • Conductor: AAC 7/3.75             │
│ • Equipment: 50kVA transformer ⚡    │
├─────────────────────────────────────┤
│ Mechanical                          │
│ • Stay Evidence: ✓ Angle Stay       │
│   @ 12.4m, bearing 215°             │
│ • Deviation: 28°                    │
├─────────────────────────────────────┤
│ Location                            │
│ • E/N: 365377.835, 643824.697       │
│ • Elevation: 127.3m                 │
│ • GNSS: RTK (±0.02m)                │
├─────────────────────────────────────┤
│ Evidence                            │
│ • Surveyed By: J. Smith (2024-03-15)│
│ • Photos: Full pole, Pole top 📷    │
│ • Remarks: ex pole                  │
├─────────────────────────────────────┤
│ Lifecycle / Design                  │
│ • Being Replaced: Yes               │
│ • Linked To: Proposed Pole 48 (15m) │
│ • Match Status: Suggested           │
└─────────────────────────────────────┘
```

**Proposed Pole Popup:**
```
┌─────────────────────────────────────┐
│ Identity                            │
│ • Point: 48                         │
│ • Type: Proposed Pole               │
│ • Status: Review Required           │
├─────────────────────────────────────┤
│ Specification                       │
│ • Height: not yet specified ℹ️       │
│   (design decision required)        │
│ • Pole Class: not specified         │
│ • Material: not specified           │
├─────────────────────────────────────┤
│ Design Requirements                 │
│ • Clearance: Road 15m south         │
│ • Stay Required: Yes (angle 32°)    │
│ • Access: Farm entrance nearby      │
├─────────────────────────────────────┤
│ Location                            │
│ • E/N: 365392.104, 643839.521       │
│ • Elevation: 128.1m                 │
├─────────────────────────────────────┤
│ Lifecycle / Design                  │
│ • Replacing: Existing Pole 47 (15m) │
│ • Match Status: Suggested           │
│ • Action: Confirm or reassign       │
└─────────────────────────────────────┘
```

**Angle Pole Popup (Mechanical Focus):**
```
┌─────────────────────────────────────┐
│ Identity                            │
│ • Point: 52                         │
│ • Type: Existing Angle Pole         │
│ • Function: Angle                   │
│ • Status: Warning                   │
├─────────────────────────────────────┤
│ Mechanical                          │
│ • ⚠️ Angle pole — stay evidence     │
│   not captured. Check field notes,  │
│   photos or plan evidence.          │
│ • Route Deviation: 32° (significant)│
│ • Action: Verify stay configuration │
│   before design                     │
├─────────────────────────────────────┤
│ Physical                            │
│ • Height: 10.5m ✓                   │
│ • Material / Condition: Wood / Good │
├─────────────────────────────────────┤
│ Location                            │
│ • E/N: 365410.225, 643855.102       │
└─────────────────────────────────────┘
```

**Stay/Anchor Popup:**
```
┌─────────────────────────────────────┐
│ Identity                            │
│ • Point: 53                         │
│ • Type: Angle Stay                  │
│ • Status: Pass                      │
├─────────────────────────────────────┤
│ Stay Details                        │
│ • Type: Angle Stay                  │
│ • Linked to: Pole 52 (12.4m)        │
│ • Direction: 215° southwest         │
│ • Configuration: Single stay        │
├─────────────────────────────────────┤
│ Location                            │
│ • E/N: 365398.442, 643843.011       │
└─────────────────────────────────────┘
```

**Context/Crossing Popup:**
```
┌─────────────────────────────────────┐
│ Identity                            │
│ • Point: 61                         │
│ • Type: Road Crossing               │
│ • Priority: HIGH                    │
├─────────────────────────────────────┤
│ Crossing Details                    │
│ • Label: Road Crossing — Critical   │
│   clearance check required          │
│ • Distance from Route: 5m           │
│ • Clearance Measured: No ⚠️          │
│ • Action: Measure statutory         │
│   clearance to road surface         │
├─────────────────────────────────────┤
│ Location                            │
│ • E/N: 365405.118, 643850.772       │
└─────────────────────────────────────┘
```

**Files to modify:**
- `app/routes/map_preview.py` — Expand map_data.json with all new fields
- `app/qa_engine.py` — Add new field extraction logic
- `app/static/js/map-viewer.js` — Build asset-specific popup layouts
- `app/static/css/map-viewer.css` — Style popup sections

**Data sources:**
- Most fields will show "not captured" initially (data doesn't exist in current CSVs)
- Some fields can be inferred (voltage from job context, angle from bearing)
- Some fields will come from future structured capture (Stage 4)

**Testing:**
- Load Gordon or Bellsprings
- Click existing pole → verify all 7 sections present
- Click proposed pole → verify design-focused layout
- Click angle pole → verify mechanical section prominent
- Click stay → verify stay details shown
- Click context record → verify crossing priority/action

---

### Package C2-3: Field Maps Display Parity (Optional - 4-6 hours)

**Goal:** Match what Field Maps shows (without building Field Maps capture yet)

**Reference:** NIE MV_Poles 19-field schema from Field Maps evidence

**Fields Field Maps shows that GridFlow should also show:**
1. OBJECTID ✅ (have as point_id)
2. Pole number ✅ (have)
3. Status (E/P/R) ✅ (have)
4. Material ➕ (add)
5. Pole type ➕ (add - wood/concrete/steel)
6. Condition ➕ (add - good/fair/poor)
7. Grade/class ➕ (add)
8. Height ✅ (have)
9. Year installed ➕ (add if available)
10. Comments/remarks ✅ (have)
11. Coordinates ✅ (have)
12. Survey date ➕ (add)
13. Surveyor ➕ (add)

**Most of these are covered in Package C2-2.**

**Additional Field Maps features to consider:**
- Attachment management (photos) — defer to Stage 4
- Related records (parent pole, linked stays) — partially covered in lifecycle
- Offline editing capability — defer to Stage 4

---

## ACCEPTANCE CRITERIA

### Package C2-1 Complete When:
- ✅ Markers 25-40% smaller (visual inspection)
- ✅ Panel split into Map Layers + Review Filters (clear headings)
- ✅ EX = square, PR = circle visible on map
- ✅ Angle shows as overlay badge on EX/PR markers
- ✅ Context records muted/hidden by default
- ✅ Match warnings shortened + dashed lines render
- ✅ Map key shows real symbol examples
- ✅ All 300+ tests still passing

### Package C2-2 Complete When:
- ✅ Existing pole popup shows 25+ fields across 7 sections
- ✅ Proposed pole popup shows design-focused layout
- ✅ Angle pole popup shows mechanical section prominently
- ✅ Stay popup shows stay details + linked pole
- ✅ Context popup shows crossing priority + action
- ✅ "Not captured" fields show appropriate status (review/info/warning)
- ✅ All 300+ tests still passing
- ✅ Validated on Gordon and Bellsprings jobs

### Package C2-3 Complete When (Optional):
- ✅ Field Maps 19-field schema matched
- ✅ All Field Maps display fields present in GridFlow popups
- ✅ Display parity confirmed by side-by-side comparison

---

## TIMELINE ESTIMATE

**Package C2-1 (Map UX):** 1 week / 8-10 hours
**Package C2-2 (Popup Data):** 1-2 weeks / 12-16 hours
**Package C2-3 (Field Maps Parity):** Optional / 4-6 hours

**Total:** 2-4 weeks / 24-32 hours of focused Cursor work

---

## AFTER PHASE C2/D COMPLETE

**Validation:**
1. Test on P010, P011, Gordon, Bellsprings
2. Collect designer feedback
3. Confirm professional survey-display quality
4. Document any remaining gaps

**Then decide:**
- Stage 4 (structured field capture, tablet workflows, photo management)
- OR more Phase C refinement
- OR operational use + adoption focus

---

## CURSOR START COMMAND

**Copy this to Cursor when ready:**

```
Phase C2/D is approved. Read /Users/noelcollins/Unitas-GridFlow/PHASE_C2_CURSOR_TASKS.md

Start with Package C2-1: Map UX Refinement

Requirements:
- Reduce marker sizes 25-40%
- Split panel into Map Layers + Review Filters
- EX = square, PR = circle, Angle = overlay badge
- Context muted/hidden by default
- Shorten match warnings + add visual dashed lines
- Update map key with real symbol examples

Test after implementation. All 300+ tests must stay green.

Report completion before proceeding to Package C2-2.
```

---

**END OF SPECIFICATION**
