document.addEventListener('DOMContentLoaded', () => {
  const sel = document.getElementById('dno');
  const badge = document.getElementById('rulepackBadge');
  const details = document.getElementById('rulepackDetails');
  if(!sel) return;

  function setAuto(){
    if(details) details.innerHTML = '<p class="text-muted mb-0">Auto-detect will analyze your file.</p>';
    if(badge) badge.innerHTML = '';
  }

  async function fetchDetails(id){
    try{
      const res = await fetch(`/api/rulepacks/${id}`);
      if(!res.ok) throw new Error();
      const data = await res.json();
      if(details){
        details.innerHTML = `
          <h6>${data.rulepack_id || id}</h6><hr/>
          <pre class="bg-light p-2 rounded"><code>${escapeHtml(JSON.stringify(data.thresholds || data, null, 2))}</code></pre>`;
      }
      if(badge) badge.innerHTML = `<span class="badge bg-info">${id}</span>`;
    }catch{
      if(details) details.innerHTML = `<div class="alert alert-warning mb-0">Failed to load QA rule details</div>`;
      Toast?.show?.('Failed to load QA rule details','warn');
    }
  }

  sel.addEventListener('change', () => {
    const v = sel.value;
    if(!v){ setAuto(); Toast?.show?.('Applied QA Rules: Auto (detect)','info'); }
    else { fetchDetails(v); Toast?.show?.(`Applied QA Rules: ${v}`,'info'); }
  });

  function escapeHtml(s){ return (''+s).replace(/[&<>"]/g, c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c])); }
  // initial state
  if(!sel.value) setAuto(); else fetchDetails(sel.value);
});
