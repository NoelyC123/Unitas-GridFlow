const CONTEXT_FEATURE_CODES = new Set([
  'Hedge', 'hedge', 'HEDGE',
  'Tree', 'tree', 'TREE',
  'Wall', 'wall', 'WALL',
  'Fence', 'fence', 'FENCE',
  'Post', 'post', 'POST',
  'Gate', 'gate', 'GATE',
  'Road', 'road', 'ROAD',
  'Track', 'track', 'TRACK',
  'Stream', 'stream', 'STREAM',
  'BTxing', 'btxing', 'BTXING',
  'LVxing', 'lvxing', 'LVXING',
  'HVxing', 'hvxing', 'HVXING',
  '11xing', '33xing',
]);

const MARKER_SIZES = {
  existing: 10,
  proposed: 10,
  angle: 12,
  anchor: 8,
  context: 6,
  thirdparty: 11,
  other: 9,
};

class MapViewer {
  constructor() {
    this.jobId = document.querySelector('meta[name="job-id"]')?.content;
    this.mapDataUrl = document.querySelector('meta[name="map-data-url"]')?.content
      || `/map/data/${this.jobId}`;
    this.mapEl = document.getElementById('map');

    this.poleCountEl = document.getElementById('pole-count');
    this.passCountEl = document.getElementById('pass-count');
    this.warnCountEl = document.getElementById('warn-count');
    this.failCountEl = document.getElementById('fail-count');
    this.rulepackBadgeEl = document.getElementById('rulepack-badge');
    this.autoNormalizedEl = document.getElementById('auto-normalized');
    this.issueCountEl = document.getElementById('issue-count');
    this.issueNoteEl = document.getElementById('issue-note');
    this.filterNoteEl = document.getElementById('filter-note');

    this.map = null;
    this.featureData = [];
    this.spanLayer = null;
    this.lifecycleMatchLayer = null;
    this.activeFilter = null;
    this.activeFilterMode = null;
    this.fileType = null;
    this.layerState = {
      existing: true,
      proposed: true,
      angle: true,
      stays: true,
      thirdparty: true,
      context: false,
      spans: true,
      matches: true,
    };
  }

