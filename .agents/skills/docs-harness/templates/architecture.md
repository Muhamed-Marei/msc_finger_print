# Architecture — {{PROJECT}}

> This file describes what IS true, not what should be. If it disagrees with the code,
> one of them is a defect — resolve it through the procedure in `rules.md`, never by
> quietly editing this file.

## Stack
{{STACK_LABEL}} <!-- FILL: versions where they constrain design -->

## Layer boundaries — MUST NOT be crossed
{{STACK_LAYERS}}
<!-- FILL: add the import direction for each layer. A layer name without an import rule is decoration. -->

Enforced by: <!-- FILL: the fitness function command -->

## Data ownership — authoritative
| Store | Owns | Written by | Never written by |
|---|---|---|---|
| <!-- store --> | <!-- entities --> | <!-- path --> | <!-- path --> |

An entity has exactly one owning store. Cross-store consistency rules go here, not in code comments.

## Contracts
- Source of truth for the API surface: <!-- FILL: path -->
- Generated artefacts: <!-- FILL --> — regenerated, never hand-edited.
- Versioning: <!-- FILL: additive-only? breaking change procedure? -->

## Known technical debt — quarantined
<!-- Existing violations recorded here are grandfathered so the build stays green. -->
<!-- New code is held to the rules above. Each line names the file and the plan. -->
| Location | Violation | Why it stands | Retire by |
|---|---|---|---|

## Folder structure
<!-- Generated. Regenerate with your tree command; do not maintain by hand. -->
<!-- @@AR@@ -->
# المعمارية — {{PROJECT}}

> تصف هذه الوثيقة الواقع الفعلي لا المرغوب. عند اختلافها عن الكود فأحدهما خطأ،
> ويُحسم الأمر عبر الإجراء الوارد في `rules.ar.md`، لا بتعديل هذه الوثيقة بهدوء.

## المنصة التقنية
{{STACK_LABEL}}

## حدود الطبقات — يُمنع تجاوزها
{{STACK_LAYERS}}
<!-- املأ: اتجاه الاستيراد لكل طبقة. اسم الطبقة بلا قاعدة استيراد مجرد زخرفة. -->

أداة الفرض: <!-- املأ -->

## ملكية البيانات — مرجعية
| المخزن | يملك | يكتب فيه | يُمنع أن يكتب فيه |
|---|---|---|---|

لكل كيان مخزن واحد يملكه. قواعد الاتساق بين المخازن تُكتب هنا لا في تعليقات الكود.

## العقود
- مرجع واجهة البرمجة: <!-- املأ -->
- المخرجات المولّدة: <!-- املأ --> — تُولَّد ولا تُحرَّر يدويًا.
- الإصدارات: <!-- املأ -->

## الدين التقني المعروف — معزول
| الموضع | المخالفة | سبب بقائها | موعد الإزالة |
|---|---|---|---|

## هيكل المجلدات
<!-- مولَّد تلقائيًا. -->
