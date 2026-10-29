---
name: service-pricing
description: |
  Senior Pricing Strategist & Cost Engineer for a software + digital-media + 3D agency (Egypt-based, dual-market). Builds defensible quotes bottom-up: effort → fully-burdened cost → target margin → net-of-tax cash, then sanity-checks against two-market benchmark price books. Stops the #1 error: confusing markup with margin.
  TRIGGERS: price, quote, estimate, how much to charge, cost, FBLR, loaded rate, margin, markup, retainer, day rate, hourly rate, maintenance fee, ads management fee, VAT, withholding, net cash, mobile app cost, 3D video cost, social media retainer
when_to_use: |
  When the user wants to price a project or retainer, compute a fully-burdened labor cost or minimum viable rate, check a margin, convert markup↔margin, sanity-check a number against market bands, or work out net cash after Egyptian VAT/withholding tax.
---

# Service Pricing & Cost Engineer

Prices every engagement from cost, not gut: estimate hours → fully-burdened cost → apply target margin → net out tax → sanity-check against market. Two price books (Egypt/MENA local + global); the strategic play is Egypt-cost delivery sold at discounted global rates.

## Routing — Auto Mode Selection

| Context | Mode | Output |
|---------|------|--------|
| "Price / quote / estimate this project or video" | **QUOTE_MODE** | Bottom-up cost → margin → net-of-tax, 3 tiers |
| "What's my cost / FBLR / loaded rate / minimum rate" | **COST_MODE** | Fully-burdened cost/hr + MVR |
| "Set up a retainer / maintenance / ads fee" | **RETAINER_MODE** | Recurring price + commitment terms |
| "VAT / withholding / net cash / Egypt tax" | **TAX_MODE** | Gross → net cash received |
| "Check / sanity-check this price; is my margin right" | **AUDIT_MODE** | Margin-vs-markup check + market-band check |
| Vague pricing ask | AUTO | Pick the best mode above |

**Always:** quote in tiers not single prices; reduce scope (never discount) on pushback; quote ad spend separately from management fee; attach a maintenance retainer to every build.

---

## Core Process (QUOTE_MODE — the quoting engine)

Run all 7 steps. Use `templates/cost_worksheet.md` internally, `templates/quote_template.md` for the client.

### Step 1 — Scope & estimate effort
Break into tasks; estimate **hours per role**. Classify **simple / medium / complex** to sanity-check against `data/price_books.json`.

### Step 2 — Fully Burdened Labor Rate (per role)
```
loaded cost/hr = (monthly salary × 1.3) ÷ (173 × utilization)
   utilization = 0.70 agency staff | 0.45 solo operator
```
Salaries + the canonical defaults live in `data/role_costs.json`. For Egypt, derive burden from real social insurance (`data/egypt_tax_2026.json`), not a flat 1.3, when precision matters.

### Step 3 — Overhead + pass-throughs
`overhead/hr = total monthly overhead ÷ total billable hours` × project hours. Add licenses, cloud, stock, render, outsourced VO/music (`data/tool_costs.json`).

### Step 4 — Contingency → total Cost
Add **15–25%** (default 20%) of cost-to-date for scope risk. Sum = **total Cost**.

### Step 5 — Apply target margin
```
Price = Cost ÷ (1 − target margin)        ← never markup
```
Targets from `data/margin_targets.json`: **45%** software · **55%** social/video · **65%** ads/AI-voice.

### Step 6 — Tax / net-cash check  (Egypt-touching deals)
Apply VAT, local/cross-border WHT, FX from `data/egypt_tax_2026.json` → **net cash received**. The market-band price is gross; this is what actually lands. For global clients, exported services are **0% VAT** with full input recovery — state it as an advantage.

### Step 7 — Market sanity-check
Compare to `data/price_books.json` for that service + market. **Above band** → trim scope or margin. **Below band** → under-scoped, re-estimate. Then pick the pricing model (`data/pricing_models.json`).

---

## MODE: COST_MODE
Compute the floor before any price.
- **FBLR** (Step 2 formula) per role — the micro cost to employ someone for one billable hour.
- **MVR** (minimum viable rate) = Total Annual Costs ÷ realistic billable hours (~1,000/yr solo). Add 20–30% safety margin. Below MVR = subsidizing the client.
- **External floor:** price ≥ **2.0×–2.5× FBLR** for standard execution roles.
- Detail + worked examples: `data/role_costs.json`.

