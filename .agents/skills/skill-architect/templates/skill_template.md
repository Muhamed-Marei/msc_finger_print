<!-- SKILL.md TEMPLATE — current Claude Code spec -->
<!-- Command name = directory name. `name` below is the display label only. -->
---
name: {{KEBAB_CASE_NAME}}
description: |
  {{KEY_USE_CASE_FIRST}}. {{WHAT_IT_DOES}}.
when_to_use: {{TRIGGER_PHRASES}}
# --- optional fields (delete what you don't need) ---
# argument-hint: {{[arg-hint]}}
# arguments: {{arg1 arg2}}
# allowed-tools: {{Read Grep Bash(git *)}}   # pre-approve (does not restrict)
# disable-model-invocation: true             # only the user can invoke
# user-invocable: false                      # only Claude can invoke
# context: fork                              # run in a subagent
# agent: {{Explore}}                         # subagent type when forked
# model: {{inherit}}
# effort: {{high}}
# paths: {{src/**/*.ts}}
---

# {{TITLE}}

{{ONE_SENTENCE_ROLE}}

## Routing

| Context | Action |
|---------|--------|
| {{PATTERN_1}} | {{ACTION_1}} |
| {{PATTERN_2}} | {{ACTION_2}} |

## Instructions

{{DENSE_STEPS_STATE_WHAT_TO_DO}}

<!-- Dynamic context injection (runs before Claude sees it; needs allowed-tools): -->
<!-- !`{{shell_command}}` -->

## Quick Reference

| Item | Value |
|------|-------|
| {{KEY}} | {{VALUE}} |

## Supporting files

- `data/{{NAME}}.json` — {{PURPOSE}}
- `references/{{NAME}}.md` — {{LOADED_ON_DEMAND}}
- `scripts/{{NAME}}.py` — run via `${CLAUDE_SKILL_DIR}/scripts/{{NAME}}.py`

<!-- Keep this file under 500 lines. Content stays in context across turns. -->
<!-- description + when_to_use are capped at 1,536 chars in the listing — key use case first. -->
