# PHASE 3 COMPLETE ROADMAP — ALL 8 SPRINTS

**Status:** APPROVED — Complete Implementation Plan
**Date:** 2026-05-01
**Total Estimated Time:** 6-8 weeks (480-640 hours)
**Current Completion:** Phase 3A Sprint 1 complete (eb0fe65)
**Next Steps:** Phase 3B → Phase 3H in sequence

---

## EXECUTIVE SUMMARY

This document defines **Phase 3: Map and Survey Asset Intelligence** — a complete transformation of GridFlow's map from a point-based QA viewer into a structured engineering review workspace.

**8 Phases / 8 Sprints:**
1. ✅ **Phase 3A** — Span/line data model (COMPLETE)
2. ⏳ **Phase 3B** — Clickable overhead span records
3. ⏳ **Phase 3C** — Cable/underground line model
4. ⏳ **Phase 3D** — Electrical field ownership cleanup
5. ⏳ **Phase 3E** — Pole/support data field redesign
6. ⏳ **Phase 3F** — Context and crossing records
7. ⏳ **Phase 3G** — Replacement pair intelligence
8. ⏳ **Phase 3H** — Popup redesign around design decisions

---

## PHASE 3A: SPAN/LINE DATA MODEL (✅ COMPLETE)

**Status:** SHIPPED (commit eb0fe65)
**What It Does:** Creates proper span/line LineString geometries, moves electrical from poles to spans

**Deliverables Shipped:**
- ✅ `app/span_generator.py` — Span generation logic
- ✅ Frontend span rendering with distance labels
- ✅ Electrical properties on spans only
- ✅ 344 tests passing
- ✅ Committed to master

**Next Developer Action:** See CURSOR_BRIEF_PHASE_3A_SPRINT_1.md for complete documentation

---

## PHASE 3B: CLICKABLE OVERHEAD SPAN RECORDS

**Status:** PENDING
**Timeline:** 1 week (40-50 hours)
**Depends On:** Phase 3A (complete ✅)

### What This Phase Builds

Makes span lines **interactive, rich objects** with comprehensive electrical and design data.

### Deliverables

#### Backend Changes

**1. Enhance `app/span_generator.py`**

Add functions:

```python
def generate_span_popup_data(span: dict, pole1: dict, pole2: dict) -> dict:
    """
    Build comprehensive popup data for span.

    Returns:
    {
        'span_id': '47-48',
        'from_support': {'id': '47', 'type': 'existing', 'height': 9.2},
        'to_support': {'48', 'type': 'proposed', 'spec': 'Class 4'},
        'span': {'distance_m': 45.2, 'bearing_deg': 215},
        'electrical': {
            'voltage': '11kV',
            'conductor_type': 'AAC',
            'conductor_size': '50mm²',
            'phases': 3,
            'circuit_id': 'SPEN-474-Main',
            'source': 'captured' | 'inferred' | 'estimated'
        },
        'clearances': {
            'measured': null,
            'required': 'TBD',
            'crossings': [...]
        },
        'design_notes': ['Long span - verify sag', 'Clearance not measured'],
        'warnings': [...],
        'actions': [...]
    }
    """

def classify_span_crossing_risks(span: dict, context_records: list) -> list:
    """
    Find context records (roads, utilities, etc.) that cross this span.

    Returns:
    [
        {
            'context_id': 'crossing_23',
            'type': 'road',
            'distance_to_pole1_m': 15,
            'distance_to_pole2_m': 25,
            'required_clearance_m': 5.8,
            'measured_clearance_m': null,
            'risk_level': 'medium'
        },
        ...
    ]
    """

def generate_span_designer_actions(span: dict, context: dict) -> list:
    """
    Generate designer action items for this span.

    Returns actions like:
    - 'Verify conductor size (not captured)'
    - 'Check clearance at road crossing (x meters)'
    - 'Confirm sag calculation for 45m span'
    """
```

**2. Update `app/routes/map_preview.py`**

