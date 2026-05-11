# Controlled Pilot Operator Decision Notes

**For: Noel's reflection and record after field capture**

**Date:** 2026-05-11
**Purpose:** Post-field notes to inform the decision template verdict
**Authority:** Document 73–75 (Pilot Prep, Match Protocol, Decision Template)
**Scope:** Noel's field observations, friction points, and confidence assessment

---

## How to Use This Document

After field capture is complete and the validator has run:

1. **Fill this document** with observations, friction notes, and confidence assessments
2. **Use this document** to inform your answers on the decision template (doc 75)
3. **Keep this document** as part of the permanent project record
4. **Do not delete** — your notes inform future pilots and decision-gate audit

This is your space to document **what it felt like to execute the pilot**, not just the numbers.

---

## Operator Friction Log

Friction: any workflow issue, confusion, or inefficiency you encountered.

Fill this section as you go through the field day (or immediately after, while fresh):

| What was hard? | How often? | Root cause | Suggestion for next time |
|---|---|---|---|
| _______________ | once / multiple times | _______________ | _______________ |
| _______________ | once / multiple times | _______________ | _______________ |
| _______________ | once / multiple times | _______________ | _______________ |

**Examples of friction to record:**

- **Template clarity:** "The 'evidence_status' field options were not clear — I didn't know if 'proxy' meant distant or angled"
- **Capture ease:** "Determining pole height by eye was harder than expected; took 5 minutes per pole"
- **Evidence organization:** "Moving files into subdirectories was tedious; 30 files took 20 minutes"
- **Baseline matching:** "Pole labels were very worn; had to infer 5 pole IDs from Trimble location alone"
- **Device usability:** "Device screen too small to see template fields clearly in bright sunlight"
- **Safety friction:** "One pole required crossing private property; had to negotiate access"

**What happens with friction notes:**
- If multiple friction points occur, they may warrant template improvements for next pilot
- If only one friction point occurs, it's documented but does not block Stage 4C approval
- Friction notes inform the "operator friction assessment" section of the decision template

---

## Unknown-Field Log

Unknown: any field in the template that you could not confidently fill.

Record the pole and the field that was unclear:

| Pole_ID | Field | What was unclear? | How did you handle it? |
|---|---|---|---|
| _______________ | _______________ | _______________ | left blank / marked verification_required / estimated |
| _______________ | _______________ | _______________ | left blank / marked verification_required / estimated |

**Examples:**

- `P008-001` | `voltage` | "Transformer had no visible nameplate; voltage not marked anywhere" | "Marked verification_required=yes; left voltage blank"
- `P010-005` | `stays_count` | "Vegetation blocked view of pole base; couldn't count stays" | "Marked evidence_status=obscured; estimated 2 stays"
- `P015-003` | `height_m` | "Pole leaning; hard to measure true height" | "Estimated 11m from context; marked verification_required=yes"

**Impact on decision:**
- If >20% of rows have unknown fields, the workflow may need adjustment
- If <5% have unknowns, that's expected field uncertainty and acceptable
- Each unknown is a data quality signal, not a pilot failure

---

## Private Land / Access Log

Access issue: any pole that required special negotiation or was inaccessible.

Record the outcome:

| Pole_ID | Challenge | Resolution | Photos captured? |
|---|---|---|---|
| _______________ | _______________ | _______________ | yes / no |
| _______________ | _______________ | _______________ | yes / no |

**Examples:**

- `P008-015` | "Located in farmer's field; required permission to enter" | "Farmer allowed 10-minute access; captured clear photos" | yes
- `P012-004` | "On steep private driveway; unsafe to approach" | "Photographed from public road; marked evidence_status=obscured" | yes (partial)
- `P009-020` | "Inside fenced compound; no entry allowed" | "Could not capture any photos; marked evidence_status=none" | no

**Impact on decision:**
- Access issues do not automatically fail the pilot
- They are documented as field realities (environmental constraints)
- If >30% of poles are inaccessible, baseline may not be suitable for real work (informs decision)

---

## Pole_ID Mismatch Notes

Mismatch: any pole where the physical label disagreed with the Trimble baseline.

Record each mismatch:

| Trimble baseline | Physical label | Confidence | Root cause assessment | Action taken |
|---|---|---|---|---|
| P008-001 | P008-01 (missing leading zero) | high | Typo by surveyor or Trimble inconsistency | Used Trimble ID; marked verification_required=yes |
| P010-005 | not visible | low | Pole label worn/missing | Inferred from location; marked evidence_status=inferred |
| P015-003 | P015-003 | high | exact match | Used pole label; no verification required |

**Mismatch categories (from doc 74):**

1. **Exact match** — Physical label matches Trimble ID exactly
   - ✅ Confidence: high
   - ✅ Action: proceed normally, no verification required

