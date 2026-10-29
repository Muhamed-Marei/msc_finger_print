# Installing docs-harness

## As a project skill (recommended — keeps the scripts and templates)

Drop the whole folder into the repo you want it to govern:

```
<your-repo>/.claude/skills/docs-harness/
```

Claude picks it up automatically in that repo. Invoke with `/docs-harness`, or just ask —
the description triggers on "organize docs", "set up documentation", "add a phase", and so on.

## As an account skill

A saved account skill is a single `SKILL.md`, so the scripts and templates do not travel
with it. `SKILL.md` is written to be complete on its own: Claude builds the same tree by
hand from the spec. Use this when you want the structure available everywhere and the
scripts only where they matter.

## First run

```bash
python scripts/scaffold.py init --root docs --project "Your Project" \
       --stack nestjs-graphql --phase 01:foundation:Foundation
```

Multiple stacks: run `init` with the main one, then copy the extra profiles' `rules` and
`layers` out of `data/stack-profiles.json` into `docs/01-architecture/rules.md` and
`architecture.md`.

Then, in order:

1. Fill every `<!-- FILL -->` in `docs/AGENTS.md`. Verify each command actually runs.
2. Write the anti-features list in `docs/00-product/prd.md`. It is the section that saves the most work.
3. Wire the profile's fitness functions into CI. A rule with no enforcer is a suggestion.
4. `python docs/_meta/validate.py docs` — expect warnings about unreviewed Arabic and unfilled placeholders; expect zero errors.

## Wiring the check into CI

```yaml
- name: Docs harness
  run: python docs/_meta/validate.py docs
```

`validate.py` is copied into `docs/_meta/` by `init`, so CI does not need this bundle.
Add `--strict` once the tree is filled in and you want warnings to block too.

## Bundle contents

```
SKILL.md                     the spec — complete on its own
INSTALL.md                   this file
scripts/scaffold.py          init · add-phase · add-feature · add-adr
scripts/validate.py          secrets · translation sync · task DAG · structure · budgets
data/file-registry.json      every file: token budget, language mode, owner
data/stack-profiles.json     7 profiles: layers, RFC 2119 rules, fitness functions
templates/                   25 bilingual templates, split on <!-- @@AR@@ -->
references/retrofit.md       adopting this on a live codebase without a freeze
references/failure-modes.md  drift symptoms, doc fix, process fix
```
