# Riverpod 3.0 Expert Skill

**Production-grade state management for Flutter with unified Ref, code generation, functional error handling, and real-time architectures.**

---

## 📦 What's Included

```
riverpod-3/
├── SKILL.md                              # Core skill documentation
├── README.md                             # This file
├── data/
│   ├── migration_map.json                # Legacy → 3.0 migration guide
│   └── lifecycle_hooks.json              # Complete lifecycle reference
├── examples/
│   ├── complete_chat_architecture.dart   # Dual-stack Firestore+WebSocket
│   ├── pagination_pattern.dart           # Infinite scroll with AsyncNotifier
│   ├── auth_with_either.dart             # Full auth flow with fpdart
│   └── video_memory_management.dart      # Scoped video controllers
└── templates/
    └── provider_templates.dart           # 14 copy-paste patterns
```

---

## 🚀 Quick Start

### 1. Installation

```yaml
# pubspec.yaml
dependencies:
  flutter_riverpod: ^3.0.0
  riverpod_annotation: ^3.0.0
  fpdart: ^1.1.0

dev_dependencies:
  riverpod_generator: ^3.0.0
  build_runner: ^2.4.0
  riverpod_lint: ^2.5.0
```

### 2. Enable Code Generation

```bash
dart run build_runner watch
```

### 3. Wrap Your App

```dart
void main() {
  runApp(
    ProviderScope(
      child: MyApp(),
    ),
  );
}
```

---

## 📚 Core Concepts

### Unified Ref Interface

**Before (Riverpod 2.x):**
```dart
final provider1 = Provider((ProviderRef ref) => ...);
final provider2 = FutureProvider((FutureProviderRef ref) => ...);
```

**After (Riverpod 3.0):**
```dart
@riverpod String name(Ref ref) => ...;
@riverpod Future<User> user(Ref ref) => ...;
```

**One `Ref` type for all providers.**

---

### Provider Type Selection (Automatic)

| Your Function Returns | Generated Provider |
|-----------------------|--------------------|
| `T` | `Provider<T>` |
| `Future<T>` | `FutureProvider<T>` |
| `Stream<T>` | `StreamProvider<T>` |
| Class extends `Notifier<T>` | `NotifierProvider<T>` |
| Class extends `AsyncNotifier<T>` | `AsyncNotifierProvider<T>` |

---

### Lifecycle Hooks

```dart
@riverpod
Stream<Data> myStream(Ref ref) {
  final stream = createStream();

  ref.onDispose(() {
    // Called when provider destroyed
    stream.close();
  });

  ref.onCancel(() {
    // Called when last listener removed
  });

  ref.onResume(() {
    // Called when listener added after cancel
  });

  return stream;
}
```

**TTL Cache Pattern:**
```dart
@riverpod
Future<Data> cachedData(Ref ref) async {
  final link = ref.keepAlive();
  Timer(Duration(minutes: 5), link.close);

  return fetchData();
}
```

---

## 🏗️ Architectural Patterns

### 1. Functional Error Handling (Either Monad)

**Repository Layer:**
```dart
abstract class AuthRepository {
  Future<Either<AuthFailure, User>> signIn(String email, String password);
}
```

**State Layer:**
```dart
@riverpod
class AuthController extends _$AuthController {
  @override
  Future<User?> build() async => null;

  Future<void> signIn(String email, String password) async {
    state = const AsyncLoading();

    final result = await ref.read(authRepositoryProvider).signIn(email, password);

    state = result.fold(
      (failure) => AsyncError(failure, StackTrace.current),
      (user) => AsyncData(user),
    );
  }
}
```

**UI Layer:**
```dart
final authState = ref.watch(authControllerProvider);

authState.when(
  data: (user) => HomeScreen(user: user),
  error: (error, _) => Text((error as AuthFailure).message),
  loading: () => CircularProgressIndicator(),
);
```

---

### 2. Real-Time Chat (Dual-Stack)

**Firestore Stream (Authoritative):**
```dart
@riverpod
Stream<List<Message>> firestoreMessages(Ref ref, String chatId) {
  return FirebaseFirestore.instance
    .collection('chats/$chatId/messages')
    .snapshots()
    .map((snap) => snap.docs.map(Message.fromFirestore).toList());
}
```

**WebSocket Stream (Ephemeral):**
```dart
@riverpod
Stream<Message> liveMessages(Ref ref) {
  final socket = ref.watch(socketClientProvider);
  final controller = StreamController<Message>();

  socket.on('new_message', (data) => controller.add(Message.fromJson(data)));

  ref.onDispose(() {
    socket.off('new_message');
    controller.close();
  });

  return controller.stream;
}
```

**Optimistic UI (Pending + Server):**
```dart
@riverpod
List<Message> chatTimeline(Ref ref, String chatId) {
  final server = ref.watch(firestoreMessagesProvider(chatId)).valueOrNull ?? [];
  final pending = ref.watch(pendingMessagesProvider(chatId));

  return [...pending, ...server];
}
```

---

### 3. Pagination (Infinite Scroll)

```dart
@riverpod
class MessagePagination extends _$MessagePagination {
  DocumentSnapshot? _lastDoc;
  bool _hasMore = true;

  @override
  Future<List<Message>> build(String chatId) async {
    return _fetchPage(chatId);
  }

  Future<void> loadMore() async {
    if (state.isLoading || !_hasMore) return;

    final current = state.value ?? [];
    state = const AsyncLoading().copyWithPrevious(state);

    state = await AsyncValue.guard(() async {
      final new = await _fetchPage(arg);
      return [...current, ...new];
    });
  }
}
```

