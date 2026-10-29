// RIVERPOD 3.0 PROVIDER TEMPLATES
// Copy-paste starting points for common patterns

import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:riverpod_annotation/riverpod_annotation.dart';

part 'provider_templates.g.dart';

// ============================================================================
// TEMPLATE 1: Simple Provider (Dependency Injection)
// ============================================================================

@riverpod
Dio httpClient(Ref ref) {
  return Dio(BaseOptions(
    baseUrl: 'https://api.example.com',
    connectTimeout: Duration(seconds: 5),
  ));
}

// ============================================================================
// TEMPLATE 2: Future Provider (REST API Call)
// ============================================================================

@riverpod
Future<User> user(Ref ref, {required int userId}) async {
  final dio = ref.watch(httpClientProvider);
  final response = await dio.get('/users/$userId');
  return User.fromJson(response.data);
}

// ============================================================================
// TEMPLATE 3: Stream Provider (Firestore)
// ============================================================================

@riverpod
Stream<List<Message>> messages(Ref ref, String chatId) {
  final firestore = ref.watch(firebaseFirestoreProvider);

  return firestore
    .collection('chats/$chatId/messages')
    .orderBy('createdAt', descending: true)
    .snapshots()
    .map((snapshot) => snapshot.docs
      .map((doc) => Message.fromFirestore(doc))
      .toList()
    );
}

// ============================================================================
// TEMPLATE 4: Notifier (Sync Mutable State)
// ============================================================================

@riverpod
class Counter extends _$Counter {
  @override
  int build() => 0; // Initial state

  void increment() {
    state++;
  }

  void decrement() {
    state--;
  }

  void reset() {
    state = 0;
  }
}

// ============================================================================
// TEMPLATE 5: AsyncNotifier (Async Actions)
// ============================================================================

@riverpod
class TodoList extends _$TodoList {
  @override
  Future<List<Todo>> build() async {
    // Initialize: fetch from API
    final repository = ref.watch(todoRepositoryProvider);
    return repository.fetchTodos();
  }

  Future<void> add(String title) async {
    // Set loading (but preserve current data)
    state = const AsyncLoading().copyWithPrevious(state);

    // Perform action
    final repository = ref.read(todoRepositoryProvider);
    final result = await repository.addTodo(title);

    // Update state
    state = await AsyncValue.guard(() async {
      final currentList = state.value ?? [];
      return result.fold(
        (failure) => throw failure,
        (newTodo) => [...currentList, newTodo],
      );
    });
  }

  Future<void> delete(String id) async {
    state = const AsyncLoading().copyWithPrevious(state);

    final repository = ref.read(todoRepositoryProvider);
    await repository.deleteTodo(id);

    state = AsyncData(
      state.value?.where((todo) => todo.id != id).toList() ?? [],
    );
  }
}

// ============================================================================
// TEMPLATE 6: StreamNotifier (WebSocket Bridge)
// ============================================================================

@riverpod
class LiveEvents extends _$LiveEvents {
  @override
  Stream<Event> build() {
    final socket = ref.watch(socketClientProvider);
    final controller = StreamController<Event>();

    void onEvent(dynamic data) {
      try {
        controller.add(Event.fromJson(data));
      } catch (e) {
        ref.read(errorLoggerProvider).log(e);
      }
    }

    socket.on('event', onEvent);

    ref.onDispose(() {
      socket.off('event', onEvent);
      controller.close();
    });

    return controller.stream;
  }
}

// ============================================================================
// TEMPLATE 7: Repository with Either (Functional Error Handling)
// ============================================================================

abstract class UserRepository {
  Future<Either<Failure, User>> getUser(int id);
  Future<Either<Failure, void>> updateUser(User user);
}

@riverpod
UserRepository userRepository(Ref ref) => ApiUserRepository(
  dio: ref.watch(httpClientProvider),
);

class ApiUserRepository implements UserRepository {
  final Dio dio;

  ApiUserRepository({required this.dio});

  @override
  Future<Either<Failure, User>> getUser(int id) async {
    try {
      final response = await dio.get('/users/$id');
      return right(User.fromJson(response.data));
    } on DioException catch (e) {
      return left(_mapDioError(e));
    } catch (e) {
      return left(UnknownFailure());
    }
  }

