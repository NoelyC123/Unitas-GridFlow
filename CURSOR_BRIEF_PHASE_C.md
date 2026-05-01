# CURSOR BRIEF — PHASE C IMPLEMENTATION

**Status:** APPROVED — Path 2 (Fast)
**Target:** 4-5 weeks / ~24 hours implementation
**Validation:** P011 operational feedback + engineering analysis + Field Maps evidence + 8,604-word consolidated spec

---

## CRITICAL CONTEXT

You are implementing **Phase C: Map Intelligence Improvements**.

**What Phase C is:**
- The next validated improvement after Phase B (UI polish complete, 298 tests passing)
- 4 independent packages fixing 6 operational blockers identified in real designer use
- All packages validated by 4 comprehensive technical specifications
- All packages must preserve existing functionality and keep tests green

**What Phase C is NOT:**
- Stage 4 structured field capture (future, do not build)
- PoleCAD export (future, do not build)
- Photo integration (future, do not build)
- New backend QA rules (not in scope)
- UI redesign (cosmetic only where specs require)

---

## EVIDENCE BASE (MUST REFERENCE)

Before implementing ANY package, read the relevant evidence:

### 1. Live Operational Feedback
**File:** `/Users/noelcollins/Unitas-GridFlow/P011_OPERATIONAL_FEEDBACK_2026-04-30.md`

