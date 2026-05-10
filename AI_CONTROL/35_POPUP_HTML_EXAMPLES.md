# C2E2 Popup HTML Examples

## Purpose

Reference examples for popup HTML structure after C2E2 implementation.
Shows grouped layout, field labels, missing-value wording.

---

## Example 1: EXpole with Measured Height

**Feature properties:**
- pole_id: "29"
- structure_type: "EXpole"
- asset_intent: "Existing asset"
- record_role: "structural"
- easting: 365155.028
- northing: 643657.644
- height: 9.2
- qa_status: "PASS"
- issue_count: 0
- warn_count: 0
- name: "ex pole"
- material: null
- relationship: "replacement_pair"

**Expected popup HTML:**

```html
<div class="popup-content">

  <!-- Group 1: Identity and role -->
  <div class="popup-section">
    <h4>IDENTITY AND ROLE</h4>
    <div class="field-row">
      <span class="field-label">Point ID:</span>
      <span class="field-value">29</span>
    </div>
    <div class="field-row">
      <span class="field-label">Feature Code:</span>
      <span class="field-value">EXpole</span>
    </div>
    <div class="field-row">
      <span class="field-label">Asset Intent:</span>
      <span class="field-value">Existing asset</span>
    </div>
    <div class="field-row">
      <span class="field-label">Record Role:</span>
      <span class="field-value">structural</span>
    </div>
  </div>

  <!-- Group 2: Geometry and measured evidence -->
  <div class="popup-section">
    <h4>GEOMETRY AND MEASURED EVIDENCE</h4>
    <div class="field-row">
      <span class="field-label">Easting:</span>
      <span class="field-value">365155m</span>
    </div>
    <div class="field-row">
      <span class="field-label">Northing:</span>
      <span class="field-value">643658m</span>
    </div>
    <div class="field-row">
      <span class="field-label">Measured Height:</span>
      <span class="field-value">9.2m</span>
    </div>
  </div>

  <!-- Group 3: QA and review status -->
  <div class="popup-section">
    <h4>QA AND REVIEW STATUS</h4>
    <div class="field-row">
      <span class="field-label">QA Status:</span>
      <span class="field-value">PASS</span>
    </div>
    <div class="field-row">
      <span class="field-label">Issues:</span>
      <span class="field-value">0</span>
    </div>
    <div class="field-row">
      <span class="field-label">Warnings:</span>
      <span class="field-value">0</span>
    </div>
  </div>

  <!-- Group 4: Survey context -->
  <div class="popup-section">
    <h4>SURVEY CONTEXT</h4>
    <div class="field-row">
      <span class="field-label">Survey Note:</span>
      <span class="field-value">ex pole</span>
    </div>
    <div class="field-row">
      <span class="field-label">Material:</span>
      <span class="field-value missing">Not recorded in survey</span>
    </div>
  </div>

  <!-- Group 5: Lifecycle / relationships -->
  <div class="popup-section">
    <h4>LIFECYCLE / RELATIONSHIPS</h4>
    <div class="field-row">
      <span class="field-label">Relationship:</span>
      <span class="field-value">replacement_pair</span>
    </div>
  </div>

</div>
```

---

## Example 2: Pol (Intermediate Pole) — No Height Expected

**Feature properties:**
- pole_id: "42"
- structure_type: "Pol"
- record_role: "structural"
- easting: 300000.0
- northing: 400000.0
- height: null
- qa_status: "PASS"
- issue_count: 0
- warn_count: 0
- material: null

**Expected popup HTML:**

