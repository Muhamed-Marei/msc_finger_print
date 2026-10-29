# Riverpod 3.0 Skill - Installation & Usage Guide

## 📍 Installing This Skill

This skill has been created in `/sessions/happy-exciting-babbage/mnt/outputs/riverpod-3/`.

To use it as a permanent skill in your Claude environment:

### Option 1: Copy to Skills Directory (If Writable)
```bash
cp -r riverpod-3 ~/.skills/skills/
```

### Option 2: Reference from Current Location
Keep the skill in your outputs folder and reference it when needed.

---

## 📂 Skill Structure

```
riverpod-3/
├── SKILL.md                              # Main skill documentation (use this!)
├── README.md                             # Overview and quick reference
├── INSTALLATION_GUIDE.md                 # This file
│
├── data/                                 # Structured reference data
│   ├── migration_map.json                # Legacy → Riverpod 3.0 mappings
│   ├── lifecycle_hooks.json              # Complete lifecycle API reference
│   └── troubleshooting.json              # Common errors and solutions
│
├── examples/                             # Production-ready implementations
│   ├── complete_chat_architecture.dart   # Full chat with Firestore + WebSocket
│   ├── pagination_pattern.dart           # Infinite scroll with AsyncNotifier
│   ├── auth_with_either.dart             # Authentication with fpdart Either
│   └── video_memory_management.dart      # Memory-safe video controllers
│
└── templates/                            # Copy-paste patterns
    └── provider_templates.dart           # 14 ready-to-use provider patterns
```

---

## 🚀 Quick Start for Your Flutter Project

### 1. Add Dependencies

```yaml
# pubspec.yaml
dependencies:
  flutter_riverpod: ^3.0.0
  riverpod_annotation: ^3.0.0
  fpdart: ^1.1.0  # For functional error handling

dev_dependencies:
  riverpod_generator: ^3.0.0
  build_runner: ^2.4.0
  riverpod_lint: ^2.5.0  # Highly recommended
  custom_lint: ^0.6.0    # Required for riverpod_lint
```

### 2. Enable Linting

```yaml
# analysis_options.yaml
include: package:flutter_lints/flutter.yaml

analyzer:
  plugins:
    - custom_lint
```

### 3. Start Code Generation

```bash
# Watch mode (recommended during development)
dart run build_runner watch --delete-conflicting-outputs

# One-time build
dart run build_runner build --delete-conflicting-outputs
```

### 4. Wrap Your App

```dart
// main.dart
import 'package:flutter_riverpod/flutter_riverpod.dart';

void main() {
  runApp(
    ProviderScope(  // Required root container
      child: MyApp(),
    ),
  );
}
```

---

## 📖 How to Use This Skill

### Reading the Documentation

**Start here:** `SKILL.md`
- Core architectural principles
- Complete provider type reference
- Lifecycle management patterns
- Code generation syntax
- Real-time architecture patterns

**Quick reference:** `README.md`
- Installation steps
- Migration guide
- Performance checklist
- Links to examples

### Using the Examples

Each example is **production-ready** and demonstrates a complete pattern:

**1. Chat Architecture** (`examples/complete_chat_architecture.dart`)
- Dual-stack Firestore + WebSocket
- Optimistic UI with pending/server state merge
- Message sending with Either error handling
- Real-time sync with TTL caching

**2. Pagination** (`examples/pagination_pattern.dart`)
- Reverse pagination for chat history
- Scroll detection with NotificationListener
- Error-preserving state updates
- Pull-to-refresh implementation

**3. Authentication** (`examples/auth_with_either.dart`)
- Repository pattern returning `Either<Failure, Success>`
- AsyncNotifier for auth controller
- Firebase integration
- Domain-driven error types

**4. Video Management** (`examples/video_memory_management.dart`)
- Scoped VideoPlayerController (automatic disposal)
- TTL caching for recently viewed videos
- Interactive playback controls
- Memory monitoring utilities

### Using the Templates

`templates/provider_templates.dart` contains 14 copy-paste patterns:

1. **Simple Provider** - Dependency injection (Dio, repositories)
2. **Future Provider** - REST API calls
3. **Stream Provider** - Firestore streams
4. **Notifier** - Synchronous mutable state
5. **AsyncNotifier** - Asynchronous actions
6. **StreamNotifier** - WebSocket bridge
7. **Repository with Either** - Functional error handling
8. **Pagination** - Infinite scroll with state preservation
9. **Debounced Search** - Search-as-you-type with cancellation
10. **TTL Cache** - Time-to-live memory management
11. **Global Singleton** - App-wide services
12. **Optimistic UI** - Pending + server state merge
13. **Listen** - Side effects (SnackBars, navigation)
14. **Select** - Performance optimization

**Usage:**
1. Copy the relevant template
2. Replace placeholder types (User, Todo, etc.)
3. Add your business logic
4. Run `dart run build_runner build`

