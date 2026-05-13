# GridFlow Designer Guide

## What GridFlow Provides

GridFlow processes field survey evidence and DNO baseline data into a structured designer review pack.

It provides:

- A QA report showing which poles have been surveyed and matched to baseline.
- A structured list of what DNO data is still required for each pole.
- A confidence score for each baseline-to-field identity match.
- Conflict flags where field observations differ from baseline records.
- A spreadsheet-ready summary for filtering, tracking, and preparing data requests.

GridFlow does not provide:

- Engineering design.
- Certified voltage specifications.
- Conductor size, material, or type certification.
- Pole class or strength rating certification.
- DNO compliance certification.
- Automated design approval.

GridFlow is a survey-to-design workflow tool. It helps organise evidence and expose blockers before CAD design. It does not replace engineering judgement or DNO records.

## Understanding the QA Report

### Match Confidence Levels

Match confidence describes the reliability of the baseline-to-field identity match. It does not mean the pole is design-ready.

**HIGH confidence**

The support number is verified from the map popup, the field photos cover the pole adequately, notes are present, and there is no conflicting identity evidence.

Use this pole for design preparation, subject to DNO engineering data being obtained.

**MEDIUM confidence**

There is minor uncertainty in the identity match. Typical causes include:

- No map popup available, with support number inferred from route context.
- Variant support number such as `903201A`.
- Partial photo coverage.
- Map and field context are consistent but not complete.

Review photos and notes before proceeding. If identity matters for design, request DNO confirmation.

**LOW confidence**

There is significant uncertainty. Typical causes include:

- Support number unclear or missing.
- Conflicting support numbers.
- Insufficient photo evidence.
- Multiple candidate poles in close proximity.

Do not rely on this pole for design until manual review or re-survey resolves the issue.

**UNMATCHED**

The baseline pole has no matching field evidence, or field evidence has no matching baseline record.

Schedule re-survey or investigate whether the baseline data or field folder is incomplete.

### Verification Flags

Every pole may show one or more verification flags. These are the items that prevent final design from proceeding until resolved.

**voltage_verification_required**

Do not assume voltage from field observation. Warning signs may be missing, wrong, old, or not visible. Obtain certified voltage from DNO records.

**conductor_verification_required**

Conductor size, type, and material require DNO records. They should not be inferred from photos.

**pole_class_verification_required**

Pole class and strength rating are not field-observable from normal survey evidence. They are required for structural checks, stay calculations, and loading assessment.

**condition_verification_required**

The field survey observed severe or uncertain condition issues. Request DNO re-inspection or obtain current inspection history before design.

**identity_verification_required**

The match confidence is MEDIUM or LOW. Confirm pole identity before relying on it for design.

**equipment_conflict_flag**

Field observations and baseline data appear to disagree. For example, the baseline describes a simple pole but the survey shows transformer equipment. Investigate before design; either source may be out of date or the wrong pole may have been surveyed.

### Design Status

**design_ready**

No verification flags are present. The pole can proceed to design preparation, subject to normal designer checks and project requirements.

In most real survey contexts, design-ready will be uncommon until DNO engineering data has been received.

**design_blocked**

One or more verification flags are present. The QA report lists the specific action needed before design can proceed.

Design-blocked does not mean the survey failed. It means GridFlow has identified exactly what remains unresolved.

## Preparing Your DNO Data Request

Use the GridFlow QA report to structure the request. Group poles by the missing data item instead of sending a general query.

Recommended request structure:

```text
Poles requiring voltage confirmation:
[support numbers]

Poles requiring conductor specification:
[support numbers]

Poles requiring pole class or strength rating:
[support numbers]

Poles requiring identity confirmation:
[support numbers and reason]

Poles requiring DNO re-inspection or condition history:
[support numbers and observed issue]
```

Attach the QA report and the per-pole summary CSV. Offer field photo evidence on request if file size or data handling rules make it unsuitable to send immediately.

## Conflict Resolution

### VOLTAGE_CONFLICT

Field notes suggest one voltage category and baseline records suggest another.

Do not assume either is correct. Request certified voltage from the DNO.

### EQUIPMENT_CONFLICT

Field evidence shows equipment that does not match the baseline asset type.

Possible causes:

- DNO records are out of date.
- Equipment has recently changed.
- The field evidence belongs to a nearby pole.
- The baseline export does not include all equipment attributes.

Resolve before design.

### SUPPORT_NO_CONFLICT

The support number in field notes or folder naming differs from the matched baseline record.

Check the map screenshot, field notes, pole sequence, and route context. If still uncertain, request DNO confirmation or re-survey.

## CSV Summary Usage

The merged dataset CSV is intended for designer tracking.

Recommended workflow:

1. Import the CSV into Excel, Numbers, or your project tracker.
2. Filter `design_blocked = true`.
3. Group by verification flag type.
4. Prepare a structured DNO data request from the grouped lists.
5. Track DNO responses against each support number.
6. Mark poles as cleared only when the required DNO engineering data has been received and reviewed.

Do not remove verification flags simply because field evidence appears clear. Voltage, conductor specification, pole class, equipment ratings, and inspection history require authoritative records.

## Using P_LOCAL_001 as a Reference

The P_LOCAL_001 validation dataset demonstrated that GridFlow can correlate structured field evidence to ENWL baseline records when evidence quality is high.

The validation covered:

- 10 poles.
- Support number matching from ENWL map popups.
- A no-popup edge case.
- A variant support number.
- Joint user equipment.
- OH/UG transition evidence.
- Transformer and streetlight examples.

This supports GridFlow as a practical survey-to-design workflow method. It does not prove that all future jobs, DNO regions, or voltage levels will behave the same way. Designers should continue to review match confidence, verification flags, and source authority on every job.
