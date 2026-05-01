# EMERGENCY POPUP FIX — 2026-05-01

**Status:** CRITICAL - Popup HTML overflowing, layout broken
**Evidence:** User screenshots showing text overflow, broken sections
**Root Cause:** Leaflet popup container not sized for expanded field count

---

## CRITICAL PROBLEMS IDENTIFIED

### 1. Popup Container Too Small
**Symptom:** Text overflowing outside popup boundary (visible in screenshots)
**Cause:** Leaflet default popup max-width (~300px) + Phase C2-2 added 15+ fields
**Fix:** Increase popup max-width to 450-500px and enable vertical scroll

### 2. Popup Sections Not Styled
**Symptom:** No visual separation between sections
**Cause:** `.popup-section` and `.popup-field` classes exist in JS but not CSS
**Fix:** Add proper CSS styling for sections, fields, and status indicators

### 3. Field Status Indicators Missing
**Symptom:** "not captured" / "review required" text not visually distinguished
**Cause:** `.status-review`, `.status-warning`, `.status-ok` classes not styled
**Fix:** Add colored backgrounds/borders for status types

### 4. No Scrolling in Popup
**Symptom:** Long popups push off screen
**Cause:** No max-height set on popup content
**Fix:** Add max-height + overflow-y: auto to `.leaflet-popup-content`

---

## IMMEDIATE FIX SPECIFICATION

### Fix 1: Leaflet Popup Container Sizing

**File:** `app/templates/map_viewer.html` (or wherever map is initialized)

**Add this CSS in a `<style>` block or in `app/static/style.css`:**

```css
/* === POPUP CONTAINER SIZING === */

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

### Fix 2: Popup Section and Field Styling

**Add to CSS:**

```css
/* === POPUP SECTIONS === */

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

/* === POPUP FIELDS === */

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

/* === FIELD STATUS STYLING === */

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

/* === RESPONSIVE === */

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

### Fix 3: Ensure Popup HTML Structure Correct

**Verify in `app/static/js/map-viewer.js`:**

The `buildExistingPolePopup()` function should output this structure:

```javascript
buildExistingPolePopup(props, lat, lon) {
  return `
    <div class="pole-popup">
      ${this.popupSection('Identity', this.identityRows(props, lat, lon))}
      ${this.popupSection('Physical', this.physicalRows(props))}
      ${this.popupSection('Electrical', this.electricalRows(props))}
      ${this.popupSection('Mechanical', this.mechanicalRows(props))}
      ${this.popupSection('Location', this.locationRows(props, lat, lon))}
      ${this.popupSection('Evidence', this.evidenceRows(props))}
      ${this.popupSection('Lifecycle / Design', this.lifecycleRows(props))}
      ${this.popupSection('QA / Review', this.qaRows(props))}
    </div>
  `;
}
```

**Check that `popupSection()` and `popupRow()` are correct:**

```javascript
popupSection(title, rows) {
  const renderedRows = rows.filter(Boolean).map(row => row).join('');
  return `
    <div class="popup-section">
      <div class="popup-section-title">${this.escapeHtml(title)}</div>
      ${renderedRows}
    </div>
  `;
}

popupRow(label, value, status = 'info', detail = '') {
  const display = this.displayValue(value);
  const detailHtml = detail ? `<div class="popup-field-detail">${this.escapeHtml(detail)}</div>` : '';
  return `
    <div class="popup-field status-${this.escapeHtml(status)}">
      <div class="popup-field-label">${this.escapeHtml(label)}</div>
      <div class="popup-field-value">${this.escapeHtml(display)}</div>
      ${detailHtml}
    </div>
  `;
}
```

---

### Fix 4: Test Popup Sizing

**After applying CSS, test on Gordon or Bellsprings:**

1. Click existing pole → popup should:
   - ✅ Be wide enough (450-500px)
   - ✅ Show all sections without overflow
   - ✅ Scroll vertically if content exceeds 70vh
   - ✅ Have clear section titles (bold, blue underline)
   - ✅ Show colored status backgrounds (green/blue/amber/red)

2. Click proposed pole → popup should show different sections

3. Click context record → popup should be narrower (fewer sections)

---

## IMPLEMENTATION STEPS

1. **Add CSS to `app/static/style.css` or create `app/static/css/map-viewer.css`**
   - All CSS from Fix 1 and Fix 2 above
   - Link new CSS file in `app/templates/map_viewer.html` if created

2. **Verify `map-viewer.js` popup functions correct**
   - `buildExistingPolePopup()` calls `popupSection()` for each section
   - `popupSection()` outputs correct HTML structure
   - `popupRow()` includes `status-${status}` class

3. **Test on real job**
   - Load Gordon or Bellsprings
   - Click 5+ different poles
   - Verify no overflow, proper scrolling, clear visual hierarchy

4. **Run tests**
   - `pytest -v` — all 300+ tests must pass

5. **Commit**
   ```
   Emergency fix: Popup container sizing and styling

   - Increase popup max-width to 500px
   - Add vertical scroll for long popups
   - Style .popup-section and .popup-field classes
   - Add color-coded status backgrounds
   - Fix text overflow visible in screenshots
   ```

---

## FILES TO MODIFY

**CSS file (choose one):**
- Option A: Add to `app/static/style.css` (simplest)
- Option B: Create `app/static/css/map-viewer.css` and link in template

**Verify/Fix:**
- `app/static/js/map-viewer.js` — Check popup HTML structure correct
- `app/templates/map_viewer.html` — Link CSS file if created separately

**Do NOT modify:**
- Backend files (`app/routes/map_preview.py`, `app/qa_engine.py`) — data model is correct
- Frontend filters/layers — those work, problem is just popup styling

---

## ACCEPTANCE CRITERIA

✅ Popup does not overflow container
✅ Popup scrolls vertically when content exceeds viewport
✅ Section titles visually distinct (bold, blue underline)
✅ Fields have colored status backgrounds
✅ "not captured" fields show amber/info styling
✅ "review required" fields show orange/warning styling
✅ "design blocker" fields show red/fail styling
✅ Mobile responsive (popup fits on mobile screens)
✅ All 300+ tests still passing

---

## NEXT AFTER THIS FIX

Once popup container is fixed and styled properly:
- Continue with Phase C2-2 data model expansion (add remaining 10-15 fields)
- Then proceed to Phase C2-3 (Field Maps parity check)

But **DO NOT** add more fields until popup container is fixed — it will just make overflow worse.

---

**END OF EMERGENCY FIX**