2. **Format difference** — Same pole, different format (P008-001 vs P008.001 vs P008/001)
   - ⚠️ Confidence: medium-high
   - ⚠️ Action: use Trimble ID; mark verification_required=yes
   - Indicates: possible normalisation issue (to be addressed in future)

3. **Typo by surveyor** — One digit off (P008-1 vs P008-01)
   - ⚠️ Confidence: medium
   - ⚠️ Action: use Trimble ID; mark verification_required=yes
   - Indicates: operator capture technique improvement needed

4. **New pole** — Physical pole exists but not in Trimble baseline
   - ⚠️ Confidence: medium
   - ⚠️ Action: use new pole_id; note "new pole not in baseline"
   - Indicates: baseline incomplete (acceptable; Stage 4 provides missing data)

5. **Trimble missing** — Physical pole has no baseline record (different ID than expected)
   - ⚠️ Confidence: low-medium
   - ❌ Action: cannot match; mark as UNKNOWN or placeholder
   - Indicates: baseline error (requires investigation)

6. **Ambiguous / uncertain** — Cannot determine if physical pole matches baseline
   - ❌ Confidence: low
   - ❌ Action: mark verification_required=yes; document uncertainty exactly
   - Indicates: needs manual review before merge

**Impact on decision:**
- If ≥80% of poles have exact matches → GO condition met
- If 75–80% have exact matches → CONDITIONAL GO (investigate format/typo issues)
- If <75% have exact matches → NO-GO (baseline/capture mismatch must be investigated)

---

## Operator Confidence Notes

Confidence: your overall assessment of data quality by category.

Rate your confidence (1 = very low, 5 = very high) for each aspect:

| Aspect | Rating | Notes |
|---|---|---|
| **pole_id accuracy** | 1 2 3 4 5 | Are pole_ids reliably matched to Trimble baseline? |
| **pole_type identification** | 1 2 3 4 5 | Can you reliably see and identify pole material? |
| **condition assessment** | 1 2 3 4 5 | Can you visually assess pole condition (good/fair/poor)? |
| **voltage/equipment data** | 1 2 3 4 5 | How clear are equipment labels and voltage markings? |
| **evidence linking** | 1 2 3 4 5 | Photos successfully linked to poles? |
| **overall data quality** | 1 2 3 4 5 | Would you trust this dataset for design handoff? |

**Confidence guidance:**

- **5:** Consistently clear and unambiguous; ready to use immediately
- **4:** Mostly clear; minor questions but generally reliable
- **3:** Mixed; some clear, some uncertain; acceptable with review
- **2:** Often unclear; significant gaps; needs improvement before production
- **1:** Unreliable; not suitable for downstream use

**Example filled section:**

| Aspect | Rating | Notes |
|---|---|---|
| **pole_id accuracy** | 4 | 24 out of 30 poles had exact matches. 5 poles had worn labels (inferred from location, marked verification_required). 1 pole was new (not in baseline). Overall solid. |
| **pole_type identification** | 4 | Wooden and concrete poles obvious. 2 lattice poles required closer inspection. Metal details sometimes hard to see in shadows. |
| **condition assessment** | 3 | Obvious defects visible (rot, cracks). Subtle damage (micro-cracks, corrosion) harder to assess without close inspection. Safe to use for basic good/fair/poor classification. |
| **voltage/equipment data** | 2 | Very few transformers had visible nameplates. Most voltage guessed from context (11kV vs 230V). Equipment types mostly visible. Would need closer inspection or nameplate records for certainty. |
| **evidence linking** | 5 | All 30 photos successfully organized and named. 100% reference coverage. No orphans or mismatches. Validator confirmed 0 missing, 0 orphaned. |
| **overall data quality** | 3 | Acceptable for Stage 4C pilot. pole_id matching is solid (≥80%). Voltage and some equipment data would benefit from baseline records or clearer labeling. Photo evidence is clean. |

---

## What Would Make This Pilot GO / CONDITIONAL GO / NO-GO?

Refer to document 75 (decision template) for the formal verdict criteria.

But before looking at numbers, **what's your gut assessment?**

Fill in your thinking:

### Scenario: This pilot is GO if...

**Necessary conditions (all must be true):**
- [ ] pole_id match rate is ≥80% (at least 24 out of 30 poles exact-matched to Trimble)
- [ ] ≥90% of rows are valid (no schema errors, no blank required fields)
- [ ] ≥50% of rows are merge-ready (confident enough for immediate design use)
- [ ] ≤50% of rows are review-required (tolerable review workload)
- [ ] 0 rows are blocked (no show-stoppers)
- [ ] Evidence linking is ≥90% (photos successfully referenced)
- [ ] You personally verified pole_ids and feel confident about matches

**If all above are true:**
- ✅ Recommend GO on decision template
- ✅ GO verdict authorizes Claude Code to start new Stage 4C implementation task
- ✅ New task will implement the runtime upload/merge logic