**UI Integration:**
```dart
NotificationListener<ScrollNotification>(
  onNotification: (notification) {
    if (notification.metrics.extentAfter < 500) {
      ref.read(messagePaginationProvider(chatId).notifier).loadMore();
    }
    return false;
  },
  child: ListView(...),
)
```

---

### 4. Memory-Safe Video Management

```dart
@riverpod
Future<VideoPlayerController> videoController(Ref ref, String url) async {
  final controller = VideoPlayerController.networkUrl(Uri.parse(url));

  // CRITICAL: Auto-dispose when widget unmounts
  ref.onDispose(() => controller.dispose());

  await controller.initialize();
  return controller;
}
```

**Result:** When user scrolls video off-screen → widget unmounts → provider disposes → controller releases native memory.

---

### 5. Debounced Search

```dart
@riverpod
Future<List<Result>> search(Ref ref, String query) async {
  if (query.isEmpty) return [];

  final client = http.Client();
  ref.onDispose(() => client.close()); // Cancel on query change

  await Future.delayed(Duration(milliseconds: 500));

  final response = await client.get(Uri.parse('...?q=$query'));
  return parseResults(response.body);
}
```

**Mechanism:** New query → new provider instance → old instance disposed → HTTP request cancelled.

---

## 🔄 Migration from Legacy Riverpod

| Legacy | Riverpod 3.0 |
|--------|--------------|
| `StateNotifier` | `Notifier` |
| `StateNotifierProvider` | `NotifierProvider` (auto-generated) |
| `ChangeNotifier` | Avoid (use `AsyncNotifier`) |
| `StateProvider` | `Notifier` for logic |
| `Provider.family((ref, arg))` | `@riverpod T name(Ref ref, String arg)` |
| Constructor logic | `build()` method |

**See `data/migration_map.json` for detailed mappings.**

---

## 🎯 Common Pitfalls & Solutions

| Problem | Solution |
|---------|----------|
| Memory leak with VideoController | Use scoped provider with `ref.onDispose` |
| "Provider was disposed" error | Use `keepAlive()` or TTL cache |
| Too many rebuilds | Use `.select()` to watch specific fields |
| Search too many requests | Debounce with `ref.onDispose` cancellation |
| Firestore costs too high | TTL cache with `keepAlive` for 5min |
| AsyncValue loading on refresh | Use `copyWithPrevious(state)` |

---

## 📖 Example Implementations

### Chat Architecture
See `examples/complete_chat_architecture.dart` for:
- Dual-stack Firestore + WebSocket
- Optimistic UI with pending state
- Message sending with Either error handling
- Real-time sync with TTL caching

### Authentication
See `examples/auth_with_either.dart` for:
- Repository pattern with Either monad
- AsyncNotifier for auth state
- Firebase integration
- Error handling with domain failures

### Pagination
See `examples/pagination_pattern.dart` for:
- Reverse pagination for chat
- ScrollNotification listener
- Error-preserving state updates
- Pull-to-refresh

### Video Management
See `examples/video_memory_management.dart` for:
- Scoped VideoPlayerController
- Automatic disposal on unmount
- TTL cache for recent videos
- Interactive controls with Notifier

---

## 🛠️ Templates

See `templates/provider_templates.dart` for 14 ready-to-use patterns:

1. Simple Provider (DI)
2. Future Provider (REST)
3. Stream Provider (Firestore)
4. Notifier (Sync State)
5. AsyncNotifier (Async Actions)
6. StreamNotifier (WebSocket)
7. Repository with Either
8. Pagination
9. Debounced Search
10. TTL Cache
11. Global Singleton
12. Optimistic UI
13. Listen for Side Effects
14. Select for Performance

---

## 🧪 Testing

### Override Providers

```dart
testWidgets('Test', (tester) async {
  await tester.pumpWidget(
    ProviderScope(
      overrides: [
        authRepositoryProvider.overrideWithValue(MockAuthRepository()),
      ],
      child: MyApp(),
    ),
  );
});
```

### Test AsyncNotifier

```dart
test('Counter increments', () async {
  final container = ProviderContainer();
  final notifier = container.read(counterProvider.notifier);

  notifier.increment();

  expect(container.read(counterProvider), 1);
});
```

---

## 📊 Performance Checklist

- [ ] All providers use `@riverpod` code generation
- [ ] No legacy StateNotifier/ChangeNotifier
- [ ] Video/Image controllers scoped to providers
- [ ] Expensive streams use `keepAlive` with TTL
- [ ] UI uses `.select()` for granular watching
- [ ] Search implements debounce + cancellation
- [ ] Pagination preserves data during loading
- [ ] Either monad for all repository errors
- [ ] `riverpod_lint` enabled

---

## 📚 Resources

- [Official Riverpod Docs](https://riverpod.dev)
- [fpdart Documentation](https://pub.dev/packages/fpdart)
- [Code Generation Guide](https://riverpod.dev/docs/concepts/about_code_generation)

---

## 🤝 Usage

This skill is designed to be used with Claude Code/Cowork mode. Simply reference patterns from:
- `SKILL.md` - Core documentation
- `examples/` - Full implementations
- `templates/` - Quick copy-paste patterns
- `data/` - Structured reference data

**Triggers:** riverpod, state management, provider, notifier, asyncnotifier, streamnotifier, real-time chat, pagination, functional error handling

---

**Created for production Flutter applications requiring scalable, maintainable, and performant state management.**
