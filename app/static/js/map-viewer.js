const CONTEXT_FEATURE_CODES = new Set([
  'Hedge', 'hedge', 'HEDGE',
  'Tree', 'tree', 'TREE',
  'Wall', 'wall', 'WALL',
  'Fence', 'fence', 'FENCE',
  'Post', 'post', 'POST',
  'Gate', 'gate', 'GATE',
  'Track', 'track', 'TRACK',
  'Stream', 'stream', 'STREAM',
]);

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
    this.activeFilter = null;
    this.fileType = null;
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
      const color = this.getMarkerColor(status);
      const markerStyle = this.getMarkerStyle(status);

      const marker = L.circleMarker([lat, lon], {
        radius: markerStyle.radius,
        color: markerStyle.stroke,
        weight: markerStyle.weight,
        fillColor: color,
        fillOpacity: markerStyle.fillOpacity,
      });

      const locName = props.name && props.name !== props.id ? props.name : null;
      const hasEasting = props.easting != null && props.easting !== '';
      const coordLine = hasEasting
        ? `<div class="popup-row" style="font-size:0.85em"><strong>E/N:</strong> ${this.escapeHtml(props.easting)}, ${this.escapeHtml(props.northing)}</div>`
        : `<div class="popup-row" style="font-size:0.85em"><strong>Lat/Lon:</strong> ${lat.toFixed(5)}, ${lon.toFixed(5)}</div>`;

      const isContext = CONTEXT_FEATURE_CODES.has(props.structure_type || '');

      // For structural (non-context) features, show "not captured" when height is absent
      // so a designer can immediately see gaps without opening the issues list.
      const heightLine = !isContext
        ? (props.height != null && props.height !== ''
            ? `<div class="popup-row"><strong>Height:</strong> ${this.escapeHtml(props.height)}m</div>`
            : `<div class="popup-row" style="color:#9ca3af;font-size:0.85em;"><strong>Height:</strong> not captured</div>`)
        : '';

      const materialLine = props.material != null && props.material !== ''
        ? `<div class="popup-row"><strong>Material:</strong> ${this.escapeHtml(props.material)}</div>`
        : '';

      const issueTexts = props.issue_texts || [];
      const issueBlock = props.issue_count > 0
        ? `<div class="popup-row" style="color:#d94141;font-weight:600;margin-top:4px;">Issues (${props.issue_count}):</div>
           ${issueTexts.map(t => `<div class="popup-row" style="color:#b91c1c;font-size:0.8em;margin-left:6px;">• ${this.escapeHtml(t)}</div>`).join('')}
           ${props.issue_count > issueTexts.length ? `<div class="popup-row" style="color:#b91c1c;font-size:0.8em;margin-left:6px;">… and ${props.issue_count - issueTexts.length} more</div>` : ''}`
        : '';

      const replacementLine = props.relationship === 'replacement_pair'
        ? `<div class="popup-row" style="color:#d39e00;font-weight:600;margin-top:4px;">&#9888; Likely replacement pair &#8212; existing asset with nearby proposed support</div>`
        : '';

      const assetIntentLine = props.asset_intent
        ? `<div class="popup-row" style="color:#9ca3af;font-size:0.85em;margin-top:1px;"><em>Asset role: ${this.escapeHtml(props.asset_intent)}</em></div>`
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
        ${heightLine}
        ${materialLine}
        ${locName ? `<div class="popup-row"><strong>Remarks:</strong> ${this.escapeHtml(locName)}</div>` : ''}
        ${coordLine}
        ${replacementLine}
        ${warnBlock}
        ${issueBlock}
      `;

      marker.bindPopup(popupHtml);
      marker.addTo(this.map);
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
    this.bindAllRecordsButton();

    if (bounds.length === 1) {
      this.map.setView(bounds[0], 13);
    } else if (bounds.length > 1) {
      this.map.fitBounds(bounds, { padding: [40, 40] });
    }
  }

  renderDesignChainSpans(spans) {
    if (!this.map || !Array.isArray(spans) || spans.length === 0) return;

    this.spanLayer = L.layerGroup().addTo(this.map);

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
        <div class="popup-title">Design Chain Span</div>
        <div class="popup-row"><strong>From:</strong> ${this.escapeHtml(span.from_point_id || span.from_design_pole_no || 'Unknown')}</div>
        <div class="popup-row"><strong>To:</strong> ${this.escapeHtml(span.to_point_id || span.to_design_pole_no || 'Unknown')}</div>
        ${span.distance_m != null ? `<div class="popup-row"><strong>Distance:</strong> ${Number(span.distance_m).toFixed(1)}m</div>` : ''}
      `;
      line.bindPopup(popupHtml);
      line.addTo(this.spanLayer);
    }
  }

  spanLabel(span) {
    if (span.distance_m == null || Number.isNaN(Number(span.distance_m))) return '';
    return `${Number(span.distance_m).toFixed(1)}m`;
  }

  bindFilterButtons() {
    document.querySelectorAll('.status-filter-btn').forEach(btn => {
      btn.addEventListener('click', () => {
        this.setFilter(btn.dataset.filter);
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
        for (const fd of this.featureData) {
          if (!this.map.hasLayer(fd.marker)) fd.marker.addTo(this.map);
        }
        document.querySelectorAll('.status-filter-btn').forEach(b => b.classList.remove('filter-active'));
        if (this.filterNoteEl) this.filterNoteEl.textContent = '';
      }
      this._showRecordPanel(this.featureData, `All Mapped Records (${this.featureData.length})`);
    });
  }

  setFilter(status) {
    if (this.activeFilter === status) {
      this.activeFilter = null;
      for (const fd of this.featureData) {
        if (!this.map.hasLayer(fd.marker)) fd.marker.addTo(this.map);
      }
      document.querySelectorAll('.status-filter-btn').forEach(btn => btn.classList.remove('filter-active'));
      if (this.filterNoteEl) this.filterNoteEl.textContent = '';
      this._hideRecordPanel();
    } else {
      this.activeFilter = status;
      for (const fd of this.featureData) {
        if (fd.status === status) {
          if (!this.map.hasLayer(fd.marker)) fd.marker.addTo(this.map);
        } else {
          if (this.map.hasLayer(fd.marker)) this.map.removeLayer(fd.marker);
        }
      }
      document.querySelectorAll('.status-filter-btn').forEach(btn => {
        btn.classList.toggle('filter-active', btn.dataset.filter === status);
      });
      const filtered = this.featureData.filter(fd => fd.status === status);
      const count = filtered.length;
      if (this.filterNoteEl) {
        this.filterNoteEl.textContent = `Showing ${count} ${status} record${count !== 1 ? 's' : ''} — click again to reset`;
      }
      this._showRecordPanel(filtered, `${status} Records (${count})`);
    }
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
    return '#2e8b57';
  }

  getMarkerStyle(status) {
    if (status === 'FAIL') {
      return { radius: 7, stroke: '#ffffff', weight: 2, fillOpacity: 0.92 };
    }
    if (status === 'WARN') {
      return { radius: 6.5, stroke: '#ffffff', weight: 1.5, fillOpacity: 0.9 };
    }
    return { radius: 5, stroke: '#064e3b', weight: 0.7, fillOpacity: 0.78 };
  }

  statusBadge(status) {
    if (status === 'FAIL') return '<span style="color:#d94141;font-weight:700;">Design Blocker</span>';
    if (status === 'WARN') return '<span style="color:#d39e00;font-weight:700;">Review Required</span>';
    return '<span style="color:#2e8b57;font-weight:700;">PASS</span>';
  }

  explainAssetType(st) {
    const map = {
      'EXpole': 'Existing pole being replaced',
      'expole': 'Existing pole being replaced',
      'EXPOLE': 'Existing pole being replaced',
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
