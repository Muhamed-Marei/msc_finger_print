# Product Requirements Document: [Product/Feature Name]

| Metadata | Details |
|----------|---------|
| **Status** | [Draft / In Review / Approved / Deprecated] |
| **Owner** | [PM Name], [Eng Name], [Design Name] |
| **Date** | [YYYY-MM-DD] |
| **Target Release** | [e.g. Q3 2025] |
| **Last Updated** | [YYYY-MM-DD] |
| **Related Links** | [Jira Epic], [Figma], [Strategy Doc] |

## 1. Strategic Fit & Problem Statement
### 1.1 Problem Statement
*Avoid solutioneering. Define the gap between current reality and desired state.*
> **Context**: [Who is experiencing pain?]
> **Pain**: [What is the specific issue?]
> **Impact**: [Quantifiable business/user impact, e.g. "15% drop in session duration"]

### 1.2 "5 Whys" Root Cause Analysis
1. Why?
2. Why?
3. Why?
4. Why?
5. **Root Cause**: [The fundamental issue]

### 1.3 Strategic Alignment (OKRs)
*Why this, why now? Link to company objectives.*
- **Objective**: [e.g. Increase Net Revenue Retention]
- **Key Result**: [e.g. Reduce churn by 5%]
- **Contribution**: [How this feature helps achieve the KR]

## 2. Target Audience
- **Primary Persona**: [The core user, e.g. "Marketing Manager"]
- **Secondary Persona**: [e.g. "CMO"]
- **Anti-Persona**: [Who this is NOT for, e.g. "Power Users requesting SQL access"]

## 3. Success Metrics
*Choose the relevant framework.*

### 3.1 Primary Metrics (HEART or AARRR)
| Metric | Category | Definition | Goal |
|--------|----------|------------|------|
| [e.g. NPS] | Happiness | User satisfaction score | > 50 |
| [e.g. DAU] | Engagement | Daily Active Users | +10% |

### 3.2 Guardrail Metrics (Counter-Metrics)
*What must NOT degrade?*
- **Metric**: [e.g. Search Latency]
- **Constraint**: [e.g. Must remain < 200ms]

## 4. Functional Requirements
### 4.1 User Stories & Acceptance Criteria
*Use Gherkin Syntax (Given-When-Then) for clarity.*

#### Story 1: [Short Title]
> **As a** [Persona], **I want to** [Action], **so that** [Benefit].

**Acceptance Criteria (BDD):**
- **Scenario**: [Happy Path]
  - **Given** [Precondition]
  - **When** [Action]
  - **Then** [Result]

- **Scenario**: [Sad Path / Edge Case]
  - **Given** [Precondition]
  - **When** [Error condition]
  - **Then** [Graceful failure message]

## 5. Non-Functional Requirements (NFRs)
*The "Hidden Architecture"*

| Category | Requirement | Success Criteria |
|----------|-------------|------------------|
| **Performance** | Latency / Throughput | e.g. < 2s load time (P95) |
| **Security** | Auth / Data Protection | e.g. Encrypt PII, GDPR compliance |
| **Reliability** | Availability / Recovery | e.g. 99.9% uptime |
| **Scalability** | Load handling | e.g. Support 10k concurrent users |

## 6. UI/UX & Interaction
- **User Flows**: [Link to flowchart or describe logic]
- **State Logic**: [e.g. Placed -> Processing -> Shipped]
- **Microcopy**: [Specific error messages, e.g. "We couldn't find that page."]

## 7. Data Strategy
### 7.1 Analytics (Instrumentation)
- **Event**: [e.g. `checkout_initiated`]
- **Properties**: `cart_value` (Float), `item_count` (Int)
- **Trigger**: [Exact moment of firing]

### 7.2 Conceptual Data Model
| Field | Type | Required? | Description |
|-------|------|-----------|-------------|
| `user_id` | String | Yes | Unique Customer ID |
| `status` | Enum | Yes | [Active, Inactive] |

## 8. Release & GTM Strategy
### 8.1 Rollout Plan
- [ ] **Alpha**: Internal employees
- [ ] **Private Beta**: Trusted customers
- [ ] **Public Beta**: [x]% traffic
- [ ] **Feature Flag**: [Flag Name]

### 8.2 GTM Checklist
- [ ] **Marketing**: Blog post, Social
- [ ] **Sales**: Battle cards, Pricing update
- [ ] **Support**: FAQs, Help Center

## 9. Risks & Dependencies
### 9.1 Risk Matrix
| Risk | Prob | Impact | Mitigation |
|------|------|--------|------------|
| [Risk Name] | High | High | [Mitigation Strategy] |

### 9.2 Dependencies
- **Internal**: [Team/API dependency]
- **External**: [3rd party vendor/approval]

---

## 10. PRD Approval Checklist
*Before moving to "Approved" status, verify all items.*

- [ ] **Header**: Owner, status, and timeline are clear.
- [ ] **Context**: Problem Statement uses "5 Whys". Strategic Fit is defined.
- [ ] **User**: Primary and Anti-Personas are defined.
- [ ] **UX**: Wireframes/flows linked. "Sad Paths" defined.
- [ ] **Functional**: User Stories use Gherkin format.
- [ ] **Technical**: Data Model defined. NFRs (Security/Performance) are specific.
- [ ] **Metrics**: Success Metrics (HEART/AARRR) and Guardrail Metrics defined.
- [ ] **Plan**: Rollout Strategy (Alpha/Beta/GA) is clear. Feature Flags specified.
- [ ] **Risk**: Assumptions and Risks (with mitigations) listed.
- [ ] **GTM**: Marketing, Sales, and Support deliverables listed.
