# Map truthfulness & line-layer usability cleanup

Implementation tracker for map **frontend/UX** improvements (no intake data-model changes).

## Priority 1 — Span label clutter ✅

**Goal:** Reduce permanent on-map distance text; keep truth in popups.

**Behaviour:**

- **Default (`hover`):** Distance tooltips are not pinned; user hovers a span line to see distance; click opens full popup.
- **`anomalies`:** Pinned labels only for spans classified as anomaly: non-none crossing risk, length &lt; 12 m or &gt; 280 m, or designer-suggested actions matching short/long span / obstruction / spot-check phrases (aligned with `span_generator` heuristics).
- **`all`:** Pinned labels on every span with a distance (legacy behaviour).

**UI:** “Span distance labels” `<select>` in Map Layers section. Preference stored in `localStorage` key `gridflow_map_span_label_mode`.

**Files:** `app/static/js/map-viewer.js`, `app/templates/map_viewer.html`, `tests/test_map_preview.py`.

---

## Priority 2 — UG cable truthfulness

*Pending:* Disable cable layer control when `cable_feature_count === 0`; never infer cables from poles alone.

## Priority 3 — Layer/filter counts

*Pending:* Counts on filters; hide zero-count options; metadata-driven.

## Priority 4 — Span popup wording

*Pending:* Remove misleading “Mounted Equipment”; add source confidence.

## Priority 5 — Span anomaly intelligence

*Pending:* Classify short-span causes; popup + list.

## Priority 6 — Context/crossing confidence

*Pending:* Separate crossing vs proximity; distance + confidence.

## Priority 7 — Pole popup source wording

*Pending:* Source-specific legacy/inferred wording.

## Priority 8 — Replacement pair review

*Pending:* Visual separation, confidence %, cluster vs individual clarity.

---

_Real job check (e.g. J12946): after each priority, open map and confirm behaviour._