  @override
  Future<Either<Failure, void>> updateUser(User user) async {
    try {
      await dio.put('/users/${user.id}', data: user.toJson());
      return right(null);
    } catch (e) {
      return left(UnknownFailure());
    }
  }

  Failure _mapDioError(DioException e) => switch (e.type) {
    DioExceptionType.connectionTimeout => NetworkFailure(),
    DioExceptionType.receiveTimeout => NetworkFailure(),
    DioExceptionType.badResponse when e.response?.statusCode == 404 => NotFoundFailure(),
    _ => UnknownFailure(),
  };
}

// ============================================================================
// TEMPLATE 8: Pagination with AsyncNotifier
// ============================================================================

@riverpod
class PaginatedList extends _$PaginatedList {
  int _page = 0;
  bool _hasMore = true;

  @override
  Future<List<Item>> build() async {
    _page = 0;
    _hasMore = true;
    return _fetchPage();
  }

  Future<List<Item>> _fetchPage() async {
    final repository = ref.read(itemRepositoryProvider);
    final items = await repository.fetchItems(page: _page, limit: 20);
    _hasMore = items.length == 20;
    return items;
  }

  Future<void> loadMore() async {
    if (state.isLoading || !_hasMore) return;

    final currentList = state.value ?? [];
    _page++;

    state = const AsyncLoading().copyWithPrevious(state);

    state = await AsyncValue.guard(() async {
      final newItems = await _fetchPage();
      return [...currentList, ...newItems];
    });
  }
}

// ============================================================================
// TEMPLATE 9: Debounced Search
// ============================================================================

@riverpod
Future<List<Result>> search(Ref ref, String query) async {
  if (query.isEmpty) return [];

  // Create cancellable client
  final client = http.Client();
  ref.onDispose(() => client.close());

  // Debounce
  await Future.delayed(Duration(milliseconds: 500));

  // Execute
  final response = await client.get(
    Uri.parse('https://api.example.com/search?q=$query'),
  );

  return (jsonDecode(response.body) as List)
    .map((json) => Result.fromJson(json))
    .toList();
}

// ============================================================================
// TEMPLATE 10: KeepAlive with TTL
// ============================================================================

@riverpod
Future<ExpensiveData> cachedData(Ref ref) async {
  // Keep in memory for 5 minutes after last use
  final link = ref.keepAlive();
  Timer(Duration(minutes: 5), link.close);

  return fetchExpensiveData();
}

// ============================================================================
// TEMPLATE 11: Global Singleton (Never Disposed)
// ============================================================================

@Riverpod(keepAlive: true)
AnalyticsService analytics(Ref ref) {
  final service = AnalyticsService();
  service.initialize();

  ref.onDispose(() {
    service.dispose();
  });

  return service;
}

// ============================================================================
// TEMPLATE 12: Optimistic UI Pattern
// ============================================================================

// Pending state
@riverpod
class PendingTodos extends _$PendingTodos {
  @override
  List<Todo> build() => [];

  void add(Todo todo) => state = [...state, todo];
  void remove(String id) => state = state.where((t) => t.id != id).toList();
}

// Server state
@riverpod
Future<List<Todo>> serverTodos(Ref ref) async {
  return ref.watch(todoRepositoryProvider).fetchTodos();
}

// Merged UI state
@riverpod
List<Todo> allTodos(Ref ref) {
  final serverAsync = ref.watch(serverTodosProvider);
  final pending = ref.watch(pendingTodosProvider);

  final serverTodos = serverAsync.valueOrNull ?? [];
  return [...pending, ...serverTodos];
}

// ============================================================================
// TEMPLATE 13: Listen for Side Effects (SnackBar)
// ============================================================================

class MyWidget extends ConsumerWidget {
  @override
  Widget build(BuildContext context, WidgetRef ref) {
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
}

// ============================================================================
// TEMPLATE 14: Select (Reduce Rebuilds)
// ============================================================================

class UserNameWidget extends ConsumerWidget {
  @override
  Widget build(BuildContext context, WidgetRef ref) {
    // Only rebuilds when name changes (not email, age, etc.)
    final name = ref.watch(userProvider.select((user) => user.name));

    return Text(name);
  }
}
