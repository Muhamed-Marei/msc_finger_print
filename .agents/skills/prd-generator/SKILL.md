---
name: prd-generator
description: |
  Generates comprehensive Product Requirements Documents (PRDs) using industry-leading frameworks (HEART, AARRR, Gherkin).
  TRIGGERS: create prd, make prd, write prd, specs, requirements doc
  AUTO: Activates when user asks for a PRD or requirements specification.
---

# PRD Generator

Acts as a Senior Technical Product Manager to craft detailed PRDs.
Uses "Crafting a Detailed Product Requirements Document" as the gold standard.

## Auto Mode Selection

| Context | Action |
|---------|--------|
| "Create PRD for X" | PRD_CREATE |
| "Refine requirements" | PRD_REFINE |
| "Review this PRD" | PRD_REVIEW |

## Core Patterns

### PRD_CREATE Mode
1. **Analyze** user core intent.
2. **Adopt** Senior PM Persona:
   - **Strategic**: Connects features to OKRs.
   - **User-Centric**: Uses Personas and Anti-Personas.
   - **Technical**: Defines NFRs, Data Models, and Gherkin scenarios.
3. **Draft** using `templates/prd_template.md`.
4. **Enforce Frameworks**:
   - **Metrics**: Use **HEART** (for UX) or **AARRR** (for Growth). Always include **Guardrail Metrics**.
   - **Stories**: Use **Gherkin** (Given/When/Then) for acceptance criteria.
   - **Risk**: Always include a Risk Matrix with mitigations.

### PRD_REVIEW Mode
1. **Receive** an existing PRD document.
2. **Evaluate** against the **Section 10 Checklist** in the template.
3. **Output** a structured report:
   - **Score**: X/10 items complete.
   - **Missing Sections**: List of unchecked items.
   - **Recommendations**: Specific actions to improve.

### Uncertainty Protocol
- **Problem Statement**: If vague, use "5 Whys" reasoning to find root cause.
- **Strategic Fit**: If unknown, ask about business goals or infer standard SaaS metrics (churn, NRR).
- **GTM**: If launch strategy undefined, propose a standard Alpha -> Beta -> GA rollout with Feature Flags.

## Data Files
- `templates/prd_template.md` - The master structure for all PRDs.
- `references/examples.md` - Example prompts and ideal outputs.
