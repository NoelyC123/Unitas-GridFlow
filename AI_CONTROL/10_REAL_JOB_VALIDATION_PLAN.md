> **HISTORICAL — Stage 2 closure document. Read-only.**
> This document describes completed Stage 2 work. Do not update it.
> For current project state see `01_CURRENT_STATE.md`.

# Real Job Validation Plan

## Purpose

This document is the validation source of truth for the current C2/D review workspace.

This is a validation-first phase. The goal is to inspect real/local jobs manually, record observed findings, and only then decide whether Codex should implement focused fixes.

C2D-AA through C2D-AD improved the map workspace, popup wording, angle highlight semantics, and review UI. Those changes make the workspace easier to review; they do not prove that the underlying engineering logic is correct.

No new implementation task is approved until validation findings exist.

## Validation Categories

### Asset Classification

Validation questions:

- Does GridFlow classify each record as the correct asset type for the source evidence?
- Are existing poles, proposed poles, context/crossing records, third-party infrastructure, stays, and anchors separated correctly?
- Are context records kept out of pole-specific evidence gaps and structural QA where appropriate?
- Are any records over-promoted into electric-network assets without supporting evidence?
- Are labels and marker types truthful when the source code/remark is ambiguous?

### Stay Evidence

Validation questions:

- Does the workspace correctly distinguish captured stay evidence, inferred stay evidence, and absent stay evidence?
- Are angle poles with no stay evidence flagged only when the source evidence supports that review need?
- Are stay/anchor records linked to the right parent or nearby structural record?
- Are stay-related warnings useful, or do they create false positives on the checked jobs?
- Does popup wording avoid implying a stay exists where only an inference or missing-evidence cue exists?

### Span Sequencing

Validation questions:

- Does the displayed route/span sequence match the real source route evidence?
- Are context/crossing records excluded from structural span sequencing where appropriate?
- Are unusual short/long spans genuine route issues, duplicate GPS bounces, replacement-pair artefacts, or sequencing errors?
- Do span labels and span-panel entries help review the route, or do they mislead the user?
- Are span/crossing links useful for engineering review on the checked jobs?

### Lifecycle Matching

Validation questions:

- Are existing/proposed lifecycle states assigned correctly?
- Are EX/PR replacement links plausible against the real source evidence?
- Are suggested replacement links clearly framed as map evidence, not reviewed design assignments?
- Are unmatched or ambiguous lifecycle relationships visible enough for manual review?
- Do lifecycle markers, dashed links, and PDF/report wording stay consistent?

### Irish Grid Coordinates

Validation questions:

- Are Irish Grid/TM65 coordinates detected and converted correctly where present?
- Do map positions align with expected route geography and source easting/northing evidence?
- Are coordinate warnings meaningful and not caused by conversion or source-format misunderstandings?
- Are OSGB and Irish Grid jobs handled distinctly where the source evidence differs?
- Do coordinate displays preserve enough source evidence for manual verification?

### Popup Field Gaps

Validation questions:

- Do existing pole popups distinguish known evidence from missing survey evidence?
- Do proposed pole popups treat missing future specs as design decisions pending?
- Do context/crossing popups avoid irrelevant pole-field gaps?
- Do equipment/photo fields avoid claiming absence where the export only lacks evidence?
- Do span/cable popups keep voltage, conductor, cable, phase, and core wording span/cable-owned?

### QA Rule Usefulness

Validation questions:

- Are FAIL/WARN/INFO outputs useful to a designer reviewing these real jobs?
- Which rules produce actionable findings, and which produce noise?
- Are missing-field rules applied to the right asset types?
- Are context/crossing, stay, span, and lifecycle warnings prioritised appropriately?
- Are any QA findings blocked by stale fixture data rather than current runtime behaviour?

## Findings Format

Each finding must include:

- Finding ID:
- Job:
- Record / Point:
- Source evidence:
- GridFlow output:
- Expected behaviour:
- Impact:
- Recommended fix:

Use one finding per discrete issue. Do not merge unrelated issues into one finding.

## Job Sections

This is a living document. Findings are added during manual validation. The sections below are intentionally not pre-filled.

### P005/F001

Findings:

### P008/F001

Findings:

### P009/F001

Findings:

### P010/F001

Findings:

## Notes

- This is a living document.
- Findings are added during manual validation.
- Findings are not pre-filled.
- Do not infer findings without manual validation evidence.
- Do not start implementation work from this document until specific findings have been recorded and prioritised.