```python
# In map enrichment, add span-specific enrichment:

def enrich_span_for_popup(span: dict, all_features: dict, all_spans: dict) -> dict:
    """
    Enrich span with full popup data, designer actions, warnings.
    """
    # Get connected poles
    pole1 = find_pole_by_id(span['properties']['from_support_id'], all_features)
    pole2 = find_pole_by_id(span['properties']['to_support_id'], all_features)

    # Get crossing context
    context_records = find_crossings_for_span(span, all_features)
    crossing_risks = classify_span_crossing_risks(span, context_records)

    # Get previous/next spans for sequence
    prev_span = find_prev_span_in_sequence(span, all_spans)
    next_span = find_next_span_in_sequence(span, all_spans)

    # Generate actions
    actions = generate_span_designer_actions(span, {
        'poles': [pole1, pole2],
        'context': context_records,
        'crossings': crossing_risks,
        'prev_span': prev_span,
        'next_span': next_span
    })

    return {
        **span['properties'],
        'popup_data': generate_span_popup_data(span, pole1, pole2),
        'crossing_risks': crossing_risks,
        'designer_actions': actions,
        'sequence_context': {
            'prev_span_id': prev_span['span_id'] if prev_span else null,
            'next_span_id': next_span['span_id'] if next_span else null,
            'sequence_position': get_span_sequence_position(span, all_spans)
        }
    }
```

#### Frontend Changes

**1. Update `app/static/js/map-viewer.js`**

```javascript
// Enhanced span popup with full content

function buildSpanPopupContent(span) {
    const data = span.properties;

    return `
        <div class="span-popup">
            <div class="popup-header">
                <h5>Overhead Span ${data.span_id}</h5>
                <span class="status-badge ${data.span_status}">${data.span_status}</span>
            </div>

            <div class="popup-section">
                <h6>From/To Supports</h6>
                <p><strong>From:</strong> ${data.from_support_id} (${getPoleName(data.from_support_id)})</p>
                <p><strong>To:</strong> ${data.to_support_id} (${getPoleName(data.to_support_id)})</p>
            </div>

            <div class="popup-section">
                <h6>Span Geometry</h6>
                <p><strong>Distance:</strong> ${data.distance_m}m (horizontal)</p>
                <p><strong>3D Distance:</strong> ${data.distance_3d_m}m</p>
                <p><strong>Bearing:</strong> ${data.bearing_deg}°</p>
                <p><strong>Elevation Change:</strong> ${data.elevation_change_m}m</p>
            </div>

            <div class="popup-section">
                <h6>Electrical Characteristics</h6>
                <p><strong>Voltage:</strong> ${data.line_voltage} (${data.voltage_source})</p>
                <p><strong>Conductor:</strong> ${data.conductor_type || 'not captured'}</p>
                <p><strong>Size:</strong> ${data.conductor_size || 'not captured'}</p>
                <p><strong>Phases:</strong> ${data.phase_count || 'not captured'}</p>
                ${data.circuit_id ? `<p><strong>Circuit ID:</strong> ${data.circuit_id}</p>` : ''}
            </div>

            <div class="popup-section">
                <h6>Clearances</h6>
                <p><strong>Measured:</strong> ${data.min_clearance_m ? data.min_clearance_m + 'm' : 'not measured'}</p>
                ${data.crossing_risks && data.crossing_risks.length > 0 ? `
                    <p><strong>Crossings:</strong> ${data.crossing_risks.length}</p>
                    <ul class="crossing-list">
                        ${data.crossing_risks.map(c => `
                            <li>${c.type} - ${c.measured_clearance_m ? c.measured_clearance_m + 'm measured' : 'clearance not measured'}</li>
                        `).join('')}
                    </ul>
                ` : '<p>No crossings detected</p>'}
            </div>

            ${data.designer_actions && data.designer_actions.length > 0 ? `
                <div class="popup-section alert alert-info">
                    <h6>Designer Actions</h6>
                    <ul>
                        ${data.designer_actions.map(a => `<li>${a}</li>`).join('')}
                    </ul>
                </div>
            ` : ''}

            ${data.span_warning ? `
                <div class="popup-section alert alert-${data.span_status === 'fail' ? 'danger' : 'warning'}">
                    <h6>Span Warning</h6>
                    <p>${data.span_warning}</p>
                </div>
            ` : ''}
        </div>
    `;
}
```

