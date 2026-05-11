# P_CONTROLLED_001 Post-Field Acceptance Gate

**For: Noel and gate auditor; formal verdict before Stage 4C authorization**

**Date:** 2026-05-11
**Purpose:** Quantitative and qualitative acceptance criteria for field trial validation
**Authority:** Documents 73–75 (Prep, Protocol, Decision Template)
**Scope:** Post-field validation gate — determines GO / CONDITIONAL GO / NO-GO / STOP verdict

---

## Acceptance Criteria: Quantitative

Use validator output to check these metrics:

| Metric | Target | GO | CONDITIONAL GO | NO-GO |
|--------|--------|-----|-------|-------|
| **pole_id exact match rate** | ≥80% | ≥80% | 75–80% | <75% |
| **valid rows** (schema + required fields) | ≥90% | ≥90% | ≥85% | <85% |
| **merge-ready rows** (≥50% threshold) | ≥50% | ≥50% | 40–50% | <40% |
| **review-required rows** (≤50% threshold) | ≤50% | ≤50% | 50–60% | >60% |
| **blocked rows** (cannot merge) | 0 | 0 | 0 | ≥1 |
| **evidence linking coverage** | ≥90% | ≥90% | ≥85% | <85% |
| **missing photos** | 0 | 0 | 0–2 | ≥3 |
| **orphaned photos** | 0 | 0 | 0–2 | ≥3 |
| **duplicate pole_ids** | 0 | 0 | 0 | ≥1 |

**Validator output files to review:**
- `validation_runs/stage4_pilots/P_CONTROLLED_001_FINAL/pilot_validation_report.json` (machine-readable)
- `validation_runs/stage4_pilots/P_CONTROLLED_001_FINAL/pilot_validation_report.md` (human-readable)
- `validation_runs/stage4_pilots/P_CONTROLLED_001_FINAL/evidence_audit.json` (photo linking details)

---

## Acceptance Criteria: Qualitative

Use Noel's operator decision notes (doc 82) to rate these aspects:

| Aspect | Target | GO | CONDITIONAL GO | NO-GO |
|--------|--------|-----|-------|-------|
| **Operator confidence: pole_id accuracy** | 4–5 | 4–5 (reliably matched) | 3–4 (mostly reliable) | <3 (unreliable) |
| **Operator confidence: overall data quality** | 4–5 | 4–5 (ready to use) | 3–4 (acceptable with caution) | <3 (not suitable) |
| **Friction points** (workflow issues) | 0–1 | 0–1 | 1–3 (manageable) | >3 (workflow problem) |
| **Unknown fields** (% of rows) | <5% | <5% (expected uncertainty) | 5–20% (tolerable) | >20% (workflow problem) |
| **Access issues** (% of poles inaccessible) | <10% | <10% (field reality) | 10–30% (documented) | >30% (baseline unsuitable) |
| **Mismatch pattern** | Understood | Clear resolution path | Documented cautions | Indicates baseline unsuitable |

**How to assess:**
- **Confidence ratings:** 1=unreliable, 2=unclear, 3=mixed, 4=mostly reliable, 5=consistently reliable
- **Friction points:** Template clarity, capture ease, equipment issues, safety friction (each documented in doc 82)
- **Unknown fields:** Fields Noel could not fill confidently (voltage guessed, height estimated, condition uncertain)
- **Access issues:** Poles inaccessible without permission, too hazardous, blocked by terrain or private property
- **Mismatch pattern:** Typos, format differences, worn labels, new poles not in baseline — does pattern indicate fixable issues or fundamental baseline mismatch?

---

## Verdict Logic

**GO verdict:** All quantitative AND all qualitative criteria met

**Conditions (all must be true):**
- pole_id ≥80%, valid ≥90%, merge-ready ≥50%, review-required ≤50%, blocked 0, evidence ≥90%, missing 0, orphaned 0, duplicates 0
- **AND** operator confidence (pole_id) ≥4, confidence (overall) ≥4, friction ≤1, unknowns <5%, access <10%
- **AND** mismatch pattern understood with clear resolution path

