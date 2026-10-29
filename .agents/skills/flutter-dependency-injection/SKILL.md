---
name: flutter-dependency-injection
description: |
  Dependency Injection Expert - GetIt, Injectable, service locators, DI patterns.
  TRIGGERS: dependency injection, DI, GetIt, injectable, service locator, IoC
---

# Flutter Dependency Injection Expert

## Core Patterns

### GetIt Setup (Recommended)
```dart
// injection.dart
import 'package:get_it/get_it.dart';
import 'package:injectable/injectable.dart';

final getIt = GetIt.instance;

@InjectableInit()
void configureDependencies() => getIt.init();
```

### Injectable Annotations
```dart
// Services
@singleton
class AuthService { }

@lazySingleton
class ApiClient { }

@injectable
class UserRepository {
  UserRepository(this._apiClient);
  final ApiClient _apiClient;
}

// Environment-specific
@Environment('dev')
@Injectable(as: ApiClient)
class MockApiClient implements ApiClient { }

@Environment('prod')
@Injectable(as: ApiClient)
class RealApiClient implements ApiClient { }
```

### Module Registration
```dart
@module
abstract class RegisterModule {
  @lazySingleton
  Dio get dio => Dio(BaseOptions(baseUrl: 'https://api.example.com'));

  @preResolve
  Future<SharedPreferences> get prefs => SharedPreferences.getInstance();
}
```

## Best Practices

| Pattern | Use Case |
|---------|----------|
| `@singleton` | App-wide single instance (AuthService) |
| `@lazySingleton` | Expensive init, single instance (Database) |
| `@injectable` | New instance each time (ViewModels) |
| `@preResolve` | Async dependencies (SharedPreferences) |

## With Riverpod
```dart
// Combine GetIt with Riverpod
final authServiceProvider = Provider((ref) => getIt<AuthService>());
final userRepoProvider = Provider((ref) => getIt<UserRepository>());
```

## Commands
```bash
# Generate injection code
dart run build_runner build --delete-conflicting-outputs
```
