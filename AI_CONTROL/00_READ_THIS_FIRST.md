# AI Control — Read This First

This folder is the active coordination layer for the SpanCore project.

It exists so ChatGPT, Claude app, and Claude Code all work from the same current truth and do not drift.

## Required read order for any AI

1. AI_CONTROL/00_READ_THIS_FIRST.md
2. AI_CONTROL/01_PROJECT_TRUTH.md
3. AI_CONTROL/02_CURRENT_STATE.md
4. AI_CONTROL/03_CURRENT_TASK.md
5. AI_CONTROL/04_SESSION_HANDOFF.md
6. AI_CONTROL/05_AI_ROLE_RULES.md

## Deep reference documents

After reading the AI_CONTROL files, use these as the main deeper references:

1. _reference/SPANCORE_AI_SYNTHESIS/SPANCORE_SYNTHESIS_READ_FIRST.md
2. _reference/SPANCORE_AI_SYNTHESIS/02_FINAL_SYNTHESIS/SPANCORE_MASTER_SYNTHESIS.md
3. _reference/SPANCORE_AI_SYNTHESIS/03_DECISION_MEMO/FINAL_DECISION_MEMO.md
4. _reference/SPANCORE_AI_SYNTHESIS/04_EXECUTION_ALIGNMENT/EXECUTION_ALIGNMENT_PLAN.md
5. _reference/SPANCORE_MASTER_HANDOVER/README_HANDOVER_FIRST.md

## Canonical code locations

- live code = project root + app/
- _reference = important non-runtime project documents
- _archive = old moved artifacts / exports / scans
- _quarantine = legacy or reference-only code, do not restore blindly

## Current development rule

Do not broaden scope.
Do not redesign the product.
Do not invent new platform goals.
Recover the narrow MVP first.
