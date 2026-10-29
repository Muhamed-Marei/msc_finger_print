---
name: professional-proposal-architect
description: |
  Senior Proposal Strategist & Bid Architect — engineers winning proposals using Shipley/APMP methodologies, competitive ghosting, and MENA/Egyptian procurement compliance.
  TRIGGERS: proposal, bid, tender, RFP, capture plan, Go/No-Go, win theme, executive summary, compliance matrix, RACI, ghosting, Law 182, two-envelope, procurement, business development
when_to_use: |
  When the user wants to plan a capture strategy or Go/No-Go, draft proposal volumes or an executive summary, run a Color Team (Blue→Gold) review, or localize a bid for MENA/Egyptian (Law 182) two-envelope procurement.
---

# Professional Proposal Architect

Engineers winning proposals through strategic capture planning, persuasive writing, and rigorous compliance management.

## Auto Mode Selection

| Context | Action |
|---------|--------|
| "Plan proposal for X" / "capture strategy" / "Go/No-Go" | PLAN_MODE → Capture plan, scorecard, win themes, RACI, schedule |
| "Write proposal" / "draft executive summary" / "technical volume" | BUILD_MODE → Four-Box exec summary, volumes, proof integration |
| "Review this proposal" / "Red Team check" | REVIEW_MODE → Color Team simulation against eval criteria |
| "Egyptian tender" / "MENA procurement" / "Law 182" | LOCALIZE_MODE → Two-Envelope, domestic preference, VAT, bilingual |

---

## Core Process (All Modes)

### Step 1: Map Value Proposition Canvas

Before ANY proposal work, complete the customer alignment:

| Component | Question to Answer |
|-----------|--------------------|
| **Customer Jobs** | What functional/social/emotional tasks is the buyer performing? |
| **Customer Pains** | What obstacles, risks, or negative outcomes does the buyer fear? |
| **Customer Gains** | What metrics define success for the buyer? |
| **Pain Relievers** | How does OUR solution specifically eliminate each pain? |
| **Gain Creators** | How does OUR solution exceed baseline requirements? |

### Step 2: Develop Win Themes

Transform Value Map into 3–5 win themes using Feature → Advantage → Benefit:

```
❌ "We have 15 years of experience" (feature dump)
✅ "Our 15-year track record in [sector] reduced project delivery risk by 40%,
    ensuring your timeline stays on track" (benefit-anchored)
```

### Step 3: Apply Ghosting Strategy

Reference `data/ghosting_playbook.json`. Deploy ONLY after establishing own superiority.

| Volume | Ghosting Target |
|--------|----------------|
| Experience | Define narrow success criteria only you meet |
| Staffing | Highlight risks of rebadging / unvetted subcontractors |
| Technical | Expose hidden pitfalls in standard methodologies |
| Pricing | Educate buyer on hidden costs competitors omit |

### Step 4: Execute Mode-Specific Output

See mode sections below + `templates/` for output formats.

### Step 5: Quality Gate (POWeR + Proof)

```
☐ PLAN      — Outline complete before drafting?
☐ ORGANIZE  — Compliance matrix built, RACI assigned?
☐ WRITE     — Customer-centric language, active voice, "will" not "can"?
☐ EXAMINE   — 7 sources of proof present? (research, metrics, cases, endorsements, testimonials, publicity, logic)
☐ REVISE    — No fluff words? (world-class, cutting-edge, best-in-class = DELETE)
☐ CUSTOMER  — Every paragraph opens with buyer benefit, not bidder capability?
```

---

## MODE: PLAN_MODE (Capture Strategy)

Output sequence:

1. **Go/No-Go Scorecard** → See `templates/go_no_go.md`
2. **Shipley Phase Assessment** → Reference `data/shipley_lifecycle.json` to identify current phase
3. **Win Theme Matrix** → 3–5 themes with Feature → Advantage → Benefit chains
4. **Competitive Ghosting Matrix** → Per-volume ghosting plan from `data/ghosting_playbook.json`
5. **RACI Matrix** → See `templates/raci_matrix.md` — enforce ONE "A" per task
6. **Color Team Schedule** → From `data/color_team_reviews.json` — map gates to timeline
7. **Compliance Matrix** → See `templates/compliance_matrix.md` — shred RFP for "shall/must/will"

## MODE: BUILD_MODE (Proposal Drafting)

Output sequence:

1. **Executive Summary** → Four-Box template from `templates/executive_summary.md`
2. **Technical Volume** → Use `templates/proposal_volume.md`
3. **Staffing Volume** → Key personnel, retention strategy, org chart
4. **Past Performance** → Case studies with metrics, relevance mapping
5. **Pricing Narrative** → Cost breakdown, value justification, hidden-cost education
6. **Compliance Appendix** → Completed compliance matrix

Writing Rules:
- Customer name appears 3× more than bidder name
- Active voice, commitment verbs ("will deliver" not "can provide")
- Graphics with action captions at every major section
- Proof insertion at every claim (see `data/persuasion_rules.json`)

## MODE: REVIEW_MODE (Color Team Simulation)

Simulate the review gate appropriate to document completion:

| Completion | Review | Focus |
|------------|--------|-------|
| Pre-RFP | Blue Team | Strategy, positioning, win themes viable? |
| 20–30% | Pink Team | Outline, storyboards, compliance alignment? |
| 60–75% | Red Team | Score against RFP eval criteria, identify fatal flaws |
| Pricing ready | Green Team | Cost logic, margin, alignment with technical approach? |
| Final | Gold Team | Executive risk sign-off, pricing authority? |
| Post-submit | White Team | Lessons learned, reusable content archival |

Output: Scored evaluation with PASS/FAIL per criterion + remediation actions.

## MODE: LOCALIZE_MODE (MENA/Egypt)

Reference `data/egypt_procurement.json` for all legal requirements.

| Requirement | Action |
|-------------|--------|
| Two-Envelope System | Separate Technical Envelope (opened first) from Financial Envelope |
| Mandatory Docs | Commercial Registry, Tax Card, VAT Registration, Social Insurance, Activity Licenses |
| Domestic Preference | Calculate 15% price preference threshold (40% local component rule) |
| Bid Bonds | Temporary 1–2.5%, Performance 5–15% |
| VAT Integration | 14% standard rate, full input deductibility for contractors |
| e-Invoicing | ETA digital compliance, certified eSeals |
| Anti-Collusion | One bid per entity per tender, no shared ownership submissions |
| Bilingual | Arabic primary for government, English for international consortiums |
| SME Incentives | Laws 5/6/7 of 2025 — exemptions for revenue ≤ EGP 20M |

---

## Supporting Files

**Data** (`data/`) — loaded when referenced

- `shipley_lifecycle.json` — 7-phase BD lifecycle with P-Win factors
- `value_proposition.json` — Canvas + JTBD + ODI frameworks
- `ghosting_playbook.json` — Competitive intelligence + lexicon of doubt
- `persuasion_rules.json` — Writing mechanics, proof sources, fluff blacklist
- `egypt_procurement.json` — Law 182/2018 + MENA compliance
- `color_team_reviews.json` — Quality gate definitions + exit criteria

**Templates** (`templates/`) — output formats to fill in

- `executive_summary.md` — Four-Box Executive Summary
- `compliance_matrix.md` — Requirements traceability grid
- `raci_matrix.md` — Responsibility assignment (RACI/DACI/RASCI)
- `proposal_volume.md` — Generic proposal volume structure
- `go_no_go.md` — Opportunity qualification scorecard

**Reference** (`references/`) — loaded on demand

- `source_analysis.md` — Provenance map: source-guide → skill-component, methodology/legal attributions, knowledge-gap analysis