**2. Add Span List Panel**

```html
<div class="spans-review-panel">
    <h6>Overhead Spans (<span id="span-count">0</span>)</h6>

    <div class="span-filters">
        <button class="filter-btn" data-filter="all">All</button>
        <button class="filter-btn" data-filter="normal">Normal</button>
        <button class="filter-btn" data-filter="anomaly">Anomaly</button>
        <button class="filter-btn" data-filter="crossing">Crossing</button>
    </div>

    <div class="spans-list">
        <!-- Populated by JavaScript -->
    </div>
</div>
```

#### Tests

```python
# tests/test_span_enrichment.py

def test_span_popup_data_generation():
    """Test comprehensive popup data generation"""

def test_span_crossing_detection():
    """Test crossing risk identification"""

def test_span_designer_actions_generation():
    """Test action item creation"""

def test_span_sequence_context():
    """Test prev/next span linking"""
```

### Acceptance Criteria

1. ✅ Span popup shows from/to supports with metadata
2. ✅ Electrical characteristics displayed (voltage, conductor, phases)
3. ✅ Crossing risks identified and listed
4. ✅ Designer actions auto-generated
5. ✅ Span sequence context (prev/next spans)
6. ✅ 350+ tests passing
7. ✅ No console errors
8. ✅ Real jobs validated (P009/F002, P009/F001, P005/F001)

---

## PHASE 3C: CABLE/UNDERGROUND LINE MODEL

**Status:** PENDING
**Timeline:** 1-1.5 weeks (50-60 hours)
**Depends On:** Phase 3A (complete ✅)

### What This Phase Builds

Creates proper cable/underground LineString features with full electrical and routing data.

### Key Components

**1. Cable LineString Generation** (`app/span_generator.py`)

```python
def generate_cable_routes(
    underground_records: list[dict],
    job_voltage: str | None = None,
    rulepack_id: str | None = None
) -> list[dict]:
    """
    Generate underground cable LineString features.

    Each cable includes:
    - from_asset, to_asset (joint IDs or pole IDs)
    - voltage, cable_type, cable_size
    - route_length, burial_depth, ducting
    - joints, terminations
    - road/footway/utility crossings
    - proposed/existing/recovered status
    """
```

**2. Cable Popup** (frontend)

Shows:
- Cable identity (from/to, voltage, type)
- Route specifications (length, depth, ducting)
- Crossings and third-party risks
- Designer actions

**3. Cable Filters** (right panel)

- Missing cable type
- Missing cable size
- Missing burial depth
- Road crossing
- Third-party crossing

### Acceptance Criteria

1. ✅ Cable LineStrings generated from UG records
2. ✅ Cable popups show routing + electrical
3. ✅ Cable filters functional
4. ✅ Joint/termination points marked
5. ✅ Crossing detection working
6. ✅ 360+ tests passing

---

## PHASE 3D: ELECTRICAL FIELD OWNERSHIP CLEANUP

**Status:** PENDING (60% complete from 3A)
**Timeline:** 3-4 days (24-32 hours)
**Depends On:** Phase 3A (complete ✅)

### What This Phase Does

**Already done in 3A:**
- ✅ Electrical removed from pole popups
- ✅ Electrical on spans only
- ✅ Raw fields remain on poles for coalescing

**This phase completes:**

1. **Verify field ownership across all objects**

```python
# Validate that:
# - Poles have ONLY: structure, mechanical, equipment, connectivity
# - Spans have: electrical (voltage, conductor, phases, circuit)
# - Cables have: electrical, routing (depth, ducting, joints)
# - Stays/Anchors have: mechanical (bearing, distance, config)
# - Context have: environmental (clearance, risk, action)
```

