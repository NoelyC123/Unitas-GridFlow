# Unitas GridFlow AI Handover Pack

This pack is for updating Claude Desktop, ChatGPT, Claude Code, Cursor, Codex, Gemini, or any other AI/tool with the latest Unitas GridFlow project direction.

## Critical Instruction

Treat this handover pack as the current project context.

Do not rely on older conversations, older batch numbers, stale project assumptions, old scripts, old folders, or previous descriptions that frame Unitas GridFlow as only a CSV QA checker.

## Current Project Identity

Unitas GridFlow is a survey-to-design workflow intelligence and automation tool for UK electricity distribution overhead line work.

It is a pre-CAD QA gatekeeper and workflow automation layer that sits between field survey output and office-based design work.

Short definition:

Unitas GridFlow turns raw field survey information into structured, validated, design-ready data for electricity network design teams.

## Current Stage

Stage 1 is complete.

Current focus is Stage 2: D2D elimination / PoleCAD-ready output.

The immediate product direction is: raw Trimble/controller dump in, structured sequenced PoleCAD-ready output out, with the manual D2D spreadsheet bridge reduced or removed.

## Latest Implementation State

Stage 2A has now been implemented as a provisional D2D replacement candidate output.

Current confirmed state:

- Stage 2A implementation commit: `5f99bf0`
- Tests: 186 passing
- D2D candidate CSV export added
- `sequenced_route.json` generated per job
- Route sequencing, EXpole matching, span calculation, deviation angle calculation and candidate section breaks implemented
- Next phase: real-file validation and Stage 2B refinement, especially section-aware sequencing against Gordon PR1/PR2 manual split evidence

## Six-Stage Vision

1. Post-survey QA gate
2. D2D elimination / PoleCAD-ready output
3. Live intake platform
4. Structured tablet-based field capture
5. Designer workspace
6. DNO submission layer

## Tool Roles

- Human/domain owner: final authority on real-world process and decisions.
- Claude Desktop: project orchestrator, defines what gets built and why.
- Claude Code/Cursor: primary builder, edits code, runs tests, commits and pushes when instructed.
- ChatGPT: second opinion, commercial thinking, strategy review, wording/help documents.
- Codex/Gemini/others: optional bounded review or second opinion only.

## Read Order For Any AI

1. source_files/CLAUDE.md
2. source_files/WORKFLOW_SYSTEM.md
3. source_files/README.md
4. source_files/AI_CONTROL/00_PROJECT_CANONICAL.md
5. source_files/AI_CONTROL/02_CURRENT_TASK.md
6. source_files/AI_CONTROL/01_CURRENT_STATE.md
7. source_files/AI_CONTROL/04_SESSION_HANDOFF.md
8. source_files/AI_CONTROL/09_PROJECT_ORIGIN_AND_FIELD_NOTES.md
9. source_files/AI_CONTROL/08_OHL_SURVEY_OPERATIONAL_STANDARD.md
10. source_files/CHANGELOG.md

## Superseded / Do Not Treat As Current Direction

Do not use archive files as current project truth unless explicitly asked.

Do not rely on superseded control files if they conflict with current canonical files.

The active source of truth is the current AI_CONTROL files, especially 00, 01, 02, 04, 08 and 09.