**Key findings:**
- Context features completely invisible (BLOCKER)
- Proposed pole "Height: not captured" misleading (designers can't measure non-existent poles)
- Symbols not distinct enough at map zoom
- Stay evidence missing at angle poles (mechanical design blocker)
- Span distance unclear (can't validate route logic)
- Insufficient data in popups for design decisions

### 2. Domain Reference Summary
**File:** `/Users/noelcollins/Unitas-GridFlow/AI_CONTROL/28_DOMAIN_REFERENCE_SUMMARY.md`

**Key principles:**
- Evidence quality matters (measured vs inferred vs missing)
- Context features ≠ structural poles
- Feature code is a clue, not final truth
- Absence of evidence ≠ evidence of compliance

### 3. Practitioner Review Summary
**File:** `/Users/noelcollins/Unitas-GridFlow/AI_CONTROL/29_PRACTITIONER_REVIEW_SUMMARY.md`

**Key guidance:**
- Terminology must be practitioner-facing
- Map must show connected OHL circuit (spans)
- Evidence quality must be visible
- Missing evidence needs design consequences
- EX/PR proximity is QA, not designer reassignment

---

## IMPLEMENTATION ORDER

Implement packages in this exact order:

1. **C1: Feature-Type Filtering + Blank Field Framework** (3-4 hours)
2. **C2: Asset Lifecycle Visualization** (4-5 hours)
3. **C3: Stay Evidence at Angle Poles** (4-5 hours)
4. **C4: Span Anomaly Detection + Crossing Context** (3-4 hours)

**After EACH package:**
- Run full test suite: `pytest -v`
- Verify all 298 tests still pass
- Manually check map renders without errors
- Report completion before proceeding to next package

---

## PACKAGE C1: FEATURE-TYPE FILTERING + BLANK FIELD FRAMEWORK

### Problems This Fixes

| Operational Issue | Root Cause | Impact |
|-------------------|------------|--------|
| Context invisible | No filter to show/hide context records | Designer can't see crossing constraints |
| Height misleading | Same "not captured" for existing (ERROR) and proposed (EXPECTED) | Designer confusion about what's actually missing |
| Symbols unclear | No visual distinction between asset types | Can't quickly scan map for specific features |
| Data insufficient | Popup shows all fields equally | Design-critical info buried in noise |

### Specifications

#### 1.1 Feature-Type Filter Buttons

**Location:** Map viewer controls (top or side panel)

**Required filters (8 total):**

```javascript
const FEATURE_FILTERS = {
  existing: { label: "Existing Poles", icon: "○", defaultOn: true },
  proposed: { label: "Proposed Poles", icon: "□", defaultOn: true },
  angle: { label: "Angle Poles", icon: "◇", defaultOn: true },
  stays: { label: "Stays/Anchors", icon: "△", defaultOn: true },
  context: { label: "Context/Crossings", icon: "◊", defaultOn: false },  // OFF by default
  missingHeight: { label: "Missing Heights", icon: "⚠", defaultOn: false },
  missingSpec: { label: "Missing Spec", icon: "⚠", defaultOn: false },
  withRemarks: { label: "Has Remarks", icon: "📝", defaultOn: false }
};
```

**Behavior:**
- Filters toggle marker visibility (show/hide)
- Multiple filters can be active simultaneously
- Filter state persists during session (not across page reload)
- Filter buttons show count when possible: "Existing Poles (47)"
- Context/crossings filter OFF by default (reduce visual noise)

**Visual design:**
- Button group with toggle state (active/inactive styling)
- Icon + label for clarity
- Responsive layout (stack vertically on mobile)

#### 1.2 Blank Field Framework

**Problem:** Blank fields mean different things:

| Asset Type | Blank Height | Meaning | Display |
|------------|--------------|---------|---------|
| Existing pole | missing | ERROR - should have been measured | "Height: not captured (review required)" + ⚠️ |
| Proposed pole | missing | EXPECTED - doesn't exist yet | "Height: not yet specified (design decision)" + ℹ️ |
| Context record | missing | N/A - not applicable | Hide height field entirely |

**Implementation:**

Add to `app/routes/map_preview.py` or relevant backend:

```python
def format_field_for_popup(record_type, field_name, value):
    """
    Format a field value based on record type and expected presence.

    Returns:
        dict with 'value', 'label', 'status', 'icon'
    """
    if field_name == 'height':
        if record_type == 'context':
            return None  # Hide field entirely

        if value is None or value == '':
            if record_type == 'existing':
                return {
                    'label': 'Height',
                    'value': 'not captured',
                    'status': 'review',
                    'icon': '⚠️',
                    'tooltip': 'Existing pole height should have been measured. Check field notes or plan evidence.'
                }
            elif record_type == 'proposed':
                return {
                    'label': 'Height',
                    'value': 'not yet specified',
                    'status': 'info',
                    'icon': 'ℹ️',
                    'tooltip': 'Proposed pole specification is a design decision.'
                }
        else:
            return {
                'label': 'Height',
                'value': f"{value}m",
                'status': 'ok',
                'icon': '✓'
            }

    # Similar logic for other fields (spec, material, etc.)
    # ...
```

**Frontend popup rendering:**

```javascript
function renderPopupField(field) {
  if (!field) return '';  // Hidden field

  const statusClass = `field-status-${field.status}`;  // 'ok', 'review', 'info'

  return `
    <div class="popup-field ${statusClass}">
      <span class="field-label">${field.label}:</span>
      <span class="field-value">${field.value}</span>
      <span class="field-icon">${field.icon}</span>
      ${field.tooltip ? `<span class="field-tooltip" title="${field.tooltip}">?</span>` : ''}
    </div>
  `;
}
```

**CSS styling:**

```css
.field-status-ok { color: #2d5016; }
.field-status-review { color: #d97706; background: #fef3c7; padding: 2px 4px; }
.field-status-info { color: #1e40af; font-style: italic; }
```

#### 1.3 Visual Symbol Hierarchy

**Current problem:** All markers look similar, only color differs

**Required changes:**

| Feature Type | Shape | Size | Stroke | Fill | Priority |
|--------------|-------|------|--------|------|----------|
| Existing pole | Circle ○ | 10px | 2px black | White | High |
| Proposed pole | Square □ | 10px | 2px blue | Light blue | High |
| Angle pole | Diamond ◇ | 12px | 2px red | Light red | High |
| Stay/anchor | Triangle △ | 8px | 1px gray | Light gray | Medium |
| Context/crossing | Small diamond ◊ | 6px | 1px orange | Light orange | Low |

**Implementation (map-viewer.js):**

```javascript
function getMarkerIcon(feature) {
  const type = feature.properties.record_type;
  const qaStatus = feature.properties.qa_status;  // 'pass', 'warning', 'fail'

  // Base shape by type
  const shapes = {
    'existing': 'circle',
    'proposed': 'square',
    'angle': 'diamond',
    'stay': 'triangle',
    'context': 'small-diamond'
  };

  // QA status affects border/badge, NOT fill
  const borderColor = {
    'pass': '#10b981',
    'warning': '#f59e0b',
    'fail': '#ef4444'
  }[qaStatus] || '#6b7280';

  return L.marker([lat, lng], {
    icon: createCustomIcon(shapes[type], borderColor)
  });
}

function createCustomIcon(shape, borderColor) {
  // SVG-based custom marker implementation
  // Shape determines visual appearance
  // borderColor adds QA status badge/outline
  // ...
}
```

**Key principle:** **Shape = asset type, Color = QA status**

#### 1.4 Popup Organization

**Current problem:** All fields shown in dump order

**Required structure:**

```
┌─────────────────────────────────────┐
│ Identity                            │
│ • Point ID: 47                      │
│ • Type: Existing Pole               │
│ • Function: Angle                   │
│ • Status: Pass                      │
├─────────────────────────────────────┤
│ Physical                            │
│ • Height: 9.2m ✓                    │
│ • Material: not captured ⚠️          │
│ • Condition: not captured ⚠️         │
├─────────────────────────────────────┤
│ Electrical                          │
│ • Line Voltage: 11kV (inferred)     │
│ • Equipment: not recorded           │
│ • Conductor: not recorded           │
├─────────────────────────────────────┤
│ Mechanical                          │
│ • Stay Evidence: ⚠️ Angle pole —    │
│   stay evidence not captured        │
│ • Loading: unknown                  │
├─────────────────────────────────────┤
│ Location                            │
│ • E/N: 365377.835, 643824.697       │
│ • Elevation: 127.3m                 │
│ • Grid: OSGB36                      │
├─────────────────────────────────────┤
│ Context                             │
│ • Access: farm entrance nearby      │
│ • Crossing: Road 15m south          │
├─────────────────────────────────────┤
│ QA / Review                         │
│ • Design Review: Required           │
│ • Missing Evidence: Material,       │
│   condition, stay configuration     │
│ • Remarks: ex pole                  │
└─────────────────────────────────────┘
```

**Implementation:**

```javascript
function buildPopupContent(feature) {
  const props = feature.properties;
  const sections = [];

  // Section 1: Identity
  sections.push({
    title: 'Identity',
    fields: [
      { label: 'Point ID', value: props.point_id },
      { label: 'Type', value: props.record_type },
      { label: 'Function', value: props.function },
      { label: 'Status', value: props.qa_status }
    ]
  });

  // Section 2: Physical (only for poles)
  if (props.record_type !== 'context') {
    sections.push({
      title: 'Physical',
      fields: [
        formatField(props.record_type, 'height', props.height),
        formatField(props.record_type, 'material', props.material),
        formatField(props.record_type, 'condition', props.condition)
      ].filter(f => f !== null)  // Remove hidden fields
    });
  }

  // Section 3: Electrical
  // Section 4: Mechanical
  // Section 5: Location
  // Section 6: Context
  // Section 7: QA/Review

  return renderSections(sections);
}
```

### Files to Modify

**Backend:**
- `app/routes/map_preview.py` — Add `format_field_for_popup()` helper
- `app/qa_engine.py` — Expose record_type and QA status in map_data.json

**Frontend:**
- `app/templates/map_viewer.html` — Add filter button controls
- `app/static/js/map-viewer.js` — Implement filtering logic, symbol hierarchy, popup organization
- `app/static/css/map-viewer.css` — Visual styling for filters, symbols, popup sections

### Testing Requirements

**After C1 implementation:**

1. Load a real job (Gordon or Bellsprings)
2. Verify filter buttons appear and work
3. Toggle each filter, verify markers show/hide correctly
4. Check context records are hidden by default
5. Inspect existing pole popup: "Height: not captured (review required)" ⚠️
6. Inspect proposed pole popup: "Height: not yet specified (design decision)" ℹ️
7. Inspect context record popup: Height field hidden entirely
8. Verify popup sections appear in correct order
9. Run `pytest -v` — all 298 tests must pass

**Acceptance criteria:**
- ✅ All 8 filter buttons functional
- ✅ Blank field framework distinguishes existing/proposed/context
- ✅ Symbol hierarchy visually clear (shape + size + stroke)
- ✅ Popup sections organized and labeled
- ✅ All tests green

---

## PACKAGE C2: ASSET LIFECYCLE VISUALIZATION

### Problems This Fixes

| Operational Issue | Root Cause | Impact |
|-------------------|------------|--------|
| Symbols unclear (lifecycle) | No visual indication of pole lifecycle state | Can't distinguish existing/proposed/replaced/retained |
| Replacement relationships hidden | EX↔PR matches not visible on map | Designer must cross-reference review page |

### Specifications

#### 2.1 Lifecycle States (11 total)

**Required states:**

| State | Meaning | Typical Records | Symbol Treatment |
|-------|---------|-----------------|------------------|
| `existing` | Pole currently in field, not being replaced | EXpole with no nearby proposed | Circle, white fill |
| `proposed` | New pole to be installed, not replacing existing | Pol/PR with no nearby existing | Square, blue fill |
| `retained` | Existing pole staying in service | EXpole explicitly marked "retained" | Circle, green fill |
| `recovered` | Existing pole to be removed with no replacement | EXpole marked "recovered" or "removed" | Circle, red fill, strikethrough |
| `replacement` | Proposed pole replacing an existing pole | Pol/PR near EXpole (confirmed match) | Square, blue fill, linked line |
| `repositioned` | Existing pole moved slightly | EXpole + nearby proposed at <5m offset | Square, yellow fill, linked line |
| `unmatched_ex` | Existing pole with no clear proposed match | EXpole with ambiguous or distant proposed | Circle, orange stroke |
| `unmatched_pr` | Proposed pole with no clear existing match | Pol/PR with ambiguous or distant existing | Square, orange stroke |
| `suggested` | System-inferred pairing (not reviewed) | Auto-detected EX↔PR within threshold | Dashed linking line |
| `confirmed` | Designer-reviewed pairing | User-confirmed EX↔PR match | Solid linking line |
| `context` | Environmental/crossing feature | Road, fence, crossing, observation | Small diamond, light fill |

**Backend implementation:**

Add to `app/qa_engine.py` or create new `app/lifecycle_classifier.py`:

```python
def classify_lifecycle_state(record, nearby_records):
    """
    Determine the lifecycle state of a record based on type, proximity, and review status.

    Args:
        record: The record to classify
        nearby_records: List of records within proximity threshold

    Returns:
        str: One of 11 lifecycle states
    """
    record_type = record.get('record_type', '').lower()
    function = record.get('function', '').lower()
    remarks = record.get('remarks', '').lower()

    # Context records
    if record_type == 'context':
        return 'context'

    # Existing poles
    if 'ex' in record_type or 'existing' in function:
        if 'retain' in remarks or 'keep' in remarks:
            return 'retained'
        if 'recover' in remarks or 'remove' in remarks:
            return 'recovered'

        # Check for nearby proposed poles
        nearby_proposed = [r for r in nearby_records if 'pr' in r.get('record_type', '').lower()]

        if nearby_proposed:
            closest = min(nearby_proposed, key=lambda r: distance_between(record, r))
            dist = distance_between(record, closest)

            if dist < 5:
                return 'repositioned'
            elif dist < 50:  # Within replacement threshold
                review_status = get_review_status(record['point_id'], closest['point_id'])
                return 'confirmed' if review_status == 'reviewed' else 'suggested'
            else:
                return 'unmatched_ex'
        else:
            return 'existing'

    # Proposed poles
    if 'pr' in record_type or 'proposed' in function:
        nearby_existing = [r for r in nearby_records if 'ex' in r.get('record_type', '').lower()]

        if nearby_existing:
            closest = min(nearby_existing, key=lambda r: distance_between(record, r))
            dist = distance_between(record, closest)

            if dist < 50:
                review_status = get_review_status(closest['point_id'], record['point_id'])
                return 'confirmed' if review_status == 'reviewed' else 'suggested'
            else:
                return 'unmatched_pr'
        else:
            return 'proposed'

    # Default
    return 'existing'
```

#### 2.2 EX↔PR Match Visualization

**Requirement:** Show linking lines between matched existing/proposed poles

**Visual design:**

```
EXpole (47) ○─────────────□ Pol (48)
             └─ suggested  (dashed line, 15.2m)

EXpole (52) ○═════════════□ Pol (53)
             └─ confirmed  (solid line, 12.8m)

EXpole (61) ○ ═══════ □ Pol (62)
 (retained)   └─ 4.2m    (repositioned)
```

**Implementation (map-viewer.js):**

```javascript
function renderLifecycleLayer(features) {
  const lifecycleLayer = L.layerGroup();

  features.forEach(feature => {
    const state = feature.properties.lifecycle_state;
    const marker = createLifecycleMarker(feature, state);
    lifecycleLayer.addLayer(marker);
  });

  // Add linking lines for matched pairs
  const pairs = detectMatchedPairs(features);
  pairs.forEach(pair => {
    const line = L.polyline(
      [[pair.ex.lat, pair.ex.lng], [pair.pr.lat, pair.pr.lng]],
      {
        color: pair.status === 'confirmed' ? '#3b82f6' : '#94a3b8',
        weight: pair.status === 'confirmed' ? 2 : 1,
        dashArray: pair.status === 'confirmed' ? null : '5, 5',
        opacity: 0.7
      }
    ).bindTooltip(`${pair.status} match: ${pair.distance.toFixed(1)}m`);

    lifecycleLayer.addLayer(line);
  });

  return lifecycleLayer;
}
```

#### 2.3 Toggle Lifecycle Layer

**Requirement:** User can turn lifecycle visualization on/off

**UI control:**

```html
<div class="map-controls">
  <button id="toggle-lifecycle" class="btn btn-secondary">
    <span class="icon">🔄</span>
    Show Lifecycle States
  </button>
</div>
```

**Behavior:**
- Default: OFF (reduce initial complexity)
- When ON: Replace basic markers with lifecycle-aware markers + linking lines
- When OFF: Show basic feature-type markers only
- State persists during session

#### 2.4 Popup Lifecycle Section

**Add to popup (Section 8):**

```
├─────────────────────────────────────┤
│ Lifecycle                           │
│ • State: Replacement (suggested)    │
│ • Matched To: EXpole 47 (15.2m)     │
│ • Review Status: Not reviewed       │
│ • Action: Confirm or reassign       │
└─────────────────────────────────────┘
```

### Files to Modify

**Backend:**
- Create `app/lifecycle_classifier.py` (new file)
- `app/routes/map_preview.py` — Add lifecycle state to map_data.json
- `app/qa_engine.py` — Integrate lifecycle classification

**Frontend:**
- `app/static/js/map-viewer.js` — Implement lifecycle layer rendering, linking lines, toggle control
- `app/static/css/map-viewer.css` — Lifecycle symbol styling, linking line styles

### Testing Requirements

1. Load real job with EX/PR pairs (Gordon or Bellsprings)
2. Toggle lifecycle layer ON
3. Verify linking lines appear between matched poles
4. Verify dashed lines for suggested, solid for confirmed
5. Check popup shows lifecycle state and matched-to reference
6. Toggle lifecycle layer OFF, verify basic view returns
7. Run `pytest -v` — all 298 tests must pass

**Acceptance criteria:**
- ✅ 11 lifecycle states correctly classified
- ✅ EX↔PR linking lines render correctly
- ✅ Toggle control functional
- ✅ Popup lifecycle section accurate
- ✅ All tests green

---

## PACKAGE C3: STAY EVIDENCE AT ANGLE POLES

### Problems This Fixes

| Operational Issue | Root Cause | Impact |
|-------------------|------------|--------|
| Stay missing (BLOCKER) | No detection of angle poles requiring stays | Mechanical design incomplete, unsafe to proceed |
| Stay configuration unknown | Stay records not linked to parent poles | Designer doesn't know stay type, direction, anchor |

### Specifications

#### 3.1 Angle Pole Detection

**Rule:** A pole is an angle pole if:

1. `function` field explicitly says "Angle", OR
2. Route deviation >10° at that point (calculated from bearing change)

**Implementation:**

Add to `app/qa_engine.py`:

```python
def detect_angle_poles(records):
    """
    Identify poles that require stay evidence.

    Returns:
        list of dicts with angle pole info
    """
    angle_poles = []

    for i, record in enumerate(records):
        is_angle = False
        deviation = None

        # Check explicit function
        if 'angle' in record.get('function', '').lower():
            is_angle = True

        # Check route deviation
        if i > 0 and i < len(records) - 1:
            prev_bearing = calculate_bearing(records[i-1], record)
            next_bearing = calculate_bearing(record, records[i+1])
            deviation = abs(next_bearing - prev_bearing)

            if deviation > 180:
                deviation = 360 - deviation

            if deviation > 10:
                is_angle = True

        if is_angle:
            angle_poles.append({
                'point_id': record['point_id'],
                'deviation': deviation,
                'explicit': 'angle' in record.get('function', '').lower()
            })

    return angle_poles
```

#### 3.2 Stay Record Scanning

**Rule:** For each angle pole, scan for stay records within 20m radius

**Stay types to detect:**

- Angle stay (most common at angle poles)
- Terminal stay (at route ends)
- Tee-off stay (at branches)
- Tandem stay (multiple stays in line)

**Implementation:**

```python
def scan_for_stays(angle_pole, all_records, radius=20):
    """
    Find stay/anchor records near an angle pole.

    Returns:
        dict with stay evidence summary
    """
    nearby_stays = []

    for record in all_records:
        record_type = record.get('record_type', '').lower()

        if 'stay' in record_type or 'anchor' in record_type:
            dist = distance_between(angle_pole, record)

            if dist <= radius:
                nearby_stays.append({
                    'point_id': record['point_id'],
                    'type': classify_stay_type(record),
                    'distance': dist,
                    'bearing': record.get('bearing'),
                    'remarks': record.get('remarks')
                })

    return {
        'angle_pole_id': angle_pole['point_id'],
        'stays_found': len(nearby_stays),
        'stay_details': nearby_stays,
        'has_stay_evidence': len(nearby_stays) > 0
    }

def classify_stay_type(stay_record):
    """
    Determine stay type from record attributes.
    """
    remarks = stay_record.get('remarks', '').lower()
    function = stay_record.get('function', '').lower()

    if 'terminal' in remarks or 'terminal' in function:
        return 'Terminal Stay'
    elif 'angle' in remarks or 'angle' in function:
        return 'Angle Stay'
    elif 'tee' in remarks or 'tee-off' in remarks:
        return 'Tee-off Stay'
    elif 'tandem' in remarks or 'double' in remarks:
        return 'Tandem Stay'
    else:
        return 'Stay/Anchor'
```

#### 3.3 Missing Stay Warning

**If angle pole has no stay evidence within 20m:**

**Map popup addition:**

```
├─────────────────────────────────────┤
│ Mechanical                          │
│ • ⚠️ Angle pole — stay evidence     │
│   not captured. Check field notes,  │
│   photos or plan evidence.          │
│ • Deviation: 32° (significant)      │
│ • Action: Verify stay configuration │
│   before design                     │
└─────────────────────────────────────┘
```

**If stay evidence found:**

```
├─────────────────────────────────────┤
│ Mechanical                          │
│ • ✓ Stay Evidence: Angle Stay       │
│   @ 12.4m, bearing 215°             │
│ • Deviation: 28°                    │
│ • Configuration: Single angle stay  │
└─────────────────────────────────────┘
```

#### 3.4 Filter: Angle Poles Missing Stay Evidence

**Add filter button:**

```javascript
const ANGLE_STAY_FILTER = {
  label: "Angle Poles Missing Stays",
  icon: "⚠️",
  defaultOn: false,
  condition: (feature) => {
    return feature.properties.is_angle_pole &&
           !feature.properties.has_stay_evidence;
  }
};
```

**Behavior:**
- When active, show ONLY angle poles without stay evidence
- Highlights critical mechanical design gaps
- Designer can quickly scan route for mechanical review requirements

### Files to Modify

**Backend:**
- `app/qa_engine.py` — Add `detect_angle_poles()`, `scan_for_stays()`, `classify_stay_type()`
- `app/routes/map_preview.py` — Include stay evidence in map_data.json

**Frontend:**
- `app/static/js/map-viewer.js` — Add angle-stay filter, popup rendering
- `app/templates/map_viewer.html` — Add filter button

### Testing Requirements

1. Load job with known angle poles (Gordon or Bellsprings)
2. Identify angle poles on map (should show ◇ symbol)
3. Click angle pole, verify Mechanical section shows stay evidence or warning
4. Activate "Angle Poles Missing Stays" filter
5. Verify only angle poles without stay evidence are shown
6. Check popup warnings are clear and actionable
7. Run `pytest -v` — all 298 tests must pass

**Acceptance criteria:**
- ✅ Angle poles detected (>10° deviation OR function="Angle")
- ✅ Stay records scanned within 20m radius
- ✅ Missing stay warnings clear and actionable
- ✅ Found stay evidence displayed with type and distance
- ✅ Filter functional
- ✅ All tests green

---

## PACKAGE C4: SPAN ANOMALY DETECTION + CROSSING CONTEXT

### Problems This Fixes

| Operational Issue | Root Cause | Impact |
|-------------------|------------|--------|
| Span unclear | No visible spans or distance labels on map | Can't validate route logic or spot errors |
| Duplicate poles hidden | GPS errors or double-capture not flagged | Design uses wrong coordinates |
| Missing poles invisible | Large gaps not detected | Incomplete route, missing intermediate poles |
| Crossing context weak | Generic "Road" label without clearance priority | Designer doesn't know which crossings are critical |

### Specifications

#### 4.1 3D Span Distance Calculation

**Rule:** Calculate distance between consecutive structural poles in design chain

**Implementation:**

```python
def calculate_span_distance(pole1, pole2):
    """
    Calculate 3D distance between two poles including elevation.

    Returns:
        float: distance in meters
    """
    # Horizontal distance (Pythagorean)
    dx = pole2['easting'] - pole1['easting']
    dy = pole2['northing'] - pole1['northing']
    horizontal = math.sqrt(dx**2 + dy**2)

    # Vertical distance (if elevation available)
    if 'elevation' in pole1 and 'elevation' in pole2:
        dz = pole2['elevation'] - pole1['elevation']
        return math.sqrt(horizontal**2 + dz**2)
    else:
        return horizontal

def generate_span_data(design_chain):
    """
    Generate span information for all consecutive pole pairs.

    Returns:
        list of span dicts
    """
    spans = []

    for i in range(len(design_chain) - 1):
        pole1 = design_chain[i]
        pole2 = design_chain[i+1]

        distance = calculate_span_distance(pole1, pole2)

        spans.append({
            'span_id': f"{pole1['point_id']}-{pole2['point_id']}",
            'from_pole': pole1['point_id'],
            'to_pole': pole2['point_id'],
            'distance': distance,
            'elevation_change': pole2.get('elevation', 0) - pole1.get('elevation', 0),
            'status': classify_span_status(distance, pole1, pole2)
        })

    return spans
```

#### 4.2 Span Anomaly Classification

**Rules:**

| Distance | Voltage | Classification | Warning |
|----------|---------|----------------|---------|
| <10m | Any | Probable duplicate | ⚠️ GPS error or double-capture |
| 10-100m | 11kV/33kV | Normal | ✓ Typical span |
| 100-300m | 11kV | Extended | ℹ️ Long span — verify conductor sag |
| 300-500m | 11kV | Very long | ⚠️ Verify no missing intermediate pole |
| >500m | 11kV | Critical gap | 🚨 Probable missing intermediate pole |
| 10-200m | 33kV/132kV | Normal | ✓ Typical span |
| >500m | 33kV | Critical gap | 🚨 Probable missing intermediate pole |

**Implementation:**

```python
def classify_span_status(distance, pole1, pole2):
    """
    Classify span based on distance and voltage.
    """
    voltage = infer_voltage(pole1, pole2)  # From job context or pole attributes

    if distance < 10:
        return {
            'class': 'duplicate',
            'severity': 'warning',
            'message': '⚠️ Probable duplicate pole or GPS error',
            'action': 'Review coordinates and field notes'
        }

    if voltage in ['11kV', '11000V']:
        if distance > 500:
            return {
                'class': 'critical_gap',
                'severity': 'fail',
                'message': '🚨 Probable missing intermediate pole',
                'action': 'Verify route and check for missing records'
            }
        elif distance > 300:
            return {
                'class': 'very_long',
                'severity': 'warning',
                'message': '⚠️ Very long span — verify no missing pole',
                'action': 'Check field notes and survey evidence'
            }
        elif distance > 100:
            return {
                'class': 'extended',
                'severity': 'info',
                'message': 'ℹ️ Long span — verify conductor sag compliance',
                'action': 'Check clearance calculations'
            }

    return {
        'class': 'normal',
        'severity': 'pass',
        'message': '✓ Typical span',
        'action': None
    }
```

#### 4.3 Crossing Context Enrichment

**Current problem:** Crossing records show generic "Road" or "BT" labels

**Required improvement:** Context-aware crossing labels with clearance priority

**Crossing types and labels:**

| Current | Improved | Priority | Action |
|---------|----------|----------|--------|
| Road | Road Crossing — Critical clearance check required | HIGH | Measure statutory clearance |
| BT | BT/Telecoms Crossing — Proximity coordination required | MEDIUM | Verify separation distance |
| 11xing | 11kV Line Crossing — Voltage separation required | HIGH | Ensure adequate clearance |
| 33xing | 33kV Line Crossing — Critical voltage clearance | CRITICAL | Engineering review required |
| 110xing | 110kV Line Crossing — Specialist review required | CRITICAL | DNO/ENWL approval needed |
| HVxing | HV Line Crossing — Voltage clearance critical | CRITICAL | Engineering review required |
| Wall/Fence | Wall/Fence — Access constraint | LOW | Note for construction planning |
| Stream/Drain | Water Crossing — Foundation consideration | MEDIUM | Check ground conditions |

**Implementation:**

```python
CROSSING_TYPES = {
    'road': {
        'label': 'Road Crossing',
        'priority': 'HIGH',
        'message': 'Critical clearance check required',
        'action': 'Measure statutory clearance to road surface'
    },
    '11xing': {
        'label': '11kV Line Crossing',
        'priority': 'HIGH',
        'message': 'Voltage separation required',
        'action': 'Ensure adequate vertical/horizontal clearance'
    },
    '33xing': {
        'label': '33kV Line Crossing',
        'priority': 'CRITICAL',
        'message': 'Critical voltage clearance',
        'action': 'Engineering review required before design'
    },
    '110xing': {
        'label': '110kV Line Crossing',
        'priority': 'CRITICAL',
        'message': 'Specialist review required',
        'action': 'DNO/ENWL approval needed, specialist design'
    },
    # ... etc
}

def enrich_crossing_context(crossing_record):
    """
    Add priority and action guidance to crossing records.
    """
    feature_code = crossing_record.get('feature_code', '').lower()

    for key, crossing_type in CROSSING_TYPES.items():
        if key in feature_code:
            return {
                **crossing_record,
                'crossing_label': crossing_type['label'],
                'priority': crossing_type['priority'],
                'clearance_message': crossing_type['message'],
                'action': crossing_type['action']
            }

    # Default for unknown crossing types
    return {
        **crossing_record,
        'crossing_label': 'Crossing/Context Feature',
        'priority': 'REVIEW',
        'clearance_message': 'Review for potential constraints',
        'action': 'Check field notes and photos'
    }
```

#### 4.4 Map Rendering: Span Lines + Labels

**Requirement:** Draw lines between consecutive poles with distance labels

**Visual design:**

```
   Pole 47 ○────── 45.2m ──────○ Pole 48
           └─ normal span ─┘

   Pole 52 ○─ 8.3m ─○ Pole 53
           └─ ⚠️ duplicate? ─┘

   Pole 61 ○──────── 312m ────────○ Pole 62
           └─ ⚠️ very long span ─┘
```

**Implementation (map-viewer.js):**

```javascript
function renderSpans(design_chain, span_data) {
  const spanLayer = L.layerGroup();

  span_data.forEach(span => {
    const pole1 = design_chain.find(p => p.point_id === span.from_pole);
    const pole2 = design_chain.find(p => p.point_id === span.to_pole);

    if (!pole1 || !pole2) return;

    // Span line
    const line = L.polyline(
      [[pole1.lat, pole1.lng], [pole2.lat, pole2.lng]],
      {
        color: getSpanColor(span.status.severity),
        weight: 2,
        opacity: 0.6
      }
    );

    // Distance label at midpoint
    const midLat = (pole1.lat + pole2.lat) / 2;
    const midLng = (pole1.lng + pole2.lng) / 2;

    const label = L.marker([midLat, midLng], {
      icon: L.divIcon({
        className: 'span-label',
        html: `<div class="span-distance ${span.status.class}">
                 ${span.distance.toFixed(1)}m
                 ${span.status.severity !== 'pass' ? span.status.message : ''}
               </div>`
      })
    });

    line.bindTooltip(`
      Span ${span.span_id}<br>
      Distance: ${span.distance.toFixed(1)}m<br>
      Status: ${span.status.message}<br>
      ${span.status.action ? 'Action: ' + span.status.action : ''}
    `);

    spanLayer.addLayer(line);
    spanLayer.addLayer(label);
  });

  return spanLayer;
}

function getSpanColor(severity) {
  return {
    'pass': '#10b981',
    'info': '#3b82f6',
    'warning': '#f59e0b',
    'fail': '#ef4444'
  }[severity] || '#6b7280';
}
```

#### 4.5 Filters: Span Anomalies + Crossings

**Add filter buttons:**

```javascript
const SPAN_FILTERS = {
  spanAnomalies: {
    label: "Show Span Anomalies",
    icon: "⚠️",
    defaultOn: false,
    condition: (span) => span.status.severity !== 'pass'
  },
  criticalCrossings: {
    label: "Show Crossings Requiring Clearance",
    icon: "🚦",
    defaultOn: false,
    condition: (feature) => {
      return feature.properties.record_type === 'context' &&
             ['HIGH', 'CRITICAL'].includes(feature.properties.priority);
    }
  }
};
```

### Files to Modify

**Backend:**
- `app/qa_engine.py` — Add `calculate_span_distance()`, `classify_span_status()`, `enrich_crossing_context()`
- `app/routes/map_preview.py` — Generate span data in map_data.json

**Frontend:**
- `app/static/js/map-viewer.js` — Render span lines + labels, add filters
- `app/static/css/map-viewer.css` — Span line styling, label styling

### Testing Requirements

1. Load real job (Gordon or Bellsprings)
2. Verify span lines render between consecutive poles
3. Check distance labels appear at midpoints
4. Verify span anomaly warnings for <10m and >500m spans
5. Activate "Show Span Anomalies" filter
6. Verify crossing records show enriched labels (e.g., "Road Crossing — Critical clearance check required")
7. Activate "Show Crossings Requiring Clearance" filter
8. Run `pytest -v` — all 298 tests must pass

**Acceptance criteria:**
- ✅ Span lines rendered with distance labels
- ✅ <10m spans flagged as probable duplicates
- ✅ >500m spans (11kV) flagged as probable missing poles
- ✅ Crossing context enriched with priority and actions
- ✅ Filters functional
- ✅ All tests green

---

## CROSS-PACKAGE INTEGRATION

After all 4 packages complete, verify:

1. **Filters work together:**
   - Can activate multiple filters simultaneously
   - E.g., "Existing Poles" + "Angle Poles Missing Stays" + "Span Anomalies"

2. **Lifecycle + Feature filters:**
   - Lifecycle layer can be toggled independently
   - Feature filters apply to lifecycle markers

3. **Popup consistency:**
   - All 8 popup sections render correctly
   - Lifecycle section appears when lifecycle layer active
   - Stay evidence section appears for angle poles
   - Blank field framework applies across all pole types

4. **Map performance:**
   - Large jobs (100+ points) render smoothly
   - Filter toggling is instant
   - Span lines don't cause lag

---

## CODING STANDARDS

Follow existing codebase patterns:

**Python:**
- Type hints where helpful
- Docstrings for public functions
- Keep functions focused (single responsibility)
- Use existing helper functions (e.g., `distance_between()`)

**JavaScript:**
- ES6+ syntax (const/let, arrow functions, template literals)
- Descriptive variable names
- Comment complex logic
- Consistent indentation (2 spaces)

**CSS:**
- BEM naming convention where applicable
- Mobile-responsive (use Bootstrap classes)
- Consistent spacing/colors with existing theme

**Testing:**
- Write tests for new backend functions
- Manual browser testing for frontend changes
- Test on mobile viewport sizes

---

## DEPLOYMENT CHECKLIST

Before marking Phase C complete:

1. ✅ All 4 packages implemented (C1, C2, C3, C4)
2. ✅ All 298+ tests passing
3. ✅ Manual testing on Gordon and Bellsprings jobs
4. ✅ No console errors in browser
5. ✅ Mobile-responsive layout verified
6. ✅ Git commit with clear message:
   ```
   Phase C complete: Map intelligence improvements

   - C1: Feature-type filtering + blank field framework
   - C2: Asset lifecycle visualization
   - C3: Stay evidence at angle poles
   - C4: Span anomaly detection + crossing context

   Fixes 6 operational blockers from P011 feedback.
   All tests green. Ready for validation.
   ```
7. ✅ Push to GitHub master
8. ✅ Update `AI_CONTROL/01_CURRENT_STATE.md`
9. ✅ Update `AI_CONTROL/02_CURRENT_TASK.md`
10. ✅ Update `CHANGELOG.md`

---

## FINAL VALIDATION

After implementation, validate on real jobs:

**Test jobs:**
- P011 (operational feedback source)
- P010
- Gordon (NIE)
- Bellsprings (SPEN)

**Validation criteria:**

1. **Context features visible:**
   - Activate "Context/Crossings" filter
   - Verify gates, fences, roads, crossings appear
   - Check different symbols from poles

2. **Height field framework correct:**
   - Existing pole: "Height: not captured (review required)" ⚠️
   - Proposed pole: "Height: not yet specified (design decision)" ℹ️
   - Context record: Height field hidden

3. **Lifecycle states accurate:**
   - EX↔PR linking lines render
   - Suggested vs confirmed matches distinguished
   - Lifecycle popup section correct

4. **Stay evidence detection:**
   - Angle poles identified
   - Missing stay warnings appear
   - Found stay evidence displayed

5. **Span anomalies flagged:**
   - <10m spans flagged as duplicates
   - >500m spans flagged as missing poles
   - Span distance labels readable

6. **Crossing context enriched:**
   - Road crossings: "Critical clearance check required"
   - 11kV/33kV crossings: "Voltage separation required"
   - Priority levels correct

---

## SUCCESS CRITERIA

Phase C is complete when:

✅ **All 6 operational blockers resolved:**
1. Context features now visible and filterable
2. Height field framework distinguishes existing/proposed/context
3. Symbols visually distinct (shape + size + stroke)
4. Stay evidence detection at angle poles functional
5. Span lines + distance labels rendered
6. Popup organization clear and design-focused

✅ **All technical requirements met:**
- 298+ tests passing
- No console errors
- Mobile-responsive
- Committed and pushed to GitHub
- Control docs updated

✅ **Real-world validation positive:**
- Designer can use filters to focus on review items
- Missing evidence is clearly flagged
- Design blockers are actionable
- Tool provides value beyond current Field Maps/manual review

---

## QUESTIONS / CLARIFICATIONS

If anything is unclear during implementation:

1. **Check evidence first:**
   - Re-read P011_OPERATIONAL_FEEDBACK
   - Re-read domain reference summary
   - Re-read practitioner review summary

2. **Minimal scope:**
   - If a feature isn't explicitly specified above, don't build it
   - Ask before adding "nice-to-have" features
   - Phase C scope is fixed — no expansion

3. **Report blockers immediately:**
   - If tests fail unexpectedly
   - If existing functionality breaks
   - If specifications conflict

---

## HANDOFF COMMAND FOR CURSOR

**When ready to begin implementation, use this exact command:**

```
Phase C is approved. Read CURSOR_BRIEF_PHASE_C.md and implement packages C1-C4.

Implementation order:
1. C1: Feature-type filtering + blank field framework
2. C2: Asset lifecycle visualization
3. C3: Stay evidence at angle poles
4. C4: Span anomaly detection + crossing context

Requirements:
- Test after each package
- All 298 tests must stay green
- No files outside Phase C scope
- Follow specifications exactly

Report completion when all 4 packages are done and tests pass.
```

---

**END OF BRIEF**