2. **Create field ownership matrix**

```
Object Type | Should Have | Should NOT Have
----------|-------------|----------------
Pole      | height, material, condition, stay, equipment | voltage, conductor, phases
Span      | voltage, conductor, phases, circuit | structure, material, condition
Cable     | voltage, size, depth, routing | structure, stay, mounting
Stay      | bearing, distance, anchor_type | electrical, structure
Context   | clearance, risk, owner | voltage, equipment
```

3. **Automated validation tests**

```python
def test_field_ownership_poles():
    """Assert poles never have electrical fields"""

def test_field_ownership_spans():
    """Assert spans always have electrical fields when available"""

def test_no_duplication():
    """Assert no field appears on multiple object types"""
```

### Acceptance Criteria

1. ✅ Field ownership matrix documented
2. ✅ Automated tests validate ownership
3. ✅ No fields on wrong objects
4. ✅ All documentation updated
5. ✅ 370+ tests passing

---

## PHASE 3E: POLE/SUPPORT DATA FIELD REDESIGN

**Status:** PENDING
**Timeline:** 1.5 weeks (60-80 hours)
**Depends On:** Phase 3A (complete ✅)

### What This Phase Designs

Restructures pole properties into **universal + role-specific** fields.

### Universal Fields (All Points)

```python
{
    # Identity
    'point_id': '47',
    'asset_id': 'EX-474-47',
    'feature_code': 'EXpole',
    'asset_type': 'electric_network_pole',
    'record_role': 'structural',

    # Location
    'easting': 365645.432,
    'northing': 643987.136,
    'lat': 55.68813,
    'lon': -2.54800,
    'elevation': 127.3,
    'crs': 'EPSG:27700',

    # Capture
    'surveyor': 'John Smith',
    'survey_date': '2026-04-15',
    'gnss_accuracy': 'RTK',
    'horizontal_accuracy_m': 0.05,
    'vertical_accuracy_m': 0.08,
    'capture_method': 'GNSS RTK',

    # QA/Status
    'qa_status': 'PASS' | 'WARN' | 'FAIL',
    'issues': ['issue_id_1', 'issue_id_2'],
    'review_category': 'design_blocker' | 'review_required' | 'pass',
    'design_impact': 'Cannot proceed without field measurement',

    # Lifecycle
    'lifecycle_state': 'existing' | 'proposed' | 'retained' | 'recovered',
    'replacement_status': 'being_replaced' | 'replacing' | 'independent',
    'linked_support_id': '48' # if replacement pair
}
```

### Existing Pole Fields

```python
{
    # Physical
    'measured_height_m': 9.2,
    'height_source': 'RTK measurement' | 'tape' | 'estimated' | 'plan',
    'pole_class': 'Class 4',
    'material': 'Timber',
    'species': 'Scots Pine',
    'treatment': 'Preservative treated',
    'year_installed': 1987,

    # Condition
    'condition': 'good' | 'fair' | 'poor' | 'unsafe',
    'defects': ['rot', 'split', 'woodpecker_damage'],
    'decay_location': 'butt',
    'decay_severity': 'minor' | 'moderate' | 'severe',
    'lean_direction': '225°',
    'lean_severity': 'slight' | 'moderate' | 'severe',

    # Foundation
    'foundation_type': 'direct_buried' | 'concrete' | 'rock_anchor',
    'ground_condition': 'clay' | 'sand' | 'rock',
    'access_constraint': 'Farm entrance - landowner permission required'
}
```

### Proposed Pole Fields

```python
{
    'proposed_height_m': 9.5,
    'proposed_class': 'Class 4',
    'proposed_material': 'Timber',
    'specification_source': 'design' | 'indicative' | 'unspecified',
    'purpose': 'Replacement for EXpole 47' | 'New intermediate',
    'design_specification': 'Full spec document',
    'unresolved_decisions': ['height_to_confirm', 'material_to_confirm']
}
```

### Angle Pole Fields

