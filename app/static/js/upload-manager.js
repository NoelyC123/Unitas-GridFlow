class UploadManager {
  constructor() {
    this.api = document.querySelector('meta[name="api-base-url"]')?.content || '/api';
    this.pollInterval = parseInt(document.querySelector('meta[name="poll-interval"]')?.content || '2000', 10);
    this.pollMax = parseInt(document.querySelector('meta[name="poll-max-attempts"]')?.content || '60', 10);
    this.projectsEnabled = document.querySelector('meta[name="projects-enabled"]')?.content === 'true';

    this.file = document.getElementById('file');
    this.dno = document.getElementById('dno');
    this.projectNameInput = document.getElementById('project-name');
    this.projectIdInput = document.getElementById('project-id');
    this.projectDescInput = document.getElementById('project-description');
    this.surveyDayInput = document.getElementById('survey-day-label');
    this.uploadedByInput = document.getElementById('uploaded-by');
    this.surveyorNoteInput = document.getElementById('surveyor-note');
    this.btn = document.getElementById('btn-upload');
    this.out = document.getElementById('result');
    this.jobSpan = document.getElementById('res-job');
    this.mapBtn = document.getElementById('btn-map');
    this.pdfBtn = document.getElementById('btn-pdf');

    // Auto-suggest project name when a file is chosen
    this.file?.addEventListener('change', () => this._suggestProjectName());

    // Pre-fill project_id from URL query param (e.g. when adding to existing project)
    const urlParams = new URLSearchParams(window.location.search);
    const urlProjectId = urlParams.get('project_id');
    if (urlProjectId && this.projectIdInput) {
      this.projectIdInput.value = urlProjectId;
      // When adding to an existing project, hide the project name field
      const group = document.getElementById('project-name-group');
      if (group) {
        group.style.display = 'none';
      }
      const heading = document.getElementById('upload-heading');
      if (heading) {
        heading.textContent = 'Add Survey Day / File';
      }
    }

    this.btn?.addEventListener('click', () => this.start());
  }

  _suggestProjectName() {
    if (!this.projectNameInput || this.projectIdInput?.value) return;
    const f = this.file?.files?.[0];
    if (!f) return;
    // Only suggest if field is currently empty
    if (this.projectNameInput.value.trim()) return;
    const stem = f.name.replace(/\.[^.]+$/, '');
    const suggested = stem.replace(/[_-]+/g, ' ').replace(/\s+/g, ' ').trim();
    this.projectNameInput.value = suggested;
  }

  async start() {
    try {
      if (!this.file?.files?.length) {
        Toast?.show?.('Choose a CSV file', 'warn');
        return;
      }

      const f = this.file.files[0];

      if (this.projectsEnabled) {
        await this._startProjectUpload(f);
      } else {
        await this._startLegacyUpload(f);
      }

    } catch (e) {
      console.error(e);
      Toast?.show?.(`Upload failed: ${e.message || e}`, 'error');
    }
  }

  async _startProjectUpload(f) {
    const projectId = this.projectIdInput?.value?.trim() || '';
    const projectName = this.projectNameInput?.value?.trim() || f.name.replace(/\.[^.]+$/, '');
    const description = this.projectDescInput?.value?.trim() || '';
    const dno = this.dno?.value || '';
    const surveyDayLabel = this.surveyDayInput?.value?.trim() || '';
    const uploadedBy = this.uploadedByInput?.value?.trim() || '';
    const surveyorNote = this.surveyorNoteInput?.value?.trim() || '';

    // 1) Project presign — creates or extends project, assigns file slot
    const presignBody = {
      filename: f.name,
      survey_day_label: surveyDayLabel,
      uploaded_by: uploadedBy,
      surveyor_note: surveyorNote
    };
    if (projectId) {
      presignBody.project_id = projectId;
    } else {
      presignBody.project_name = projectName;
      if (description) presignBody.description = description;
    }

    const ps = await this.jsonPOST(`${this.api}/project/presign`, presignBody);
    if (!ps.ok) throw new Error(ps.error || 'Presign failed');

    const { project_id, file_id, url, finalize_url, status_url, project_url } = ps;

    // 2) Upload file
    await this.put(url, f, { 'Content-Type': 'text/csv' });

    // 3) Finalize import
    const finBody = {};
    if (dno) finBody.dno = dno;
    const fin = await this.jsonPOST(finalize_url, finBody);

    if (fin.auto_normalized) {
      Toast?.show?.('Auto-normalized Trimble CSV before import.', 'info');
    }

    // 4) Poll until complete
    await this.pollProject(status_url);

    Toast?.show?.(`Import complete — project ${project_id} / file ${file_id}`, 'success');

    // 5) Redirect to project page
    setTimeout(() => {
      window.location.assign(project_url || `/project/${project_id}`);
    }, 700);
  }

  async _startLegacyUpload(f) {
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
      Toast?.show?.('Auto-normalized Trimble CSV before import.', 'info');
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

    // 6) Redirect to map view
    setTimeout(() => {
      window.location.assign(`/map/view/${jobId}`);
    }, 700);
  }

  async pollProject(statusUrl) {
    let tries = 0;
    while (tries < this.pollMax) {
      const r = await fetch(statusUrl, { cache: 'no-store' });
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
