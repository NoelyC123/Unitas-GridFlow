// Minimal Bootstrap toast helper
(function(){
  function ensureContainer(){
    let c = document.getElementById('toastContainer');
    if(!c){
      c = document.createElement('div');
      c.id = 'toastContainer';
      c.className = 'toast-container position-fixed top-0 end-0 p-3';
      c.style.zIndex = '9999';
      document.body.appendChild(c);
    }
    return c;
  }
  function show(message, type='info', delay=4000){
    const c = ensureContainer();
    const el = document.createElement('div');
    el.className = `toast align-items-center text-bg-${map(type)} border-0`;
    el.setAttribute('role','alert'); el.setAttribute('aria-live','assertive'); el.setAttribute('aria-atomic','true');
    el.innerHTML = `<div class="d-flex"><div class="toast-body">${escape(message)}</div><button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast" aria-label="Close"></button></div>`;
    c.appendChild(el);
    const t = new bootstrap.Toast(el, { delay });
    t.show();
    el.addEventListener('hidden.bs.toast', ()=> el.remove());
  }
  function map(t){ return ({success:'success', error:'danger', warn:'warning', info:'info'})[t] || 'secondary'; }
  function escape(s){ return (''+s).replace(/[&<>"]/g, c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c])); }
  window.Toast = { show };
})();
