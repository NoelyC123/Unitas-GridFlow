# Stage 4B: Matching Confidence Model

## Purpose

Define repeatable rules for assessing baseline-to-field correlation confidence.

This model scores **identity match confidence** only: whether a baseline asset and field evidence folder refer to the same physical support. It does not score engineering design readiness, asset condition certification, load capacity, voltage certainty, or DNO approval status.

## Methodology Scope Limits

- HIGH confidence means the baseline-to-field identity correlation is strong for the available evidence.
- HIGH confidence does not mean the pole is design-ready.
- HIGH confidence does not remove the need for DNO engineering data where design decisions require voltage, conductor, pole class, load, inspection, or ownership records.
- Confidence scoring is for baseline correlation and review prioritisation, not design authorization.
- P_LOCAL_001 demonstrates viability for this dataset structure: ENWL popup screenshots, field photos, and notes arranged in the normalized evidence folders.
- Future datasets with different evidence quality, missing support numbers, underground-only assets, multi-circuit complexity, EHV assets, or sparse photos may require additional manual review or a controlled pilot.

## Assumptions

- Support numbers in ENWL popup screenshots are treated as baseline identifiers, not independently certified engineering records.
- Map locations are sufficient for correlation checks, but not for survey-grade design positioning unless independently confirmed.
- Field observations are descriptive evidence and may be constrained by access, lighting, vegetation, distance, or safety limits.

## Confidence Levels

### HIGH CONFIDENCE

Criteria for definitive match:

- Support number visible in field photos OR map popup
- Pole location matches baseline coordinates (+/-10m)
- Equipment/conductor configuration matches baseline expectations
- Route context consistent (pole sequence, line direction)
- No conflicting evidence

### MEDIUM CONFIDENCE

Criteria for probable match:

- Support number unclear but route context strong
- Location matches (+/-20m) with equipment partially consistent
- Map popup exists but field verification incomplete
- Minor discrepancies explainable (viewing angle, seasonal changes)

### LOW CONFIDENCE

Criteria for uncertain match:

- Only approximate location available
- Ambiguous structures or multiple candidates
- Conflicting evidence between baseline and field
- Insufficient field photos for verification
- Missing critical identifiers

## Identity Verification Checklist

For each pole, verify:

- [ ] Support number visible (carved/painted/plate)
- [ ] Location verified via map screenshot
- [ ] Pole top configuration photographed
- [ ] Pole base condition photographed
- [ ] Warning signs photographed (if present)
- [ ] Equipment matches baseline expectations
- [ ] Route context confirms position in network

## Match Rejection Criteria

Reject match if:

- Support number contradicts baseline
- Location error >50m without explanation
- Equipment fundamentally incompatible with baseline voltage
- Clear evidence this is wrong pole

## Uncertainty Handling

When uncertain:

- Flag for manual review
- Document conflicting evidence
- Request additional field verification
- Do NOT force-fit ambiguous matches

## Untested / Limited Edge Cases

The P_LOCAL_001 evidence set does not fully prove behaviour for every network scenario. Additional validation may be needed for:

- Underground-only assets with limited visible support evidence
- Dense multi-circuit poles where conductors/equipment are difficult to separate visually
- EHV or transmission assets outside the current LV/HV evidence pattern
- Assets with missing or contradictory DNO map popup identifiers
- Multiple nearby supports within the same coordinate tolerance
- Joint-use assets where non-DNO equipment dominates the field view
