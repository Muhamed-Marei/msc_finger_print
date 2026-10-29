# Riverpod 3.0 Skill - Complete Index

## 📑 File Organization

```
riverpod-3/
├── Core Documentation
│   ├── SKILL.md ⭐                       # MAIN SKILL - Start here
│   ├── README.md                         # Overview and quick reference
│   ├── CHEATSHEET.md                     # Quick syntax reference
│   ├── INSTALLATION_GUIDE.md             # Setup and usage instructions
│   └── INDEX.md                          # This file
│
├── data/                                 # Structured JSON reference
│   ├── migration_map.json                # Legacy → Riverpod 3.0 mappings
│   ├── lifecycle_hooks.json              # Complete lifecycle API
│   └── troubleshooting.json              # Common errors and solutions
│
├── examples/                             # Production-ready code
│   ├── complete_chat_architecture.dart   # Full chat implementation
│   ├── pagination_pattern.dart           # Infinite scroll patterns
│   ├── auth_with_either.dart             # Authentication with Either
│   └── video_memory_management.dart      # Memory-safe media handling
│
└── templates/
    └── provider_templates.dart           # 14 copy-paste patterns
```

---

## 🎯 Quick Navigation by Use Case

### "I'm new to Riverpod 3.0"
1. **Start:** `INSTALLATION_GUIDE.md` - Setup your project
2. **Learn:** `SKILL.md` - Core concepts and architecture
3. **Reference:** `CHEATSHEET.md` - Quick syntax lookup
4. **Practice:** `templates/provider_templates.dart` - Copy basic patterns

### "I'm migrating from Riverpod 2.x"
1. **Read:** `data/migration_map.json` - All breaking changes
2. **Reference:** `SKILL.md` → "Migration from Legacy" section
3. **Copy:** `templates/provider_templates.dart` - Modern patterns
4. **Replace:** Legacy StateNotifier → Notifier

### "I'm building a chat app"
1. **Study:** `examples/complete_chat_architecture.dart` - Full implementation
2. **Learn:** Dual-stack pattern (Firestore + WebSocket)
3. **Implement:** Optimistic UI with pending state
4. **Reference:** `SKILL.md` → "Real-Time Chat Architecture"

### "I need pagination/infinite scroll"
1. **Study:** `examples/pagination_pattern.dart` - Complete pattern
2. **Copy:** `templates/provider_templates.dart` → Template #8
3. **Reference:** `SKILL.md` → "Pagination (Infinite Scroll)"

### "I'm having performance issues"
1. **Check:** `data/troubleshooting.json` → "excessive_rebuilds"
2. **Learn:** `CHEATSHEET.md` → "Performance Tips"
3. **Apply:** `.select()` for granular watching
4. **Reference:** `SKILL.md` → "Performance Checklist"

### "I need error handling with Either"
1. **Study:** `examples/auth_with_either.dart` - Complete flow
2. **Copy:** `templates/provider_templates.dart` → Template #7
3. **Reference:** `SKILL.md` → "Functional Error Handling with Either"

### "Video/images are causing memory leaks"
1. **Study:** `examples/video_memory_management.dart`
2. **Learn:** Scoped provider pattern with `ref.onDispose`
3. **Reference:** `data/troubleshooting.json` → "memory_leak_video"

### "I'm getting errors"
1. **Search:** `data/troubleshooting.json` - All common errors
2. **Check:** Error message → find exact match
3. **Apply:** Solution from troubleshooting guide

---

## 📚 Document Details

### SKILL.md (Main Documentation)
**Purpose:** Complete architectural guide for Riverpod 3.0

**Sections:**
- Auto Mode Selection (triggers)
- Core Architecture Principles
- Installation & Setup
- Provider Types & Code Generation
- Lifecycle Management
- Functional Error Handling with Either
- Real-Time Communication Layer
- Memory-Safe Media Handling
- Pagination (Infinite Scroll)
- Debounced Search
- OneSignal Integration
- Advanced Patterns
- Migration from Legacy
- Common Pitfalls

**When to use:** Reference for understanding architecture, best practices, and production patterns.

---

### README.md (Overview)
**Purpose:** Quick overview and navigation

**Sections:**
- What's Included
- Quick Start
- Core Concepts
- Architectural Patterns (summaries)
- Migration Guide
- Example Implementations
- Templates
- Testing
- Performance Checklist

**When to use:** First-time overview, quick reference, finding examples.

---

### CHEATSHEET.md (Quick Reference)
**Purpose:** Fast syntax lookup

