<!-- INTERNAL cost build-up. Fill top-to-bottom. Never shown to client. -->
# Cost Worksheet — {{PROJECT_NAME}}

**Service line:** {{e.g. mobile app / 3D explainer / social retainer}}
**Market:** {{egypt_mena | global}}  ·  **Delivery base:** {{Egypt staff | freelance | global}}  ·  **Date:** {{DATE}}
**Complexity:** {{simple | medium | complex}}  ·  **Pricing model:** {{fixed | retainer | hourly | value}}

## 1. Effort estimate (hours by role)
| Role | Hours | Loaded cost/hr | Line cost |
|------|------:|---------------:|----------:|
| {{role}} | {{h}} | {{(salary×1.3)/(173×util)}} | {{=}} |
| … | | | |
| **Direct labor subtotal** | {{Σh}} | | **{{Σ}}** |

> Loaded cost/hr = (monthly salary × **1.3**) ÷ (173 × utilization **0.70** staff / **0.45** solo).

## 2. Overhead + pass-throughs
| Item | Basis | Amount |
|------|-------|-------:|
| Overhead allocation | {{$/hr}} × {{total hrs}} | {{=}} |
| Cloud / hosting | | |
| Licenses / stock / render | | |
| Outsourced (VO, music, subcontract) | | |
| **Subtotal (labor + above)** | | **{{=}}** |

## 3. Contingency → total Cost
| | |
|--|--:|
| Contingency ({{15–25%, default 20}}%) | {{=}} |
| **TOTAL COST** | **{{=}}** |

## 4. Price from target margin
- Target gross margin (from `data/margin_targets.json`): **{{m}}%**
- **Price = Cost ÷ (1 − {{m}})** = **{{PRICE}}**
- Effective margin if sold at a *global* price of {{X}}: {{(X−Cost)/X}}

## 5. Tax / net-cash check (Egypt-touching deals — `data/egypt_tax_2026.json`)
| Friction | Applies? | Effect on cash |
|----------|----------|---------------:|
| VAT 14% (0% if exported service to non-resident) | {{y/n}} | {{add to invoice}} |
| Local WHT (5% prof. / 3% services, on pre-VAT base) | {{y/n}} | {{−}} |
| Cross-border WHT 20% (verify PE/DTT) | {{y/n}} | {{−}} |
| FX slippage (bill in USD?) | {{y/n}} | {{−}} |
| **NET CASH RECEIVED** | | **{{=}}** |

## 6. Sanity check (`data/price_books.json`)
- Market band for {{service}}/{{market}}: **{{band}}**
- Quote vs band: {{inside | above → trim scope/margin | below → re-estimate, under-scoped}}
