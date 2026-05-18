# Stage 7E — Search and Filter Specification

**Date:** 2026-05-18
**Reference:** `AI_CONTROL/132_STAGE7_ROADMAP.md`

---

## Purpose

Allow designers to search and filter across all poles in a survey without manually clicking
through each one. Currently the workspace shows a list with basic filter buttons; there is
no text search and no compound filtering.

---

## Current State

The workspace job overview already has filter buttons for:
- All Poles / Design Ready / Design Blocked
- HIGH / MEDIUM / LOW match confidence
- Has Flags

These work via URL query parameters (`?design_ready=true`, `?match_confidence=HIGH`).
There is no text search, no status filter by readiness level, no photo filter, no conflict
filter, and no sort control.

---

## Stage 7E Scope

### Search

- Text search across `support_no`, `folder_name`, and excerpt of `notes_content`
- Case-insensitive substring match
- Submitted via form GET (consistent with existing filter approach)
- Clear button removes the `q` param

### Filters (combinable with AND logic)

| Filter | Parameter | Values |
|---|---|---|
| Readiness status | `status` | `ready` / `review_required` / `not_ready` / `insufficient_evidence` |
| Linking confidence | `confidence` | `HIGH` / `MEDIUM` / `LOW` / `UNMATCHED` |
| Photo presence | `photos` | `yes` / `no` |
| Conflict presence | `conflicts` | `yes` / `no` |

### Sort

| Option | Parameter value | Default |
|---|---|---|
| Pole number | `pole_number` | ✅ default |
| Readiness status | `readiness_status` | |
| Linking confidence | `linking_confidence` | |
| Photo count | `photo_count` | |
| Conflict count | `conflict_count` | |

### Results display

- Show filtered count vs total: "Showing 3 of 10 poles"
- Each result shows: pole ID, support no, readiness badge, photo count, conflict count
- Click result → pole detail page
- No active filters → show all poles (current behaviour preserved)

---

## Implementation Approach

### Option A — Server-side filtering (implemented)

Filter params are passed as URL query strings. Flask route handles filtering and page
reloads with filtered results. Consistent with existing Flask patterns in this codebase.

`GET /workspace/view/<job_id>?q=900344&status=not_ready&confidence=HIGH&photos=yes&sort=photo_count`

Advantages:
- Consistent with existing filter button pattern
- Works without JavaScript framework
- Bookmarkable / shareable filter URLs
- No additional frontend complexity

The existing `?design_ready=...`, `?evidence_quality=...`, `?match_confidence=...`,
`?has_flags=...` params continue to work alongside the new params.

### Option B — Client-side filtering (future enhancement)

All pole data embedded as JSON in the page; JavaScript handles filtering in real-time
without page reloads. Can be added as a progressive enhancement after Option A is proven.

---

## Backend: `gridflow/workspace/filter_engine.py`

### `PoleFilterEngine.filter()`

```python
def filter(
    self,
    poles: list[MergedPole],
    query: str | None = None,
    status: str | None = None,
    confidence: str | None = None,
    has_photos: bool | None = None,
    has_conflicts: bool | None = None,
    sort_by: str | None = None,
) -> list[MergedPole]
```

All parameters are optional. No active filters returns all poles unchanged. All active
filters are applied with AND logic in a single pass.

**Status mapping from `MergedPole` fields:**

| Status value | Condition |
|---|---|
| `ready` | `pole.design_ready == True` |
| `review_required` | `pole.review_required == True` |
| `not_ready` | `pole.design_blocked == True` and not ready and not review_required |
| `insufficient_evidence` | everything else |

**Sort order:**

| `sort_by` value | Sort key |
|---|---|
| `pole_number` | `folder_name` (or `support_no`) alphabetically |
| `readiness_status` | status rank: ready > review_required > not_ready > insufficient |
| `linking_confidence` | confidence rank: HIGH > MEDIUM > LOW > UNMATCHED |
| `photo_count` | `field_photo_count` descending |
| `conflict_count` | `len(conflict_flags)` descending |

---

## Frontend: `review_workspace.html` changes

Add above the existing filter buttons (not replacing them):

```
┌─ Search ──────────────────────────────────────────────────────┐
│ [Search poles...____________________________] [Search] [Clear] │
└────────────────────────────────────────────────────────────────┘
┌─ Filters ─────────────────────────────────────────────────────┐
│ [All statuses ▼] [All confidence ▼] [Sort: Pole Number ▼]     │
│                                          [Apply Filters]       │
└────────────────────────────────────────────────────────────────┘
Showing 3 of 10 poles
```

- Clear button removes `q` param and returns to base URL
- Active filter values are visually preserved in selects via Jinja `selected` logic
- "Showing N of M poles" shown above the pole table

---

## Route changes: `app/routes/workspace.py`

The `view_job()` function is extended to:
1. Parse new params from `request.args`: `q`, `status`, `photos`, `conflicts`, `sort`
2. Get all poles (for total count and stats)
3. Apply `PoleFilterEngine.filter()` on the full pole list
4. Pass `total_poles` (unfiltered count) to template

---

## Acceptance Criteria

- Text search on `q` filters pole list to matching poles
- `status` filter returns only poles at that readiness level
- `confidence` filter returns only poles at that linking confidence
- `photos=yes` returns only poles with `field_photo_count > 0`
- `conflicts=yes` returns only poles with `len(conflict_flags) > 0`
- Multiple filters combine with AND logic
- `sort_by` orders results correctly
- "Showing N of M poles" displays correct counts
- Active filter values preserved in form on page reload
- No filters → same result as current unfiltered view
- Existing `?design_ready`, `?evidence_quality`, `?match_confidence`, `?has_flags` params
  continue to work
- `pytest -q` passes with no regressions

---

## Out of Scope — Stage 7E

- Cross-job search (different feature — requires job index layer)
- Full-text search of photo content
- Saved filter presets
- Export filtered results (Stage 7C)
- Real-time client-side filtering without page reload (Option B — future enhancement)
