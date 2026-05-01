# CURSOR: Phase C2/D Complete Implementation

**Date:** 2026-05-01
**Status:** APPROVED FOR IMMEDIATE EXECUTION
**Scope:** Complete Phase C2/D refinement (2-4 weeks / 24-32 hours)
**Evidence:** Phase C review (3,924 words) + Survey research (4,544 words) + Operational feedback

---

## 🎯 EXECUTIVE SUMMARY

**What You're Building:**
Transform GridFlow from "basic QA tool with intelligence" to **"professional survey-display platform with narrow QA focus"**

**Timeline:** 2-4 weeks of focused implementation

**Deliverables:**
1. ✅ Popup CSS emergency fix (2-4 hours)
2. ✅ Map UX professional refinement (1 week)
3. ✅ Popup data model expansion 12→25-35 fields (1-2 weeks)
4. ✅ Asset-specific popup layouts (5 types)
5. ✅ Field Maps display parity confirmation

**Result:** Professional survey-to-design QA platform ready for operational validation

---

## 📋 IMPLEMENTATION ORDER

### **Execute packages in this exact order:**

1. **Package 1:** Emergency Popup CSS Fix (2-4 hours) — FIX OVERFLOW FIRST
2. **Package 2:** Map UX Improvements (1 week) — VISUAL CLARITY
3. **Package 3:** Popup Data Model Expansion (1-2 weeks) — COMPREHENSIVE FIELDS
4. **Package 4:** Asset-Specific Layouts (included in Package 3)
5. **Package 5:** Field Maps Parity Check (4-6 hours, optional)

**After EACH package:**
- Run full test suite: `pytest -v`
- Manual test on Gordon or Bellsprings job
- Verify no regressions
- Report completion before proceeding

---

# PACKAGE 1: EMERGENCY POPUP CSS FIX

**Priority:** CRITICAL — Must complete before other packages
**Time:** 2-4 hours
**Evidence:** User screenshots show text overflow

---

## Problems to Fix

1. Popup container too small (300px default, need 500px)
2. No vertical scrolling (long popups push off screen)
3. Section/field classes exist in JS but have no CSS
4. Status indicators (ok/review/warning/blocker) not styled
5. No visual hierarchy between sections

---

## Implementation

### Step 1.1: Add Popup Container CSS

**File:** `app/static/style.css`

**Add at bottom of file:**

```css
/* ========================================
   LEAFLET POPUP CONTAINER OVERRIDES
   ======================================== */

/* Increase max-width for expanded field count */
.leaflet-popup-content-wrapper {
  max-width: 500px !important;
  min-width: 350px;
}

/* Enable vertical scrolling for long popups */
.leaflet-popup-content {
  max-height: 70vh !important;
  overflow-y: auto !important;
  margin: 0 !important;
  padding: 12px 16px !important;
}

/* Scrollbar styling */
.leaflet-popup-content::-webkit-scrollbar {
  width: 8px;
}

.leaflet-popup-content::-webkit-scrollbar-track {
  background: #f1f1f1;
}

.leaflet-popup-content::-webkit-scrollbar-thumb {
  background: #888;
  border-radius: 4px;
}

.leaflet-popup-content::-webkit-scrollbar-thumb:hover {
  background: #555;
}
```

---

### Step 1.2: Add Popup Section and Field Styling

**Continue in `app/static/style.css`:**

```css
/* ========================================
   POPUP SECTIONS
   ======================================== */

.popup-section {
  margin-bottom: 12px;
  border-bottom: 1px solid #e5e7eb;
  padding-bottom: 8px;
}

.popup-section:last-child {
  border-bottom: none;
  margin-bottom: 0;
}

.popup-section-title {
  font-size: 0.9rem;
  font-weight: 700;
  color: #1f2937;
  margin-bottom: 6px;
  padding-bottom: 4px;
  border-bottom: 2px solid #3b82f6;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

/* ========================================
   POPUP FIELDS
   ======================================== */

.popup-field {
  margin-bottom: 6px;
  padding: 4px 8px;
  border-radius: 3px;
  background-color: #ffffff;
}

.popup-field-label {
  font-size: 0.75rem;
  font-weight: 600;
  color: #6b7280;
  margin-bottom: 2px;
}

.popup-field-value {
  font-size: 0.85rem;
  color: #1f2937;
  font-weight: 500;
}

.popup-field-detail {
  font-size: 0.72rem;
  color: #6b7280;
  margin-top: 2px;
  font-style: italic;
  line-height: 1.3;
}

/* ========================================
   FIELD STATUS STYLING
   ======================================== */

/* OK/Pass - Green background */
.popup-field.status-ok {
  background-color: #f0fdf4;
  border-left: 3px solid #10b981;
}

/* Info - Blue background */
.popup-field.status-info {
  background-color: #eff6ff;
  border-left: 3px solid #3b82f6;
}

/* Review - Amber background */
.popup-field.status-review {
  background-color: #fffbeb;
  border-left: 3px solid #f59e0b;
}

/* Warning - Orange background */
.popup-field.status-warning {
  background-color: #fef3c7;
  border-left: 3px solid #d97706;
}

/* Blocker/Fail - Red background */
.popup-field.status-blocker,
.popup-field.status-fail {
  background-color: #fef2f2;
  border-left: 3px solid #ef4444;
}

/* ========================================
   RESPONSIVE
   ======================================== */

@media (max-width: 768px) {
  .leaflet-popup-content-wrapper {
    max-width: 90vw !important;
    min-width: 280px;
  }

  .leaflet-popup-content {
    max-height: 60vh !important;
  }
}
```

---

### Step 1.3: Test Popup CSS Fix

**After adding CSS:**

1. Load Gordon or Bellsprings job
2. Click existing pole → popup should:
   - Be 450-500px wide (no overflow)
   - Scroll vertically if content > 70vh
   - Show section titles (bold, blue underline)
   - Show colored status backgrounds
3. Take screenshot showing fixed layout
4. Run `pytest -v` — all tests must pass

---

### Step 1.4: Commit Package 1

```bash
git add app/static/style.css
git commit -m "Package 1: Emergency popup CSS fix

- Increase popup max-width to 500px
- Enable vertical scroll (max-height 70vh)
- Add popup section/field styling
- Add color-coded status backgrounds (ok/info/review/warning/blocker)
- Fix text overflow from Phase C2-2 field expansion

Fixes user-reported popup layout overflow issue.
All 300+ tests passing."
git push origin master
```

**Report completion with screenshots before proceeding to Package 2.**

---

# PACKAGE 2: MAP UX IMPROVEMENTS

**Priority:** HIGH — Visual clarity and usability
**Time:** ~1 week / 8-10 hours
**Evidence:** Phase C review identified 7 major UX problems

---

## Problems to Fix

1. **Markers too large** (visual clutter, overlapping)
2. **Layers vs filters mixed** (confusing panel structure)
3. **EX/PR distinction weak** (not intuitive at glance)
4. **Angle hides lifecycle** (shows "A" but not whether existing/proposed)
5. **Context records compete visually** (should be secondary/muted)
6. **Match warnings too long** (paragraphs instead of visual + short text)
7. **Map key lacks real examples** (text-only legend)

