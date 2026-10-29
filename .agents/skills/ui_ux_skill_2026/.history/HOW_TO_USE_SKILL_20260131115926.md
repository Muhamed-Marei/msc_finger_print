# Flutter UI/UX Design 2026 - Skill Files

This skill incorporates all **2026 Design Trends** (Intent-Driven, Tactile, Mood Modes) into a streamlined, AI-optimized package.

## 📁 Skill Structure

```
skill/
├── SKILL.md                          # Main skill file (Streamlined <200 lines)
├── README.md                         # Skill overview
├── data/
│   ├── color_palettes_2026.json     # Color database
│   ├── typography_2026.json         # Font database
│   └── mood_data.json               # [NEW] Mood mode definitions
└── references/
    ├── setup.md                      # [NEW] Quick start & checklist
    ├── patterns.md                   # [NEW] Detailed code examples
    ├── troubleshooting.md            # [NEW] Validation & performance
    └── quick-reference.md            # Quick lookup
```

## 🚀 How to Use

### 1. Upload to Claude Project
Upload `SKILL.md` and the `data/` and `references/` folders.

### 2. Auto-Routing
The skill automatically detects your intent:
*   **"Create a fintech app"** -> Activates Deep Trust palette & tabular fonts.
*   **"Fix my contrast"** -> Uses APCA rules from `troubleshooting.md`.
*   **"Add squishy buttons"** -> Pulls code from `patterns.md`.

### 3. Key Resources
*   **Mood Modes**: See `data/mood_data.json` for "Work", "Energy", "Calm", "Luxury" definitions.
*   **Setup**: Use `references/setup.md` for the 5-minute integration guide.
*   **Patterns**: Copy-paste production code from `references/patterns.md`.
