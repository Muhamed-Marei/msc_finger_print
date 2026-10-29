# Source Analysis — service-pricing skill

Provenance map, accuracy flags, and known gaps for the pricing knowledge base. Loaded on demand.

## Source documents
| Source | Role | Lives in |
|--------|------|----------|
| `docs/skill_rs/pricing/compass_artifact_…md` | Operational playbook: benchmark price books, complexity bands, worked quotes, margin targets | → `price_books.json`, `role_costs.json` (salary bands), `margin_targets.json`, `tool_costs.json` |
| `docs/skill_rs/pricing/Service Pricing Cost Calculation.md` | Theory + Egypt tax compliance: FBLR, MVR, capacity, margin-vs-markup, 4 pricing models, Egypt 2026 tax | → `role_costs.json` (FBLR), `margin_targets.json` (matrix), `egypt_tax_2026.json`, `pricing_models.json` |

## What this skill fixed vs the raw sources
1. **Restored missing formulas.** The Cost-Calculation doc lost its margin/markup and efficiency-variance formulas in render (bare `[cite: …]` markers). Re-derived and verified in `margin_targets.json`.
2. **Closed the tax-friction gap.** The compass worked quotes stop at `Cost ÷ (1 − margin)` and ignore VAT/WHT. This skill makes the net-cash check a mandatory step (`egypt_tax_2026.json`, worksheet §5).
3. **Reconciled conflicting defaults** into one canonical set: burden ×1.3; utilization 0.70 staff / 0.45 solo; contingency 20%; target margins 45% software / 55% social-video / 65% ads-AI-voice; floor 2.0× FBLR for premium/global.
4. **Tempered the arbitrage optimism.** "Egypt cost → global price = 83% effective margin" is gross; net it against 20% WHT, EOR fees, and FX first.

## Accuracy flags — RESOLVED via verified research report (June 2026)

A targeted research pass (June 2026) confirmed the Egypt tax layer against named laws. Status below; full detail in `egypt_tax_2026.json`.

| Claim | Status (June 2026) |
|-------|--------------------|
| Cross-border WHT = blanket 20% to non-residents | **CONFIRMED — my earlier "overstated" flag was WRONG.** Egypt's utilization sourcing (Law 91/2005) deems any service *consumed* in Egypt as Egyptian-source regardless of PE or where performed. DTT relief exists but is **refund-only** (Decree 771/2009). |
| EGP/USD rate | **CORRECTED to ~52.17** (user-confirmed on-the-ground, 8 Jun 2026). Research report's 47.95 was too strong and rejected; original 51.8 was close. Mild continued slide, not a reversal. |
| Social insurance caps min 2,700 / max 16,700 (2026) | **CONFIRMED** (Law 148/2019). Added: uncapped employee health 1%, employer training-fund 0.25% (Labour Law 14/2025). |
| PIT brackets + 27.5% top; corporate 22.5% | **CONFIRMED** (PIT per Law 7/2024). |
| Local WHT 1/3/5%, EGP 300 floor, pre-VAT base, Form 41 | **CONFIRMED** (Law 91/2005). |
| Dynamics 365 BC ($80/$110/$8) | **CONFIRMED** (Microsoft repricing 1 Nov 2025). |
| All compass worked-quote math | **Recomputed and correct.** |
| FBLR / margin-matrix / social-insurance cap math | **Recomputed and correct.** |

**New material added from the research pass:** 10% schedule tax on pure consulting (restricted input recovery); e-invoicing threshold dropped EGP 500k→250k (Resolution 281/2025); reverse-charge UIN/API validation; **MSME gross-turnover tax** (≤EGP 20M → ~0.75–1.5% of revenue, often beats 22.5% net for low-COGS agencies); KSA/UAE tax (`gcc_expansion.json`).

## Sourcing caveats (carried from compass)
- Bands span 5–10×; planning ranges, not quotes. Drivers: complexity, seniority, location, platform, revisions.
- Egypt salary data is noisy (Glassdoor understated); reconciled vs ERI/Payscale/Paylab — directional.
- Vendor/rate-card blogs anchor high; prefer salary aggregators + platform (Upwork) data. Disregard "90%+ margin" claims (conflate gross/net) in favor of Promethean 11–18% net benchmarks.
- AI cuts coding cost ~10–25% (not 50–80%); revisit cost models quarterly.

## Known gaps (not yet in the skill)
- No automated calculator script — math is done inline. A `scripts/quote.py` could take effort+rates+margin+tax and emit the worksheet.
- GCC coverage is summary-level (KSA/UAE in `gcc_expansion.json`); other MENA jurisdictions (Qatar, Kuwait, etc.) not modeled.
- No historical actuals feedback loop; estimating precision improves only with logged real project margins.
- FX (52.17) and MSME turnover-tax brackets drift — re-confirm quarterly.