---

## Implementation

### Step 2.1: Reduce Marker Size (25-40%)

**File:** `app/static/js/map-viewer.js`

**Find:** `const MARKER_SIZES = {...}`

**Change from:**
```javascript
const MARKER_SIZES = {
  existing: 17,
  proposed: 17,
  angle: 19,
  anchor: 14,
  context: 11,
  other: 15,
};
```

**Change to:**
```javascript
const MARKER_SIZES = {
  existing: 10,      // was 17 → 41% reduction
  proposed: 10,      // was 17 → 41% reduction
  angle: 12,         // was 19 → 37% reduction
  anchor: 8,         // was 14 → 43% reduction
  context: 6,        // was 11 → 45% reduction
  other: 9,          // was 15 → 40% reduction
};
```

**Test:** Load map, verify markers 30-40% smaller, less visual clutter

---

### Step 2.2: Split Panel (Map Layers + Review Filters)

**File:** `app/templates/map_viewer.html`

**Find the right panel section (likely around line 50-150).**

**Replace single panel with TWO distinct sections:**

```html
<!-- RIGHT PANEL: Map Controls -->
<div class="map-controls-panel" style="position:absolute;top:10px;right:10px;width:280px;background:white;border-radius:8px;box-shadow:0 2px 8px rgba(0,0,0,0.15);padding:16px;max-height:90vh;overflow-y:auto;">

  <!-- SECTION 1: Map Layers (What to show) -->
  <div class="map-layers-section" style="margin-bottom:20px;padding-bottom:16px;border-bottom:2px solid #e5e7eb;">
    <h4 style="margin:0 0 12px 0;font-size:0.95rem;font-weight:700;color:#1f2937;text-transform:uppercase;letter-spacing:0.5px;">Map Layers</h4>

    <div class="layer-toggles" style="display:flex;flex-direction:column;gap:8px;">
      <label style="display:flex;align-items:center;gap:8px;cursor:pointer;padding:4px;border-radius:4px;transition:background 0.2s;" class="layer-toggle">
        <input type="checkbox" id="layer-existing" checked style="cursor:pointer;">
        <span style="font-size:0.85rem;color:#374151;">Existing Poles</span>
      </label>

      <label style="display:flex;align-items:center;gap:8px;cursor:pointer;padding:4px;border-radius:4px;transition:background 0.2s;" class="layer-toggle">
        <input type="checkbox" id="layer-proposed" checked style="cursor:pointer;">
        <span style="font-size:0.85rem;color:#374151;">Proposed Poles</span>
      </label>

      <label style="display:flex;align-items:center;gap:8px;cursor:pointer;padding:4px;border-radius:4px;transition:background 0.2s;" class="layer-toggle">
        <input type="checkbox" id="layer-angle" checked style="cursor:pointer;">
        <span style="font-size:0.85rem;color:#374151;">Angle Poles</span>
      </label>

      <label style="display:flex;align-items:center;gap:8px;cursor:pointer;padding:4px;border-radius:4px;transition:background 0.2s;" class="layer-toggle">
        <input type="checkbox" id="layer-stays" checked style="cursor:pointer;">
        <span style="font-size:0.85rem;color:#374151;">Stays/Anchors</span>
      </label>

      <label style="display:flex;align-items:center;gap:8px;cursor:pointer;padding:4px;border-radius:4px;transition:background 0.2s;" class="layer-toggle">
        <input type="checkbox" id="layer-context" style="cursor:pointer;">
        <span style="font-size:0.85rem;color:#6b7280;">Context/Crossings</span>
      </label>

      <label style="display:flex;align-items:center;gap:8px;cursor:pointer;padding:4px;border-radius:4px;transition:background 0.2s;" class="layer-toggle">
        <input type="checkbox" id="layer-spans" checked style="cursor:pointer;">
        <span style="font-size:0.85rem;color:#374151;">Design Chain Spans</span>
      </label>

      <label style="display:flex;align-items:center;gap:8px;cursor:pointer;padding:4px;border-radius:4px;transition:background 0.2s;" class="layer-toggle">
        <input type="checkbox" id="layer-matches" checked style="cursor:pointer;">
        <span style="font-size:0.85rem;color:#374151;">Replacement Links</span>
      </label>
    </div>
  </div>

  <!-- SECTION 2: Review Filters (What needs attention) -->
  <div class="review-filters-section">
    <h4 style="margin:0 0 12px 0;font-size:0.95rem;font-weight:700;color:#1f2937;text-transform:uppercase;letter-spacing:0.5px;">Review Focus</h4>

    <div class="filter-buttons" style="display:flex;flex-direction:column;gap:6px;">
      <button class="filter-btn" data-filter="blockers" style="padding:8px 12px;border:1px solid #ef4444;background:#fef2f2;color:#991b1b;border-radius:4px;cursor:pointer;font-size:0.8rem;font-weight:600;transition:all 0.2s;text-align:left;">
        🚨 Design Blockers
      </button>

      <button class="filter-btn" data-filter="warnings" style="padding:8px 12px;border:1px solid #f59e0b;background:#fffbeb;color:#92400e;border-radius:4px;cursor:pointer;font-size:0.8rem;font-weight:600;transition:all 0.2s;text-align:left;">
        ⚠️ Review Required
      </button>

      <button class="filter-btn" data-filter="missing-heights" style="padding:8px 12px;border:1px solid #d97706;background:#fef3c7;color:#78350f;border-radius:4px;cursor:pointer;font-size:0.8rem;font-weight:600;transition:all 0.2s;text-align:left;">
        📏 Missing Heights
      </button>

      <button class="filter-btn" data-filter="missing-stays" style="padding:8px 12px;border:1px solid #d97706;background:#fef3c7;color:#78350f;border-radius:4px;cursor:pointer;font-size:0.8rem;font-weight:600;transition:all 0.2s;text-align:left;">
        ⚓ Missing Stay Evidence
      </button>

      <button class="filter-btn" data-filter="span-anomalies" style="padding:8px 12px;border:1px solid #f59e0b;background:#fffbeb;color:#92400e;border-radius:4px;cursor:pointer;font-size:0.8rem;font-weight:600;transition:all 0.2s;text-align:left;">
        📐 Span Anomalies
      </button>

      <button class="filter-btn" data-filter="ex-pr-matches" style="padding:8px 12px;border:1px solid #3b82f6;background:#eff6ff;color:#1e40af;border-radius:4px;cursor:pointer;font-size:0.8rem;font-weight:600;transition:all 0.2s;text-align:left;">
        🔗 EX/PR Matches
      </button>
    </div>
  </div>

</div>
```

**Add CSS for hover effects:**

```css
/* In app/static/style.css */
.layer-toggle:hover {
  background-color: #f3f4f6 !important;
}

.filter-btn:hover {
  transform: translateX(2px);
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.filter-btn:active {
  transform: translateX(0);
}
```

