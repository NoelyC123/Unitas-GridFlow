"""Stage 4 proof-of-concept: structured field capture storage and CSV export for Stage 1 intake.

SQLite lives under each project folder: ``uploads/projects/<job_id>/field_capture.db``.
Photos live under ``uploads/projects/<job_id>/field_capture/<session_id>/photos/``.
"""

from __future__ import annotations

import csv
import io
import json
import sqlite3
import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from werkzeug.utils import secure_filename

_PROJECT_ROOT = Path(__file__).resolve().parents[1]
PROJECTS_ROOT = _PROJECT_ROOT / "uploads" / "projects"


def _now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def project_dir(job_id: str) -> Path:
    return PROJECTS_ROOT / job_id


def database_path(job_id: str) -> Path:
    return project_dir(job_id) / "field_capture.db"


def capture_root(job_id: str, session_id: str) -> Path:
    return project_dir(job_id) / "field_capture" / session_id


def photos_dir(job_id: str, session_id: str) -> Path:
    return capture_root(job_id, session_id) / "photos"


@dataclass
class FieldCaptureSession:
    id: str
    job_id: str
    surveyor: str
    start_time: str
    end_time: str | None
    record_count: int
    status: str
    imported_file_id: str | None = None


@dataclass
class CaptureRecord:
    id: str
    session_id: str
    record_type: str
    fields: dict[str, Any]
    photos: list[str]
    gnss_data: dict[str, Any]
    timestamp: str


def _connect(job_id: str) -> sqlite3.Connection:
    project_dir(job_id).mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(database_path(job_id))
    conn.row_factory = sqlite3.Row
    return conn


def init_schema(conn: sqlite3.Connection) -> None:
    conn.executescript(
        """
        CREATE TABLE IF NOT EXISTS sessions (
            id TEXT PRIMARY KEY,
            job_id TEXT NOT NULL,
            surveyor TEXT NOT NULL DEFAULT '',
            start_time TEXT NOT NULL,
            end_time TEXT,
            record_count INTEGER NOT NULL DEFAULT 0,
            status TEXT NOT NULL DEFAULT 'open',
            imported_file_id TEXT
        );
        CREATE TABLE IF NOT EXISTS records (
            id TEXT PRIMARY KEY,
            session_id TEXT NOT NULL,
            record_type TEXT NOT NULL,
            fields_json TEXT NOT NULL,
            photos_json TEXT NOT NULL DEFAULT '[]',
            gnss_json TEXT NOT NULL DEFAULT '{}',
            created_at TEXT NOT NULL,
            FOREIGN KEY (session_id) REFERENCES sessions(id)
        );
        CREATE INDEX IF NOT EXISTS idx_records_session ON records(session_id);
        """
    )
    conn.commit()


def create_session(job_id: str, surveyor: str = "") -> FieldCaptureSession:
    sid = str(uuid.uuid4())
    surveyor_clean = str(surveyor or "").strip()
    session = FieldCaptureSession(
        id=sid,
        job_id=job_id,
        surveyor=surveyor_clean,
        start_time=_now_iso(),
        end_time=None,
        record_count=0,
        status="open",
        imported_file_id=None,
    )
    conn = _connect(job_id)
    try:
        init_schema(conn)
        conn.execute(
            """
            INSERT INTO sessions (id, job_id, surveyor, start_time, end_time, record_count, status)
            VALUES (?, ?, ?, ?, NULL, 0, 'open')
            """,
            (session.id, session.job_id, session.surveyor, session.start_time),
        )
        conn.commit()
    finally:
        conn.close()
    return session


def _row_to_session(row: sqlite3.Row) -> FieldCaptureSession:
    return FieldCaptureSession(
        id=row["id"],
        job_id=row["job_id"],
        surveyor=row["surveyor"] or "",
        start_time=row["start_time"],
        end_time=row["end_time"],
        record_count=int(row["record_count"] or 0),
        status=row["status"] or "open",
        imported_file_id=row["imported_file_id"],
    )


def get_session(job_id: str, session_id: str) -> FieldCaptureSession | None:
    conn = _connect(job_id)
    try:
        init_schema(conn)
        cur = conn.execute("SELECT * FROM sessions WHERE id = ?", (session_id,))
        row = cur.fetchone()
        return _row_to_session(row) if row else None
    finally:
        conn.close()


