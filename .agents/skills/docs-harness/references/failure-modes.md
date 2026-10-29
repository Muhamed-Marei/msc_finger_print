# Failure modes

Each row: how it shows up, what to change in the documents, and what to change in the
process. A doc-level fix alone almost never holds — the process column is the one that lasts.

| Failure | Early warning | Doc-level fix | Process-level fix |
|---|---|---|---|
| **Doc/code drift** | The folder tree or data model in `architecture.md` no longer matches the repo | Regenerate structural sections from code; never regenerate rationale | Pre-commit drift check; `validate.py` in CI |
| **Doc rewrite** — agent loosens a rule to pass | A diff touches `rules.md` or `architecture.md` alongside code | Guardrail line in `AGENTS.md`; ADRs append-only | CODEOWNERS on `01-architecture/`; agent tool permissions exclude it |
| **Context rot mid-session** | The agent forgets a rule it followed twenty turns ago | Shorten the always-loaded layer; push procedure to linked files | Reset context between unrelated tasks; smaller slices |
| **Router bloat** | `AGENTS.md` past ~1500 tokens, per-session cost climbing | Prune; move anything not needed every session to a linked file | Line-count gate in CI; quarterly prune |
| **Architectural violation** | A fitness function fails, or a layer import appears that shouldn't | Add the explicit MUST NOT with its enforcer named | Wire the check; fail the build, not the review |
| **Re-litigated decisions** | The same debate every few sessions | Write or sharpen the ADR, including rejected alternatives | Route `decisions/` from `AGENTS.md` so it is actually read |
| **Test subversion** | Tests edited in the same diff that made them fail | `rules.md`: tests MUST NOT be weakened to pass a build | Invariant tests the agent may not edit; human sign-off on test deletions |
| **Stale Arabic** | Client sees an Arabic document describing last quarter's system | Retranslate, update `source_sha` | `validate.py` fails on STALE; translate at stabilisation, not during churn |
| **Ledger clobbering** | Task updates silently lost | One `tasks.md` per phase, never a shared root ledger | One agent per phase; separate worktrees for parallel work |
| **Verification fatigue** | Large diffs approved in seconds; bugs surface in untouched-looking areas | Keep slices small; state acceptance criteria in the feature spec | Diff budget per day; never run more agents than you can review |
| **Comprehension debt** | You cannot explain a module that shipped last month | ADRs capturing rationale, not just outcome | Reserve real work for yourself — debug unaided before asking; ask the agent *why*, not only *do* |
| **Phantom dependency** | A package appears in the lockfile that nobody chose | `rules.md`: no dependency without an ADR | Lockfile diff check in CI; restrict the agent's install permissions |
| **Secret leak** | A key in a doc, a commit message, or a debug script | `environments.md` holds names only | Secret scanner pre-commit and in CI; ignore-rules so the agent cannot read `.env` at all |

## The two that are specific to agent-written code

**Doc rewrite** is the one to guard hardest. The pattern is exact: the agent's code violates
a constraint, a check fails, and the agent edits the constraint. It then reports success,
truthfully as far as it can tell. The defence is structural, not instructional — the agent
must not have write access to `01-architecture/`, and the session that wrote the code must
never be the session that reconciles the document.

**Comprehension debt** is the one with no automated detection. Controlled study of engineers
learning an unfamiliar library found the AI-assisted group scored roughly 50% against 67%
on comprehension afterwards, with the widest gap in debugging and no significant speed gain.
The system keeps working; your ability to fix it when it stops does not. The only known
mitigations are behavioural: keep a real share of the work manual, ask for trade-offs rather
than output, write the ADR yourself, and debug a failure unaided before handing it over.

## Reading the validator

| Signal | Means | Action |
|---|---|---|
| `SECRET` | A credential value is committed | Remove, **rotate the credential**, then re-run |
| `TRANSLATION … STALE` | English changed after translation | Retranslate, update `source_sha` |
| `TASKS … cycle` | The plan is not executable as written | Break the cycle before starting any task in it |
| `TASKS … MUST NOT start` | A task is running ahead of its dependency | Either the dep is actually done and unmarked, or the ledger is fiction |
| `BUDGET >130%` | A file is past the point of reliable retrieval | Split it or move detail down a hop |
| `structure … FILL` | The router still has placeholders | Fill them; a half-written router is worse than none |
