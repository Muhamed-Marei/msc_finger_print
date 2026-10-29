# Rules — {{PROJECT}}

Phrasing is RFC 2119: MUST, MUST NOT, SHOULD. "Prefer" and "try to" are not rules —
a model trades those off under pressure. Every load-bearing rule names its enforcer.
A rule with no enforcer is a suggestion and will be violated.

## Universal
- Typecheck, tests, lint, and the architecture check MUST pass before a task is marked `[x]`. — *enforcer: CI*
- A dependency MUST NOT be added without an ADR. — *enforcer: lockfile diff check in CI*
- A test MUST NOT be weakened, skipped, or deleted to make a build pass. — *enforcer: human review + coverage gate*
- Secrets MUST NOT appear in any file under `docs/`, in committed config, or in a commit message. — *enforcer: secret scanner pre-commit*
- Generated artefacts MUST NOT be hand-edited. — *enforcer: regenerate-and-diff CI step*
- A change exceeding <!-- FILL: e.g. 400 --> changed lines excluding tests and lockfiles MUST be split. — *enforcer: PR size check*

## Stack rules — {{STACK_LABEL}}
{{STACK_RULES}}

Fitness functions to wire up:
{{STACK_FITNESS}}

## Localisation
- User-facing strings MUST NOT be hardcoded; they go through the localisation layer.
- Every new string key MUST ship with both Arabic and English values.
- Layout MUST NOT assume text direction. Use logical properties (start/end), not left/right.
- A term MUST match `00-product/glossary.md` before it reaches a component.

## Documentation
- An agent MUST NOT edit `architecture.md`, `rules.md`, or anything under `decisions/`.
- A conflict between code and docs is reported, not resolved unilaterally.
- An accepted ADR MUST NOT be edited. Supersede it with a new one.

## Contradiction procedure
1. Does it fail a fitness function or test? → the code is wrong. Stop and fix the code.
2. Is the violated rule backed by an ADR? → the code is wrong. Fix the code.
3. No ADR, and the rule has been overtaken by a defensible change? → write a NEW ADR superseding it, get human approval, then update the doc.
4. The rule stands and was violated without justification? → revert, however clean the code looks.
5. Record the outcome so the next session does not re-litigate it.

Never step 3 in the same session that wrote the violating code.
<!-- @@AR@@ -->
# القواعد — {{PROJECT}}

الصياغة إلزامية بمعيار RFC 2119: "يجب"، "يُمنع". عبارات مثل "يُفضَّل" ليست قواعد.
كل قاعدة أساسية تذكر أداة فرضها. القاعدة بلا أداة فرض مجرد اقتراح وستُخالَف.

## قواعد عامة
- يجب اجتياز فحص الأنواع والاختبارات وفحص المعمارية قبل وضع علامة `[x]`.
- يُمنع إضافة أي اعتمادية بدون سجل ADR.
- يُمنع إضعاف أو حذف أي اختبار لتمرير البناء.
- يُمنع وجود أي أسرار داخل `docs/` أو في الإعدادات المرفوعة أو في رسائل الالتزام.
- يُمنع التحرير اليدوي للمخرجات المولّدة.

## قواعد المنصة — {{STACK_LABEL}}
{{STACK_RULES}}

## التعريب
- يُمنع كتابة النصوص الظاهرة للمستخدم مباشرة في الكود.
- كل مفتاح نصي جديد يجب أن يصدر بالعربية والإنجليزية معًا.
- يُمنع افتراض اتجاه النص في التخطيط؛ تُستخدم الخصائص المنطقية (start/end).
- يجب مطابقة المصطلح لملف `glossary.md` قبل استخدامه في أي مكوّن.

## التوثيق
- يُمنع على الوكيل تعديل `architecture.md` أو `rules.md` أو أي ملف في `decisions/`.
- التعارض بين الكود والتوثيق يُبلَّغ عنه ولا يُحسم من طرف واحد.
- يُمنع تعديل سجل ADR معتمد؛ يُستبدل بسجل جديد ينسخه.