  init() {
    if (!this.jobId || !this.mapEl) return;

    this.map = L.map('map').setView([54.55, -3.1], 10);

    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
      attribution: '&copy; OpenStreetMap contributors',
      maxZoom: 19,
    }).addTo(this.map);

    this.loadData();
  }

  async loadData() {
    try {
      const res = await fetch(this.mapDataUrl, { cache: 'no-store' });
      if (!res.ok) throw new Error(`Failed to load map data: ${res.status}`);

      const data = await res.json();
      this.renderSummary(data.metadata || {});
      this.renderMarkers(data.features || []);
      this.renderDesignChainSpans(data.design_chain_spans || []);
    } catch (err) {
      console.error(err);
      if (this.issueNoteEl) {
        this.issueNoteEl.textContent = `Map data failed to load: ${err.message || err}`;
      }
    }
  }

  renderSummary(meta) {
    this.fileType = meta.file_type || 'structured';
    if (this.poleCountEl) this.poleCountEl.textContent = meta.pole_count ?? 0;
    if (this.passCountEl) this.passCountEl.textContent = meta.pass_count ?? 0;
    if (this.warnCountEl) this.warnCountEl.textContent = meta.warn_count ?? 0;
    if (this.failCountEl) this.failCountEl.textContent = meta.fail_count ?? 0;
    if (this.issueCountEl) this.issueCountEl.textContent = meta.issue_count ?? 0;
    if (this.rulepackBadgeEl) this.rulepackBadgeEl.textContent = meta.rulepack_id || 'Unknown';
    if (this.autoNormalizedEl) this.autoNormalizedEl.textContent = meta.auto_normalized ? 'Yes' : 'No';

    if (this.issueNoteEl) {
      if ((meta.issue_count ?? 0) > 0) {
        this.issueNoteEl.textContent = 'This job contains flagged issues. Click markers to inspect record details, then use the PDF for the full issue list.';
      } else {
        this.issueNoteEl.textContent = 'No issues recorded for this job.';
      }
    }

    // Framing line: "N review signals: W warn, F fail" — shown below the status grid.
    const frameSummaryEl = document.getElementById('frame-summary');
    if (frameSummaryEl) {
      const totalSignals = (meta.warn_count ?? 0) + (meta.fail_count ?? 0);
      if (totalSignals > 0) {
        const parts = [];
        if ((meta.warn_count ?? 0) > 0) parts.push(`${meta.warn_count} warn`);
        if ((meta.fail_count ?? 0) > 0) parts.push(`${meta.fail_count} fail`);
        frameSummaryEl.textContent = `${totalSignals} review signal${totalSignals !== 1 ? 's' : ''}: ${parts.join(', ')}`;
        frameSummaryEl.style.display = 'block';
      } else {
        frameSummaryEl.style.display = 'none';
      }
    }

    // File composition breakdown — structural / context / anchor counts.
    const roleEl = document.getElementById('role-breakdown');
    if (roleEl) {
      const parts = [];
      if (meta.structural_count != null) parts.push(`<span style="color:#2e8b57;">■ ${meta.structural_count} structural</span>`);
      if (meta.context_count != null && meta.context_count > 0) parts.push(`<span style="color:#9ca3af;">■ ${meta.context_count} context</span>`);
      if (meta.third_party_count != null && meta.third_party_count > 0) parts.push(`<span style="color:#b45309;">■ ${meta.third_party_count} third-party</span>`);
      if (meta.anchor_count != null && meta.anchor_count > 0) parts.push(`<span style="color:#6b7280;">◇ ${meta.anchor_count} anchor</span>`);
      roleEl.innerHTML = parts.join('<span style="margin:0 5px;color:#d1d5db;">·</span>');
      roleEl.style.display = parts.length > 0 ? 'block' : 'none';
    }
  }

  renderMarkers(features) {
    const bounds = [];

    for (const feature of features) {
      const geometry = feature.geometry || {};
      const props = feature.properties || {};
      const coords = geometry.coordinates || [];

      if (geometry.type !== 'Point' || coords.length < 2) continue;

      const lon = coords[0];
      const lat = coords[1];
      bounds.push([lat, lon]);

      const status = (props.qa_status || 'PASS').toUpperCase();
      const assetMarker = this.getAssetMarker(props);
      const lifecycleClass = this.lifecycleMarkerClass(props);
      const sourceClass = this.sourceConfidenceMarkerClass(props);
      const isAngle = this.isAnglePole(props);
      const markerSize = MARKER_SIZES[isAngle ? 'angle' : assetMarker.type] || MARKER_SIZES.other;

      const marker = L.marker([lat, lon], {
        icon: L.divIcon({
          className: `asset-marker status-${status} asset-${assetMarker.type} ${lifecycleClass} ${sourceClass}${isAngle ? ' is-angle' : ''}`,
          html: `<span class="asset-marker-shape" title="${this.escapeHtml(assetMarker.title)}"><span class="asset-marker-label">${this.escapeHtml(assetMarker.label)}</span>${isAngle ? '<span class="asset-marker-angle-badge">A</span>' : ''}</span>`,
          iconSize: [markerSize, markerSize],
          iconAnchor: [Math.round(markerSize / 2), Math.round(markerSize / 2)],
          popupAnchor: [0, -Math.round(markerSize / 2)],
        }),
      });

      const locName = props.name && props.name !== props.id ? props.name : null;
      const hasEasting = props.easting != null && props.easting !== '';
      const coordLine = hasEasting
        ? `<div class="popup-row" style="font-size:0.85em"><strong>E/N:</strong> ${this.escapeHtml(props.easting)}, ${this.escapeHtml(props.northing)}</div>`
        : `<div class="popup-row" style="font-size:0.85em"><strong>Lat/Lon:</strong> ${lat.toFixed(5)}, ${lon.toFixed(5)}</div>`;

      const isContext = this.isContextRecord(props);
      const isExisting = this.isExistingPole(props);
      const isProposed = this.isProposedPole(props);
      const hasHeight = this.hasValue(props.height);
      const hasSpecification = this.hasValue(props.specification) || this.hasValue(props.material);

      // Blank fields do not mean the same thing for every asset type. Existing
      // poles need measured height; proposed poles need a design specification.
      const heightLine = !isContext && hasHeight
        ? `<div class="popup-row"><strong>Height:</strong> ${this.escapeHtml(props.height)}m</div>`
        : '';

      const missingExistingHeightLine = isExisting && !hasHeight
        ? '<div class="popup-row" style="color:#b91c1c;font-weight:700;">⚠️ Measured height missing — clearance check impossible</div>'
        : '';

      const missingProposedSpecLine = isProposed && !hasSpecification
        ? '<div class="popup-row" style="color:#92400e;font-weight:700;">Proposed pole specification required (e.g., 11m Medium Pole)</div>'
        : '';

      const contextLine = isContext
        ? `<div class="popup-row" style="color:#6b7280;font-size:0.85em;">${this.escapeHtml(this.contextReviewLabel(props))}</div>`
        : '';

      const stayEvidenceLine = this.isAnglePole(props)
        ? this.stayEvidenceLine(props)
        : '';

      const materialLine = props.material != null && props.material !== ''
        ? `<div class="popup-row"><strong>Material:</strong> ${this.escapeHtml(props.material)}</div>`
        : '';

      const specificationLine = props.specification != null && props.specification !== ''
        ? `<div class="popup-row"><strong>Specification:</strong> ${this.escapeHtml(props.specification)}</div>`
        : '';

      const issueTexts = props.issue_texts || [];
      const issueBlock = props.issue_count > 0
        ? `<div class="popup-row" style="color:#d94141;font-weight:600;margin-top:4px;">Issues (${props.issue_count}):</div>
           ${issueTexts.map(t => `<div class="popup-row" style="color:#b91c1c;font-size:0.8em;margin-left:6px;">• ${this.escapeHtml(t)}</div>`).join('')}
           ${props.issue_count > issueTexts.length ? `<div class="popup-row" style="color:#b91c1c;font-size:0.8em;margin-left:6px;">… and ${props.issue_count - issueTexts.length} more</div>` : ''}`
        : '';

      const replacementLine = props.relationship === 'replacement_pair'
        ? '<div class="popup-row" style="color:#92400e;font-weight:600;margin-top:4px;">Suggested replacement link — unconfirmed. Review pairing page to confirm.</div>'
        : '';

      const assetIntentLine = props.asset_intent
        ? `<div class="popup-row" style="color:#9ca3af;font-size:0.85em;margin-top:1px;"><em>Asset role: ${this.escapeHtml(props.asset_intent)}</em></div>`
        : '';

      const lifecycleLine = props.lifecycle_state
        ? `<div class="popup-row" style="margin-top:4px;"><strong>Lifecycle:</strong> ${this.escapeHtml(props.lifecycle_state)}</div>`
        : '';

      const replacingLine = props.replacing
        ? `<div class="popup-row"><strong>Replacing:</strong> Point ${this.escapeHtml(props.replacing)}</div>`
        : '';

      const beingReplacedLine = props.being_replaced_by
        ? `<div class="popup-row"><strong>Being replaced by:</strong> Point ${this.escapeHtml(props.being_replaced_by)}</div>`
        : '';

      // General WARN block — shown for WARN features that are not replacement pairs
      // (replacement pairs have their own dedicated replacementLine above).
      const warnTexts = props.warn_texts || [];
      const warnBlock = (props.warn_count > 0 && props.relationship !== 'replacement_pair')
        ? `<div class="popup-row" style="color:#d39e00;font-weight:600;margin-top:4px;">&#9888; Design Note${props.warn_count > 1 ? 's' : ''} (${props.warn_count}):</div>
           ${warnTexts.map(t => `<div class="popup-row" style="color:#92400e;font-size:0.8em;margin-left:6px;">&#8226; ${this.escapeHtml(t)}</div>`).join('')}`
        : '';

      const idLabel = this.fileType === 'controller' ? 'Point no.' : 'Record ID';
      const explainedType = props.structure_type != null ? this.explainAssetType(props.structure_type) : null;

      const popupHtml = `
        <div class="popup-title">${this.escapeHtml(props.name || props.id || 'Record')}</div>
        <div class="popup-row"><strong>Status:</strong> ${this.statusBadge(status)}</div>
        ${props.pole_id != null ? `<div class="popup-row"><strong>${idLabel}:</strong> ${this.escapeHtml(props.pole_id)}</div>` : ''}
        ${props.structure_type != null ? `<div class="popup-row"><strong>Type:</strong> ${this.escapeHtml(props.structure_type)}</div>` : ''}
        ${explainedType ? `<div class="popup-row" style="color:#6b7280;font-size:0.83em;padding-left:8px;">${this.escapeHtml(explainedType)}</div>` : ''}
        ${assetIntentLine}
        ${lifecycleLine}
        ${replacingLine}
        ${beingReplacedLine}
        ${heightLine}
        ${materialLine}
        ${specificationLine}
        ${missingExistingHeightLine}
        ${missingProposedSpecLine}
        ${contextLine}
        ${stayEvidenceLine}
        ${locName ? `<div class="popup-row"><strong>Remarks:</strong> ${this.escapeHtml(locName)}</div>` : ''}
        ${coordLine}
        ${replacementLine}
        ${warnBlock}
        ${issueBlock}
      `;

      marker.bindPopup(this.buildPopupHtml(props, status, lat, lon));
      this.featureData.push({ marker, status, lat, lon, props });
    }

    // Detect overlapping coordinates (to 4 decimal places).
    const coordCounts = {};
    for (const fd of this.featureData) {
      const key = `${fd.lat.toFixed(4)},${fd.lon.toFixed(4)}`;
      coordCounts[key] = (coordCounts[key] || 0) + 1;
    }
    const overlapCount = Object.values(coordCounts).filter(c => c > 1).length;
    if (overlapCount > 0 && this.issueNoteEl) {
      const note = document.createElement('div');
      note.style.marginTop = '6px';
      note.style.color = '#6b7280';
      note.textContent = `Note: ${overlapCount} location(s) have overlapping markers — zoom in to separate them.`;
      this.issueNoteEl.appendChild(note);
    }

    this.bindFilterButtons();
    this.bindFocusFilterButtons();
    this.bindLayerToggles();
    this.bindLifecycleMatchToggle();
    this.bindAllRecordsButton();
    this.renderLifecycleMatches();
    this.applyVisibility();

    if (bounds.length === 1) {
      this.map.setView(bounds[0], 13);
    } else if (bounds.length > 1) {
      this.map.fitBounds(bounds, { padding: [40, 40] });
    }
  }

  renderLifecycleMatches() {
    if (!this.map || this.featureData.length === 0) return;

    if (this.lifecycleMatchLayer) {
      this.lifecycleMatchLayer.clearLayers();
      this.map.removeLayer(this.lifecycleMatchLayer);
    }

    this.lifecycleMatchLayer = L.layerGroup();
    const byPoleId = new Map();
    for (const fd of this.featureData) {
      if (this.hasValue(fd.props.pole_id)) byPoleId.set(String(fd.props.pole_id), fd);
    }

    for (const fd of this.featureData) {
      if (!this.hasValue(fd.props.replacing)) continue;
      const existing = byPoleId.get(String(fd.props.replacing));
      if (!existing) continue;

      const line = L.polyline([[existing.lat, existing.lon], [fd.lat, fd.lon]], {
        color: '#94a3b8',
        weight: 1,
        opacity: 0.55,
        dashArray: '5 5',
        lineCap: 'round',
      });
      const offsetLine = fd.props.match_offset_m != null
        ? `<div class="popup-row"><strong>Offset:</strong> ${Number(fd.props.match_offset_m).toFixed(1)}m</div>`
        : '';
      line.bindPopup(`
        <div class="popup-title">Suggested Existing/Proposed Match</div>
        <div class="popup-row"><strong>Existing:</strong> Point ${this.escapeHtml(fd.props.replacing)}</div>
        <div class="popup-row"><strong>Proposed:</strong> Point ${this.escapeHtml(fd.props.pole_id || fd.props.id || 'Unknown')}</div>
        ${offsetLine}
        <div class="popup-row" style="color:#64748b;font-size:0.82em;margin-top:4px;">Suggested replacement link — unconfirmed. Review pairing page to confirm.</div>
      `);
      line.addTo(this.lifecycleMatchLayer);
    }

    const toggle = document.getElementById('lifecycle-match-toggle');
    if (!toggle || toggle.checked) {
      this.lifecycleMatchLayer.addTo(this.map);
    }
  }

  renderDesignChainSpans(spans) {
    if (!this.map || !Array.isArray(spans) || spans.length === 0) return;

    this.spanLayer = L.layerGroup();

    for (const span of spans) {
      const coords = span.coordinates || [];
      if (coords.length !== 2) continue;

      const from = coords[0];
      const to = coords[1];
      if (!Array.isArray(from) || !Array.isArray(to) || from.length < 2 || to.length < 2) {
        continue;
      }

      const line = L.polyline([from, to], {
        color: '#1d4ed8',
        weight: 5,
        opacity: 0.88,
        lineCap: 'round',
        lineJoin: 'round',
      });

      const label = this.spanLabel(span);
      if (label) {
        line.bindTooltip(label, {
          permanent: false,
          sticky: true,
          className: 'span-distance-label',
          opacity: 0.9,
        });
      }

      const popupHtml = `
        <div class="popup-title">Surveyed Route Sequence</div>
        <div class="popup-row"><strong>From:</strong> ${this.escapeHtml(span.from_point_id || span.from_design_pole_no || 'Unknown')}</div>
        <div class="popup-row"><strong>To:</strong> ${this.escapeHtml(span.to_point_id || span.to_design_pole_no || 'Unknown')}</div>
        ${span.distance_m != null ? `<div class="popup-row"><strong>Distance:</strong> ${Number(span.distance_m).toFixed(1)}m</div>` : ''}
      `;
      line.bindPopup(popupHtml);
      line.addTo(this.spanLayer);
    }

    if (this.layerState.spans) {
      this.spanLayer.addTo(this.map);
    }
  }

  spanLabel(span) {
    if (span.distance_m == null || Number.isNaN(Number(span.distance_m))) return '';
    return `${Number(span.distance_m).toFixed(1)}m`;
  }

  bindFilterButtons() {
    document.querySelectorAll('.status-filter-btn').forEach(btn => {
      btn.addEventListener('click', () => {
        this.setFilter('status', btn.dataset.filter);
      });
    });
  }

  bindFocusFilterButtons() {
    document.querySelectorAll('.focus-filter-btn').forEach(btn => {
      btn.addEventListener('click', () => {
        this.setFilter('focus', btn.dataset.focus);
      });
    });
  }

  bindLayerToggles() {
    document.querySelectorAll('input[data-layer]').forEach(input => {
      const layerName = input.dataset.layer;
      if (Object.prototype.hasOwnProperty.call(this.layerState, layerName)) {
        this.layerState[layerName] = input.checked;
      }
      input.addEventListener('change', () => {
        this.layerState[layerName] = input.checked;
        if (layerName === 'spans') {
          this.toggleLayer(this.spanLayer, input.checked);
        } else if (layerName === 'matches') {
          this.toggleLayer(this.lifecycleMatchLayer, input.checked);
        } else {
          this.applyVisibility();
        }
      });
    });
  }

  bindAllRecordsButton() {
    const btn = document.getElementById('all-records-btn');
    if (!btn) return;
    btn.addEventListener('click', () => {
      // Clear any active status filter without hiding the panel.
      if (this.activeFilter) {
        this.activeFilter = null;
        this.activeFilterMode = null;
        this.applyVisibility();
        document.querySelectorAll('.status-filter-btn').forEach(b => b.classList.remove('filter-active'));
        document.querySelectorAll('.focus-filter-btn').forEach(b => b.classList.remove('filter-active'));
        if (this.filterNoteEl) this.filterNoteEl.textContent = '';
      }
      this._showRecordPanel(this.featureData, `All Mapped Records (${this.featureData.length})`);
    });
  }

  bindLifecycleMatchToggle() {
    const toggle = document.getElementById('lifecycle-match-toggle');
    if (!toggle) return;
    toggle.addEventListener('change', () => {
      if (!this.lifecycleMatchLayer) return;
      this.layerState.matches = toggle.checked;
      if (toggle.checked) {
        this.lifecycleMatchLayer.addTo(this.map);
      } else if (this.map.hasLayer(this.lifecycleMatchLayer)) {
        this.map.removeLayer(this.lifecycleMatchLayer);
      }
    });
  }

  setFilter(mode, value) {
    if (this.activeFilterMode === mode && this.activeFilter === value) {
      this.activeFilter = null;
      this.activeFilterMode = null;
      this.applyVisibility();
      document.querySelectorAll('.status-filter-btn').forEach(btn => btn.classList.remove('filter-active'));
      document.querySelectorAll('.focus-filter-btn').forEach(btn => btn.classList.remove('filter-active'));
      if (this.filterNoteEl) this.filterNoteEl.textContent = '';
      this._hideRecordPanel();
    } else {
      this.activeFilter = value;
      this.activeFilterMode = mode;
      const filtered = this.filterFeatureData(mode, value);
      this.applyVisibility(filtered);
      document.querySelectorAll('.status-filter-btn').forEach(btn => {
        btn.classList.toggle('filter-active', mode === 'status' && btn.dataset.filter === value);
      });
      document.querySelectorAll('.focus-filter-btn').forEach(btn => {
        btn.classList.toggle('filter-active', mode === 'focus' && btn.dataset.focus === value);
      });
      const count = filtered.length;
      const label = this.filterLabel(mode, value);
      if (this.filterNoteEl) {
        const recordWord = count !== 1 ? 'records' : 'record';
        const contextNote = value === 'replacement-proximity'
          ? ' (map records, not reviewed pairing count)'
          : '';
        this.filterNoteEl.textContent = `Showing ${count} ${label} ${recordWord}${contextNote} — click again to reset`;
      }
      this._showRecordPanel(filtered, `${label} (${count})`);
    }
  }

  filterFeatureData(mode, value) {
    if (mode === 'status') {
      return this.featureData.filter(fd => fd.status === value);
    }
    if (value === 'design-blockers') {
      return this.featureData.filter(fd => fd.status === 'FAIL');
    }
    if (value === 'review-required') {
      return this.featureData.filter(fd => fd.status === 'WARN');
    }
    if (value === 'replacement-proximity') {
      return this.featureData.filter(fd => fd.props.relationship === 'replacement_pair');
    }
    if (value === 'missing-height') {
      return this.featureData.filter(fd => this.isExistingPole(fd.props) && !this.hasValue(fd.props.height));
    }
    if (value === 'existing-poles') {
      return this.featureData.filter(fd => this.isExistingPole(fd.props));
    }
    if (value === 'proposed-poles') {
      return this.featureData.filter(fd => this.isProposedPole(fd.props));
    }
    if (value === 'angle-poles') {
      return this.featureData.filter(fd => this.isAnglePole(fd.props));
    }
    if (value === 'stays-anchors') {
      return this.featureData.filter(fd => this.isStayOrAnchor(fd.props));
    }
    if (value === 'context-crossings') {
      return this.featureData.filter(fd => this.isContextRecord(fd.props));
    }
    if (value === 'missing-specification') {
      return this.featureData.filter(fd => (
        this.isProposedPole(fd.props)
        && !this.hasValue(fd.props.specification)
        && !this.hasValue(fd.props.material)
      ));
    }
    if (value === 'records-with-remarks') {
      return this.featureData.filter(fd => (
        this.hasValue(fd.props.name)
        && fd.props.name !== fd.props.id
        && fd.props.name !== fd.props.pole_id
      ));
    }
    if (value === 'angle-missing-stay') {
      return this.featureData.filter(fd => (
        this.isAnglePole(fd.props)
        && fd.props.stay_evidence_status === 'missing'
      ));
    }
    if (value === 'span-anomalies') {
      return this.featureData.filter(fd => this.hasSpanAnomaly(fd.props));
    }
    if (value === 'clearance-crossings') {
      return this.featureData.filter(fd => this.isClearanceCrossing(fd.props));
    }
    return this.featureData;
  }

  currentFilteredFeatureData() {
    if (!this.activeFilter) return this.featureData;
    return this.filterFeatureData(this.activeFilterMode, this.activeFilter);
  }

  applyVisibility(filteredItems = this.currentFilteredFeatureData()) {
    if (!this.map) return;
    const visibleRecords = new Set(filteredItems);
    for (const fd of this.featureData) {
      const shouldShow = visibleRecords.has(fd) && this.passesLayerState(fd);
      if (shouldShow) {
        if (!this.map.hasLayer(fd.marker)) fd.marker.addTo(this.map);
      } else if (this.map.hasLayer(fd.marker)) {
        this.map.removeLayer(fd.marker);
      }
    }
  }

  passesLayerState(fd) {
    const props = fd.props || {};
    if (this.isThirdPartyInfrastructure(props)) return this.layerState.thirdparty;
    if (this.isContextRecord(props)) return this.layerState.context;
    if (this.isStayOrAnchor(props)) return this.layerState.stays;
    if (this.isAnglePole(props) && !this.layerState.angle) return false;
    if (this.isExistingPole(props)) return this.layerState.existing;
    if (this.isProposedPole(props)) return this.layerState.proposed;
    return true;
  }

  toggleLayer(layer, shouldShow) {
    if (!this.map || !layer) return;
    if (shouldShow) {
      if (!this.map.hasLayer(layer)) layer.addTo(this.map);
    } else if (this.map.hasLayer(layer)) {
      this.map.removeLayer(layer);
    }
  }

  filterLabel(mode, value) {
    const labels = {
      PASS: 'Pass',
      WARN: 'Review Required',
      FAIL: 'Design Blocker',
      'design-blockers': 'Design Blocker',
      'review-required': 'Review Required',
      'replacement-proximity': 'Existing/Proposed Match',
      'missing-height': 'Missing existing height',
      'existing-poles': 'Existing pole',
      'proposed-poles': 'Proposed pole',
      'angle-poles': 'Angle pole',
      'stays-anchors': 'Stay / anchor',
      'context-crossings': 'Context / crossing',
      'missing-specification': 'Missing proposed specification',
      'angle-missing-stay': 'Angle pole missing stay evidence',
      'span-anomalies': 'Span anomaly',
      'clearance-crossings': 'Crossing requiring clearance check',
      'records-with-remarks': 'Record with remarks',
    };
    return labels[value] || value || mode;
  }

  hasValue(value) {
    return value != null && value !== '' && String(value).trim() !== '';
  }

  isContextRecord(props) {
    const role = String(props.record_role || '').toLowerCase();
    return role === 'context' || CONTEXT_FEATURE_CODES.has(props.structure_type || '');
  }

  isThirdPartyInfrastructure(props) {
    const primary = String(props.primary_type || '').toLowerCase();
    const role = String(props.record_role || '').toLowerCase();
    const intent = String(props.asset_intent || '').toLowerCase();
    return primary === 'third_party_infrastructure'
      || role === 'third_party'
      || intent === 'third_party_not_network';
  }

  hasSpanAnomaly(props) {
    const allText = [
      ...(props.issue_texts || []),
      ...(props.warn_texts || []),
    ].join(' ');
    return (
      allText.includes('Probable duplicate pole')
      || allText.includes('Probable missing intermediate pole')
      || allText.includes('Span very short')
      || allText.includes('Span unusually short')
      || allText.includes('Span borderline short')
      || allText.includes('Span too long')
    );
  }

  isClearanceCrossing(props) {
    const st = String(props.structure_type || '').toLowerCase();
    return (
      st.includes('road')
      || st.includes('track')
      || st.includes('xing')
      || st.includes('pline')
    );
  }

  contextReviewLabel(props) {
    const st = String(props.structure_type || '').toLowerCase();
    if (st.includes('road') || st.includes('track') || st.includes('xing') || st.includes('pline')) {
      return 'Road Crossing — Critical clearance check required';
    }
    if (st.includes('wall') || st.includes('fence') || st.includes('gate')) {
      return 'Wall/Fence — Access constraint';
    }
    if (st.includes('stream')) {
      return 'Stream — Environmental constraint';
    }
    return 'Access Constraint';
  }

  isExistingPole(props) {
    if (this.isThirdPartyInfrastructure(props)) return false;
    const st = String(props.structure_type || '').toLowerCase();
    const intent = String(props.asset_intent || '').toLowerCase();
    return st.includes('expole') || intent.includes('existing');
  }

  isProposedPole(props) {
    if (this.isThirdPartyInfrastructure(props)) return false;
    const st = String(props.structure_type || '').toLowerCase();
    const intent = String(props.asset_intent || '').toLowerCase();
    return st.includes('prpole') || st === 'pol' || st.includes('angle') || intent.includes('proposed');
  }

  isAnglePole(props) {
    const st = String(props.structure_type || '').toLowerCase();
    return st.includes('angle');
  }

  isStayOrAnchor(props) {
    const st = String(props.structure_type || '').toLowerCase();
    const role = String(props.record_role || '').toLowerCase();
    return role === 'anchor' || st.includes('stay') || st.includes('anchor');
  }

  stayEvidenceLine(props) {
    if (props.stay_evidence_status === 'missing') {
      return '<div class="popup-row" style="color:#92400e;font-weight:700;">⚠️ Angle pole — stay evidence not captured. Check field notes, photos or plan evidence.</div>';
    }
    if (props.stay_evidence_status === 'captured') {
      const stayTypes = Array.isArray(props.stay_types) && props.stay_types.length > 0
        ? props.stay_types.join(', ')
        : 'Stay evidence captured';
      const distanceText = props.nearest_stay_distance_m != null
        ? ` within ${Number(props.nearest_stay_distance_m).toFixed(1)}m`
        : '';
      return `<div class="popup-row" style="color:#166534;font-weight:600;">Stay evidence: ${this.escapeHtml(stayTypes)}${distanceText}</div>`;
    }
    return '';
  }

  buildPopupHtml(props, status, lat, lon) {
    const assetKind = this.popupAssetKind(props);
    const title = this.escapeHtml(props.name || props.id || 'Record');
    const sections = assetKind === 'thirdparty'
      ? this.thirdPartyPopupSections(props, status, lat, lon)
      : assetKind === 'context'
        ? this.contextPopupSections(props, status, lat, lon)
        : assetKind === 'stay'
          ? this.stayPopupSections(props, status, lat, lon)
          : assetKind === 'proposed'
            ? this.proposedPopupSections(props, status, lat, lon)
            : assetKind === 'angle'
              ? this.anglePopupSections(props, status, lat, lon)
              : this.existingPopupSections(props, status, lat, lon);
    return `
      <div class="asset-popup asset-popup-${assetKind}">
        <div class="popup-title">${title}</div>
        ${sections.map(section => this.popupSection(section.title, section.rows)).join('')}
      </div>
    `;
  }

  popupAssetKind(props) {
    if (this.isThirdPartyInfrastructure(props)) return 'thirdparty';
    if (this.isContextRecord(props)) return 'context';
    if (this.isStayOrAnchor(props)) return 'stay';
    if (this.isAnglePole(props)) return 'angle';
    if (this.isProposedPole(props)) return 'proposed';
    return 'existing';
  }

  existingPopupSections(props, status, lat, lon) {
    return [
      ...this.legacyDataWarningSections(props),
      ...this.heightEvidenceAlertSections(props),
      { title: 'Identity', rows: this.identityRows(props, status, 'Existing Pole') },
      { title: 'Physical', rows: this.physicalRows(props, 'existing') },
      { title: 'Electrical', rows: this.electricalRows(props) },
      { title: 'Mechanical', rows: this.mechanicalRows(props) },
      { title: 'Third-Party Attachments', rows: this.attachmentsRows(props) },
      { title: 'Location', rows: this.locationRows(props, lat, lon) },
      { title: 'Evidence', rows: this.evidenceRows(props) },
      { title: 'Source & Confidence', rows: this.sourceConfidenceRows(props) },
      { title: 'Lifecycle / Design', rows: this.lifecycleRows(props) },
      { title: 'QA / Review', rows: this.qaRows(props) },
    ];
  }

  legacyDataWarningSections(props) {
    const sourceConf = props.source_confidence_detail || {};
    if (sourceConf.provenance !== 'legacy_map_data') return [];
    return [
      {
        title: 'Legacy Map Data - Not Field Verified',
        rows: [
          this.popupRow(
            'Designer Action',
            'Field verification required before design or construction',
            'warning',
            'Geometry and attributes are from historical records and may be outdated.',
          ),
        ],
      },
    ];
  }

  heightEvidenceAlertSections(props) {
    const heightConf = props.height_confidence || {};
    if (!['warning', 'blocker', 'fail', 'review'].includes(heightConf.status)) {
      return [];
    }
    return [
      {
        title: 'Height Evidence',
        rows: [
          this.popupRow('Measured Height', this.hasValue(props.height) ? `${props.height}m` : 'not captured', heightConf.status),
          this.popupRow('Height Source', props.height_source || 'not captured', props.height_source ? 'info' : 'warning'),
          this.popupRow('Height Confidence', this.formatHeightConfidence(heightConf.level), heightConf.status, heightConf.warning),
        ],
      },
    ];
  }

  thirdPartyPopupSections(props, status, lat, lon) {
    return [
      {
        title: 'Third-Party Infrastructure',
        rows: [
          this.popupRow('Type', props.popup_type_label || 'Third-Party Infrastructure', 'warning'),
          this.popupRow('Owner', props.infrastructure_owner || 'unknown', 'warning'),
          this.popupRow(
            'Classification',
            'NOT part of electric network',
            'warning',
            'This asset is owned or maintained by a third party, not the DNO.',
          ),
        ],
      },
      { title: 'Identity', rows: this.identityRows(props, status, props.popup_type_label || 'Third-Party Infrastructure') },
      { title: 'Location', rows: this.locationRows(props, lat, lon) },
      { title: 'Evidence', rows: this.evidenceRows(props) },
      {
        title: 'Design Action',
        rows: [
          this.popupRow('Designer Action', 'EXCLUDE from electric network design', 'warning'),
          this.popupRow('Construction Impact', 'Note proximity for access/construction planning only', 'info'),
          this.popupRow('Wayleave / Coordination', 'May require third-party coordination if work nearby', 'info'),
        ],
      },
      { title: 'QA / Review', rows: this.qaRows(props) },
    ];
  }

  proposedPopupSections(props, status, lat, lon) {
    return [
      ...this.legacyDataWarningSections(props),
      { title: 'Identity', rows: this.identityRows(props, status, 'Proposed Pole') },
      { title: 'Specification', rows: this.specificationRows(props) },
      { title: 'Third-Party Attachments', rows: this.attachmentsRows(props) },
      { title: 'Design Requirements', rows: this.designRequirementRows(props) },
      { title: 'Location', rows: this.locationRows(props, lat, lon) },
      { title: 'Evidence', rows: this.evidenceRows(props) },
      { title: 'Source & Confidence', rows: this.sourceConfidenceRows(props) },
      { title: 'Lifecycle / Design', rows: this.lifecycleRows(props) },
      { title: 'QA / Review', rows: this.qaRows(props) },
    ];
  }

  anglePopupSections(props, status, lat, lon) {
    return [
      ...this.legacyDataWarningSections(props),
      { title: 'Identity', rows: this.identityRows(props, status, 'Angle Pole') },
      { title: 'Mechanical', rows: this.mechanicalRows(props, true) },
      { title: 'Third-Party Attachments', rows: this.attachmentsRows(props) },
      { title: 'Physical', rows: this.physicalRows(props, 'angle') },
      { title: 'Electrical', rows: this.electricalRows(props) },
      { title: 'Location', rows: this.locationRows(props, lat, lon) },
      { title: 'Evidence', rows: this.evidenceRows(props) },
      { title: 'Source & Confidence', rows: this.sourceConfidenceRows(props) },
      { title: 'Lifecycle / Design', rows: this.lifecycleRows(props) },
      { title: 'QA / Review', rows: this.qaRows(props) },
    ];
  }

  stayPopupSections(props, status, lat, lon) {
    return [
      { title: 'Identity', rows: this.identityRows(props, status, 'Stay / Anchor') },
      { title: 'Stay Details', rows: this.stayDetailRows(props) },
      { title: 'Location', rows: this.locationRows(props, lat, lon) },
      { title: 'Evidence', rows: this.evidenceRows(props) },
      { title: 'QA / Review', rows: this.qaRows(props) },
    ];
  }

  contextPopupSections(props, status, lat, lon) {
    return [
      ...this.legacyDataWarningSections(props),
      { title: 'Identity', rows: this.identityRows(props, status, 'Context / Crossing') },
      { title: 'Crossing Details', rows: this.crossingRows(props) },
      { title: 'Location', rows: this.locationRows(props, lat, lon) },
      { title: 'Evidence', rows: this.evidenceRows(props) },
      { title: 'Source & Confidence', rows: this.sourceConfidenceRows(props) },
      { title: 'QA / Review', rows: this.qaRows(props) },
    ];
  }

  identityRows(props, status, fallbackType) {
    return [
      this.popupRow('Point', props.pole_id || props.id),
      this.popupRow('Type', props.popup_type_label || this.explainAssetType(props.structure_type) || fallbackType),
      this.popupRow('Feature Code', props.structure_type),
      this.popupRow('Circuit ID', props.circuit_id || 'not captured', props.circuit_id ? 'ok' : 'info'),
      this.popupRow('Year Installed', props.year_installed || 'not captured', props.year_installed ? 'ok' : 'info'),
      this.popupRow('Function', this.isAnglePole(props) ? 'Angle' : props.record_role),
      this.popupRow('Status', this.statusText(status), this.statusToFieldStatus(status)),
      this.popupRow('Role', props.asset_intent || props.record_role || 'mapped survey record'),
    ];
  }

  physicalRows(props, mode) {
    const hasHeight = this.hasValue(props.height);
    const heightConf = props.height_confidence || {};
    return [
      this.popupRow(
        mode === 'proposed' ? 'Proposed Height' : 'Measured Height',
        hasHeight ? `${props.height}m` : 'not captured',
        heightConf.status || (hasHeight ? 'ok' : mode === 'existing' ? 'blocker' : 'info'),
        heightConf.warning || (mode === 'existing' && !hasHeight ? 'Clearance check impossible without measured existing pole height.' : ''),
      ),
      this.popupRow(
        'Height Source',
        props.height_source || 'not captured',
        props.height_source ? 'info' : 'warning',
        props.height_source
          ? this.explainHeightSource(props.height_source)
          : 'Height measurement method not recorded - reliability unknown',
      ),
      hasHeight
        ? this.popupRow(
          'Height Confidence',
          this.formatHeightConfidence(heightConf.level),
          heightConf.status || 'info',
          heightConf.level === 'high'
            ? 'Suitable for clearance calculations'
            : 'Verify before use in clearance calculations',
        )
        : null,
      this.popupRow('Pole Class', props.pole_class || 'not captured', props.pole_class ? 'ok' : 'review'),
      this.popupRow(
        'Material / Condition',
        `${this.displayValue(props.material)} / ${this.displayValue(props.condition)}`,
        props.material || props.condition ? 'ok' : 'review',
      ),
      this.popupRow(
        'Lean',
        props.lean_severity || props.lean_direction
          ? `${this.displayValue(props.lean_severity)} ${this.displayValue(props.lean_direction)}`.trim()
          : 'not captured',
        props.lean_severity || props.lean_direction ? 'warning' : 'info',
      ),
      this.popupRow('Defects', props.defect_type || 'not captured', props.defect_type ? 'warning' : 'info'),
      this.popupRow('Foundation', props.foundation_type || 'not captured', props.foundation_type ? 'ok' : 'info'),
    ].filter(Boolean);
  }

  explainHeightSource(source) {
    const normalized = String(source || '').toLowerCase().replace(/\s+/g, '_');
    const explanations = {
      measured_rtk: 'Survey-grade RTK GNSS measurement',
      measured_ppk: 'Post-processed kinematic GNSS measurement',
      measured_gnss: 'Standalone GNSS measurement',
      measured_tape: 'Tape/rangefinder ground measurement',
      estimated_visual: 'Visual estimate from surveyor',
      from_plan: 'Taken from existing plan/drawing',
      legacy_data: 'Inherited from legacy records',
      not_captured: 'Measurement method not recorded',
    };
    return explanations[normalized] || `Height source: ${source}`;
  }

  formatHeightConfidence(level) {
    const labels = {
      high: 'High confidence (survey-grade)',
      'medium-high': 'Medium-high confidence',
      medium: 'Medium confidence',
      low: 'Low confidence',
      missing: 'Missing',
      not_applicable: 'N/A (proposed pole)',
      unknown: 'Unknown',
    };
    return labels[level] || level || 'Unknown';
  }

  specificationRows(props) {
    const hasSpec = this.hasValue(props.specification) || this.hasValue(props.material);
    return [
      this.popupRow(
        'Specification',
        props.specification || 'not specified',
        hasSpec ? 'ok' : 'review',
        hasSpec ? '' : 'Design decision required; this is not a field-capture error.',
      ),
      this.popupRow('Pole Class', props.pole_class || 'not specified', props.pole_class ? 'ok' : 'review'),
      this.popupRow('Material', props.material || 'not specified', props.material ? 'ok' : 'review'),
      this.popupRow('Condition', props.condition || 'not applicable yet', 'info'),
      this.popupRow('Design Height', props.height ? `${props.height}m` : 'not yet specified', props.height ? 'ok' : 'review'),
    ];
  }

  electricalRows(props) {
    const equipment = Array.isArray(props.equipment) && props.equipment.length > 0
      ? props.equipment.join(', ')
      : props.equipment;
    return [
      this.popupRow('Line Voltage', props.voltage || 'not recorded', props.voltage ? 'ok' : 'info'),
      this.popupRow('Conductor Type', props.conductor_type || 'not recorded', props.conductor_type ? 'ok' : 'info'),
      this.popupRow('Phases', props.phase_count || 'not recorded', props.phase_count ? 'ok' : 'info'),
      this.popupRow('Mounted Equipment', equipment || 'none recorded', equipment ? 'ok' : 'info'),
      this.popupRow('Equipment Rating', props.equipment_rating || 'not recorded', props.equipment_rating ? 'ok' : 'info'),
    ];
  }

  mechanicalRows(props, prominent = false) {
    const stayStatus = props.stay_evidence_status;
    const stayTypes = Array.isArray(props.stay_types) && props.stay_types.length > 0
      ? props.stay_types.join(', ')
      : props.stay_type;
    return [
      this.popupRow(
        'Stay Evidence',
        stayStatus === 'captured' || props.stay_present
          ? `captured: ${stayTypes || props.stay_present || 'stay record'}`
          : 'not captured',
        stayStatus === 'captured' ? 'ok' : prominent ? 'warning' : 'info',
        stayStatus === 'captured'
          ? this.nearestStayDetail(props)
          : 'Angle pole — stay evidence not captured. Check field notes, photos or plan evidence.',
      ),
      this.popupRow('Stay Type', stayTypes || 'not captured', stayTypes ? 'ok' : 'info'),
      this.popupRow('Stay Bearing', props.stay_bearing || 'not captured', props.stay_bearing ? 'ok' : 'info'),
      this.popupRow('Anchor Details', props.anchor_details || 'not linked', props.anchor_details ? 'ok' : 'info'),
      this.popupRow('Route Deviation', props.route_deviation_deg ? `${props.route_deviation_deg}°` : 'not calculated', props.route_deviation_deg ? 'warning' : 'info'),
      this.popupRow('Action', prominent ? 'Verify stay configuration before design' : 'Check field notes if stay evidence is expected', prominent ? 'warning' : 'info'),
    ];
  }

  stayDetailRows(props) {
    return [
      this.popupRow('Type', props.structure_type || 'Stay / anchor'),
      this.popupRow('Linked Pole', props.linked_pole_id || 'not linked', props.linked_pole_id ? 'ok' : 'info'),
      this.popupRow('Direction', props.stay_bearing || 'not captured', props.stay_bearing ? 'ok' : 'info'),
      this.popupRow('Configuration', props.stay_configuration || 'not captured', props.stay_configuration ? 'ok' : 'info'),
      this.popupRow('Nearest Pole', this.nearestStayDetail(props) || 'not calculated', props.nearest_stay_distance_m ? 'ok' : 'info'),
    ];
  }

  designRequirementRows(props) {
    return [
      this.popupRow('Action Required', props.action_required || 'not captured', props.action_required ? 'warning' : 'info'),
      this.popupRow('Clearance', this.isClearanceCrossing(props) ? this.contextReviewLabel(props) : 'check route context / plans', 'info'),
      this.popupRow('Stay Required', this.isAnglePole(props) ? 'review angle/stay evidence' : 'not indicated by current data', this.isAnglePole(props) ? 'warning' : 'info'),
      this.popupRow('Access', props.access_constraint || 'check field notes / plans', 'info'),
      this.popupRow('Design Note', props.name && props.name !== props.id ? props.name : 'not captured', props.name && props.name !== props.id ? 'ok' : 'info'),
    ];
  }

  crossingRows(props) {
    return [
      this.popupRow('Priority', this.isClearanceCrossing(props) ? 'HIGH' : 'Review', this.isClearanceCrossing(props) ? 'warning' : 'info'),
      this.popupRow('Label', this.contextReviewLabel(props), this.isClearanceCrossing(props) ? 'warning' : 'info'),
      this.popupRow('Clearance Measured', props.clearance_measured || 'No', props.clearance_measured ? 'ok' : 'warning'),
      this.popupRow('Distance from Route', props.distance_from_route_m ? `${props.distance_from_route_m}m` : 'not calculated', 'info'),
      this.popupRow('Action', this.isClearanceCrossing(props) ? 'Measure statutory clearance to crossing surface' : 'Review site constraint before design', 'warning'),
    ];
  }

  locationRows(props, lat, lon) {
    return [
      this.popupRow('Easting / Northing', props.easting ? `${props.easting}, ${props.northing}` : 'not captured', props.easting ? 'ok' : 'info'),
      this.popupRow('Lat / Lon', `${lat.toFixed(5)}, ${lon.toFixed(5)}`, 'ok'),
      this.popupRow('Elevation', props.elevation != null && props.elevation !== '' ? `${props.elevation}m` : 'not captured', props.elevation ? 'ok' : 'info'),
      this.popupRow('GNSS Accuracy', props.gnss_accuracy || 'not captured', props.gnss_accuracy ? 'ok' : 'info'),
    ];
  }

  evidenceRows(props) {
    const photos = this.photoEvidenceText(props);
    return [
      this.popupRow('Surveyed By', props.surveyor || 'not captured', props.surveyor ? 'ok' : 'info'),
      this.popupRow('Survey Date', props.survey_date || 'not captured', props.survey_date ? 'ok' : 'info'),
      this.popupRow('GNSS Accuracy', props.gnss_accuracy || 'not captured', props.gnss_accuracy ? 'ok' : 'info'),
      this.popupRow('Photo Evidence', photos, photos === 'no linked photos' ? 'info' : 'ok'),
      this.popupRow('Source Confidence', props.source_confidence || 'raw survey export', 'info'),
      this.popupRow('Remarks', props.name && props.name !== props.id ? props.name : 'not captured', props.name && props.name !== props.id ? 'ok' : 'info'),
    ];
  }

  sourceConfidenceRows(props) {
    const sourceConf = props.source_confidence_detail || {};
    const confidence = sourceConf.confidence || 'unknown';
    return [
      this.popupRow(
        'Data Provenance',
        this.formatProvenance(sourceConf.provenance),
        this.getProvenanceStatus(confidence),
        sourceConf.designer_note || '',
      ),
      this.popupRow(
        'Confidence Level',
        this.formatSourceConfidence(confidence),
        this.getProvenanceStatus(confidence),
      ),
      this.popupRow(
        'Geometry Trust',
        this.formatGeometryTrust(sourceConf.geometry_trust),
        this.getProvenanceStatus(confidence),
      ),
      ...(sourceConf.warnings || []).map(warning => (
        this.popupRow('Warning', warning, 'warning')
      )),
    ];
  }

  attachmentsRows(props) {
    const attachments = props.attachments_detail || {};
    if (!attachments.has_attachments) {
      return [
        this.popupRow('Third-Party Attachments', 'None recorded', 'info'),
      ];
    }

    return [
      this.popupRow(
        'Attachments Present',
        `Yes (${attachments.attachment_count})`,
        'warning',
        'Third-party coordination may be required',
      ),
      ...(attachments.attachment_list || []).map(attachment => (
        this.popupRow(
          `${attachment.icon || ''} ${this.formatAttachmentType(attachment.type)}`.trim(),
          `Owner: ${attachment.owner || 'unknown'}`,
          'warning',
          attachment.impact || '',
        )
      )),
      this.popupRow(
        'Coordination Required',
        'Yes - notify third parties before pole work',
        'warning',
      ),
    ];
  }

  formatAttachmentType(type) {
    const labels = {
      telecoms: 'Telecoms',
      streetlight: 'Streetlight',
      customer_service: 'Customer Service',
      signage: 'Signage',
      cctv: 'CCTV / Security',
    };
    return labels[type] || type || 'Attachment';
  }

  formatProvenance(provenance) {
    const labels = {
      field_observed_rtk: 'Field Survey (RTK GNSS)',
      field_observed_gnss: 'Field Survey (Standalone GNSS)',
      field_observed: 'Field Survey',
      dno_gis_import: 'DNO GIS Import',
      legacy_map_data: 'Legacy Map Data',
      digitised_from_drawing: 'Digitised from Drawing',
      proposed_by_design: 'Design Proposal',
      inferred: 'Inferred / Calculated',
      unknown: 'Unknown Source',
    };
    return labels[provenance] || provenance || 'Unknown Source';
  }

  formatSourceConfidence(confidence) {
    const labels = {
      high: 'High',
      'medium-high': 'Medium-high',
      medium: 'Medium',
      low: 'Low',
      'n/a': 'N/A',
      unknown: 'Unknown',
    };
    return labels[confidence] || confidence || 'Unknown';
  }

  getProvenanceStatus(confidence) {
    if (confidence === 'high') return 'ok';
    if (confidence === 'medium-high' || confidence === 'medium') return 'info';
    if (confidence === 'low') return 'warning';
    return 'review';
  }

  formatGeometryTrust(trust) {
    const labels = {
      survey_grade: 'Survey-grade',
      mapping_grade: 'Mapping-grade',
      field_verified: 'Field-verified',
      gis_inherited: 'GIS inherited (verify if critical)',
      unverified: 'Unverified (field check required)',
      indicative: 'Indicative only',
      design_intent: 'Design proposal',
      estimated: 'Estimated',
      unknown: 'Unknown',
    };
    return labels[trust] || trust || 'Unknown';
  }

  lifecycleRows(props) {
    return [
      this.popupRow('Lifecycle', props.lifecycle_state || 'not classified', props.lifecycle_state ? 'ok' : 'info'),
      this.popupRow('Replacing', props.replacing ? `Point ${props.replacing}` : 'not linked', props.replacing ? 'warning' : 'info'),
      this.popupRow('Being Replaced By', props.being_replaced_by ? `Point ${props.being_replaced_by}` : 'not linked', props.being_replaced_by ? 'warning' : 'info'),
      this.popupRow('Match Status', props.relationship === 'replacement_pair' ? 'suggested, unconfirmed' : 'none', props.relationship === 'replacement_pair' ? 'warning' : 'info'),
      this.popupRow('Match Offset', props.match_offset_m != null ? `${Number(props.match_offset_m).toFixed(1)}m` : 'not applicable', 'info'),
      this.popupRow('Action', props.relationship === 'replacement_pair' ? 'Review pairing page to confirm or reassign' : 'No pairing action from current data', props.relationship === 'replacement_pair' ? 'warning' : 'info'),
    ];
  }

  qaRows(props) {
    const rows = [];
    if (props.warn_count > 0) {
      rows.push(this.popupRow('Review Notes', `${props.warn_count}`, 'warning', (props.warn_texts || []).join(' | ')));
    }
    if (props.issue_count > 0) {
      rows.push(this.popupRow('Design Blockers', `${props.issue_count}`, 'blocker', (props.issue_texts || []).join(' | ')));
    }
    if (rows.length === 0) rows.push(this.popupRow('QA Items', 'none recorded', 'ok'));
    return rows;
  }

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

  displayValue(value) {
    if (value == null || value === '' || (Array.isArray(value) && value.length === 0)) {
      return 'not captured';
    }
    if (Array.isArray(value)) return value.join(', ');
    return String(value);
  }

  statusText(status) {
    if (status === 'FAIL') return 'Design Blocker';
    if (status === 'WARN') return 'Review Required';
    return 'Pass';
  }

  statusToFieldStatus(status) {
    if (status === 'FAIL') return 'blocker';
    if (status === 'WARN') return 'warning';
    return 'ok';
  }

  nearestStayDetail(props) {
    if (props.nearest_stay_distance_m == null) return '';
    return `within ${Number(props.nearest_stay_distance_m).toFixed(1)}m`;
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

  _showRecordPanel(items, title) {
    const panelEl = document.getElementById('record-panel');
    const listEl = document.getElementById('record-list');
    const titleEl = document.getElementById('record-panel-title');
    if (!panelEl || !listEl) return;

    if (titleEl) titleEl.textContent = title;
    listEl.innerHTML = '';

    for (const fd of items) {
      const p = fd.props;
      const item = document.createElement('div');
      item.className = `record-item status-${fd.status}`;

      const idText = this.escapeHtml(String(p.pole_id || p.id || 'Record'));
      const typeText = p.structure_type ? this.escapeHtml(p.structure_type) : '—';
      const explainedType = p.structure_type ? this.explainAssetType(p.structure_type) : null;
      const statusColor = this.getMarkerColor(fd.status);

      const detailParts = [];
      if (p.height != null && p.height !== '') detailParts.push(`H: ${p.height}m`);
      if (p.material) detailParts.push(this.escapeHtml(p.material));
      if (p.name && p.name !== p.id && p.name !== p.pole_id) {
        detailParts.push(this.escapeHtml(String(p.name).substring(0, 30)));
      }
      const detailText = detailParts.join(' · ');

      const firstIssue = (p.issue_texts || [])[0] || '';
      const issueHtml = fd.status === 'FAIL' && firstIssue
        ? `<div style="color:#b91c1c;font-size:0.78em;margin-top:2px;">• ${this.escapeHtml(firstIssue.substring(0, 65))}</div>`
        : '';

      const firstWarn = (p.warn_texts || [])[0] || '';
      const warnHtml = fd.status === 'WARN' && firstWarn && p.relationship !== 'replacement_pair'
        ? `<div style="color:#92400e;font-size:0.78em;margin-top:2px;">&#9888; ${this.escapeHtml(firstWarn.substring(0, 65))}</div>`
        : '';

      const intentHtml = p.asset_intent
        ? `<div style="color:#9ca3af;font-size:0.75em;margin-top:1px;font-style:italic;">${this.escapeHtml(p.asset_intent)}</div>`
        : '';

      const missingHeightHtml = (this.isExistingPole(p) && !this.hasValue(p.height))
        ? '<div style="color:#b91c1c;font-size:0.75em;margin-top:1px;font-weight:700;">⚠️ Measured height missing — clearance check impossible</div>'
        : '';

      const missingSpecHtml = (
        this.isProposedPole(p)
        && !this.hasValue(p.specification)
        && !this.hasValue(p.material)
      )
        ? '<div style="color:#92400e;font-size:0.75em;margin-top:1px;font-weight:700;">Proposed pole specification required (e.g., 11m Medium Pole)</div>'
        : '';

      const contextHtml = this.isContextRecord(p)
        ? `<div style="color:#6b7280;font-size:0.75em;margin-top:1px;">${this.escapeHtml(this.contextReviewLabel(p))}</div>`
        : '';

      const spanAnomalyHtml = this.hasSpanAnomaly(p)
        ? '<div style="color:#b91c1c;font-size:0.75em;margin-top:1px;font-weight:700;">Span anomaly</div>'
        : '';

      const stayEvidenceHtml = this.isAnglePole(p)
        ? `<div style="font-size:0.75em;margin-top:1px;">${this.stayEvidenceLine(p)}</div>`
        : '';

      const replacementHtml = p.relationship === 'replacement_pair'
        ? '<div style="color:#92400e;font-size:0.75em;margin-top:1px;">Existing/proposed match signal</div>'
        : '';

      const explainedTypeHtml = explainedType
        ? `<div style="color:#9ca3af;font-size:0.73em;margin-top:1px;font-style:italic;">${this.escapeHtml(explainedType)}</div>`
        : '';

      item.innerHTML = `
        <div style="display:flex;justify-content:space-between;align-items:baseline;">
          <span style="font-weight:600;font-size:0.82rem;">${idText}</span>
          <span style="font-size:0.75rem;font-weight:700;color:${statusColor};">${fd.status}</span>
        </div>
        <div style="color:#6b7280;font-size:0.78rem;">${typeText}${detailText ? ' · ' + detailText : ''}</div>
        ${explainedTypeHtml}
        ${intentHtml}
        ${missingHeightHtml}
        ${missingSpecHtml}
        ${contextHtml}
        ${stayEvidenceHtml}
        ${spanAnomalyHtml}
        ${replacementHtml}
        ${issueHtml}
        ${warnHtml}
      `;

      item.addEventListener('click', () => {
        fd.marker.openPopup();
        this.map.setView([fd.lat, fd.lon], Math.max(this.map.getZoom(), 15));
      });

      listEl.appendChild(item);
    }

    panelEl.style.display = items.length > 0 ? 'block' : 'none';
  }

  _hideRecordPanel() {
    const panelEl = document.getElementById('record-panel');
    if (panelEl) panelEl.style.display = 'none';
  }

  getMarkerColor(status) {
    if (status === 'FAIL') return '#d94141';
    if (status === 'WARN') return '#d39e00';
    return '#2563eb';
  }

  getAssetMarker(props) {
    const st = String(props.structure_type || '').toLowerCase();
    const role = String(props.record_role || '').toLowerCase();
    const intent = String(props.asset_intent || '').toLowerCase();

    if (this.isThirdPartyInfrastructure(props)) {
      return { type: 'thirdparty', label: 'TP', title: 'Third-party infrastructure' };
    }
    if (st.includes('expole') || intent.includes('existing')) {
      return { type: 'existing', label: 'EX', title: 'Existing pole' };
    }
    if (st.includes('prpole') || st === 'pol' || st.includes('angle') || intent.includes('proposed')) {
      return { type: 'proposed', label: 'PR', title: 'Proposed pole' };
    }
    if (role === 'anchor' || st.includes('stay') || st.includes('anchor')) {
      return { type: 'anchor', label: 'ST', title: 'Stay / anchor' };
    }
    if (role === 'context' || CONTEXT_FEATURE_CODES.has(props.structure_type || '')) {
      return { type: 'context', label: 'CTX', title: 'Context / crossing record' };
    }
    return { type: 'other', label: 'R', title: 'Mapped survey record' };
  }

  lifecycleMarkerClass(props) {
    const state = String(props.lifecycle_state || '').toLowerCase();
    if (state.includes('being replaced') || state.includes('recovered')) {
      return 'lifecycle-recovered';
    }
    if (state.includes('proposed replacement')) {
      return 'lifecycle-proposed-replacement';
    }
    if (state.includes('proposed pole')) {
      return 'lifecycle-proposed';
    }
    if (state.includes('unmatched existing')) {
      return 'lifecycle-unmatched';
    }
    return 'lifecycle-standard';
  }

  sourceConfidenceMarkerClass(props) {
    const provenance = String(props.source_confidence_detail?.provenance || '').toLowerCase();
    return provenance === 'legacy_map_data' ? 'source-legacy-data' : '';
  }

  statusBadge(status) {
    if (status === 'FAIL') return '<span style="color:#d94141;font-weight:700;">Design Blocker</span>';
    if (status === 'WARN') return '<span style="color:#d39e00;font-weight:700;">Review Required</span>';
    return '<span style="color:#2e8b57;font-weight:700;">Pass</span>';
  }

  explainAssetType(st) {
    const map = {
      'EXpole': 'Existing pole (EXpole) being replaced',
      'expole': 'Existing pole (EXpole) being replaced',
      'EXPOLE': 'Existing pole (EXpole) being replaced',
      'PRpole': 'Proposed replacement pole',
      'prpole': 'Proposed replacement pole',
      'PRPOLE': 'Proposed replacement pole',
      'Pol': 'Proposed new pole',
      'pol': 'Proposed new pole',
      'POL': 'Proposed new pole',
      'Angle': 'Angle pole (structural)',
      'angle': 'Angle pole (structural)',
      'ANGLE': 'Angle pole (structural)',
      'Hedge': 'Hedge (environmental context)',
      'hedge': 'Hedge (environmental context)',
      'HEDGE': 'Hedge (environmental context)',
      'Tree': 'Tree (environmental context)',
      'tree': 'Tree (environmental context)',
      'TREE': 'Tree (environmental context)',
      'Gate': 'Gate (crossing context)',
      'gate': 'Gate (crossing context)',
      'GATE': 'Gate (crossing context)',
      'Track': 'Track (crossing context)',
      'track': 'Track (crossing context)',
      'TRACK': 'Track (crossing context)',
      'Stream': 'Stream / watercourse (crossing context)',
      'stream': 'Stream / watercourse (crossing context)',
      'STREAM': 'Stream / watercourse (crossing context)',
    };
    return map[st] || null;
  }

  escapeHtml(value) {
    return String(value)
      .replaceAll('&', '&amp;')
      .replaceAll('<', '&lt;')
      .replaceAll('>', '&gt;')
      .replaceAll('"', '&quot;')
      .replaceAll("'", '&#039;');
  }
}

document.addEventListener('DOMContentLoaded', () => {
  const viewer = new MapViewer();
  viewer.init();
});
