---
name: riverpod-3
description: |
  Riverpod 3.0 Expert - Production-grade state management with unified Ref, code generation, lifecycle control, functional error handling, and real-time architectures.
  TRIGGERS: riverpod, state management, provider, notifier, asyncnotifier, streamnotifier, ref, lifecycle, keepalive, autodispose, fpdart, either, firebase stream, websocket, real-time chat, optimistic ui, pagination, infinite scroll, onesignal
  AUTO: Activates on Riverpod 3.0 implementation, migration from legacy providers, or complex state management architecture
---

# Riverpod 3.0 Expert

Senior Flutter architect specializing in Riverpod 3.0's unified provider system, functional error handling, and production-grade real-time architectures.

## Auto Mode Selection

| Context | Action |
|---------|--------|
| "StateNotifier" mentioned | Migrate to Notifier pattern |
| "ChangeNotifier" used | Recommend AsyncNotifier with code generation |
| "memory leak" + video/image | Implement scoped autoDispose controllers |
| "real-time chat" | Deploy dual-stack architecture (Firestore + WebSocket) |
| "optimistic ui" | Implement pending/server state merge pattern |
| "search" + debounce | Use ref.onDispose cancellation pattern |
| "notification" + navigation | Bridge OneSignal with event stream provider |
| "infinite scroll" | AsyncNotifier pagination pattern |
| Error handling needed | Integrate Either<Failure, Success> with fpdart |

---

## Core Architecture Principles

1. **Unified Ref Interface** - Single Ref type for all providers
2. **Code Generation First** - Use @riverpod for all providers
3. **Notifier-First** - No legacy StateNotifier/ChangeNotifier
4. **Lifecycle Precision** - Explicit autoDispose, keepAlive, onDispose
5. **Functional Errors** - Either monad, never throw in repositories
6. **Scoped Resources** - Bind VideoController/ImageCache to provider lifecycle

---

## Installation & Setup

```yaml
# pubspec.yaml
dependencies:
  flutter_riverpod: ^3.0.0
  riverpod_annotation: ^3.0.0
  fpdart: ^1.1.0  # Functional error handling

dev_dependencies:
  riverpod_generator: ^3.0.0
  build_runner: ^2.4.0
  riverpod_lint: ^2.5.0  # Essential for best practices
```

```dart
// main.dart
void main() {
  runApp(
    ProviderScope(  // Root container
      child: MyApp(),
    ),
  );
}
```

---

## Provider Types & Code Generation

| Return Type | Generated Provider | Use Case |
|-------------|-------------------|----------|
| `T` | `Provider<T>` | Sync values, DI (Dio, Repositories) |
| `Future<T>` | `FutureProvider<T>` | One-time async fetch (REST API) |
| `Stream<T>` | `StreamProvider<T>` | Continuous data (Firestore, WebSocket) |
| `Notifier<T>` | `NotifierProvider<T>` | Sync mutable state (counter, form) |
| `AsyncNotifier<T>` | `AsyncNotifierProvider<T>` | Async mutable state (auth, pagination) |
| `StreamNotifier<T>` | `StreamNotifierProvider<T>` | Stream with imperative control (Socket.io) |

### Syntax Patterns

```dart
// Simple Provider (DI)
@riverpod
Dio httpClient(Ref ref) => Dio(BaseOptions(baseUrl: 'https://api.app'));

// Future Provider (REST API)
@riverpod
Future<User> user(Ref ref, {required int id}) async {
  final dio = ref.watch(httpClientProvider);
  final response = await dio.get('/users/$id');
  return User.fromJson(response.data);
}

// Stream Provider (Firestore)
@riverpod
Stream<List<Message>> firestoreMessages(Ref ref, String chatId) {
  final firestore = ref.watch(firebaseFirestoreProvider);
  return firestore
    .collection('chats/$chatId/messages')
    .orderBy('createdAt', descending: true)
    .snapshots()
    .map((snap) => snap.docs.map((d) => Message.fromFirestore(d)).toList());
}

// Notifier (Sync State)
@riverpod
class Counter extends _$Counter {
  @override
  int build() => 0;  // Initial state in build()

  void increment() {
    state++;
    ref.read(analyticsProvider).log('incremented');
  }
}

// AsyncNotifier (Async State + Actions)
@riverpod
class AuthController extends _$AuthController {
  @override
  Future<User?> build() async {
    // Initialization: check persisted auth
    final token = await ref.watch(secureStorageProvider).read('token');
    return token != null ? await _verifyToken(token) : null;
  }

  Future<void> signIn(String email, String password) async {
    state = const AsyncLoading();

    final repository = ref.read(authRepositoryProvider);
    final result = await repository.signIn(email, password);

    state = result.fold(
      (failure) => AsyncError(failure, StackTrace.current),
      (user) => AsyncData(user),
    );
  }
}

// StreamNotifier (WebSocket Bridge)
@riverpod
class SocketMessages extends _$SocketMessages {
  @override
  Stream<Message> build() {
    final socket = ref.watch(socketClientProvider);
    final controller = StreamController<Message>();

    void onMessage(dynamic data) {
      try {
        controller.add(Message.fromJson(data));
      } catch (e) {
        ref.read(errorLoggerProvider).log(e);
      }
    }

    socket.on('new_message', onMessage);

    ref.onDispose(() {
      socket.off('new_message', onMessage);
      controller.close();
    });

    return controller.stream;
  }
}
```

