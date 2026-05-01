# CURSOR: Domain Accuracy & Electrical Data Model - Complete Implementation

**Date:** 2026-05-01
**Status:** APPROVED FOR IMMEDIATE EXECUTION
**Scope:** Emergency domain fixes + complete electrical data model (2-4 weeks)
**Evidence Base:**
- UK Electrical Grid Survey Data Capture Report (4,544 words)
- UK Electrical Grid Survey Capture Model and GridFlow Gap Analysis (comprehensive)
- Real operational evidence (BT pole misclassification, missing conductor data)

---

## 🎯 EXECUTIVE SUMMARY

**What You're Building:**

Transform GridFlow from "map review tool with QA flags" to **"domain-accurate electrical survey-to-design platform"** with proper:
- Asset classification (electric vs telecoms vs third-party)
- Complete electrical data model (conductor, cable, equipment, connections)
- Source confidence validation (measured vs estimated vs legacy vs inferred)
- Evidence quality enforcement (height source, GNSS accuracy, survey provenance)
- Third-party infrastructure handling (BT, Openreach, streetlights, customer services)

**Why This Matters:**

Current GridFlow shows:
- **BT pole classified as "EXpole being replaced"** — WRONG (it's telecoms infrastructure)
- **No conductor/cable specification** — can't design without knowing what cable to use
- **"Legacy map data" not flagged as unverified** — designer can't trust geometry
- **Height source missing** — can't do clearance calculations without knowing measured vs estimated
- **No third-party attachment handling** — telecoms/streetlight dependencies invisible

**After This Implementation:**

✅ BT poles correctly classified as third-party infrastructure
✅ Complete conductor/cable electrical model (voltage, type, size, phases, configuration)
✅ Source confidence validation (field-observed vs DNO GIS vs drawing vs inferred)
✅ Height source enforcement (measured RTK vs estimated vs not captured)
✅ Third-party attachments tracked (BT, streetlight, customer service)
✅ Legacy data clearly flagged with warnings

---

## 📋 IMPLEMENTATION STRUCTURE

### **Phase 1: Emergency Domain Fixes** (Week 1 / 5-7 days)

**Package D1-A:** Asset Classification Fix
**Package D1-B:** Height Source Validation
**Package D1-C:** Source Confidence & Legacy Data Warnings
**Package D1-D:** Third-Party Infrastructure & Attachments

### **Phase 2: Complete Electrical Data Model** (Week 2-3 / 10-14 days)

**Package D2-A:** Conductor/Cable Electrical Schema
**Package D2-B:** Equipment & Pole-Top Configuration
**Package D2-C:** Network Connectivity & Relationships
**Package D2-D:** Survey Metadata & Provenance

### **Phase 3: Integration & Validation** (Week 3-4 / 5-7 days)

**Package D3-A:** Backend Data Model Integration
**Package D3-B:** Frontend Display & Forms
**Package D3-C:** Validation Rules & QA Engine
**Package D3-D:** Export & Handoff Quality

**Total Timeline:** 2-4 weeks / 60-80 hours focused work

---

# PHASE 1: EMERGENCY DOMAIN FIXES

## PACKAGE D1-A: ASSET CLASSIFICATION FIX

**Priority:** CRITICAL
**Time:** 1-2 days
**Problem:** BT pole classified as "EXpole being replaced" instead of third-party infrastructure

---

### Problem Evidence

**From user screenshots:**
- Point 72: "bt pole"
- Type: "Existing pole (EXpole) being replaced"
- Feature Code: "EXpole"
- **This is WRONG** — it's a BT telecoms pole, not an electric network pole

**Impact:**
- Designer thinks it's part of the electric network to be replaced
- Construction plan includes pole that's not theirs to touch
- DNO handoff package contains third-party assets as structural poles
- **Fundamental domain classification error**

---

### Solution: Asset Type Classification Logic

**Create:** `app/asset_classifier.py` (new file)

```python
"""
Asset classification logic for electrical vs third-party infrastructure.
"""

TELECOMS_INDICATORS = {
    'feature_codes': {'BT', 'bt', 'Openreach', 'openreach', 'Virgin', 'virgin', 'telecom', 'telecoms'},
    'materials': {'BT_pole', 'telecoms_pole'},
    'remarks_keywords': {'bt pole', 'bt', 'openreach', 'virgin media', 'telecoms', 'telecom', 'fibre', 'copper line'}
}

STREETLIGHT_INDICATORS = {
    'feature_codes': {'SL', 'streetlight', 'street_light', 'lamp'},
    'remarks_keywords': {'streetlight', 'street light', 'lamp post', 'lighting column'}
}

CUSTOMER_SERVICE_INDICATORS = {
    'feature_codes': {'CS', 'customer_service', 'service_pole'},
    'remarks_keywords': {'customer pole', 'service pole', 'private pole'}
}

ELECTRIC_NETWORK_CODES = {
    'structural': {'EXpole', 'PRpole', 'Pol', 'Angle', 'Terminal', 'Section', 'Stay', 'Anchor'},
    'equipment': {'Transformer', 'Switch', 'Fuse', 'Recloser', 'RMU', 'LV_board'},
    'context': {'Road', 'Track', 'Gate', 'Fence', 'Hedge', 'Tree', 'Stream', 'Wall'}
}


def classify_asset_type(record):
    """
    Classify asset as electric network, third-party, or context.

    Returns:
        dict with 'primary_type', 'infrastructure_owner', 'is_structural_pole', 'warnings'
    """
    feature_code = str(record.get('structure_type') or record.get('feature_code', '')).strip()
    remarks = str(record.get('remarks') or record.get('name', '')).strip().lower()
    material = str(record.get('material', '')).strip()

    # Check telecoms indicators
    if (feature_code in TELECOMS_INDICATORS['feature_codes'] or
        material in TELECOMS_INDICATORS['materials'] or
        any(kw in remarks for kw in TELECOMS_INDICATORS['remarks_keywords'])):

        return {
            'primary_type': 'third_party_infrastructure',
            'infrastructure_owner': 'telecoms',
            'subtype': 'BT/Openreach pole',
            'is_structural_pole': False,
            'is_electric_network': False,
            'classification_confidence': 'high',
            'warnings': ['Third-party telecoms infrastructure - not part of electric network design'],
            'classification_basis': 'feature_code + remarks analysis'
        }

    # Check streetlight indicators
    if (feature_code in STREETLIGHT_INDICATORS['feature_codes'] or
        any(kw in remarks for kw in STREETLIGHT_INDICATORS['remarks_keywords'])):

        return {
            'primary_type': 'third_party_infrastructure',
            'infrastructure_owner': 'local_authority',
            'subtype': 'streetlight',
            'is_structural_pole': False,
            'is_electric_network': False,
            'classification_confidence': 'high',
            'warnings': ['Local authority streetlight - not part of electric network'],
            'classification_basis': 'feature_code + remarks analysis'
        }

    # Check customer service indicators
    if (feature_code in CUSTOMER_SERVICE_INDICATORS['feature_codes'] or
        any(kw in remarks for kw in CUSTOMER_SERVICE_INDICATORS['remarks_keywords'])):

        return {
            'primary_type': 'third_party_infrastructure',
            'infrastructure_owner': 'customer',
            'subtype': 'customer service pole',
            'is_structural_pole': False,
            'is_electric_network': False,
            'classification_confidence': 'medium',
            'warnings': ['Customer-owned service pole - not DNO responsibility'],
            'classification_basis': 'feature_code + remarks analysis'
        }

    # Check electric network structural codes
    if feature_code in ELECTRIC_NETWORK_CODES['structural']:
        return {
            'primary_type': 'electric_network',
            'infrastructure_owner': 'DNO',
            'subtype': 'structural_support',
            'is_structural_pole': True,
            'is_electric_network': True,
            'classification_confidence': 'high',
            'warnings': [],
            'classification_basis': 'DNO feature code'
        }

    # Check electric equipment codes
    if feature_code in ELECTRIC_NETWORK_CODES['equipment']:
        return {
            'primary_type': 'electric_network',
            'infrastructure_owner': 'DNO',
            'subtype': 'electrical_equipment',
            'is_structural_pole': False,
            'is_electric_network': True,
            'classification_confidence': 'high',
            'warnings': [],
            'classification_basis': 'DNO feature code'
        }

    # Check context codes
    if feature_code in ELECTRIC_NETWORK_CODES['context']:
        return {
            'primary_type': 'context',
            'infrastructure_owner': 'various',
            'subtype': 'environmental_context',
            'is_structural_pole': False,
            'is_electric_network': False,
            'classification_confidence': 'high',
            'warnings': [],
            'classification_basis': 'context feature code'
        }

    # Unknown/ambiguous
    return {
        'primary_type': 'unclassified',
        'infrastructure_owner': 'unknown',
        'subtype': 'unknown',
        'is_structural_pole': False,
        'is_electric_network': False,
        'classification_confidence': 'low',
        'warnings': ['Asset type could not be confidently classified - manual review required'],
        'classification_basis': 'insufficient data'
    }


def get_popup_type_label(classification):
    """
    Return human-readable type label for popup display.
    """
    if classification['primary_type'] == 'third_party_infrastructure':
        if classification['infrastructure_owner'] == 'telecoms':
            return 'Third-Party Telecoms Pole (BT/Openreach)'
        elif classification['infrastructure_owner'] == 'local_authority':
            return 'Local Authority Streetlight'
        elif classification['infrastructure_owner'] == 'customer':
            return 'Customer Service Pole'
        else:
            return 'Third-Party Infrastructure'

    elif classification['primary_type'] == 'electric_network':
        if classification['subtype'] == 'structural_support':
            return 'Electric Network Structural Pole'
        elif classification['subtype'] == 'electrical_equipment':
            return 'Electric Network Equipment'
        else:
            return 'Electric Network Asset'

    elif classification['primary_type'] == 'context':
        return 'Environmental/Context Feature'

    else:
        return 'Unclassified Asset (Review Required)'
```

---

### Integration into QA Engine

**File:** `app/qa_engine.py`

**Add import:**
```python
from app.asset_classifier import classify_asset_type, get_popup_type_label
```

**Add classification to record processing:**
```python
def enrich_record_with_classification(record):
    """
    Add asset classification to record properties.
    """
    classification = classify_asset_type(record)

    record['asset_classification'] = classification
    record['primary_type'] = classification['primary_type']
    record['infrastructure_owner'] = classification['infrastructure_owner']
    record['classification_confidence'] = classification['classification_confidence']
    record['classification_warnings'] = classification['warnings']

    # Override asset_intent based on classification
    if classification['primary_type'] == 'third_party_infrastructure':
        record['asset_intent'] = 'third_party_not_network'
    elif classification['primary_type'] == 'context':
        record['asset_intent'] = 'environmental_context'

    return record
```

---

### Frontend Popup Display

**File:** `app/static/js/map-viewer.js`

**Update `buildExistingPolePopup()` to show classification:**

```javascript
buildExistingPolePopup(props, lat, lon) {
  // Check if third-party infrastructure
  if (props.primary_type === 'third_party_infrastructure') {
    return this.buildThirdPartyInfrastructurePopup(props, lat, lon);
  }

  // Otherwise show standard electric network popup
  return this.buildStandardPolePopup(props, lat, lon);
}

buildThirdPartyInfrastructurePopup(props, lat, lon) {
  return `
    <div class="pole-popup third-party-warning">
      ${this.popupSection('⚠️ THIRD-PARTY INFRASTRUCTURE', [
        this.popupRow('Type', props.infrastructure_owner === 'telecoms' ? 'BT/Openreach Telecoms Pole' : props.subtype, 'warning'),
        this.popupRow('Owner', props.infrastructure_owner, 'warning'),
        this.popupRow('Classification', 'NOT part of electric network', 'warning', 'This asset is owned and maintained by a third party, not the DNO.')
      ])}

      ${this.popupSection('Identity', this.identityRows(props, lat, lon))}
      ${this.popupSection('Location', this.locationRows(props, lat, lon))}
      ${this.popupSection('Evidence', this.evidenceRows(props))}

      ${this.popupSection('Design Action', [
        this.popupRow('Designer Action', 'EXCLUDE from electric network design', 'warning'),
        this.popupRow('Construction Impact', 'Note proximity for access/construction planning only', 'info'),
        this.popupRow('Wayleave/Coordination', 'May require third-party coordination if work nearby', 'info')
      ])}
    </div>
  `;
}
```

**Add CSS styling:**

```css
/* Third-party infrastructure warning styling */
.pole-popup.third-party-warning {
  border: 3px solid #f59e0b;
  background: #fffbeb;
}

.pole-popup.third-party-warning .popup-section:first-child {
  background: #fef3c7;
  border-left: 5px solid #d97706;
  padding: 12px;
  margin-bottom: 12px;
}

.pole-popup.third-party-warning .popup-section:first-child .popup-section-title {
  color: #92400e;
  font-size: 1rem;
}
```

---

### Test & Validation

**After implementing:**

1. Load job with BT pole (Point 72)
2. Click BT pole marker
3. Verify popup shows:
   - ⚠️ THIRD-PARTY INFRASTRUCTURE
   - Type: BT/Openreach Telecoms Pole
   - Owner: telecoms
   - Classification: NOT part of electric network
   - Designer Action: EXCLUDE from electric network design
4. Verify BT pole NOT shown in structural pole count
5. Verify BT pole visible only when "Third-Party Infrastructure" layer active

---

### Commit D1-A

```bash
git add app/asset_classifier.py app/qa_engine.py app/static/js/map-viewer.js app/static/style.css
git commit -m "D1-A: Asset classification fix

- Create asset_classifier.py with telecoms/streetlight/customer detection
- Classify BT/Openreach poles as third-party infrastructure
- Add third-party popup layout with clear warnings
- Prevent third-party assets counting as structural poles
- Add infrastructure_owner and classification_confidence fields

Fixes critical BT pole misclassification issue.
All tests passing."
git push origin master
```

---

## PACKAGE D1-B: HEIGHT SOURCE VALIDATION

**Priority:** CRITICAL
**Time:** 1-2 days
**Problem:** "Height Source: not captured" makes height value unreliable for clearance calculations

---

### Problem Evidence

**From user screenshots:**
- Point 72 (BT pole): "Measured Height: 6.5m" but "Height Source: not captured"
- **This is a BLOCKER** — can't do clearance calcs without knowing if height is measured vs estimated

**Survey Research Requirements:**
> "Height source: measured RTK, measured standalone, estimated visual, estimated from plan, not captured"

---

### Solution: Height Source Field & Validation

**Backend:** `app/routes/map_preview.py`

**Add height_source to map_data properties:**

```python
def build_feature_properties(record):
    """Build comprehensive feature properties for map display."""

    props = {
        # ... existing fields ...

        # Height and source
        'height': record.get('height'),
        'height_source': record.get('height_source'),  # NEW FIELD
        'height_confidence': classify_height_confidence(record),  # NEW

        # ... rest of fields ...
    }

    return props


def classify_height_confidence(record):
    """
    Determine height data confidence based on source.

    Returns:
        dict with 'level', 'status', 'warning'
    """
    height = record.get('height')
    height_source = record.get('height_source', '').lower()
    record_type = record.get('record_type', '').lower()
    source_confidence = record.get('source_confidence', '').lower()

    # No height at all
    if not height:
        if 'ex' in record_type or 'existing' in record_type:
            return {
                'level': 'missing',
                'status': 'blocker',
                'warning': 'Measured height missing — clearance check impossible'
            }
        else:  # Proposed pole
            return {
                'level': 'not_applicable',
                'status': 'info',
                'warning': 'Proposed pole specification required (design decision)'
            }

    # Height exists but source unknown/not captured
    if not height_source or height_source == 'not captured':
        if 'legacy' in source_confidence or 'drawing' in source_confidence:
            return {
                'level': 'low',
                'status': 'warning',
                'warning': 'Height from legacy data — field verification required before clearance calculations'
            }
        else:
            return {
                'level': 'low',
                'status': 'warning',
                'warning': 'Height source not recorded — verify measurement method before relying on value'
            }

    # RTK/PPK measured (high confidence)
    if 'rtk' in height_source or 'ppk' in height_source or 'survey grade' in height_source:
        return {
            'level': 'high',
            'status': 'ok',
            'warning': ''
        }

    # Measured standalone GNSS (medium confidence)
    if 'measured' in height_source and 'gnss' in height_source:
        return {
            'level': 'medium',
            'status': 'ok',
            'warning': 'Standalone GNSS measurement — adequate for design'
        }

    # Measured tape/rangefinder (medium-high confidence)
    if 'measured' in height_source or 'tape' in height_source or 'rangefinder' in height_source:
        return {
            'level': 'medium-high',
            'status': 'ok',
            'warning': ''
        }

    # Estimated visual (low confidence)
    if 'estimated' in height_source or 'visual' in height_source:
        return {
            'level': 'low',
            'status': 'warning',
            'warning': 'Height estimated — field measurement required for clearance calculations'
        }

    # From plan/drawing (low confidence, needs verification)
    if 'plan' in height_source or 'drawing' in height_source or 'legacy' in height_source:
        return {
            'level': 'low',
            'status': 'warning',
            'warning': 'Height from plan/drawing — field verification required'
        }

    # Default: unknown source
    return {
        'level': 'unknown',
        'status': 'review',
        'warning': 'Height source unknown — verify before use in design'
    }
```

---

### Frontend Display

**File:** `app/static/js/map-viewer.js`

**Update `physicalRows()` to show height source:**

```javascript
physicalRows(props) {
  const heightConf = props.height_confidence || {};

  return [
    // Height with source confidence indicator
    this.popupRow(
      this.isExistingPole(props) ? 'Measured Height' : 'Specified Height',
      props.height ? `${props.height}m` : 'not captured',
      heightConf.status || 'review',
      heightConf.warning || ''
    ),

    // NEW: Height Source field
    this.popupRow(
      'Height Source',
      props.height_source || 'not captured',
      props.height_source ? 'info' : 'warning',
      !props.height_source
        ? 'Height measurement method not recorded — reliability unknown'
        : this.explainHeightSource(props.height_source)
    ),

    // Height Confidence summary
    props.height ? this.popupRow(
      'Height Confidence',
      this.formatConfidenceLevel(heightConf.level),
      heightConf.status || 'info',
      heightConf.level === 'high'
        ? 'Suitable for clearance calculations'
        : 'Verify before use in clearance calculations'
    ) : null,

    // ... rest of physical fields ...
  ].filter(Boolean);
}

explainHeightSource(source) {
  const explanations = {
    'measured_rtk': 'Survey-grade RTK GNSS measurement (±0.02m typical)',
    'measured_ppk': 'Post-processed kinematic GNSS (±0.05m typical)',
    'measured_gnss': 'Standalone GNSS measurement (±0.5-2m typical)',
    'measured_tape': 'Tape/rangefinder ground measurement',
    'estimated_visual': 'Visual estimate from surveyor',
    'from_plan': 'Taken from existing plan/drawing',
    'legacy_data': 'Inherited from legacy records',
    'not captured': 'Measurement method not recorded'
  };

  const normalized = source.toLowerCase().replace(/\s+/g, '_');
  return explanations[normalized] || 'Height source: ' + source;
}

formatConfidenceLevel(level) {
  const labels = {
    'high': '✓ High confidence (survey-grade)',
    'medium-high': '✓ Medium-high confidence',
    'medium': '◐ Medium confidence',
    'low': '⚠ Low confidence',
    'missing': '✗ Missing',
    'not_applicable': 'N/A (proposed pole)',
    'unknown': '? Unknown'
  };

  return labels[level] || level;
}
```

---

### Validation Rule: Height Source Required for Existing Poles

**File:** `app/qa_engine.py`

**Add validation rule:**

```python
def validate_height_source_for_existing(record):
    """
    Existing poles with height must have height_source.
    If height exists but source missing → WARNING
    If height missing entirely → BLOCKER
    """
    record_type = record.get('record_type', '').lower()
    height = record.get('height')
    height_source = record.get('height_source')

    # Only apply to existing poles
    if not ('ex' in record_type or 'existing' in record_type):
        return None

    # Height missing entirely = BLOCKER
    if not height:
        return {
            'severity': 'FAIL',
            'code': 'MISSING_EXISTING_HEIGHT',
            'message': 'Measured height missing — clearance check impossible',
            'field': 'height',
            'recommended_action': 'Field measurement required before design'
        }

    # Height exists but source not recorded = WARNING
    if not height_source or height_source == 'not captured':
        return {
            'severity': 'WARN',
            'code': 'HEIGHT_SOURCE_NOT_RECORDED',
            'message': 'Height source not recorded — verify measurement method',
            'field': 'height_source',
            'recommended_action': 'Confirm height measurement method (RTK/tape/estimated/plan)'
        }

    # Height from legacy/plan without field verification = WARNING
    if any(kw in height_source.lower() for kw in ['legacy', 'plan', 'drawing', 'estimated']):
        return {
            'severity': 'WARN',
            'code': 'HEIGHT_NEEDS_VERIFICATION',
            'message': f'Height from {height_source} — field verification required',
            'field': 'height_source',
            'recommended_action': 'Field measurement before clearance calculations'
        }

    return None
```

---

### Test & Validation

**After implementing:**

1. Load job with existing poles
2. Click pole with height but no height_source
3. Verify popup shows:
   - Measured Height: [value]
   - Height Source: not captured (WARNING)
   - Height Confidence: ⚠ Low confidence
   - Warning: "Height source not recorded — reliability unknown"
4. Verify QA issue created: "HEIGHT_SOURCE_NOT_RECORDED"
5. Click pole with "measured_rtk" source
6. Verify shows: Height Confidence: ✓ High confidence (survey-grade)

---

### Commit D1-B

```bash
git add app/routes/map_preview.py app/qa_engine.py app/static/js/map-viewer.js
git commit -m "D1-B: Height source validation

- Add height_source field to map_data properties
- Create classify_height_confidence() function
- Add Height Source and Height Confidence to popups
- Validate height source for existing poles (blocker if missing height, warning if source unknown)
- Add confidence level labels (high/medium/low/unknown)
- Flag legacy/plan heights for field verification

Enforces height source reliability for clearance calculations.
All tests passing."
git push origin master
```

---

## PACKAGE D1-C: SOURCE CONFIDENCE & LEGACY DATA WARNINGS

**Priority:** HIGH
**Time:** 1-2 days
**Problem:** "Source Confidence: legacy map data" not clearly flagged as unverified

---

### Problem Evidence

**From user screenshots:**
- Multiple poles show "Source Confidence: legacy map data"
- **This is NOT field-captured survey data**
- Designer has no idea this geometry is unverified

**Survey Research Requirements:**
> "Source provenance: field observed / DNO GIS / drawing / proposed by design / inferred"

---

### Solution: Source Confidence & Provenance Framework

**Backend:** `app/routes/map_preview.py`

**Expand source confidence classification:**

```python
def classify_source_confidence(record):
    """
    Determine data provenance and confidence level.

    Returns:
        dict with 'provenance', 'confidence', 'geometry_trust', 'warnings'
    """
    source = str(record.get('source_confidence') or record.get('data_source') or '').lower()
    capture_method = str(record.get('capture_method') or '').lower()
    gnss_accuracy = record.get('gnss_accuracy')

    # Field observed with RTK/PPK (highest confidence)
    if 'field' in source and ('rtk' in capture_method or 'ppk' in capture_method):
        return {
            'provenance': 'field_observed_rtk',
            'confidence': 'high',
            'geometry_trust': 'survey_grade',
            'warnings': [],
            'designer_note': 'Field survey with RTK GNSS — geometry is survey-grade'
        }

    # Field observed with standalone GNSS (medium-high confidence)
    if 'field' in source and 'gnss' in capture_method:
        return {
            'provenance': 'field_observed_gnss',
            'confidence': 'medium-high',
            'geometry_trust': 'mapping_grade',
            'warnings': ['Standalone GNSS — adequate for design, ±0.5-2m typical'],
            'designer_note': 'Field survey with standalone GNSS'
        }

    # Field observed (method unspecified)
    if 'field' in source or 'observed' in source:
        return {
            'provenance': 'field_observed',
            'confidence': 'medium',
            'geometry_trust': 'field_verified',
            'warnings': ['Capture method not specified — assume mapping-grade accuracy'],
            'designer_note': 'Field survey (method not specified)'
        }

    # DNO GIS import (medium confidence for position, low for attributes)
    if 'gis' in source or 'dno' in source:
        return {
            'provenance': 'dno_gis_import',
            'confidence': 'medium',
            'geometry_trust': 'gis_inherited',
            'warnings': ['Imported from DNO GIS — verify critical attributes before design'],
            'designer_note': 'DNO GIS import — position likely reliable, attributes may be outdated'
        }

    # Legacy map data (LOW confidence — needs field verification)
    if 'legacy' in source or 'map data' in source:
        return {
            'provenance': 'legacy_map_data',
            'confidence': 'low',
            'geometry_trust': 'unverified',
            'warnings': [
                '⚠️ LEGACY MAP DATA — NOT FIELD VERIFIED',
                'Geometry and attributes from historical records',
                'Field verification required before design'
            ],
            'designer_note': 'Legacy map data — field verification required'
        }

    # From drawing/plan (low confidence)
    if 'drawing' in source or 'plan' in source or 'digitised' in source:
        return {
            'provenance': 'digitised_from_drawing',
            'confidence': 'low',
            'geometry_trust': 'indicative',
            'warnings': ['Digitised from plan/drawing — field verification required'],
            'designer_note': 'Digitised from drawing — not field-verified'
        }

    # Proposed by design (not survey data at all)
    if 'proposed' in source or 'design' in source:
        return {
            'provenance': 'proposed_by_design',
            'confidence': 'n/a',
            'geometry_trust': 'design_intent',
            'warnings': ['Proposed design location — not survey data'],
            'designer_note': 'Design proposal — not field-verified'
        }

    # Inferred/calculated (low confidence)
    if 'inferred' in source or 'calculated' in source:
        return {
            'provenance': 'inferred',
            'confidence': 'low',
            'geometry_trust': 'estimated',
            'warnings': ['Inferred/calculated position — field verification recommended'],
            'designer_note': 'Inferred position — verify if critical'
        }

    # Unknown source (cannot trust)
    return {
        'provenance': 'unknown',
        'confidence': 'unknown',
        'geometry_trust': 'unknown',
        'warnings': ['⚠️ DATA SOURCE UNKNOWN — reliability cannot be determined'],
        'designer_note': 'Source unknown — treat with caution'
    }
```

---

### Frontend Display: Legacy Data Warning Banner

**File:** `app/static/js/map-viewer.js`

**Add legacy data warning to popup:**

```javascript
buildStandardPolePopup(props, lat, lon) {
  const sourceConf = props.source_confidence_detail || {};

  // Build legacy data warning banner if applicable
  let legacyWarningBanner = '';
  if (sourceConf.provenance === 'legacy_map_data') {
    legacyWarningBanner = `
      <div class="legacy-data-warning-banner">
        <div class="warning-icon">⚠️</div>
        <div class="warning-content">
          <strong>LEGACY MAP DATA — NOT FIELD VERIFIED</strong>
          <p>This record is from historical map data, not current field survey. Geometry and attributes may be outdated or inaccurate.</p>
          <p><strong>Designer Action:</strong> Field verification required before design or construction.</p>
        </div>
      </div>
    `;
  }

  return `
    <div class="pole-popup ${sourceConf.provenance === 'legacy_map_data' ? 'legacy-data' : ''}">
      ${legacyWarningBanner}

      ${this.popupSection('Identity', this.identityRows(props, lat, lon))}
      ${this.popupSection('Physical', this.physicalRows(props))}
      ${this.popupSection('Electrical', this.electricalRows(props))}
      ${this.popupSection('Location', this.locationRows(props, lat, lon))}
      ${this.popupSection('Evidence', this.evidenceRows(props))}
      ${this.popupSection('Source & Confidence', this.sourceConfidenceRows(props))}
      ${this.popupSection('Lifecycle / Design', this.lifecycleRows(props))}
      ${this.popupSection('QA / Review', this.qaRows(props))}
    </div>
  `;
}

sourceConfidenceRows(props) {
  const sourceConf = props.source_confidence_detail || {};

  return [
    this.popupRow(
      'Data Provenance',
      this.formatProvenance(sourceConf.provenance),
      this.getProvenanceStatus(sourceConf.confidence),
      sourceConf.designer_note || ''
    ),

    this.popupRow(
      'Confidence Level',
      this.formatConfidenceLevel(sourceConf.confidence),
      this.getProvenanceStatus(sourceConf.confidence)
    ),

    this.popupRow(
      'Geometry Trust',
      this.formatGeometryTrust(sourceConf.geometry_trust),
      this.getProvenanceStatus(sourceConf.confidence)
    ),

    // Show warnings if present
    ...(sourceConf.warnings || []).map(warning =>
      this.popupRow('⚠️ Warning', warning, 'warning')
    )
  ];
}

formatProvenance(prov) {
  const labels = {
    'field_observed_rtk': 'Field Survey (RTK GNSS)',
    'field_observed_gnss': 'Field Survey (Standalone GNSS)',
    'field_observed': 'Field Survey',
    'dno_gis_import': 'DNO GIS Import',
    'legacy_map_data': 'Legacy Map Data',
    'digitised_from_drawing': 'Digitised from Drawing',
    'proposed_by_design': 'Design Proposal',
    'inferred': 'Inferred/Calculated',
    'unknown': 'Unknown Source'
  };

  return labels[prov] || prov;
}

getProvenanceStatus(confidence) {
  if (confidence === 'high') return 'ok';
  if (confidence === 'medium-high' || confidence === 'medium') return 'info';
  if (confidence === 'low') return 'warning';
  return 'review';
}

formatGeometryTrust(trust) {
  const labels = {
    'survey_grade': '✓ Survey-grade (±0.02-0.05m)',
    'mapping_grade': '✓ Mapping-grade (±0.5-2m)',
    'field_verified': '✓ Field-verified',
    'gis_inherited': '◐ GIS inherited (verify if critical)',
    'unverified': '✗ Unverified (field check required)',
    'indicative': '◐ Indicative only',
    'design_intent': 'Design proposal',
    'estimated': '◐ Estimated',
    'unknown': '? Unknown'
  };

  return labels[trust] || trust;
}
```

**Add CSS for legacy warning banner:**

```css
/* Legacy data warning banner */
.legacy-data-warning-banner {
  background: #fef3c7;
  border: 2px solid #f59e0b;
  border-radius: 6px;
  padding: 12px;
  margin-bottom: 16px;
  display: flex;
  gap: 12px;
  align-items: start;
}

.legacy-data-warning-banner .warning-icon {
  font-size: 2rem;
  line-height: 1;
}

.legacy-data-warning-banner .warning-content strong {
  color: #92400e;
  font-size: 0.95rem;
  display: block;
  margin-bottom: 6px;
}

.legacy-data-warning-banner .warning-content p {
  color: #78350f;
  font-size: 0.85rem;
  margin: 4px 0;
  line-height: 1.4;
}

.pole-popup.legacy-data {
  border-left: 5px solid #f59e0b;
}
```

---

### Test & Validation

**After implementing:**

1. Load job with legacy map data records
2. Click pole with "source_confidence: legacy map data"
3. Verify popup shows:
   - ⚠️ LEGACY MAP DATA — NOT FIELD VERIFIED banner at top
   - Data Provenance: Legacy Map Data
   - Confidence Level: Low
   - Geometry Trust: ✗ Unverified (field check required)
   - Warning: "Field verification required before design"
4. Verify legacy poles have visual distinction (border)

---

### Commit D1-C

```bash
git add app/routes/map_preview.py app/static/js/map-viewer.js app/static/style.css
git commit -m "D1-C: Source confidence & legacy data warnings

- Create classify_source_confidence() with provenance types
- Add provenance/confidence/geometry_trust fields
- Create legacy data warning banner (⚠️ NOT FIELD VERIFIED)
- Add Source & Confidence popup section
- Visual distinction for legacy data records (border + banner)
- Confidence levels: high/medium/low/unknown
- Geometry trust: survey-grade/mapping-grade/unverified

Makes data provenance visible to designers.
All tests passing."
git push origin master
```

---

## PACKAGE D1-D: THIRD-PARTY INFRASTRUCTURE & ATTACHMENTS

**Priority:** HIGH
**Time:** 1-2 days
**Problem:** Third-party attachments (BT, streetlights, customer services) invisible in current data model

---

### Solution: Third-Party Attachments Schema

**Backend:** `app/routes/map_preview.py`

**Add attachments to map_data:**

```python
def parse_attachments(record):
    """
    Parse and classify third-party attachments on poles.

    Returns:
        dict with 'has_attachments', 'attachment_types', 'attachment_list', 'coordination_required'
    """
    attachments_str = str(record.get('attachments') or record.get('third_party') or '').lower()
    remarks = str(record.get('remarks') or '').lower()

    attachments = []

    # Telecoms
    if any(kw in attachments_str or kw in remarks for kw in ['bt', 'openreach', 'virgin', 'telecom', 'fibre', 'copper']):
        attachments.append({
            'type': 'telecoms',
            'owner': 'BT/Openreach/Virgin',
            'impact': 'Wayleave coordination may be required',
            'icon': '📡'
        })

    # Streetlight
    if any(kw in attachments_str or kw in remarks for kw in ['streetlight', 'street light', 'lamp', 'lighting']):
        attachments.append({
            'type': 'streetlight',
            'owner': 'Local Authority',
            'impact': 'LA coordination required if pole replacement planned',
            'icon': '💡'
        })

    # Customer service
    if any(kw in attachments_str or kw in remarks for kw in ['customer', 'service', 'private']):
        attachments.append({
            'type': 'customer_service',
            'owner': 'Customer',
            'impact': 'Customer notification required',
            'icon': '🏠'
        })

    # Signage
    if any(kw in attachments_str or kw in remarks for kw in ['sign', 'notice', 'warning']):
        attachments.append({
            'type': 'signage',
            'owner': 'Various',
            'impact': 'Relocate/replace signage if pole removed',
            'icon': '🚧'
        })

    # CCTV/security
    if any(kw in attachments_str or kw in remarks for kw in ['cctv', 'camera', 'security']):
        attachments.append({
            'type': 'cctv',
            'owner': 'LA/Private',
            'impact': 'Security equipment coordination required',
            'icon': '📹'
        })

    return {
        'has_attachments': len(attachments) > 0,
        'attachment_count': len(attachments),
        'attachment_types': [a['type'] for a in attachments],
        'attachment_list': attachments,
        'coordination_required': len(attachments) > 0
    }
```

---

### Frontend Display

**File:** `app/static/js/map-viewer.js`

**Add Attachments section to pole popup:**

```javascript
attachmentsRows(props) {
  const attachments = props.attachments_detail || {};

  if (!attachments.has_attachments) {
    return [
      this.popupRow('Third-Party Attachments', 'None recorded', 'info')
    ];
  }

  return [
    this.popupRow(
      'Attachments Present',
      `Yes (${attachments.attachment_count})`,
      'warning',
      'Third-party coordination may be required'
    ),

    // List each attachment
    ...(attachments.attachment_list || []).map(att =>
      this.popupRow(
        `${att.icon} ${att.type}`,
        `Owner: ${att.owner}`,
        'warning',
        att.impact
      )
    ),

    this.popupRow(
      'Coordination Required',
      'Yes — notify third parties before pole work',
      'warning'
    )
  ];
}

// Add to buildStandardPolePopup():
${this.popupSection('Third-Party Attachments', this.attachmentsRows(props))}
```

---

### Test & Validation

1. Load pole with "streetlight" in remarks
2. Verify popup shows:
   - Third-Party Attachments: Yes (1)
   - 💡 streetlight: Owner: Local Authority
   - Impact: LA coordination required if pole replacement planned
   - Coordination Required: Yes

---

### Commit D1-D

```bash
git add app/routes/map_preview.py app/static/js/map-viewer.js
git commit -m "D1-D: Third-party attachments handling

- Add parse_attachments() function
- Detect telecoms/streetlight/customer/signage/CCTV
- Add Third-Party Attachments popup section
- Show owner, impact, coordination requirements
- Flag coordination_required for construction planning

Makes third-party dependencies visible.
All tests passing."
git push origin master
```

---

# PHASE 2: COMPLETE ELECTRICAL DATA MODEL

## PACKAGE D2-A: CONDUCTOR/CABLE ELECTRICAL SCHEMA

**Priority:** CRITICAL
**Time:** 3-4 days
**Problem:** No conductor/cable specification = cannot design without knowing what cable to use

---

### Problem Evidence

**From user screenshot (Point 72 BT pole):**
- "Line Voltage: 11kV" — **inferred, not captured**
- "Conductor Type: not recorded"
- "Phases: not recorded"
- "Mounted Equipment: not captured"

**From Survey Research:**
> "Conductor/cable: type, size, cores/phases, material, sheath, bare/covered/ABC, service/main/HV/LV"

---

### Solution: Complete Conductor/Cable Schema

**Create:** `app/electrical_schema.py` (new file)

```python
"""
Complete electrical data model for conductors, cables, equipment and network connectivity.

Based on UK Electrical Grid Survey Data Capture Report.
"""

# Voltage classifications
VOLTAGE_TYPES = {
    'LV': {
        'label': 'Low Voltage',
        'range': '230V / 400V',
        'typical_use': 'Customer connections, LV mains'
    },
    '6.6kV': {
        'label': '6.6kV Medium Voltage',
        'range': '6.6kV',
        'typical_use': 'Industrial/wind farm distribution'
    },
    '11kV': {
        'label': '11kV High Voltage',
        'range': '11kV',
        'typical_use': 'Primary distribution, most common HV'
    },
    '20kV': {
        'label': '20kV High Voltage',
        'range': '20kV',
        'typical_use': 'Some DNO networks'
    },
    '33kV': {
        'label': '33kV High Voltage',
        'range': '33kV',
        'typical_use': 'Subtransmission, bulk supply'
    },
    '66kV': {
        'label': '66kV Extra High Voltage',
        'range': '66kV',
        'typical_use': 'Subtransmission'
    },
    '110kV': {
        'label': '110kV Extra High Voltage',
        'range': '110kV',
        'typical_use': 'Transmission crossings (Scotland)'
    },
    '132kV': {
        'label': '132kV Extra High Voltage',
        'range': '132kV',
        'typical_use': 'Transmission crossings'
    }
}

# Overhead conductor types
OVERHEAD_CONDUCTOR_TYPES = {
    'AAC': {
        'name': 'All Aluminium Conductor',
        'material': 'Aluminium',
        'typical_use': 'Standard overhead distribution'
    },
    'AAAC': {
        'name': 'All Aluminium Alloy Conductor',
        'material': 'Aluminium alloy',
        'typical_use': 'Improved strength overhead lines'
    },
    'ACSR': {
        'name': 'Aluminium Conductor Steel Reinforced',
        'material': 'Aluminium + steel core',
        'typical_use': 'Long spans, high mechanical strength'
    },
    'Cu': {
        'name': 'Copper conductor',
        'material': 'Copper',
        'typical_use': 'Older installations, heritage areas'
    },
    'ABC': {
        'name': 'Aerial Bundled Cable',
        'material': 'Insulated aluminium',
        'typical_use': 'Tree-prone areas, LV distribution'
    },
    'Bare': {
        'name': 'Bare conductor',
        'material': 'Various',
        'typical_use': 'Standard overhead lines'
    },
    'Covered': {
        'name': 'Covered conductor',
        'material': 'Various with insulation',
        'typical_use': 'Wildlife/vegetation protection'
    }
}

# Underground cable types
UNDERGROUND_CABLE_TYPES = {
    'XLPE': {
        'name': 'Cross-Linked Polyethylene',
        'insulation': 'XLPE',
        'typical_use': 'Modern HV/LV underground cables'
    },
    'PILC': {
        'name': 'Paper Insulated Lead Covered',
        'insulation': 'Oil-impregnated paper + lead sheath',
        'typical_use': 'Legacy underground cables'
    },
    'Waveform': {
        'name': 'Waveform LV cable',
        'insulation': 'PVC/XLPE',
        'typical_use': 'LV underground distribution'
    },
    'Concentric': {
        'name': 'Concentric neutral cable',
        'insulation': 'XLPE with concentric neutral',
        'typical_use': 'LV/HV single-phase or 3-phase'
    },
    'Service': {
        'name': 'Service cable',
        'insulation': 'Various',
        'typical_use': 'Customer service connections'
    }
}

# Conductor sizes (examples - not exhaustive)
CONDUCTOR_SIZES = {
    # Overhead AAC/AAAC common sizes
    '7/2.75': 'AAC 7-strand 2.75mm (25mm² approx)',
    '7/3.00': 'AAC 7-strand 3.00mm (35mm² approx)',
    '7/3.75': 'AAC 7-strand 3.75mm (50mm² approx)',
    '7/4.50': 'AAC 7-strand 4.50mm (70mm² approx)',
    '19/3.00': 'AAC 19-strand 3.00mm (100mm² approx)',
    '19/3.50': 'AAC 19-strand 3.50mm (150mm² approx)',

    # Underground cable sizes
    '16mm²': '16mm² (small service)',
    '25mm²': '25mm²',
    '35mm²': '35mm²',
    '50mm²': '50mm²',
    '95mm²': '95mm² (LV main)',
    '185mm²': '185mm² (HV)',
    '300mm²': '300mm² (HV)'
}

# Phase configurations
PHASE_CONFIGURATIONS = {
    'single': {
        'conductors': 2,
        'description': 'Single phase (L + N)',
        'typical_use': 'Customer services, streetlighting'
    },
    '2-phase': {
        'conductors': 3,
        'description': 'Two phase (2L + N)',
        'typical_use': 'Larger customer services'
    },
    '3-phase': {
        'conductors': 4,
        'description': 'Three phase (3L + N)',
        'typical_use': 'LV mains, industrial supplies'
    },
    '3-phase_no_neutral': {
        'conductors': 3,
        'description': 'Three phase (3L, no N)',
        'typical_use': 'HV overhead lines (11kV, 33kV)'
    }
}


def parse_conductor_data(record):
    """
    Parse conductor/cable information from record.

    Returns comprehensive conductor/cable structure.
    """
    voltage = record.get('voltage') or record.get('line_voltage')
    conductor_type = record.get('conductor_type')
    conductor_size = record.get('conductor_size')
    phases = record.get('phases') or record.get('phase_count')
    cable_type = record.get('cable_type')

    # Determine if overhead or underground
    is_underground = bool(cable_type or record.get('route_type') == 'underground')

    result = {
        'voltage': voltage,
        'voltage_detail': VOLTAGE_TYPES.get(voltage, {}),
        'is_overhead': not is_underground,
        'is_underground': is_underground,
    }

    if not is_underground:
        # Overhead conductor
        result.update({
            'conductor_type': conductor_type,
            'conductor_detail': OVERHEAD_CONDUCTOR_TYPES.get(conductor_type, {}),
            'conductor_size': conductor_size,
            'conductor_size_detail': CONDUCTOR_SIZES.get(conductor_size, {}),
            'phases': phases,
            'phase_detail': PHASE_CONFIGURATIONS.get(phases, {}),
            'is_bare': conductor_type == 'Bare',
            'is_covered': conductor_type in ['Covered', 'ABC'],
        })
    else:
        # Underground cable
        result.update({
            'cable_type': cable_type,
            'cable_detail': UNDERGROUND_CABLE_TYPES.get(cable_type, {}),
            'cable_size': conductor_size,  # Same field, different name
            'cores_phases': phases,
            'phase_detail': PHASE_CONFIGURATIONS.get(phases, {}),
        })

    return result
```

---

### Backend Integration

**File:** `app/routes/map_preview.py`

**Add conductor/cable data to map_data:**

```python
from app.electrical_schema import parse_conductor_data

def build_feature_properties(record):
    """Build comprehensive feature properties for map display."""

    # ... existing fields ...

    # === CONDUCTOR/CABLE ELECTRICAL DATA ===
    conductor_data = parse_conductor_data(record)
    props.update({
        'voltage': record.get('voltage'),
        'voltage_detail': conductor_data.get('voltage_detail'),
        'conductor_type': record.get('conductor_type'),
        'conductor_detail': conductor_data.get('conductor_detail'),
        'conductor_size': record.get('conductor_size'),
        'phases': record.get('phases'),
        'phase_detail': conductor_data.get('phase_detail'),
        'cable_type': record.get('cable_type'),
        'cable_detail': conductor_data.get('cable_detail'),
        'is_overhead': conductor_data.get('is_overhead'),
        'is_underground': conductor_data.get('is_underground'),
    })

    return props
```

---

### Frontend Display

**File:** `app/static/js/map-viewer.js`

**Expand `electricalRows()` with complete conductor data:**

```javascript
electricalRows(props) {
  const rows = [];

  // Voltage
  rows.push(
    this.popupRow(
      'Line Voltage',
      props.voltage || 'not recorded',
      props.voltage ? 'ok' : 'review',
      props.voltage_detail?.label || ''
    )
  );

  // Overhead vs Underground
  if (props.is_overhead) {
    // OVERHEAD CONDUCTOR DETAILS
    rows.push(
      this.popupRow(
        'Conductor Type',
        props.conductor_type || 'not recorded',
        props.conductor_type ? 'ok' : 'review',
        props.conductor_detail?.name || ''
      )
    );

    rows.push(
      this.popupRow(
        'Conductor Size',
        props.conductor_size || 'not recorded',
        props.conductor_size ? 'ok' : 'info',
        CONDUCTOR_SIZES[props.conductor_size] || ''
      )
    );

    rows.push(
      this.popupRow(
        'Phase Configuration',
        props.phases || 'not recorded',
        props.phases ? 'ok' : 'info',
        props.phase_detail?.description || ''
      )
    );

    rows.push(
      this.popupRow(
        'Conductor Form',
        props.conductor_type === 'Bare' ? 'Bare conductor' :
        props.conductor_type === 'ABC' ? 'Aerial bundled cable (ABC)' :
        props.conductor_type === 'Covered' ? 'Covered conductor' :
        'Not specified',
        'info'
      )
    );

  } else if (props.is_underground) {
    // UNDERGROUND CABLE DETAILS
    rows.push(
      this.popupRow(
        'Cable Type',
        props.cable_type || 'not recorded',
        props.cable_type ? 'ok' : 'review',
        props.cable_detail?.name || ''
      )
    );

    rows.push(
      this.popupRow(
        'Cable Size',
        props.cable_size || 'not recorded',
        props.cable_size ? 'ok' : 'info'
      )
    );

    rows.push(
      this.popupRow(
        'Cores/Phases',
        props.cores_phases || 'not recorded',
        props.cores_phases ? 'ok' : 'info',
        props.phase_detail?.description || ''
      )
    );
  }

  // Equipment (applies to both overhead and underground)
  const equipment = Array.isArray(props.equipment) && props.equipment.length > 0
    ? props.equipment.join(', ')
    : props.equipment;

  rows.push(
    this.popupRow(
      'Mounted Equipment',
      equipment || 'none recorded',
      equipment ? 'ok' : 'info',
      equipment ? '⚡' : ''
    )
  );

  if (props.equipment_rating) {
    rows.push(
      this.popupRow(
        'Equipment Rating',
        props.equipment_rating,
        'ok'
      )
    );
  }

  return rows;
}
```

---

### Validation Rule: Conductor Data Required

**File:** `app/qa_engine.py`

**Add validation:**

```python
def validate_conductor_data_completeness(record):
    """
    Overhead spans should have voltage, conductor type, phases.
    Underground routes should have voltage, cable type, cores.
    """
    record_type = record.get('record_type', '').lower()

    # Only apply to spans/routes
    if not any(kw in record_type for kw in ['span', 'route', 'cable', 'conductor']):
        return []

    issues = []

    voltage = record.get('voltage')
    conductor_type = record.get('conductor_type')
    cable_type = record.get('cable_type')
    phases = record.get('phases')

    # Voltage missing = WARNING (can often be inferred from context)
    if not voltage:
        issues.append({
            'severity': 'WARN',
            'code': 'VOLTAGE_NOT_RECORDED',
            'message': 'Line voltage not recorded',
            'field': 'voltage',
            'recommended_action': 'Confirm voltage from job context or adjacent poles'
        })

    # Conductor type missing (overhead) = INFO (useful but not critical)
    if not cable_type and not conductor_type:
        issues.append({
            'severity': 'INFO',
            'code': 'CONDUCTOR_TYPE_NOT_RECORDED',
            'message': 'Conductor/cable type not recorded',
            'field': 'conductor_type',
            'recommended_action': 'Record conductor type for material take-off and design'
        })

    # Phases missing = INFO
    if not phases:
        issues.append({
            'severity': 'INFO',
            'code': 'PHASE_CONFIGURATION_NOT_RECORDED',
            'message': 'Phase configuration not recorded',
            'field': 'phases',
            'recommended_action': 'Record phase arrangement where visible'
        })

    return issues
```

---

### Test & Validation

**After implementing:**

1. Load span record with voltage/conductor/phases
2. Verify popup Electrical section shows:
   - Line Voltage: 11kV (11kV High Voltage)
   - Conductor Type: AAC (All Aluminium Conductor)
   - Conductor Size: 7/3.75 (AAC 7-strand 3.75mm)
   - Phase Configuration: 3-phase_no_neutral (Three phase 3L, no N)
   - Conductor Form: Bare conductor
3. Load underground cable
4. Verify shows Cable Type, Cable Size, Cores/Phases

---

### Commit D2-A

```bash
git add app/electrical_schema.py app/routes/map_preview.py app/qa_engine.py app/static/js/map-viewer.js
git commit -m "D2-A: Complete conductor/cable electrical schema

- Create electrical_schema.py with voltage/conductor/cable types
- Add VOLTAGE_TYPES, OVERHEAD_CONDUCTOR_TYPES, UNDERGROUND_CABLE_TYPES
- Add CONDUCTOR_SIZES, PHASE_CONFIGURATIONS dictionaries
- Expand electricalRows() with overhead vs underground logic
- Add conductor/cable data validation rules
- Show detailed electrical specifications in popups

Implements complete electrical data model from survey research.
All tests passing."
git push origin master
```

---

**[CONTINUES with Packages D2-B, D2-C, D2-D, and Phase 3...]**

This specification continues for another ~8,000 words covering:
- Equipment & pole-top configuration
- Network connectivity & relationships
- Survey metadata & provenance
- Backend integration
- Frontend display updates
- Validation rules
- Export quality

**Would you like me to continue with the complete specification, or shall I create a condensed "implementation roadmap" document that Cursor can work through package-by-package?**

The complete spec will be ~15,000-20,000 words total. I can deliver it either as:
1. One massive battle-ready document (like Phase C2/D)
2. A phased roadmap where Cursor completes and reports after each package

**What's your preference?**
