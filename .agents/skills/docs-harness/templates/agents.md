# AGENTS.md — {{PROJECT}}

## Project
{{PROJECT}} — one sentence: what it is and who it serves. <!-- FILL -->

## Build & verify (run before marking any task [x])
- Install: `<command>` <!-- FILL -->
- Run: `<command>` <!-- FILL -->
- Typecheck: `<command>` · Test: `<command>` · Lint: `<command>` <!-- FILL -->
- Architecture check: `<command>` <!-- FILL: the fitness function; see 01-architecture/rules.md -->
- Docs check: `python docs/_meta/validate.py docs`

## Repo map
<!-- FILL: one line per deployable unit. Keep it to what changes where. -->

## Doc routing — read before editing
| If you are… | Read |
|---|---|
| picking up work | `docs/03-phases/ROADMAP.md`, then the active phase's `tasks.md` |
| adding or changing a feature | that phase's `features/<slug>/spec.md` and `implementation.md` |
| touching architecture, layers, or data ownership | `docs/01-architecture/architecture.md` |
| writing any code | `docs/01-architecture/rules.md` |
| touching UI, copy, or tokens | `docs/02-brand/design-tokens.md`, `ui-patterns.md` |
| naming anything user-facing (AR or EN) | `docs/00-product/glossary.md` |
| making a non-obvious decision | `docs/01-architecture/decisions/` — append, never edit |
| deploying or debugging production | `docs/04-operations/runbook.md` |

## Operating protocol
1. Read the routed doc(s) before writing code. Do not infer conventions from nearby files.
2. Take ONE task from the active phase's `tasks.md`. Mark it `[/]` before starting.
3. All of a task's `deps:` MUST be `[x]` before it may be started.
4. Write or update the test asserting the requirement, then the code.
5. Run typecheck, tests, lint, and the architecture check. Fix failures inside the task.
6. Mark `[x]` and write the status back to `tasks.md`. Blocked → `[!]` with the reason and whether a human is needed.
7. Append an ADR for any decision a future session would otherwise re-litigate.
8. Reset context between unrelated tasks. The docs carry the state; a reset loses nothing.

## Hard boundaries — explicit human approval required
- Auth, permissions, and session handling.
- Database schema migrations and any destructive change.
- Security rules and access policies.
- Public API or contract shape.
- Money, billing, and pricing logic.
- Adding a dependency.
- Editing `01-architecture/architecture.md`, `rules.md`, or anything under `decisions/`.

## Guardrail
If your implementation conflicts with a doc, the CODE is wrong by default.
You MUST NOT edit a doc to match your own output. Stop and report the conflict.

---
## دليل التشغيل — ملخص عربي
- نقطة البداية: `docs/03-phases/ROADMAP.md` ثم ملف `tasks.md` للمرحلة النشطة.
- مهمة واحدة في كل جلسة. لا تبدأ مهمة قبل اكتمال كل اعتمادياتها.
- التحقق (فحص الأنواع، الاختبارات، فحص المعمارية) إلزامي قبل وضع علامة `[x]`.
- عند تعارض الكود مع التوثيق: الكود هو الخطأ. ممنوع تعديل التوثيق لتبرير الكود.
- القرارات المعمارية تُضاف كسجل ADR جديد، ولا تُعدَّل السجلات المعتمدة.
