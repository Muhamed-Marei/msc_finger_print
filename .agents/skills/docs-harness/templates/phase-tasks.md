# Phase {{PHASE_NUM}} — Execution Ledger · سجل التنفيذ

This is the ONLY write-target for task state in this phase. One agent session owns it at a time.

## Legend · المفتاح
`[ ]` todo / لم تبدأ · `[/]` in progress / جارية · `[x]` done / منجزة
`[!]` blocked / معطّلة · `[~]` partial / جزئية

## Grammar
- Id: `T-{{PHASE_NUM}}.<FEATURE_CODE>.<NN>` — assigned once, never renumbered.
- Dependencies: `<!-- deps: T-01.AUTH.02, T-01.AUTH.03 -->` on the same line.
- A task MUST NOT start until every id in its `deps` is `[x]`.
- `[!]` and `[~]` MUST carry a reason and, for `[!]`, whether a human is required.
- Each task is one vertical slice: schema → logic → interface → test, in one session.
  If it needs two entities, or touches auth AND money AND schema, split it.

## Tasks

### <!-- FEATURE_CODE --> — <!-- Feature name / اسم الميزة -->
- [ ] T-{{PHASE_NUM}}.XXXX.01 <!-- task in English --> / <!-- المهمة بالعربية --> <!-- deps: — | req: REQ-000 -->
- [ ] T-{{PHASE_NUM}}.XXXX.02 <!-- --> / <!-- --> <!-- deps: T-{{PHASE_NUM}}.XXXX.01 -->

## Blocked · معطّلة
<!-- Move [!] tasks here with the full reason, artefacts already written, and the next action required. -->

## Deferred out of this phase · مؤجلة
| Id | Task | Deferred to | Why |
|---|---|---|---|
