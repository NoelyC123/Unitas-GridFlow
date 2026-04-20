class UploadManager {
  constructor() {
    this.api = document.querySelector('meta[name="api-base-url"]')?.content || '/api';
    this.pollInterval = parseInt(document.querySelector('meta[name="poll-interval"]')?.content || '2000', 10);
    this.pollMax = parseInt(document.querySelector('meta[name="poll-max-attempts"]')?.content || '60', 10);
    this.file = document.getElementById('file');
    this.dno = document.getElementById('dno');
    this.btn = document.getElementById('btn-upload');
    this.out = document.getElementById('result');
    this.jobSpan = document.getElementById('res-job');
    this.mapBtn = document.getElementById('btn-map');
    this.pdfBtn = document.getElementById('btn-pdf');

    this.btn?.addEventListener('click', () => this.start());
  }

  async start() {
    try {
      if (!this.file?.files?.length) {
        Toast?.show?.('Choose a CSV file', 'warn');
        return;
      }

      const f = this.file.files[0];
      const jobId = 'J' + Math.floor(10000 + Math.random() * 90000);
      const key = `uploads/${jobId}/${f.name}`;

      // 1) Presign
      const ps = await this.jsonPOST(`${this.api}/presign`, {
        key,
        size: f.size,
        content_type: 'text/csv',
        multipart: false
      });

      if (ps.upload_type !== 'single') {
        throw new Error('multipart not enabled');
      }

      // 2) Upload file
      await this.put(ps.url, f, ps.headers || { 'Content-Type': 'text/csv' });

      // 3) Finalize import
      const bare = jobId.startsWith('J') ? jobId.slice(1) : jobId;
      const body = { keys: [key] };
      if (this.dno?.value) body.dno = this.dno.value;

      const fin = await this.jsonPOST(`${this.api}/import/${bare}`, body);

      if (fin.auto_normalized) {
        Toast?.show?.('✅ Auto-normalized Trimble CSV before import.', 'info');
      }

      // 4) Poll until complete
      await this.poll(jobId);

      // 5) Update result card as fallback
      if (this.out) {
        this.out.style.display = '';
        this.out.classList.remove('d-none');
      }
      if (this.jobSpan) this.jobSpan.textContent = jobId;
      if (this.mapBtn) this.mapBtn.href = `/map/view/${jobId}`;
      if (this.pdfBtn) this.pdfBtn.href = `/pdf/qa/${jobId}`;

      Toast?.show?.(`Import complete for ${jobId}`, 'success');

      // 6) Redirect to the map view and keep upload page in browser history
      setTimeout(() => {
        window.location.assign(`/map/view/${jobId}`);
      }, 700);

    } catch (e) {
      console.error(e);
      Toast?.show?.(`Upload failed: ${e.message || e}`, 'error');
    }
  }

  async poll(jobId) {
    let tries = 0;

    while (tries < this.pollMax) {
      const r = await fetch(`${this.api}/jobs/${jobId}/status`, { cache: 'no-store' });

      if (r.ok) {
        const js = await r.json();

        if (js.status === 'complete') return js;
        if (js.status === 'error' || js.status === 'failed') {
          throw new Error(js.error || 'processing error');
        }
      }

      await new Promise(res => setTimeout(res, this.pollInterval));
      tries++;
    }

    throw new Error('timeout');
  }

  async jsonPOST(url, data) {
    const r = await fetch(url, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data)
    });

    if (!r.ok) throw new Error(`${url} ${r.status}`);
    return r.json();
  }

  async put(url, blob, headers) {
    const r = await fetch(url, {
      method: 'PUT',
      headers: headers || {},
      body: blob
    });

    if (!r.ok) throw new Error(`PUT ${r.status}`);
  }
}

document.addEventListener('DOMContentLoaded', () => {
  window.uploadManager = new UploadManager();
});