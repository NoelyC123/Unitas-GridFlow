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
    this.cableLayer = null;
    this.lifecycleMatchLayer = null;
    this.plannerAwarenessLayer = null;
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
      cables: true,
      plannerAwareness: true,
    };
    this._spanFeatureList = [];
    this._spanLineRefs = [];
    this._spanRouteGroups = [];
    this._activeRouteGroupIndex = null;
    this._spanCrossingFilterOnly = false;
    this._cableLineRefs = [];
    this._plannerAwarenessItems = [];
    this._awarenessMarkerRefs = [];
    this._reviewNavigationTargets = { blockers: [], review: [], gaps: [], awareness: [] };
    this._activeReviewTargetGroup = null;
    this._activeReviewTargetIndex = -1;
    this._focusedReviewTarget = null;
    try {
      const v = localStorage.getItem('gridflow_map_span_label_mode');
      const allowed = new Set(['hover', 'critical', 'crossing', 'review', 'all']);
      if (v === 'anomalies') {
        this._spanLabelMode = 'review';
      } else if (allowed.has(v)) {
        this._spanLabelMode = v;
      } else {
        this._spanLabelMode = 'hover';
      }
    } catch {
      this._spanLabelMode = 'hover';
    }
    this._spanLabelModeControlBound = false;
    this._mapMeta = {};
    /** @type {'provisional_route'|'survey_circuit'} */
    this._spanLayerOrigin = 'provisional_route';
    this._usedDesignChainSpanFallback = false;
    this._replacementDrawableLineCount = 0;
  }

  init() {
    if (!this.jobId || !this.mapEl) return;

    this.map = L.map('map').setView([54.55, -3.1], 10);

    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
      attribution: '&copy; OpenStreetMap contributors',
      maxZoom: 19,
    }).addTo(this.map);

    this.bindSpanLabelModeControl();
    this.bindReviewNavigationControls();
    this.loadData();
  }

  async loadData() {
    try {
      const res = await fetch(this.mapDataUrl, { cache: 'no-store' });
      if (!res.ok) throw new Error(`Failed to load map data: ${res.status}`);

      const data = await res.json();
      const meta = data.metadata || {};
      this._geometryTrust = String(meta.geometry_trust || 'HIGH').toUpperCase();
      this.renderSummary(meta);
      this.renderGeometryTrustBanner(this._geometryTrust);
      this._spanLayerOrigin = meta.span_layer_origin === 'survey_circuit' ? 'survey_circuit' : 'provisional_route';
      this._usedDesignChainSpanFallback = false;
      this.renderMarkers(data.features || []);
      this._fallbackDesignSpans = data.design_chain_spans || [];
      const spanFeatures = data.span_features || [];
      if (Array.isArray(spanFeatures) && spanFeatures.length > 0) {
        this.renderGeoJsonSpanFeatures(spanFeatures);
      } else {
        this._usedDesignChainSpanFallback = true;
        this._spanLayerOrigin = 'provisional_route';
        this.renderDesignChainSpans(this._fallbackDesignSpans);
      }
      this.renderPlannerAwareness(data.planner_awareness || []);
      const cableFeatures = data.cable_features || [];
      this.renderCableFeatures(Array.isArray(cableFeatures) ? cableFeatures : []);
      this.applyZeroCountLayerTruthfulness(meta);
      this.applyLayerAndFilterCounts(meta);
      this.syncSpanPanelHeading();
    } catch (err) {
      console.error(err);
      if (this.issueNoteEl) {
        this.issueNoteEl.textContent = `Map data failed to load: ${err.message || err}`;
      }
    }
  }

  renderGeometryTrustBanner(trust) {
    const el = document.getElementById('geometry-trust-banner');
    if (!el) return;
    el.className = 'issue-note';
    if (trust === 'LOW') {
      el.textContent = 'Geometry reliability LOW — verify before design use';
      el.classList.add('issue-note-fail');
      el.style.display = '';
    } else if (trust === 'MEDIUM') {
      el.textContent = 'Geometry may contain inconsistencies';
      el.classList.add('issue-note-warn');
      el.style.display = '';
    } else {
      el.style.display = 'none';
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
    const workspaceBlockersEl = document.getElementById('workspace-blocker-count');
    if (workspaceBlockersEl) workspaceBlockersEl.textContent = meta.fail_count ?? 0;
    const workspaceWarningsEl = document.getElementById('workspace-warning-count');
    if (workspaceWarningsEl) workspaceWarningsEl.textContent = meta.warn_count ?? 0;

    if (this.issueNoteEl) {
      this.issueNoteEl.classList.remove('issue-note-fail', 'issue-note-warn', 'issue-note-ok');
      if ((meta.fail_count ?? 0) > 0) {
        this.issueNoteEl.textContent = 'Design blockers are present. Start with blocker tiles or focused filters, then confirm the evidence in the popup and PDF review workspace.';
        this.issueNoteEl.classList.add('issue-note-fail');
      } else if ((meta.warn_count ?? 0) > 0) {
        this.issueNoteEl.textContent = 'Review-needed records are present. Use the focus groups to work through missing evidence, route checks, and lifecycle signals before sign-off.';
        this.issueNoteEl.classList.add('issue-note-warn');
      } else {
        this.issueNoteEl.textContent = 'No open blockers or review-required records are currently surfaced in this workspace.';
        this.issueNoteEl.classList.add('issue-note-ok');
      }
    }

    // Framing line: "N review signals: W warn, F fail" — shown below the status grid.
    const frameSummaryEl = document.getElementById('frame-summary');
    if (frameSummaryEl) {
      const totalSignals = (meta.warn_count ?? 0) + (meta.fail_count ?? 0);
      if (totalSignals > 0) {
        const parts = [];
        if ((meta.warn_count ?? 0) > 0) parts.push(`${meta.warn_count} review-needed`);
        if ((meta.fail_count ?? 0) > 0) parts.push(`${meta.fail_count} blocker`);
        frameSummaryEl.textContent = `${totalSignals} active review signal${totalSignals !== 1 ? 's' : ''}: ${parts.join(', ')}`;
        frameSummaryEl.style.display = 'block';
      } else {
        frameSummaryEl.style.display = 'none';
      }
    }

    const spanPanelMeta = document.getElementById('span-panel-meta');
    if (spanPanelMeta) {
      const n = meta.span_feature_count ?? 0;
      if (n > 0 || (meta.span_crossing_high_count ?? 0) > 0) {
        const bits = [`${n} span segment${n !== 1 ? 's' : ''}`];
        const hi = meta.span_crossing_high_count ?? 0;
        const med = meta.span_crossing_medium_count ?? 0;
        const lo = meta.span_crossing_low_count ?? 0;
        if (hi) bits.push(`<span class="span-meta-risk-high">${hi} high clearance context</span>`);
        if (med) bits.push(`<span class="span-meta-risk-med">${med} medium</span>`);
        if (lo) bits.push(`<span class="span-meta-risk-low">${lo} low</span>`);
        spanPanelMeta.innerHTML = bits.join(' · ');
      } else {
        spanPanelMeta.textContent = '';
      }
    }

    const cablePanelMeta = document.getElementById('cable-panel-meta');
    if (cablePanelMeta) {
      const nc = meta.cable_feature_count ?? 0;
      if (nc > 0) {
        cablePanelMeta.textContent = `${nc} underground cable segment${nc !== 1 ? 's' : ''} (dashed purple)`;
        cablePanelMeta.style.display = 'block';
      } else {
        cablePanelMeta.textContent = '';
        cablePanelMeta.style.display = 'none';
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
    this._mapMeta = { ...meta };
  }

  _resetLayerToggle(layerKey, hasRecords, disabledTitle) {
    const input = document.querySelector(`input[data-layer="${layerKey}"]`);
    const label = input ? input.closest('label') : null;
    if (hasRecords) {
      if (input) input.disabled = false;
      if (label) {
        label.classList.remove('layer-toggle-disabled');
        label.title = '';
      }
      return;
    }
    if (Object.prototype.hasOwnProperty.call(this.layerState, layerKey)) {
      this.layerState[layerKey] = false;
    }
    if (input) {
      input.checked = false;
      input.disabled = true;
    }
    if (label) {
      label.classList.add('layer-toggle-disabled');
      label.title = disabledTitle;
    }
  }

  _removeMapLayerIfPresent(layer) {
    if (layer && this.map && this.map.hasLayer(layer)) {
      this.map.removeLayer(layer);
    }
  }

  /**
   * Grey out and uncheck layers that have nothing to show (truthful toggles).
   * Replacement links stay enabled when match *records* exist even if no line geometry.
   */
  applyZeroCountLayerTruthfulness(meta) {
    const lc = {
      existing: 0, proposed: 0, stays: 0, thirdparty: 0, context: 0,
    };
    for (const fd of this.featureData) {
      const k = this.primaryLayerKey(fd.props);
      if (k && Object.prototype.hasOwnProperty.call(lc, k)) lc[k] += 1;
    }
    const m = meta || this._mapMeta || {};
    const spanN = Number(m.span_feature_count ?? this._spanFeatureList?.length ?? 0);
    const cabN = Number(m.cable_feature_count ?? 0);
    const awarenessN = Number(m.planner_awareness_count ?? 0);
    const matchRecN = this.featureData.filter((fd) => this.hasValue(fd.props.replacing)).length;
    const angleN = this.angleHighlightCount();

    this._resetLayerToggle('existing', lc.existing >= 1, 'No existing pole records in this job.');
    this._resetLayerToggle('proposed', lc.proposed >= 1, 'No proposed pole records in this job.');
    this._resetLayerToggle('angle', angleN >= 1, 'No angle pole highlights in this job.');
    this._resetLayerToggle('stays', lc.stays >= 1, 'No stay or anchor structure records in this job.');
    this._resetLayerToggle('thirdparty', lc.thirdparty >= 1, 'No third-party infrastructure records in this job.');
    this._resetLayerToggle('context', lc.context >= 1, 'No context / crossing records in this job.');
    this._resetLayerToggle('spans', spanN >= 1, 'No route span segments for this job.');
    this._resetLayerToggle(
      'cables',
      cabN >= 1,
      'No underground cable segments in survey data (not inferred from pole records).',
    );
    this._resetLayerToggle(
      'matches',
      matchRecN >= 1,
      'No suggested replacement links in record data (no replacing references).',
    );
    this._resetLayerToggle(
      'plannerAwareness',
      awarenessN >= 1,
      'No planner awareness notes for this job.',
    );

    if (cabN < 1) this._removeMapLayerIfPresent(this.cableLayer);
    if (spanN < 1) this._removeMapLayerIfPresent(this.spanLayer);
    if (matchRecN < 1) this._removeMapLayerIfPresent(this.lifecycleMatchLayer);
    if (awarenessN < 1) this._removeMapLayerIfPresent(this.plannerAwarenessLayer);
  }

  primaryLayerKey(props) {
    if (this.isThirdPartyInfrastructure(props)) return 'thirdparty';
    if (this.isContextRecord(props)) return 'context';
    if (this.isStayOrAnchor(props)) return 'stays';
    if (this.isExistingPole(props)) return 'existing';
    if (this.isProposedPole(props)) return 'proposed';
    return null;
  }

  applyLayerAndFilterCounts(meta) {
    const lc = {
      existing: 0, proposed: 0, stays: 0, thirdparty: 0, context: 0,
    };
    for (const fd of this.featureData) {
      const k = this.primaryLayerKey(fd.props);
      if (k && Object.prototype.hasOwnProperty.call(lc, k)) lc[k] += 1;
    }
    const m = meta || this._mapMeta || {};
    const spanN = Number(m.span_feature_count ?? this._spanFeatureList?.length ?? 0);
    const cabN = Number(m.cable_feature_count ?? 0);
    const awarenessN = Number(m.planner_awareness_count ?? 0);
    document.querySelectorAll('label.layer-toggle[data-layer-key]').forEach((lab) => {
      const key = lab.dataset.layerKey;
      const cap = lab.querySelector('.layer-toggle-caption');
      if (!cap) return;
      const raw = cap.textContent.replace(/\s*\(\d+\)\s*$/, '').trim();
      cap.textContent = raw;
      if (key === 'spans') {
        const base = this._spanLayerOrigin === 'survey_circuit'
          ? 'Circuit spans (line)'
          : 'Provisional route spans (line)';
        cap.textContent = `${base} (${spanN})`;
        return;
      }
      if (key === 'cables') {
        cap.textContent = `${raw} (${cabN})`;
        return;
      }
      if (key === 'plannerAwareness') {
        cap.textContent = `${raw} (${awarenessN})`;
        return;
      }
      if (key === 'angle') {
        const angleN = this.angleHighlightCount();
        cap.textContent = `${raw} (${angleN})`;
        if (angleN > 0) {
          lab.title = 'Angle highlights are derived from structural pole records; toggling them only hides or shows the A badge, not the pole record.';
        }
        return;
      }
      if (key === 'matches') {
        const matchRec = this.featureData.filter((fd) => this.hasValue(fd.props.replacing)).length;
        const lines = this._replacementDrawableLineCount ?? 0;
        cap.textContent = `${raw} (${matchRec} rec · ${lines} on map)`;
        if (lab) {
          lab.title = matchRec > 0 && lines === 0
            ? 'EX/PR match records are present, but dashed link lines only appear when both supports exist on the map with a resolved pair.'
            : '';
        }
        return;
      }
      const c = lc[key];
      if (c != null) cap.textContent = `${raw} (${c})`;
    });

    const focusDefs = [
      ['design-blockers', () => this.filterFeatureData('focus', 'design-blockers').length],
      ['review-required', () => this.filterFeatureData('focus', 'review-required').length],
      ['missing-height', () => this.filterFeatureData('focus', 'missing-height').length],
      ['missing-specification', () => this.filterFeatureData('focus', 'missing-specification').length],
      ['angle-missing-stay', () => this.filterFeatureData('focus', 'angle-missing-stay').length],
      ['span-anomalies', () => this.filterFeatureData('focus', 'span-anomalies').length],
      ['span-crossing-risk', () => this._spanLineRefs.filter(({ props }) => {
        const r = String(props.crossing_risk_level || 'none').toLowerCase();
        return r !== 'none' && r !== '';
      }).length],
      ['ug-cable-missing-spec', () => this.filterFeatureData('focus', 'ug-cable-missing-spec').length],
      ['clearance-crossings', () => this.filterFeatureData('focus', 'clearance-crossings').length],
      ['replacement-proximity', () => this.filterFeatureData('focus', 'replacement-proximity').length],
      ['records-with-remarks', () => this.filterFeatureData('focus', 'records-with-remarks').length],
    ];
    for (const [focus, fn] of focusDefs) {
      const btn = document.querySelector(`.focus-filter-btn[data-focus="${focus}"]`);
      if (!btn) continue;
      const cap = btn.querySelector('.focus-filter-caption');
      if (!cap) continue;
      const raw = cap.textContent.replace(/\s*\(\d+\)\s*$/, '').trim();
      let n = 0;
      try {
        n = fn();
      } catch {
        n = 0;
      }
      cap.textContent = `${raw} (${n})`;
      btn.style.display = n > 0 ? '' : 'none';
    }
  }

  _spanEndpointHasReplacementHint(fromId, toId) {
    const ids = [String(fromId || ''), String(toId || '')].filter(Boolean);
    if (!ids.length || !this.featureData.length) return false;
    for (const fd of this.featureData) {
      const pid = String(fd.props.pole_id || fd.props.id || '').trim();
      if (!pid || !ids.includes(pid)) continue;
      if (fd.props.relationship === 'replacement_pair' || this.hasValue(fd.props.replacing)) {
        return true;
      }
    }
    return false;
  }

  /** Likely explanation when distance_m is very short (< 12 m). */
  classifyShortLikelySpanCause(props) {
    const dm = props.distance_m != null ? Number(props.distance_m) : NaN;
    if (Number.isNaN(dm) || dm >= 12) return null;
    const txt = [...(props.issue_texts || []), ...(props.warn_texts || [])].join(' ').toLowerCase();
    if (txt.includes('duplicate')) {
      return { tag: 'Possible duplicate capture', detail: 'Multiple points may represent the same structure.' };
    }
    if (txt.includes('missing intermediate')) {
      return { tag: 'Possible sequence issue', detail: 'Route order may skip an intermediate support.' };
    }
    if (this._spanEndpointHasReplacementHint(props.from_point_id, props.to_point_id)) {
      return {
        tag: 'Likely replacement / co-located pair',
        detail: 'Supports show EX/PR or replacement linkage — short separation may be expected.',
      };
    }
    if (dm >= 3) {
      return {
        tag: 'Possible genuine short span',
        detail: 'Distance is short but may be valid — confirm against survey notes or design.',
      };
    }
    return {
      tag: 'Uncertain',
      detail: 'Very short segment — verify point IDs, sequence, and field notes.',
    };
  }

  /** Remove designer-action lines that only repeat review-signal wording. */
  filterSpanDesignerActions(actions, causeStrings) {
    const norm = (s) => String(s).toLowerCase().replace(/\s+/g, ' ').trim();
    const causes = causeStrings.map(norm).filter(Boolean);
    return actions.filter((raw) => {
      const a = norm(raw);
      if (!a) return false;
      if (causes.some((c) => c.length >= 8 && (a.includes(c.slice(0, Math.min(40, c.length))) || c.includes(a.slice(0, Math.min(40, a.length)))))) {
        return false;
      }
      return true;
    });
  }

  condenseVacuousPopupRows(rows, summaryWhenAllEmpty) {
    const kept = rows.filter((r) => r && !this.isVacuousPopupRowHtml(r));
    if (kept.length === 0) {
      return [this.popupRow('Summary', summaryWhenAllEmpty, 'info')];
    }
    return kept;
  }

  /**
   * Rows where the value is only an empty placeholder and the row is not a blocker/warning status.
   */
  isVacuousPopupRowHtml(rowHtml) {
    if (!rowHtml || typeof rowHtml !== 'string') return false;
    if (rowHtml.includes('status-blocker') || rowHtml.includes('status-warning')) return false;
    return /popup-field-value">(?:—|not captured|not recorded(?: [^<]*)?|not supplied(?: [^<]*)?|evidence gap - [^<]+|none recorded|not specified|not specified yet|design decision pending|not linked(?: [^<]*)?|not applicable yet|not yet specified|not inferred|none inferred|none inferred from current fields|not parsed|no linked photos|no linked photo references in current export)(<\/div>)/i.test(rowHtml)
      && !rowHtml.includes('popup-field-detail');
  }

  syncSpanPanelHeading() {
    const el = document.getElementById('span-panel-heading');
    if (el) {
      el.textContent = this._spanLayerOrigin === 'survey_circuit' ? 'Circuit spans' : 'Provisional route spans';
    }
    const leg = document.getElementById('legend-span-line-caption');
    if (leg) {
      leg.textContent = this._spanLayerOrigin === 'survey_circuit'
        ? 'Circuit spans — hover line for distance; click for details.'
        : 'Provisional route spans (from sequenced supports) — hover for distance; click for details.';
    }
  }

  classifyRouteSpanAnomaly(props) {
    const causes = [];
    const dm = props.distance_m != null ? Number(props.distance_m) : NaN;
    const shortGuess = this.classifyShortLikelySpanCause(props);
    if (shortGuess) {
      causes.push(`Short span — ${shortGuess.tag}: ${shortGuess.detail}`);
    } else if (!Number.isNaN(dm) && dm < 12) {
      causes.push('Very short span — check IDs / sequence');
    }
    const r = String(props.crossing_risk_level || 'none').toLowerCase();
    if (r && r !== 'none') causes.push(`Crossing / route context: ${r}`);
    if (!Number.isNaN(dm)) {
      if (dm > 280) causes.push('Long span — verify intermediate supports & conductor');
    }
    const acts = Array.isArray(props.designer_suggested_actions) ? props.designer_suggested_actions : [];
    acts.forEach((a) => {
      const s = String(a);
      if (/very short span|long span|voltage|conductor|phase|obstruction|spot-check/i.test(s)) {
        if (!causes.some((c) => c.includes(s.slice(0, Math.min(20, s.length))))) causes.push(s);
      }
    });
    const allText = [...(props.issue_texts || []), ...(props.warn_texts || [])].join(' ');
    if (allText.includes('Span very short') || allText.includes('Span unusually short') || allText.includes('Span borderline short')) {
      if (!causes.some((c) => /short span/i.test(c))) causes.push('QA: short-span anomaly flag on record');
    }
    if (allText.includes('Span too long') || allText.includes('long span')) {
      causes.push('QA: long-span review');
    }
    if (allText.includes('duplicate pole')) causes.push('QA: possible duplicate structure');
    if (allText.includes('missing intermediate')) causes.push('QA: possible gap in route');
    const short = causes.length ? causes[0].split(' —')[0].split(':')[0].trim().slice(0, 42) : '';
    return { short: short || (causes.length ? 'Review span' : ''), causes };
  }

  spanIssueSeverityRank(severity) {
    const s = String(severity || 'INFO').toUpperCase();
    if (s === 'BLOCKER') return 3;
    if (s === 'REVIEW' || s === 'WARNING' || s === 'WARN' || s === 'HIGH' || s === 'MEDIUM') return 2;
    return 1;
  }

  spanIssueSeverityFromSignal(severity) {
    const s = String(severity || 'INFO').toUpperCase();
    if (s === 'BLOCKER' || s === 'BLOCKED' || s === 'FAIL' || s === 'CRITICAL') return 'BLOCKER';
    if (s === 'REVIEW' || s === 'WARNING' || s === 'WARN' || s === 'HIGH' || s === 'MEDIUM') return 'REVIEW';
    return 'INFO';
  }

  strongestSpanIssueSeverity(current, candidate) {
    return this.spanIssueSeverityRank(candidate) > this.spanIssueSeverityRank(current)
      ? (String(candidate || 'INFO').toUpperCase() === 'BLOCKER' ? 'BLOCKER' : 'REVIEW')
      : current;
  }

  spanAwarenessKeys(props) {
    const from = this.hasValue(props?.from_point_id) ? String(props.from_point_id) : '';
    const to = this.hasValue(props?.to_point_id) ? String(props.to_point_id) : '';
    const keys = new Set();
    if (this.hasValue(props?.span_id)) keys.add(String(props.span_id));
    if (from && to) {
      keys.add(`${from}->${to}`);
      keys.add(`${to}->${from}`);
    }
    return keys;
  }

  spanAwarenessItems(props) {
    const keys = this.spanAwarenessKeys(props);
    if (!keys.size || !Array.isArray(this._plannerAwarenessItems)) return [];
    return this._plannerAwarenessItems.filter((item) => keys.has(String(item?.related_span_id || '')));
  }

  classifyTextIssue(text, categories) {
    const s = String(text || '');
    if (!s) return false;
    let matched = false;
    if (/clearance|crossing|obstruction|road|stream|track|access/i.test(s)) {
      categories.add('CLEARANCE');
      matched = true;
    }
    if (/span|geometry|duplicate|sequence|intermediate|distance|route/i.test(s)) {
      categories.add('GEOMETRY');
      matched = true;
    }
    if (/stay|anchor|structure|pole|height|material|specification|spec\b/i.test(s)) {
      categories.add('STRUCTURAL');
      matched = true;
    }
    if (/voltage|conductor|phase|cable|circuit|electrical/i.test(s)) {
      categories.add('ELECTRICAL');
      matched = true;
    }
    if (/missing|unknown|confirm|verify|not captured|not available|gap|required|pending/i.test(s)) {
      categories.add('DATA');
      matched = true;
    }
    return matched;
  }

  classifySpanIssues(span) {
    const props = span?.properties || span?.props || span || {};
    const categories = new Set();
    let severity = 'INFO';
    const addIssue = (category, issueSeverity = 'REVIEW') => {
      if (category) categories.add(category);
      severity = this.strongestSpanIssueSeverity(severity, issueSeverity);
    };

    const designStatus = String(props.design_status || '').toUpperCase();
    if (designStatus === 'BLOCKED') addIssue('GEOMETRY', 'BLOCKER');
    else if (designStatus === 'REVIEW') severity = this.strongestSpanIssueSeverity(severity, 'REVIEW');
    if (props.design_usable === false) addIssue('GEOMETRY', 'BLOCKER');

    const sourceDetail = props.source_confidence_detail || {};
    const geometryTrust = String(props.geometry_trust || sourceDetail.geometry_trust || '').toLowerCase();
    if (geometryTrust === 'unverified') addIssue('GEOMETRY', 'REVIEW');

    const qaStatus = String(props.qa_status || '').toUpperCase();
    if (qaStatus === 'FAIL') addIssue('DATA', 'BLOCKER');
    else if (qaStatus === 'WARN') addIssue('DATA', 'REVIEW');

    const validity = String(props.span_validity || '').toLowerCase();
    if (validity === 'invalid') addIssue('GEOMETRY', 'BLOCKER');
    else if (validity === 'suspect') addIssue('GEOMETRY', 'REVIEW');

    const dm = props.distance_m != null ? Number(props.distance_m) : NaN;
    if (!Number.isNaN(dm)) {
      if (dm < 5) addIssue('GEOMETRY', 'BLOCKER');
      else if (dm < 12 || dm > 280) addIssue('GEOMETRY', 'REVIEW');
    }

    const crossingRisk = String(props.crossing_risk_level || 'none').toLowerCase();
    if (crossingRisk === 'blocker') addIssue('CLEARANCE', 'BLOCKER');
    else if (crossingRisk && crossingRisk !== 'none') addIssue('CLEARANCE', 'REVIEW');

    const reasonTypes = {
      clearance: 'CLEARANCE',
      geometry: 'GEOMETRY',
      geometry_cluster: 'GEOMETRY',
      geometry_trust: 'GEOMETRY',
      structural: 'STRUCTURAL',
      electrical: 'ELECTRICAL',
      data: 'DATA',
      evidence: 'DATA',
      source: 'DATA',
    };
    const reasons = Array.isArray(props.design_blocker_reasons) ? props.design_blocker_reasons : [];
    reasons.forEach((reason) => {
      const item = reason && typeof reason === 'object'
        ? reason
        : { type: 'legacy', severity: 'info', message: String(reason || '') };
      const type = String(item.type || '').toLowerCase();
      const category = reasonTypes[type] || null;
      if (category) categories.add(category);
      this.classifyTextIssue(item.message, categories);
      severity = this.strongestSpanIssueSeverity(severity, this.spanIssueSeverityFromSignal(item.severity));
    });

    const actions = Array.isArray(props.designer_suggested_actions) ? props.designer_suggested_actions : [];
    actions.forEach((action) => {
      if (this.classifyTextIssue(action, categories)) {
        severity = this.strongestSpanIssueSeverity(severity, 'REVIEW');
      }
    });

    const issueTexts = [
      ...(Array.isArray(props.issue_texts) ? props.issue_texts : []),
      ...(Array.isArray(props.warn_texts) ? props.warn_texts : []),
    ];
    issueTexts.forEach((text) => {
      if (this.classifyTextIssue(text, categories)) {
        const critical = /fail|blocker|invalid|impossible|duplicate pole/i.test(String(text || ''));
        severity = this.strongestSpanIssueSeverity(severity, critical ? 'BLOCKER' : 'REVIEW');
      }
    });

    ['missing_fields', 'missing_required_fields', 'evidence_gaps', 'field_gaps'].forEach((key) => {
      const value = props[key];
      const values = Array.isArray(value) ? value : (this.hasValue(value) ? [value] : []);
      values.forEach((item) => {
        categories.add('DATA');
        this.classifyTextIssue(item, categories);
        severity = this.strongestSpanIssueSeverity(severity, 'REVIEW');
      });
    });

    const awareness = this.spanAwarenessItems(props);
    awareness.forEach((item) => {
      this.classifyTextIssue(`${item.category || ''} ${item.message || ''}`, categories);
      severity = this.strongestSpanIssueSeverity(severity, this.spanIssueSeverityFromSignal(item.severity));
    });

    return { categories: [...categories], severity };
  }

  computeReviewSummary(spans) {
    const items = Array.isArray(spans) ? spans : [];
    const summary = {
      blockers: 0,
      review: 0,
      gaps: 0,
      verdict: 'PARTIALLY READY',
    };

    items.forEach((span) => {
      const issue = this.classifySpanIssues(span);
      if (issue.severity === 'BLOCKER') summary.blockers += 1;
      else if (issue.severity === 'REVIEW') summary.review += 1;
      if (issue.categories.includes('DATA')) summary.gaps += 1;
    });

    if (summary.blockers > 0) summary.verdict = 'NOT READY';
    else if (items.length > 0 && summary.review === 0 && summary.gaps === 0) summary.verdict = 'READY';

    return summary;
  }

  reviewVerdictStatusClass(verdict) {
    if (verdict === 'READY') return 'status-ok';
    if (verdict === 'NOT READY') return 'status-fail';
    return 'status-warn';
  }

  renderReviewIntelligenceSummary() {
    const spans = (this._spanLineRefs || []).map((ref) => ref.props || {});
    const summary = this.computeReviewSummary(spans);
    this._reviewNavigationTargets = this.buildReviewNavigationTargets();
    const updates = [
      ['workspace-blocker-count', summary.blockers],
      ['workspace-warning-count', summary.review],
      ['workspace-gap-count', summary.gaps],
      ['workspace-awareness-count', this._reviewNavigationTargets.awareness.length],
    ];
    updates.forEach(([id, value]) => {
      const el = document.getElementById(id);
      if (el) el.textContent = value;
    });

    const verdictEl = document.getElementById('workspace-readiness-verdict');
    if (verdictEl) {
      verdictEl.textContent = summary.verdict;
      verdictEl.classList.remove('status-ok', 'status-warn', 'status-fail');
      verdictEl.classList.add(this.reviewVerdictStatusClass(summary.verdict));
    }

    const noteEl = document.getElementById('review-intelligence-note');
    if (noteEl) {
      noteEl.textContent = spans.length
        ? 'Span-level review signals derived from current map data only.'
        : 'No route spans available for review intelligence yet.';
    }
    this.renderReviewNavigationState();
  }

  spanReviewLabel(props, index = null) {
    const from = props?.from_point_id || props?.from_design_pole_no || '?';
    const to = props?.to_point_id || props?.to_design_pole_no || '?';
    if (from !== '?' || to !== '?') return `Span ${from} → ${to}`;
    if (props?.span_sequence_label) return `Span ${props.span_sequence_label}`;
    return index == null ? 'Span' : `Span ${index + 1}`;
  }

  primarySpanReviewReason(props, issue) {
    const reasons = Array.isArray(props?.design_blocker_reasons) ? props.design_blocker_reasons : [];
    const structuredReason = reasons.find((reason) => reason && typeof reason === 'object' && reason.message);
    if (structuredReason) return String(structuredReason.message);
    const legacyReason = reasons.find((reason) => this.hasValue(reason));
    if (legacyReason) return String(legacyReason);

    const anomaly = this.classifyRouteSpanAnomaly(props || {});
    if (anomaly.causes.length) return anomaly.causes[0];

    const actions = Array.isArray(props?.designer_suggested_actions) ? props.designer_suggested_actions : [];
    if (actions.length) return String(actions[0]);

    if (issue?.categories?.includes('DATA')) return 'Missing or unconfirmed span evidence';
    if (issue?.categories?.includes('CLEARANCE')) return 'Crossing or clearance context needs review';
    if (issue?.categories?.includes('GEOMETRY')) return 'Route geometry needs review';
    return issue?.severity === 'BLOCKER' ? 'Design blocker present' : 'Review signal present';
  }

  awarenessSpanRef(item) {
    const related = String(item?.related_span_id || '');
    if (!related) return null;
    return (this._spanLineRefs || []).find((ref) => this.spanAwarenessKeys(ref.props || {}).has(related)) || null;
  }

  buildReviewNavigationTargets() {
    const targets = { blockers: [], review: [], gaps: [], awareness: [] };
    (this._spanLineRefs || []).forEach((ref, idx) => {
      const props = ref.props || {};
      const issue = this.classifySpanIssues(props);
      const target = {
        type: 'span',
        spanIndex: idx,
        spanRef: ref,
        label: this.spanReviewLabel(props, idx),
        category: issue.categories[0] || 'DATA',
        severity: issue.severity,
        reason: this.primarySpanReviewReason(props, issue),
      };
      if (issue.severity === 'BLOCKER') targets.blockers.push(target);
      else if (issue.severity === 'REVIEW') targets.review.push(target);
      if (issue.categories.includes('DATA')) {
        targets.gaps.push({ ...target, category: 'DATA', reason: 'Missing or unconfirmed span evidence' });
      }
    });

    const markerRefs = Array.isArray(this._awarenessMarkerRefs) ? this._awarenessMarkerRefs : [];
    markerRefs.forEach((markerRef, idx) => {
      const item = markerRef.item || {};
      const linkedSpanRef = this.awarenessSpanRef(item);
      targets.awareness.push({
        type: 'awareness',
        id: item.id || `awareness-${idx + 1}`,
        label: 'Planner Awareness',
        category: item.category || 'context',
        severity: item.severity || 'INFO',
        reason: item.message || 'Planner awareness note',
        markerRef,
        spanRef: linkedSpanRef,
      });
    });

    return targets;
  }

  reviewNavigationGroupLabel(group) {
    const labels = {
      blockers: 'blockers',
      review: 'review targets',
      gaps: 'evidence gaps',
      awareness: 'planner awareness notes',
    };
    return labels[group] || 'review targets';
  }

  bindReviewNavigationControls() {
    document.querySelectorAll('[data-review-nav-group]').forEach((card) => {
      const activate = () => this.selectReviewNavigationGroup(card.dataset.reviewNavGroup);
      card.addEventListener('click', activate);
      card.addEventListener('keydown', (ev) => {
        if (ev.key === 'Enter' || ev.key === ' ') {
          ev.preventDefault();
          activate();
        }
      });
    });
    const prev = document.getElementById('review-nav-prev');
    const next = document.getElementById('review-nav-next');
    if (prev) prev.addEventListener('click', () => this.focusPreviousReviewTarget());
    if (next) next.addEventListener('click', () => this.focusNextReviewTarget());
    this.renderReviewNavigationState();
  }

  renderReviewNavigationState() {
    const targets = this._reviewNavigationTargets || { blockers: [], review: [], gaps: [], awareness: [] };
    document.querySelectorAll('[data-review-nav-group]').forEach((card) => {
      const group = card.dataset.reviewNavGroup;
      const count = (targets[group] || []).length;
      const disabled = count < 1;
      card.classList.toggle('gf-review-card-disabled', disabled);
      card.classList.toggle('gf-review-card-active', group === this._activeReviewTargetGroup && !disabled);
      card.setAttribute('aria-disabled', disabled ? 'true' : 'false');
      card.setAttribute('title', disabled ? `No ${this.reviewNavigationGroupLabel(group)} found` : `Jump to ${this.reviewNavigationGroupLabel(group)}`);
    });

    const group = this._activeReviewTargetGroup;
    const groupTargets = group ? (targets[group] || []) : [];
    const count = groupTargets.length;
    if (group && count < 1) this._activeReviewTargetIndex = -1;
    else if (group && this._activeReviewTargetIndex < 0) this._activeReviewTargetIndex = 0;
    else if (group && this._activeReviewTargetIndex >= count) this._activeReviewTargetIndex = count - 1;
    const status = document.getElementById('review-nav-status');
    if (status) {
      if (!group) status.textContent = 'Select a review category';
      else if (!count) status.textContent = `No ${this.reviewNavigationGroupLabel(group)} found`;
      else status.textContent = `${this._activeReviewTargetIndex + 1} of ${count}`;
    }

    const showStepButtons = count > 1;
    const prev = document.getElementById('review-nav-prev');
    const next = document.getElementById('review-nav-next');
    [prev, next].forEach((button) => {
      if (!button) return;
      button.disabled = !showStepButtons;
      button.style.visibility = showStepButtons ? 'visible' : 'hidden';
    });
  }

  selectReviewNavigationGroup(group) {
    if (!group) return;
    this._reviewNavigationTargets = this.buildReviewNavigationTargets();
    const targets = this._reviewNavigationTargets[group] || [];
    this._activeReviewTargetGroup = group;
    if (!targets.length) {
      this._activeReviewTargetIndex = -1;
      this.renderReviewNavigationState();
      return;
    }
    this._activeReviewTargetIndex = 0;
    this.renderReviewNavigationState();
    this.focusReviewTarget(targets[0]);
  }

  currentReviewTargetGroup() {
    const group = this._activeReviewTargetGroup;
    if (!group) return [];
    return (this._reviewNavigationTargets || {})[group] || [];
  }

  focusNextReviewTarget() {
    const targets = this.currentReviewTargetGroup();
    if (!targets.length) return;
    this._activeReviewTargetIndex = (this._activeReviewTargetIndex + 1) % targets.length;
    this.renderReviewNavigationState();
    this.focusReviewTarget(targets[this._activeReviewTargetIndex]);
  }

  focusPreviousReviewTarget() {
    const targets = this.currentReviewTargetGroup();
    if (!targets.length) return;
    this._activeReviewTargetIndex = (this._activeReviewTargetIndex - 1 + targets.length) % targets.length;
    this.renderReviewNavigationState();
    this.focusReviewTarget(targets[this._activeReviewTargetIndex]);
  }

  clearFocusedReviewTarget() {
    if (this._focusedReviewTarget?.classList) {
      this._focusedReviewTarget.classList.remove('gf-review-target-focused');
    }
    this._focusedReviewTarget = null;
  }

  markFocusedReviewTarget(layer) {
    this.clearFocusedReviewTarget();
    const el = typeof layer?.getElement === 'function' ? layer.getElement() : null;
    if (el?.classList) {
      el.classList.add('gf-review-target-focused');
      this._focusedReviewTarget = el;
    }
  }

  ensureSpanRouteHighlighted(spanRef) {
    if (!spanRef || spanRef.routeGroupIndex == null) return;
    if (this._activeRouteGroupIndex !== spanRef.routeGroupIndex) {
      this.toggleSpanRouteHighlight(spanRef);
    } else {
      this.applySpanRouteHighlightStyles(this._spanCrossingFilterOnly);
    }
  }

  focusReviewTarget(target) {
    if (!target) return;
    if (target.type === 'span') {
      const ref = target.spanRef || this._spanLineRefs?.[target.spanIndex];
      if (!ref?.line) return;
      if (this.map && typeof ref.line.getBounds === 'function') {
        this.map.fitBounds(ref.line.getBounds(), { padding: [48, 48], maxZoom: 17 });
      }
      this.ensureSpanRouteHighlighted(ref);
      this.markFocusedReviewTarget(ref.line);
      if (typeof ref.line.openPopup === 'function') ref.line.openPopup();
      return;
    }

    if (target.type === 'awareness') {
      const marker = target.markerRef?.marker;
      if (target.spanRef) this.ensureSpanRouteHighlighted(target.spanRef);
      if (this.map && marker && typeof marker.getLatLng === 'function') {
        this.map.setView(marker.getLatLng(), Math.max(this.map.getZoom?.() || 15, 16));
      }
      this.markFocusedReviewTarget(marker);
      if (marker && typeof marker.openPopup === 'function') marker.openPopup();
    }
  }

  spanReviewClassName(props) {
    const issue = this.classifySpanIssues(props);
    if (issue.severity === 'BLOCKER') return 'gf-span-blocker';
    if (issue.severity === 'REVIEW') return 'gf-span-review';
    return '';
  }

  applySpanReviewSignalClasses() {
    for (const ref of this._spanLineRefs || []) {
      const el = typeof ref.line?.getElement === 'function' ? ref.line.getElement() : null;
      if (!el?.classList) continue;
      const cls = this.spanReviewClassName(ref.props || {});
      el.classList.toggle('gf-span-blocker', cls === 'gf-span-blocker');
      el.classList.toggle('gf-span-review', cls === 'gf-span-review');
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

      marker.bindPopup(this.buildPopupHtml(props, status, lat, lon), {
        autoPanPadding: [24, 24],
        className: 'gridflow-asset-popup',
        keepInView: true,
        maxWidth: 476,
      });
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
    this._replacementDrawableLineCount = 0;
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

    const prCountByExisting = new Map();
    for (const fd of this.featureData) {
      if (!this.hasValue(fd.props.replacing)) continue;
      const ex = String(fd.props.replacing);
      prCountByExisting.set(ex, (prCountByExisting.get(ex) || 0) + 1);
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
      const clusterN = prCountByExisting.get(String(fd.props.replacing)) || 1;
      const clusterHint = clusterN > 1
        ? `<div class="popup-row lifecycle-cluster-hint"><strong>Cluster:</strong> ${clusterN} proposed points share existing <strong>${this.escapeHtml(String(fd.props.replacing))}</strong> — confirm the intended pair on the review page.</div>`
        : '';
      const audit = fd.props.replacement_pair_audit || {};
      const pct = audit.confidence_pct != null ? Number(audit.confidence_pct) : null;
      const pctClass = pct == null ? '' : pct >= 75 ? 'lifecycle-conf-high' : pct >= 50 ? 'lifecycle-conf-med' : 'lifecycle-conf-low';
      const confBlock = pct != null
        ? `<div class="popup-row"><strong>Match confidence:</strong> <span class="${pctClass}">${pct}%</span>${audit.match_type ? ` — ${this.escapeHtml(String(audit.match_type))}` : ''}</div>`
        : '';
      line.bindPopup(`
        <div class="popup-title">Suggested Existing/Proposed Match</div>
        <div class="popup-row"><strong>Existing:</strong> Point ${this.escapeHtml(fd.props.replacing)}</div>
        <div class="popup-row"><strong>Proposed:</strong> Point ${this.escapeHtml(fd.props.pole_id || fd.props.id || 'Unknown')}</div>
        ${confBlock}
        ${offsetLine}
        ${clusterHint}
        <div class="popup-row" style="color:#64748b;font-size:0.82em;margin-top:4px;">Suggested replacement link — unconfirmed. Review pairing page to confirm.</div>
      `);
      line.addTo(this.lifecycleMatchLayer);
      this._replacementDrawableLineCount += 1;
    }

    const toggle = document.getElementById('lifecycle-match-toggle');
    if (!toggle || toggle.checked) {
      this.lifecycleMatchLayer.addTo(this.map);
    }
  }

  renderGeoJsonSpanFeatures(spanFeatures) {
    if (!this.map || !Array.isArray(spanFeatures) || spanFeatures.length === 0) return;

    if (this.spanLayer) {
      this.spanLayer.clearLayers();
      this.map.removeLayer(this.spanLayer);
    }
    this.spanLayer = L.layerGroup();
    this._spanFeatureList = spanFeatures.slice();
    this._spanLineRefs = [];
    this._spanRouteGroups = [];
    this._activeRouteGroupIndex = null;

    spanFeatures.forEach((feat, si) => {
      if (!feat || feat.type !== 'Feature') return;
      const geom = feat.geometry || {};
      if (geom.type !== 'LineString') return;
      const coords = geom.coordinates || [];
      if (coords.length < 2) return;
      const latLngs = coords.map((c) => {
        if (!Array.isArray(c) || c.length < 2) return null;
        return [c[1], c[0]];
      }).filter(Boolean);
      if (latLngs.length < 2) return;

      const props = feat.properties || {};
      const vis = this.spanPolylineVisual(props, false);
      const reviewClass = this.spanReviewClassName(props);
      const line = L.polyline(latLngs, {
        color: vis.color,
        weight: vis.weight,
        opacity: vis.opacity,
        lineCap: 'round',
        lineJoin: 'round',
        className: ['gridflow-span-line', reviewClass].filter(Boolean).join(' '),
      });

      const label = this.spanDistanceLabel(props);
      if (label) {
        this.bindSpanDistanceTooltip(line, props);
      }

      line.bindPopup(this.buildSpanPopupHtml(props), {
        autoPanPadding: [24, 24],
        className: 'gridflow-asset-popup',
        keepInView: true,
        maxWidth: 476,
      });
      const ref = { line, props, index: si, routeGroupIndex: null };
      line.on('click', () => this.toggleSpanRouteHighlight(ref));
      line.addTo(this.spanLayer);
      this._spanLineRefs.push(ref);
    });

    this.initialiseSpanRouteGroups();

    if (this.layerState.spans) {
      this.spanLayer.addTo(this.map);
    }

    this.refreshSpanListPanel({ onlyCrossingRisk: this._spanCrossingFilterOnly });
  }

  spanPolylineVisual(props, focusDimOthers) {
    const risk = String(props.crossing_risk_level || 'none').toLowerCase();
    let color = '#1d4ed8';
    let weight = 5;
    let opacity = 0.88;
    if (risk === 'blocker') {
      color = '#991b1b';
      weight = 7;
    } else if (risk === 'high') {
      color = '#c2410c';
      weight = 6;
    } else if (risk === 'medium') {
      color = '#d97706';
      weight = 5;
    } else if (risk === 'low') {
      color = '#2563eb';
      weight = 5;
    }
    if (focusDimOthers) {
      const has = risk !== 'none' && risk !== '';
      if (!has) {
        opacity = 0.22;
        weight = 3;
        color = '#93c5fd';
      } else {
        opacity = 0.95;
        weight = Math.max(weight, 6);
      }
    }
    return { color, weight, opacity };
  }

  refreshSpanListPanel({ onlyCrossingRisk = false } = {}) {
    const panel = document.getElementById('span-panel');
    const list = document.getElementById('span-list');
    if (!panel || !list) return;
    if (!this._spanLineRefs.length) {
      panel.style.display = 'none';
      list.innerHTML = '';
      return;
    }
    panel.style.display = 'block';
    const refs = onlyCrossingRisk
      ? this._spanLineRefs.filter(({ props }) => {
        const r = String(props.crossing_risk_level || 'none').toLowerCase();
        return r !== 'none' && r !== '';
      })
      : this._spanLineRefs.slice();

    list.innerHTML = '';
    refs.forEach(({ line, props, index }) => {
      const row = document.createElement('button');
      row.type = 'button';
      row.className = 'span-list-item';
      const r = String(props.crossing_risk_level || 'none').toLowerCase();
      if (r === 'blocker' || r === 'high') row.classList.add('span-list-item-risk-high');
      else if (r === 'medium') row.classList.add('span-list-item-risk-med');
      else if (r === 'low') row.classList.add('span-list-item-risk-low');
      const seq = props.span_sequence_label || `#${index + 1}`;
      const dist = this.formatSpanDistance(props.distance_m, this._geometryTrust) || '';
      const fromTo = `${this.escapeHtml(props.from_point_id || '?')} → ${this.escapeHtml(props.to_point_id || '?')}`;
      const anomaly = this.classifyRouteSpanAnomaly(props);
      const anomalyChip = anomaly.causes.length
        ? `<span class="span-list-anomaly" title="${this.escapeHtml(anomaly.causes.join(' · '))}">${this.escapeHtml(anomaly.short)}</span>`
        : '';
      row.innerHTML = `<span class="span-list-seq">${this.escapeHtml(seq)}</span><span class="span-list-route">${fromTo}</span>${dist ? `<span class="span-list-dist">${dist}</span>` : ''}${anomalyChip}${r !== 'none' ? `<span class="span-list-risk">${r}</span>` : ''}`;
      row.addEventListener('click', () => {
        if (!this.map || !line.getBounds) return;
        const ref = this._spanLineRefs.find((item) => item.line === line);
        if (ref) this.toggleSpanRouteHighlight(ref);
        this.map.fitBounds(line.getBounds(), { padding: [48, 48], maxZoom: 17 });
        line.openPopup();
      });
      list.appendChild(row);
    });
  }

  _applySpanCrossingFocusMode(active) {
    if (!this._spanLineRefs || !this.map) return;
    this.applySpanRouteHighlightStyles(active);
  }

  spanRouteKey(value) {
    const s = String(value ?? '').trim();
    return s ? s.toUpperCase() : null;
  }

  spanRouteKeys(props) {
    const keys = [
      this.spanRouteKey(props?.from_point_id),
      this.spanRouteKey(props?.to_point_id),
    ].filter(Boolean);
    if (!keys.length && props?.section_id != null && props.section_id !== '') {
      keys.push(`SECTION:${String(props.section_id).trim().toUpperCase()}`);
    }
    return keys;
  }

  buildSpanRouteGroups(spanRefs = this._spanLineRefs) {
    const groups = [];
    const keyToGroup = new Map();
    if (!Array.isArray(spanRefs)) return groups;

    spanRefs.forEach((ref) => {
      const keys = this.spanRouteKeys(ref?.props || {});
      const matchedGroups = [...new Set(keys.map((key) => keyToGroup.get(key)).filter((idx) => idx != null))];
      let groupIndex = matchedGroups.length ? matchedGroups[0] : groups.length;
      if (!groups[groupIndex]) groups[groupIndex] = [];
      if (!groups[groupIndex].includes(ref)) groups[groupIndex].push(ref);

      matchedGroups.slice(1).forEach((mergeIndex) => {
        if (mergeIndex === groupIndex || !groups[mergeIndex]) return;
        groups[mergeIndex].forEach((mergeRef) => {
          if (!groups[groupIndex].includes(mergeRef)) groups[groupIndex].push(mergeRef);
        });
        groups[mergeIndex] = [];
      });

      groups[groupIndex].forEach((groupRef) => {
        this.spanRouteKeys(groupRef.props || {}).forEach((key) => keyToGroup.set(key, groupIndex));
      });
    });

    return groups.filter((group) => group.length > 0);
  }

  initialiseSpanRouteGroups() {
    this._spanRouteGroups = this.buildSpanRouteGroups(this._spanLineRefs);
    this._spanRouteGroups.forEach((group, groupIndex) => {
      group.forEach((ref) => {
        ref.routeGroupIndex = groupIndex;
      });
    });
  }

  clearSpanRouteHighlight() {
    this._activeRouteGroupIndex = null;
    this.applySpanRouteHighlightStyles(this._spanCrossingFilterOnly);
  }

  toggleSpanRouteHighlight(spanRef) {
    const groupIndex = spanRef?.routeGroupIndex;
    if (groupIndex == null) return;
    if (this._activeRouteGroupIndex === groupIndex) {
      this.clearSpanRouteHighlight();
      return;
    }
    this._activeRouteGroupIndex = groupIndex;
    this.applySpanRouteHighlightStyles(this._spanCrossingFilterOnly);
  }

  applySpanRouteHighlightStyles(focusDimOthers = false) {
    const activeGroup = this._activeRouteGroupIndex;
    const hasActiveRoute = activeGroup != null;
    for (const ref of this._spanLineRefs || []) {
      const { line, props } = ref;
      const selected = hasActiveRoute && ref.routeGroupIndex === activeGroup;
      const dimNonSelected = hasActiveRoute && !selected;
      const vis = this.spanPolylineVisual(props, focusDimOthers && !selected);
      const style = selected
        ? {
            color: '#0f63ff',
            weight: Math.max(vis.weight + 3, 8),
            opacity: 1,
          }
        : {
            color: vis.color,
            weight: dimNonSelected ? Math.max(3, vis.weight - 1) : vis.weight,
            opacity: dimNonSelected ? 0.24 : vis.opacity,
          };
      line.setStyle(style);
      const el = typeof line.getElement === 'function' ? line.getElement() : null;
      if (el?.classList) el.classList.toggle('gf-route-highlight', selected);
      if (selected && typeof line.bringToFront === 'function') line.bringToFront();
    }
  }

  cablePolylineVisual(props) {
    const risk = String(props.crossing_risk_level || 'none').toLowerCase();
    let color = '#6b21a8';
    let weight = 4;
    let opacity = 0.9;
    if (risk === 'blocker') {
      color = '#7f1d1d';
      weight = 6;
    } else if (risk === 'high') {
      color = '#9f1239';
      weight = 5;
    } else if (risk === 'medium') {
      color = '#7e22ce';
    } else if (risk === 'low') {
      color = '#9333ea';
    }
    return { color, weight, opacity };
  }

  plannerAwarenessColor(severity) {
    const s = String(severity || 'INFO').toUpperCase();
    if (s === 'BLOCKER') return '#dc2626';
    if (s === 'REVIEW') return '#f97316';
    if (s === 'WARNING') return '#eab308';
    return '#2563eb';
  }

  buildPlannerAwarenessPopupHtml(item) {
    return `
      <div class="asset-popup asset-popup-planner-awareness">
        <div class="popup-title">Planner Awareness</div>
        ${this.popupSection('Context note', [
          this.popupRow('Category', item.category || 'planner note', 'info'),
          this.popupRow('Severity', item.severity || 'INFO', 'review'),
          this.popupRow('Message', item.message || 'No message supplied', 'info'),
        ])}
      </div>
    `;
  }

  renderPlannerAwareness(items) {
    if (!this.map) return;
    this._plannerAwarenessItems = Array.isArray(items) ? items.slice() : [];
    this._awarenessMarkerRefs = [];
    if (this.plannerAwarenessLayer) {
      this.plannerAwarenessLayer.clearLayers();
      this.map.removeLayer(this.plannerAwarenessLayer);
    }
    this.plannerAwarenessLayer = L.layerGroup();
    if (!Array.isArray(items) || items.length === 0) {
      this.applySpanReviewSignalClasses();
      this.renderReviewIntelligenceSummary();
      return;
    }

    items.forEach((item) => {
      if (!item || item.lat == null || item.lon == null) return;
      const lat = Number(item.lat);
      const lon = Number(item.lon);
      if (Number.isNaN(lat) || Number.isNaN(lon)) return;
      const color = this.plannerAwarenessColor(item.severity);
      const marker = L.circleMarker([lat, lon], {
        radius: 7,
        color,
        fillColor: color,
        fillOpacity: 0.78,
        opacity: 0.95,
        weight: 2,
        className: 'planner-awareness-marker',
      });
      marker.bindPopup(this.buildPlannerAwarenessPopupHtml(item), {
        autoPanPadding: [24, 24],
        className: 'gridflow-asset-popup',
        keepInView: true,
        maxWidth: 360,
      });
      this._awarenessMarkerRefs.push({ item, marker, index: this._awarenessMarkerRefs.length });
      marker.addTo(this.plannerAwarenessLayer);
    });

    if (this.layerState.plannerAwareness) {
      this.plannerAwarenessLayer.addTo(this.map);
    }
    this.applySpanReviewSignalClasses();
    this.renderReviewIntelligenceSummary();
  }

  togglePlannerAwarenessLayer(shouldShow) {
    if (!this.map || !this.plannerAwarenessLayer) return;
    if (shouldShow) {
      if (!this.map.hasLayer(this.plannerAwarenessLayer)) {
        this.plannerAwarenessLayer.addTo(this.map);
      }
      (this._awarenessMarkerRefs || []).forEach(({ marker }) => {
        if (marker && !this.plannerAwarenessLayer.hasLayer?.(marker)) {
          marker.addTo(this.plannerAwarenessLayer);
        }
      });
      return;
    }

    if (this.map.hasLayer(this.plannerAwarenessLayer)) {
      this.map.removeLayer(this.plannerAwarenessLayer);
    }
    (this._awarenessMarkerRefs || []).forEach(({ marker }) => {
      if (marker && this.map.hasLayer(marker)) {
        this.map.removeLayer(marker);
      }
    });
  }

  renderCableFeatures(cableFeatures) {
    if (!this.map) return;
    if (this.cableLayer) {
      this.cableLayer.clearLayers();
      this.map.removeLayer(this.cableLayer);
    }
    this._cableLineRefs = [];
    if (!Array.isArray(cableFeatures) || cableFeatures.length === 0) {
      this.cableLayer = null;
      return;
    }
    this.cableLayer = L.layerGroup();
    cableFeatures.forEach((feat, ci) => {
      if (!feat || feat.type !== 'Feature') return;
      const geom = feat.geometry || {};
      if (geom.type !== 'LineString') return;
      const coords = geom.coordinates || [];
      if (coords.length < 2) return;
      const latLngs = coords.map((c) => {
        if (!Array.isArray(c) || c.length < 2) return null;
        return [c[1], c[0]];
      }).filter(Boolean);
      if (latLngs.length < 2) return;
      const props = feat.properties || {};
      const vis = this.cablePolylineVisual(props);
      const line = L.polyline(latLngs, {
        color: vis.color,
        weight: vis.weight,
        opacity: vis.opacity,
        dashArray: '10, 7',
        lineCap: 'round',
        lineJoin: 'round',
        className: 'gridflow-cable-line',
      });
      const dist = props.distance_m != null && !Number.isNaN(Number(props.distance_m))
        ? `${Number(props.distance_m).toFixed(1)} m UG`
        : 'UG';
      line.bindTooltip(dist, {
        permanent: false,
        direction: 'center',
        className: 'gridflow-cable-tooltip',
        sticky: true,
      });
      line.bindPopup(this.buildCablePopupHtml(props), {
        autoPanPadding: [24, 24],
        className: 'gridflow-asset-popup',
        keepInView: true,
        maxWidth: 476,
      });
      line.addTo(this.cableLayer);
      this._cableLineRefs.push({ line, props, index: ci });
    });
    if (this.layerState.cables) {
      this.cableLayer.addTo(this.map);
    }
  }

  cableCrossingRiskLabel(props) {
    const r = String(props.crossing_risk_level || 'none').toLowerCase();
    if (r === 'blocker') return 'Blocker — high-tier crossing within clearance proximity';
    if (r === 'high') return 'High — road/track/utility-type context near cable trace';
    if (r === 'medium') return 'Medium — obstruction or environmental context nearby';
    if (r === 'low') return 'Low — general route context nearby';
    return 'None — no surveyed context points matched near this segment';
  }

  cablePopupSections(props) {
    const routeRows = [
      this.popupRow('From structure', props.from_point_id || '—', props.from_point_id ? 'ok' : 'info'),
      this.popupRow('To structure', props.to_point_id || '—', props.to_point_id ? 'ok' : 'info'),
      this.popupRow(
        'Trace length',
        props.distance_m != null ? `${Number(props.distance_m).toFixed(1)} m (plan)` : '—',
        props.distance_m != null ? 'ok' : 'info',
      ),
      this.popupRow(
        'Routing source',
        props.routing_source === 'support_span' ? 'Support IDs (UG record)' : 'Cable link fields',
        'info',
      ),
    ];
    const installRows = [
      this.popupRow('Depth of lay', props.burial_depth_m != null ? String(props.burial_depth_m) : '—', props.burial_depth_m ? 'ok' : 'warning'),
      this.popupRow('Duct / protection', props.ducting_type || '—', props.ducting_type ? 'ok' : 'info'),
    ];
    const clearanceRows = [
      this.popupRow('Crossing risk (survey context)', this.cableCrossingRiskLabel(props), this.spanCrossingRiskRowStatus(props)),
      ...this.crossingHitRowsForSpan(props),
    ];
    const acts = Array.isArray(props.designer_suggested_actions) ? props.designer_suggested_actions : [];
    const actionSection = acts.length
      ? [{ title: 'Designer actions (auto-suggested)', rows: acts.map((t) => this.popupRow('Action', t, 'review')) }]
      : [];
    const electricalNote = [
      this.popupRow(
        'Electrical scope',
        'Values describe this underground cable trace (segment between supports), not pole-top equipment.',
        'info',
      ),
    ];
    return [
      { title: 'Underground cable route', rows: routeRows },
      { title: 'Installation', rows: installRows },
      { title: 'Clearance & crossings', rows: clearanceRows },
      ...actionSection,
      { title: 'Electrical', rows: [...electricalNote, ...this.electricalRows(props, { includeEquipment: false })] },
    ];
  }

  buildCablePopupHtml(props) {
    const title = `${this.escapeHtml(props.from_point_id || '?')} → ${this.escapeHtml(props.to_point_id || '?')} (UG)`;
    const sections = this.cablePopupSections(props);
    return `
      <div class="asset-popup asset-popup-cable">
        <div class="popup-title">${title}</div>
        ${sections.map((s) => this.popupSection(s.title, s.rows)).join('')}
      </div>
    `;
  }

  formatSpanDistance(distance_m, trust) {
    if (distance_m == null || Number.isNaN(Number(distance_m))) return null;
    const d = Number(distance_m);
    const t = String(trust || 'HIGH').toUpperCase();
    if (t === 'LOW') return `~${Math.round(d)} m`;
    if (t === 'MEDIUM') return `~${d.toFixed(1)} m`;
    return `${d.toFixed(2)} m`;
  }

  spanDistanceLabel(props) {
    return this.formatSpanDistance(props.distance_m, this._geometryTrust) || '';
  }

  spanCrossingRiskLabel(props) {
    const r = String(props.crossing_risk_level || 'none').toLowerCase();
    if (r === 'blocker') return 'Blocker — high-tier crossing within clearance proximity';
    if (r === 'high') return 'High — road/track/utility-type context near span';
    if (r === 'medium') return 'Medium — obstruction or environmental context nearby';
    if (r === 'low') return 'Low — general route context nearby';
    return 'None — no surveyed context points matched near this span';
  }

  spanCrossingRiskRowStatus(props) {
    const r = String(props.crossing_risk_level || 'none').toLowerCase();
    if (r === 'blocker') return 'blocker';
    if (r === 'high') return 'blocker';
    if (r === 'medium') return 'warning';
    if (r === 'low') return 'review';
    return 'info';
  }

  crossingHitRowsForSpan(props) {
    const hits = props.crossing_hits_survey;
    if (!Array.isArray(hits) || !hits.length) {
      return [this.popupRow(
        'Context hits',
        'No context records within span correlation distance.',
        'info',
        'Correlation uses surveyed coordinates — missing hits do not prove the span is clear.',
      )];
    }
    return hits.slice(0, 8).map((h) => {
      const t = String(h.crossing_tier || 'low').toLowerCase();
      const crossingWeighted = t === 'high' || t === 'medium';
      const st = this.escapeHtml(h.structure_type || 'context');
      const pid = h.point_id ? ` · ${this.escapeHtml(h.point_id)}` : '';
      const dm = h.distance_m != null ? `${Number(h.distance_m).toFixed(1)} m` : 'distance n/a';
      const label = crossingWeighted ? `Crossing-weighted context${pid}` : `Route proximity (general context)${pid}`;
      const detail = crossingWeighted
        ? `${st} · ${dm} from span corridor · tier ${t} — prioritise clearance / coordination review`
        : `${st} · ${dm} from span corridor · tier ${t} — confirm relevance to electrical clearance`;
      const status = t === 'high' ? 'blocker' : t === 'medium' ? 'warning' : 'info';
      return this.popupRow(label, detail, status);
    });
  }

  spanPopupSections(props) {
    const seqRows = [
      this.popupRow(
        'Position',
        props.span_sequence_label || (props.span_index != null ? `Span ${Number(props.span_index) + 1}` : '—'),
        'info',
      ),
      this.popupRow('Section', props.section_id != null && props.section_id !== '' ? String(props.section_id) : '—', 'info'),
      this.popupRow(
        'Design chain',
        (props.from_design_pole_no != null || props.to_design_pole_no != null)
          ? `${props.from_design_pole_no ?? '—'} → ${props.to_design_pole_no ?? '—'}`
          : '—',
        'info',
      ),
    ];
    if (props.previous_span && typeof props.previous_span === 'object') {
      const ps = props.previous_span;
      seqRows.push(this.popupRow(
        'Previous span',
        `${ps.from_point_id || '—'} → ${ps.to_point_id || '—'}`,
        'info',
      ));
    }
    if (props.next_span && typeof props.next_span === 'object') {
      const ns = props.next_span;
      seqRows.push(this.popupRow(
        'Next span',
        `${ns.from_point_id || '—'} → ${ns.to_point_id || '—'}`,
        'info',
      ));
    }

    const routeRows = [
      this.popupRow('From support', props.from_point_id || '—', props.from_point_id ? 'ok' : 'info'),
      this.popupRow('To support', props.to_point_id || '—', props.to_point_id ? 'ok' : 'info'),
      this.popupRow(
        'Distance',
        this.formatSpanDistance(props.distance_m, this._geometryTrust) || '—',
        props.distance_m != null ? 'ok' : 'info',
      ),
    ];

    const clearanceRows = [
      this.popupRow('Crossing risk (survey context)', this.spanCrossingRiskLabel(props), this.spanCrossingRiskRowStatus(props)),
      ...this.crossingHitRowsForSpan(props),
    ];

    const anomaly = this.classifyRouteSpanAnomaly(props);
    const actionsRaw = Array.isArray(props.designer_suggested_actions) ? props.designer_suggested_actions : [];
    const actionsUse = this.filterSpanDesignerActions(actionsRaw, anomaly.causes);
    const actionSection = actionsUse.length
      ? [{
        title: 'Designer actions (what to do next)',
        rows: actionsUse.map((text) => this.popupRow('Action', text, 'review')),
      }]
      : [];

    const anomalySection = anomaly.causes.length
      ? [{
        title: 'Route span — review signals (what looks wrong)',
        rows: [
          this.popupRow('Summary', anomaly.short || 'Review this span', 'warning'),
          ...anomaly.causes.slice(0, 8).map((c) => this.popupRow('Signal', c, 'review')),
        ],
      }]
      : [];

    const clusterSection = props.geometry_issue_cluster
      ? [{
        title: 'Geometry cluster',
        rows: [
          this.popupRow(
            'Note',
            `Multiple short spans detected in this section${props.cluster_size ? ` (${props.cluster_size} spans)` : ''}`,
            'warning',
          ),
        ],
      }]
      : [];

    const electricalIntro = [
      this.popupRow(
        'Electrical scope',
        'Conductor / voltage attributes apply to this overhead span between supports (derived from adjacent structure records). Pole popups list equipment only when captured on that structure.',
        'info',
      ),
    ];

    return [
      { title: 'Sequence', rows: seqRows },
      { title: 'Route span', rows: routeRows },
      ...clusterSection,
      ...anomalySection,
      { title: 'Clearance & crossings', rows: clearanceRows },
      ...actionSection,
      { title: 'Electrical', rows: [...electricalIntro, ...this.electricalRows(props, { includeEquipment: false })] },
    ];
  }

  buildSpanPopupHtml(props) {
    const detail = props.source_confidence_detail || {};
    const trust = props.geometry_trust || detail.geometry_trust;
    const confidence = detail.confidence;
    const showGeometryWarning =
      trust === 'unverified' ||
      confidence === 'low';

    const warningBanner = showGeometryWarning
      ? `<div class="gf-warning-banner">
          <strong>⚠️ Unverified geometry</strong><br>
          ${detail.designer_note || 'Field verification required before design use'}
        </div>`
      : '';

    const blockerReasons = this.sortedDesignReasons(props.design_blocker_reasons);
    const blockerSection = blockerReasons.length
      ? this.popupSection(
          'Design validation',
          blockerReasons.map((r) => this.popupRow(
            `Reason (${String(r.severity || 'info').toUpperCase()})`,
            r.message || r,
            this.designReasonStatus(r.severity),
            r.type ? `Type: ${r.type}` : '',
          )),
        )
      : '';

    const title = `${this.escapeHtml(props.from_point_id || '?')} → ${this.escapeHtml(props.to_point_id || '?')}`;
    const sections = this.spanPopupSections(props);
    return `
      <div class="asset-popup asset-popup-span">
        ${warningBanner}${blockerSection}<div class="popup-title">${title}</div>
        ${sections.map((s) => this.popupSection(s.title, s.rows)).join('')}
      </div>
    `;
  }

  designReasonSeverityRank(severity) {
    return {
      blocker: 0,
      high: 1,
      medium: 2,
      low: 3,
      info: 4,
    }[String(severity || 'info').toLowerCase()] ?? 4;
  }

  designReasonStatus(severity) {
    const s = String(severity || 'info').toLowerCase();
    if (s === 'blocker') return 'blocker';
    if (s === 'high') return 'warning';
    if (s === 'medium') return 'review';
    return 'info';
  }

  sortedDesignReasons(reasons) {
    if (!Array.isArray(reasons)) return [];
    return reasons
      .map((reason) => {
        if (reason && typeof reason === 'object') return reason;
        return { type: 'legacy', severity: 'info', message: String(reason || '') };
      })
      .filter((reason) => reason.message)
      .sort((a, b) => this.designReasonSeverityRank(a.severity) - this.designReasonSeverityRank(b.severity));
  }

  renderDesignChainSpans(spans) {
    if (!this.map || !Array.isArray(spans) || spans.length === 0) return;

    this.spanLayer = L.layerGroup();
    this._spanFeatureList = spans.slice();
    this._spanLineRefs = [];
    this._spanRouteGroups = [];
    this._activeRouteGroupIndex = null;

    spans.forEach((span, si) => {
      const coords = span.coordinates || [];
      if (coords.length !== 2) return;

      const from = coords[0];
      const to = coords[1];
      if (!Array.isArray(from) || !Array.isArray(to) || from.length < 2 || to.length < 2) {
        return;
      }

      const props = {
        from_point_id: span.from_point_id,
        to_point_id: span.to_point_id,
        from_design_pole_no: span.from_design_pole_no,
        to_design_pole_no: span.to_design_pole_no,
        section_id: span.section_id,
        distance_m: span.distance_m,
        span_index: si,
        span_total: spans.length,
        span_sequence_label: `${si + 1} of ${spans.length}`,
        crossing_risk_level: 'none',
        crossing_hits_survey: [],
        designer_suggested_actions: [],
        feature_type: 'circuit_span',
      };

      const vis = this.spanPolylineVisual(props, false);
      const reviewClass = this.spanReviewClassName(props);
      const line = L.polyline([from, to], {
        color: vis.color,
        weight: vis.weight,
        opacity: vis.opacity,
        lineCap: 'round',
        lineJoin: 'round',
        className: ['gridflow-span-line', reviewClass].filter(Boolean).join(' '),
      });

      const label = this.spanDistanceLabel(props);
      if (label) {
        this.bindSpanDistanceTooltip(line, props);
      }

      line.bindPopup(this.buildSpanPopupHtml(props), {
        autoPanPadding: [24, 24],
        className: 'gridflow-asset-popup',
        keepInView: true,
        maxWidth: 476,
      });
      const ref = { line, props, index: si, routeGroupIndex: null };
      line.on('click', () => this.toggleSpanRouteHighlight(ref));
      line.addTo(this.spanLayer);
      this._spanLineRefs.push(ref);
    });

    this.initialiseSpanRouteGroups();

    if (this.layerState.spans) {
      this.spanLayer.addTo(this.map);
    }

    this.refreshSpanListPanel({ onlyCrossingRisk: this._spanCrossingFilterOnly });
  }

  /**
   * Spans that merit a pinned distance label when mode is "review" or similar.
   * Aligns with span_generator crossing tiers and length heuristics (12 m / 280 m).
   */
  isSpanLabelAnomaly(props) {
    const r = String(props.crossing_risk_level || 'none').toLowerCase();
    if (r && r !== 'none') return true;
    const dm = props.distance_m != null ? Number(props.distance_m) : NaN;
    if (!Number.isNaN(dm) && (dm < 12 || dm > 280)) return true;
    const acts = Array.isArray(props.designer_suggested_actions) ? props.designer_suggested_actions : [];
    return acts.some((a) => {
      const s = String(a);
      return /very short span|long span|verify conductor choice|Review obstruction|Spot-check route context/i.test(s);
    });
  }

  isSpanPinCrossing(props) {
    const r = String(props.crossing_risk_level || 'none').toLowerCase();
    return Boolean(r && r !== 'none');
  }

  isSpanPinCritical(props) {
    const tx = [...(props.issue_texts || []), ...(props.warn_texts || [])].join(' ');
    if (/duplicate pole|missing intermediate|Span very short|borderline short|unusually short/i.test(tx)) {
      return true;
    }
    const dm = props.distance_m != null ? Number(props.distance_m) : NaN;
    if (!Number.isNaN(dm) && dm < 8) return true;
    const r = String(props.crossing_risk_level || 'none').toLowerCase();
    if (r === 'blocker' || r === 'high') return true;
    return false;
  }

  isSpanPinReview(props) {
    return this.isSpanLabelAnomaly(props) || this.hasSpanAnomaly(props);
  }

  bindSpanDistanceTooltip(line, props) {
    const label = this.spanDistanceLabel(props);
    if (!label) return;
    const mode = this._spanLabelMode || 'hover';
    let permanent = false;
    if (mode === 'all') permanent = true;
    else if (mode === 'hover') permanent = false;
    else if (mode === 'critical') permanent = this.isSpanPinCritical(props);
    else if (mode === 'crossing') permanent = this.isSpanPinCrossing(props);
    else if (mode === 'review') permanent = this.isSpanPinReview(props);
    line.bindTooltip(label, {
      permanent,
      direction: 'center',
      className: 'gridflow-span-distance-label',
      opacity: 0.95,
      sticky: true,
    });
  }

  applySpanLabelMode() {
    if (!this._spanLineRefs || !this._spanLineRefs.length) return;
    for (const { line, props } of this._spanLineRefs) {
      line.unbindTooltip();
      const label = this.spanDistanceLabel(props);
      if (label) {
        this.bindSpanDistanceTooltip(line, props);
      }
    }
  }

  bindSpanLabelModeControl() {
    const sel = document.getElementById('span-label-mode');
    if (!sel) return;
    sel.value = this._spanLabelMode;
    if (!this._spanLabelModeControlBound) {
      this._spanLabelModeControlBound = true;
      sel.addEventListener('change', () => {
        const v = sel.value;
        const allowed = new Set(['hover', 'critical', 'crossing', 'review', 'all']);
        this._spanLabelMode = allowed.has(v) ? v : 'hover';
        try {
          localStorage.setItem('gridflow_map_span_label_mode', this._spanLabelMode);
        } catch {
          /* ignore */
        }
        this.applySpanLabelMode();
      });
    }
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
        if (input.disabled) {
          input.checked = false;
          return;
        }
        this.layerState[layerName] = input.checked;
        if (layerName === 'spans') {
          this.toggleLayer(this.spanLayer, input.checked);
        } else if (layerName === 'cables') {
          this.toggleLayer(this.cableLayer, input.checked);
        } else if (layerName === 'matches') {
          this.toggleLayer(this.lifecycleMatchLayer, input.checked);
        } else if (layerName === 'plannerAwareness') {
          this.togglePlannerAwarenessLayer(input.checked);
        } else if (layerName === 'angle') {
          this.applyAngleHighlightState();
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
        this._spanCrossingFilterOnly = false;
        this.applyVisibility();
        document.querySelectorAll('.status-filter-btn').forEach(b => b.classList.remove('filter-active'));
        document.querySelectorAll('.focus-filter-btn').forEach(b => b.classList.remove('filter-active'));
        if (this.filterNoteEl) this.filterNoteEl.textContent = '';
        this.refreshSpanListPanel({ onlyCrossingRisk: false });
        this._applySpanCrossingFocusMode(false);
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
      this._spanCrossingFilterOnly = false;
      this.applyVisibility();
      document.querySelectorAll('.status-filter-btn').forEach(btn => btn.classList.remove('filter-active'));
      document.querySelectorAll('.focus-filter-btn').forEach(btn => btn.classList.remove('filter-active'));
      if (this.filterNoteEl) this.filterNoteEl.textContent = '';
      this._hideRecordPanel();
      this.refreshSpanListPanel({ onlyCrossingRisk: false });
      this._applySpanCrossingFocusMode(false);
    } else {
      this.activeFilter = value;
      this.activeFilterMode = mode;
      const isSpanCrossing = mode === 'focus' && value === 'span-crossing-risk';
      const filtered = isSpanCrossing ? this.featureData : this.filterFeatureData(mode, value);
      this.applyVisibility(filtered);
      document.querySelectorAll('.status-filter-btn').forEach(btn => {
        btn.classList.toggle('filter-active', mode === 'status' && btn.dataset.filter === value);
      });
      document.querySelectorAll('.focus-filter-btn').forEach(btn => {
        btn.classList.toggle('filter-active', mode === 'focus' && btn.dataset.focus === value);
      });
      const label = this.filterLabel(mode, value);
      if (isSpanCrossing) {
        this._spanCrossingFilterOnly = true;
        const crossing = this._spanLineRefs.filter(({ props }) => {
          const r = String(props.crossing_risk_level || 'none').toLowerCase();
          return r !== 'none' && r !== '';
        });
        if (this.filterNoteEl) {
          this.filterNoteEl.textContent = `${crossing.length} span(s) with crossing or route context review cues — list filtered for QA scan; click again to reset`;
        }
        this._hideRecordPanel();
        this.refreshSpanListPanel({ onlyCrossingRisk: true });
        this._applySpanCrossingFocusMode(true);
      } else {
        this._spanCrossingFilterOnly = false;
        this.refreshSpanListPanel({ onlyCrossingRisk: false });
        this._applySpanCrossingFocusMode(false);
        const count = filtered.length;
        const recordWord = count !== 1 ? 'records' : 'record';
        const contextNote = value === 'replacement-proximity'
          ? ' (map evidence signals, not reviewed pairing count)'
          : '';
        if (this.filterNoteEl) {
          this.filterNoteEl.textContent = `Showing ${count} ${label} ${recordWord}${contextNote} for review scan — click again to reset`;
        }
        this._showRecordPanel(filtered, `${label} (${count})`);
      }
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
    if (value === 'ug-cable-missing-spec') {
      return this.featureData.filter((fd) => this.hasUgCableIncompleteSpec(fd.props));
    }
    if (value === 'clearance-crossings') {
      return this.featureData.filter((fd) => {
        if (!this.isContextRecord(fd.props)) return false;
        if (this.isClearanceCrossing(fd.props)) return true;
        const links = fd.props.span_crossing_links || [];
        return links.some((l) => {
          const t = String(l.crossing_tier || '').toLowerCase();
          return t === 'high' || t === 'medium';
        });
      });
    }
    return this.featureData;
  }

  currentFilteredFeatureData() {
    if (!this.activeFilter) return this.featureData;
    if (this.activeFilterMode === 'focus' && this.activeFilter === 'span-crossing-risk') {
      return this.featureData;
    }
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
    this.applyAngleHighlightState();
  }

  passesLayerState(fd) {
    const props = fd.props || {};
    if (this.isThirdPartyInfrastructure(props)) return this.layerState.thirdparty;
    if (this.isContextRecord(props)) return this.layerState.context;
    if (this.isStayOrAnchor(props)) return this.layerState.stays;
    if (this.isExistingPole(props)) return this.layerState.existing;
    if (this.isProposedPole(props)) return this.layerState.proposed;
    return true;
  }

  angleHighlightCount() {
    return this.featureData.filter((fd) => this.isAnglePole(fd.props)).length;
  }

  applyAngleHighlightState() {
    const showAngleHighlights = Boolean(this.layerState.angle);
    for (const fd of this.featureData) {
      if (!this.isAnglePole(fd.props)) continue;
      const el = fd.marker?.getElement?.();
      if (el) el.classList.toggle('angle-highlight-hidden', !showAngleHighlights);
    }
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
      'replacement-proximity': 'Replacement pairing signal',
      'missing-height': 'Existing pole missing measured height',
      'existing-poles': 'Existing pole',
      'proposed-poles': 'Proposed pole',
      'angle-poles': 'Angle pole',
      'stays-anchors': 'Stay / anchor',
      'context-crossings': 'Context / crossing',
      'missing-specification': 'Proposed pole missing specification',
      'angle-missing-stay': 'Angle pole missing stay evidence',
      'span-anomalies': 'Span anomaly',
      'span-crossing-risk': 'Span crossing / context review',
      'ug-cable-missing-spec': 'UG cable record missing specification',
      'clearance-crossings': 'Crossing needing clearance review',
      'records-with-remarks': 'Record with survey remarks',
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
    return this.classifyRouteSpanAnomaly(props).causes.length > 0;
  }

  hasUgCableIncompleteSpec(props) {
    if (props.is_underground !== true) return false;
    const hasCableType = this.hasValue(props.cable_type)
      || (props.cable_detail && typeof props.cable_detail === 'object' && props.cable_detail.name);
    const hasBurial = this.hasValue(props.burial_depth_m);
    return !hasCableType || !hasBurial;
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
      return '<div class="popup-row" style="color:#92400e;font-weight:700;">⚠️ Angle pole — stay evidence gap. Check field notes, photos or plan evidence.</div>';
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
    const designSections = this.buildDesignDecisionSections(props, status, lat, lon);
    const popupContract = this.popupSchemaContractRole(assetKind);
    if (popupContract) {
      return this.buildContractPopupHtml(props, status, lat, lon, assetKind, title, designSections, popupContract);
    }
    const sections = this.legacyPointPopupSections(assetKind, props, status, lat, lon);
    return this.buildLegacyPointPopupHtml(assetKind, title, designSections, sections, props);
  }

  buildLegacyPointPopupHtml(assetKind, title, designSections, sections, props) {
    const emptySectionSummary = {
      'Equipment & pole-top': 'No pole-mounted equipment inferred from current fields.',
      'Physical': 'Pole class, material, lean and foundation not fully specified in this export.',
      'Mechanical': 'Stay / mechanical evidence is not explicit in the current export.',
      'Specification': 'Pole class, material and design height not fully specified.',
      'Evidence': 'Surveyor, date and GNSS/photo references are not fully recorded in this export.',
    };
    const condenseable = new Set(Object.keys(emptySectionSummary));
    const mapSection = (section) => {
      let rows = section.rows;
      if (condenseable.has(section.title)) {
        rows = this.condenseVacuousPopupRows(rows, emptySectionSummary[section.title]);
      }
      return this.popupSection(section.title, rows);
    };
    return `
      <div class="asset-popup asset-popup-${assetKind}">
        <div class="popup-title">${title}</div>
        ${designSections.map(mapSection).join('')}
        ${sections.map(mapSection).join('')}
        ${this.rawTechnicalDetailsBlock(props)}
      </div>
    `;
  }

  legacyPointPopupSections(assetKind, props, status, lat, lon) {
    return assetKind === 'thirdparty'
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
  }

  popupSchemaContractRole(assetKind) {
    const roles = this._mapMeta?.popup_schema_contract?.roles;
    if (!roles || typeof roles !== 'object') return null;
    const roleKey = assetKind === 'thirdparty' ? 'third_party' : assetKind;
    const roleContract = roles[roleKey];
    if (!roleContract || !Array.isArray(roleContract.sections)) return null;
    return roleContract;
  }

  buildContractPopupHtml(props, status, lat, lon, assetKind, title, designSections, contract) {
    const rendered = [];
    for (const section of contract.sections || []) {
      if (section.kind === 'banner') {
        if (designSections.length > 0) {
          rendered.push(...designSections.map((designSection) => this.popupSection(designSection.title, designSection.rows)));
        }
        continue;
      }
      if (section.kind === 'collapsed' && section.id === 'raw_technical') {
        const rawBlock = this.rawTechnicalDetailsBlock(props);
        if (rawBlock) rendered.push(rawBlock);
        continue;
      }
      let rows = this.contractSectionRows(section, props, status, lat, lon, assetKind);
      if (section.kind === 'condenseable') {
        rows = this.condenseVacuousPopupRows(rows, section.blank_state_text || 'No popup fields available.');
      }
      if (!rows || rows.filter(Boolean).length === 0) continue;
      rendered.push(this.popupSection(section.title, rows));
    }
    return `
      <div class="asset-popup asset-popup-${assetKind}">
        <div class="popup-title">${title}</div>
        ${rendered.join('')}
      </div>
    `;
  }

  contractSectionRows(section, props, status, lat, lon, assetKind) {
    const role = assetKind === 'thirdparty' ? 'third_party' : assetKind;
    switch (section.id) {
      case 'identity':
        return this.identityRows(props, status, this.contractFallbackType(role, props));
      case 'physical_evidence':
        return this.physicalRows(props, role === 'proposed' ? 'proposed' : role === 'angle' ? 'angle' : 'existing');
      case 'mechanical':
        return this.mechanicalRows(props, role === 'angle');
      case 'equipment_pole_top':
        return this.equipmentDetailRows(props);
      case 'network_links':
        return this.connectivityRows(props);
      case 'survey_metadata_evidence':
        return this.surveyMetadataEvidenceRows(props);
      case 'location':
        return this.locationRows(props, lat, lon);
      case 'source_confidence':
        return this.sourceConfidenceRows(props);
      case 'lifecycle_design':
        return this.lifecycleRows(props);
      case 'qa_review':
        return this.qaRows(props);
      case 'specification':
        return this.specificationRows(props);
      case 'design_requirements':
        return this.designRequirementRows(props);
      case 'crossing_details':
        return this.crossingRows(props);
      case 'stay_details':
        return this.stayDetailRows(props);
      default:
        return [];
    }
  }

  contractFallbackType(role, props) {
    if (role === 'proposed') return 'Proposed Pole';
    if (role === 'angle') return 'Angle Pole';
    if (role === 'stay') return 'Stay / Anchor';
    if (role === 'context') return 'Context / Crossing';
    if (role === 'third_party') return props.popup_type_label || 'Third-Party Infrastructure';
    return 'Existing Pole';
  }

  buildDesignDecisionSections(props, status, lat, lon) {
    const sections = [];
    sections.push(...this.legacyDataWarningSections(props));
    sections.push(...this.heightEvidenceAlertSections(props));
    const audit = props.replacement_pair_audit;
    if (audit && typeof audit === 'object') {
      const pct = audit.confidence_pct != null ? String(audit.confidence_pct) : '';
      const rows = [
        this.popupRow('Replacement pair', `${this.displayValue(audit.ex_pole_id)} → ${this.displayValue(audit.pr_pole_id)}`, 'info'),
        this.popupRow('Match confidence', `${pct}% — ${this.displayValue(audit.match_type)}`, Number(pct) >= 75 ? 'ok' : 'warning', this.displayValue(audit.match_type_detail)),
        this.popupRow('Review status', audit.review_status || 'unconfirmed', 'warning', 'Confirm on designer review page before construction.'),
      ];
      sections.push({ title: 'Design focus — replacement pairing', rows });
    }
    if (this.isContextRecord(props)) {
      const ca = props.context_crossing_assessment || {};
      const cp = props.context_type_profile || {};
      const rows = [];
      if (cp.owner) rows.push(this.popupRow('Context owner', cp.owner, 'info'));
      if (ca.risk_level) {
        rows.push(this.popupRow('Crossing risk', ca.risk_level, ca.risk_level === 'high' ? 'warning' : 'info'));
      }
      if (ca.designer_action) {
        rows.push(this.popupRow('Designer action', ca.designer_action, 'warning'));
      }
      const nlink = (props.span_crossing_links || []).length;
      if (nlink) rows.push(this.popupRow('Span links (survey corridor)', String(nlink), 'info'));
      if (rows.length) sections.push({ title: 'Design focus — crossing / context', rows });
    }
    if (this.isAnglePole(props)) {
      if (props.stay_evidence_status === 'missing') {
        sections.push({
          title: 'Design focus — stay / angle',
          rows: [this.popupRow('Stay evidence', 'missing — check field notes, photos, or plan', 'warning')],
        });
      } else if (props.stay_evidence_status === 'captured') {
        const st = Array.isArray(props.stay_types) && props.stay_types.length > 0
          ? props.stay_types.join(', ')
          : 'Captured';
        sections.push({
          title: 'Design focus — stay / angle',
          rows: [this.popupRow('Stay evidence', st, 'ok')],
        });
      }
    }
    return sections;
  }

  rawTechnicalDetailsBlock(props) {
    const rawPairs = [
      ['support_schema_role', props.support_schema_role],
      ['primary_type', props.primary_type],
      ['asset_intent', props.asset_intent],
      ['lifecycle_state', props.lifecycle_state],
      ['replacement_status', props.replacement_status],
      ['linked_support_id', props.linked_support_id],
      ['match_role', props.match_role],
      ['gnss_fix_type', props.gnss_fix_type],
      ['horizontal_accuracy_m', props.horizontal_accuracy_m],
      ['vertical_accuracy_m', props.vertical_accuracy_m],
    ];
    const rows = [];
    for (const [k, v] of rawPairs) {
      if (v != null && v !== '') rows.push(this.popupRow(k, String(v), 'info'));
    }
    if (props.classification_basis != null && props.classification_basis !== '') {
      const b = props.classification_basis;
      rows.push(this.popupRow('classification_basis', typeof b === 'object' ? JSON.stringify(b) : String(b), 'info'));
    }
    if (Array.isArray(props.classification_warnings) && props.classification_warnings.length > 0) {
      rows.push(this.popupRow('classification_warnings', props.classification_warnings.join('; '), 'info'));
    }
    if (rows.length === 0) return '';
    const inner = rows.join('');
    return `<details class="popup-raw-details"><summary>Raw / technical fields</summary>${inner}</details>`;
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
      { title: 'Identity', rows: this.identityRows(props, status, 'Existing Pole') },
      { title: 'Physical', rows: this.physicalRows(props, 'existing') },
      { title: 'Equipment & pole-top', rows: this.equipmentDetailRows(props) },
      { title: 'Network links', rows: this.connectivityRows(props) },
      { title: 'Survey metadata', rows: this.surveyMetadataRows(props) },
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
    const prov = sourceConf.provenance;
    const conf = sourceConf.confidence || 'unknown';
    const note = sourceConf.designer_note || '';
    const geomHint = sourceConf.geometry_trust
      ? `Geometry trust: ${this.formatGeometryTrust(sourceConf.geometry_trust)}.`
      : '';
    const banner = (title, action, detail, status = 'warning') => ({
      title,
      rows: [
        this.popupRow('Designer note', action, status, [detail, note, geomHint].filter(Boolean).join(' ')),
      ],
    });

    switch (prov) {
      case 'legacy_map_data':
        return [banner(
          'Source cue — legacy map data',
          'Field-verify geometry and attributes before relying on them for clearance or structure design.',
          'Coordinates and labels may pre-date the surveyed job.',
        )];
      case 'dno_gis_import':
        return [banner(
          'Source cue — DNO GIS import',
          'Treat as network reference geometry unless this point was tied to contemporaneous survey evidence.',
          'GIS lineage can omit site-specific offsets.',
          conf === 'high' ? 'info' : 'warning',
        )];
      case 'digitised_from_drawing':
        return [banner(
          'Source cue — digitised drawing / plan',
          'Confirm scale, revision, and any offsets against GNSS survey before using for clearance.',
          'Digitisation introduces plan-to-ground uncertainty.',
        )];
      case 'inferred':
        return [banner(
          'Source cue — inferred or calculated',
          'Do not treat inferred attributes as surveyed fact without independent confirmation.',
          'Includes connectivity or model-derived values.',
        )];
      case 'proposed_by_design':
        return [banner(
          'Source cue — design proposal',
          'Design intent only — not evidence of as-built or surveyed field state.',
          '',
          'info',
        )];
      case 'unknown':
        if (conf === 'low') {
          return [banner(
            'Source cue — unknown / low confidence',
            'Establish provenance (field vs plan vs import) before high-stakes decisions.',
            '',
          )];
        }
        return [];
      default:
        return [];
    }
  }

  heightEvidenceAlertSections(props) {
    const kind = this.popupAssetKind(props);
    if (!['existing', 'angle'].includes(kind)) {
      return [];
    }
    const heightConf = props.height_confidence || {};
    if (!['warning', 'blocker', 'fail', 'review'].includes(heightConf.status)) {
      return [];
    }
    return [
      {
        title: 'Height Evidence',
        rows: [
          this.popupRow(
            'Measured Height',
            this.hasValue(props.measured_height_m ?? props.height)
              ? `${this.displayValue(props.measured_height_m ?? props.height)}m`
              : 'evidence gap - not captured in current export',
            heightConf.status,
            'Existing pole height is missing survey evidence; clearance checks cannot rely on this record.',
          ),
          this.popupRow('Height Source', props.height_source || 'evidence gap - source not recorded', props.height_source ? 'info' : 'warning'),
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
      { title: 'Survey metadata', rows: this.surveyMetadataRows(props) },
      { title: 'QA / Review', rows: this.qaRows(props) },
    ];
  }

  proposedPopupSections(props, status, lat, lon) {
    return [
      { title: 'Identity', rows: this.identityRows(props, status, 'Proposed Pole') },
      { title: 'Specification', rows: this.specificationRows(props) },
      { title: 'Third-Party Attachments', rows: this.attachmentsRows(props) },
      { title: 'Design Requirements', rows: this.designRequirementRows(props) },
      { title: 'Equipment & pole-top', rows: this.equipmentDetailRows(props) },
      { title: 'Network links', rows: this.connectivityRows(props) },
      { title: 'Survey metadata', rows: this.surveyMetadataRows(props) },
      { title: 'Location', rows: this.locationRows(props, lat, lon) },
      { title: 'Evidence', rows: this.evidenceRows(props) },
      { title: 'Source & Confidence', rows: this.sourceConfidenceRows(props) },
      { title: 'Lifecycle / Design', rows: this.lifecycleRows(props) },
      { title: 'QA / Review', rows: this.qaRows(props) },
    ];
  }

  anglePopupSections(props, status, lat, lon) {
    return [
      { title: 'Identity', rows: this.identityRows(props, status, 'Angle Pole') },
      { title: 'Mechanical', rows: this.mechanicalRows(props, true) },
      { title: 'Third-Party Attachments', rows: this.attachmentsRows(props) },
      { title: 'Physical', rows: this.physicalRows(props, 'angle') },
      { title: 'Equipment & pole-top', rows: this.equipmentDetailRows(props) },
      { title: 'Network links', rows: this.connectivityRows(props) },
      { title: 'Survey metadata', rows: this.surveyMetadataRows(props) },
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
      { title: 'Network links', rows: this.connectivityRows(props) },
      { title: 'Survey metadata', rows: this.surveyMetadataRows(props) },
      { title: 'Location', rows: this.locationRows(props, lat, lon) },
      { title: 'Evidence', rows: this.evidenceRows(props) },
      { title: 'QA / Review', rows: this.qaRows(props) },
    ];
  }

  contextPopupSections(props, status, lat, lon) {
    return [
      { title: 'Identity', rows: this.identityRows(props, status, 'Context / Crossing') },
      { title: 'Crossing Details', rows: this.crossingRows(props) },
      { title: 'Survey metadata', rows: this.surveyMetadataRows(props) },
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
      this.popupRow('Circuit ID', props.circuit_id || 'not recorded in export', props.circuit_id ? 'ok' : 'info'),
      this.popupRow('Year Installed', props.year_installed || 'not recorded in export', props.year_installed ? 'ok' : 'info'),
      this.popupRow('Function', this.isAnglePole(props) ? 'Angle' : props.record_role),
      this.popupRow('Status', this.statusText(status), this.statusToFieldStatus(status)),
      this.popupRow('Role', props.asset_intent || props.record_role || 'mapped survey record'),
    ];
  }

  physicalRows(props, mode) {
    const isProposedMode = mode === 'proposed';
    const rawHeight = mode === 'proposed'
      ? (props.proposed_height_m ?? props.height)
      : (props.measured_height_m ?? props.height);
    const hasHeight = this.hasValue(rawHeight);
    const heightConf = props.height_confidence || {};
    return [
      this.popupRow(
        mode === 'proposed' ? 'Proposed Height' : 'Measured Height',
        hasHeight ? `${rawHeight}m` : isProposedMode ? 'design decision pending' : 'evidence gap - not captured in current export',
        heightConf.status || (hasHeight ? 'ok' : isProposedMode ? 'info' : 'blocker'),
        heightConf.warning || (isProposedMode
          ? 'Proposed height is a future design specification, not a survey capture gap.'
          : 'Existing pole height is missing survey evidence; clearance checks cannot rely on this record.'),
      ),
      this.popupRow(
        'Height Source',
        props.height_source || (isProposedMode ? 'not applicable until design height is specified' : 'evidence gap - source not recorded'),
        props.height_source ? 'info' : 'warning',
        props.height_source
          ? this.explainHeightSource(props.height_source)
          : isProposedMode
            ? 'Design height source will be known when the proposed specification is confirmed.'
            : 'Height measurement method not recorded - reliability unknown.',
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
      this.popupRow(
        'Pole Class',
        props.pole_class || (isProposedMode ? 'design decision pending' : 'evidence gap - not captured in current export'),
        props.pole_class ? 'ok' : 'review',
        props.pole_class ? '' : isProposedMode
          ? 'Specify pole strength/class before design issue.'
          : 'Confirm from field notes, pole plate, or asset records.',
      ),
      this.popupRow(
        'Material / Condition',
        `${props.material || (isProposedMode ? 'design decision pending' : 'evidence gap - material unknown')} / ${props.condition || (isProposedMode ? 'not applicable yet' : 'evidence gap - condition not evidenced')}`,
        props.material || props.condition ? 'ok' : 'review',
      ),
      this.popupRow(
        'Lean',
        props.lean_severity || props.lean_direction
          ? `${this.displayValue(props.lean_severity)} ${this.displayValue(props.lean_direction)}`.trim()
          : isProposedMode ? 'not applicable yet' : 'evidence gap - lean not assessed in digital file',
        props.lean_severity || props.lean_direction ? 'warning' : 'info',
      ),
      this.popupRow(
        'Defects',
        props.defect_type || (isProposedMode ? 'not applicable yet' : 'evidence gap - defect evidence not supplied'),
        props.defect_type ? 'warning' : 'info',
      ),
      this.popupRow(
        'Foundation',
        props.foundation_type || (isProposedMode ? 'design decision pending' : 'evidence gap - foundation not recorded'),
        props.foundation_type ? 'ok' : 'info',
      ),
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
        props.specification || 'design decision pending',
        hasSpec ? 'ok' : 'review',
        hasSpec ? '' : 'Future pole specification required; this is not a field-capture error.',
      ),
      this.popupRow('Pole Class', props.pole_class || 'design decision pending', props.pole_class ? 'ok' : 'review'),
      this.popupRow('Material', props.material || 'design decision pending', props.material ? 'ok' : 'review'),
      this.popupRow('Condition', props.condition || 'not applicable yet', 'info'),
      this.popupRow('Design Height', props.proposed_height_m != null ? `${props.proposed_height_m}m` : (props.height ? `${props.height}m` : 'design decision pending'), props.proposed_height_m != null || props.height ? 'ok' : 'review'),
    ];
  }

  electricalRows(props, opts = {}) {
    const includeEquipment = opts.includeEquipment !== false;
    const rows = [];
    const isUg = props.is_underground === true;
    const routeKind = isUg ? 'underground cable trace' : 'overhead span';
    const voltageLabel =
      props.voltage_detail && props.voltage_detail.label
        ? String(props.voltage_detail.label)
        : '';

    rows.push(
      this.popupRow(
        'Line Voltage',
        props.voltage || `not recorded - circuit voltage not supplied for this ${routeKind}`,
        props.voltage ? 'ok' : 'review',
        voltageLabel,
      ),
    );

    if (!isUg) {
      rows.push(
        this.popupRow(
          'Conductor Type',
          props.conductor_type || 'not recorded - conductor specification not supplied for this span',
          props.conductor_type ? 'ok' : 'review',
          props.conductor_detail && props.conductor_detail.name ? String(props.conductor_detail.name) : '',
        ),
      );
      rows.push(
        this.popupRow(
          'Conductor Size',
          props.conductor_size || 'not recorded - conductor size not supplied for this span',
          props.conductor_size ? 'ok' : 'info',
          props.conductor_size_description ? String(props.conductor_size_description) : '',
        ),
      );
      rows.push(
        this.popupRow(
          'Phase Configuration',
          props.phase_count || 'not recorded - phase configuration not supplied for this span',
          props.phase_count ? 'ok' : 'info',
          props.phase_detail && props.phase_detail.description
            ? String(props.phase_detail.description)
            : '',
        ),
      );
      const ct = String(props.conductor_type || '').toUpperCase();
      let form = 'Not specified';
      if (ct.includes('BARE')) form = 'Bare conductor';
      else if (ct.includes('ABC')) form = 'Aerial bundled cable (ABC)';
      else if (ct.includes('COVERED')) form = 'Covered conductor';
      rows.push(this.popupRow('Conductor Form', form, 'info'));
    } else {
      rows.push(
        this.popupRow(
          'Cable Type',
          props.cable_type || 'not recorded - cable specification not supplied for this trace',
          props.cable_type ? 'ok' : 'review',
          props.cable_detail && props.cable_detail.name ? String(props.cable_detail.name) : '',
        ),
      );
      rows.push(
        this.popupRow(
          'Cable Size',
          props.cable_size || props.conductor_size || 'not recorded - cable size not supplied for this trace',
          props.cable_size || props.conductor_size ? 'ok' : 'info',
          props.conductor_size_description ? String(props.conductor_size_description) : '',
        ),
      );
      rows.push(
        this.popupRow(
          'Cores/Phases',
          props.cores_phases || props.phase_count || 'not recorded - cores/phases not supplied for this trace',
          props.cores_phases || props.phase_count ? 'ok' : 'info',
          props.phase_detail && props.phase_detail.description
            ? String(props.phase_detail.description)
            : '',
        ),
      );
    }

    if (includeEquipment) {
      const equipment = Array.isArray(props.equipment) && props.equipment.length > 0
        ? props.equipment.join(', ')
        : props.equipment;
      rows.push(
        this.popupRow(
          'Mounted Equipment',
          equipment || 'none inferred from current fields',
          equipment ? 'ok' : 'info',
        ),
      );
      rows.push(
        this.popupRow(
          'Equipment Rating',
          props.equipment_rating || 'not recorded in current export',
          props.equipment_rating ? 'ok' : 'info',
        ),
      );
    }
    return rows;
  }

  equipmentDetailRows(props) {
    const rows = [];
    const cats = Array.isArray(props.equipment_categories) && props.equipment_categories.length > 0
      ? props.equipment_categories.join(', ')
      : '';
    const ptc = props.equipment_primary_category || '';
    rows.push(this.popupRow('Equipment categories', cats || 'none inferred from current fields', cats ? 'ok' : 'info'));
    rows.push(this.popupRow('Primary equipment', ptc || 'none inferred from current fields', ptc ? 'ok' : 'info'));
    const kvaLabel = props.equipment_kva_label || (props.equipment_kva != null ? `${props.equipment_kva} kVA` : '');
    rows.push(this.popupRow('Parsed kVA', kvaLabel || 'not parsed', kvaLabel ? 'ok' : 'info'));
    rows.push(
      this.popupRow(
        'Voltage ratio',
        props.equipment_voltage_ratio || 'not recorded in digital file',
        props.equipment_voltage_ratio ? 'ok' : 'info',
      ),
    );
    const ptd = props.pole_top_detail && props.pole_top_detail.label ? String(props.pole_top_detail.label) : '';
    rows.push(
      this.popupRow(
        'Pole-top arrangement',
        ptd || props.pole_top_arrangement || 'not recorded in digital file',
        ptd || props.pole_top_arrangement ? 'ok' : 'info',
        props.pole_top_detail && props.pole_top_detail.description ? String(props.pole_top_detail.description) : '',
      ),
    );
    rows.push(
      this.popupRow('Insulator type', props.insulator_type || 'not recorded in digital file', props.insulator_type ? 'ok' : 'info'),
    );
    rows.push(
      this.popupRow(
        'Crossarm configuration',
        props.crossarm_configuration || 'not recorded in digital file',
        props.crossarm_configuration ? 'ok' : 'info',
      ),
    );
    rows.push(
      this.popupRow('Earthing', props.earthing_status || 'not recorded in digital file', props.earthing_status ? 'ok' : 'info'),
    );
    rows.push(
      this.popupRow(
        'Asset plate / label',
        props.asset_plate_id || 'not recorded in digital file',
        props.asset_plate_id ? 'ok' : 'info',
      ),
    );
    let mount = 'not recorded in digital file';
    if (props.equipment_mounting === 'pole') mount = 'Pole-mounted';
    else if (props.equipment_mounting === 'ground') mount = 'Ground-mounted';
    rows.push(this.popupRow('Equipment mounting', mount, props.equipment_mounting ? 'ok' : 'info'));
    return rows;
  }

  connectivityRows(props) {
    const rows = [];
    rows.push(
      this.popupRow('From support', props.from_support_id || '—', props.from_support_id ? 'ok' : 'info'),
    );
    rows.push(this.popupRow('To support', props.to_support_id || '—', props.to_support_id ? 'ok' : 'info'));
    rows.push(
      this.popupRow(
        'Parent pole (stay / anchor)',
        props.connectivity_parent_pole || props.parent_support_id || props.linked_pole_id || '—',
        props.connectivity_parent_pole || props.parent_support_id || props.linked_pole_id ? 'ok' : 'info',
      ),
    );
    rows.push(
      this.popupRow(
        'Parent structure',
        props.parent_structure_id || '—',
        props.parent_structure_id ? 'ok' : 'info',
      ),
    );
    rows.push(
      this.popupRow(
        'Cable from asset',
        props.cable_from_asset_id || '—',
        props.cable_from_asset_id ? 'ok' : 'info',
      ),
    );
    rows.push(
      this.popupRow(
        'Cable to asset',
        props.cable_to_asset_id || '—',
        props.cable_to_asset_id ? 'ok' : 'info',
      ),
    );
    return rows;
  }

  surveyMetadataRows(props) {
    const rows = [];
    rows.push(this.popupRow('Job / scheme ref', props.survey_job_ref || 'not recorded in export', props.survey_job_ref ? 'ok' : 'info'));
    rows.push(this.popupRow('Surveyor', props.surveyor || 'not recorded in export', props.surveyor ? 'ok' : 'info'));
    rows.push(this.popupRow('Survey date', props.survey_date || 'not recorded in export', props.survey_date ? 'ok' : 'info'));
    rows.push(
      this.popupRow(
        'Survey equipment',
        props.equipment_used || 'not recorded in export',
        props.equipment_used ? 'ok' : 'info',
      ),
    );
    rows.push(
      this.popupRow(
        'Capture method',
        props.capture_method_label || props.capture_method || 'not recorded in export',
        props.capture_method_label || props.capture_method ? 'ok' : 'info',
      ),
    );
    const gsum = props.gnss_accuracy_summary || props.gnss_accuracy;
    rows.push(this.popupRow('GNSS / accuracy', gsum || 'not recorded - positional confidence unknown', gsum ? 'ok' : 'info'));
    if (props.horizontal_accuracy_m != null || props.vertical_accuracy_m != null) {
      const h = props.horizontal_accuracy_m != null ? `H ±${props.horizontal_accuracy_m} m` : '';
      const v = props.vertical_accuracy_m != null ? `V ±${props.vertical_accuracy_m} m` : '';
      rows.push(this.popupRow('Accuracy (parsed)', [h, v].filter(Boolean).join(', ') || '—', 'info'));
    }
    rows.push(
      this.popupRow(
        'Survey limitations',
        props.survey_limitations || 'not recorded in current export',
        props.survey_limitations ? 'warning' : 'info',
      ),
    );
    return rows;
  }

  surveyMetadataEvidenceRows(props) {
    const rows = [...this.surveyMetadataRows(props)];
    const photos = this.photoEvidenceText(props);
    rows.push(this.popupRow('Photo Evidence', photos, photos === 'no linked photo references in current export' ? 'info' : 'ok'));
    rows.push(
      this.popupRow(
        'Remarks',
        props.name && props.name !== props.id ? props.name : 'not recorded in export',
        props.name && props.name !== props.id ? 'ok' : 'info',
      ),
    );
    return rows;
  }

  mechanicalRows(props, prominent = false) {
    const stayEvidence = this.stayEvidenceSummary(props);
    const stayTypes = Array.isArray(props.stay_types) && props.stay_types.length > 0
      ? props.stay_types.join(', ')
      : props.stay_type;
    return [
      this.popupRow(
        'Stay Evidence',
        stayEvidence.value,
        stayEvidence.status === 'ok' ? 'ok' : prominent && stayEvidence.status !== 'info' ? 'warning' : stayEvidence.status,
        stayEvidence.detail,
      ),
      this.popupRow(
        'Stay Type',
        stayTypes || (stayEvidence.kind === 'captured' ? 'captured stay record - type not supplied' : stayEvidence.kind === 'inferred' ? 'inferred - type not supplied' : 'evidence gap - stay configuration unknown'),
        stayTypes ? 'ok' : stayEvidence.kind === 'missing' && prominent ? 'warning' : 'info',
      ),
      this.popupRow('Stay Bearing', props.stay_bearing || 'not recorded in current export', props.stay_bearing ? 'ok' : 'info'),
      this.popupRow('Anchor Details', props.anchor_details || 'not linked in current export', props.anchor_details ? 'ok' : 'info'),
      this.popupRow('Route Deviation', props.route_deviation_deg ? `${props.route_deviation_deg}°` : 'not calculated', props.route_deviation_deg ? 'warning' : 'info'),
      this.popupRow('Action', prominent ? 'Verify stay configuration before design' : 'Check field notes if stay evidence is expected', prominent ? 'warning' : 'info'),
    ];
  }

  stayEvidenceSummary(props) {
    const stayStatus = String(props.stay_evidence_status || '').toLowerCase();
    const stayTypes = Array.isArray(props.stay_types) && props.stay_types.length > 0
      ? props.stay_types.join(', ')
      : props.stay_type;
    const stayPresent = String(props.stay_present || '').trim();
    if (stayStatus === 'captured') {
      return {
        kind: 'captured',
        value: `captured evidence: ${stayTypes || stayPresent || 'stay record'}`,
        status: 'ok',
        detail: this.nearestStayDetail(props) || 'Captured from stay/anchor record or explicit survey evidence.',
      };
    }
    if (stayStatus === 'inferred') {
      return {
        kind: 'inferred',
        value: `inferred evidence: ${stayTypes || stayPresent || 'stay likely from current fields'}`,
        status: 'review',
        detail: 'Inferred from current fields; confirm against field notes, photos, or plan evidence.',
      };
    }
    if (stayStatus === 'missing') {
      return {
        kind: 'missing',
        value: 'evidence gap - no captured stay evidence in current export',
        status: 'warning',
        detail: 'Angle pole - check field notes, photos, or plan evidence before design reliance.',
      };
    }
    if (stayPresent && !/^no|false|none$/i.test(stayPresent)) {
      return {
        kind: 'inferred',
        value: `survey field indicates stay: ${stayPresent}`,
        status: 'review',
        detail: 'Stay presence is indicated, but linked stay/anchor evidence is not explicit.',
      };
    }
    return {
      kind: 'absent',
      value: 'not indicated by current data',
      status: 'info',
      detail: 'No captured or inferred stay evidence in the current export.',
    };
  }

  stayDetailRows(props) {
    return [
      this.popupRow('Type', props.structure_type || 'Stay / anchor'),
      this.popupRow(
        'Parent pole',
        props.connectivity_parent_pole || props.parent_support_id || props.linked_pole_id || 'not linked in current export',
        props.connectivity_parent_pole || props.parent_support_id || props.linked_pole_id ? 'ok' : 'info',
      ),
      this.popupRow('Direction', props.stay_bearing || 'not recorded in current export', props.stay_bearing ? 'ok' : 'info'),
      this.popupRow('Configuration', props.stay_configuration || 'not recorded in current export', props.stay_configuration ? 'ok' : 'info'),
      this.popupRow('Nearest Pole', this.nearestStayDetail(props) || 'not calculated', props.nearest_stay_distance_m ? 'ok' : 'info'),
    ];
  }

  designRequirementRows(props) {
    return [
      this.popupRow('Action Required', props.action_required || 'not specified yet', props.action_required ? 'warning' : 'info'),
      this.popupRow('Clearance', this.isClearanceCrossing(props) ? this.contextReviewLabel(props) : 'check route context / plans', 'info'),
      this.popupRow('Stay Required', this.isAnglePole(props) ? 'review angle/stay evidence' : 'not indicated by current data', this.isAnglePole(props) ? 'warning' : 'info'),
      this.popupRow('Access', props.access_constraint || 'check field notes / plans', 'info'),
      this.popupRow('Design Note', props.name && props.name !== props.id ? props.name : 'not specified yet', props.name && props.name !== props.id ? 'ok' : 'info'),
    ];
  }

  crossingRows(props) {
    const links = Array.isArray(props.span_crossing_links) ? props.span_crossing_links : [];
    const linkRows = [];
    if (links.length) {
      const dists = links.map((l) => Number(l.distance_m)).filter((n) => !Number.isNaN(n));
      const minD = dists.length ? Math.min(...dists) : null;
      const tiers = links.map((l) => String(l.crossing_tier || '').toLowerCase());
      const hasHigh = tiers.some((t) => t === 'high');
      const hasMed = tiers.some((t) => t === 'medium');
      const spanBits = links.slice(0, 3).map((l) => {
        const a = l.from_point_id || '?';
        const b = l.to_point_id || '?';
        return `${a}→${b}`;
      });
      const more = links.length > 3 ? ` (+${links.length - 3} more)` : '';
      linkRows.push(this.popupRow(
        'Span corridor links (survey)',
        `${links.length} span segment(s) within correlation: ${spanBits.join(', ')}${more}`,
        'info',
      ));
      if (minD != null) {
        linkRows.push(this.popupRow(
          'Closest corridor distance',
          `${minD.toFixed(1)} m (plan) from this point to a matched span`,
          'info',
        ));
      }
      const confText = hasHigh
        ? 'Higher — at least one linked hit used a high crossing tier (treat as clearance-sensitive).'
        : hasMed
          ? 'Moderate — medium-tier context may need coordination.'
          : 'General proximity — low tier; confirm whether this record constrains the line design.';
      linkRows.push(this.popupRow('Correlation confidence', confText, hasHigh ? 'warning' : 'info'));
    }
    return [
      ...linkRows,
      this.popupRow('Priority', this.isClearanceCrossing(props) ? 'HIGH' : 'Review', this.isClearanceCrossing(props) ? 'warning' : 'info'),
      this.popupRow('Label', this.contextReviewLabel(props), this.isClearanceCrossing(props) ? 'warning' : 'info'),
      this.popupRow(
        'Clearance Measured',
        props.clearance_measured || 'not measured in current export',
        props.clearance_measured ? 'ok' : 'review',
        props.clearance_measured ? '' : 'Do not infer absence of clearance risk from a blank measurement.',
      ),
      this.popupRow('Distance from Route', props.distance_from_route_m ? `${props.distance_from_route_m}m` : 'not calculated', 'info'),
      this.popupRow('Action', this.isClearanceCrossing(props) ? 'Measure statutory clearance to crossing surface' : 'Review site constraint before design', 'warning'),
    ];
  }

  locationRows(props, lat, lon) {
    return [
      this.popupRow('Easting / Northing', props.easting ? `${props.easting}, ${props.northing}` : 'not recorded in export', props.easting ? 'ok' : 'info'),
      this.popupRow('Lat / Lon', `${lat.toFixed(5)}, ${lon.toFixed(5)}`, 'ok'),
      this.popupRow('Elevation', props.elevation != null && props.elevation !== '' ? `${props.elevation}m` : 'not recorded in export', props.elevation ? 'ok' : 'info'),
      this.popupRow('GNSS Accuracy', props.gnss_accuracy || 'not recorded - positional confidence unknown', props.gnss_accuracy ? 'ok' : 'info'),
    ];
  }

  evidenceRows(props) {
    const photos = this.photoEvidenceText(props);
    return [
      this.popupRow('Surveyed By', props.surveyor || 'not recorded in export', props.surveyor ? 'ok' : 'info'),
      this.popupRow('Survey Date', props.survey_date || 'not recorded in export', props.survey_date ? 'ok' : 'info'),
      this.popupRow('GNSS Accuracy', props.gnss_accuracy || 'not recorded - positional confidence unknown', props.gnss_accuracy ? 'ok' : 'info'),
      this.popupRow('Photo Evidence', photos, photos === 'no linked photo references in current export' ? 'info' : 'ok'),
      this.popupRow('Source Confidence', props.source_confidence || 'raw survey export', 'info'),
      this.popupRow('Remarks', props.name && props.name !== props.id ? props.name : 'not recorded in export', props.name && props.name !== props.id ? 'ok' : 'info'),
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
    if (rows.length === 0) rows.push(this.popupRow('QA Items', 'no QA items in current export', 'ok'));
    return rows;
  }

  popupSection(title, rows) {
    const renderedRows = rows.filter(Boolean).map(row => row).join('');
    const meta = this.popupSectionMeta(rows);
    const chipText = meta.blank ? 'Blank state' : this.popupSectionChipText(meta.status);
    const chipHtml = chipText
      ? `<span class="popup-section-chip status-${this.escapeHtml(meta.status)}">${this.escapeHtml(chipText)}</span>`
      : '';
    return `
      <div class="popup-section popup-section-${this.escapeHtml(meta.status)}${meta.blank ? ' popup-section-blank' : ''}" data-popup-section-status="${this.escapeHtml(meta.status)}">
        <div class="popup-section-header">
          <div class="popup-section-title">${this.escapeHtml(title)}</div>
          ${chipHtml}
        </div>
        ${renderedRows}
      </div>
    `;
  }

  popupRow(label, value, status = 'info', detail = '') {
    const display = this.displayValue(value);
    const isSummary = label === 'Summary';
    const emptyValue = this.isEmptyPopupDisplay(display);
    const rowClasses = [
      'popup-field',
      `status-${this.escapeHtml(status)}`,
      isSummary ? 'popup-field-summary' : '',
      emptyValue ? 'popup-field-empty' : '',
    ].filter(Boolean).join(' ');
    const detailHtml = detail ? `<div class="popup-field-detail">${this.escapeHtml(detail)}</div>` : '';
    const statusChip = this.popupFieldStatusChip(status, label, display);
    const statusChipHtml = statusChip ? `<span class="popup-field-status">${this.escapeHtml(statusChip)}</span>` : '';
    return `
      <div class="${rowClasses}" data-popup-label="${this.escapeHtml(label)}" data-popup-status="${this.escapeHtml(status)}">
        <div class="popup-field-topline">
          <div class="popup-field-label">${this.escapeHtml(label)}</div>
          ${statusChipHtml}
        </div>
        <div class="popup-field-value">${this.escapeHtml(display)}</div>
        ${detailHtml}
      </div>
    `;
  }

  popupSectionMeta(rows) {
    const statuses = ['blocker', 'fail', 'warning', 'review', 'info', 'ok'];
    const combined = (rows || []).filter(Boolean).join(' ');
    const match = statuses.find((status) => combined.includes(`status-${status}`)) || 'info';
    const blank = (rows || []).filter(Boolean).length === 1 && combined.includes('data-popup-label="Summary"');
    return { status: match === 'fail' ? 'blocker' : match, blank };
  }

  popupSectionChipText(status) {
    const labels = {
      blocker: 'Blocker',
      warning: 'Action',
      review: 'Review',
      info: 'Info',
      ok: 'Ready',
    };
    return labels[status] || '';
  }

  popupFieldStatusChip(status, label, display) {
    if (label === 'Summary') return 'Summary';
    if (this.isEmptyPopupDisplay(display) && (status === 'info' || status === 'review')) return 'Missing';
    const labels = {
      blocker: 'Blocker',
      fail: 'Blocker',
      warning: 'Action',
      review: 'Review',
      info: 'Info',
      ok: 'Ready',
    };
    return labels[status] || '';
  }

  isEmptyPopupDisplay(display) {
    const value = String(display || '').trim().toLowerCase();
    if (
      value.startsWith('not recorded')
      || value.startsWith('not supplied')
      || value.startsWith('evidence gap -')
      || value.startsWith('not linked')
    ) {
      return true;
    }
    return new Set([
      '—',
      'not captured',
      'none recorded',
      'not specified',
      'not specified yet',
      'design decision pending',
      'not linked',
      'not applicable',
      'not applicable yet',
      'not yet specified',
      'not inferred',
      'none inferred',
      'none inferred from current fields',
      'not parsed',
      'no linked photos',
      'no linked photo references in current export',
    ]).has(value);
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
    return photos.length > 0 ? photos.join(', ') : 'no linked photo references in current export';
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
      const reviewStatus = this.statusText(fd.status);

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
          <span style="font-size:0.75rem;font-weight:700;color:${statusColor};">${this.escapeHtml(reviewStatus)}</span>
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