**Wire up layer toggle JavaScript in `map-viewer.js`:**

```javascript
// Add to MapViewer class init() method:
this.setupLayerToggles();

// Add new method:
setupLayerToggles() {
  const toggles = {
    'layer-existing': 'existing',
    'layer-proposed': 'proposed',
    'layer-angle': 'angle',
    'layer-stays': 'stays',
    'layer-context': 'context',
    'layer-spans': 'spans',
    'layer-matches': 'matches'
  };

  Object.entries(toggles).forEach(([id, layerType]) => {
    const checkbox = document.getElementById(id);
    if (checkbox) {
      checkbox.addEventListener('change', (e) => {
        this.layerState[layerType] = e.target.checked;
        this.updateVisibleLayers();
      });
    }
  });
}

updateVisibleLayers() {
  // Filter visible features based on layer state
  this.featureData.forEach(fd => {
    const assetType = this.getAssetMarker(fd.props).type;
    const shouldShow = this.layerState[assetType] !== false;

    if (fd.marker) {
      if (shouldShow) {
        this.map.addLayer(fd.marker);
      } else {
        this.map.removeLayer(fd.marker);
      }
    }
  });

  // Show/hide spans
  if (this.spanLayer) {
    if (this.layerState.spans) {
      this.map.addLayer(this.spanLayer);
    } else {
      this.map.removeLayer(this.spanLayer);
    }
  }

  // Show/hide match links
  if (this.lifecycleMatchLayer) {
    if (this.layerState.matches) {
      this.map.addLayer(this.lifecycleMatchLayer);
    } else {
      this.map.removeLayer(this.lifecycleMatchLayer);
    }
  }
}
```

---

### Step 2.3: Better EX/PR Symbol Distinction

**File:** `app/static/js/map-viewer.js`

**Find:** `createMarker()` or similar marker creation function

**Implement shape-based distinction:**

```javascript
createMarker(lat, lon, props, status) {
  const assetType = this.getAssetMarker(props).type;
  const lifecycleState = props.lifecycle_state || 'standard';

  // SHAPE by asset type (NEVER CHANGES)
  const shapes = {
    'existing': 'square',
    'proposed': 'circle',
    'angle': 'diamond',
    'anchor': 'triangle',
    'context': 'small-diamond',
    'other': 'circle'
  };

  // FILL COLOR by lifecycle state
  const fillColors = {
    'existing': '#ffffff',              // white
    'proposed': '#bfdbfe',              // light blue
    'retained': '#bbf7d0',              // light green
    'recovered': '#fecaca',             // light red
    'being replaced': '#fef3c7',        // light yellow
    'proposed replacement': '#bfdbfe',  // light blue
    'standard': '#ffffff'               // white
  };

  // STROKE COLOR by QA status
  const strokeColors = {
    'PASS': '#10b981',    // green
    'WARN': '#f59e0b',    // amber
    'FAIL': '#ef4444'     // red
  };

  const shape = shapes[assetType] || 'circle';
  const fillColor = fillColors[lifecycleState] || '#ffffff';
  const strokeColor = strokeColors[status] || '#6b7280';
  const size = MARKER_SIZES[assetType] || 10;

  // Create SVG marker
  return this.createSVGMarker(lat, lon, shape, fillColor, strokeColor, size, props);
}

createSVGMarker(lat, lon, shape, fill, stroke, size, props) {
  let svgPath;
  const half = size / 2;

  switch (shape) {
    case 'square':
      svgPath = `M ${-half} ${-half} L ${half} ${-half} L ${half} ${half} L ${-half} ${half} Z`;
      break;
    case 'circle':
      svgPath = `M ${-half} 0 A ${half} ${half} 0 1 1 ${half} 0 A ${half} ${half} 0 1 1 ${-half} 0`;
      break;
    case 'diamond':
      svgPath = `M 0 ${-half} L ${half} 0 L 0 ${half} L ${-half} 0 Z`;
      break;
    case 'triangle':
      svgPath = `M 0 ${-half} L ${half} ${half} L ${-half} ${half} Z`;
      break;
    case 'small-diamond':
      const smallHalf = half * 0.7;
      svgPath = `M 0 ${-smallHalf} L ${smallHalf} 0 L 0 ${smallHalf} L ${-smallHalf} 0 Z`;
      break;
    default:
      svgPath = `M ${-half} 0 A ${half} ${half} 0 1 1 ${half} 0 A ${half} ${half} 0 1 1 ${-half} 0`;
  }

  const svgIcon = L.divIcon({
    className: 'custom-svg-marker',
    html: `
      <svg width="${size * 2}" height="${size * 2}" viewBox="${-size} ${-size} ${size * 2} ${size * 2}">
        <path d="${svgPath}" fill="${fill}" stroke="${stroke}" stroke-width="2"/>
      </svg>
    `,
    iconSize: [size * 2, size * 2],
    iconAnchor: [size, size],
    popupAnchor: [0, -size]
  });

  return L.marker([lat, lon], { icon: svgIcon });
}
```

---

### Step 2.4: Angle as Overlay Badge

**Add angle badge to existing/proposed markers when function is "Angle":**

```javascript
createSVGMarker(lat, lon, shape, fill, stroke, size, props) {
  // ... existing SVG creation code ...

  // Add angle badge if pole has angle function
  let angleBadge = '';
  if (props.function === 'Angle' || props.is_angle_pole) {
    const badgeSize = size * 0.5;
    const badgeX = size * 0.5;
    const badgeY = -size * 0.5;
    angleBadge = `
      <circle cx="${badgeX}" cy="${badgeY}" r="${badgeSize}" fill="#ef4444" stroke="white" stroke-width="1"/>
      <text x="${badgeX}" y="${badgeY}" text-anchor="middle" dominant-baseline="central" fill="white" font-size="${badgeSize * 1.2}" font-weight="bold">A</text>
    `;
  }

  const svgIcon = L.divIcon({
    className: 'custom-svg-marker',
    html: `
      <svg width="${size * 3}" height="${size * 3}" viewBox="${-size * 1.5} ${-size * 1.5} ${size * 3} ${size * 3}">
        <path d="${svgPath}" fill="${fill}" stroke="${stroke}" stroke-width="2"/>
        ${angleBadge}
      </svg>
    `,
    iconSize: [size * 3, size * 3],
    iconAnchor: [size * 1.5, size * 1.5],
    popupAnchor: [0, -size * 1.5]
  });

  return L.marker([lat, lon], { icon: svgIcon });
}
```

---

### Step 2.5: Context Records Visually Secondary

**Modify context marker creation:**

```javascript
// In createSVGMarker(), add context-specific styling:
if (assetType === 'context') {
  fill = '#f3f4f6';      // very light gray
  stroke = '#9ca3af';    // muted gray
  opacity = 0.6;         // semi-transparent
}

// Update SVG with opacity:
const svgIcon = L.divIcon({
  className: 'custom-svg-marker',
  html: `
    <svg width="${size * 2}" height="${size * 2}" viewBox="${-size} ${-size} ${size * 2} ${size * 2}" opacity="${opacity || 1}">
      <path d="${svgPath}" fill="${fill}" stroke="${stroke}" stroke-width="2"/>
      ${angleBadge}
    </svg>
  `,
  // ...
});
```

