let map, layerGroup;
function initMap(jobId){
  map = L.map('map').setView([54.5, -4.0], 6);
  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',{
    attribution:'© OpenStreetMap contributors'
  }).addTo(map);
  layerGroup = L.featureGroup().addTo(map);
  load(jobId);
}
async function load(jobId){
  try{
    const r = await fetch(`/map/data/${jobId}`, { cache:'no-store' });
    if(!r.ok) throw new Error('failed to load map data');
    const gj = await r.json();
    (gj.features||[]).forEach(f => draw(f));
    const b = layerGroup.getBounds(); if(b.isValid()) map.fitBounds(b, {padding:[30,30]});
    // summary
    const m = gj.metadata || {};
    setText('jobIdDisplay', jobId);
    setText('poleCount', m.pole_count || 0);
    setText('spanCount', m.span_count || 0);
    setText('passCount', m.pass_count || m.qa_pass || 0);
    setText('warnCount', m.warn_count || m.qa_warn || 0);
    setText('failCount', m.fail_count || m.qa_fail || 0);
    if(m.rulepack_id) {
      const rb = document.getElementById('rulepackBadge');
      if(rb) rb.innerHTML = `<span class="badge bg-info">${m.rulepack_id}</span>`;
    }
    if(m.auto_normalized) Toast?.show?.('Info: Auto-normalized input', 'info');
  }catch(e){
    console.error(e); Toast?.show?.('Failed to load map data','error');
  }
}
function draw(feat){
  const g = feat.geometry, p = feat.properties || {};
  const color = qaColor(p.qa_status || p.QA || 'PASS');
  if(g?.type === 'Point'){
    const [lng, lat] = g.coordinates;
    const mk = L.circleMarker([lat,lng], { radius:6, color:'#fff', weight:2, fillColor:color, fillOpacity:0.9 });
    mk.bindPopup(popup(p)); mk.addTo(layerGroup);
  } else if(g?.type === 'LineString'){
    const latlngs = g.coordinates.map(([lng,lat])=> [lat,lng]);
    const ln = L.polyline(latlngs, { color, weight:3, opacity:0.9 });
    ln.bindPopup(popup(p)); ln.addTo(layerGroup);
  }
}
function qaColor(s){ return {PASS:'#28a745', WARN:'#ffc107', FAIL:'#dc3545'}[s] || '#28a745'; }
function popup(p){
  return `<div><strong>${p.name || p.id || 'Feature'}</strong><br/>
  Status: <span class="badge" style="background:${qaColor(p.qa_status||'PASS')}">${p.qa_status||'PASS'}</span></div>`;
}
function setText(id, val){ const el = document.getElementById(id); if(el) el.textContent = val; }
window.initMap = initMap;
