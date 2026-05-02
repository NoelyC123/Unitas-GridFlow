# TASK 0: MAP FINAL CLEANUP — P005/F001 VALIDATION FOLLOW-UP

**Timeline:** 1-2 days | **Target:** 500+ tests | **Priority:** HIGH — Must complete before Task 1

**Status:** Ready to implement based on P005/F001 manual validation review

---

## VALIDATION EVIDENCE

**Job:** P005/F001
**Mapped records:** 155
**Total survey records:** 157
**Structural records:** 128
**Context records:** 27
**Top summary shows:** 2 anchor
**Layer panel shows:** Stays/Anchors (0)
**Provisional route spans:** 101
**EX/PR matches:** 11
**Replacement map links:** 0 rec · 0 on map

---

## WHAT PASSED ✅

The following are validated and working:
- ✅ Provisional route span naming (was "Circuit spans", now correct)
- ✅ Span label dropdown (5 modes functional)
- ✅ Zero-count layers disabled/greyed out
- ✅ UG cable truthfulness
- ✅ Context/crossing review panel
- ✅ Source cue / legacy map warning
- ✅ Export/download controls
- ✅ Readiness summary

---

## WHAT NEEDS FIXING (5 ISSUES)

### ISSUE 1: Pole Popup Empty-Section Collapse ❌ HIGH PRIORITY

**Problem:** Pole popups still show long lists of empty fields like:
```
Circuit ID — not captured
Year Installed — not captured
Action Required — not captured
Design Note — not captured
Parsed kVA — not parsed
Voltage ratio — not recorded
Pole-top arrangement — not recorded
Insulator type — not recorded
Crossarm configuration — not recorded
Earthing — not recorded
Asset plate / label — not recorded
Equipment mounting — not recorded
From support —
To support —
Parent pole —
Parent structure —
Cable from asset —
Cable to asset —
Surveyor —
Survey date —
Survey equipment —
GNSS / accuracy —
```

**Required fix:** Collapse empty field groups into concise summaries.

**Implementation:**

Replace empty equipment fields with:
```
Equipment & pole-top
No pole-mounted equipment captured or inferred.
```

Replace empty network link fields with:
```
Network links
No explicit pole/cable/parent structure links captured for this record.
```

Replace empty survey metadata with:
```
Survey metadata
Surveyor, date, survey equipment and GNSS accuracy not captured in this export.
```

Then add a real collapsed accordion:
```
[+ Show raw / technical fields] (collapsed by default)

When expanded:
[- Hide raw / technical fields]
  Circuit ID: not captured
  Year Installed: not captured
  ... (all raw fields)
```

**Files to modify:**
- `app/templates/map_viewer.html` — popup HTML structure
- `app/static/js/map-viewer.js` — popup rendering logic
- `app/static/css/map-viewer.css` — accordion styling

**Tests:**
- `test_pole_popup_empty_sections_collapsed()` — verify empty groups collapsed
- `test_raw_fields_expandable()` — verify accordion works

---

### ISSUE 2: Anchor/Stay Count Clarity ❌ HIGH PRIORITY

**Problem:** Top summary says "2 anchor", layer panel says "Stays/Anchors (0)", no stay/anchor features visible on map.

**Confusion:** Survey/control/base anchor records vs mechanical stay/anchor assets are different things.

**Required fix:** Distinguish the two clearly.

**Implementation:**

Change top summary from:
```
2 anchor
```

To:
```
2 control/base records
```

Or:
```
2 non-mechanical anchor records
```

Change layer panel from:
```
Stays/Anchors (0)
```

To:
```
Mechanical stays/anchors (0)
```

Add tooltip:
```
No mechanical stay or anchor asset records detected. The 2 anchor records in the summary are survey/control records, not stay assets.
```

**Files to modify:**
- `app/routes/map_preview.py` — summary text generation
- `app/templates/map_viewer.html` — layer panel labels
- `app/static/js/map-viewer.js` — tooltip text

**Tests:**
- `test_anchor_stay_count_distinction()` — verify wording distinguishes types
- `test_mechanical_stay_layer_label()` — verify layer name clear

---

### ISSUE 3: Replacement Link Wording ⚠️ MEDIUM PRIORITY

**Problem:** Current UI shows:
```
EX/PR matches (11)
Suggested replacement map links (0 rec · 0 on map)
```

This is confusing — why 11 matches but 0 links?

**Required fix:** Clearer wording that explains the distinction.

**Implementation:**

Change to:
```
EX/PR match records (11)
Replacement map links (0 drawn)
```

Add explanatory note (tooltip or help text):
```
Match records are detected relationships based on proximity and context.
Map links are only drawn where drawable link geometry exists.
```

**Alternative (if drawable):** If the 11 relationships can be drawn reliably, generate the dashed orange links and show:
```
Suggested replacement links (11)
```

**Files to modify:**
- `app/templates/map_viewer.html` — layer/filter labels
- `app/static/js/map-viewer.js` — tooltip/help text

**Tests:**
- `test_replacement_link_wording()` — verify labels clear

---

### ISSUE 4: Short-Span Cause Classification ⚠️ MEDIUM-HIGH PRIORITY

**Problem:** Short spans show "Short span" and generic "verify no duplicate entry" warnings, but don't classify the likely cause.