**Generate Code:**
```bash
dart run build_runner build --delete-conflicting-outputs
# Or watch mode:
dart run build_runner watch
```

---

## Lifecycle Management

### AutoDispose (Default in Codegen)

```dart
// Auto-disposes when last listener removed
@riverpod
Future<Data> autoData(Ref ref) async => fetchData();
```

### KeepAlive (Prevent Disposal)

```dart
// Never disposes (global singleton)
@Riverpod(keepAlive: true)
SocketClient socketClient(Ref ref) => SocketClient();

// Conditional TTL cache (5-minute memory)
@riverpod
Future<List<Message>> cachedMessages(Ref ref, String chatId) async {
  final link = ref.keepAlive();
  Timer(Duration(minutes: 5), link.close);

  return fetchMessages(chatId);
}
```

### Lifecycle Hooks

```dart
@riverpod
Stream<Data> managedStream(Ref ref) {
  final stream = createStream();

  ref.onDispose(() {
    // Called when provider permanently destroyed
    stream.close();
  });

  ref.onCancel(() {
    // Called when last listener removed (but not disposed yet)
    print('Paused - no listeners');
  });

  ref.onResume(() {
    // Called when listener added after onCancel
    print('Resumed');
  });

  return stream;
}
```

---

## Functional Error Handling with Either

### Domain Layer (Repository)

```dart
import 'package:fpdart/fpdart.dart';

// Define domain failures
sealed class AuthFailure {
  const AuthFailure();
}
class InvalidCredentials extends AuthFailure {}
class NetworkError extends AuthFailure {}
class UnknownError extends AuthFailure {}

// Repository returns Either
abstract class AuthRepository {
  Future<Either<AuthFailure, User>> signIn(String email, String password);
}

class FirebaseAuthRepository implements AuthRepository {
  @override
  Future<Either<AuthFailure, User>> signIn(String email, String password) async {
    try {
      final userCredential = await FirebaseAuth.instance
        .signInWithEmailAndPassword(email: email, password: password);
      return right(User.fromFirebase(userCredential.user!));
    } on FirebaseAuthException catch (e) {
      return left(_mapFailure(e.code));
    } catch (e) {
      return left(UnknownError());
    }
  }

  AuthFailure _mapFailure(String code) => switch (code) {
    'user-not-found' => InvalidCredentials(),
    'wrong-password' => InvalidCredentials(),
    'network-request-failed' => NetworkError(),
    _ => UnknownError(),
  };
}
```

### State Layer (Notifier Integration)

```dart
@riverpod
class AuthController extends _$AuthController {
  @override
  Future<User?> build() async => null;

  Future<void> signIn(String email, String password) async {
    state = const AsyncLoading();

    final repository = ref.read(authRepositoryProvider);
    final result = await repository.signIn(email, password);

    // Fold Either into AsyncValue
    state = result.fold(
      (failure) => AsyncError(failure, StackTrace.current),
      (user) => AsyncData(user),
    );
  }
}
```

### UI Layer (Pattern Matching)

