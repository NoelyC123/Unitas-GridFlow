# Stage 4C → Stage 6 Integration Roadmap

**Date:** 2026-05-17
**Status:** Stage 4C authorized — Phase 4 CONDITIONAL GO on P_LOCAL_002
**Reference:** `AI_CONTROL/30_STAGE4C_IMPLEMENTATION_PLAN.md`,
`AI_CONTROL/98_PHASE_4_VERDICT.md`

---

## Current State (Post-Phase 4)

| Capability | Status |
|---|---|
| Stage 1/2 QA pipeline (Trimble GNSS → QA report) | ✅ Working |
| Survey validation and evidence organisation | ✅ Working |
| Baseline-field matching (Stage 4C) | ✅ Working |
| Stage 6A–6E ENWL evidence integration | ✅ Working (P_LOCAL_002 proven) |
| Design-readiness with conductor spec | ❌ Blocked (no span-confirmed conductor yet) |
| Mobile field capture | ❌ Not built |
| Multi-DNO format support | ⚠️ ENWL proven; SPEN/NIE untested |
| Production deployment | ❌ Not yet |

---

## Stage 4C: Survey-to-Design Validation Hardening (Current)

**Timeline:** Weeks
**Goal:** Harden the baseline-field matching pipeline against P_LOCAL_002 and prove
repeatability on at least one additional job

### Milestone Status

| Milestone | Task | Status |
|---|---|---|
| M1 | Pipeline validation run on P_LOCAL_002 | ⏳ Ready to start |
| M2 | `baseline_coordinate_missing` flag in QA report | ⏳ After M1 |
| M3 | Pole 06 conflict auto-detection confirmed | ⏳ After M1 |
| M4 | Coordinate closure (Noel action — ENWL NAV lookup) | ⏳ Noel action |
| M5 | Full M1 acceptance check with all criteria met | ⏳ After M2–M4 |

### Stage 4C Outputs
- Full pipeline run on P_LOCAL_002 with all 10 reports
- All five known Phase 4 issues surfaced automatically in QA output
- P_LOCAL_003 repeatability validation (after M5)
- Stage 4C declared complete

---

## Stage 5: Field Capture Integration (Future)

**Timeline:** Months
**Goal:** Mobile or tablet-assisted field capture replacing paper notes and ad-hoc photos

### What This Adds
- Structured digital entry during field survey (pole type, stay, condition, attachments)
- GPS coordinate capture tied to pole record
- Photo organisation automation (sort by pole, tag by category)
- Offline sync capability (field work is rarely on-network)
- Field note templates matching the `FieldPole` model structure

### Platform Decision Required
The biggest pre-Stage 5 decision is platform choice. Options:
- **iOS native** — best photo integration, Trimble-friendly, requires Swift/Obj-C
- **Android native** — broader device choice for field teams
- **Progressive Web App (PWA)** — cross-platform, no app store, limited camera/GPS control
- **React Native / Flutter** — cross-platform native-adjacent

This decision affects the entire Stage 5 build. It should not be made until there is a
committed early customer or field team willing to trial the tool.

### Dependencies
- Stage 4C complete and proven on ≥ 2 jobs
- P_LOCAL_003 validation complete
- At least one real field team committed to trialling the tool
- Platform decision made

### Risk Assessment
- **HIGH** — Mobile dev is a different skill set from the current backend/Python codebase
- **HIGH** — Offline sync reliability is hard; field conditions are unpredictable
- **MEDIUM** — App store distribution adds maintenance burden (review cycles, OS updates)
- **MEDIUM** — Platform lock-in; wrong choice is expensive to reverse

---

## Stage 6: DNO Integration (Future)

**Note:** This is the project's internal Stage 6 (ENWL evidence integration) as tracked in
`AI_CONTROL/121` onwards — not to be confused with the briefing material's use of
"Stage 6" for commercial packaging. The internal Stage 6A–6E is already largely complete
on P_LOCAL_002.

### What Remains in Stage 6 (Internal)

