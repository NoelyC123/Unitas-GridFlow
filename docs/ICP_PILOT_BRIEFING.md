# GridFlow ICP Pilot Briefing

## What Is GridFlow?

GridFlow is a survey-to-design workflow tool for UK overhead line infrastructure.

It helps an ICP or contractor capture structured field evidence, correlate that evidence with DNO baseline records, and produce a clear QA report for the designer.

GridFlow is intended to replace ad-hoc photo sharing, manual support number lookups, and unclear survey handoffs with a structured, auditable workflow.

It does not replace DNO engineering data, designer judgement, or formal design approval.

## The Problem It Solves

Current survey-to-design handoffs often involve:

- Unstructured photo collections shared through email, messaging apps, or shared drives.
- Manual support number checks against maps, screenshots, or paper schedules.
- Designer uncertainty about which poles were actually surveyed.
- Repeated requests back to surveyors for missing views or unclear notes.
- General DNO data requests that do not clearly identify which engineering data is missing.

This creates delay, rework, and avoidable uncertainty before CAD design can begin.

## What GridFlow Does

1. The field surveyor captures photos, map screenshots, and notes per pole.
2. GridFlow matches field evidence to the DNO baseline using support number correlation.
3. GridFlow scores match confidence as HIGH, MEDIUM, LOW, or UNMATCHED.
4. GridFlow generates a QA report showing matched poles, conflicts, evidence gaps, and required DNO data.
5. The designer uses the report to prepare a structured DNO data request.
6. Design proceeds only after required DNO engineering data has been received and reviewed.

The output is a practical handoff pack: evidence, match register, verification flags, and designer actions.

## Validated Evidence

P_LOCAL_001 validation, May 2026, ENWL network:

- 10 poles surveyed.
- 10 poles matched to baseline records.
- 100% match rate on the controlled validation dataset.
- 9 HIGH confidence matches and 1 MEDIUM confidence edge case.
- Edge cases included no-popup map evidence, joint user equipment, support number variation, OH/UG transition evidence, transformer poles, and LV terminal/streetlight context.

This demonstrates that the method is viable for a controlled ICP survey-to-design workflow where evidence quality matches the P_LOCAL_001 structure.

It does not yet prove production performance across all DNOs, all voltage levels, all terrain types, or large multi-route jobs. Broader validation is the purpose of an ICP pilot.

## What a Pilot Would Involve

Recommended duration: 4 to 8 weeks.

Recommended scope: 1 to 2 active ICP jobs with an overhead line survey component.

Surveyor requirement: 1 to 2 surveyors using the GridFlow field capture method.

Data requirement: DNO baseline export, GIS screenshots, or equivalent support number data for the survey area.

GridFlow pilot deliverables:

- QA report per job.
- Match register CSV per job.
- Evidence quality summary.
- DNO data request draft.
- Designer workflow feedback session.
- Pilot findings report with limitations and next actions.

What is needed from the ICP:

- Access to a suitable live or recent job.
- Permission to use project survey evidence for controlled pilot evaluation.
- Surveyor time for field capture.
- Designer time to review the QA report.
- Feedback on whether the output fits existing design and DNO request workflows.

## Limitations

- Current controlled validation is based on 10 ENWL poles.
- ENWL-style map evidence is the best tested source so far.
- Other DNO formats require pilot testing and mapping.
- Current workflow is CLI and document based; a designer web interface is planned.
- GridFlow does not certify voltage, conductor specification, pole class, transformer rating, or compliance.
- DNO engineering data remains required before final design.
- Surveyor training is required, typically around 30 minutes for the field capture method.

## Commercial Model

Pilot commercial terms should be agreed before mobilisation.

A practical pilot package should define:

- Number of jobs and approximate pole count.
- Survey support and training expectations.
- Data handling and confidentiality requirements.
- GridFlow processing and report turnaround.
- Review sessions with surveyor, designer, and project manager.
- Post-pilot decision criteria for wider use.

Pricing and licensing should be confirmed separately based on pilot size, deployment model, support needs, and whether the pilot uses live client data.

## Next Step

The recommended next step is a short scoping session with the project sponsor, survey lead, and designer.

The session should confirm:

- Which job is suitable for the pilot.
- Which DNO baseline data is available.
- How survey evidence will be captured and transferred.
- Who will review the GridFlow QA report.
- What decision criteria will be used at the end of the pilot.
