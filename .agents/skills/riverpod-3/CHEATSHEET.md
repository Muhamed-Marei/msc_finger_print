# Riverpod 3.0 Cheatsheet

## 🚀 Quick Reference

### Provider Types

| Return Type | Generated | Use Case |
|------------|-----------|----------|
| `T` | `Provider<T>` | DI, config, singletons |
| `Future<T>` | `FutureProvider<T>` | REST API calls |
| `Stream<T>` | `StreamProvider<T>` | Firestore, WebSocket |
| `Notifier<T>` | `NotifierProvider<T>` | Sync mutable state |
| `AsyncNotifier<T>` | `AsyncNotifierProvider<T>` | Async actions (auth, CRUD) |
| `StreamNotifier<T>` | `StreamNotifierProvider<T>` | Stream with control (Socket.io) |

---

### Code Generation Syntax

```dart
// Simple value
@riverpod
String appName(Ref ref) => 'MyApp';

// Dependency injection
@riverpod
Dio httpClient(Ref ref) => Dio(BaseOptions(baseUrl: '...'));

// Future (REST API)
@riverpod
Future<User> user(Ref ref, {required int id}) async {
  final dio = ref.watch(httpClientProvider);
  return User.fromJson(await dio.get('/users/$id'));
}

// Stream (Firestore)
@riverpod
Stream<List<Message>> messages(Ref ref, String chatId) {
  return FirebaseFirestore.instance
    .collection('chats/$chatId/messages')
    .snapshots()
    .map((snap) => snap.docs.map(Message.fromFirestore).toList());
}

// Notifier (sync state)
@riverpod
class Counter extends _$Counter {
  @override
  int build() => 0;

  void increment() => state++;
}

// AsyncNotifier (async actions)
@riverpod
class Auth extends _$Auth {
  @override
  Future<User?> build() async => fetchCurrentUser();

  Future<void> signIn(String email, String password) async {
    state = const AsyncLoading();
    state = await AsyncValue.guard(() => performSignIn(email, password));
  }
}
```

---

### Lifecycle Hooks

```dart
@riverpod
Stream<Data> myProvider(Ref ref) {
  // Dispose resources
  ref.onDispose(() => resource.close());

  // Last listener removed (not disposed yet)
  ref.onCancel(() => print('Paused'));

  // Listener added after cancel
  ref.onResume(() => print('Resumed'));

  // Prevent disposal
  final link = ref.keepAlive();
  Timer(Duration(minutes: 5), link.close); // TTL cache

  return stream;
}
```

---

### Ref API

```dart
// Read once (doesn't listen)
final value = ref.read(userProvider);

// Watch (rebuilds on change)
final user = ref.watch(userProvider);

// Watch specific field (reduce rebuilds)
final name = ref.watch(userProvider.select((u) => u.name));

// Listen for side effects (SnackBar, navigation)
ref.listen(authProvider, (previous, next) {
  next.whenData((user) => showWelcome(user));
});

// Invalidate (force refresh)
ref.invalidate(userProvider);

// Refresh (rebuild provider)
ref.refresh(userProvider);
```

---

### AsyncValue Pattern Matching

```dart
final asyncValue = ref.watch(userProvider);

// Dart 3 pattern matching
return switch (asyncValue) {
  AsyncData(:final value) => UserWidget(value),
  AsyncError(:final error) => ErrorWidget(error),
  _ => LoadingWidget(),
};

// Traditional when
return asyncValue.when(
  data: (user) => UserWidget(user),
  loading: () => LoadingWidget(),
  error: (error, stack) => ErrorWidget(error),
);

// Preserve data while loading
if (asyncValue.isReloading) {
  // Show data + spinner
}
```

---

### Functional Error Handling

```dart
// Domain failures
sealed class Failure {}
class NetworkFailure extends Failure {}
class NotFoundFailure extends Failure {}

// Repository returns Either
Future<Either<Failure, User>> getUser(int id) async {
  try {
    final response = await dio.get('/users/$id');
    return right(User.fromJson(response.data));
  } catch (e) {
    return left(NetworkFailure());
  }
}

// Notifier consumes Either
Future<void> fetchUser(int id) async {
  state = const AsyncLoading();

  final result = await repository.getUser(id);

  state = result.fold(
    (failure) => AsyncError(failure, StackTrace.current),
    (user) => AsyncData(user),
  );
}
```

---

### Common Patterns

#### Optimistic UI
```dart
// Pending state
@riverpod
class Pending extends _$Pending {
  @override
  List<Item> build() => [];
  void add(Item item) => state = [...state, item];
  void remove(String id) => state = state.where((i) => i.id != id).toList();
}

// Server state
@riverpod
Future<List<Item>> serverItems(Ref ref) async => fetchItems();

// Merged UI state
@riverpod
List<Item> allItems(Ref ref) {
  final server = ref.watch(serverItemsProvider).valueOrNull ?? [];
  final pending = ref.watch(pendingProvider);
  return [...pending, ...server];
}
```