```dart
class LoginScreen extends ConsumerWidget {
  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final authState = ref.watch(authControllerProvider);

    return switch (authState) {
      AsyncData(:final value) => HomeScreen(user: value),
      AsyncError(:final error) => Column(
        children: [
          Text(_getErrorMessage(error)),
          ElevatedButton(
            onPressed: () => ref.invalidate(authControllerProvider),
            child: Text('Retry'),
          ),
        ],
      ),
      _ => CircularProgressIndicator(),
    };
  }

  String _getErrorMessage(Object error) => switch (error) {
    InvalidCredentials() => 'Invalid email or password',
    NetworkError() => 'Network connection failed',
    _ => 'An unexpected error occurred',
  };
}
```

---

## Real-Time Chat Architecture

### Dual-Stack Pattern (Firestore + WebSocket)

```dart
// 1. Firestore Stream (Authoritative Source)
@riverpod
Stream<List<Message>> firestoreMessages(Ref ref, String chatId) {
  final firestore = ref.watch(firebaseFirestoreProvider);
  return firestore
    .collection('chats/$chatId/messages')
    .orderBy('createdAt', descending: true)
    .limit(50)
    .snapshots()
    .map((snap) => snap.docs.map((d) => Message.fromFirestore(d)).toList());
}

// 2. WebSocket Stream (Ephemeral Events)
@Riverpod(keepAlive: true)
SocketClient socketClient(Ref ref) {
  final socket = io('wss://api.app', <String, dynamic>{
    'transports': ['websocket'],
  });

  socket.connect();

  ref.onDispose(() {
    socket.disconnect();
    socket.dispose();
  });

  return socket;
}

@riverpod
Stream<Message> liveSocketMessages(Ref ref) {
  final socket = ref.watch(socketClientProvider);
  final controller = StreamController<Message>();

  void onNewMessage(dynamic data) {
    try {
      controller.add(Message.fromJson(data));
    } catch (e) {
      ref.read(errorLoggerProvider).log(e);
    }
  }

  socket.on('new_message', onNewMessage);

  ref.onDispose(() {
    socket.off('new_message', onNewMessage);
    controller.close();
  });

  return controller.stream;
}

// 3. Pending Messages (Optimistic UI)
@riverpod
class PendingMessages extends _$PendingMessages {
  @override
  List<Message> build(String chatId) => [];

  void add(Message message) {
    state = [...state, message];
  }

  void remove(String messageId) {
    state = state.where((m) => m.id != messageId).toList();
  }
}

// 4. Merged Timeline (UI-Facing)
@riverpod
List<Message> chatTimeline(Ref ref, String chatId) {
  final serverAsync = ref.watch(firestoreMessagesProvider(chatId));
  final pending = ref.watch(pendingMessagesProvider(chatId));

  final serverMessages = serverAsync.valueOrNull ?? [];

  return [...pending, ...serverMessages];
}
```

### Send Message Flow

```dart
@riverpod
class MessageSender extends _$MessageSender {
  @override
  void build() {}

  Future<void> send(String chatId, String text) async {
    final tempMessage = Message(
      id: 'temp_${DateTime.now().millisecondsSinceEpoch}',
      text: text,
      status: MessageStatus.sending,
      createdAt: DateTime.now(),
    );

    // 1. Add to pending (immediate UI update)
    ref.read(pendingMessagesProvider(chatId).notifier).add(tempMessage);

    // 2. Send to server
    final repository = ref.read(chatRepositoryProvider);
    final result = await repository.sendMessage(chatId, text);

    result.fold(
      (failure) {
        // Mark as failed, keep in pending for retry
        ref.read(pendingMessagesProvider(chatId).notifier).update(
          tempMessage.copyWith(status: MessageStatus.failed),
        );
      },
      (serverMessage) {
        // Remove from pending (will appear in Firestore stream)
        ref.read(pendingMessagesProvider(chatId).notifier).remove(tempMessage.id);
      },
    );
  }
}
```

---

## Memory-Safe Media Handling

### Video Controllers (Scoped AutoDispose)

```dart
// Provider creates and disposes controller automatically
@riverpod
Future<VideoPlayerController> videoController(
  Ref ref,
  String videoUrl,
) async {
  final controller = VideoPlayerController.networkUrl(Uri.parse(videoUrl));

  // CRITICAL: Bind disposal to provider lifecycle
  ref.onDispose(() {
    controller.dispose();
  });

  await controller.initialize();
  return controller;
}

// UI Widget
class VideoBubble extends ConsumerWidget {
  final String videoUrl;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final controllerAsync = ref.watch(videoControllerProvider(videoUrl));

    return controllerAsync.when(
      data: (controller) => AspectRatio(
        aspectRatio: controller.value.aspectRatio,
        child: VideoPlayer(controller),
      ),
      loading: () => CircularProgressIndicator(),
      error: (e, st) => Icon(Icons.error),
    );
  }
}
```

