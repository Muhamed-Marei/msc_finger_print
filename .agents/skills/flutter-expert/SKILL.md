---
name: flutter-expert
description: |
  Flutter Expert - Unified auto-routing agent. Detects context, applies expertise, auto-fixes errors, learns solutions.
  TRIGGERS: flutter, dart, widget, riverpod, provider, firebase, firestore, ios, android, xcode, gradle, api, dio, http, test, mock, build, deploy, error, exception, failed, crash, pubspec, package, state, navigation, go_router, performance
  AUTO: Activates on any Flutter-related query or error. No commands needed.
---

# Flutter Expert

Auto-routing unified agent. Detects context → applies expertise → fixes errors → learns.

## Auto Mode Selection

| Context Detected | Mode | Action |
|------------------|------|--------|
| Error/Exception/Failed | FIX | Search errors.json → apply fix |
| Question/How to | GUIDE | Compact answer with code |
| Build/Create | BUILD | Architecture + code |
| Review/Check | REVIEW | Analyze + suggest |

## Error Auto-Fix

On error detected → scan `data/errors.json` → return fix or diagnose new.

## Core Stack
```yaml
flutter_riverpod: ^3.2.0    # State
go_router: ^17.0.1          # Navigation  
dio: ^5.9.0                 # Network
freezed: ^3.2.4             # Models
get_it: ^9.2.0              # DI
firebase_core: ^4.4.0       # Firebase
```

## Architecture
```
lib/
├── core/           # Shared
├── features/[name]/
│   ├── data/       # Models, repos, sources
│   ├── domain/     # Entities, interfaces, usecases
│   └── presentation/ # ViewModels, UI
```

## Quick Patterns

**Provider:**
```dart
@riverpod
class Items extends _$Items {
  @override
  Future<List<Item>> build() async => _repo.getAll();
  void add(Item i) async { await _repo.add(i); ref.invalidateSelf(); }
}
```

**Repository:**
```dart
Future<Either<Failure, T>> call() async {
  try { return Right(await remote.fetch()); }
  catch (e) { return Left(ServerFailure()); }
}
```

## Commands
```bash
flutter clean && flutter pub get           # Clean
dart run build_runner build -d             # Generate
cd ios && pod deintegrate && pod install   # iOS fix
cd android && ./gradlew clean              # Android fix
```

## Domain Routing

Context | Route to
--------|----------
`ios\|pod\|xcode\|signing\|plist` | iOS specifics → references/ios.md
`android\|gradle\|manifest\|apk` | Android specifics → references/android.md
`error\|exception\|failed\|crash` | Error lookup → data/errors.json
`pubspec\|package\|version\|dependency` | Versions → data/versions.json

## Self-Learning

New error solved → append to `data/errors.json`:
```json
{"pattern": "error text", "fix": "solution", "category": "type"}
```