| Sub-stage | Description | Status |
|---|---|---|
| 6A–6E | ENWL evidence classification, combining, linking, conflict, readiness | ✅ Implemented |
| 6D Pole 06 rule | Structural conflict auto-detection for ENWL vs field mismatch | ⚠️ TBD |
| 6E span-confirmed conductor | Prove conductor FID-to-span-to-pole chain | ❌ Not yet |
| Multi-DNO formats | SPEN, SSEN, NIE record formats | ❌ Not yet |
| Stage 6 reports | ENWL evidence export, workspace display | ✅ Implemented |

### What a Broader "DNO Integration" Stage Would Add
- SPEN baseline CSV format support
- NIE baseline format (Irish Grid coordinates)
- DNO-specific rulepack extensions for each operator
- Export formats acceptable to DNO design teams
- Possibly: DNO API integration (longer term — needs DNO partnership)

### Dependencies
- Stage 4C complete
- At least one non-ENWL DNO baseline sample obtained
- DNO partnership or data access agreement for live testing

### Risk Assessment
- **HIGH** — DNO data access is politically complex; procurement cycles are long
- **HIGH** — Each DNO has different record formats; generalisation is expensive
- **MEDIUM** — Conductor-to-span linking requires DNO engineering records not currently available

---

## Critical Decision Points

### Decision 1: After Stage 4C M1

**Question:** Continue hardening (M2–M5), or pause for P_LOCAL_003 capture first?

**Recommended answer:** Continue to M5. P_LOCAL_003 capture can run in parallel with M2–M4
(which are short tasks), but M5 acceptance check should use current P_LOCAL_002 evidence.
P_LOCAL_003 then immediately follows M5 as repeatability validation.

---

### Decision 2: After Stage 4C Complete

**Question:** Build Stage 5 (mobile field capture) or expand Stage 6 (DNO formats)?

**Framework for deciding:**
- If a real survey contractor or field team is willing to trial the tool → Stage 5
- If a second DNO (SPEN/NIE) project is imminent → Stage 6 DNO formats
- If neither → use GridFlow internally on Unitas projects while gathering evidence

**Recommended answer:** Do not decide until Stage 4C is proven on ≥ 2 jobs and
at least one practising UK OHL designer has reviewed the output (see
`AI_CONTROL/02_CURRENT_TASK.md` — designer review is the current active priority).

---

### Decision 3: Commercial Viability

**Question:** Internal tool, consultancy offering, or product/SaaS?

See `AI_CONTROL/38_COMMERCIAL_VIABILITY_ASSESSMENT.md` for full analysis.

**Short answer:** Prove internal value first. Offer as a consultancy service to test
willingness to pay. Do not invest in a SaaS product before demand is proven by at least
3–5 paying customers or signed pilots.

---

## Resource Requirements

| Stage | Time estimate | Key skills needed | External dependencies |
|---|---|---|---|
| Stage 4C completion | 2–4 weeks | Python, validation logic | None |
| P_LOCAL_003 validation | 1–2 days (capture) + 1 week (pipeline) | Field survey + Python | Access to second site |
| Stage 5 mobile | 3–6 months | Mobile dev (iOS/Android/PWA) | App store, test devices, field team |
| Stage 6 DNO formats | 2–4 months | Python, CSV/API formats | DNO baseline sample data |
| Stage 6 DNO API | 6–12 months | API integration | DNO partnership + data access |

---

## Recommended Path

**Immediate (now — weeks):**
1. Complete Stage 4C M1
2. Validate findings from M1
3. Run M2–M4 (short tasks; can run in parallel)
4. Complete M5 acceptance check
5. Capture P_LOCAL_003 to prove repeatability

**Short-term (weeks — months):**
1. Designer review on P_LOCAL_001/P_LOCAL_002 output (`AI_CONTROL/02_CURRENT_TASK.md`)
2. Use GridFlow on next real Unitas project
3. Assess designer feedback — does it prompt a Stage 5 or Stage 6 decision?

**Medium-term (months):**
1. Choose Stage 5 or Stage 6 DNO based on actual project pipeline, not speculation
2. Do not build both simultaneously
3. Validate commercial interest before major build investment

**Long-term (year+):**
1. Complete chosen stage
2. Validate with real users on real projects
3. Then build remaining stage