**Memory Safety**: When widget scrolls off-screen → `ref.watch` disposed → `ref.onDispose` called → `controller.dispose()` executed → native texture freed.

### Image Caching (TTL Strategy)

```dart
@riverpod
Future<Uint8List> chatImage(Ref ref, String url) async {
  // Keep in memory for 60s after leaving screen
  final link = ref.keepAlive();
  final timer = Timer(Duration(seconds: 60), link.close);
  ref.onDispose(() => timer.cancel());

  final response = await ref.read(httpClientProvider).get(url);
  return response.bodyBytes;
}
```

---

## Pagination (Infinite Scroll)

### AsyncNotifier Pattern

```dart
@riverpod
class MessagePagination extends _$MessagePagination {
  DocumentSnapshot? _lastDoc;
  bool _hasMore = true;

  @override
  Future<List<Message>> build(String chatId) async {
    _lastDoc = null;
    _hasMore = true;
    return _fetchPage(chatId);
  }

  Future<List<Message>> _fetchPage(String chatId) async {
    final firestore = ref.read(firebaseFirestoreProvider);

    var query = firestore
      .collection('chats/$chatId/messages')
      .orderBy('createdAt', descending: true)
      .limit(20);

    if (_lastDoc != null) {
      query = query.startAfterDocument(_lastDoc!);
    }

    final snapshot = await query.get();
    _lastDoc = snapshot.docs.isNotEmpty ? snapshot.docs.last : null;
    _hasMore = snapshot.docs.length == 20;

    return snapshot.docs.map((d) => Message.fromFirestore(d)).toList();
  }

  Future<void> loadMore() async {
    if (state.isLoading || !_hasMore) return;

    final currentList = state.value ?? [];

    // Preserve previous data while loading
    state = const AsyncLoading().copyWithPrevious(state);

    state = await AsyncValue.guard(() async {
      final newMessages = await _fetchPage(arg);
      return [...currentList, ...newMessages];
    });
  }
}
```

### UI Integration

```dart
class ChatScreen extends ConsumerWidget {
  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final messagesAsync = ref.watch(messagePaginationProvider(chatId));

    return NotificationListener<ScrollNotification>(
      onNotification: (notification) {
        if (notification.metrics.extentAfter < 500) {
          ref.read(messagePaginationProvider(chatId).notifier).loadMore();
        }
        return false;
      },
      child: messagesAsync.when(
        data: (messages) => ListView.builder(
          reverse: true,
          itemCount: messages.length,
          itemBuilder: (ctx, i) => MessageBubble(messages[i]),
        ),
        loading: () => Center(child: CircularProgressIndicator()),
        error: (e, st) => ErrorWidget(e),
      ),
    );
  }
}
```

---

## Debounced Search with Cancellation

```dart
@riverpod
Future<List<Message>> messageSearch(Ref ref, String query) async {
  if (query.isEmpty) return [];

  // Create cancellable HTTP client
  final client = http.Client();

  // Register disposal (triggers on query change)
  ref.onDispose(() {
    client.close();  // Cancels in-flight requests
  });

  // Debounce delay
  await Future.delayed(Duration(milliseconds: 500));

  // If disposed during delay, execution stops here
  final response = await client.get(
    Uri.parse('https://api.app/search?q=$query'),
  );

  return (jsonDecode(response.body) as List)
    .map((json) => Message.fromJson(json))
    .toList();
}

// UI
TextField(
  onChanged: (value) {
    // Each keystroke creates new provider instance
    // Previous instance disposed → client.close() → request cancelled
    ref.read(messageSearchProvider(value));
  },
)
```

**Mechanism**: New query → new provider instance → old instance disposed → `ref.onDispose` → `client.close()` → network abort.

---

## OneSignal Integration

### Eager Initialization