---

### Scenario: This pilot is CONDITIONAL GO if...

**Conditions (most must be true, with documented cautions):**
- [ ] pole_id match rate is 75–80% (lower but acceptable)
- [ ] ≥85% of rows are valid
- [ ] 40–50% of rows are merge-ready (still acceptable, just more review)
- [ ] 50–60% of rows are review-required (manageable)
- [ ] 0 rows are blocked
- [ ] Evidence linking is ≥85% (minor gaps acceptable)
- [ ] 1–2 friction points are documented but do not block workflow
- [ ] Mismatch issues are understood (e.g., "format differences resolved by normalisation")

**If above are true with documented cautions:**
- ⚠️ Recommend CONDITIONAL GO on decision template
- ⚠️ Document the specific cautions (e.g., "format differences require dash normalisation")
- ⚠️ CONDITIONAL GO also authorizes new Stage 4C implementation task
- ⚠️ Implementation must handle the documented cautions (e.g., apply dash normalisation)

---

### Scenario: This pilot is NO-GO if...

**Blockers (any one of these triggers NO-GO):**
- [ ] pole_id match rate is <75% (too many mismatches; baseline unsuitable)
- [ ] >20% of rows have missing required fields (template or capture technique problem)
- [ ] <40% of rows are merge-ready (insufficient confidence for design use)
- [ ] >60% of rows are review-required (unsustainable review burden)
- [ ] Any rows are BLOCKED (show-stopping issues)
- [ ] Evidence linking is <85% (missing/orphaned photos indicate workflow problem)
- [ ] >3 friction points suggest template or workflow needs redesign
- [ ] Mismatch pattern indicates baseline is unsuitable (e.g., field uses different pole_id format)

**If any blocker is true:**
- ❌ Recommend NO-GO on decision template
- ❌ NO-GO does NOT authorize Stage 4C implementation
- ❌ Instead, root-cause analysis and re-pilot planning begin
- ❌ Specify what would fix it (template change? baseline re-check? capture technique training?)

---

### Scenario: Pilot is STOP if...

**Unrecoverable issue (pilot cannot continue):**
- [ ] Device crashed / data lost (cannot continue field work)
- [ ] Baseline CSV was wrong or incomplete (cannot match poles)
- [ ] Validator crashes on the captured CSV (software bug)
- [ ] Real data accidentally committed to repo (isolation breach)
- [ ] Field team encountered serious safety issue (justifiable abandonment)

**If STOP condition occurs:**
- ❌ Halt all field work immediately
- ❌ Contact Codex for emergency investigation
- ❌ Do not proceed to decision template
- ❌ Investigate root cause and plan recovery

---

## Final Notes Before Decision Template

Before filling the decision template (doc 75), ask yourself:

1. **Did I personally verify pole_ids?**
   - Can you point to specific poles and confirm they match baseline?
   - Or did you rely entirely on Trimble location and infer IDs?

2. **Do I trust the evidence?**
   - Are photos clear enough for an auditor to verify your work?
   - Or are many photos obscured/inferred/estimated?

3. **Would I use this data for real design work?**
   - If a designer asked to use this dataset right now, would you feel confident?
   - Or would you ask them to wait for improvements?

4. **Are the thresholds met?**
   - Validator output: match rate ≥80%? Valid rows ≥90%? Merge-ready ≥50%?
   - Or do you need to investigate further before signing a verdict?

5. **What's the ONE thing that could flip GO to CONDITIONAL GO?**
   - Documenting that one thing in your decision template justifies the caution

---

## Reminder: What GO Means

**If you sign GO on the decision template:**

- ✅ You are confirming pole_id matching is reliable (≥80% exact match)
- ✅ You are confirming electrical attributes are usable for design
- ✅ You are confirming evidence photos are correctly linked
- ✅ You are authorizing Claude Code to build Stage 4C runtime integration

**What GO does NOT do:**

- ❌ Does NOT auto-merge anything to master
- ❌ Does NOT enable Stage 4C in production
- ❌ Does NOT approve Stage 4D (popup surfacing)
- ❌ Does NOT bypass any review or testing

**What happens after GO:**

1. Your signed decision board becomes a formal governance record
2. Claude Code starts a NEW task: "Stage 4C Runtime Integration"
3. That task implements upload route, merge algorithm, database integration
4. That task is subject to SEPARATE tests and reviews
5. Runtime code goes through merge_safety_check before integration

---

## Reference

- **Doc 73:** Controlled Baseline Pilot Prep (why this pilot matters)
- **Doc 74:** Pole_ID Match Protocol (exact matching rules and thresholds)
- **Doc 75:** Controlled Pilot Decision Template (where you sign GO/NO-GO)
- **Doc 80:** Controlled Pilot Field Pack (field-day procedure)
- **Doc 81:** Photo and Evidence Rules (photo requirements)
