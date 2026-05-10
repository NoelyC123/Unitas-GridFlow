# 40 — Validation Audit

Snapshot: master HEAD `f2587ed`, audit date 2026-05-10.

## Automated test status

| Aspect | Result |
|---|---|
| `pytest -v` | **866 passed**, 13 pre-existing third-party warnings |
| `pre-commit run --all-files` | All hooks pass: trim-trailing-whitespace, fix-end-of-files, check-yaml, check-json, check-large-files, ruff (legacy alias), ruff-format |
| Test runtime | ~2.3 s on the dev machine |
| Coverage of Stage 4 library | 23 tests across schema / validators / template generator |
| Coverage of C2E2 popup rendering | 7 tests in `tests/test_c2e2_popup_rendering.py` |
| Coverage of project-control scripts | 10 tests in `tests/test_project_control_scripts.py` + 7 in `test_control_status.py` |
| Coverage of manual-review harness | 5 tests in `tests/test_manual_review_harness.py` |

The 866 number is the canonical count for the next milestone. Any
branch that drops below this without explicit justification has
introduced a regression.

## Browser validation (manual review harness)

The most recent recorded harness runs (per
`AI_CONTROL/04_VALIDATION_LOG.md`):

| Run | Branch | Jobs | Verdict | Report |
|---|---|---|---|---|
| 2026-05-09T20:40:39Z | `codex/c2f-review-focus-issue-filtering` | `P008/F001`, `P010` | pass | `validation_runs/20260509_204010/validation_report.md` |
| 2026-05-09T21:16:02Z | `codex/c2g-lifecycle-replacement-visualization` | `P008/F001`, `P010` | pass | `validation_runs/20260509_211538/validation_report.md` |

Older runs from the C2D phase exist in archived forms but are no
longer the canonical evidence baseline.

## Jobs covered by the most recent UI validation

- `P008/F001` (alias `Bellsprings`) — the reference 11kV survey.
- `P010` (alias `Gordon`) — the densest real route.

**Not yet covered in 2026-05** runs:

- `P005/F001` — listed in `README_MANUAL_REVIEW.md` as a recommended
  job; no recent validation evidence on master.

## Failures.json status

The two most recent recorded harness runs both produced `failures.json
= []`. The harness's screenshot-on-failure policy means
`validation_runs/<UTC>/screenshots/` is *not* present in those run
directories — that is a **clean run**, not a missing run.

## Known open bugs (audit-discovered)

| ID | Severity | Source | Description |
|---|---|---|---|
| **VLD-1** | High | [22_STAGE4_TECHNICAL_AUDIT.md](22_STAGE4_TECHNICAL_AUDIT.md) on `claude-code/stage4-structured-capture-technical-audit` (not on master) | `is_blank("none")` returns `True` in `app/structured_capture_validators.py`, erasing valid `none` enum values for `stay_type`, `equipment_type`, `lean_direction`, `lean_severity`. Stage 4 library only — not in the runtime path, so not user-facing today. |
| **VLD-2** | Medium | This audit | The Stage 4 schema has no `pole_id` / `project_id` / `file_id` field. Cannot key Stage 4 rows to specific poles. Library-only impact today. |
| **VLD-3** | Low | This audit | `app/field_reference.py` does not register a `source: "structured_capture"` value. Popup renderer has no path for Stage 4 fields. Library-only impact today. |
| **VLD-4** | Low | This audit | `P005/F001` has not been run through the manual review harness in any 2026-05 entry. |
| **VLD-5** | Medium | Aborted merge of `claude-code/c2e2-support-suite` | Merge spec assumed master had the *old* popup behaviour; reality is master is *stricter* than the branch. Future merge attempts must not blindly follow "keep branch side". |

None of VLD-1, VLD-2, VLD-3 affect runtime today because Stage 4 is
library-only. They become release-blocking when Stage 4 integration
work begins.

## Evidence storage

The harness writes:

```
validation_runs/<UTC-timestamp>/
├── validation_report.md
├── console_log.txt
├── failures.json
└── screenshots/   (only failures, unless --evidence-screenshot is passed)
```

`validation_runs/` is git-tracked at the directory level (a `.gitkeep`
exists; `.gitignore` excludes the run subdirectories). This means
**run output is local-only** — it is not preserved in git or pushed
to origin.

### Should evidence be formalised?

**Yes — for milestone runs only.** The recommendation:

1. Local runs remain ephemeral (current behaviour).
2. **Milestone runs** (the harness run that gates a tag) should be
   archived: copy the `validation_runs/<UTC>/` directory to a
   side-car repo or a release artifact, and reference its location in
   the `04_VALIDATION_LOG.md` entry for the milestone.
3. Per-screenshot review during PRs is still a human-only activity;
   the harness verifies behaviour, humans verify experience.

This is a process recommendation; do not implement it in this audit.

## Recommended validation gates per task type

| Task type | Required gates |
|---|---|
| App code change | `pytest -v` + `pre-commit run --all-files` |
| Map-viewer / popup change | All of the above + `python scripts/manual_review.py --jobs P008/F001 P010 --suite baseline --checklist <relevant>.yml` |
| Library-only (Stage 4 / control scripts) | `pytest -v` + targeted file tests + `pre-commit run --all-files` |
| Docs only | `pre-commit run --all-files` (markdown lints + trim-trailing-whitespace) |
| Branch retirement | Confirm `master` HEAD pre/post; confirm `git branch --merged master` lists the branch; **never** `--no-merged` |

## What this audit confirms

- Master is at the cleanest state of any moment in the last 30 days.
- 866 tests pass; pre-commit clean; no in-flight work.
- The two recent harness runs (`P008/F001`, `P010`) produce `failures.json = []`.
- Stage 4 audit-known bugs are **not** in the runtime path.
- No user-facing regressions are recorded as of 2026-05-10.

## What this audit does not confirm

- That `P005/F001` would pass the harness today (no recent run).
- That the `claude-code/c2e2-support-suite` regression tests still
  apply under master's stricter `c2e2SupportPopupSections` (a
  cherry-pick task should re-run them).
- That the older C2D feature branches' tests work when checked out (no
  obligation to run them; they're retirement candidates).
