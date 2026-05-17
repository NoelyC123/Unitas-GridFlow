# GridFlow Commercial Viability Assessment

**Date:** 2026-05-17
**Basis:** P_LOCAL_001 and P_LOCAL_002 validation results;
direct OHL survey and design experience

---

## What GridFlow Has Proven

### Technical Validation

| Capability | Evidence |
|---|---|
| Field capture methodology works | P_LOCAL_001 (10 poles), P_LOCAL_002 (12 poles) |
| Baseline matching works | 100% structural match on both jobs |
| Conflict detection works | Pole 06 structural mismatch found (ENWL Stub Pole vs field H-pole) |
| Conservative data handling works | 2 coordinate gaps documented honestly; not fabricated |
| Evidence organisation scales | 12-pole job audits cleanly; automation works |
| ENWL evidence integration works | Stage 6A–6E proven on P_LOCAL_002 |
| Multi-AI workflow efficient | Phase 4 completed in 1 working day with parallel tasks |

### Operational Validation

| Capability | Evidence |
|---|---|
| Real survey data handled | ENWL Network Asset Viewer + Trimble GNSS controller data |
| Workflow documentation comprehensive | AI_CONTROL layer, evidence audits, validation reports |
| Quality gates functional | Two-layer validation (structural + content) proven |
| Conservative output | design_ready = False for all poles — correct, not a failure |

---

## What GridFlow Hasn't Proven

### Technical Gaps

| Gap | Why It Matters |
|---|---|
| Scale (only 12 poles) | Real OHL routes are 30–200+ poles |
| Multiple DNOs (ENWL only) | SPEN, SSEN, NIE have different record formats |
| Production reliability | Only validation runs, no live operational use |
| Performance at scale | Runtime untested at 50+ poles |
| Mobile field capture | Currently manual photo organisation |
| Span-confirmed conductor | No conductor FID-to-span linkage proven yet |

### Operational Gaps

| Gap | Why It Matters |
|---|---|
| Real designer usage | No practising OHL designer has used the output in anger |
| Real surveyor team usage | Noel only; not yet tested with a field team |
| Multi-job workflows | Pipeline proven on single jobs, not batch/project workflows |
| Customer willingness to pay | No pricing tested; no paid pilots |

---

## Market Analysis

### Customer Segment 1: DNOs (Distribution Network Operators)

**Organisations:** ENWL, SPEN, SSEN, NIE, UK Power Networks, Western Power

| Factor | Assessment |
|---|---|
| Pain | Survey QA overhead, design rework from poor handoffs |
| Budget | HIGH — capital project budgets are millions; tools budget is thousands |
| Sales cycle | VERY LONG — 18–24 months minimum; procurement/legal/IT approval required |
| Risk | HIGH — complex procurement, internal politics, competing internal tools |
| Technical match | Good — GridFlow speaks DNO data formats |

**Realistic path:** Only viable as a later-stage product with multiple proven pilots
behind it. Not a first customer. Do not target DNOs until product is proven elsewhere.

---

### Customer Segment 2: Survey Contractors

**Organisations:** Subcontractors doing DNO overhead line survey work

| Factor | Assessment |
|---|---|
| Pain | QA rejections from DNOs, rework costs, data quality disputes |
| Budget | MEDIUM — tight margins; will pay £5–30K if proven ROI |
| Sales cycle | MEDIUM — 2–4 months; decisions made by operations directors |
| Risk | MEDIUM — competitive, price-sensitive, may expect DNO to fund |
| Technical match | Strong — they produce exactly the data GridFlow consumes |

**Realistic path:** Good early commercial target. Survey contractors lose money on
QA rejections; GridFlow's pre-CAD QA gate directly protects that margin.

---

### Customer Segment 3: Design Consultancies

**Organisations:** Firms doing OHL design work for DNOs (AECOM, WSP, Jacobs, independents)

| Factor | Assessment |
|---|---|
| Pain | Unclear survey data, repeated clarification requests, design rework |
| Budget | LOW to MEDIUM — professional fees-based; tool budget £2–15K |
| Sales cycle | SHORT — 1–2 months; decision made by project director |
| Risk | LOW — small firms move quickly; GridFlow improves their delivery |
| Technical match | Strong — designers are the primary users of GridFlow output |

**Realistic path:** Best first commercial target. Short sales cycle, direct value
proposition, low risk. Designer feedback is the current priority because this segment
is where the tool's value is most immediately felt.

---

## Pricing Models

### Option 1: Per-Job Licensing

**Price range:** £500–2,000 per survey job processed

