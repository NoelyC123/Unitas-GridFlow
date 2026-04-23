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

    this.map = null;
    this.markers = [];
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
        fillOpacity: 0.9
      });

      const locName = props.name && props.name !== props.id ? props.name : null;
      const hasEasting = props.easting != null && props.easting !== '';
      const coordLine = hasEasting
        ? `<div class="popup-row" style="font-size:0.85em"><strong>E/N:</strong> ${this.escapeHtml(props.easting)}, ${this.escapeHtml(props.northing)}</div>`
        : `<div class="popup-row" style="font-size:0.85em"><strong>Lat/Lon:</strong> ${lat.toFixed(5)}, ${lon.toFixed(5)}</div>`;

      const popupHtml = `
        <div class="popup-title">${this.escapeHtml(props.name || props.id || 'Record')}</div>
        <div class="popup-row"><strong>Status:</strong> ${this.statusBadge(status)}</div>
        ${props.pole_id != null ? `<div class="popup-row"><strong>Pole ID:</strong> ${this.escapeHtml(props.pole_id)}</div>` : ''}
        ${props.structure_type != null ? `<div class="popup-row"><strong>Type:</strong> ${this.escapeHtml(props.structure_type)}</div>` : ''}
        ${props.height != null && props.height !== '' ? `<div class="popup-row"><strong>Height:</strong> ${this.escapeHtml(props.height)}m</div>` : ''}
        ${props.material != null && props.material !== '' ? `<div class="popup-row"><strong>Material:</strong> ${this.escapeHtml(props.material)}</div>` : ''}
        ${locName ? `<div class="popup-row"><strong>Remarks:</strong> ${this.escapeHtml(locName)}</div>` : ''}
        ${coordLine}
        ${props.issue_count > 0 ? `<div class="popup-row" style="color:#d94141;font-weight:600;">Issues: ${props.issue_count}</div>` : ''}
      `;

      marker.bindPopup(popupHtml);
      marker.addTo(this.map);
      this.markers.push(marker);
    }

    if (bounds.length === 1) {
      this.map.setView(bounds[0], 13);
    } else if (bounds.length > 1) {
      this.map.fitBounds(bounds, { padding: [40, 40] });
    }
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
