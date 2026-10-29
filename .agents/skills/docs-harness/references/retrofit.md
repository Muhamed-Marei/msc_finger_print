# Retrofitting the harness onto a live codebase

The rule that matters: **never freeze the project to document it.** A documentation freeze
gets cancelled in week two and leaves a half-written tree that nobody trusts. Ratchet
instead — new work is held to the standard, old debt is paid down as it is touched.

## Day 1 — toolchain pinning (non-invasive)

Hand-write a minimal `AGENTS.md`: build, run, typecheck, test, lint commands, and the repo
map. Nothing else. Verify each command actually runs — a stale command sends an agent into
a loop debugging your environment instead of doing the task.

Do **not** auto-generate this file. Generated context files measured *worse* than short
hand-written ones on task success, and they cost more per session. Twenty-five lines you
wrote beat three hundred a tool produced.

## Day 2–3 — empirical boundary mapping

Run a dependency analyser over the code and write `architecture.md` from what it reports,
not from what you intended. Every existing violation goes into the quarantined-debt table
with a location, a reason it stands, and a retire-by date.

Add three to five fitness functions with a **baseline that grandfathers existing
violations**, so the build stays green on day one. New code is held to the rule; the
baseline only shrinks.

## Day 4 — rules from real failures

Write `rules.md` from the last ten things that went wrong in review, phrased as RFC 2119
imperatives, each naming its enforcer. Do not write a style guide. A rule enters this file
because something broke, not because it sounded like good practice.

## Day 5 — ledger and phases

Create `03-phases/phase-NN-<current work>/` and convert the current sprint into
dependency-ordered tasks. The phase you are already in is phase 01 of the harness; earlier
history is reconstructed only where someone needs it.

## Week 2 onward — backfill by touching

- Back-fill three to five ADRs for decisions you are already living with. Choose the ones
  that get re-argued.
- When a feature is touched, write its `spec.md` and `implementation.md` then — not before.
- Product documents (`prd.md`, `srs.md`) are back-filled from what shipped, not from the
  original plan. The SRS describes the system that exists.
- Arabic mirrors follow the same rule: translate a document when it stabilises, not while
  it is still moving. `source_sha` will tell you the moment it moves again.

## When to stop

The harness is net negative below a certain size. Skip it for exploratory spikes under a
couple of days, one-off scripts, and throwaway prototypes with no maintenance horizon.
It earns its keep when work spans months, crosses sessions or people, or when agents write
a large share of the code — which is exactly when nobody can hold the system in their head.

Budget roughly 10–15% of effort on documentation maintenance. Past ~30%, the harness has
become the project, and something is wrong with how it is scoped.

## Order of operations, compressed

| Day | Deliverable | Do NOT |
|---|---|---|
| 1 | `AGENTS.md`, hand-written, commands verified | auto-generate it |
| 2–3 | `architecture.md` describing reality + baselined fitness functions | document the intended architecture |
| 4 | `rules.md` from real review failures | write a style guide |
| 5 | Current phase folder + dependency-ordered ledger | reconstruct old phases |
| Wk 2+ | ADRs, feature specs, product docs, Arabic mirrors — as touched | back-fill everything at once |
