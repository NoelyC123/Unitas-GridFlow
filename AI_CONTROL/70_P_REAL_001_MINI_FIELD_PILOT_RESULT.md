# P_REAL_001_MINI Field Pilot Result

Purpose: tracked, non-sensitive project record of the `P_REAL_001_MINI` local field-pilot shakedown. This file records the outcome without committing real photos, the real CSV, or local validation artefacts.

## Pilot Type

- Informal real-world mini pilot
- Public-access local survey
- Workflow and evidence-handling shakedown, not Stage 4C approval evidence

## Dataset Summary

- Total rows: **10**
- Final evidence photos: **33**
- Valid rows: **10**
- Invalid rows: **0**
- Merge-ready rows: **2**
- Review-required rows: **8**
- Blocked rows: **0**

## Evidence Cleanup Summary

- Missing referenced photos: **0**
- Unreferenced photos: **0**
- Duplicate photo names: **0**
- Invalid filename patterns: **0**

## Remaining Warnings

- `verification_required=yes`: **8**
- Low-confidence rows: **7**
- Evidence-status verification warnings: **7**

## Verdict

- Successful mini-pilot shakedown: **yes**
- Stage 4C gate result: **PARTIAL / RE-PILOT REQUIRED**
- Operational reading: the workflow is usable, the evidence-pack cleanup process works, and the validator behaves as intended on a real local survey-derived pack.

## What It Proves

- A real local survey-derived mini pilot can be converted into a Stage 4-compatible local evidence pack without runtime integration.
- The Stage 4 pilot validator can process a real mini-pilot CSV plus a curated evidence folder and produce a clean evidence audit.
- Evidence filename normalisation and reference cleanup can eliminate missing-photo, surplus-photo, duplicate-name, and invalid-filename warnings.
- The current Stage 4B workflow is strong enough for operator rehearsal, data-handling checks, and validation reporting.

## What It Does Not Prove

- It does not prove exact electrical attributes for the surveyed supports.
- It does not prove technical correctness where access, distance, private land, vegetation, or partial views limited confidence.
- It does not prove that Stage 4C runtime integration is safe.
- It does not replace a controlled pilot against a real GridFlow/Trimble job baseline with exact `pole_id` matching.

## Why Stage 4C Remains Blocked

- Only **2** rows are merge-ready.
- **8** rows remain review-required.
- The warning profile still reflects material real-world uncertainty rather than evidence-pack hygiene.
- This was an informal local mini pilot, not a controlled baseline pilot.
- Stage 4C still requires stronger field evidence plus Noel's explicit manual go/no-go decision.

## Next Recommended Pilot

- Run a controlled pilot against a real GridFlow/Trimble job baseline with exact `pole_id` matching.
- Favour supports with stronger access, closer capture, and clearer identifier evidence.
- Use the current Stage 4 pilot validator and operator workflow again, but treat the result as a formal gate input rather than a shakedown run.

## Boundary

- No real photos committed
- No real CSV committed
- No local validation reports committed
- Stage 4C runtime integration remains blocked