```dart
@Riverpod(keepAlive: true)
Future<void> appStartup(Ref ref) async {
  // 1. Initialize Firebase
  await Firebase.initializeApp();

  // 2. Initialize OneSignal
  OneSignal.Debug.setLogLevel(OSLogLevel.verbose);
  OneSignal.initialize("YOUR_ONESIGNAL_APP_ID");

  // 3. Register notification handler
  OneSignal.Notifications.addClickListener((event) {
    final chatId = event.notification.additionalData?['chat_id'];
    if (chatId != null) {
      ref.read(notificationHandlerProvider.notifier).navigateToChat(chatId);
    }
  });
}

// main.dart
void main() {
  runApp(
    ProviderScope(
      child: AppInitializer(),
    ),
  );
}

class AppInitializer extends ConsumerWidget {
  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final startupAsync = ref.watch(appStartupProvider);

    return startupAsync.when(
      data: (_) => MyApp(),  // Main app only after initialization
      loading: () => MaterialApp(
        home: Scaffold(body: Center(child: CircularProgressIndicator())),
      ),
      error: (e, st) => MaterialApp(
        home: Scaffold(body: Center(child: Text('Initialization failed'))),
      ),
    );
  }
}
```

### Navigation Bridge

```dart
@riverpod
class NotificationHandler extends _$NotificationHandler {
  @override
  String? build() => null;  // Stores chatId to navigate to

  void navigateToChat(String chatId) {
    state = chatId;
  }

  void clearNavigation() {
    state = null;
  }
}

// In GoRouter definition
final router = GoRouter(
  refreshListenable: // Create listenable from notificationHandlerProvider,
  redirect: (context, state) {
    final ref = ProviderScope.containerOf(context);
    final chatId = ref.read(notificationHandlerProvider);

    if (chatId != null) {
      ref.read(notificationHandlerProvider.notifier).clearNavigation();
      return '/chat/$chatId';
    }
    return null;
  },
  routes: [...],
);
```

---

## Advanced Patterns

### Select (Reduce Rebuilds)

```dart
// ❌ Rebuilds on ANY user field change
final userName = ref.watch(userProvider).name;

// ✅ Only rebuilds when name changes
final userName = ref.watch(userProvider.select((user) => user.name));
```

### Listen (Side Effects)

```dart
@override
Widget build(BuildContext context, WidgetRef ref) {
  // Listen for auth changes, show SnackBar
  ref.listen<AsyncValue<User?>>(
    authControllerProvider,
    (previous, next) {
      next.whenData((user) {
        if (user != null) {
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(content: Text('Welcome ${user.name}')),
          );
        }
      });
    },
  );

  return Scaffold(...);
}
```

### Invalidate (Force Refresh)

```dart
// Refresh single provider
ref.invalidate(userProvider);

// Refresh all providers of family
ref.invalidate(chatMessagesProvider);
```

### Dependency Override (Testing)

```dart
testWidgets('Auth test', (tester) async {
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

---

## Migration from Legacy

| Legacy | Riverpod 3.0 |
|--------|--------------|
| `StateNotifier` | `Notifier` with `@riverpod` |
| `StateNotifierProvider` | `NotifierProvider` (auto-generated) |
| `ChangeNotifier` | `AsyncNotifier` or avoid entirely |
| `StateProvider` | `Notifier` for logic, direct value for simple cases |
| `Provider.family((ref, arg))` | `@riverpod T name(Ref ref, String arg)` |
| `ref.read(provider.notifier).method()` | Same, but with generated provider |
| Constructor logic | Move to `build()` method |

---

## Common Pitfalls

| Issue | Solution |
|-------|----------|
| Memory leak with VideoController | Use scoped provider with `ref.onDispose` |
| "Provider was disposed" error | Use `keepAlive()` or increase cache duration |
| Too many rebuilds | Use `.select()` to watch specific fields |
| Search sending too many requests | Implement debounce with `ref.onDispose` |
| OneSignal navigation before app ready | Use eager `appStartupProvider` |
| Firestore costs too high | Use `keepAlive` + TTL for expensive streams |
| AsyncValue always loading on refresh | Use `copyWithPrevious(state)` |

---

## Performance Checklist

- [ ] All providers use code generation (`@riverpod`)
- [ ] No legacy StateNotifier/ChangeNotifier
- [ ] Video/Image controllers scoped to providers
- [ ] Expensive streams use `keepAlive` with TTL
- [ ] UI uses `.select()` for granular watching
- [ ] Search implements debounce + cancellation
- [ ] Pagination preserves data during loading
- [ ] Either monad used for all repository errors
- [ ] OneSignal initialized before ProviderScope
- [ ] `riverpod_lint` enabled in analysis_options.yaml

---

**See `examples/` for full implementations of chat, auth, and pagination patterns.**
