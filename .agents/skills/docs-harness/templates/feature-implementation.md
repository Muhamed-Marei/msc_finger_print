# Implementation plan — {{FEATURE_TITLE}} (phase {{PHASE_NUM}})

- Code: {{FEATURE_CODE}} · Spec: `./spec.md`
- Approach approved by: <!-- human name --> on <!-- date -->

## Approach
<!-- FILL: two or three sentences. The shape of the solution, and why this shape. -->
<!-- If this choice has consequences a future session would question, it needs an ADR. -->

## Layers touched
| Layer | Change | Files (indicative) |
|---|---|---|

## Vertical slices
Each slice completes in one session: data → logic → interface → test.

| Slice | Delivers | Task ids |
|---|---|---|
| 1 | <!-- --> | T-{{PHASE_NUM}}.{{FEATURE_CODE}}.01–0X |

## Contracts changed
- API / schema: <!-- FILL or "none" --> — breaking? <!-- yes/no -->
- If breaking: migration path and the ADR covering it: <!-- FILL -->

## Test plan
| What | Level | Asserts |
|---|---|---|
| <!-- --> | unit \| integration \| e2e | <!-- the invariant, not the implementation --> |

## Rollout and rollback
- Feature flag: <!-- FILL or "none" -->
- Rollback: <!-- FILL: the actual steps, not "revert the commit" if data moved. -->

## Risks accepted
<!-- FILL: what could go wrong that is being accepted rather than mitigated. -->
<!-- @@AR@@ -->
# خطة التنفيذ — {{FEATURE_TITLE}} (المرحلة {{PHASE_NUM}})

- الرمز: {{FEATURE_CODE}} · المواصفة: `./spec.ar.md`
- اعتُمد النهج من: <!-- الاسم --> بتاريخ <!-- التاريخ -->

## النهج
<!-- املأ: جملتان أو ثلاث. شكل الحل وسبب اختياره. -->

## الطبقات المتأثرة
| الطبقة | التغيير | الملفات (استرشادي) |
|---|---|---|

## الشرائح الرأسية
كل شريحة تكتمل في جلسة واحدة: بيانات ← منطق ← واجهة ← اختبار.

| الشريحة | ما تنجزه | معرفات المهام |
|---|---|---|

## العقود المتغيرة
- الواجهة / المخطط: <!-- املأ أو "لا شيء" --> — تغيير كاسر؟ <!-- نعم/لا -->
- إن كان كاسرًا: مسار الترحيل وسجل ADR المغطي: <!-- املأ -->

## خطة الاختبار
| ماذا | المستوى | ما يتحقق منه |
|---|---|---|

## الإطلاق والتراجع
- مفتاح الميزة: <!-- املأ أو "لا يوجد" -->
- التراجع: <!-- املأ: الخطوات الفعلية. -->

## مخاطر مقبولة
<!-- املأ -->