**Outcome:**
- ✅ New Stage 4C implementation task authorized
- ✅ Noel signs decision template (doc 75) with GO verdict
- ✅ Gate auditor approves with no cautions
- ✅ Claude Code starts runtime integration (upload route, merge algorithm, database)
- ✅ Stage 4C no longer blocked; implementation can proceed

---

## Verdict Logic

**CONDITIONAL GO verdict:** Most quantitative AND most qualitative criteria met, with documented cautions

**Conditions (most must be true, with caution documentation):**
- pole_id 75–80%, valid ≥85%, merge-ready 40–50%, review-required 50–60%, blocked 0, evidence ≥85%, missing 0–2, orphaned 0–2, duplicates 0
- **AND** operator confidence (pole_id) ≥3, confidence (overall) ≥3, friction ≤3, unknowns 5–20%, access 10–30%
- **AND** mismatch pattern documented with explicit cautions (e.g., "format normalisation required", "voltage sparse but baseline matches", "1–2 worn labels flagged for review")

**Outcome:**
- ⚠️ New Stage 4C implementation task authorized WITH caution handling
- ⚠️ Noel documents specific cautions on decision template (doc 75) and signs CONDITIONAL GO
- ⚠️ Gate auditor reviews cautions and approves; may require implementation to handle cautions (e.g., apply dash normalisation, flag sparse voltage rows, pre-review worn labels)
- ⚠️ Claude Code starts runtime integration with caution-handling requirements documented
- ⚠️ Stage 4C implementation proceeds with documented cautions built into merge logic

---

## Verdict Logic

**NO-GO verdict:** Any quantitative or qualitative blocker triggered

**Blockers (any one triggers NO-GO):**
- pole_id <75%, valid <85%, merge-ready <40%, blocked ≥1, evidence <85%, missing ≥3, orphaned ≥3, duplicates ≥1
- **OR** operator confidence (pole_id) <3, confidence (overall) <3, friction >3, unknowns >20%, access >30%
- **OR** mismatch pattern indicates baseline unsuitable (e.g., field uses different pole_id format system, Trimble baseline wrong, new poles ubiquitous)

**Outcome:**
- ❌ New Stage 4C implementation task NOT authorized
- ❌ Noel documents root cause on decision template (doc 75) and signs NO-GO
- ❌ Gate auditor confirms blocker assessment
- ❌ Stage 4C remains blocked; no implementation task started
- ❌ Root-cause investigation begins: What would fix it? (template change? baseline re-check? capture technique training? different job selection?)
- ❌ Re-pilot planning: Next pilot designed to address identified failure

---

## Verdict Logic

**STOP verdict:** Unrecoverable pilot failure

**STOP triggers (pilot cannot continue):**
- Device crashed / data lost (cannot resume field work)
- Baseline CSV wrong or incomplete (cannot match poles reliably)
- Validator crashes on captured CSV (software bug prevents validation)
- Real data accidentally committed to repo (isolation breach; security risk)
- Field team encountered serious safety incident (justifiable abandonment)

**Outcome:**
- ❌ Halt all field work immediately
- ❌ Contact Codex for emergency investigation
- ❌ Do not proceed to decision template
- ❌ Do not sign any verdict
- ❌ Investigate root cause and plan recovery (data recovery, baseline audit, software fix, security audit, safety review)

---

## Approval Workflow

### Step 1: Noel Completes Field Capture

- 34 poles (full option) or 15 poles (fallback) captured
- All photos organized in evidence folder structure
- CSV complete with required fields

### Step 2: Noel Runs Validator

```bash
python scripts/validate_stage4_pilot.py \
  --csv real_pilot_data/P_CONTROLLED_001/csv/P_CONTROLLED_001.csv \
  --evidence-dir real_pilot_data/P_CONTROLLED_001/photos_final/ \
  --pilot-name P_CONTROLLED_001 \
  --out validation_runs/stage4_pilots/P_CONTROLLED_001_FINAL
```