```python
{
    'route_deviation_deg': 28.5,
    'angle_severity': 'minor' | 'moderate' | 'severe',
    'stay_required': True,
    'stay_evidence_status': 'captured' | 'missing' | 'not_applicable',
    'stay_type': 'Angle stay' | 'Terminal stay' | 'Tee-off stay',
    'stay_count': 1,
    'stay_bearing': '215°',
    'stay_lead_distance_m': 12.4,
    'stay_configuration': 'single' | 'tandem' | 'multiple'
}
```

### Stay/Anchor Fields

```python
{
    'parent_pole_id': '47',
    'linked_support_id': null,  # If multiple supports
    'stay_type': 'Angle stay',
    'stay_bearing': '215°',
    'stay_lead_distance_m': 12.4,
    'stay_count': 1,
    'anchor_type': 'Ground',
    'anchor_coordinates': [easting, northing],
    'condition': 'good' | 'fair' | 'poor',
    'existing_proposed_recovered': 'existing'
}
```

### Implementation

1. **Restructure POPUP_DATA_FIELDS in `app/routes/map_preview.py`**
2. **Update `app/electrical_schema.py` field lists**
3. **Create field validation schema (`app/pole_field_schema.py`)**
4. **Generate field documentation**

### Acceptance Criteria

1. ✅ Universal field schema defined + implemented
2. ✅ Role-specific fields (existing, proposed, angle, stay) defined
3. ✅ Field validation tests (all required fields present)
4. ✅ Documentation complete
5. ✅ 380+ tests passing
6. ✅ Real jobs verified

---

## PHASE 3F: CONTEXT AND CROSSING RECORDS

**Status:** PENDING
**Timeline:** 1 week (40-50 hours)
**Depends On:** Phase 3A-3E

### What This Phase Builds

Makes context/crossing records **first-class objects** with proper linking and risk assessment.

### Context Asset Types

```python
CONTEXT_TYPES = {
    'BT_pole': {'owner': 'BT/Openreach', 'risk': 'coordination'},
    'BT_line': {'owner': 'BT/Openreach', 'risk': 'crossing'},
    'LV_line': {'owner': 'DNO/other', 'risk': 'crossing'},
    '33kV_line': {'owner': 'DNO/other', 'risk': 'voltage_separation'},
    'road': {'owner': 'Authority', 'risk': 'clearance'},
    'footway': {'owner': 'Authority', 'risk': 'clearance'},
    'railway': {'owner': 'Network Rail', 'risk': 'clearance'},
    'water': {'owner': 'Environmental', 'risk': 'foundation'},
    'hedge': {'owner': 'Landowner', 'risk': 'access'},
    'tree': {'owner': 'Landowner', 'risk': 'access'},
    'fence': {'owner': 'Landowner', 'risk': 'access'},
    'building': {'owner': 'Property', 'risk': 'clearance'},
    'underground_utility': {'owner': 'Utility', 'risk': 'crossing'}
}
```

### Crossing Linking

```python
def link_context_to_spans(context_records: list, span_features: list) -> dict:
    """
    Link context records to affected spans.

    Returns:
    {
        'span_id': '47-48',
        'crossings': [
            {
                'context_id': 'crossing_42',
                'type': 'road',
                'distance_from_pole1_m': 15,
                'distance_from_pole2_m': 25,
                'measured_clearance_m': null,
                'required_clearance_m': 5.8,
                'risk_level': 'medium',
                'action': 'Measure clearance before design'
            }
        ]
    }
    """

def assess_crossing_risk(context: dict, span: dict) -> dict:
    """
    Assess risk level for a context/span combination.

    Consider:
    - Type of crossing (road, utility, building)
    - Owner/operator
    - Measured vs required clearance
    - Third-party coordination needs
    """
```

### Popup

Shows:
- Context type + owner
- Linked spans (if any)
- Clearance (measured vs required)
- Risk assessment
- Designer actions

### Acceptance Criteria