### Using the Data Files

**migration_map.json** - Quick lookup for converting legacy code:
```json
{
  "StateNotifier": {
    "target": "Notifier",
    "pattern": "@riverpod class Name extends _$Name",
    "key_change": "Logic moves from constructor to build() method"
  }
}
```

**lifecycle_hooks.json** - Complete reference for all lifecycle methods:
- `ref.onDispose` - When to use, examples
- `ref.onCancel` - When to use, examples
- `ref.onResume` - When to use, examples
- `ref.keepAlive` - TTL cache patterns

**troubleshooting.json** - Solutions for common errors:
- Provider was disposed
- Memory leaks with video
- Excessive rebuilds
- Search too many requests
- Firestore read costs
- AsyncLoading flicker
- And more...

---

## 🎯 Common Workflows

### Creating a New Feature

1. **Define domain models**
   ```dart
   class User {
     final String id;
     final String name;
     const User({required this.id, required this.name});
   }
   ```

2. **Create repository (with Either)**
   ```dart
   abstract class UserRepository {
     Future<Either<Failure, User>> getUser(String id);
   }
   ```

3. **Implement repository**
   ```dart
   @riverpod
   UserRepository userRepository(Ref ref) => ApiUserRepository(
     dio: ref.watch(httpClientProvider),
   );
   ```

4. **Create state provider**
   ```dart
   @riverpod
   Future<User> user(Ref ref, {required String userId}) async {
     final repository = ref.watch(userRepositoryProvider);
     final result = await repository.getUser(userId);

     return result.fold(
       (failure) => throw failure,
       (user) => user,
     );
   }
   ```

5. **Use in UI**
   ```dart
   class UserScreen extends ConsumerWidget {
     @override
     Widget build(BuildContext context, WidgetRef ref) {
       final userAsync = ref.watch(userProvider(userId: '123'));

       return userAsync.when(
         data: (user) => Text(user.name),
         loading: () => CircularProgressIndicator(),
         error: (e, st) => Text('Error: ${e.message}'),
       );
     }
   }
   ```

### Migrating Legacy Code

1. **Identify provider type** (check `data/migration_map.json`)
2. **Copy relevant template** from `templates/provider_templates.dart`
3. **Replace with code generation syntax**
4. **Move constructor logic to build() method**
5. **Run build_runner**

### Debugging Performance Issues

1. **Check `data/troubleshooting.json`** for your symptom
2. **Add lifecycle logging**
   ```dart
   ref.onDispose(() => debugPrint('Provider disposed'));
   ```
3. **Use select() for granular watching**
   ```dart
   ref.watch(userProvider.select((u) => u.name))
   ```
4. **Enable ProviderObserver** for global monitoring

---

## 🧪 Testing Your Providers

### Unit Testing

```dart
import 'package:flutter_test/flutter_test.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

void main() {
  test('Counter increments', () {
    final container = ProviderContainer();
    addTearDown(container.dispose);

    expect(container.read(counterProvider), 0);

    container.read(counterProvider.notifier).increment();

    expect(container.read(counterProvider), 1);
  });
}
```

### Widget Testing with Overrides

```dart
testWidgets('Login test', (tester) async {
  await tester.pumpWidget(
    ProviderScope(
      overrides: [
        authRepositoryProvider.overrideWithValue(MockAuthRepository()),
      ],
      child: MyApp(),
    ),
  );

  // Test interactions...
});
```

---

## 📊 Performance Best Practices

✅ **DO:**
- Use `@riverpod` code generation for all providers
- Implement `==` operator on domain models
- Use `.select()` when watching specific fields
- Scope video/image controllers to providers
- Use TTL caching for expensive Firestore streams
- Preserve data during pagination (`copyWithPrevious`)
- Return `Either<Failure, Success>` from repositories

❌ **DON'T:**
- Use legacy StateNotifier/ChangeNotifier
- Watch entire objects when only one field needed
- Create video controllers in StatefulWidget
- Skip error handling in repositories
- Use `setState` in StatefulWidget for server state
- Call `ref.watch` inside async gaps

---

## 🔗 Additional Resources

- [Riverpod Official Docs](https://riverpod.dev)
- [Code Generation Guide](https://riverpod.dev/docs/concepts/about_code_generation)
- [fpdart Package](https://pub.dev/packages/fpdart)
- [Firebase + Riverpod Best Practices](https://riverpod.dev/docs/cookbooks/testing)

---

## 🆘 Getting Help

1. **Check `SKILL.md`** for architectural patterns
2. **Search `data/troubleshooting.json`** for your error
3. **Review relevant example** in `examples/`
4. **Copy template** from `templates/provider_templates.dart`
5. **Ask Claude** with context from this skill

---

**This skill is designed for production Flutter applications requiring scalable, maintainable, and performant state management with Riverpod 3.0.**