- Pros: Low barrier to entry; customers pay only when they use it; aligns cost with value
- Cons: Revenue unpredictable; requires volume to be meaningful; needs billing infrastructure
- Best for: Survey contractors trialling the tool before committing to annual subscription

---

### Option 2: Annual Subscription

**Price range:** £10,000–50,000 per organisation per year

- Pros: Predictable recurring revenue; justifies product investment
- Cons: Requires proven value before customers commit; harder to land without track record
- Best for: Design consultancies or survey firms with regular OHL project flow

---

### Option 3: Consultancy Service

**Model:** Noel runs GridFlow as a managed QA service, charged by day or project

- Pros: Immediate revenue; no product support burden; high perceived quality
- Cons: Time-limited (scales only with Noel's availability); not a business, it is a job
- Best for: Phase 1 validation — prove willingness to pay before investing in a product

---

## Competitive Landscape

| Tool | Category | Gap GridFlow fills |
|---|---|---|
| Esri Field Maps / ArcGIS | General GIS field data collection | Not OHL-specific; no DNO evidence model |
| PoleCAD | OHL design tool | Downstream — GridFlow is the pre-CAD gate before PoleCAD |
| Excel + manual QA | Current state of the market | GridFlow replaces the manual spreadsheet-based QA process |
| DNO internal tools | Varies per DNO | Internal scope only; not available to contractors or consultancies |

**GridFlow's specific differentiation:** The pre-CAD QA gate. GridFlow sits in the gap
between field survey completion and design start — a step that currently happens manually
(or not at all) in most OHL workflows. Other tools are either pure data capture (before
GridFlow's territory) or pure design (after it).

---

## Viability Assessment

### Internal Tool (Current Phase)

**Viability: HIGH ✅**

- Use GridFlow on Unitas OHL projects immediately
- No sales, no support burden, no pricing pressure
- Every real project use builds evidence for later commercial conversations
- Immediate ROI: saves survey QA rework time on own projects
- **Investment required: time only**

---

### Consultancy Offering (Next Phase)

**Viability: MEDIUM ⚠️**

- Sell Noel's time running GridFlow as a managed QA service
- Direct path to first revenue without product investment
- Validates willingness to pay before committing to a product build
- Revenue is time-bounded (scales with capacity, not usage)
- Requires: 1–2 customers, proven designer feedback, word of mouth
- **Investment required: sales time, customer acquisition**

---

### Product / SaaS (Later Phase)

**Viability: LOW to MEDIUM ⚠️**

- Requires significant Stage 5/6 development (months, significant cost)
- No customer validation yet (no paying pilots, no confirmed demand)
- Long DNO sales cycles are incompatible with typical SaaS economics
- Survey contractor segment is more viable but price-sensitive
- Design consultancy segment is too small for a standalone SaaS
- **Do not invest in a product build before demand is demonstrated by paying customers**

---

## Phased Recommendation

### Phase 1: Internal Tool Validation (Now — 6 months)

- Use GridFlow on every applicable Unitas OHL project
- Measure time saved on survey QA and design prep
- Document concrete case studies with real data
- Show output to 2–3 practising OHL designers (the current active task)
- **Decision gate:** Do designers find the output useful enough to pay for it?

---

### Phase 2: Consultancy Demand Test (6–12 months)

- Offer GridFlow QA as a managed service on 1–2 external projects
- Charge £500–2,000 per job or day rate for QA service delivery
- Validate: Do customers pay? Do they return? Do they recommend it?
- Target: Design consultancies and survey contractors, not DNOs
- **Decision gate:** Do 3–5 external organisations pay for the service?

---

### Phase 3: Product Decision (12+ months)

- If Phase 2 proves demand → invest in product (Stage 5 or 6 depending on feedback)
- If Phase 2 does not prove demand → remain consultancy/internal tool
- Do not build a SaaS product before paying customers are confirmed
- **Investment scale:** Determined by Phase 2 evidence

---

## Critical Success Factors

The following must be proven before any significant product investment:

1. A practising UK OHL designer would use the output directly (not just find it interesting)
2. At least one customer has paid for the service (not just said it looks useful)
3. The tool saves more time than it costs to run on a real project
4. The pipeline runs reliably on at least 3 different jobs without manual intervention
5. At least one non-ENWL DNO format is handled (SPEN or NIE)

---

## What to Avoid

- Building a product before validating willingness to pay
- Targeting DNOs as first customers (sales cycle too long)
- Building Stage 5 (mobile) before any field team has trialled it
- Competing directly with Esri on GIS functionality
- Over-engineering before the core value proposition is commercially validated