**Required fix:** Add a "Likely cause" field to short-span popups.

**Implementation:**

Add classification to span popups:
```
Short span classification
Likely cause: Replacement/co-located pair
Reason: Nearby EX/PR relationship detected within 5m tolerance.
```

Or:
```
Short span classification
Likely cause: Possible duplicate capture
Reason: Span is below normal design threshold (5m) and adjacent records are very close.
```

Or:
```
Short span classification
Likely cause: Possible sequence issue
Reason: Span is unusually short but no obvious duplicate or replacement pair detected.
```

Or:
```
Short span classification
Likely cause: Possible genuine short span
Reason: Pole function suggests intentional short span (terminal, strut, etc.).
```

Or:
```
Short span classification
Likely cause: Uncertain
Reason: Insufficient evidence to determine cause. Manual review required.
```

**Logic:**
```python
def classify_short_span_cause(span, from_pole, to_pole, nearby_records):
    """Determine likely cause of short span."""
    distance = span['distance']

    # Check for nearby EX/PR pair
    ex_pr_pair = detect_nearby_ex_pr_pair(from_pole, to_pole, nearby_records, tolerance=5)
    if ex_pr_pair:
        return {
            'cause': 'Replacement/co-located pair',
            'reason': f'Nearby EX/PR relationship detected within {ex_pr_pair.distance}m tolerance.'
        }

    # Check for possible duplicate
    if distance < 2:  # Very short
        return {
            'cause': 'Possible duplicate capture',
            'reason': 'Span is extremely short, suggesting possible double-capture of same pole.'
        }

    # Check pole functions
    if 'terminal' in from_pole.get('function', '').lower() or 'strut' in from_pole.get('function', '').lower():
        return {
            'cause': 'Possible genuine short span',
            'reason': 'Pole function suggests intentional short span (terminal, strut, etc.).'
        }

    # Default
    return {
        'cause': 'Uncertain',
        'reason': 'Insufficient evidence to determine cause. Manual review required.'
    }
```

**Files to modify:**
- `app/qa_engine.py` — add `classify_short_span_cause()`
- `app/routes/map_preview.py` — include classification in map_data.json
- `app/static/js/map-viewer.js` — render classification in span popup

**Tests:**
- `test_short_span_cause_classification()` — verify all 5 causes detectable
- `test_replacement_pair_detection()` — verify EX/PR pair logic

---

### ISSUE 5: Span Popup Review/Action Wording ⚠️ LOW-MEDIUM PRIORITY

**Problem:** Span popups show conductor/phase missing as review signals, but only show crossing/clearance in designer actions. Need combined action for missing electrical data.

**Required fix:** Add combined designer action for conductor/phase when missing.

**Implementation:**

For span popups where conductor type/size or phase configuration is missing, add:
```
Designer actions (what to do next)
- Confirm statutory clearance and crossing profile for this span.
- Confirm conductor type, size and phase configuration before sag/tension or loading design.
```

Do NOT repeat the same text twice. Keep it concise.

**Files to modify:**
- `app/static/js/map-viewer.js` — span popup action section logic

**Tests:**
- `test_span_popup_combined_actions()` — verify actions not duplicated

---

## ACCEPTANCE CRITERIA

✅ Pole popups show collapsed empty-section summaries (not 20+ "not captured" lines)
✅ Raw/technical fields expandable accordion functional
✅ Anchor/stay count wording distinguishes control records vs mechanical assets
✅ Replacement link wording clear (match records vs drawable links)
✅ Short-span cause classification showing 5 possible causes
✅ Span popup actions combined and not duplicated
✅ All tests passing (500+)
✅ Committed and pushed to master

---

## TESTING INSTRUCTIONS

After implementation, validate on P005/F001:

1. Open `/map/view/P005` (or equivalent P005/F001 job)
2. Click existing pole 159 → verify empty sections collapsed, not 20+ empty fields
3. Click "Show raw/technical fields" → verify accordion expands
4. Check top summary → should say "2 control/base records" not "2 anchor"
5. Check layer panel → should say "Mechanical stays/anchors (0)"
6. Check EX/PR wording → should say "EX/PR match records (11)" and "Replacement map links (0 drawn)"
7. Find a short span (4.6m) → verify "Likely cause" shows classification
8. Click span 159→160 → verify designer actions show both clearance AND conductor/phase if missing

---

## FILES TO MODIFY

**Backend:**
- `app/qa_engine.py` — short-span cause classification logic
- `app/routes/map_preview.py` — summary text, classification in map_data.json

**Frontend:**
- `app/templates/map_viewer.html` — popup structure, layer labels, tooltips
- `app/static/js/map-viewer.js` — popup rendering, accordion, classification display
- `app/static/css/map-viewer.css` — accordion styling

**Tests:**
- `tests/test_map_popup_cleanup.py` (new file) — pole popup, accordion, classifications
- `tests/test_map_wording.py` (new file) — anchor/stay, replacement link wording

---

**READY FOR CURSOR IMPLEMENTATION**

This is a 1-2 day cleanup task based on real validation evidence from P005/F001.

Once complete, map will be professionally polished and ready for Task 1 (Stage 4 Polish).
