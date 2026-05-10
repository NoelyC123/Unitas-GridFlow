---
status: ACTIVE
created: 2026-05-10
last_reviewed: 2026-05-10
---

# 55 — Stage 4 Risk Register

Known risks in Stage 4 structured capture. Rated L (likelihood) × I (impact), 1–3 scale. Score = L × I.

## Active risks

| ID | Risk | L | I | Score | Mitigation | Status |
|---|---|---|---|---|---|---|
| R01 | Wrong pole_id match corrupts live job | 2 | 3 | 6 | Exact-match only, no fuzzy; log all merges; Trimble values never overwritten; integration test | Monitoring |
| R02 | Fake completeness: Stage 4 values present but meaningless | 3 | 2 | 6 | Completeness classification; QA warn on all-unknown fields; don't conflate min/complete | Mitigating |
| R03 | Stage 4 leaks into map popup before 4D | 2 | 2 | 4 | Leakage tests; AST import scanning; merge safety checks | Active guards |
| R04 | pole_id format mismatch (P008-001 vs P008001) | 3 | 2 | 6 | Strip whitespace, normalise dashes; log unmatched IDs; real pilot validates format | Monitoring |
| R05 | Stage 4B preview diverges from 4C merge behaviour | 2 | 2 | 4 | Use same library functions; integration test | Prevention |
| R06 | Schema drift breaks previously valid CSVs | 2 | 2 | 4 | Golden sample regression suite; schema changelog | Monitoring |
| R07 | AI worker extends Stage 4 scope without gate approval | 2 | 3 | 6 | merge_safety_check boundary checks; "Do Not Start" explicit in handoff | Prevention |
| R08 | Duplicate pole_id across separate uploads | 2 | 2 | 4 | Within-upload detection implemented; Stage 4C must check for existing records | Monitoring |

## Closed risks

| ID | Description | Closed | Resolution |
|---|---|---|---|
| VLD-1 | `"none"` in `_BLANK_TOKENS` erases valid evidence | 2026-05-10 | Removed from blank tokens; field-aware none handling added (Codex) |
| VLD-2 | No `pole_id` field in schema — no stable merge key | 2026-05-10 | row_identity group added with `pole_id` required field (Codex) |
| VLD-3 | `structured_capture` not registered as source | 2026-05-10 | Source label added library-only, popup not yet wired (Codex) |

## Review schedule

At: Stage 4B merge, Stage 4C gate, after each field pilot, after schema change.
