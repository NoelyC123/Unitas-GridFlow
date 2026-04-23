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
    this.mapEl = document.getElementById('map');

    this.poleCountEl = document.getElementById('pole-count');
    this.spanCountEl = document.getElementById('span-count');
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
    this.activeFilter = null;
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
      const res = await fetch(`/map/data/${this.jobId}`, { cache: 'no-store' });
      if (!res.ok) throw new Error(`Failed to load map data: ${res.status}`);

      const data = await res.json();
      this.renderSummary(data.metadata || {});
      this.renderMarkers(data.features || []);
    } catch (err) {
      console.error(err);
      if (this.issueNoteEl) {
        this.issueNoteEl.textContent = `Map data failed to load: ${err.message || err}`;
      }
    }
  }

  renderSummary(meta) {
    if (this.poleCountEl) this.poleCountEl.textContent = meta.pole_count ?? 0;
    if (this.spanCountEl) this.spanCountEl.textContent = meta.span_count ?? 0;
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

      const marker = L.circleMarker([lat, lon], {
        radius: 7,
        color: '#ffffff',
        weight: 2,
        fillColor: color,
        fillOpacity: 0.9,
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

      const popupHtml = `
        <div class="popup-title">${this.escapeHtml(props.name || props.id || 'Record')}</div>
        <div class="popup-row"><strong>Status:</strong> ${this.statusBadge(status)}</div>
        ${props.pole_id != null ? `<div class="popup-row"><strong>ID:</strong> ${this.escapeHtml(props.pole_id)}</div>` : ''}
        ${props.structure_type != null ? `<div class="popup-row"><strong>Type:</strong> ${this.escapeHtml(props.structure_type)}</div>` : ''}
        ${heightLine}
        ${materialLine}
        ${locName ? `<div class="popup-row"><strong>Remarks:</strong> ${this.escapeHtml(locName)}</div>` : ''}
        ${coordLine}
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
      this._showRecordPanel(this.featureData, `All Records (${this.featureData.length})`);
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

      item.innerHTML = `
        <div style="display:flex;justify-content:space-between;align-items:baseline;">
          <span style="font-weight:600;font-size:0.82rem;">${idText}</span>
          <span style="font-size:0.75rem;font-weight:700;color:${statusColor};">${fd.status}</span>
        </div>
        <div style="color:#6b7280;font-size:0.78rem;">${typeText}${detailText ? ' · ' + detailText : ''}</div>
        ${issueHtml}
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

  statusBadge(status) {
    if (status === 'FAIL') return '<span style="color:#d94141;font-weight:700;">FAIL</span>';
    if (status === 'WARN') return '<span style="color:#d39e00;font-weight:700;">WARN</span>';
    return '<span style="color:#2e8b57;font-weight:700;">PASS</span>';
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