def list_sessions(job_id: str) -> list[FieldCaptureSession]:
    conn = _connect(job_id)
    try:
        init_schema(conn)
        cur = conn.execute("SELECT * FROM sessions ORDER BY start_time DESC")
        return [_row_to_session(r) for r in cur.fetchall()]
    finally:
        conn.close()


def list_records(job_id: str, session_id: str) -> list[CaptureRecord]:
    conn = _connect(job_id)
    try:
        init_schema(conn)
        cur = conn.execute(
            "SELECT * FROM records WHERE session_id = ? ORDER BY created_at ASC",
            (session_id,),
        )
        out: list[CaptureRecord] = []
        for row in cur.fetchall():
            out.append(
                CaptureRecord(
                    id=row["id"],
                    session_id=row["session_id"],
                    record_type=row["record_type"],
                    fields=json.loads(row["fields_json"] or "{}"),
                    photos=json.loads(row["photos_json"] or "[]"),
                    gnss_data=json.loads(row["gnss_json"] or "{}"),
                    timestamp=row["created_at"],
                )
            )
        return out
    finally:
        conn.close()


def _increment_session_count(conn: sqlite3.Connection, session_id: str) -> None:
    conn.execute(
        "UPDATE sessions SET record_count = record_count + 1 WHERE id = ?",
        (session_id,),
    )