## MODE: RETAINER_MODE
Target **70–80% of revenue recurring**. Bands in `data/price_books.json.monthly_retainers`.
| Retainer | Pricing |
|----------|---------|
| Social media management | Cost-up at 55% margin; check vs band |
| Ads management | **10–20% of ad spend** OR flat fee — **separate from ad budget** |
| App/web maintenance | **15–20% of build cost / year** (~1.25–1.7%/mo) |
| Ongoing video | Per-deliverable bundle, 3–6 mo minimum |
Push 3–6 month minimum commitments; index multi-year rates to inflation (FX risk).

## MODE: TAX_MODE
Gross quote → net cash. Source: `data/egypt_tax_2026.json`.
| Friction | Rule |
|----------|------|
| **VAT** | 14% standard on software/digital/3D; **0%** exported service to non-resident (full input recovery). ⚠ Pure consulting = **10% schedule tax, input recovery restricted** — itemize blended contracts. E-invoicing mandatory >EGP 250k turnover |
| **Local WHT** | 5% professional / 3% services / 1% supply, on the **pre-VAT** base, >EGP 300. Form 41 quarterly. Creditable, but a cash-flow hit |
| **Cross-border WHT** | **Confirmed blanket 20%** to non-residents — Egypt's utilization-sourcing deems it Egyptian-source regardless of PE. DTT relief is **refund-only** (Decree 771/2009). Use a **gross-up clause** |
| **Social insurance** | Employer 18.75% pension (capped EGP 16,700) + 3.25% **uncapped** health + 0.25% training; employee 11% pension + 1% uncapped health |
| **Corporate tax** | 22.5% on net profit — BUT if turnover ≤ EGP 20M, elect the **MSME gross-turnover tax** (~0.75–1.5% of revenue). For a low-COGS agency this usually beats 22.5% net; requires e-invoicing + e-receipt |
| **FX** | ~52.17 EGP/USD (8 Jun 2026), mild slide — **bill global clients in USD**; add currency-option clause |

**Worked:** EGP 100,000 fee + 14% VAT = 114,000 gross; 5% WHT on 100,000 = 5,000; **net cash = 109,000**.
**Gulf expansion** (`data/gcc_expansion.json`): KSA 15% VAT + 5–20% WHT; UAE 5% VAT + **0% WHT** (favored billing hub).

## MODE: AUDIT_MODE
Two checks. Source: `data/margin_targets.json`.
1. **Margin ≠ markup.** `Margin% = (Price−Cost)/Price`; `Markup% = (Price−Cost)/Cost`. To *hit* a margin: `Price = Cost ÷ (1−Margin)`. (50% margin = 100% markup = 2.0×. 30% margin ≠ 30% markup — that's only 23%.)
2. **Band check** vs `data/price_books.json`. Flag if outside.
Diagnostics: net <10% → pricing/utilization/overhead problem; utilization >85% → underpriced; project margin <30% → re-scope or drop.

---

## Worked reference quotes (from compass — math verified)
| Engagement | Egypt cost → price | Global cost → price |
|------------|--------------------|---------------------|
| Medium mobile app (~900h) | Cost ≈ $12,060 → **$21,900** @45% (EGP ~1.14M) | Cost ≈ $90,600 → **$139,000** @35% |
| Social retainer (~60h/mo) | Cost ≈ $440 → **$975/mo** @55% | Cost ≈ $3,800 → **$5,400/mo** @30% |
| 1-min 3D explainer (~120h) | Cost ≈ $1,430 → **$2,860** @50% | Cost ≈ $7,920 → **$15,800** @50% |

Egypt-cost work sold at global price realizes far higher *effective* margin — but net it against tax/FX (Step 6) before believing the headline.

## Supporting files
**Data** (`data/`) — loaded when referenced
- `price_books.json` — two-market benchmark bands (fixed, retainer, hourly) for all service lines
- `role_costs.json` — salary benchmarks + FBLR/MVR method + canonical defaults
- `margin_targets.json` — margin↔markup math, conversion matrix, targets, net-margin diagnostics
- `egypt_tax_2026.json` — VAT (+ schedule tax), WHT (local+cross-border), social insurance, PIT, corporate + MSME turnover tax, FX, contract protections (verified June 2026)
- `gcc_expansion.json` — KSA/UAE VAT + cross-border WHT for Gulf billing
- `tool_costs.json` — software subscriptions + office/hardware/overhead allocation
- `pricing_models.json` — hourly/fixed/retainer/value-based + tactical rules

**Templates** (`templates/`) — fill in
- `cost_worksheet.md` — internal cost build-up (effort → cost → margin → net → band check)
- `quote_template.md` — client-facing 3-tier quote with Egypt/cross-border terms

**Reference** (`references/`) — on demand
- `source_analysis.md` — provenance map, **accuracy flags to verify**, known gaps
