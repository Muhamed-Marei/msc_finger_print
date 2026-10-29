# PRD Generator Examples

This file provides example prompts and expected agent behavior.

---

## Example 1: Simple Feature Request

**User Prompt:**
> "Create a PRD for a dark mode feature in our dashboard app."

**Expected Agent Behavior:**
1. Adopt Senior PM persona.
2. Ask clarifying questions if needed (e.g., "What is the primary user persona?").
3. Draft PRD using `prd_template.md`.
4. Output includes:
   - Problem Statement (e.g., eye strain in low-light).
   - Primary Metric: HEART - Happiness (e.g., CSAT improvement).
   - Guardrail: Performance (e.g., no increase in load time).

---

## Example 2: Complex B2B Feature

**User Prompt:**
> "Write requirements for an enterprise reporting dashboard that integrates with Salesforce."

**Expected Agent Behavior:**
1. Identify this as a B2B/Growth scenario.
2. Use AARRR framework (focus on Retention/Revenue).
3. Include:
   - Anti-Persona: "Not for small business users without CRM."
   - NFRs: Security (SOC2), Performance (< 3s report generation).
   - Dependencies: Salesforce API access.
   - Risk Matrix: API rate limiting, data sync failures.

---

## Example 3: PRD Review

**User Prompt:**
> "Review this PRD: [pastes document]"

**Expected Agent Output:**
```
## PRD Review Summary

**Score**: 7/10 checklist items complete.

### ✅ Complete
- Header (Owner, Status, Timeline)
- Problem Statement
- User Stories (Gherkin)
- NFRs

### ❌ Missing
- Anti-Persona not defined.
- Guardrail Metrics missing.
- GTM Checklist incomplete.

### Recommendations
1. Add an Anti-Persona to clarify scope boundaries.
2. Define a Guardrail Metric (e.g., "Error rate must not exceed 0.5%").
3. Complete the GTM checklist (Support FAQs missing).
```