```html
<div class="popup-content">

  <div class="popup-section">
    <h4>IDENTITY AND ROLE</h4>
    <div class="field-row">
      <span class="field-label">Point ID:</span>
      <span class="field-value">42</span>
    </div>
    <div class="field-row">
      <span class="field-label">Feature Code:</span>
      <span class="field-value">Pol</span>
    </div>
    <div class="field-row">
      <span class="field-label">Record Role:</span>
      <span class="field-value">structural</span>
    </div>
  </div>

  <div class="popup-section">
    <h4>GEOMETRY AND MEASURED EVIDENCE</h4>
    <div class="field-row">
      <span class="field-label">Easting:</span>
      <span class="field-value">300000m</span>
    </div>
    <div class="field-row">
      <span class="field-label">Northing:</span>
      <span class="field-value">400000m</span>
    </div>
    <div class="field-row">
      <span class="field-label">Measured Height:</span>
      <span class="field-value missing">Not measured (intermediate pole)</span>
    </div>
  </div>

  <div class="popup-section">
    <h4>QA AND REVIEW STATUS</h4>
    <div class="field-row">
      <span class="field-label">QA Status:</span>
      <span class="field-value">PASS</span>
    </div>
    <div class="field-row">
      <span class="field-label">Issues:</span>
      <span class="field-value">0</span>
    </div>
    <div class="field-row">
      <span class="field-label">Warnings:</span>
      <span class="field-value">0</span>
    </div>
  </div>

  <div class="popup-section">
    <h4>SURVEY CONTEXT</h4>
    <div class="field-row">
      <span class="field-label">Material:</span>
      <span class="field-value missing">Not recorded in survey</span>
    </div>
  </div>

  <!-- Lifecycle/relationships section omitted when no relationship -->

</div>
```

**Note:** "Not measured (intermediate pole)" indicates expected behaviour, not a data quality gap.

---

## Example 3: Context Record (Minimal Fields)

**Feature properties:**
- pole_id: "999"
- structure_type: "Road"
- record_role: "context"
- easting: 365200.0
- northing: 643700.0
- qa_status: "PASS"

**Expected popup HTML:**

```html
<div class="popup-content">

  <div class="popup-section">
    <h4>IDENTITY AND ROLE</h4>
    <div class="field-row">
      <span class="field-label">Point ID:</span>
      <span class="field-value">999</span>
    </div>
    <div class="field-row">
      <span class="field-label">Feature Code:</span>
      <span class="field-value">Road</span>
    </div>
    <div class="field-row">
      <span class="field-label">Record Role:</span>
      <span class="field-value">context</span>
    </div>
  </div>

  <div class="popup-section">
    <h4>GEOMETRY AND MEASURED EVIDENCE</h4>
    <div class="field-row">
      <span class="field-label">Easting:</span>
      <span class="field-value">365200m</span>
    </div>
    <div class="field-row">
      <span class="field-label">Northing:</span>
      <span class="field-value">643700m</span>
    </div>
  </div>

  <div class="popup-section">
    <h4>QA AND REVIEW STATUS</h4>
    <div class="field-row">
      <span class="field-label">QA Status:</span>
      <span class="field-value">PASS</span>
    </div>
  </div>

</div>
```

**Note:** Context records omit height (not applicable) and relationship fields.

---

## JavaScript Usage

```javascript
// Import helpers (or paste inline in map-viewer.js)
// <script src="/static/js/field-display-helpers.js"></script>

const props = feature.properties;

// Get height display for any structure type
const heightStr = getPopupDisplayValue('height', props);
// → "9.2m" (EXpole with height)
// → "Not measured (intermediate pole)" (Pol, no height)

// Get material display
const materialStr = getPopupDisplayValue('material', props);
// → "Not recorded in survey" (all Trimble jobs)

// Render all fields in a group
for (const fieldName of getFieldsForGroup('geometry')) {
  const label = getFieldLabel(fieldName);
  const value = getPopupDisplayValue(fieldName, props);
  // render label + value
}
```

---

## CSS Classes

| Class | Purpose |
|-------|---------|
| `.popup-content` | Outer popup wrapper |
| `.popup-section` | One field group |
| `.popup-section h4` | Group heading |
| `.field-row` | Single label + value pair |
| `.field-label` | Left-aligned label |
| `.field-value` | Right-aligned value |
| `.field-value.missing` | Greyed-out missing-value wording |

---

*Produced by Claude Code claude-code/c2e2-support-suite on 2026-05-09.*
*Paired with: app/static/js/field-display-helpers.js, 32_C2E2_PRE_IMPLEMENTATION_GUIDE.md*