**Sections:**
- Provider Types (table)
- Code Generation Syntax
- Lifecycle Hooks
- Ref API
- AsyncValue Pattern Matching
- Functional Error Handling
- Common Patterns (code snippets)
- UI Widgets
- Testing
- Migration Quick Reference
- Build Commands
- Common Mistakes
- Performance Tips

**When to use:** Daily development, syntax lookup, code writing.

---

### INSTALLATION_GUIDE.md (Setup)
**Purpose:** Step-by-step installation and usage

**Sections:**
- Installing the Skill
- Skill Structure
- Quick Start for Flutter Project
- How to Use This Skill
- Common Workflows
- Testing Providers
- Performance Best Practices
- Getting Help

**When to use:** First-time setup, understanding skill structure.

---

### data/migration_map.json
**Purpose:** Structured reference for legacy → 3.0 migration

**Contents:**
- `provider_migrations` - All provider type conversions
- `ref_api_changes` - Ref interface changes
- `initialization_changes` - Constructor → build() logic

**When to use:** Converting old code to Riverpod 3.0.

---

### data/lifecycle_hooks.json
**Purpose:** Complete lifecycle API reference

**Contents:**
- `lifecycle_methods` - ref.onDispose, onCancel, onResume, keepAlive
- `autodispose_behavior` - Default behavior
- `ttl_cache_pattern` - Time-to-live implementation
- `common_patterns` - Real-world usage examples

**When to use:** Understanding provider lifecycle, memory management.

---

### data/troubleshooting.json
**Purpose:** Solutions for common errors

**Contents:**
- `common_errors` - 10+ error scenarios with solutions
  - provider_was_disposed
  - memory_leak_video
  - excessive_rebuilds
  - search_too_many_requests
  - firestore_read_costs
  - async_loading_flicker
  - And more...
- `performance_optimization` - Techniques with impact metrics
- `debugging_tips` - Practical debugging approaches
- `migration_issues` - Legacy migration problems

**When to use:** Debugging errors, performance optimization.

---

### examples/complete_chat_architecture.dart
**Purpose:** Production-ready chat implementation

**Demonstrates:**
- Dual-stack architecture (Firestore + WebSocket)
- Optimistic UI with pending/server state merge
- Either monad for error handling
- Repository pattern
- Message sending with failure handling
- Real-time sync
- TTL caching for streams

**Lines of code:** ~350 (fully documented)

**When to use:** Building chat, real-time features, understanding complex architecture.

---

### examples/pagination_pattern.dart
**Purpose:** Infinite scroll with AsyncNotifier

**Demonstrates:**
- Reverse pagination (chat-style)
- State preservation during loading
- ScrollNotification listener
- Alternative ScrollController approach
- Error-preserving updates
- Pull-to-refresh
- isReloading vs isLoading handling

**Lines of code:** ~250

**When to use:** Implementing infinite scroll, list pagination.

---

### examples/auth_with_either.dart
**Purpose:** Complete authentication flow with functional error handling

**Demonstrates:**
- Domain failures (sealed classes)
- Repository returning Either<Failure, Success>
- AsyncNotifier consuming Either
- Firebase integration
- Auth state stream
- UI pattern matching with errors
- Navigation on auth state change

**Lines of code:** ~300

**When to use:** Building authentication, learning Either monad, error handling.

---

### examples/video_memory_management.dart
**Purpose:** Memory-safe video player patterns

**Demonstrates:**
- Scoped VideoPlayerController with autoDispose
- Automatic disposal on scroll
- TTL caching for recently viewed videos
- VideoPlayback Notifier with controls
- Memory monitoring utilities
- Widget integration

**Lines of code:** ~230

**When to use:** Handling video/media, preventing memory leaks, infinite scroll with media.

---

### templates/provider_templates.dart
**Purpose:** 14 copy-paste starting points

**Templates:**
1. Simple Provider (Dependency Injection)
2. Future Provider (REST API Call)
3. Stream Provider (Firestore)
4. Notifier (Sync Mutable State)
5. AsyncNotifier (Async Actions)
6. StreamNotifier (WebSocket Bridge)
7. Repository with Either
8. Pagination with AsyncNotifier
9. Debounced Search
10. KeepAlive with TTL
11. Global Singleton
12. Optimistic UI Pattern
13. Listen for Side Effects
14. Select (Reduce Rebuilds)

**Lines of code:** ~400 (templates only)

**When to use:** Starting new features, learning patterns.

---

## 🔍 Search Guide

### By Keyword

