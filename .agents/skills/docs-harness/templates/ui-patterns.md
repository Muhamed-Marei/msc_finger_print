# UI Patterns — {{PROJECT}}

## Component source of truth
- Library: <!-- FILL --> · Local components: <!-- FILL: path -->
- A component MUST NOT be reinvented locally when the library provides it.

## Required states
Every interactive component MUST define and implement: default, hover, focus-visible,
active, disabled, loading, error, empty. A component shipped without its empty and error
states is incomplete.

## Patterns
### <!-- Pattern name -->
- When to use: <!-- FILL --> · When not to: <!-- FILL -->
- Behaviour: <!-- FILL -->
- Bilingual note: <!-- FILL: what changes in RTL beyond mirroring -->

## Accessibility contracts
- Focus MUST be visible and MUST NOT be removed without an equivalent replacement.
- Form errors MUST be announced, linked to their field programmatically.
- Touch targets MUST be at least 44×44 px.
- Colour MUST NOT be the only carrier of meaning.

## Destructive actions
MUST require confirmation naming the object being destroyed, in the user's language.
<!-- @@AR@@ -->
# أنماط الواجهة — {{PROJECT}}

## مرجع المكوّنات
- المكتبة: <!-- املأ --> · المكوّنات المحلية: <!-- املأ -->
- يُمنع إعادة بناء مكوّن توفره المكتبة.

## الحالات الإلزامية
كل مكوّن تفاعلي يجب أن يعرّف ويطبّق: الافتراضية، التمرير، التركيز الظاهر، الضغط،
المعطّلة، التحميل، الخطأ، الفارغة. المكوّن الذي يصدر بلا حالتي الفراغ والخطأ ناقص.

## الأنماط
### <!-- اسم النمط -->
- متى يُستخدم: <!-- املأ --> · متى لا يُستخدم: <!-- املأ -->
- السلوك: <!-- املأ -->
- ملاحظة ثنائية اللغة: <!-- املأ: ما يتغير في الاتجاه RTL بخلاف الانعكاس -->

## عقود إتاحة الوصول
- يجب أن يكون مؤشر التركيز ظاهرًا، ويُمنع إزالته دون بديل مكافئ.
- يجب الإعلان عن أخطاء النماذج وربطها برمجيًا بحقولها.
- أصغر مساحة لمس 44×44 بكسل.
- يُمنع الاعتماد على اللون وحده لنقل المعنى.

## الإجراءات المدمِّرة
يجب أن تتطلب تأكيدًا يذكر اسم العنصر المراد حذفه بلغة المستخدم.