**Set context layer OFF by default:**

```javascript
// In map_viewer.html, change context checkbox:
<input type="checkbox" id="layer-context" style="cursor:pointer;">
<!-- Note: NOT checked by default -->
```

---

### Step 2.6: Shorten Match Warnings

**File:** `app/static/js/map-viewer.js`

**Find lifecycle/match warning text in popup builders.**

**Change from:**
```javascript
"This existing pole appears to have a nearby proposed pole at 15.2m distance. Review to confirm this is an intended replacement pair or reassign if needed."
```

**Change to:**
```javascript
"Suggested replacement link — unconfirmed. Review pairing page to confirm."
```

**Visual representation via dashed line (already exists from Phase C, verify it's rendering):**

```javascript
// Verify this function exists and works:
renderLifecycleMatchLinks(features) {
  const matchPairs = features.filter(f =>
    f.properties.relationship === 'replacement_pair'
  );

  matchPairs.forEach(pair => {
    const exPole = features.find(f => f.properties.id === pair.properties.replacing);
    const prPole = pair;

    if (exPole && prPole) {
      L.polyline(
        [[exPole.lat, exPole.lon], [prPole.lat, prPole.lon]],
        {
          color: '#94a3b8',
          weight: 1,
          dashArray: '5, 5',
          opacity: 0.5
        }
      ).bindTooltip(`Suggested replacement link — ${pair.properties.match_offset_m?.toFixed(1) || '?'}m`);
    }
  });
}
```

---

### Step 2.7: Update Map Key with Real Symbol Examples

**File:** `app/templates/map_viewer.html`

**Add map legend/key below the map or in left panel:**

```html
<!-- MAP LEGEND -->
<div class="map-legend" style="position:absolute;bottom:20px;left:20px;background:white;border-radius:8px;box-shadow:0 2px 8px rgba(0,0,0,0.15);padding:16px;max-width:300px;">
  <h4 style="margin:0 0 12px 0;font-size:0.9rem;font-weight:700;color:#1f2937;">Map Key</h4>

  <!-- Asset Types -->
  <div class="legend-section" style="margin-bottom:12px;">
    <h5 style="margin:0 0 6px 0;font-size:0.8rem;font-weight:600;color:#6b7280;text-transform:uppercase;">Asset Types (by shape)</h5>

    <div class="legend-item" style="display:flex;align-items:center;gap:8px;margin-bottom:4px;">
      <svg width="16" height="16" viewBox="-8 -8 16 16">
        <path d="M -6 -6 L 6 -6 L 6 6 L -6 6 Z" fill="white" stroke="#10b981" stroke-width="2"/>
      </svg>
      <span style="font-size:0.8rem;color:#374151;">Existing Pole</span>
    </div>

    <div class="legend-item" style="display:flex;align-items:center;gap:8px;margin-bottom:4px;">
      <svg width="16" height="16" viewBox="-8 -8 16 16">
        <circle cx="0" cy="0" r="6" fill="#bfdbfe" stroke="#10b981" stroke-width="2"/>
      </svg>
      <span style="font-size:0.8rem;color:#374151;">Proposed Pole</span>
    </div>

    <div class="legend-item" style="display:flex;align-items:center;gap:8px;margin-bottom:4px;">
      <svg width="16" height="16" viewBox="-8 -8 16 16">
        <path d="M 0 -6 L 6 0 L 0 6 L -6 0 Z" fill="white" stroke="#ef4444" stroke-width="2"/>
        <circle cx="4" cy="-4" r="3" fill="#ef4444" stroke="white" stroke-width="1"/>
        <text x="4" y="-4" text-anchor="middle" dominant-baseline="central" fill="white" font-size="4" font-weight="bold">A</text>
      </svg>
      <span style="font-size:0.8rem;color:#374151;">Angle Pole (overlay badge)</span>
    </div>

    <div class="legend-item" style="display:flex;align-items:center;gap:8px;margin-bottom:4px;">
      <svg width="16" height="16" viewBox="-8 -8 16 16">
        <path d="M 0 -6 L 6 6 L -6 6 Z" fill="white" stroke="#6b7280" stroke-width="2"/>
      </svg>
      <span style="font-size:0.8rem;color:#374151;">Stay/Anchor</span>
    </div>

    <div class="legend-item" style="display:flex;align-items:center;gap:8px;">
      <svg width="12" height="12" viewBox="-6 -6 12 12">
        <path d="M 0 -4 L 4 0 L 0 4 L -4 0 Z" fill="#f3f4f6" stroke="#9ca3af" stroke-width="1" opacity="0.6"/>
      </svg>
      <span style="font-size:0.8rem;color:#6b7280;">Context/Crossing</span>
    </div>
  </div>

  <!-- QA Status -->
  <div class="legend-section" style="margin-bottom:12px;">
    <h5 style="margin:0 0 6px 0;font-size:0.8rem;font-weight:600;color:#6b7280;text-transform:uppercase;">QA Status (by stroke color)</h5>

    <div class="legend-item" style="display:flex;align-items:center;gap:8px;margin-bottom:4px;">
      <svg width="16" height="16" viewBox="-8 -8 16 16">
        <circle cx="0" cy="0" r="6" fill="white" stroke="#10b981" stroke-width="3"/>
      </svg>
      <span style="font-size:0.8rem;color:#374151;">Pass</span>
    </div>

    <div class="legend-item" style="display:flex;align-items:center;gap:8px;margin-bottom:4px;">
      <svg width="16" height="16" viewBox="-8 -8 16 16">
        <circle cx="0" cy="0" r="6" fill="white" stroke="#f59e0b" stroke-width="3"/>
      </svg>
      <span style="font-size:0.8rem;color:#374151;">Review Required</span>
    </div>

    <div class="legend-item" style="display:flex;align-items:center;gap:8px;">
      <svg width="16" height="16" viewBox="-8 -8 16 16">
        <circle cx="0" cy="0" r="6" fill="white" stroke="#ef4444" stroke-width="3"/>
      </svg>
      <span style="font-size:0.8rem;color:#374151;">Design Blocker</span>
    </div>
  </div>

  <!-- Route Elements -->
  <div class="legend-section">
    <h5 style="margin:0 0 6px 0;font-size:0.8rem;font-weight:600;color:#6b7280;text-transform:uppercase;">Route Elements</h5>

    <div class="legend-item" style="display:flex;align-items:center;gap:8px;margin-bottom:4px;">
      <svg width="30" height="4">
        <line x1="0" y1="2" x2="30" y2="2" stroke="#3b82f6" stroke-width="2"/>
      </svg>
      <span style="font-size:0.8rem;color:#374151;">Design Chain Span</span>
    </div>

    <div class="legend-item" style="display:flex;align-items:center;gap:8px;">
      <svg width="30" height="4">
        <line x1="0" y1="2" x2="30" y2="2" stroke="#94a3b8" stroke-width="1" stroke-dasharray="3, 2"/>
      </svg>
      <span style="font-size:0.8rem;color:#374151;">Suggested Replacement Link</span>
    </div>
  </div>
</div>
```

---

### Step 2.8: Test Map UX Improvements

**After implementing all 7 changes:**

1. Load Gordon or Bellsprings job
2. Verify:
   - ✅ Markers 30-40% smaller
   - ✅ Panel split (Map Layers + Review Filters)
   - ✅ EX = square, PR = circle visible
   - ✅ Angle poles show base type + A badge
   - ✅ Context records muted/smaller
   - ✅ Match warnings shortened
   - ✅ Map key shows real symbol examples
3. Take screenshots
4. Run `pytest -v` — all tests must pass

---

### Step 2.9: Commit Package 2

```bash
git add app/templates/map_viewer.html app/static/js/map-viewer.js app/static/style.css
git commit -m "Package 2: Map UX improvements

- Reduce marker sizes 30-40% (less visual clutter)
- Split panel: Map Layers + Review Filters (clear separation)
- Better EX/PR symbols: square vs circle (shape = type, color = lifecycle, stroke = QA)
- Angle as overlay badge (shows EX/PR base type + A badge)
- Context records visually secondary (muted, smaller, off by default)
- Shorten match warnings (visual dashed lines + brief text)
- Add map legend with real symbol examples

Implements 7 UX improvements from Phase C review.
All 300+ tests passing."
git push origin master
```

**Report completion with screenshots before proceeding to Package 3.**

---

# PACKAGE 3: POPUP DATA MODEL EXPANSION

**Priority:** HIGH — Comprehensive field coverage
**Time:** ~1-2 weeks / 12-16 hours
**Goal:** Expand from 12 fields → 25-35 fields per popup

---

## Fields to Add (15-20 total)

### Physical Structure (7 fields)
1. Pole class/strength
2. Material (expand current)
3. Condition (good/fair/poor/unsafe)
4. Lean direction
5. Lean severity
6. Defect type
7. Foundation type

### Electrical/Network (5 fields)
8. Voltage carried
9. Conductor type
10. Number of phases
11. Equipment presence
12. Equipment rating

### Mechanical (3 fields)
13. Stay present (yes/no)
14. Stay type
15. Stay direction/bearing

### Evidence (5 fields)
16. Surveyor/date
17. GNSS accuracy
18. Photo indicators
19. Source confidence
20. Action required

---

## Implementation

### Step 3.1: Expand Backend Data Model

**File:** `app/routes/map_preview.py`

**Find the function that builds `map_data.json` (likely `generate_map_data()` or similar).**

**Add new fields to feature properties:**

```python
def build_feature_properties(record):
    """Build comprehensive feature properties for map display."""

    props = {
        # Existing fields (keep these)
        'id': record.get('id'),
        'pole_id': record.get('pole_id'),
        'point_id': record.get('point_id'),
        'structure_type': record.get('structure_type'),
        'record_type': record.get('record_type'),
        'record_role': record.get('record_role'),
        'asset_intent': record.get('asset_intent'),
        'function': record.get('function'),
        'qa_status': record.get('qa_status', 'PASS'),
        'lifecycle_state': record.get('lifecycle_state'),
        'relationship': record.get('relationship'),

        # Coordinates
        'easting': record.get('easting'),
        'northing': record.get('northing'),
        'elevation': record.get('elevation'),

        # Basic existing fields
        'height': record.get('height'),
        'material': record.get('material'),
        'name': record.get('name'),
        'remarks': record.get('remarks'),

        # QA fields
        'issue_count': record.get('issue_count', 0),
        'warn_count': record.get('warn_count', 0),
        'issue_texts': record.get('issue_texts', []),
        'warn_texts': record.get('warn_texts', []),

        # === NEW PHYSICAL FIELDS ===
        'pole_class': record.get('pole_class'),
        'specification': record.get('specification'),
        'condition': record.get('condition'),
        'lean_direction': record.get('lean_direction'),
        'lean_severity': record.get('lean_severity'),
        'defect_type': record.get('defect_type'),
        'foundation_type': record.get('foundation_type'),

        # === NEW ELECTRICAL FIELDS ===
        'voltage': record.get('voltage') or infer_voltage_from_context(record),
        'conductor_type': record.get('conductor_type'),
        'phase_count': record.get('phase_count') or record.get('phases'),
        'equipment': parse_equipment_list(record.get('equipment')),
        'equipment_rating': record.get('equipment_rating'),

        # === NEW MECHANICAL FIELDS ===
        'stay_present': record.get('stay_present'),
        'stay_type': record.get('stay_type'),
        'stay_bearing': record.get('stay_bearing'),
        'stay_configuration': record.get('stay_configuration'),
        'stay_evidence_status': record.get('stay_evidence_status'),
        'stay_types': record.get('stay_types', []),
        'nearest_stay_distance_m': record.get('nearest_stay_distance_m'),
        'linked_pole_id': record.get('linked_pole_id'),
        'route_deviation_deg': record.get('route_deviation_deg'),
        'is_angle_pole': record.get('is_angle_pole', False),

        # === NEW EVIDENCE FIELDS ===
        'surveyor': record.get('surveyor'),
        'survey_date': record.get('survey_date'),
        'gnss_accuracy': record.get('gnss_accuracy'),
        'source_confidence': record.get('source_confidence'),
        'has_full_pole_photo': record.get('has_full_pole_photo', False),
        'has_pole_top_photo': record.get('has_pole_top_photo', False),
        'has_defect_photo': record.get('has_defect_photo', False),
        'photo_links': record.get('photo_links', []),

        # === NEW DESIGN/ACTION FIELDS ===
        'action_required': record.get('action_required'),
        'access_constraint': record.get('access_constraint'),
        'clearance_measured': record.get('clearance_measured'),
        'distance_from_route_m': record.get('distance_from_route_m'),

        # Lifecycle/replacement
        'replacing': record.get('replacing'),
        'being_replaced_by': record.get('being_replaced_by'),
        'match_offset_m': record.get('match_offset_m'),
    }

    return props


def infer_voltage_from_context(record):
    """Infer voltage from job context or other clues."""
    # Check job metadata for default voltage
    # Check structure_type for voltage indicators (e.g., "11kV", "33kV")
    # Return best guess or None
    return None


def parse_equipment_list(equipment_str):
    """Parse equipment string into list."""
    if not equipment_str:
        return []
    if isinstance(equipment_str, list):
        return equipment_str
    # Parse comma-separated string
    return [e.strip() for e in str(equipment_str).split(',') if e.strip()]
```

**Test:** Verify `map_data.json` now includes all new fields (even if mostly null)

---

### Step 3.2: Expand Frontend Popup Row Builders

**File:** `app/static/js/map-viewer.js`

**The code already has section builders. Expand them with new fields:**

**Verify/expand `physicalRows()`:**

```javascript
physicalRows(props) {
  return [
    // Height
    this.popupRow(
      'Measured Height',
      props.height ? `${props.height}m` : 'not captured',
      props.height ? 'ok' : 'review',
      !props.height && this.isExistingPole(props)
        ? 'Existing pole height should have been measured'
        : ''
    ),

    // NEW: Pole class
    this.popupRow(
      'Pole Class',
      props.pole_class || 'not captured',
      props.pole_class ? 'ok' : 'info'
    ),

    // Material / Condition combined
    this.popupRow(
      'Material / Condition',
      `${this.displayValue(props.material)} / ${this.displayValue(props.condition)}`,
      (props.material && props.condition) ? 'ok' : 'review',
      (!props.material || !props.condition) && this.isExistingPole(props)
        ? 'Material and condition should be recorded for existing poles'
        : ''
    ),

    // NEW: Lean
    this.popupRow(
      'Lean',
      (props.lean_severity || props.lean_direction)
        ? `${this.displayValue(props.lean_severity)} ${this.displayValue(props.lean_direction)}`.trim()
        : 'not captured',
      props.lean_severity === 'severe' ? 'warning' : 'info'
    ),

    // NEW: Defects
    this.popupRow(
      'Defects',
      props.defect_type || 'not captured',
      props.defect_type ? 'warning' : 'info'
    ),

    // NEW: Foundation
    this.popupRow(
      'Foundation',
      props.foundation_type || 'not captured',
      props.foundation_type ? 'ok' : 'info'
    ),
  ];
}
```

**Verify/expand `electricalRows()`:**

```javascript
electricalRows(props) {
  const equipment = Array.isArray(props.equipment) && props.equipment.length > 0
    ? props.equipment.join(', ')
    : props.equipment;

  return [
    // NEW: Voltage
    this.popupRow(
      'Line Voltage',
      props.voltage || 'not recorded',
      props.voltage ? 'ok' : 'info'
    ),

    // NEW: Conductor
    this.popupRow(
      'Conductor Type',
      props.conductor_type || 'not recorded',
      props.conductor_type ? 'ok' : 'info'
    ),

    // NEW: Phases
    this.popupRow(
      'Phases',
      props.phase_count || 'not recorded',
      props.phase_count ? 'ok' : 'info'
    ),

    // NEW: Equipment
    this.popupRow(
      'Mounted Equipment',
      equipment || 'none recorded',
      equipment ? 'ok' : 'info',
      equipment ? '⚡' : ''
    ),

    // NEW: Equipment rating
    this.popupRow(
      'Equipment Rating',
      props.equipment_rating || 'not recorded',
      props.equipment_rating ? 'ok' : 'info'
    ),
  ];
}
```

**Verify/expand `mechanicalRows()`:**

```javascript
mechanicalRows(props, prominent = false) {
  const stayStatus = props.stay_evidence_status;
  const stayTypes = Array.isArray(props.stay_types) && props.stay_types.length > 0
    ? props.stay_types.join(', ')
    : null;

  return [
    // Stay evidence
    this.popupRow(
      'Stay Evidence',
      stayStatus === 'captured' ? `✓ ${stayTypes || 'stay record'}` : 'not captured',
      stayStatus === 'captured' ? 'ok' : (prominent ? 'warning' : 'info'),
      stayStatus === 'captured'
        ? this.nearestStayDetail(props)
        : (prominent
            ? 'Angle pole — stay evidence not captured. Check field notes, photos or plan evidence.'
            : 'No stay evidence in digital file')
    ),

    // NEW: Stay type (if present)
    this.popupRow(
      'Stay Type',
      stayTypes || 'not captured',
      stayTypes ? 'ok' : 'info'
    ),

    // NEW: Stay bearing
    this.popupRow(
      'Stay Bearing',
      props.stay_bearing || 'not captured',
      props.stay_bearing ? 'ok' : 'info'
    ),

    // NEW: Anchor details
    this.popupRow(
      'Anchor Details',
      props.anchor_details || 'not linked',
      props.anchor_details ? 'ok' : 'info'
    ),

    // Route deviation
    this.popupRow(
      'Route Deviation',
      props.route_deviation_deg ? `${props.route_deviation_deg}°` : 'not calculated',
      props.route_deviation_deg > 30 ? 'warning' : 'info'
    ),

    // Action (if prominent)
    prominent ? this.popupRow(
      'Action',
      'Verify stay configuration before design',
      'warning'
    ) : null,
  ].filter(Boolean);
}
```

**Verify/expand `evidenceRows()`:**

```javascript
evidenceRows(props) {
  const photos = this.photoEvidenceText(props);

  return [
    // NEW: Surveyor
    this.popupRow(
      'Surveyed By',
      props.surveyor || 'not captured',
      props.surveyor ? 'ok' : 'info'
    ),

    // NEW: Survey date
    this.popupRow(
      'Survey Date',
      props.survey_date || 'not captured',
      props.survey_date ? 'ok' : 'info'
    ),

    // NEW: GNSS accuracy
    this.popupRow(
      'GNSS Accuracy',
      props.gnss_accuracy || 'not captured',
      props.gnss_accuracy && props.gnss_accuracy.includes('RTK') ? 'ok' : 'info'
    ),

    // NEW: Photo evidence
    this.popupRow(
      'Photo Evidence',
      photos,
      photos === 'no linked photos' ? 'info' : 'ok',
      photos !== 'no linked photos' ? '📷' : ''
    ),

    // NEW: Source confidence
    this.popupRow(
      'Source Confidence',
      props.source_confidence || 'raw survey export',
      'info'
    ),

    // Remarks
    this.popupRow(
      'Remarks',
      (props.name && props.name !== props.id && props.name !== props.pole_id)
        ? props.name
        : 'not captured',
      (props.name && props.name !== props.id) ? 'ok' : 'info'
    ),
  ];
}

photoEvidenceText(props) {
  const photos = [];
  if (props.has_full_pole_photo) photos.push('full pole');
  if (props.has_pole_top_photo) photos.push('pole top');
  if (props.has_defect_photo) photos.push('defect');
  if (Array.isArray(props.photo_links) && props.photo_links.length > 0) {
    photos.push(`${props.photo_links.length} linked ref${props.photo_links.length === 1 ? '' : 's'}`);
  }
  return photos.length > 0 ? photos.join(', ') : 'no linked photos';
}
```

---

### Step 3.3: Asset-Specific Popup Layouts

**Verify popup builders call correct sections for each asset type:**

**Existing pole popup:**

```javascript
buildExistingPolePopup(props, lat, lon) {
  return `
    <div class="pole-popup">
      ${this.popupSection('Identity', this.identityRows(props, lat, lon))}
      ${this.popupSection('Physical', this.physicalRows(props))}
      ${this.popupSection('Electrical', this.electricalRows(props))}
      ${this.popupSection('Mechanical', this.mechanicalRows(props, this.isAnglePole(props)))}
      ${this.popupSection('Location', this.locationRows(props, lat, lon))}
      ${this.popupSection('Evidence', this.evidenceRows(props))}
      ${this.popupSection('Lifecycle / Design', this.lifecycleRows(props))}
      ${this.popupSection('QA / Review', this.qaRows(props))}
    </div>
  `;
}
```

**Proposed pole popup (design-focused):**

```javascript
buildProposedPolePopup(props, lat, lon) {
  return `
    <div class="pole-popup">
      ${this.popupSection('Identity', this.identityRows(props, lat, lon))}
      ${this.popupSection('Specification', this.specificationRows(props))}
      ${this.popupSection('Design Requirements', this.designRequirementRows(props))}
      ${this.popupSection('Location', this.locationRows(props, lat, lon))}
      ${this.popupSection('Lifecycle / Design', this.lifecycleRows(props))}
      ${this.popupSection('QA / Review', this.qaRows(props))}
    </div>
  `;
}
```

**Angle pole popup (mechanical-focused):**

```javascript
buildAnglePolePopup(props, lat, lon) {
  // Angle poles show mechanical section FIRST (most important)
  return `
    <div class="pole-popup">
      ${this.popupSection('Identity', this.identityRows(props, lat, lon))}
      ${this.popupSection('Mechanical', this.mechanicalRows(props, true))}  <!-- prominent=true -->
      ${this.popupSection('Physical', this.physicalRows(props))}
      ${this.popupSection('Electrical', this.electricalRows(props))}
      ${this.popupSection('Location', this.locationRows(props, lat, lon))}
      ${this.popupSection('Evidence', this.evidenceRows(props))}
      ${this.popupSection('Lifecycle / Design', this.lifecycleRows(props))}
      ${this.popupSection('QA / Review', this.qaRows(props))}
    </div>
  `;
}
```

**Stay/anchor popup:**

```javascript
buildStayPopup(props, lat, lon) {
  return `
    <div class="pole-popup">
      ${this.popupSection('Identity', this.identityRows(props, lat, lon))}
      ${this.popupSection('Stay Details', this.stayDetailRows(props))}
      ${this.popupSection('Location', this.locationRows(props, lat, lon))}
      ${this.popupSection('Evidence', this.evidenceRows(props))}
    </div>
  `;
}
```

**Context/crossing popup:**

```javascript
buildContextPopup(props, lat, lon) {
  return `
    <div class="pole-popup">
      ${this.popupSection('Identity', this.identityRows(props, lat, lon))}
      ${this.popupSection('Crossing Details', this.crossingRows(props))}
      ${this.popupSection('Location', this.locationRows(props, lat, lon))}
    </div>
  `;
}
```

**Wire up asset-specific builders:**

```javascript
buildPopupContent(props, lat, lon) {
  // Determine asset type and call appropriate builder
  if (this.isAnglePole(props)) {
    return this.buildAnglePolePopup(props, lat, lon);
  } else if (this.isExistingPole(props)) {
    return this.buildExistingPolePopup(props, lat, lon);
  } else if (this.isProposedPole(props)) {
    return this.buildProposedPolePopup(props, lat, lon);
  } else if (this.isStay(props)) {
    return this.buildStayPopup(props, lat, lon);
  } else if (this.isContextRecord(props)) {
    return this.buildContextPopup(props, lat, lon);
  } else {
    // Generic fallback
    return this.buildExistingPolePopup(props, lat, lon);
  }
}
```

---

### Step 3.4: Test Popup Data Model Expansion

**After implementing all field additions:**

1. Load Gordon or Bellsprings job
2. Click existing pole → verify:
   - ✅ 8 sections visible
   - ✅ Physical section shows: height, pole class, material/condition, lean, defects, foundation
   - ✅ Electrical section shows: voltage, conductor, phases, equipment
   - ✅ Mechanical section shows: stay evidence, stay type, bearing
   - ✅ Evidence section shows: surveyor, date, GNSS, photos
   - ✅ "not captured" fields show appropriate status colors
3. Click proposed pole → verify design-focused layout
4. Click angle pole → verify mechanical section first
5. Click stay → verify stay details
6. Click context record → verify crossing details
7. Run `pytest -v` — all tests must pass

---

### Step 3.5: Commit Package 3

```bash
git add app/routes/map_preview.py app/static/js/map-viewer.js
git commit -m "Package 3: Popup data model expansion

Backend (map_preview.py):
- Add 20 new fields to map_data.json properties
- Physical: pole_class, condition, lean, defects, foundation
- Electrical: voltage, conductor, phases, equipment, rating
- Mechanical: stay details, bearing, configuration
- Evidence: surveyor, date, GNSS, photos, confidence

Frontend (map-viewer.js):
- Expand physicalRows() with 6 new fields
- Expand electricalRows() with 5 new fields
- Expand mechanicalRows() with 4 new fields
- Expand evidenceRows() with 6 new fields
- Asset-specific popup layouts (existing/proposed/angle/stay/context)

Popup field count: 12 → 25-35 fields (professional survey display)
All 300+ tests passing."
git push origin master
```

**Report completion with screenshots before proceeding to Package 4.**

---

# PACKAGE 4: ASSET-SPECIFIC LAYOUTS

**Status:** INCLUDED IN PACKAGE 3
**No separate implementation needed** — Package 3 already implements 5 asset-specific layouts

---

# PACKAGE 5: FIELD MAPS PARITY CHECK (OPTIONAL)

**Priority:** OPTIONAL — Validation step
**Time:** 4-6 hours
**Goal:** Confirm GridFlow displays all Field Maps fields

---

## Implementation

### Step 5.1: Compare to NIE MV_Poles Schema

**Reference:** NIE Field Maps MV_Poles layer (19 fields)

**Field Maps fields:**
1. OBJECTID ✅ (GridFlow: point_id)
2. Pole number ✅ (GridFlow: pole_id)
3. Status (E/P/R) ✅ (GridFlow: asset_intent, lifecycle_state)
4. Material ✅ (GridFlow: material)
5. Pole type ✅ (GridFlow: structure_type)
6. Condition ✅ (GridFlow: condition) — **ADDED IN PACKAGE 3**
7. Grade/class ✅ (GridFlow: pole_class) — **ADDED IN PACKAGE 3**
8. Height ✅ (GridFlow: height)
9. Year installed ❓ (GridFlow: not captured — add if available)
10. Comments/remarks ✅ (GridFlow: remarks, name)
11. Coordinates ✅ (GridFlow: easting, northing, lat, lon)
12. Survey date ✅ (GridFlow: survey_date) — **ADDED IN PACKAGE 3**
13. Surveyor ✅ (GridFlow: surveyor) — **ADDED IN PACKAGE 3**
14. Voltage ✅ (GridFlow: voltage) — **ADDED IN PACKAGE 3**
15. Circuit ID ❓ (GridFlow: not captured — add if available)
16. Equipment ✅ (GridFlow: equipment) — **ADDED IN PACKAGE 3**
17. Photos ✅ (GridFlow: photo indicators) — **ADDED IN PACKAGE 3**
18. Related records ✅ (GridFlow: lifecycle links, stay links)
19. GNSS accuracy ✅ (GridFlow: gnss_accuracy) — **ADDED IN PACKAGE 3**

**Result:** GridFlow displays 17/19 Field Maps fields. Missing:
- Year installed (add if CSV contains this)
- Circuit ID (add if job metadata contains this)

---

### Step 5.2: Add Missing Fields (If Available)

**If CSVs contain year_installed or circuit_id:**

**Backend (`app/routes/map_preview.py`):**
```python
props['year_installed'] = record.get('year_installed')
props['circuit_id'] = record.get('circuit_id') or job_metadata.get('circuit_id')
```

**Frontend (`app/static/js/map-viewer.js`):**
```javascript
// Add to identityRows():
this.popupRow(
  'Year Installed',
  props.year_installed || 'not captured',
  props.year_installed ? 'ok' : 'info'
),

this.popupRow(
  'Circuit ID',
  props.circuit_id || 'not captured',
  props.circuit_id ? 'ok' : 'info'
),
```

---

### Step 5.3: Document Field Maps Parity

**Create:** `FIELD_MAPS_PARITY_REPORT.md`

```markdown
# Field Maps Display Parity Report

**Date:** 2026-05-01
**Reference:** NIE MV_Poles Field Maps layer (19 fields)

## Parity Status

**GridFlow displays:** 17/19 Field Maps fields (89% parity)

**Covered fields (17):**
✅ OBJECTID / Pole number / Status
✅ Material / Pole type / Condition / Grade
✅ Height / Comments / Coordinates
✅ Survey date / Surveyor / GNSS accuracy
✅ Voltage / Equipment / Photos
✅ Related records (lifecycle links)

**Missing fields (2):**
❌ Year installed — not in current CSVs
❌ Circuit ID — not in current CSVs

**Conclusion:** GridFlow achieves Field Maps display parity for all fields available in current survey data format.
```

---

### Step 5.4: Commit Package 5 (If Implemented)

```bash
git add app/routes/map_preview.py app/static/js/map-viewer.js FIELD_MAPS_PARITY_REPORT.md
git commit -m "Package 5: Field Maps parity check

- Verify 17/19 NIE MV_Poles fields displayed
- Add year_installed and circuit_id (if available in CSVs)
- Document parity status in FIELD_MAPS_PARITY_REPORT.md

GridFlow achieves 89% Field Maps display parity.
All 300+ tests passing."
git push origin master
```

---

# FINAL VALIDATION & COMPLETION

**After all packages complete:**

---

## Validation Steps

### 1. Load Real Jobs

Test on 4 real jobs:
- **Gordon** (NIE, raw controller + manual PR split)
- **Bellsprings** (SPEN, real design package)
- **P010** (operational job)
- **P011** (operational feedback source)

### 2. Verify Each Package

**Package 1 (Popup CSS):**
- ✅ No overflow
- ✅ Vertical scroll works
- ✅ Section titles clear
- ✅ Status colors visible

**Package 2 (Map UX):**
- ✅ Markers 30-40% smaller
- ✅ Panel split clear
- ✅ EX square, PR circle
- ✅ Angle overlay badge
- ✅ Context muted
- ✅ Map key accurate

**Package 3 (Popup Data):**
- ✅ 25-35 fields per popup
- ✅ Asset-specific layouts
- ✅ Physical section complete
- ✅ Electrical section complete
- ✅ Mechanical section complete
- ✅ Evidence section complete

**Package 5 (Field Maps Parity):**
- ✅ 17/19 fields covered

### 3. Run Full Test Suite

```bash
pytest -v
```

**All 300+ tests must pass.**

### 4. Take Screenshots

**Required screenshots:**
- Map view (markers, layers, legend)
- Existing pole popup (all 8 sections)
- Proposed pole popup (design-focused)
- Angle pole popup (mechanical first)
- Stay popup (stay details)
- Context popup (crossing details)
- Right panel (Map Layers + Review Filters)

### 5. Document Completion

**Update files:**
- `AI_CONTROL/01_CURRENT_STATE.md`
- `AI_CONTROL/02_CURRENT_TASK.md`
- `CHANGELOG.md`

---

## Final Commit

```bash
git add .
git commit -m "Phase C2/D complete: Professional survey-display platform

DELIVERABLES:
✅ Package 1: Emergency popup CSS fix (2-4 hours)
✅ Package 2: Map UX improvements (1 week)
✅ Package 3: Popup data model expansion (1-2 weeks)
✅ Package 4: Asset-specific layouts (included in P3)
✅ Package 5: Field Maps parity check (optional)

RESULTS:
- Popup overflow fixed (500px width, vertical scroll)
- Map UX professional (7 improvements implemented)
- Popup fields expanded 12 → 25-35 per asset type
- Asset-specific layouts (existing/proposed/angle/stay/context)
- Field Maps parity 17/19 fields (89%)

VALIDATION:
- Tested on Gordon, Bellsprings, P010, P011
- All 300+ tests passing
- Screenshots confirm professional quality

Phase C2/D timeline: 2-4 weeks
Ready for operational validation and designer feedback."
git push origin master
```

---

# SUCCESS CRITERIA

**Phase C2/D is complete when:**

✅ **All 5 packages implemented**
✅ **All 300+ tests passing**
✅ **Validated on 4 real jobs** (Gordon, Bellsprings, P010, P011)
✅ **Screenshots confirm quality**
✅ **Control docs updated**
✅ **Committed and pushed to GitHub**

**Result:** GridFlow is now a **professional survey-display platform** with **narrow QA focus**, ready for operational use and designer validation.

---

# WHAT HAPPENS NEXT

**After Phase C2/D validates:**

### Option A: Operational Use & Adoption
- Deploy to real projects
- Collect designer feedback
- Iterate based on real use
- Document best practices

### Option B: Stage 4 Planning
- Structured field capture (tablets, iPads)
- Photo evidence integration
- Offline workflows
- GIS integration
- 6-12 month roadmap

### Option C: More Refinement
- Additional polish based on validation
- Performance optimization
- UI/UX tweaks
- Documentation

**Decision point:** After operational validation proves value

---

**END OF SPECIFICATION**

---

# CURSOR START COMMAND

**Copy this to Cursor when ready to begin:**

```
Phase C2/D is approved for immediate execution.

Read: /Users/noelcollins/Unitas-GridFlow/CURSOR_PHASE_C2D_COMPLETE_IMPLEMENTATION.md

Execute packages in order:
1. Package 1: Emergency Popup CSS Fix (2-4 hours)
2. Package 2: Map UX Improvements (1 week)
3. Package 3: Popup Data Model Expansion (1-2 weeks)
4. Package 4: Asset-Specific Layouts (included in P3)
5. Package 5: Field Maps Parity (optional)

Requirements:
- Test after EACH package
- All 300+ tests must stay green
- Report completion with screenshots after each package
- Do NOT proceed to next package without approval

Timeline: 2-4 weeks total
Goal: Transform GridFlow to professional survey-display platform

Start with Package 1 immediately.
```