1. ✅ Context records linked to spans
2. ✅ Crossing risks auto-assessed
3. ✅ Clearance tracking (measured vs required)
4. ✅ Third-party coordination flagged
5. ✅ Context filters functional
6. ✅ 390+ tests passing

---

## PHASE 3G: REPLACEMENT PAIR INTELLIGENCE

**Status:** PENDING (20% complete, basic detection works)
**Timeline:** 5-6 days (40-48 hours)
**Depends On:** Phase 3A-3C

### What This Phase Enhances

Makes **replacement pair matching auditable, verifiable, and designer-actionable**.

### Current State

✅ Detection works (offset matching, proximity)
✅ Pairs shown on map (orange dashed lines)
❌ Matching logic not fully documented
❌ Confidence scoring missing
❌ Designer review workflow missing

### Enhancements

**1. Confidence Scoring**

```python
def calculate_replacement_confidence(ex_pole: dict, pr_pole: dict) -> dict:
    """
    Score replacement pair likelihood (0-100%).

    Factors:
    - Offset distance (ideal <5m, acceptable <20m)
    - Function match (angle→angle, terminal→terminal)
    - Height similarity (existing measured, proposed spec)
    - Material compatibility
    - Sequence position (should be adjacent in route)
    """
```

**2. Match Classification**

```python
MATCH_TYPES = {
    'direct_replacement': 'EX at position being replaced by PR at same location',
    'nearby_replacement': 'EX near PR (offset <20m), likely replacement',
    'co_located': 'EX and PR at nearly same spot, unclear intent',
    'repositioned': 'EX moved slightly, PR at offset 5-20m',
    'unmatched_ex': 'EX with no nearby PR',
    'unmatched_pr': 'PR with no nearby EX',
    'ambiguous_cluster': 'Multiple EX/PR in area, pairings unclear'
}
```

**3. Designer Review Interface**

```
Replacement Pair 47→48
Status: Suggested (unconfirmed)
Confidence: 92%
Distance Offset: 0.5m
Match Type: Direct replacement

EXpole 47:
  Height: 9.2m (measured)
  Class: Class 4
  Condition: Fair
  Action: Being replaced

Proposed Support 48:
  Height: 9.5m (spec)
  Class: Class 4
  Design: Complete

Designer Actions:
  [ ] Confirm pairing
  [ ] Reassign pole (if needed)
  [ ] Link stay to replacement
```

**4. Pairing Audit Trail**

```python
{
    'pair_id': 'pair_47_48',
    'ex_pole_id': '47',
    'pr_pole_id': '48',
    'offset_m': 0.5,
    'match_type': 'direct_replacement',
    'confidence_pct': 92,
    'detection_method': 'automatic_proximity_match',
    'detection_timestamp': '2026-04-15T14:32:00Z',
    'review_status': 'unconfirmed' | 'confirmed' | 'rejected',
    'reviewed_by': null,
    'review_timestamp': null,
    'designer_notes': null
}
```

### Implementation

1. **Add confidence scoring to `app/span_generator.py`**
2. **Create replacement pair review UI (frontend)**
3. **Add designer annotation capability**
4. **Create audit trail tracking**

### Acceptance Criteria

1. ✅ Confidence scoring functional
2. ✅ Match types classified correctly
3. ✅ Designer review interface working
4. ✅ Audit trail recorded
5. ✅ Rejection/confirmation workflow tested
6. ✅ 400+ tests passing

---

## PHASE 3H: POPUP REDESIGN AROUND DESIGN DECISIONS

**Status:** PENDING
**Timeline:** 1.5 weeks (60-80 hours)
**Depends On:** Phase 3A-3G

### What This Phase Does

Redesigns all popups to be **designer-decision-centric**, not data-dump focused.

### Design Principle

> **Every popup should answer one question: "What do I need to do with this object?"**

### Popup Structures

#### Pole Popup Structure

