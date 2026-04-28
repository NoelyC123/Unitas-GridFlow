# Project Reference

**Purpose:** Preserve historical context and wider project documentation without bloading day-to-day control files.

**This file is reference only.** It is not part of the active operational control layer.

---

## Project evolution

The project has evolved through multiple iterations and naming conventions:

### SpanCore (original phase)

- Initial DNO compliance / QA tool concept
- Early design and problem definition
- Decision memos and initial architecture work
- Archived but still useful for historical understanding

### EW Design Tool (middle phase)

- Secondary naming convention during development
- Broader design-tool exploration
- Later deprecated in favour of the narrow MVP approach
- Historical only, not for active development

### Unitas GridFlow (current phase)

- Final, canonical name for the project
- Narrow pre-CAD QA and compliance tool
- Current active repository and development branch
- All future work happens here

---

## Active repository locations

### Active development

- **GitHub:** `https://github.com/NoelyC123/Unitas-GridFlow`
- **Local:** `/Users/noelcollins/Unitas-GridFlow`
- **Branch:** `master`

### Archive/reference

- `_archive/` contains historical materials, previous control-layer files, old exports, synthesis documents, and quarantined code
- `_archive/` is reference-only unless explicitly needed

Do not treat archived material as active instruction.

---

## Current structural model

The repository is deliberately organised into three categories:

### 1. Active project surface

These are the live files and folders used for current development:

- `AI_CONTROL/`
- `app/`
- `tests/`
- `sample_data/`
- `README.md`
- `CHANGELOG.md`
- `CLAUDE.md`
- `PROJECT_DEEP_CONTEXT.md`
- root config/runtime files

These define the current working system.

### 2. Archive/reference surface

Historical, archived, or non-active materials live under:

- `_archive/control_layer/old_ai_control/`
- `_archive/docs/PROJECT_SYNTHESIS/`
- `_archive/docs/FRONTEND_FINAL_IMPLEMENTATION.md`
- `_archive/docs/MANIFEST.md`
- `_archive/docs/PROJECT_OPERATING_MODEL.md`
- `_archive/docs/RUNBOOK.md`
- `_archive/admin/GITHUB_ADMIN/`
- `_archive/quarantine/old_quarantine/`
- `_archive/ai_bundles/`

These are preserved for historical understanding, not active development.

### 3. Local/tool-specific surface

These exist in the working repo but are not part of the shared project truth:

- `.env`
- `.vscode/`
- `.claude/`
- `.venv312/`
- caches / coverage files

---

## Active control layer

The active operational control layer is:

- `AI_CONTROL/00_PROJECT_CANONICAL.md`
- `AI_CONTROL/01_CURRENT_STATE.md`
- `AI_CONTROL/02_CURRENT_TASK.md`
- `AI_CONTROL/03_WORKING_RULES.md`
- `AI_CONTROL/04_SESSION_HANDOFF.md`
- `AI_CONTROL/05_PROJECT_REFERENCE.md`
- `AI_CONTROL/06_STRATEGIC_REVIEW_2026-04-22.md`
- `AI_CONTROL/28_DOMAIN_REFERENCE_SUMMARY.md`
- `AI_CONTROL/29_PRACTITIONER_REVIEW_SUMMARY.md`

### Purpose of each file

- `00_PROJECT_CANONICAL.md` — project identity and canonical model
- `01_CURRENT_STATE.md` — current state of the live system
- `02_CURRENT_TASK.md` — immediate next work
- `03_WORKING_RULES.md` — how to work on the project
- `04_SESSION_HANDOFF.md` — latest session continuity
- `05_PROJECT_REFERENCE.md` — this file, for historical/reference context
- `06_STRATEGIC_REVIEW_2026-04-22.md` — distilled conclusions from the external AI strategic review
- `28_DOMAIN_REFERENCE_SUMMARY.md` — repo-safe development summary of the private domain reference, evidence-quality model, D2D boundary, and future implementation questions
- `29_PRACTITIONER_REVIEW_SUMMARY.md` — repo-safe summary of the full 2026-04-28 practitioner review and prioritised remediation plan