**Authentication:**
- `examples/auth_with_either.dart`
- `SKILL.md` → "Functional Error Handling"
- `templates/provider_templates.dart` → Template #5, #7

**Chat:**
- `examples/complete_chat_architecture.dart` ⭐
- `SKILL.md` → "Real-Time Chat Architecture"

**Error Handling:**
- `examples/auth_with_either.dart`
- `SKILL.md` → "Functional Error Handling with Either"
- `templates/provider_templates.dart` → Template #7
- `CHEATSHEET.md` → "Functional Error Handling"

**Firebase:**
- `examples/complete_chat_architecture.dart` (Firestore)
- `examples/auth_with_either.dart` (Auth)
- `SKILL.md` → "Real-Time Communication Layer"

**Lifecycle:**
- `data/lifecycle_hooks.json` ⭐
- `SKILL.md` → "Lifecycle Management"
- `CHEATSHEET.md` → "Lifecycle Hooks"

**Memory Management:**
- `examples/video_memory_management.dart` ⭐
- `SKILL.md` → "High-Performance Media Management"
- `data/troubleshooting.json` → "memory_leak_video"

**Migration:**
- `data/migration_map.json` ⭐
- `SKILL.md` → "Migration from Legacy"
- `CHEATSHEET.md` → "Migration from Legacy"

**Pagination:**
- `examples/pagination_pattern.dart` ⭐
- `templates/provider_templates.dart` → Template #8
- `SKILL.md` → "Infinite Scroll Pagination"

**Performance:**
- `data/troubleshooting.json` → "performance_optimization"
- `CHEATSHEET.md` → "Performance Tips"
- `SKILL.md` → "Performance Checklist"

**Search:**
- `templates/provider_templates.dart` → Template #9
- `SKILL.md` → "Search Implementation"
- `CHEATSHEET.md` → "Debounced Search"

**Testing:**
- `INSTALLATION_GUIDE.md` → "Testing Your Providers"
- `CHEATSHEET.md` → "Testing"
- `templates/provider_templates.dart` → End of file

**Troubleshooting:**
- `data/troubleshooting.json` ⭐
- `SKILL.md` → "Common Pitfalls"

**WebSocket:**
- `examples/complete_chat_architecture.dart` ⭐
- `templates/provider_templates.dart` → Template #6
- `SKILL.md` → "Managing Firestore Streams with StreamNotifier"

---

## 📊 Statistics

- **Total Files:** 12
- **Documentation:** 5 MD files (~15,000 words)
- **Data Files:** 3 JSON files (~800 lines structured data)
- **Examples:** 4 Dart files (~1,130 lines production code)
- **Templates:** 1 Dart file (~400 lines reusable patterns)
- **Coverage:**
  - Provider types: 6/6 (100%)
  - Common patterns: 14 templates
  - Real-world examples: 4 complete implementations
  - Error scenarios: 10+ with solutions
  - Lifecycle hooks: 4/4 documented

---

## 🎓 Learning Path

### Beginner (Day 1-3)
1. Read `INSTALLATION_GUIDE.md`
2. Setup project with dependencies
3. Study `CHEATSHEET.md` → Provider Types
4. Copy `templates/provider_templates.dart` → Templates #1-4
5. Practice: Create simple counter, fetch API data

### Intermediate (Day 4-7)
6. Read `SKILL.md` → "Provider Types & Code Generation"
7. Read `SKILL.md` → "Lifecycle Management"
8. Study `examples/auth_with_either.dart`
9. Copy `templates/provider_templates.dart` → Template #7
10. Practice: Build login/logout with Either

### Advanced (Week 2)
11. Read `SKILL.md` → "Real-Time Chat Architecture"
12. Study `examples/complete_chat_architecture.dart`
13. Study `examples/pagination_pattern.dart`
14. Study `examples/video_memory_management.dart`
15. Practice: Build chat with pagination

### Expert (Week 3+)
16. Review `data/lifecycle_hooks.json` → All patterns
17. Implement TTL caching for your use case
18. Optimize with `.select()` and profiling
19. Study `data/troubleshooting.json` for edge cases
20. Build production-ready features

---

## 🆘 Quick Help

**"I don't know where to start"**
→ `INSTALLATION_GUIDE.md`

**"I need quick syntax"**
→ `CHEATSHEET.md`

**"I'm getting an error"**
→ `data/troubleshooting.json`

**"I need a full example"**
→ `examples/` directory

**"I want to understand architecture"**
→ `SKILL.md`

**"I'm migrating old code"**
→ `data/migration_map.json`

---

**This skill contains everything needed for production-grade Riverpod 3.0 development.**