def add_record(
    job_id: str,
    session_id: str,
    record_type: str,
    fields: dict[str, Any],
    gnss_data: dict[str, Any],
    photo_storage: list[tuple[str, bytes]],
) -> CaptureRecord:
    """Persist a capture record and optional photo bytes."""
    rid = str(uuid.uuid4())
    session = get_session(job_id, session_id)
    if session is None:
        raise ValueError("session_not_found")
    if session.status != "open":
        raise ValueError("session_closed")

    pdir = photos_dir(job_id, session_id)
    pdir.mkdir(parents=True, exist_ok=True)
    stored_paths: list[str] = []
    for idx, (orig_name, raw) in enumerate(photo_storage):
        base = secure_filename(orig_name) or f"photo_{idx}.bin"
        root, ext = Path(base).stem, Path(base).suffix
        fname = f"{rid}_{idx}_{root}{ext or '.bin'}"
        path = pdir / fname
        path.write_bytes(raw)
        rel = str(path.relative_to(project_dir(job_id)))
        stored_paths.append(rel)

    rec = CaptureRecord(
        id=rid,
        session_id=session_id,
        record_type=record_type,
        fields=fields,
        photos=stored_paths,
        gnss_data=gnss_data,
        timestamp=_now_iso(),
    )
    conn = _connect(job_id)
    try:
        init_schema(conn)
        conn.execute(
            """
            INSERT INTO records (
              id, session_id, record_type, fields_json, photos_json, gnss_json, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                rec.id,
                rec.session_id,
                rec.record_type,
                json.dumps(rec.fields, allow_nan=False),
                json.dumps(rec.photos, allow_nan=False),
                json.dumps(rec.gnss_data, allow_nan=False),
                rec.timestamp,
            ),
        )
        _increment_session_count(conn, session_id)
        conn.commit()
    finally:
        conn.close()
    return rec


def close_session(job_id: str, session_id: str) -> None:
    conn = _connect(job_id)
    try:
        init_schema(conn)
        conn.execute(
            "UPDATE sessions SET end_time = ? WHERE id = ?",
            (_now_iso(), session_id),
        )
        conn.commit()
    finally:
        conn.close()


def mark_session_imported(job_id: str, session_id: str, file_id: str) -> None:
    conn = _connect(job_id)
    try:
        init_schema(conn)
        conn.execute(
            """
            UPDATE sessions
            SET status = 'imported', imported_file_id = ?,
                end_time = COALESCE(end_time, ?)
            WHERE id = ?
            """,
            (file_id, _now_iso(), session_id),
        )
        conn.commit()
    finally:
        conn.close()


def _map_structure_type(record_type: str, fields: dict[str, Any]) -> str:
    st = str(fields.get("structure_type") or fields.get("record_type") or "").strip()
    if record_type == "pole":
        rt = fields.get("record_type") or st
        s = str(rt).strip().upper()
        if s == "PR":
            return "PRpole"
        if s == "EXPOLE" or s == "EX":
            return "EXpole"
        return str(rt).strip() or "Pole"
    if record_type == "context":
        key = st.lower()
        mapping = {
            "road": "Road",
            "fence": "Fence",
            "bt": "BT",
            "crossing": "11xing",
        }
        return mapping.get(key, st or "Road")
    return st or "unknown"


def record_to_intake_row(record: CaptureRecord) -> dict[str, Any]:
    """Flatten one capture record to CSV columns understood by Stage 1 normalization."""
    rt = record.record_type
    f = dict(record.fields)
    g = record.gnss_data or {}
    row: dict[str, Any] = {
        "_capture_record_type": rt,
        "_capture_record_id": record.id,
    }

    lat = g.get("latitude") or f.get("latitude") or f.get("lat")
    lon = g.get("longitude") or f.get("longitude") or f.get("lon")
    elev = g.get("elevation") or f.get("elevation")

    if rt == "pole":
        row["pole_id"] = f.get("point_id") or f.get("pole_id")
        row["structure_type"] = _map_structure_type("pole", f)
        row["height"] = f.get("height_m")
        row["material"] = f.get("material")
        row["condition"] = f.get("condition")
        if f.get("stay_required") is not None:
            row["stay_required"] = f.get("stay_required")
        loc_bits = [str(f.get("remarks") or "").strip()]
        if f.get("stay_required"):
            loc_bits.append("stay_required=yes")
        row["location"] = " | ".join([b for b in loc_bits if b]) or None
        row["photo_links"] = ";".join(record.photos) if record.photos else None
    elif rt == "span":
        row["pole_id"] = f"S-{f.get('from_pole_id')}-{f.get('to_pole_id')}"
        row["structure_type"] = "Cable span (field capture)"
        row["location"] = (
            f"from={f.get('from_pole_id')} to={f.get('to_pole_id')} | "
            f"conductor={f.get('conductor_type')} {f.get('conductor_size') or ''} | "
            f"phases={f.get('phases')}"
        ).strip()
        if f.get("remarks"):
            row["location"] = f"{row['location']} | {f['remarks']}"
        row["conductor_type"] = f.get("conductor_type")
        row["conductor_size"] = f.get("conductor_size")
        row["phase_count"] = f.get("phases")
        row["from_pole_id"] = f.get("from_pole_id")
        row["to_pole_id"] = f.get("to_pole_id")
    else:  # context
        row["pole_id"] = f"C-{f.get('structure_type', 'ctx')}-{record.id[:8]}"
        row["structure_type"] = _map_structure_type("context", f)
        row["distance_from_route_m"] = f.get("distance_m")
        row["location"] = (f.get("remarks") or "").strip() or None

    if lat is not None:
        row["latitude"] = lat
    if lon is not None:
        row["longitude"] = lon
    if elev is not None:
        row["elevation"] = elev

    return {k: v for k, v in row.items() if v is not None and v != ""}


def session_to_csv_text(job_id: str, session_id: str) -> str:
    records = list_records(job_id, session_id)
    if not records:
        return ""
    rows = [record_to_intake_row(r) for r in records]
    fieldnames: list[str] = sorted({key for row in rows for key in row})
    buf = io.StringIO()
    w = csv.DictWriter(buf, fieldnames=fieldnames, extrasaction="ignore")
    w.writeheader()
    for row in rows:
        w.writerow(row)
    return buf.getvalue()


def validate_pole_payload(fields: dict[str, Any], photo_count: int) -> list[str]:
    errors: list[str] = []
    pid = str(fields.get("point_id") or fields.get("pole_id") or "").strip()
    if not pid:
        errors.append("missing_point_id")
    rt = str(fields.get("record_type") or "").strip()
    if not rt:
        errors.append("missing_record_type")
    try:
        h = fields.get("height_m")
        if h is not None and h != "":
            float(h)
    except (TypeError, ValueError):
        errors.append("invalid_height_m")
    if photo_count < 1:
        errors.append("pole_requires_photo")
    return errors


def validate_span_payload(fields: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if not str(fields.get("from_pole_id") or "").strip():
        errors.append("missing_from_pole_id")
    if not str(fields.get("to_pole_id") or "").strip():
        errors.append("missing_to_pole_id")
    return errors


def validate_context_payload(fields: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if not str(fields.get("structure_type") or "").strip():
        errors.append("missing_structure_type")
    return errors
