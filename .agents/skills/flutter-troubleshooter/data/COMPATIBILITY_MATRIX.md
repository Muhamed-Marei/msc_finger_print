# Flutter Package Compatibility Matrix

> Last Updated: January 2026

## Verified Working Combinations

### ✅ Tested Stack (January 2026)

| Package | Version | Requires | Notes |
|---------|---------|----------|-------|
| **Flutter SDK** | 3.24.0+ | Dart 3.5+ | Minimum for this stack |
| **Dart SDK** | 3.5.0+ | - | Required for latest packages |

### State Management

| Package | Version | Compatible With | Breaking Changes |
|---------|---------|-----------------|------------------|
| flutter_riverpod | 3.2.0 | Dart 3.5+, Flutter 3.22+ | StateNotifierProvider moved to legacy.dart |
| riverpod_annotation | 4.0.1 | flutter_riverpod 3.x | New Ref type, removed UserRef |
| riverpod_generator | 4.0.1 | riverpod_annotation 4.x | Must match annotation version |

### Navigation

| Package | Version | Compatible With | Breaking Changes |
|---------|---------|-----------------|------------------|
| go_router | 17.0.1 | Flutter 3.22+ | shellRoute API changes |

### Networking

| Package | Version | Compatible With | Breaking Changes |
|---------|---------|-----------------|------------------|
| dio | 5.9.0 | Dart 3.3+ | None major |
| retrofit | 4.9.2 | dio 5.x | Generator version must match |
| retrofit_generator | 9.1.8 | retrofit 4.9.x | - |

### Serialization

| Package | Version | Compatible With | Breaking Changes |
|---------|---------|-----------------|------------------|
| freezed | 3.2.4 | Dart 3.5+ | copyWith signature changed |
| freezed_annotation | 3.1.0 | freezed 3.x | - |
| json_serializable | 6.11.4 | json_annotation 4.9+ | - |
| json_annotation | 4.9.0 | - | - |

### Dependency Injection

| Package | Version | Compatible With | Breaking Changes |
|---------|---------|-----------------|------------------|
| get_it | 9.2.0 | Dart 3.0+ | None major |
| injectable | 2.7.1 | get_it 9.x | - |
| injectable_generator | 2.7.1 | injectable 2.7.x | Must match |

### Firebase (All Must Update Together!)

| Package | Version | firebase_core | Notes |
|---------|---------|---------------|-------|
| firebase_core | 4.4.0 | - | Base requirement |
| firebase_auth | 6.1.4 | 4.x | - |
| cloud_firestore | 6.1.2 | 4.x | - |
| firebase_storage | 13.0.6 | 4.x | - |
| firebase_messaging | 16.1.1 | 4.x | - |
| firebase_analytics | 12.1.1 | 4.x | - |
| firebase_crashlytics | 5.0.7 | 4.x | - |

### Local Storage

| Package | Version | Compatible With | Notes |
|---------|---------|-----------------|-------|
| hive | 2.2.3 | Dart 3.0+ | Stable, recommended |
| hive_flutter | 1.1.0 | hive 2.x | - |
| isar | 3.1.0 | Dart 3.0+ | More features, larger size |

### UI & Utilities

| Package | Version | Compatible With | Notes |
|---------|---------|-----------------|-------|
| cached_network_image | 3.4.1 | Flutter 3.10+ | - |
| flutter_svg | 2.0.10 | Flutter 3.10+ | - |
| connectivity_plus | 7.0.0 | Flutter 3.22+ | API changed from 6.x |
| permission_handler | 12.0.1 | Flutter 3.10+ | - |

---

## Known Incompatibilities

### ❌ DO NOT MIX

| Combination | Problem | Solution |
|-------------|---------|----------|
| riverpod 2.x + riverpod_annotation 4.x | API mismatch | Use riverpod 3.x |
| freezed 2.x + freezed 3.x in same project | Generated code conflicts | Pick one version |
| firebase_* 3.x + firebase_core 4.x | Version mismatch | Update all Firebase packages |
| go_router 14.x + Flutter 3.10 | Missing APIs | Update Flutter or downgrade go_router |

### ⚠️ Requires Dependency Override

| Scenario | Override Needed |
|----------|-----------------|
| Riverpod 3.x + Flutter < 3.16 | `collection: ^1.18.0` |

---

## Flutter Version Requirements

| Flutter Version | Minimum Dart | Compatible Stack |
|-----------------|--------------|------------------|
| 3.24.0+ | 3.5.0 | Full 2026 stack ✅ |
| 3.22.0 | 3.4.0 | Most packages work |
| 3.19.0 | 3.3.0 | Limited - downgrade riverpod |
| < 3.16.0 | < 3.3.0 | Not recommended |

---

## Upgrade Path

### From Riverpod 2.x to 3.x

1. Update versions in pubspec.yaml
2. Change `UserRef ref` to `Ref ref` in providers
3. Move StateNotifierProvider imports to `legacy.dart`
4. Run code generator
5. Test thoroughly

### From Freezed 2.x to 3.x

1. Update versions
2. Delete all `.freezed.dart` and `.g.dart` files
3. Run `dart run build_runner build --delete-conflicting-outputs`
4. Check copyWith usage for breaking changes

### From Firebase 3.x to 4.x

1. Update ALL Firebase packages together
2. Check FlutterFire documentation for API changes
3. Update iOS/Android configurations
4. Test on both platforms

---

## Version Lock File

For guaranteed compatibility, use these exact versions:

```yaml
# LOCKED VERSIONS - January 2026
flutter_riverpod: 3.2.0
riverpod_annotation: 4.0.1
go_router: 17.0.1
dio: 5.9.0
retrofit: 4.9.2
freezed: 3.2.4
freezed_annotation: 3.1.0
json_serializable: 6.11.4
get_it: 9.2.0
injectable: 2.7.1
firebase_core: 4.4.0
```

Use caret (^) for flexibility or exact version for stability.
