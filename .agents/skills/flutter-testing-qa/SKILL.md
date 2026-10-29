---
name: flutter-testing-qa
description: |
  Flutter Testing & QA Agent - Writes unit tests, widget tests, integration tests, and golden tests. Implements TDD and ensures >80% coverage.
  TRIGGERS: testing, unit test, widget test, integration test, golden test, Mockito, test coverage, TDD, mocking, test-driven development, flutter_test
---

# Flutter Testing & QA Agent

You are the Testing Expert. Implement comprehensive testing with TDD approach.

## Testing Pyramid

```
        /\
       /  \      Integration Tests (10%)
      /----\     End-to-end flows
     /      \
    /--------\   Widget Tests (30%)
   /          \  UI component testing
  /------------\ Unit Tests (60%)
 /              \ Business logic, models
```

## Test Structure

```
test/
├── unit/
│   ├── domain/
│   │   └── usecases/
│   └── data/
│       └── repositories/
├── widget/
│   └── features/
│       └── [feature]/
│           └── presentation/
├── integration/
│   └── flows/
└── golden/
    └── widgets/
```

## Unit Tests

### Testing Usecases
```dart
// test/unit/domain/usecases/get_user_test.dart
import 'package:flutter_test/flutter_test.dart';
import 'package:mockito/annotations.dart';
import 'package:mockito/mockito.dart';
import 'package:dartz/dartz.dart';

@GenerateMocks([UserRepository])
import 'get_user_test.mocks.dart';

void main() {
  late GetUser usecase;
  late MockUserRepository mockRepository;

  setUp(() {
    mockRepository = MockUserRepository();
    usecase = GetUser(mockRepository);
  });

  group('GetUser', () {
    const tUserId = '123';
    final tUser = User(id: tUserId, name: 'John');

    test('should get user from repository', () async {
      // Arrange
      when(mockRepository.getUser(any))
          .thenAnswer((_) async => Right(tUser));

      // Act
      final result = await usecase(tUserId);

      // Assert
      expect(result, Right(tUser));
      verify(mockRepository.getUser(tUserId));
      verifyNoMoreInteractions(mockRepository);
    });

    test('should return failure when repository fails', () async {
      // Arrange
      when(mockRepository.getUser(any))
          .thenAnswer((_) async => Left(ServerFailure()));

      // Act
      final result = await usecase(tUserId);

      // Assert
      expect(result, Left(ServerFailure()));
    });
  });
}
```

### Testing Models
```dart
// test/unit/data/models/user_model_test.dart
void main() {
  group('UserModel', () {
    final tJson = {
      'id': '123',
      'name': 'John',
      'email': 'john@example.com',
      'created_at': '2024-01-01T00:00:00Z',
    };

    final tModel = UserModel(
      id: '123',
      name: 'John',
      email: 'john@example.com',
      createdAt: DateTime.parse('2024-01-01T00:00:00Z'),
    );

    test('fromJson should return valid model', () {
      final result = UserModel.fromJson(tJson);
      expect(result, tModel);
    });

    test('toJson should return valid JSON', () {
      final result = tModel.toJson();
      expect(result['id'], tJson['id']);
      expect(result['name'], tJson['name']);
    });

    test('toEntity should return valid entity', () {
      final entity = tModel.toEntity();
      expect(entity.id, tModel.id);
      expect(entity.name, tModel.name);
    });
  });
}
```

## Widget Tests

```dart
// test/widget/features/auth/presentation/pages/login_page_test.dart
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:mockito/mockito.dart';

void main() {
  group('LoginPage', () {
    late MockAuthNotifier mockAuthNotifier;

    setUp(() {
      mockAuthNotifier = MockAuthNotifier();
    });

    Widget createWidget() {
      return ProviderScope(
        overrides: [
          authProvider.overrideWith(() => mockAuthNotifier),
        ],
        child: const MaterialApp(
          home: LoginPage(),
        ),
      );
    }

    testWidgets('should display login form', (tester) async {
      await tester.pumpWidget(createWidget());

      expect(find.byType(TextField), findsNWidgets(2));
      expect(find.text('Email'), findsOneWidget);
      expect(find.text('Password'), findsOneWidget);
      expect(find.byType(ElevatedButton), findsOneWidget);
    });

    testWidgets('should show error on invalid input', (tester) async {
      await tester.pumpWidget(createWidget());

      await tester.tap(find.byType(ElevatedButton));
      await tester.pump();

      expect(find.text('Email is required'), findsOneWidget);
    });

    testWidgets('should call signIn when form is valid', (tester) async {
      when(mockAuthNotifier.signIn(any, any))
          .thenAnswer((_) async {});

      await tester.pumpWidget(createWidget());

      await tester.enterText(
        find.byKey(const Key('email_field')),
        'test@example.com',
      );
      await tester.enterText(
        find.byKey(const Key('password_field')),
        'password123',
      );
      await tester.tap(find.byType(ElevatedButton));
      await tester.pump();

      verify(mockAuthNotifier.signIn('test@example.com', 'password123'));
    });

    testWidgets('should show loading indicator', (tester) async {
      when(mockAuthNotifier.state).thenReturn(const AuthState.loading());

      await tester.pumpWidget(createWidget());

      expect(find.byType(CircularProgressIndicator), findsOneWidget);
    });
  });
}
```

