# Current Active Phase

Stage 5 - Pilot Hardening & Operational Review Workflow

## Active Priority

Move GridFlow from a completed Stage 4C backend pipeline into a pilot-ready operational review workflow.

Stage 4C is complete:

- Baseline ingestion operational.
- Field evidence import operational.
- Baseline-to-field matching operational.
- Merge + QA operational.
- Unified pipeline CLI operational.

The current priority is not more core reconciliation logic. The current priority is making the completed backend pipeline usable, reviewable, and pilot-ready for real ICP/Tier-1 evaluation.

## Current Work Themes

### Stabilize Stage 4C

- Keep pipeline outputs stable.
- Preserve structured JSON, CSV, and Markdown outputs.
- Keep CLI behavior predictable.
- Maintain test coverage across baseline, field, matching, merge, and pipeline layers.
- Protect governance-safe wording around design blockers and DNO verification.

### Operational Review Workflows

- Define how designers review merged records.
- Define how survey evidence is navigated.
- Define how verification flags become DNO request actions.
- Define review states such as reviewed, awaiting DNO data, requires re-survey, and approved for design preparation.

### Review Workspace Planning

- Plan Stage 5 review UI.
- Support evidence/photo review.
- Support merged record exploration.
- Support blocker/action dashboards.
- Support export packaging.

### Multi-job Validation

- Validate beyond P_LOCAL_001 where safe data is available.
- Test larger pole counts.
- Track DNO format differences.
- Record limitations honestly.

### Pilot Preparation

- Prepare ICP/Tier-1 pilot materials.
- Package surveyor and designer guidance.
- Prepare DNO data request templates.
- Define pilot success criteria.

### Workflow Packaging

- Package outputs so a designer can move from survey evidence to DNO data request without manually interpreting raw JSON.
- Preserve audit traceability from baseline to field evidence to match register to merged QA output.

## Current Acceptance Direction

Stage 5 work should prove:

- Stage 4C outputs are understandable by a designer.
- Evidence traceability is clear.
- DNO data requirements are explicit.
- The workflow can support a real pilot.
- GridFlow remains honest about what is verified and what still requires DNO data.

## Active Boundaries

Do not claim:

- final engineering design capability,
- DNO data replacement,
- autonomous design authorization,
- production multi-user deployment,
- PoleCAD export,
- broad multi-DNO production validation.

Do preserve:

- evidence-based claims,
- source authority hierarchy,
- verification flags,
- design blocker visibility,
- Stage 4C test stability.
