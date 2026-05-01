/**
 * Stage 4 field capture — offline-first drafts, GNSS, multipart submit, sync queue replay.
 */
(function () {
  "use strict";

  const meta = document.querySelector('meta[name="fc-project-id"]');
  const INITIAL_PROJECT = (meta && meta.content) || "";

  function storageKey(suffix) {
    const job = document.getElementById("fc-job-id")?.value?.trim() || "_noid";
    return `gridflow_field_capture_${job}_${suffix}`;
  }

  function getSessionState() {
    try {
      const raw = localStorage.getItem(storageKey("session"));
      return raw ? JSON.parse(raw) : null;
    } catch {
      return null;
    }
  }

  function setSessionState(obj) {
    localStorage.setItem(storageKey("session"), JSON.stringify(obj));
  }

  function getQueue() {
    try {
      const raw = localStorage.getItem(storageKey("sync_queue"));
      return raw ? JSON.parse(raw) : [];
    } catch {
      return [];
    }
  }

  function setQueue(arr) {
    localStorage.setItem(storageKey("sync_queue"), JSON.stringify(arr));
  }

  function updateQueueLabel() {
    const el = document.getElementById("queue-label");
    if (el) el.textContent = `Sync queue: ${getQueue().length}`;
  }

  function updateImportButton() {
    const btn = document.getElementById("btn-import");
    const s = getSessionState();
    const can =
      navigator.onLine && s && s.job_id && (Boolean(s.session_id) || getQueue().length > 0);
    if (btn) btn.disabled = !can;
  }

  function logLine(text, kind) {
    const ul = document.getElementById("record-log");
    if (!ul) return;
    const li = document.createElement("li");
    li.className = "list-group-item small" + (kind ? ` list-group-item-${kind}` : "");
    const t = new Date().toLocaleTimeString();
    li.textContent = `[${t}] ${text}`;
    if (ul.firstChild && ul.firstChild.textContent.includes("No local events")) {
      ul.innerHTML = "";
    }
    ul.insertBefore(li, ul.firstChild);
  }

  function setOnlineUi(online) {
    const dot = document.getElementById("net-dot");
    const text = document.getElementById("net-text");
    if (dot) {
      dot.classList.toggle("status-online", online);
      dot.classList.toggle("status-offline", !online);
    }
    if (text) text.textContent = online ? "Online — sync enabled" : "Offline — drafts queued";
    updateImportButton();
  }

  function readGnssIntoForm(pos) {
    const lat = pos.coords.latitude;
    const lon = pos.coords.longitude;
    const el = pos.coords.altitude != null ? pos.coords.altitude : "";
    const acc = pos.coords.accuracy != null ? ` ±${Math.round(pos.coords.accuracy)}m` : "";
    const out = document.getElementById("gnss-readout");
    if (out) {
      out.textContent = `lat ${lat.toFixed(6)}, lon ${lon.toFixed(6)}${el !== "" ? `, elev ${Number(el).toFixed(2)}m` : ""}${acc}`;
    }
    const latEl = document.getElementById("fc-lat");
    const lonEl = document.getElementById("fc-lon");
    const elevEl = document.getElementById("fc-elev");
    if (latEl) latEl.value = String(lat);
    if (lonEl) lonEl.value = String(lon);
    if (elevEl) elevEl.value = el === "" ? "" : String(el);
  }

  function captureGeolocation() {
    const out = document.getElementById("gnss-readout");
    if (!navigator.geolocation) {
      if (out) out.textContent = "Geolocation not available — enter coords elsewhere if needed.";
      logLine("GNSS: not available", "warning");
      return;
    }
    if (out) out.textContent = "Locating…";
    navigator.geolocation.getCurrentPosition(
      (pos) => {
        readGnssIntoForm(pos);
        logLine("GNSS fix stored for next submit");
      },
      (err) => {
        if (out) out.textContent = `GNSS error: ${err.message || err.code}`;
        logLine(`GNSS failed: ${err.message || err.code}`, "warning");
      },
      { enableHighAccuracy: true, maximumAge: 30_000, timeout: 20_000 }
    );
  }

  function gnssPayload() {
    const lat = document.getElementById("fc-lat")?.value;
    const lon = document.getElementById("fc-lon")?.value;
    const elev = document.getElementById("fc-elev")?.value;
    const o = {};
    if (lat) o.latitude = Number(lat);
    if (lon) o.longitude = Number(lon);
    if (elev) o.elevation = Number(elev);
    o.captured_at = new Date().toISOString();
    return o;
  }

  function formDataFromForm(form, recordKind, sessionId) {
    const fd = new FormData();
    fd.append("session_id", sessionId);
    fd.append("record_kind", recordKind);
    const fields = {};
    const formData = new FormData(form);
    formData.forEach((v, k) => {
      if (k === "photos") return;
      if (k === "stay_required") {
        fields[k] = form.querySelector('[name="stay_required"]')?.checked === true;
        return;
      }
      fields[k] = v;
    });
    fd.append("fields", JSON.stringify(fields));
    fd.append("gnss", JSON.stringify(gnssPayload()));
    const fileInput = form.querySelector('input[type="file"][name="photos"]');
    if (fileInput && fileInput.files) {
      for (const f of fileInput.files) {
        fd.append("photos", f, f.name);
      }
    }
    return fd;
  }

  async function serializePoleForQueue(form) {
      const fields = {};
      const data = new FormData(form);
      data.forEach((v, k) => {
        if (k === "photos") return;
        if (k === "stay_required") {
          fields[k] = form.querySelector('[name="stay_required"]')?.checked === true;
          return;
        }
        fields[k] = v;
      });
      const fileInput = form.querySelector('input[type="file"][name="photos"]');
      const photos = [];
      if (fileInput && fileInput.files?.length) {
        for (const file of fileInput.files) {
          const buf = await file.arrayBuffer();
          let binary = "";
          const bytes = new Uint8Array(buf);
          const chunk = 0x8000;
          for (let i = 0; i < bytes.length; i += chunk) {
            binary += String.fromCharCode.apply(null, bytes.subarray(i, i + chunk));
          }
          photos.push({ name: file.name, data: btoa(binary) });
        }
      }
      return {
        record_kind: "pole",
        fields,
        gnss: gnssPayload(),
        photos,
      };
    }

  function rebuildPoleFormData(item, sessionId) {
    const fd = new FormData();
    fd.append("session_id", sessionId);
    fd.append("record_kind", "pole");
    fd.append("fields", JSON.stringify(item.fields));
    fd.append("gnss", JSON.stringify(item.gnss || {}));
    (item.photos || []).forEach((p) => {
      const bytes = Uint8Array.from(atob(p.data), (c) => c.charCodeAt(0));
      const blob = new Blob([bytes]);
      fd.append("photos", blob, p.name || "photo.jpg");
    });
    return fd;
  }

  async function postRecord(formData) {
    const res = await fetch("/api/field_capture/record", {
      method: "POST",
      body: formData,
    });
    const js = await res.json().catch(() => ({}));
    if (!res.ok || !js.ok) {
      throw new Error(js.error || js.details?.join?.(", ") || res.statusText || "save failed");
    }
    return js;
  }

  /** Ensure server-backed session id when online (creates session if missing). */
  async function ensureServerSession() {
    let s = getSessionState();
    if (!s || !s.job_id) throw new Error("Start session first (set job & surveyor)");
    if (s.session_id) return s.session_id;
    if (!navigator.onLine) throw new Error("offline");
    const res = await fetch("/api/field_capture/session", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ job_id: s.job_id, surveyor: s.surveyor || "" }),
    });
    const data = await res.json();
    if (!res.ok || !data.ok) {
      throw new Error(data.error || "session create failed");
    }
    s = {
      job_id: data.job_id,
      surveyor: data.surveyor,
      session_id: data.session_id,
    };
    setSessionState(s);
    const lbl = document.getElementById("session-label");
    if (lbl) lbl.textContent = `Session ${data.session_id.slice(0, 8)}…`;
    updateImportButton();
    logLine("Server session registered");
    return data.session_id;
  }

  async function flushQueue() {
    if (!navigator.onLine) return;
    let q = getQueue();
    if (!q.length) return;
    try {
      const sid = await ensureServerSession();
      const remain = [];
      for (const item of q) {
        try {
          let fd;
          if (item.record_kind === "pole") {
            fd = rebuildPoleFormData(item, sid);
          } else {
            fd = new FormData();
            fd.append("session_id", sid);
            fd.append("record_kind", item.record_kind);
            fd.append("fields", JSON.stringify(item.fields));
            fd.append("gnss", JSON.stringify(item.gnss || {}));
          }
          await postRecord(fd);
          logLine(`Synced queued ${item.record_kind} OK`);
        } catch {
          remain.push(item);
        }
      }
      setQueue(remain);
    } catch (e) {
      logLine(`Sync paused: ${e.message}`, "warning");
    }
    updateQueueLabel();
  }

  function saveDraft(formId, recordKind) {
    const form = document.getElementById(formId);
    if (!form) return;
    const fields = {};
    new FormData(form).forEach((v, k) => {
      if (k === "photos") return;
      if (k === "stay_required") {
        fields[k] = form.querySelector('[name="stay_required"]')?.checked === true;
        return;
      }
      fields[k] = v;
    });
    const draft = { recordKind, fields, savedAt: new Date().toISOString() };
    localStorage.setItem(storageKey(`draft_${recordKind}`), JSON.stringify(draft));
    logLine(`Draft saved (${recordKind})`);
  }

  function loadDraft(formId, recordKind) {
    try {
      const raw = localStorage.getItem(storageKey(`draft_${recordKind}`));
      if (!raw) return;
      const draft = JSON.parse(raw);
      const form = document.getElementById(formId);
      if (!form || !draft.fields) return;
      Object.entries(draft.fields).forEach(([k, v]) => {
        const el = form.elements[k];
        if (!el) return;
        if (el.type === "checkbox") el.checked = Boolean(v);
        else el.value = v;
      });
      logLine(`Draft restored (${recordKind})`);
    } catch {
      /* ignore */
    }
  }

  async function startSession() {
    const jobId = document.getElementById("fc-job-id")?.value?.trim();
    const surveyor = document.getElementById("fc-surveyor")?.value?.trim() || "";
    if (!jobId) {
      logLine("Enter project id first", "warning");
      return;
    }
    if (!navigator.onLine) {
      setSessionState({ job_id: jobId, surveyor, session_id: null });
      document.getElementById("session-label").textContent = "Offline session — records queue until online";
      logLine("Offline: queued captures will register a server session when you sync.");
      updateImportButton();
      return;
    }
    const res = await fetch("/api/field_capture/session", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ job_id: jobId, surveyor }),
    });
    const data = await res.json();
    if (!res.ok || !data.ok) {
      logLine(`Session failed: ${data.error || res.status}`, "warning");
      return;
    }
    setSessionState({
      session_id: data.session_id,
      job_id: data.job_id,
      surveyor: data.surveyor,
    });
    const lbl = document.getElementById("session-label");
    if (lbl) lbl.textContent = `Session ${data.session_id.slice(0, 8)}…`;
    logLine("Session registered on server");
    updateImportButton();
  }

  async function submitPole(ev) {
    ev.preventDefault();
    const form = document.getElementById("form-pole");
    const sess = getSessionState();
    if (!sess || !sess.job_id) {
      logLine("Start session first", "warning");
      return;
    }
    const files = form.querySelector('input[name="photos"]')?.files || [];
    if (!files.length) {
      logLine("Pole requires at least one photo", "warning");
      return;
    }
    try {
      if (!navigator.onLine) throw new Error("offline");
      const sid = await ensureServerSession();
      const fd = formDataFromForm(form, "pole", sid);
      await postRecord(fd);
      logLine("Pole record saved to server");
      form.reset();
    } catch (e) {
      if (String(e.message) !== "offline" && navigator.onLine) {
        logLine(`Save failed: ${e.message}`, "warning");
        return;
      }
      logLine("Queuing pole for offline / retry sync", "warning");
      const serialized = await serializePoleForQueue(form);
      const q = getQueue();
      q.push(serialized);
      setQueue(q);
      updateQueueLabel();
      form.reset();
    }
  }

  async function submitSpan(ev) {
    ev.preventDefault();
    const form = document.getElementById("form-span");
    const sess = getSessionState();
    if (!sess || !sess.job_id) {
      logLine("Start session first", "warning");
      return;
    }
    const fields = {};
    new FormData(form).forEach((v, k) => {
      fields[k] = v;
    });
    try {
      if (!navigator.onLine) throw new Error("offline");
      const sid = await ensureServerSession();
      const fd = formDataFromForm(form, "span", sid);
      await postRecord(fd);
      logLine("Span record saved");
      form.reset();
    } catch {
      getQueue().push({ record_kind: "span", fields, gnss: gnssPayload() });
      setQueue(getQueue());
      updateQueueLabel();
      logLine("Span queued for sync");
      form.reset();
    }
  }

  async function submitContext(ev) {
    ev.preventDefault();
    const form = document.getElementById("form-context");
    const sess = getSessionState();
    if (!sess || !sess.job_id) {
      logLine("Start session first", "warning");
      return;
    }
    const fields = {};
    new FormData(form).forEach((v, k) => {
      fields[k] = v;
    });
    try {
      if (!navigator.onLine) throw new Error("offline");
      const sid = await ensureServerSession();
      const fd = formDataFromForm(form, "context", sid);
      await postRecord(fd);
      logLine("Context record saved");
      form.reset();
    } catch {
      getQueue().push({ record_kind: "context", fields, gnss: gnssPayload() });
      setQueue(getQueue());
      updateQueueLabel();
      logLine("Context queued for sync");
      form.reset();
    }
  }

  async function importSession() {
    await flushQueue();
    try {
      await ensureServerSession();
    } catch (e) {
      logLine(`Cannot import: ${e.message}`, "warning");
      return;
    }
    const sess = getSessionState();
    if (!sess?.session_id) {
      logLine("No session — add records or start session online", "warning");
      return;
    }
    const jobId = document.getElementById("fc-job-id")?.value?.trim();
    const res = await fetch(
      `/api/field_capture/import/${sess.session_id}?job_id=${encodeURIComponent(jobId)}`,
      {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ dno: "SPEN_11kV", surveyor_note: "Stage 4 field capture import" }),
      }
    );
    const data = await res.json().catch(() => ({}));
    if (!res.ok || !data.ok) {
      logLine(`Import failed: ${data.error || res.status}`, "warning");
      return;
    }
    logLine(`Imported → file ${data.file_id} (issues ${data.issue_count ?? "?"})`);
    document.getElementById("import-hint").textContent =
      `Processed as ${data.file_id}. Open project to view map/PDF.`;
  }

  function bind() {
    document.getElementById("btn-start-session")?.addEventListener("click", () => {
      startSession().catch((e) => logLine(String(e), "warning"));
    });
    document.getElementById("btn-refresh-gnss")?.addEventListener("click", captureGeolocation);
    document.getElementById("form-pole")?.addEventListener("submit", (ev) => {
      submitPole(ev).catch((e) => logLine(String(e), "warning"));
    });
    document.getElementById("form-span")?.addEventListener("submit", (ev) => {
      submitSpan(ev).catch((e) => logLine(String(e), "warning"));
    });
    document.getElementById("form-context")?.addEventListener("submit", (ev) => {
      submitContext(ev).catch((e) => logLine(String(e), "warning"));
    });
    document.getElementById("btn-draft-pole")?.addEventListener("click", () => saveDraft("form-pole", "pole"));
    document.getElementById("btn-import")?.addEventListener("click", () => {
      importSession().catch((e) => logLine(String(e), "warning"));
    });
    document.getElementById("btn-refresh-log")?.addEventListener("click", () => logLine("—"));

    window.addEventListener("online", () => {
      setOnlineUi(true);
      flushQueue().catch(() => {});
    });
    window.addEventListener("offline", () => setOnlineUi(false));

    const jobInput = document.getElementById("fc-job-id");
    if (jobInput && INITIAL_PROJECT) jobInput.value = INITIAL_PROJECT;

    loadDraft("form-pole", "pole");
    loadDraft("form-span", "span");
    loadDraft("form-context", "context");

    const existing = getSessionState();
    if (existing && existing.job_id) {
      const lbl = document.getElementById("session-label");
      if (lbl && existing.session_id) {
        lbl.textContent = `Session ${existing.session_id.slice(0, 8)}…`;
      } else if (lbl) {
        lbl.textContent = "Offline / pending server session";
      }
    }
    updateQueueLabel();
    updateImportButton();
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", () => {
      setOnlineUi(navigator.onLine);
      bind();
      captureGeolocation();
    });
  } else {
    setOnlineUi(navigator.onLine);
    bind();
    captureGeolocation();
  }
})();
