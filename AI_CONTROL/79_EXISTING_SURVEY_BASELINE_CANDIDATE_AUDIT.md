# Existing Survey Baseline Candidate Audit

**Date:** 2026-05-11
**Branch:** `codex/audit-existing-files-for-stage4c-baseline-pilot`
**Purpose:** Audit tracked survey/job CSV availability for the next Stage 4C controlled baseline pilot without exposing row-level contents.

---

## Audit Outcome

This worktree does **not** contain any tracked real survey/job CSV files under:

- `uploads/projects/`
- `uploads/jobs/`
- `validation_data/`

The priority candidate paths named for this audit are all unavailable in this checkout. A broader tracked-file scan also found **no other eligible real survey/job CSVs** outside excluded fixture/template/mock/archive locations.

**Result:** there is no auditable tracked baseline CSV in this worktree that is sufficient to start the Stage 4C controlled baseline pilot.

---

## Scan Scope

Priority candidates requested:

1. `uploads/projects/P008/files/F001/Bellsprings_Woodside_Park_11kV_Rebuild_Trimble_Controller_Export.csv`
2. `uploads/projects/P009/files/F001/Bellsprings_Woodside_Park_11kV_Rebuild_Trimble_Controller_Export.csv`
3. `uploads/projects/P009/files/F002/2814_474c_raw_trimble_export.csv`
4. `uploads/jobs/J12946/2814_474c_raw_trimble_export.csv`
5. `uploads/jobs/J57530/2814_4-474_raw_trimble_export.csv`
6. `validation_data/2814_474/raw/2814_4-474_raw_trimble_export.csv`
7. `validation_data/2814_474/raw/2814_474c_raw_trimble_export.csv`
8. `validation_data/gordon_pt1/raw/Gordon Pt1 - Original.csv`

Broader repository scan:

- Included: tracked `*.csv` files in the current worktree
- Excluded: `issues.csv`, `sample_data/mock_survey.csv`, `templates/`, `tests/fixtures/`, `real_pilot_data/`, `validation_runs/`, `_archive/`

---

## Candidate Audit Table

| File path | File type | Total row count | Likely pole_id / point identity column | Likely structure/type/code column | Estimated pole/support count | Suitability | Reason |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `uploads/projects/P008/files/F001/Bellsprings_Woodside_Park_11kV_Rebuild_Trimble_Controller_Export.csv` | CSV (expected) | unavailable | unavailable | unavailable | unavailable | `UNKNOWN / NEEDS MANUAL REVIEW` | File not present in this worktree; no header or count audit possible. |
| `uploads/projects/P009/files/F001/Bellsprings_Woodside_Park_11kV_Rebuild_Trimble_Controller_Export.csv` | CSV (expected) | unavailable | unavailable | unavailable | unavailable | `UNKNOWN / NEEDS MANUAL REVIEW` | File not present in this worktree; no header or count audit possible. |
| `uploads/projects/P009/files/F002/2814_474c_raw_trimble_export.csv` | CSV (expected) | unavailable | unavailable | unavailable | unavailable | `UNKNOWN / NEEDS MANUAL REVIEW` | File not present in this worktree; no header or count audit possible. |
| `uploads/jobs/J12946/2814_474c_raw_trimble_export.csv` | CSV (expected) | unavailable | unavailable | unavailable | unavailable | `UNKNOWN / NEEDS MANUAL REVIEW` | File not present in this worktree; no header or count audit possible. |
| `uploads/jobs/J57530/2814_4-474_raw_trimble_export.csv` | CSV (expected) | unavailable | unavailable | unavailable | unavailable | `UNKNOWN / NEEDS MANUAL REVIEW` | File not present in this worktree; no header or count audit possible. |
| `validation_data/2814_474/raw/2814_4-474_raw_trimble_export.csv` | CSV (expected) | unavailable | unavailable | unavailable | unavailable | `UNKNOWN / NEEDS MANUAL REVIEW` | File not present in this worktree; no header or count audit possible. |
| `validation_data/2814_474/raw/2814_474c_raw_trimble_export.csv` | CSV (expected) | unavailable | unavailable | unavailable | unavailable | `UNKNOWN / NEEDS MANUAL REVIEW` | File not present in this worktree; no header or count audit possible. |
| `validation_data/gordon_pt1/raw/Gordon Pt1 - Original.csv` | CSV (expected) | unavailable | unavailable | unavailable | unavailable | `UNKNOWN / NEEDS MANUAL REVIEW` | File not present in this worktree; no header or count audit possible. |

---

## Repository-Present CSV Findings

Tracked CSV scan result for this worktree:

- Eligible real survey/job CSV files found: **0**
- Only CSV found in `sample_data/`: `sample_data/mock_survey.csv`
- `sample_data/mock_survey.csv` is explicitly excluded from controlled-baseline candidacy because it is mock/synthetic data.

Because there are no tracked real survey/job CSVs here, there is no safe way to score:

- actual header suitability
- stable `pole_id` availability
- support/pole row count
- exact `pole_id` match readiness

---

## Best Candidate Recommendation

**Best candidate in this checkout:** none available.

**Preferred next acquisition target:** the real Trimble export for `P008/F001` or `P009/F001`, provided Noel can place an auditable copy into the working repository or make it available in the audit worktree for header/count inspection.

Reason for that preference:

- these are already named as first-priority candidates
- they are likely to represent real GridFlow project baselines rather than synthetic test artifacts
- they are the strongest candidates for the exact `pole_id` matching requirement defined in docs 73–75

---

## Is an Existing File Enough for the Controlled Pilot?

**No.**

From this checkout alone, there is no existing tracked baseline CSV that is sufficient for the controlled pilot.

To proceed, Noel needs one real accessible baseline CSV that has:

- stable support/pole identity values (`Point`, `Name`, `pole_id`, or equivalent)
- enough support rows for a controlled pilot:
  - preferred: `30–50`
  - fallback: `10–20`
- a usable structure/type/code column to distinguish poles/supports from context rows
- real, non-synthetic Trimble survey data

---

## What Noel Needs To Obtain

Noel should provide or surface **one real baseline CSV** into the auditable worktree, preferably:

1. `P008/F001` Trimble controller export, or
2. `P009/F001` Trimble controller export

Minimum required for the next audit pass:

- file path accessible in the repo/worktree
- CSV headers intact
- exact `pole_id` or point naming preserved
- enough rows to estimate real support coverage

Once one of those files is accessible, the next audit can classify it as:

- `SUITABLE`
- `POSSIBLE FALLBACK`
- `NOT SUITABLE`

with real header/count evidence instead of unavailability.