**Produces:**
- pilot_validation_report.json (row metrics, match rate, evidence audit)
- pilot_validation_report.md (human-readable summary)
- evidence_audit.json (photo linking details)

### Step 3: Noel Assesses Quantitative Metrics

Compare validator output against quantitative criteria table (above):
- Extract: match rate, valid row %, merge-ready %, blocked rows, evidence coverage %
- Check: missing photos, orphaned photos, duplicate pole_ids
- Determine: which quantitative criteria met, which failed

### Step 4: Noel Fills Operator Decision Notes (Doc 82)

Record:
- Friction log (workflow issues encountered)
- Unknown-field log (fields couldn't be filled)
- Access log (inaccessible poles or special negotiations)
- Pole_ID mismatch notes (categories and assessment)
- Operator confidence ratings (1–5 for each aspect)

### Step 5: Noel Assesses Qualitative Criteria

Review operator decision notes and rate:
- Confidence (pole_id accuracy): 1–5
- Confidence (overall data quality): 1–5
- Friction points: count and assess
- Unknown fields: % of rows
- Access issues: % of poles
- Mismatch pattern: understood or concerning?

### Step 6: Noel Chooses Verdict

Compare quantitative + qualitative results against verdict logic (GO / CONDITIONAL GO / NO-GO / STOP):
- **All criteria met?** → GO
- **Most criteria met with cautions?** → CONDITIONAL GO (document cautions)
- **Any blocker triggered?** → NO-GO (document root cause)
- **Unrecoverable failure?** → STOP (halt immediately)

### Step 7: Noel Fills Decision Template (Doc 75)

Fill decision template with:
- Metadata (pilot name, date, poles captured, subset choice)
- Row-level findings (match rate, valid %, merge-ready %, blocked count)
- Evidence findings (coverage %, missing, orphaned, duplicates)
- Operator friction assessment (friction rating 1–5, cautions documented)
- Verdict choice (checkbox for GO / CONDITIONAL GO / NO-GO / STOP)
- Confirmation checklist (6 confirmations; see doc 75 for detail)
- Sign-off: Noel's signature, timestamp, authorizing or blocking Stage 4C

### Step 8: Gate Auditor Reviews

Independent reviewer (not Noel):
- Reads decision template
- Checks validator output
- Reads operator notes
- Confirms: Does verdict match criteria? Are cautions real? Are blockers justified?
- **Approval:** Signs off; verdict accepted
- **Questions:** Requests clarification from Noel before approval
- **Rejection:** Flags discrepancy; asks Noel to re-assess

### Step 9: Verdict Outcome

**If approval:**
- GO or CONDITIONAL GO: Claude Code starts new Stage 4C implementation task
- NO-GO: Investigation planning begins (do not start implementation)

**What happens next:**
- GO → Stage 4C runtime integration authorized; implementation task created
- CONDITIONAL GO → Stage 4C runtime integration authorized WITH caution handling; implementation includes caution code
- NO-GO → Stage 4C remains blocked; analysis phase begins
- STOP → Emergency recovery phase; no implementation scheduled

---

## What This Gate Controls

✅ **Controls:** Authorization for Stage 4C runtime implementation (upload route, merge logic, database integration)

❌ **Does NOT control:** Auto-merge to master, auto-enable in production, Stage 4D approval, bypass review/testing

---

## Critical Reminder

**Noel's signature on the decision template (doc 75) is the formal authorization mechanism for Stage 4C.**

The thresholds above are clear and objective. Your assessment is authoritative. The gate auditor confirms the thresholds were met, not re-decides the verdict.

---

## Reference

- **Doc 73:** Controlled Baseline Pilot Prep (why this pilot matters)
- **Doc 74:** Pole_ID Match Protocol (exact matching rules and thresholds)
- **Doc 75:** Controlled Pilot Decision Template (verdict recording and sign-off)
- **Doc 80:** Controlled Pilot Field Pack (field-day procedure)
- **Doc 82:** Operator Decision Notes (friction, unknowns, confidence)
- **Doc 84:** Field Decision Checklist (per-pole targets and stop conditions)
