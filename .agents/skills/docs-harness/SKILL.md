---
name: docs-harness
description: |
  Structure and maintain a project's documentation so the work survives context resets, handovers, and months of drift. Phases own feature slices; business requirements, architecture, and brand each get their own layer; task ledgers are dependency-ordered; every document exists in Arabic and English with sync machine-verified.
  TRIGGERS: organize docs, documentation structure, docs folder, project documentation, doc harness, AGENTS.md, CLAUDE.md, PRD, SRS, phase plan, implementation plan, task file, ADR, decision record, brand docs, design tokens, doc drift, retrofit docs, بنية التوثيق, توثيق المشروع
  AUTO: user asks how to structure or organize project documentation, starts a new project, opens a phase, adds a feature, reports docs drifting from code, or asks where a document belongs.
---

# Docs Harness

Documentation is the only memory a project keeps. Chat history dies, agents reset, people leave — the repository stays. This skill builds that memory and keeps it honest.

## Mode selection

| The user… | Mode | Do |
|---|---|---|
| starts a project / "set up docs" | `INIT` | Ask the 5 questions, then scaffold |
| opens a new phase | `ADD_PHASE` | New phase folder + ROADMAP row |
| adds or revisits a feature | `ADD_FEATURE` | Feature slice inside the active phase + index row |
| settles a non-obvious choice | `ADD_ADR` | Next numbered ADR, rejected alternatives included |
| has an existing undocumented repo | `RETROFIT` | `references/retrofit.md` — never freeze the project |
| asks "is this still accurate" | `VALIDATE` | Run `validate.py`, report, fix the source not the symptom |
| asks where a document goes | `ROUTE` | Answer from the tree below in one line |

## The tree

```
docs/
├── AGENTS.md                 Hop 0. The only always-loaded file. ≤1500 tokens.
├── 00-product/               prd · srs · personas · glossary(AR/EN)
├── 01-architecture/          architecture · rules · data-model · decisions/
├── 02-brand/                 identity · design-tokens · ui-patterns · assets/
├── 03-phases/
│   ├── ROADMAP.md            phase index, one active at a time
│   └── phase-NN-slug/
│       ├── plan.md           goal, scope, exit criteria, risks
│       ├── tasks.md          THE ledger. One write-target per phase.
│       └── features/<slug>/  spec.md (what) · implementation.md (how)
├── 04-operations/            runbook · environments · release-log
└── _meta/                    features-index · file-registry.json · translation-status
```

**Why phases own features.** A phase is when; a feature is what. Phase 2 hardening the auth
from phase 1 is a folder inside phase 2 carrying the same feature code `AUTH`. Chronology
lives in the path, continuity in `_meta/features-index.md`. Neither is reconstructed later.

## Routing — the two-hop rule

Hop 0 is `AGENTS.md`: commands, repo map, routing table, protocol. Hop 1 is the routed
document. Hop 2 is a leaf (one ADR, one feature spec) pulled only when the task needs it.

A line belongs in `AGENTS.md` only if **every** session needs it. Test: *would removing this
sentence make a future session pick the wrong file, command, or boundary?* If no, it is a
linked file. A router that grows past ~1500 tokens stops routing — its load-bearing lines
get lost in the middle of the context, and the cost of every session rises with it.

## Task ledgers

One ledger per phase — `03-phases/phase-NN-*/tasks.md`. Never a second write-target; two
agents editing one markdown ledger lose each other's updates.

```
- [ ] T-02.CART.03 Cart totals service / خدمة إجماليات السلة  <!-- deps: T-02.CART.02 | req: REQ-014 -->
```

| Element | Rule |
|---|---|
| Id `T-PP.FEAT.NN` | Assigned once. Never renumbered, never reused. |
| `[ ] [/] [x] [!] [~]` | todo · in progress · done · blocked · partial |
| `deps:` | A task MUST NOT start until every dep is `[x]`. Enforced by `validate.py`. |
| `[!]` / `[~]` | MUST carry the reason, and whether a human is required. |
| Task size | One vertical slice — data → logic → interface → test — in one session. Two entities, or auth AND money AND schema together, means split it. |

## Bilingual protocol

Every document exists in both languages, by one of two mechanisms:

