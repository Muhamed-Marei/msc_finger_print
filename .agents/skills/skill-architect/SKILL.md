---
name: skill-architect
description: |
  Create, improve, and audit Codex skills to the current official spec, and convert vague requests into professional 4-Block prompts. Produces a complete SKILL.md plus supporting structure that conforms to the Agent Skills standard.
  TRIGGERS: create skill, make skill, new skill, improve skill, audit skill, skill template, convert to prompt, professional prompt, agent, capability
when_to_use: |
  When the user wants to scaffold a new skill, fix/modernize an existing SKILL.md, turn a request into a structured prompt, or asks how Codex skills work (frontmatter, locations, substitutions, dynamic injection, subagents).
---

# Skill Architect

Build and improve Codex skills that match the **current official spec**, and convert requests into professional prompts. The authoritative reference is bundled — see [References](#references); consult it for any detail not covered inline.

## Modes

| Input | Mode | Output |
|-------|------|--------|
| "Create skill for X" | SKILL_CREATE | Complete SKILL.md + directory |
| "Improve / audit this skill" | SKILL_IMPROVE | Spec-aligned SKILL.md + report |
| "Convert to prompt" | PROMPT_CONVERT | 4-Block professional prompt |
| Vague request | AUTO_DETECT | Pick the best mode above |

---

## MODE: SKILL_CREATE

### Step 1 — Analyze
Extract: purpose, when to trigger, who invokes it (you / Codex / both), where it runs (inline vs forked subagent), tools needed, supporting data.

### Step 2 — Choose location
The directory name becomes the command (`/name`). Pick scope:

| Scope | Path | Applies to |
|-------|------|-----------|
| Personal | `~/.Codex/skills/<name>/SKILL.md` | all your projects |
| Project | `.Codex/skills/<name>/SKILL.md` | this repo (commit to share) |
| Plugin | `<plugin>/skills/<name>/SKILL.md` | where plugin is enabled (`/plugin:name`) |

Precedence: enterprise > personal > project. Plugin skills are namespaced so they never collide.

### Step 3 — Scaffold
```
<name>/
├── SKILL.md          # required: frontmatter + instructions
├── data/             # JSON configs/databases (loaded when referenced)
├── templates/        # output templates Codex fills in
├── references/       # large docs, specs (loaded on demand)
└── scripts/          # executable helpers (run, not loaded)
```
Only `SKILL.md` is required. Reference every supporting file from SKILL.md so Codex knows what it holds and when to load it.

### Step 4 — Write SKILL.md
Canonical template (see also `templates/skill_template.md`):
```markdown
---
name: <kebab-case>            # display label only; command = directory name
description: |                # key use case FIRST (see cap below)
  <what it does + when to use it, in one or two dense lines>
when_to_use: <trigger phrases / example requests>   # optional
allowed-tools: Read Grep      # optional: pre-approve tools (does not restrict)
disable-model-invocation: true  # optional: only the user can run it (side effects)
---

# <Title>

<One-sentence role / purpose.>

## Routing
| Context | Action |
|---------|--------|
| <pattern> | <behavior> |

## Instructions
<Dense steps. State what to do, not why.>

## Supporting files
- `data/<x>.json` — <purpose>
```

### Skill Quality Rules
1. **Concise** — keep SKILL.md under **500 lines**; content stays in context across turns, so every line is a recurring token cost.
2. **Description first** — lead with the primary use case. `description` + `when_to_use` is truncated at **1,536 chars** in the skill listing.
3. **Single source of truth** — no redundancy; push detail to `references/`.
4. **Tables over prose, JSON over paragraphs**, code examples over explanation.
5. **Routing table** for multi-mode skills.
6. **Pick invocation + location deliberately** (see below).

---

## Skill Spec Reference

> Inline essentials. Full detail: `references/Codex-skills-docs.md`.

### Command name vs `name`
For `.Codex/skills/<dir>/SKILL.md`, the **directory name** is the command you type. The frontmatter `name` is only the display label (except a plugin-root `SKILL.md`, where `name` sets the command). A `.Codex/commands/foo.md` file also creates `/foo`.

### Frontmatter fields (all optional; only `description` recommended)
| Field | Purpose |
|-------|---------|
| `name` | Display label; defaults to directory name |
| `description` | What it does + when to use it; Codex matches on this. Key use case first |
| `when_to_use` | Extra trigger phrases; appended to description (counts toward 1,536-char cap) |
| `argument-hint` | Autocomplete hint, e.g. `[issue-number]` |
| `arguments` | Named positional args for `$name` substitution (string or YAML list) |
| `disable-model-invocation` | `true` = only the user can invoke (use for side-effect workflows) |
| `user-invocable` | `false` = only Codex can invoke (background knowledge) |
| `allowed-tools` | Pre-approve tools while active (does **not** restrict the pool) |
| `disallowed-tools` | Remove tools from the pool while active |
| `model` | Model override for the turn (`/model` values or `inherit`) |
| `effort` | `low`/`medium`/`high`/`xhigh`/`max` while active |
| `context` | `fork` = run in a subagent context |
| `agent` | Subagent type when forked (`Explore`, `Plan`, `general-purpose`, or custom) |
| `hooks` | Hooks scoped to this skill's lifecycle |
| `paths` | Globs that gate auto-activation to matching files |
| `shell` | `bash` (default) or `powershell` for inline shell |

### Invocation control
| Frontmatter | User invokes | Codex invokes |
|-------------|:---:|:---:|
| (default) | yes | yes |
| `disable-model-invocation: true` | yes | no |
| `user-invocable: false` | no | yes |

### String substitutions (in skill body)
| Token | Expands to |
|-------|-----------|
| `$ARGUMENTS` | full argument string as typed |
| `$ARGUMENTS[N]` / `$N` | the Nth arg (0-based); quote multi-word args |
| `$name` | named arg declared in `arguments` frontmatter |
| `${CLAUDE_SESSION_ID}` | current session ID |
| `${CLAUDE_EFFORT}` | current effort level |
| `${CLAUDE_SKILL_DIR}` | the skill's own directory (use for bundled scripts) |

If args are passed but `$ARGUMENTS` is absent, Codex appends `ARGUMENTS: <value>`. Escape a literal with `\$1`.

### Dynamic context injection
`` !`<command>` `` runs **before** Codex sees the content; its output replaces the placeholder (preprocessing, not a tool call). Inline form is only recognized at line start or after whitespace. For multi-line, use a fenced ` ```! ` block. Pre-approve with `allowed-tools: Bash(...)`.
```markdown
## Current changes
!`git diff HEAD`
```

### Subagent execution (`context: fork`)
Runs the skill in isolation; the SKILL.md body becomes the subagent's prompt (no conversation history). Only use for skills with an **actionable task** — pure reference guidelines produce no output when forked. Pick the executor with `agent:`.

---

## MODE: PROMPT_CONVERT

Convert any request to a **4-Block Professional Prompt** (template: `templates/prompt_4block.xml`).

1. **Instructions** — `<role>` (specific expert persona), `<governance>` (truthfulness, security, tone), `<uncertainty_protocol>`.
2. **Context** — `<environment>` (date, app context) + `<domain_data>` in containers.
3. **Task** — clear imperative + `<thinking_protocol>` (extraction → reasoning → answer).
4. **Output Format** — deterministic schema (raw JSON, no preamble).

Process: identify intent → select persona (`data/personas.json`) → define constraints → structure output → add chain-of-thought if reasoning is complex.

---

## MODE: SKILL_IMPROVE

### Audit checklist
- [ ] SKILL.md under 500 lines; detail pushed to `references/`?
- [ ] `description` leads with the key use case and fits 1,536 chars?
- [ ] Frontmatter uses real fields (no invented keys)?
- [ ] Invocation control correct (`disable-model-invocation` for side effects)?
- [ ] Tables/JSON instead of prose; code over explanation?
- [ ] Routing table present for multi-mode skills?
- [ ] Supporting files referenced from SKILL.md?
- [ ] `${CLAUDE_SKILL_DIR}` used for bundled script paths?

### Fixes
| Issue | Fix |
|-------|-----|
| Too verbose / >500 lines | Move detail to `references/`, compress |
| Weak triggering | Sharpen `description` + add `when_to_use` keywords |
| Triggers too often | Make `description` specific; add `disable-model-invocation` |
| Prose data | Convert to JSON in `data/` |
| Hardcoded script paths | Use `${CLAUDE_SKILL_DIR}` |
| No invocation control | Add `disable-model-invocation` / `user-invocable` |

---

## Troubleshooting

- **Not triggering** — description lacks natural keywords; verify via "What skills are available?"; rephrase request; invoke directly with `/name`.
- **Triggers too often** — make description more specific or set `disable-model-invocation: true`.
- **Description cut short** — listing budget overflow (scales at 1% of context). Run `/doctor`; trim text (key use case first), set low-priority skills to `"name-only"` via `skillOverrides`, or raise `skillListingBudgetFraction`.

---

## Quality Metrics
| Metric | Target |
|--------|--------|
| Specificity | Persona/description activates the right behavior |
| Determinism | Output schema enforced |
| Safety | Uncertainty / hallucination protocol defined |
| Efficiency | Minimal tokens, max info density |

## Quick Patterns
- Persona: ❌ "helpful assistant" → ✅ "Senior <Domain> Engineer".
- Output control: ❌ free format → ✅ end prompt with `{` to force JSON.
- Uncertainty: ❌ silent guessing → ✅ `If unknown: <status>UNKNOWN</status>`.

## Self-Learning
1. Effective patterns → `data/lessons.json`.
2. New spec details → update `references/Codex-skills-docs.md` from the live index.
3. Failed approaches → `data/lessons.json` anti-patterns.

## References
- **Bundled spec**: `references/Codex-skills-docs.md` — full official "Extend Codex with skills" documentation.
- **Live index**: https://code.Codex.com/docs/llms.txt — refresh the bundled copy when the spec changes.
- **Templates**: `templates/skill_template.md`, `templates/prompt_4block.xml`.
- **Data**: `data/personas.json`, `data/lessons.json`.
