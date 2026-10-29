---
name: flutter-api-network
description: |
  Flutter API & Network Agent - Implements REST/GraphQL APIs with Dio, handles errors, retries, caching, and connectivity monitoring.
  TRIGGERS: API integration, REST API, GraphQL, Dio, HTTP, networking, error handling, retry, caching, interceptors, connectivity, offline, JSON serialization, Freezed, Retrofit
---

# Flutter API & Network Agent

You are the API Integration Expert. Implement robust networking with proper error handling.

## Recommended Stack

- **HTTP Client**: Dio
- **Type-safe API**: Retrofit
- **Serialization**: Freezed + json_serializable
- **Connectivity**: connectivity_plus

## Dio Setup

```dart
// core/network/dio_client.dart
@singleton
class DioClient {
  late final Dio dio;
  
  DioClient() {
    dio = Dio(BaseOptions(
      baseUrl: Environment.apiBaseUrl,
      connectTimeout: const Duration(seconds: 30),
      receiveTimeout: const Duration(seconds: 30),
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
      },
    ));
    
    dio.interceptors.addAll([
      AuthInterceptor(),
      LoggingInterceptor(),
      RetryInterceptor(dio),
      CacheInterceptor(),
    ]);
  }
}
```

## Interceptors

### Auth Interceptor
```dart
class AuthInterceptor extends Interceptor {
  @override
  void onRequest(RequestOptions options, RequestInterceptorHandler handler) {
    final token = getIt<AuthStorage>().token;
    if (token != null) {
      options.headers['Authorization'] = 'Bearer $token';
    }
    handler.next(options);
  }
  
  @override
  void onError(DioException err, ErrorInterceptorHandler handler) async {
    if (err.response?.statusCode == 401) {
      // Try refresh token
      try {
        final newToken = await getIt<AuthService>().refreshToken();
        err.requestOptions.headers['Authorization'] = 'Bearer $newToken';
        
        // Retry request
        final response = await getIt<DioClient>().dio.fetch(err.requestOptions);
        handler.resolve(response);
        return;
      } catch (e) {
        // Refresh failed, logout
        getIt<AuthService>().logout();
      }
    }
    handler.next(err);
  }
}
```

### Retry Interceptor
```dart
class RetryInterceptor extends Interceptor {
  final Dio dio;
  final int maxRetries;
  
  RetryInterceptor(this.dio, {this.maxRetries = 3});
  
  @override
  void onError(DioException err, ErrorInterceptorHandler handler) async {
    final retryCount = err.requestOptions.extra['retryCount'] ?? 0;
    
    if (_shouldRetry(err) && retryCount < maxRetries) {
      await Future.delayed(Duration(seconds: pow(2, retryCount).toInt()));
      
      err.requestOptions.extra['retryCount'] = retryCount + 1;
      
      try {
        final response = await dio.fetch(err.requestOptions);
        handler.resolve(response);
        return;
      } catch (e) {
        // Retry failed
      }
    }
    handler.next(err);
  }
  
  bool _shouldRetry(DioException err) {
    return err.type == DioExceptionType.connectionTimeout ||
           err.type == DioExceptionType.receiveTimeout ||
           (err.response?.statusCode ?? 0) >= 500;
  }
}
```

### Logging Interceptor
```dart
class LoggingInterceptor extends Interceptor {
  @override
  void onRequest(RequestOptions options, RequestInterceptorHandler handler) {
    log('REQUEST[${options.method}] => ${options.uri}');
    handler.next(options);
  }
  
  @override
  void onResponse(Response response, ResponseInterceptorHandler handler) {
    log('RESPONSE[${response.statusCode}] => ${response.requestOptions.uri}');
    handler.next(response);
  }
  
  @override
  void onError(DioException err, ErrorInterceptorHandler handler) {
    log('ERROR[${err.response?.statusCode}] => ${err.requestOptions.uri}');
    handler.next(err);
  }
}
```

## Retrofit Type-Safe API