#### Pagination
```dart
@riverpod
class Pagination extends _$Pagination {
  int _page = 0;
  bool _hasMore = true;

  @override
  Future<List<Item>> build() async {
    _page = 0;
    return _fetchPage();
  }

  Future<void> loadMore() async {
    if (state.isLoading || !_hasMore) return;

    final current = state.value ?? [];
    state = const AsyncLoading().copyWithPrevious(state);

    state = await AsyncValue.guard(() async {
      _page++;
      final newItems = await _fetchPage();
      return [...current, ...newItems];
    });
  }
}
```

#### Debounced Search
```dart
@riverpod
Future<List<Result>> search(Ref ref, String query) async {
  if (query.isEmpty) return [];

  final client = http.Client();
  ref.onDispose(() => client.close()); // Cancel on query change

  await Future.delayed(Duration(milliseconds: 500)); // Debounce

  final response = await client.get(Uri.parse('...?q=$query'));
  return parseResults(response.body);
}
```

#### Video Controller (Memory Safe)
```dart
@riverpod
Future<VideoPlayerController> video(Ref ref, String url) async {
  final controller = VideoPlayerController.networkUrl(Uri.parse(url));

  ref.onDispose(() => controller.dispose()); // Auto-dispose

  await controller.initialize();
  return controller;
}
```

#### TTL Cache
```dart
@riverpod
Future<Data> cached(Ref ref) async {
  final link = ref.keepAlive();
  Timer(Duration(minutes: 5), link.close); // Dispose after 5min

  return fetchExpensiveData();
}
```

---

### UI Widgets

```dart
// ConsumerWidget (stateless)
class MyWidget extends ConsumerWidget {
  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final user = ref.watch(userProvider);
    return Text(user.name);
  }
}

// ConsumerStatefulWidget
class MyWidget extends ConsumerStatefulWidget {
  @override
  ConsumerState<MyWidget> createState() => _MyWidgetState();
}

class _MyWidgetState extends ConsumerState<MyWidget> {
  @override
  Widget build(BuildContext context) {
    final user = ref.watch(userProvider);
    return Text(user.name);
  }
}

// Consumer (for specific subtree)
Consumer(
  builder: (context, ref, child) {
    final user = ref.watch(userProvider);
    return Text(user.name);
  },
)
```

---

### Testing

```dart
// Unit test
test('Counter increments', () {
  final container = ProviderContainer();
  addTearDown(container.dispose);

  container.read(counterProvider.notifier).increment();

  expect(container.read(counterProvider), 1);
});

// Widget test with mocks
testWidgets('Test', (tester) async {
  await tester.pumpWidget(
    ProviderScope(
      overrides: [
        userRepositoryProvider.overrideWithValue(MockRepository()),
      ],
      child: MyApp(),
    ),
  );
});
```

---

### Migration from Legacy

| Legacy | Riverpod 3.0 |
|--------|--------------|
| `StateNotifier` | `Notifier` |
| `StateNotifierProvider` | `NotifierProvider` (generated) |
| `ChangeNotifier` | Avoid (use `AsyncNotifier`) |
| `StateProvider` | `Notifier` |
| `Provider.family` | Function parameters |
| Constructor logic | `build()` method |

---

### Build Commands

```bash
# Watch mode (recommended)
dart run build_runner watch --delete-conflicting-outputs

# One-time build
dart run build_runner build --delete-conflicting-outputs

# Clean build
dart run build_runner clean
dart run build_runner build --delete-conflicting-outputs
```

---

### Common Mistakes

❌ **Wrong:**
```dart
// Using ref.watch in async gap
Future<void> fetch() async {
  await Future.delayed(Duration(seconds: 1));
  final user = ref.watch(userProvider); // ERROR
}

// Not disposing controller
final controller = VideoPlayerController.network(url);
// Missing: ref.onDispose(() => controller.dispose());

// Watching full object
final user = ref.watch(userProvider);
final name = user.name; // Rebuilds on ANY field change
```

✅ **Correct:**
```dart
// Read ref BEFORE async
Future<void> fetch() async {
  final user = ref.watch(userProvider);
  await Future.delayed(Duration(seconds: 1));
}

// Auto-dispose controller
@riverpod
Future<VideoPlayerController> video(Ref ref, String url) async {
  final controller = VideoPlayerController.network(url);
  ref.onDispose(() => controller.dispose());
  await controller.initialize();
  return controller;
}

// Select specific field
final name = ref.watch(userProvider.select((u) => u.name));
```

---

### Performance Tips

1. ✅ Use `.select()` to watch specific fields
2. ✅ Implement `==` operator on models
3. ✅ Use `copyWithPrevious(state)` for pagination
4. ✅ Scope video controllers to providers
5. ✅ Use TTL caching for expensive streams
6. ✅ Enable `riverpod_lint`
7. ❌ Don't use legacy providers
8. ❌ Don't watch entire objects unnecessarily

---

**For full documentation, see `SKILL.md` and examples in `examples/`**