## Integration Tests

```dart
// integration_test/app_test.dart
import 'package:flutter_test/flutter_test.dart';
import 'package:integration_test/integration_test.dart';
import 'package:my_app/main.dart' as app;

void main() {
  IntegrationTestWidgetsFlutterBinding.ensureInitialized();

  group('end-to-end test', () {
    testWidgets('complete login flow', (tester) async {
      app.main();
      await tester.pumpAndSettle();

      // Find and tap login button
      final loginButton = find.text('Login');
      expect(loginButton, findsOneWidget);
      await tester.tap(loginButton);
      await tester.pumpAndSettle();

      // Enter credentials
      await tester.enterText(
        find.byKey(const Key('email_field')),
        'test@example.com',
      );
      await tester.enterText(
        find.byKey(const Key('password_field')),
        'password123',
      );

      // Submit
      await tester.tap(find.text('Sign In'));
      await tester.pumpAndSettle();

      // Verify navigation to home
      expect(find.text('Welcome'), findsOneWidget);
    });
  });
}
```

## Golden Tests

```dart
// test/golden/widgets/primary_button_test.dart
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';

void main() {
  group('PrimaryButton Golden Tests', () {
    testWidgets('default state', (tester) async {
      await tester.pumpWidget(
        MaterialApp(
          theme: AppTheme.light,
          home: Scaffold(
            body: Center(
              child: PrimaryButton(
                label: 'Click Me',
                onPressed: () {},
              ),
            ),
          ),
        ),
      );

      await expectLater(
        find.byType(PrimaryButton),
        matchesGoldenFile('goldens/primary_button_default.png'),
      );
    });

    testWidgets('loading state', (tester) async {
      await tester.pumpWidget(
        MaterialApp(
          theme: AppTheme.light,
          home: Scaffold(
            body: Center(
              child: PrimaryButton(
                label: 'Click Me',
                isLoading: true,
                onPressed: () {},
              ),
            ),
          ),
        ),
      );

      await expectLater(
        find.byType(PrimaryButton),
        matchesGoldenFile('goldens/primary_button_loading.png'),
      );
    });
  });
}
```

## Mocking with Riverpod

```dart
// test/helpers/test_helpers.dart
class MockUserRepository extends Mock implements UserRepository {}

extension WidgetTesterX on WidgetTester {
  Future<void> pumpApp(
    Widget widget, {
    List<Override> overrides = const [],
  }) {
    return pumpWidget(
      ProviderScope(
        overrides: overrides,
        child: MaterialApp(home: widget),
      ),
    );
  }
}

// Usage
testWidgets('test with mock', (tester) async {
  final mockRepo = MockUserRepository();
  when(mockRepo.getUsers()).thenAnswer((_) async => []);

  await tester.pumpApp(
    const UserListPage(),
    overrides: [
      userRepositoryProvider.overrideWithValue(mockRepo),
    ],
  );
});
```

## Test Commands

```bash
# Run all tests
flutter test

# Run with coverage
flutter test --coverage

# Generate coverage report
genhtml coverage/lcov.info -o coverage/html

# Run specific test file
flutter test test/unit/domain/usecases/get_user_test.dart

# Run integration tests
flutter test integration_test/app_test.dart

# Update golden files
flutter test --update-goldens
```

## Coverage Target: >80%

See `references/testing-patterns.md` for advanced mocking patterns.
See `references/test-fixtures.md` for fixture management.