---

## Historical synthesis and strategy documents

The deeper strategic and historical reasoning for the project is preserved under:

- `_archive/docs/PROJECT_SYNTHESIS/`

This includes:

- `00_RAW_AI_RESPONSES/` — raw AI analyses and exploratory thinking
- `01_COMPARISON/` — comparison and evaluation work
- `02_FINAL_SYNTHESIS/` — consolidated synthesis documents
- `03_DECISION_MEMO/` — strategic decision records
- `04_EXECUTION_ALIGNMENT/` — execution planning
- `05_SUPPORT_NOTES/` — prompts, notes, reviews, follow-up context

### Purpose

These explain **why** past decisions were made.

### Rule

Do not treat these as daily operational instructions. Use them only when strategic history or rationale is needed.

---

## External AI review process (2026-04-22)

A separate external AI review process was completed outside the repo using a dedicated review pack.

That process gathered analysis from multiple AI systems and produced:

- raw review responses
- a comparison document
- a decision memo
- a final synthesis

These external review artefacts were intentionally kept **outside the live repo**.

### Reason

The live repository should contain only the distilled strategic conclusions, not the full raw review archive.

### Result

The important conclusions from that review were folded back into the live project truth via:

- `AI_CONTROL/01_CURRENT_STATE.md`
- `AI_CONTROL/02_CURRENT_TASK.md`
- `AI_CONTROL/04_SESSION_HANDOFF.md`
- `AI_CONTROL/06_STRATEGIC_REVIEW_2026-04-22.md`
- `CHANGELOG.md`

---

## Multi-AI workflow background

The project has used multiple AI systems across its earlier strategic phases.

### Purpose of that workflow

- challenge assumptions
- compare options
- preserve decision reasoning
- avoid rediscovering the project from scratch

### Result

The strongest conclusions from those earlier phases were consolidated into:

- the active control layer
- the live repo structure
- the current narrow MVP direction

The old raw and synthesis materials are now historical context, not active instruction.

---

## Archive locations and meaning

### `_archive/control_layer/old_ai_control/`

Older control-layer files that were superseded by the cleaned active control layer.

### `_archive/docs/PROJECT_SYNTHESIS/`

Historical strategic reasoning, AI analysis, and project synthesis.

### `_archive/admin/GITHUB_ADMIN/`

Archived GitHub/admin planning material.

### `_archive/quarantine/old_quarantine/`

Legacy or reference-only code and materials that were intentionally removed from the active project surface.

### `_archive/ai_bundles/`

Old upload/export bundles used for earlier AI workflows and handoffs.

---

## How to use this file

Read this file when you need to understand:

- how the project evolved
- what older naming conventions meant
- where archived materials now live
- how historical reasoning is organised
- what kinds of materials exist outside the active control layer
- how the external AI review work relates to the live repo

Do **not** use this file to decide the current task or current live status.

For that, use:

- `AI_CONTROL/01_CURRENT_STATE.md`
- `AI_CONTROL/02_CURRENT_TASK.md`
- `AI_CONTROL/06_STRATEGIC_REVIEW_2026-04-22.md`

---

## Important reminders

- Do not broaden scope based on historical material alone.
- Do not restore archived or quarantined code blindly.
- Do not treat old repo names as current project identity.
- Do preserve archive material, because it explains earlier decisions.
- Do keep raw external review artefacts outside the live repo unless there is a specific reason to import them.
- Do rely on the active control layer for current truth.

---

## Summary

This file exists to preserve continuity without polluting the active operational layer.

It helps future sessions, tools, and AIs understand:

- where the project came from
- how it changed
- where old materials were moved
- how to distinguish live files from historical ones
- how the external AI review relates to the live project without becoming a second truth system