```
┌─────────────────────────────────────────┐
│ Design Action / Status                  │
│ • Existing pole being replaced by 48    │
│ • Height measurement required           │
│ • Mechanical review required            │
├─────────────────────────────────────────┤
│ Identity                                │
│ • Point: 47                             │
│ • Asset Type: Existing pole             │
│ • Function: Angle                       │
├─────────────────────────────────────────┤
│ Physical Structure                      │
│ • Height: 9.2m (measured RTK)          │
│ • Class: Class 4                        │
│ • Material: Timber (Scots Pine)         │
│ • Condition: Fair                       │
│ • Lean: None detected                   │
├─────────────────────────────────────────┤
│ Mechanical Support                      │
│ • Stay: Angle stay present @ 215°      │
│ • Distance: 12.4m                       │
│ • Condition: Good                       │
├─────────────────────────────────────────┤
│ Mounted Equipment                       │
│ • Transformer: 50kVA                    │
│ • Switch: 3-phase isolator              │
├─────────────────────────────────────────┤
│ Connected Lines                         │
│ • Incoming: from pole 46 (45.2m)       │
│ • Outgoing: to pole 48 (projected)      │
│ → Click span lines for electrical data  │
├─────────────────────────────────────────┤
│ Location                                │
│ • Easting/Northing: 365645.432, 643987 │
│ • Elevation: 127.3m                     │
├─────────────────────────────────────────┤
│ Evidence                                │
│ • Surveyor: John Smith                  │
│ • Date: 2026-04-15                      │
│ • Photos: Pole, pole-top, defect        │
│ • GNSS: RTK (5cm accuracy)              │
├─────────────────────────────────────────┤
│ Designer Blockers                       │
│ • ❌ Height measurement required        │
│ • ⚠️ Material not captured              │
│ • ⚠️ Condition estimate only            │
├─────────────────────────────────────────┤
│ Raw Data (collapsed by default)         │
│ [+] Show raw fields...                  │
└─────────────────────────────────────────┘
```

#### Span Popup Structure

```
┌─────────────────────────────────────────┐
│ Design Actions / Blockers               │
│ • Verify conductor size (not captured)  │
│ • Check clearance at road (15m south)   │
│ • Confirm no intermediate pole missing  │
├─────────────────────────────────────────┤
│ Span Identity                           │
│ • Span 47→48                            │
│ • Status: Recommended route line        │
├─────────────────────────────────────────┤
│ Span Geometry                           │
│ • Distance: 45.2m horizontal            │
│ • 3D: 46.1m (with elevation)           │
│ • Bearing: 215° (southwest)             │
│ • Elevation Change: +8.3m               │
├─────────────────────────────────────────┤
│ Electrical Characteristics              │
│ • Voltage: 11kV (inferred from job)    │
│ • Conductor: Not captured               │
│ • Phases: 3 (assumed)                   │
│ • Circuit ID: SPEN-474-Main (assumed)   │
├─────────────────────────────────────────┤
│ Clearances & Crossings                  │
│ • Measured Clearance: Not measured      │
│ • Road Crossing: 15m south              │
│   Required: 5.8m statutory              │
│   Measured: Not yet (ACTION: measure)   │
├─────────────────────────────────────────┤
│ Support Details                         │
│ • From: EXpole 47 (9.2m, Class 4)      │
│ • To: Proposed 48 (9.5m spec, Class 4) │
├─────────────────────────────────────────┤
│ Warnings                                │
│ ⚠️ Long span - verify sag compliance    │
│ ❌ Clearance not measured               │
├─────────────────────────────────────────┤
│ Raw Data (collapsed)                    │
│ [+] Show electrical detail, crossings...│
└─────────────────────────────────────────┘
```

#### Cable Popup Structure

