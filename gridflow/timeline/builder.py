"""Build a conservative evidence timeline for one pole."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


@dataclass
class TimelineEvent:
    date: str
    date_display: str
    source: str
    event_type: str
    title: str
    description: str
    confidence: str
    evidence_ref: str | None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class Timeline:
    pole_id: str
    events: list[TimelineEvent]

    def to_dict(self) -> dict[str, Any]:
        return {
            "pole_id": self.pole_id,
            "events": [event.to_dict() for event in self.events],
        }


class EvidenceTimelineBuilder:
    """Build read-only evidence timelines from combined evidence records."""

    def build(self, pole_id: str, combined_evidence: dict[str, Any]) -> Timeline:
        events: list[TimelineEvent] = []
        record = dict(combined_evidence or {})

        contributing = record.get("contributing_files", {}) or {}
        support_no = record.get("support_no")
        pole_folder = contributing.get("pole_folder")
        notes_path = (
            Path(contributing.get("pole_notes", "")) if contributing.get("pole_notes") else None
        )
        photos_dir = (
            Path(contributing.get("field_photos", "")) if contributing.get("field_photos") else None
        )

        survey_event_dt = self._mtime(notes_path)
        if survey_event_dt is None and pole_folder:
            survey_event_dt = self._mtime(Path(pole_folder))
        events.append(
            self._event(
                date=self._iso_or_unknown(survey_event_dt),
                source="field_survey",
                event_type="survey_captured",
                title="Field survey recorded",
                description="Pole surveyed and field notes captured.",
                confidence="HIGH",
                evidence_ref=pole_folder or pole_id,
            )
        )

        linking = _as_dict(record.get("linking"))
        link_method = str(linking.get("linking_method") or "").strip()
        link_confidence = str(linking.get("confidence") or "UNKNOWN").upper()
        pole_fid = record.get("pole_fid")
        if pole_fid or support_no or record.get("spn"):
            enwl_confidence = "HIGH" if link_method == "fid_polestructure" else "MEDIUM"
            description = "ENWL asset record identified in network trace."
            if link_method == "fid_polestructure":
                description = "ENWL asset record identified in network trace via fid_polestructure."
            elif support_no:
                description = (
                    "ENWL asset record identified in network trace via support number context."
                )
            events.append(
                self._event(
                    date="unknown",
                    source="enwl_baseline",
                    event_type="enwl_record_found",
                    title="ENWL network record found",
                    description=description,
                    confidence=enwl_confidence,
                    evidence_ref=pole_fid or support_no or pole_id,
                )
            )

        for equipment in record.get("direct_equipment_records", []) or []:
            equipment = _as_dict(equipment)
            equipment_fid = equipment.get("fid")
            equipment_type = equipment.get("feature_type") or "ENWL equipment"
            link_basis = str(equipment.get("link_basis") or "")
            confidence = "HIGH" if equipment.get("fid_polestructure") else "MEDIUM"
            if "fid_polestructure" in link_basis:
                confidence = "HIGH"
            events.append(
                self._event(
                    date="unknown",
                    source="enwl_equipment",
                    event_type="equipment_linked",
                    title="ENWL equipment linked",
                    description=f"{equipment_type} linked to this pole in ENWL evidence."
                    + (f" Asset FID {equipment_fid}." if equipment_fid else ""),
                    confidence=confidence,
                    evidence_ref=equipment_fid or support_no or pole_id,
                )
            )

        if linking:
            method_label = link_method or "manual"
            warnings = (
                "manual review required"
                if linking.get("manual_confirmation_required")
                else "confirmed"
            )
            events.append(
                self._event(
                    date="unknown",
                    source="linking",
                    event_type="link_confirmed",
                    title="Survey linked to ENWL record",
                    description=(
                        f"Linking confidence: {link_confidence or 'UNKNOWN'} via {method_label}. "
                        f"Status: {warnings}."
                    ),
                    confidence=link_confidence or "UNKNOWN",
                    evidence_ref=support_no or pole_id,
                )
            )

        photo_count = int(record.get("photo_count") or 0)
        photo_dt = self._latest_photo_mtime(photos_dir)
        photo_confidence = "HIGH" if photo_count > 0 else "LOW"
        photo_description = (
            f"{photo_count} field photos captured."
            if photo_count > 0
            else "No field photos detected for this pole."
        )
        events.append(
            self._event(
                date=self._iso_or_unknown(photo_dt),
                source="field_survey",
                event_type="photo_captured",
                title="Field photos detected",
                description=photo_description,
                confidence=photo_confidence,
                evidence_ref=pole_folder or pole_id,
            )
        )

        conflicts = [_as_dict(conflict) for conflict in (record.get("conflicts") or [])]
        for conflict in conflicts:
            events.append(
                self._event(
                    date="unknown",
                    source="assessment",
                    event_type="conflict_detected",
                    title="Evidence conflict detected",
                    description=str(
                        conflict.get("description") or "Conflict detected in evidence review."
                    ),
                    confidence="LOW",
                    evidence_ref=support_no or pole_id,
                )
            )

        readiness = _as_dict(record.get("readiness"))
        if readiness:
            assessed_at = readiness.get("assessment_timestamp") or record.get(
                "assessment_timestamp"
            )
            readiness_dt = _parse_datetime(assessed_at) or datetime.now(UTC)
            blockers = len(readiness.get("readiness_blockers") or [])
            warnings = len(readiness.get("readiness_warnings") or [])
            status = readiness.get("readiness_status") or "unknown"
            confidence = str(readiness.get("readiness_confidence") or "UNKNOWN").upper()
            events.append(
                self._event(
                    date=self._iso_or_unknown(readiness_dt),
                    source="assessment",
                    event_type="readiness_assessed",
                    title="Design readiness assessed",
                    description=(
                        f"Status: {status}. {blockers} blocker{'s' if blockers != 1 else ''}. "
                        f"{warnings} warning{'s' if warnings != 1 else ''}."
                    ),
                    confidence=confidence,
                    evidence_ref=support_no or pole_id,
                )
            )

        return Timeline(pole_id=pole_id, events=self._sort_events(events))

    def _event(
        self,
        *,
        date: str,
        source: str,
        event_type: str,
        title: str,
        description: str,
        confidence: str,
        evidence_ref: str | None,
    ) -> TimelineEvent:
        return TimelineEvent(
            date=date,
            date_display=self._date_display(date),
            source=source,
            event_type=event_type,
            title=title,
            description=description,
            confidence=(confidence or "UNKNOWN").upper(),
            evidence_ref=evidence_ref,
        )

    def _sort_events(self, events: list[TimelineEvent]) -> list[TimelineEvent]:
        def sort_key(event: TimelineEvent) -> tuple[int, datetime, str, str]:
            parsed = _parse_datetime(event.date)
            if parsed is None:
                return (1, datetime.max.replace(tzinfo=UTC), event.source, event.title)
            return (0, parsed, event.source, event.title)

        return sorted(events, key=sort_key)

    def _date_display(self, value: str) -> str:
        parsed = _parse_datetime(value)
        if parsed is None:
            return "Date unknown"
        today = datetime.now(UTC).date()
        if parsed.date() == today:
            return "Today"
        return parsed.strftime("%d %B %Y")

    def _iso_or_unknown(self, value: datetime | None) -> str:
        return value.astimezone(UTC).isoformat() if value else "unknown"

    def _mtime(self, path: Path | None) -> datetime | None:
        if not path or not path.exists():
            return None
        return datetime.fromtimestamp(path.stat().st_mtime, tz=UTC)

    def _latest_photo_mtime(self, photos_dir: Path | None) -> datetime | None:
        if not photos_dir or not photos_dir.exists():
            return None
        latest = None
        for path in photos_dir.iterdir():
            if not path.is_file():
                continue
            candidate = datetime.fromtimestamp(path.stat().st_mtime, tz=UTC)
            if latest is None or candidate > latest:
                latest = candidate
        return latest


def _parse_datetime(value: Any) -> datetime | None:
    if value is None:
        return None
    text = str(value).strip()
    if not text or text.lower() == "unknown":
        return None
    if text.endswith("Z"):
        text = text[:-1] + "+00:00"
    try:
        parsed = datetime.fromisoformat(text)
    except ValueError:
        return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=UTC)
    return parsed.astimezone(UTC)


def _as_dict(value: Any) -> dict[str, Any]:
    if value is None:
        return {}
    if isinstance(value, dict):
        return dict(value)
    if hasattr(value, "to_dict") and callable(value.to_dict):
        return dict(value.to_dict())
    if hasattr(value, "__dict__"):
        return dict(vars(value))
    return {}
