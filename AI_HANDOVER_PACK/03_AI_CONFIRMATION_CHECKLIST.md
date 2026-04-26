# AI Confirmation Checklist

Use this checklist after giving the handover pack to any AI/tool.

The AI should be able to answer all of these correctly before you let it advise or work on the project.

## Project Identity

- [ ] Confirms Unitas GridFlow is a survey-to-design workflow intelligence and automation tool.
- [ ] Confirms it is for UK electricity distribution overhead line survey/design workflows.
- [ ] Confirms it sits between field survey output and office design work.
- [ ] Does not describe it as only a CSV checker.

## Current Stage

- [ ] Confirms Stage 1 is complete.
- [ ] Confirms Stage 2 is current.
- [ ] Confirms Stage 2 means D2D elimination / PoleCAD-ready output.
- [ ] Does not jump straight to tablet app, DNO submission, or broad platform build.

## Source Of Truth

- [ ] Confirms real survey files are highest truth.
- [ ] Confirms AI_CONTROL files are current project control layer.
- [ ] Confirms CLAUDE.md and WORKFLOW_SYSTEM.md define tool roles and workflow.
- [ ] Confirms archive/superseded files should not drive current work.

## Tool Roles

- [ ] Confirms Claude Desktop is orchestrator.
- [ ] Confirms Claude Code/Cursor is builder.
- [ ] Confirms ChatGPT is second opinion/commercial/writing support.
- [ ] Does not claim all AIs have equal authority.

## Development Completed So Far

- [ ] Mentions raw Trimble/controller dump parsing.
- [ ] Mentions CRS detection/conversion.
- [ ] Mentions role classification for structural/context/anchor records.
- [ ] Mentions EX/PR replacement pair detection.
- [ ] Mentions confidence-aware QA and evidence gates.
- [ ] Mentions interactive map/PDF pre-design briefing.
- [ ] Mentions 211 passing tests.
- [ ] Mentions 4 real NIE/SPEN files validated.
- [ ] Mentions Phase 3A context classification/span threshold/location cleanup.
- [ ] Mentions Stage 2A implementation commit `5f99bf0`.
- [ ] Mentions Stage 2B implementation commit `54417ba`.
- [ ] Mentions Stage 2B validation bugfix commit `e51d0ee`.
- [ ] Mentions provisional D2D candidate CSV export.
- [ ] Mentions D2D interleaved working view export.
- [ ] Mentions `sequenced_route.json`.
- [ ] Mentions route sequencing, EXpole matching, span calculation, deviation angles, section-aware output, detached record handling, confidence warnings and design numbering.

## Immediate Next Work

- [ ] Focuses on Stage 2.
- [ ] Talks about clean, sequenced, PoleCAD-ready output.
- [ ] Talks about replacing/reducing D2D spreadsheet work.
- [ ] Treats Stage 2A and Stage 2B as implemented.
- [ ] Treats Stage 2B as validated against the current Gordon/NIE file set.
- [ ] Treats the next phase as Stage 2C polish pass vs Stage 2 completion review.
- [ ] Mentions Gordon PR1/PR2 manual split files as validation evidence.
- [ ] Keeps work small, testable and validation-led.