```
┌─────────────────────────────────────────┐
│ Design Actions                          │
│ • Confirm burial depth (not captured)   │
│ • Verify road crossing risk (ACTION)    │
│ • Plan joint locations                  │
├─────────────────────────────────────────┤
│ Cable Identity                          │
│ • Cable: From joint 47 to termination 48│
│ • Status: Proposed                      │
├─────────────────────────────────────────┤
│ Cable Specifications                    │
│ • Voltage: 11kV                         │
│ • Cable Type: XLPE                      │
│ • Size: 95mm² Cu (assumed)              │
│ • Cores: 3 (3-phase)                    │
├─────────────────────────────────────────┤
│ Route & Installation                    │
│ • Length: 180m                          │
│ • Burial: Direct buried (no duct)       │
│ • Burial Depth: Not captured (ACTION)   │
│ • Surface: Footway                      │
├─────────────────────────────────────────┤
│ Crossings & Risks                       │
│ • Road Crossing: Yes (high risk)        │
│ • Utility Crossing: BT - coordination   │
│ • Joint Locations: 3 planned            │
├─────────────────────────────────────────┤
│ Warnings                                │
│ ❌ Burial depth not captured            │
│ ⚠️ Road crossing - confirm with DNO     │
│ ⚠️ BT crossing - coordination needed    │
└─────────────────────────────────────────┘
```

#### Context/Crossing Popup

```
┌─────────────────────────────────────────┐
│ Crossing Type: Road                     │
│ Owner: Local Authority                  │
│ Risk Level: High (statutory clearance)  │
├─────────────────────────────────────────┤
│ Location                                │
│ • Linked Span: 47→48                    │
│ • Distance from pole 47: 15m south      │
│ • Distance from pole 48: 25m south      │
├─────────────────────────────────────────┤
│ Clearance Requirements                  │
│ • Required (statutory): 5.8m            │
│ • Measured: Not captured (ACTION)       │
│ • Risk: Medium (measurement needed)     │
├─────────────────────────────────────────┤
│ Designer Action                         │
│ [!] MEASURE CLEARANCE before design     │
│     Statutory minimum: 5.8m             │
│     Check at highest road point         │
└─────────────────────────────────────────┘
```

### Implementation

1. **Restructure popup templates in `app/templates/`**
2. **Update `app/static/js/map-viewer.js` popup builders**
3. **Create popup CSS with new layout**
4. **Add collapsible sections for raw data**
5. **Add designer action callouts**

### Acceptance Criteria

1. ✅ All popup structures redesigned
2. ✅ Designer actions prominent
3. ✅ Raw data collapsed by default
4. ✅ CSS styling clean and professional
5. ✅ Mobile-responsive layouts
6. ✅ 410+ tests passing
7. ✅ Real jobs validated

---

## IMPLEMENTATION SCHEDULE

**Timeline: 6-8 weeks (assuming 40 hours/week development)**

```
Week 1-2:   Phase 3B — Clickable overhead spans
Week 2-3:   Phase 3C — Cable/UG lines
Week 3:     Phase 3D — Field ownership cleanup
Week 4-5:   Phase 3E — Pole field redesign
Week 5:     Phase 3F — Context/crossing linking
Week 6:     Phase 3G — Replacement pair intelligence
Week 6-8:   Phase 3H — Popup redesign
Week 8:     Validation, testing, documentation
```

---

## SUCCESS CRITERIA (FINAL)

All 8 phases complete when:

✅ 420+ tests passing
✅ All object types (poles, spans, cables, stays, context) are first-class
✅ Electrical properties on correct objects (spans/cables only)
✅ Popups designed around designer decisions
✅ Real jobs validate correctly on all 3 platforms
✅ Documentation complete and accurate
✅ Code clean, committed to master
✅ No console errors
✅ Mobile-responsive design verified

---

## NEXT DEVELOPER NOTES

Before starting Phase 3B:

1. **Understand Phase 3A:** Read `CURSOR_BRIEF_PHASE_3A_SPRINT_1.md`
2. **Study real jobs:** Validate Phase 3A on P009/F002, P009/F001, P005/F001
3. **Review field ownership:** Understand poles vs spans vs cables
4. **Check tests:** 344 tests passing from Phase 3A
5. **Read this document:** Full context of all 8 phases

---

**END OF PHASE 3 MASTER ROADMAP**
