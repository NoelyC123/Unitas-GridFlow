"""Stage 7E search and filter engine for the review workspace.

Filters and sorts a list of MergedPole records. All parameters are optional;
no active filter returns the list unchanged. Multiple active filters combine
with AND logic in a single pass.
"""

from __future__ import annotations

from gridflow.merge.models import MergedPole

_STATUS_RANK = {
    "ready": 0,
    "review_required": 1,
    "not_ready": 2,
    "insufficient_evidence": 3,
}

_CONFIDENCE_RANK = {
    "HIGH": 0,
    "MEDIUM": 1,
    "LOW": 2,
    "UNMATCHED": 3,
}


def _pole_status(pole: MergedPole) -> str:
    """Derive a four-level readiness status from MergedPole fields."""
    if pole.design_ready:
        return "ready"
    if pole.review_required:
        return "review_required"
    if (
        pole.design_blocked
        or pole.voltage_verification_required
        or pole.conductor_verification_required
        or pole.pole_class_verification_required
        or pole.condition_verification_required
        or pole.identity_verification_required
        or pole.equipment_conflict_flag
        or pole.designer_actions
    ):
        return "not_ready"
    return "insufficient_evidence"


class PoleFilterEngine:
    """Filter and sort a list of MergedPole records for the review workspace."""

    def filter(
        self,
        poles: list[MergedPole],
        query: str | None = None,
        status: str | None = None,
        confidence: str | None = None,
        has_photos: bool | None = None,
        has_conflicts: bool | None = None,
        sort_by: str | None = None,
    ) -> list[MergedPole]:
        """Apply all active filters in a single pass, then sort.

        Args:
            poles: input list of MergedPole records
            query: case-insensitive text search across support_no, folder_name, notes_content
            status: readiness level — ready/review_required/not_ready/insufficient_evidence
            confidence: match_confidence level — HIGH/MEDIUM/LOW/UNMATCHED
            has_photos: True = only poles with photos; False = only poles without
            has_conflicts: True = only poles with conflict_flags; False = only without
            sort_by: pole_number/readiness_status/linking_confidence/photo_count/conflict_count
        """
        result = [
            p
            for p in poles
            if self._matches(p, query, status, confidence, has_photos, has_conflicts)
        ]
        return self._sort(result, sort_by)

    def _matches(
        self,
        pole: MergedPole,
        query: str | None,
        status: str | None,
        confidence: str | None,
        has_photos: bool | None,
        has_conflicts: bool | None,
    ) -> bool:
        if query:
            q = query.lower()
            searchable = " ".join(
                filter(
                    None,
                    [pole.support_no, pole.folder_name, pole.notes_content or ""],
                )
            ).lower()
            if q not in searchable:
                return False

        if status and _pole_status(pole) != status:
            return False

        if confidence and pole.match_confidence != confidence:
            return False

        if has_photos is not None:
            pole_has_photos = pole.field_photo_count > 0
            if has_photos != pole_has_photos:
                return False

        if has_conflicts is not None:
            pole_has_conflicts = bool(pole.conflict_flags)
            if has_conflicts != pole_has_conflicts:
                return False

        return True

    def _sort(self, poles: list[MergedPole], sort_by: str | None) -> list[MergedPole]:
        if not sort_by or sort_by == "pole_number":
            return sorted(poles, key=lambda p: p.folder_name or p.support_no or "")

        if sort_by == "readiness_status":
            return sorted(poles, key=lambda p: _STATUS_RANK.get(_pole_status(p), 99))

        if sort_by == "linking_confidence":
            return sorted(
                poles,
                key=lambda p: _CONFIDENCE_RANK.get(p.match_confidence, 99),
            )

        if sort_by == "photo_count":
            return sorted(poles, key=lambda p: p.field_photo_count, reverse=True)

        if sort_by == "conflict_count":
            return sorted(poles, key=lambda p: len(p.conflict_flags), reverse=True)

        return sorted(poles, key=lambda p: p.folder_name or p.support_no or "")
