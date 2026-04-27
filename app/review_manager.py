from __future__ import annotations

import copy
import json
import math
from datetime import datetime, timezone
from pathlib import Path


def _now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def load_review(file_dir: Path) -> dict | None:
    path = file_dir / "review.json"
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None


def save_review(file_dir: Path, review: dict) -> None:
    path = file_dir / "review.json"
    path.write_text(json.dumps(review, indent=2, ensure_ascii=False), encoding="utf-8")


def delete_review(file_dir: Path) -> bool:
    """Remove review.json if it exists. Returns True if deleted."""
    path = file_dir / "review.json"
    if path.exists():
        path.unlink()
        return True
    return False


def build_review(
    file_id: str,
    review_status: str,
    review_notes: str,
    pairing_overrides: list[dict],
    existing_review: dict | None = None,
) -> dict:
    version = 1 if existing_review is None else existing_review.get("version", 1) + 1
    reviewed_at = _now_iso() if review_status == "reviewed" else None
    return {
        "file_id": file_id,
        "review_status": review_status,
        "reviewed_by": "Designer",
        "reviewed_at": reviewed_at,
        "review_notes": review_notes.strip() if review_notes else "",
        "pairing_overrides": pairing_overrides,
        "version": version,
    }


def calc_distance(
    e1: float | None, n1: float | None, e2: float | None, n2: float | None
) -> float | None:
    if None in (e1, n1, e2, n2):
        return None
    try:
        return round(
            math.sqrt((float(e1) - float(e2)) ** 2 + (float(n1) - float(n2)) ** 2),
            1,
        )
    except Exception:
        return None


def enrich_overrides_with_distances(
    pairing_overrides: list[dict],
    seq: dict,
) -> list[dict]:
    """Fill in reviewed_distance_m and original_distance_m by looking up
    coordinates from seq.  Works in-place on a copy."""
    # Build coordinate lookup for all points in chain + matched/unmatched EXpoles
    coords: dict[str, tuple[float | None, float | None]] = {}
    for r in seq.get("chain", []):
        coords[str(r["point_id"])] = (r.get("easting"), r.get("northing"))
    for r in seq.get("matched_expoles", []) + seq.get("unmatched_expoles", []):
        coords[str(r["point_id"])] = (r.get("easting"), r.get("northing"))

    result = []
    for ov in pairing_overrides:
        ov = dict(ov)
        expole_id = str(ov.get("expole_point_id", ""))
        ex_e, ex_n = coords.get(expole_id, (None, None))

        orig_id = ov.get("original_matched_to")
        if orig_id is not None:
            orig_id = str(orig_id)
            orig_e, orig_n = coords.get(orig_id, (None, None))
            ov["original_distance_m"] = calc_distance(ex_e, ex_n, orig_e, orig_n)

        rev_id = ov.get("reviewed_matched_to")
        if rev_id is not None:
            rev_id = str(rev_id)
            rev_e, rev_n = coords.get(rev_id, (None, None))
            ov["reviewed_distance_m"] = calc_distance(ex_e, ex_n, rev_e, rev_n)
        else:
            ov["reviewed_distance_m"] = None

        result.append(ov)
    return result


def apply_pairing_overrides(seq: dict, review: dict | None) -> dict:
    """Return a deep-copied seq with pairing overrides from review applied.

    Never mutates seq.  If review is None or has no overrides, returns the
    original seq object unchanged.
    """
    if not review or not review.get("pairing_overrides"):
        return seq

    seq = copy.deepcopy(seq)
    chain_by_id: dict[str, dict] = {str(r["point_id"]): r for r in seq.get("chain", [])}

    for override in review["pairing_overrides"]:
        expole_id = str(override["expole_point_id"])
        original_proposed_id = override.get("original_matched_to")
        if original_proposed_id is not None:
            original_proposed_id = str(original_proposed_id)
        reviewed_proposed_id = override.get("reviewed_matched_to")
        if reviewed_proposed_id is not None:
            reviewed_proposed_id = str(reviewed_proposed_id)
        reviewed_distance = override.get("reviewed_distance_m")

        # Find EXpole entry in matched_expoles (may also be in unmatched if
        # a prior pass already moved it — but we always start from the
        # deep-copied original so this case only arises with multiple overrides
        # for the same EXpole, which is an authoring error; last one wins).
        matched = seq.get("matched_expoles") or []
        unmatched = seq.get("unmatched_expoles") or []
        expole_entry = next((e for e in matched if str(e["point_id"]) == expole_id), None)
        was_matched = expole_entry is not None
        if expole_entry is None:
            expole_entry = next((e for e in unmatched if str(e["point_id"]) == expole_id), None)

        if reviewed_proposed_id is None:
            # Mark as unmatched
            if was_matched and expole_entry:
                seq["matched_expoles"] = [e for e in matched if str(e["point_id"]) != expole_id]
                expole_entry["matched_to_proposed_id"] = None
                expole_entry["matched_design_pole_number"] = None
                expole_entry["distance_m"] = None
                seq.setdefault("unmatched_expoles", []).append(expole_entry)
        else:
            # Reassign to new proposed pole (or promote from unmatched)
            if expole_entry:
                if not was_matched:
                    # Move from unmatched to matched
                    seq["unmatched_expoles"] = [
                        e for e in unmatched if str(e["point_id"]) != expole_id
                    ]
                    seq.setdefault("matched_expoles", []).append(expole_entry)
                expole_entry["matched_to_proposed_id"] = reviewed_proposed_id
                expole_entry["distance_m"] = reviewed_distance
                new_chain_item = chain_by_id.get(reviewed_proposed_id, {})
                expole_entry["matched_design_pole_number"] = new_chain_item.get(
                    "design_pole_number"
                )

        # Clear old chain replacement reference
        if original_proposed_id and original_proposed_id in chain_by_id:
            old_item = chain_by_id[original_proposed_id]
            if str(old_item.get("replaces_point_id") or "") == expole_id:
                old_item["replaces_point_id"] = None
                old_item["replaces_distance_m"] = None

        # Set new chain replacement reference
        if reviewed_proposed_id and reviewed_proposed_id in chain_by_id:
            new_item = chain_by_id[reviewed_proposed_id]
            new_item["replaces_point_id"] = expole_id
            new_item["replaces_distance_m"] = reviewed_distance

        # Update interleaved_view EXpole row
        for r in seq.get("interleaved_view") or []:
            if str(r.get("point_id", "")) == expole_id:
                r["matched_proposed_id"] = reviewed_proposed_id
                if reviewed_proposed_id:
                    new_chain_item = chain_by_id.get(reviewed_proposed_id, {})
                    r["matched_design_pole_number"] = new_chain_item.get("design_pole_number")
                else:
                    r["matched_design_pole_number"] = None
                break

    return seq
