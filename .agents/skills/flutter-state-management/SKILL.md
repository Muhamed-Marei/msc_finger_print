---
name: flutter-state-management
description: |
  Flutter State Management Agent - Implements Riverpod 3.0 state management, widget lifecycle, navigation with go_router, and dependency injection with GetIt.
  TRIGGERS: state management, Riverpod, providers, StateNotifier, AsyncNotifier, go_router, navigation, GetIt, dependency injection, widget lifecycle, StatefulWidget, setState
---

# Flutter State Management Agent

You are the State Management Expert. Implement Riverpod 3.x patterns and proper widget lifecycle.

## Recommended Stack (2026)

- **State Management**: Riverpod 3.2+ / 4.x
- **Navigation**: go_router 17.x
- **Dependency Injection**: GetIt 9.x + Injectable 2.7+

## Riverpod Setup

### pubspec.yaml
```yaml
dependencies:
  flutter_riverpod: ^3.2.0
  riverpod_annotation: ^4.0.1

dev_dependencies:
  riverpod_generator: ^4.0.1
  build_runner: ^2.4.0
```

### Main Setup
```dart
void main() {
  runApp(
    ProviderScope(
      observers: [LoggingObserver()],  // Optional
      child: const MyApp(),
    ),
  );
}
```

## Provider Types

### Simple Provider (Computed Values)
```dart
@riverpod
int doubledValue(Ref ref) {
  final value = ref.watch(counterProvider);
  return value * 2;
}
```

### Notifier (Sync State)
```dart
@riverpod
class Counter extends _$Counter {
  @override
  int build() => 0;  // Initial state
  
  void increment() => state++;
  void decrement() => state--;
  void reset() => state = 0;
}
```

### AsyncNotifier (Async State)
```dart
@riverpod
class UserList extends _$UserList {
  @override
  Future<List<User>> build() async {
    return await ref.read(userRepositoryProvider).getUsers();
  }
  
  Future<void> refresh() async {
    state = const AsyncLoading();
    state = await AsyncValue.guard(() => 
      ref.read(userRepositoryProvider).getUsers()
    );
  }
  
  Future<void> addUser(User user) async {
    await ref.read(userRepositoryProvider).addUser(user);
    ref.invalidateSelf();  // Refresh the list
  }
}
```

### Family Provider (With Parameters)
```dart
@riverpod
Future<User> user(Ref ref, String userId) async {
  return ref.read(userRepositoryProvider).getUser(userId);
}

// Usage
final user = ref.watch(userProvider('123'));
```

## Consuming Providers

### In Widgets
```dart
class UserPage extends ConsumerWidget {
  const UserPage({super.key});
  
  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final userAsync = ref.watch(userListProvider);
    
    return userAsync.when(
      loading: () => const CircularProgressIndicator(),
      error: (error, stack) => ErrorWidget(error.toString()),
      data: (users) => ListView.builder(
        itemCount: users.length,
        itemBuilder: (context, index) => UserTile(users[index]),
      ),
    );
  }
}
```

### In StatefulWidget
```dart
class MyPage extends ConsumerStatefulWidget {
  const MyPage({super.key});
  
  @override
  ConsumerState<MyPage> createState() => _MyPageState();
}

class _MyPageState extends ConsumerState<MyPage> {
  @override
  void initState() {
    super.initState();
    // Can use ref here
    ref.read(analyticsProvider).logPageView();
  }
  
  @override
  Widget build(BuildContext context) {
    final data = ref.watch(dataProvider);
    return ...;
  }
}
```

### Listen for Side Effects
```dart
ref.listen(authProvider, (previous, next) {
  if (next == null) {
    context.go('/login');
  }
});
```

## go_router Setup

```dart
@riverpod
GoRouter router(Ref ref) {
  final authState = ref.watch(authProvider);
  
  return GoRouter(
    initialLocation: '/',
    redirect: (context, state) {
      final isLoggedIn = authState != null;
      final isLoggingIn = state.matchedLocation == '/login';
      
      if (!isLoggedIn && !isLoggingIn) return '/login';
      if (isLoggedIn && isLoggingIn) return '/';
      return null;
    },
    routes: [
      GoRoute(
        path: '/',
        builder: (context, state) => const HomePage(),
        routes: [
          GoRoute(
            path: 'user/:id',
            builder: (context, state) => UserPage(
              userId: state.pathParameters['id']!,
            ),
          ),
        ],
      ),
      GoRoute(
        path: '/login',
        builder: (context, state) => const LoginPage(),
      ),
    ],
  );
}
```

## GetIt Dependency Injection

```dart
// core/di/injection.dart
final getIt = GetIt.instance;

@InjectableInit()
Future<void> configureDependencies() async => getIt.init();

// Usage with Injectable annotations
@singleton
class ApiClient {
  final Dio dio;
  ApiClient(this.dio);
}

@lazySingleton
class UserRepository {
  final ApiClient client;
  UserRepository(this.client);
}

// In Riverpod providers
@riverpod
UserRepository userRepository(Ref ref) => getIt<UserRepository>();
```

## Widget Lifecycle

```dart
class MyStatefulWidget extends StatefulWidget {
  @override
  State<MyStatefulWidget> createState() => _MyStatefulWidgetState();
}

class _MyStatefulWidgetState extends State<MyStatefulWidget> 
    with WidgetsBindingObserver {
  
  @override
  void initState() {
    super.initState();
    // Called once when widget is inserted
    WidgetsBinding.instance.addObserver(this);
    _initialize();
  }
  
  @override
  void didChangeDependencies() {
    super.didChangeDependencies();
    // Called when dependencies change (InheritedWidget)
  }
  
  @override
  void didUpdateWidget(MyStatefulWidget oldWidget) {
    super.didUpdateWidget(oldWidget);
    // Called when parent rebuilds with new widget
    if (widget.id != oldWidget.id) {
      _reload();
    }
  }
  
  @override
  void didChangeAppLifecycleState(AppLifecycleState state) {
    // App lifecycle changes
    switch (state) {
      case AppLifecycleState.resumed:
        _onResume();
        break;
      case AppLifecycleState.paused:
        _onPause();
        break;
      default:
        break;
    }
  }
  
  @override
  void dispose() {
    // Clean up resources
    WidgetsBinding.instance.removeObserver(this);
    _controller.dispose();
    super.dispose();
  }
}
```

See `references/riverpod-patterns.md` for advanced patterns.
See `references/navigation-patterns.md` for complex navigation scenarios.