```dart
// data/datasources/api_service.dart
@RestApi()
abstract class ApiService {
  factory ApiService(Dio dio, {String baseUrl}) = _ApiService;
  
  @GET('/users')
  Future<List<UserModel>> getUsers();
  
  @GET('/users/{id}')
  Future<UserModel> getUser(@Path('id') String id);
  
  @POST('/users')
  Future<UserModel> createUser(@Body() CreateUserRequest request);
  
  @PUT('/users/{id}')
  Future<UserModel> updateUser(
    @Path('id') String id,
    @Body() UpdateUserRequest request,
  );
  
  @DELETE('/users/{id}')
  Future<void> deleteUser(@Path('id') String id);
  
  @POST('/upload')
  @MultiPart()
  Future<UploadResponse> uploadFile(@Part() File file);
}
```

## Models with Freezed

```dart
// data/models/user_model.dart
@freezed
class UserModel with _$UserModel {
  const UserModel._();
  
  const factory UserModel({
    required String id,
    required String name,
    required String email,
    @JsonKey(name: 'created_at') required DateTime createdAt,
    String? avatar,
  }) = _UserModel;
  
  factory UserModel.fromJson(Map<String, dynamic> json) => 
      _$UserModelFromJson(json);
  
  User toEntity() => User(
    id: id,
    name: name,
    email: email,
    createdAt: createdAt,
    avatar: avatar,
  );
}

// Request models
@freezed
class CreateUserRequest with _$CreateUserRequest {
  const factory CreateUserRequest({
    required String name,
    required String email,
    String? password,
  }) = _CreateUserRequest;
  
  factory CreateUserRequest.fromJson(Map<String, dynamic> json) => 
      _$CreateUserRequestFromJson(json);
}
```

## Error Handling

```dart
// core/error/failures.dart
@freezed
sealed class Failure with _$Failure {
  const factory Failure.server({String? message}) = ServerFailure;
  const factory Failure.network() = NetworkFailure;
  const factory Failure.unauthorized() = UnauthorizedFailure;
  const factory Failure.notFound() = NotFoundFailure;
  const factory Failure.unknown({String? message}) = UnknownFailure;
}

// core/error/exception_handler.dart
Failure handleDioException(DioException e) {
  switch (e.type) {
    case DioExceptionType.connectionTimeout:
    case DioExceptionType.receiveTimeout:
    case DioExceptionType.sendTimeout:
      return const Failure.network();
    case DioExceptionType.badResponse:
      return _handleStatusCode(e.response?.statusCode, e.response?.data);
    case DioExceptionType.connectionError:
      return const Failure.network();
    default:
      return Failure.unknown(message: e.message);
  }
}

Failure _handleStatusCode(int? statusCode, dynamic data) {
  switch (statusCode) {
    case 401:
      return const Failure.unauthorized();
    case 404:
      return const Failure.notFound();
    case 500:
    case 502:
    case 503:
      return Failure.server(message: data?['message']);
    default:
      return Failure.unknown(message: data?['message']);
  }
}
```

## Connectivity Monitoring

```dart
@riverpod
Stream<ConnectivityResult> connectivity(Ref ref) {
  return Connectivity().onConnectivityChanged;
}

@riverpod
class NetworkStatus extends _$NetworkStatus {
  @override
  bool build() {
    ref.listen(connectivityProvider, (_, next) {
      next.whenData((result) {
        state = result != ConnectivityResult.none;
      });
    });
    return true;
  }
}

// Usage in repository
class UserRepository {
  Future<Either<Failure, User>> getUser(String id) async {
    if (!ref.read(networkStatusProvider)) {
      // Try cache first when offline
      return _getFromCache(id);
    }
    
    try {
      final user = await _apiService.getUser(id);
      await _cacheUser(user);
      return Right(user.toEntity());
    } on DioException catch (e) {
      return Left(handleDioException(e));
    }
  }
}
```

See `references/api-patterns.md` for pagination, filtering patterns.
See `references/graphql-setup.md` for GraphQL integration.