- **Mirror** — `prd.md` + `prd.ar.md`. Narrative documents. The Arabic file's frontmatter
  carries `source_sha`: the SHA-256 of the English body it was translated from.
- **Inline** — one file carrying both, e.g. `glossary.md`, `tasks.md`, `ROADMAP.md`. Used
  wherever the file is written back constantly or is a lookup table. A mirror of an
  execution ledger is stale within minutes; a bilingual task line never is.

`validate.py` recomputes the hash and fails on `STALE`, `MISSING`, or `NO-HASH`. Coverage
that is not verified is coverage that has already drifted. Arabic is written, not
translated — a literal rendering of English reads as machine output, and terms come from
`00-product/glossary.md`, which is the naming authority for code, UI, and client documents.

## Authoring rules

- **RFC 2119 or it is not a rule.** "MUST NOT contain business logic" is checkable.
  "We prefer thin resolvers" is narrative a model trades away under pressure.
- **Every load-bearing rule names its enforcer.** A rule with no fitness function, linter,
  or test behind it will be violated and nobody will notice. Documentation explains
  boundaries; only executable checks defend them.
- **Describe reality.** `architecture.md` states what is true. Existing violations go in
  its quarantined-debt table with a retire-by date, not into a fiction of what should be.
- **Anti-features earn their section.** The out-of-scope list in `prd.md` prevents more
  wasted work than the in-scope list creates.
- **ADRs are append-only** and always carry the rejected alternatives. That table is what
  stops the same debate reopening every session.

## Guardrails

- An agent MUST NOT edit `architecture.md`, `rules.md`, or anything under `decisions/`.
  The failure mode is specific and common: an agent hits a constraint, loosens the document
  instead of fixing the code, and reports success.
- When code and docs disagree, **the code is wrong by default.** Work the contradiction
  procedure in `rules.md`; never let the session that wrote the violating code reconcile
  the document.
- No secret values under `docs/` — names only, in `environments.md`. `validate.py` scans.
- Human sign-off, always: auth, migrations, security rules, public contracts, money,
  dependency additions.

## Commands

If `scripts/` is not present alongside this file, the skill is installed standalone: build
the tree by hand in exactly the shape above. Everything below is an accelerant, not a
dependency — the spec, not the script, is what makes the harness work.

```bash
python scripts/scaffold.py init --root docs --project "Name" --stack <profile> \
       --phase 01:foundation:Foundation
python scripts/scaffold.py add-phase   --root docs --num 02 --slug commerce --title "Commerce"
python scripts/scaffold.py add-feature --root docs --phase 02 --code CART --title "Shopping Cart"
python scripts/scaffold.py add-adr     --root docs --title "Postgres owns orders"
python docs/_meta/validate.py docs [--strict]
```

`init` copies `validate.py` into `docs/_meta/` so the project validates without this skill.
Stack profiles (`data/stack-profiles.json`): `flutter-riverpod`, `nextjs-app-router`,
`nestjs-graphql`, `firebase`, `node-clean-architecture`, `laravel`, `generic`. Each supplies
layer boundaries, RFC 2119 rules, and the fitness functions to wire into CI. Apply every
profile the project uses.

## INIT — ask before scaffolding

1. Project name, and one sentence on what it is.
2. Stack(s) — maps to profiles.
3. Phase 1: its name and its goal.
4. The anti-features: what will explicitly not be built.
5. Does anything ship to a client or government body in Arabic? (Changes review depth, not structure.)

Then scaffold, fill `AGENTS.md` completely, and run `validate.py`. A tree still full of
`<!-- FILL -->` is worse than no tree — it looks authoritative and says nothing.

## Files

- `scripts/scaffold.py` · `scripts/validate.py`
- `data/file-registry.json` — every file, its token budget, language mode, owner
- `data/stack-profiles.json` — per-stack layers, rules, fitness functions
- `templates/*.md` — bilingual templates, split on `<!-- @@AR@@ -->`
- `references/retrofit.md` — adopting this on a live codebase without a freeze
- `references/failure-modes.md` — drift symptoms, doc-level fix, process-level fix

Without the bundle, the spec above is complete: write the tree by hand in the same shape.
