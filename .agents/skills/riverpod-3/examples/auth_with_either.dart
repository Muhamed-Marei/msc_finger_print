// AUTHENTICATION WITH FUNCTIONAL ERROR HANDLING (fpdart Either)
// Complete architecture: Repository → Notifier → UI

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:riverpod_annotation/riverpod_annotation.dart';
import 'package:firebase_auth/firebase_auth.dart' as firebase_auth;
import 'package:fpdart/fpdart.dart';

part 'auth_with_either.g.dart';

// ============================================================================
// DOMAIN MODELS
// ============================================================================

class User {
  final String uid;
  final String email;
  final String? displayName;

  User({required this.uid, required this.email, this.displayName});

  factory User.fromFirebase(firebase_auth.User firebaseUser) => User(
    uid: firebaseUser.uid,
    email: firebaseUser.email!,
    displayName: firebaseUser.displayName,
  );
}

// ============================================================================
// DOMAIN FAILURES (Exhaustive Error Types)
// ============================================================================

sealed class AuthFailure {
  const AuthFailure();

  String get message => switch (this) {
    InvalidCredentials() => 'Invalid email or password',
    EmailAlreadyInUse() => 'This email is already registered',
    WeakPassword() => 'Password must be at least 6 characters',
    NetworkError() => 'Network connection failed',
    UnknownError(:final message) => message,
  };
}

class InvalidCredentials extends AuthFailure {}
class EmailAlreadyInUse extends AuthFailure {}
class WeakPassword extends AuthFailure {}
class NetworkError extends AuthFailure {}
class UnknownError extends AuthFailure {
  final String message;
  const UnknownError([this.message = 'An unexpected error occurred']);
}

// ============================================================================
// REPOSITORY LAYER (Always Returns Either)
// ============================================================================

abstract class AuthRepository {
  Future<Either<AuthFailure, User>> signIn(String email, String password);
  Future<Either<AuthFailure, User>> signUp(String email, String password);
  Future<Either<AuthFailure, void>> signOut();
  Stream<User?> authStateChanges();
}

@riverpod
AuthRepository authRepository(Ref ref) => FirebaseAuthRepository(
  auth: ref.watch(firebaseAuthProvider),
);

@Riverpod(keepAlive: true)
firebase_auth.FirebaseAuth firebaseAuth(Ref ref) => firebase_auth.FirebaseAuth.instance;

class FirebaseAuthRepository implements AuthRepository {
  final firebase_auth.FirebaseAuth auth;

  FirebaseAuthRepository({required this.auth});

  @override
  Future<Either<AuthFailure, User>> signIn(String email, String password) async {
    try {
      final credential = await auth.signInWithEmailAndPassword(
        email: email,
        password: password,
      );
      return right(User.fromFirebase(credential.user!));
    } on firebase_auth.FirebaseAuthException catch (e) {
      return left(_mapFirebaseError(e.code));
    } catch (e) {
      return left(NetworkError());
    }
  }

  @override
  Future<Either<AuthFailure, User>> signUp(String email, String password) async {
    try {
      final credential = await auth.createUserWithEmailAndPassword(
        email: email,
        password: password,
      );
      return right(User.fromFirebase(credential.user!));
    } on firebase_auth.FirebaseAuthException catch (e) {
      return left(_mapFirebaseError(e.code));
    } catch (e) {
      return left(NetworkError());
    }
  }

  @override
  Future<Either<AuthFailure, void>> signOut() async {
    try {
      await auth.signOut();
      return right(null);
    } catch (e) {
      return left(UnknownError('Sign out failed'));
    }
  }

  @override
  Stream<User?> authStateChanges() {
    return auth.authStateChanges().map((firebaseUser) =>
      firebaseUser != null ? User.fromFirebase(firebaseUser) : null
    );
  }

  AuthFailure _mapFirebaseError(String code) => switch (code) {
    'user-not-found' => InvalidCredentials(),
    'wrong-password' => InvalidCredentials(),
    'invalid-credential' => InvalidCredentials(),
    'email-already-in-use' => EmailAlreadyInUse(),
    'weak-password' => WeakPassword(),
    'network-request-failed' => NetworkError(),
    _ => UnknownError('Firebase error: $code'),
  };
}

// ============================================================================
// STATE LAYER: AUTH STREAM (Passive State)
// ============================================================================

@Riverpod(keepAlive: true)
Stream<User?> authStateChanges(Ref ref) {
  final repository = ref.watch(authRepositoryProvider);
  return repository.authStateChanges();
}

// ============================================================================
// STATE LAYER: AUTH CONTROLLER (Active State - Actions)
// ============================================================================

@riverpod
class AuthController extends _$AuthController {
  @override
  Future<User?> build() async {
    // Initialization: listen to auth state
    final authStream = ref.watch(authStateChangesProvider);

    // Return current user (if any)
    return authStream.value;
  }

  Future<void> signIn(String email, String password) async {
    // 1. Set loading state
    state = const AsyncLoading();

    // 2. Call repository
    final repository = ref.read(authRepositoryProvider);
    final result = await repository.signIn(email, password);

    // 3. Fold Either into AsyncValue
    state = result.fold(
      (failure) => AsyncError(failure, StackTrace.current),
      (user) => AsyncData(user),
    );
  }

  Future<void> signUp(String email, String password) async {
    state = const AsyncLoading();

    final repository = ref.read(authRepositoryProvider);
    final result = await repository.signUp(email, password);

    state = result.fold(
      (failure) => AsyncError(failure, StackTrace.current),
      (user) => AsyncData(user),
    );
  }

  Future<void> signOut() async {
    final repository = ref.read(authRepositoryProvider);
    final result = await repository.signOut();

    result.fold(
      (failure) {
        // Even if sign-out fails, we might want to clear local state
        state = const AsyncData(null);
      },
      (_) => state = const AsyncData(null),
    );
  }
}

// ============================================================================
// UI LAYER: LOGIN SCREEN
// ============================================================================

class LoginScreen extends ConsumerStatefulWidget {
  @override
  ConsumerState<LoginScreen> createState() => _LoginScreenState();
}

class _LoginScreenState extends ConsumerState<LoginScreen> {
  final _emailController = TextEditingController();
  final _passwordController = TextEditingController();

  @override
  void dispose() {
    _emailController.dispose();
    _passwordController.dispose();
    super.dispose();
  }

  void _signIn() {
    ref.read(authControllerProvider.notifier).signIn(
      _emailController.text.trim(),
      _passwordController.text,
    );
  }

  @override
  Widget build(BuildContext context) {
    final authState = ref.watch(authControllerProvider);

    // Listen for errors to show SnackBar
    ref.listen<AsyncValue<User?>>(
      authControllerProvider,
      (previous, next) {
        next.whenData((user) {
          if (user != null) {
            // Navigate to home on successful login
            Navigator.of(context).pushReplacementNamed('/home');
          }
        });
      },
    );

    return Scaffold(
      appBar: AppBar(title: Text('Sign In')),
      body: Padding(
        padding: EdgeInsets.all(16),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            // Email field
            TextField(
              controller: _emailController,
              decoration: InputDecoration(
                labelText: 'Email',
                errorText: authState.error is AuthFailure
                  ? null // Show error below form, not per-field
                  : null,
              ),
              keyboardType: TextInputType.emailAddress,
              enabled: !authState.isLoading,
            ),
            SizedBox(height: 16),

            // Password field
            TextField(
              controller: _passwordController,
              decoration: InputDecoration(labelText: 'Password'),
              obscureText: true,
              enabled: !authState.isLoading,
              onSubmitted: (_) => _signIn(),
            ),
            SizedBox(height: 24),

            // Error display
            if (authState.hasError)
              Container(
                padding: EdgeInsets.all(12),
                decoration: BoxDecoration(
                  color: Colors.red.shade50,
                  borderRadius: BorderRadius.circular(8),
                ),
                child: Row(
                  children: [
                    Icon(Icons.error, color: Colors.red),
                    SizedBox(width: 8),
                    Expanded(
                      child: Text(
                        (authState.error as AuthFailure).message,
                        style: TextStyle(color: Colors.red.shade900),
                      ),
                    ),
                  ],
                ),
              ),
            SizedBox(height: 16),

            // Sign In button
            SizedBox(
              width: double.infinity,
              child: ElevatedButton(
                onPressed: authState.isLoading ? null : _signIn,
                child: authState.isLoading
                  ? SizedBox(
                      height: 20,
                      width: 20,
                      child: CircularProgressIndicator(strokeWidth: 2),
                    )
                  : Text('Sign In'),
              ),
            ),

            SizedBox(height: 8),

            // Sign Up link
            TextButton(
              onPressed: () => Navigator.of(context).pushNamed('/signup'),
              child: Text('Don\'t have an account? Sign Up'),
            ),
          ],
        ),
      ),
    );
  }
}

// ============================================================================
// UI LAYER: APP ROOT (Auth Gate)
// ============================================================================

class AppRoot extends ConsumerWidget {
  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final authState = ref.watch(authStateChangesProvider);

    return authState.when(
      data: (user) => user != null
        ? HomeScreen(user: user)
        : LoginScreen(),
      loading: () => Scaffold(
        body: Center(child: CircularProgressIndicator()),
      ),
      error: (error, stackTrace) => Scaffold(
        body: Center(
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              Icon(Icons.error, size: 64, color: Colors.red),
              SizedBox(height: 16),
              Text('Authentication initialization failed'),
              SizedBox(height: 8),
              ElevatedButton(
                onPressed: () => ref.invalidate(authStateChangesProvider),
                child: Text('Retry'),
              ),
            ],
          ),
        ),
      ),
    );
  }
}

class HomeScreen extends StatelessWidget {
  final User user;

  const HomeScreen({required this.user});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text('Home'),
        actions: [
          IconButton(
            icon: Icon(Icons.logout),
            onPressed: () => context.read(authControllerProvider.notifier).signOut(),
          ),
        ],
      ),
      body: Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Text('Welcome, ${user.displayName ?? user.email}!'),
          ],
        ),
      ),
    );
  }
}

// Extension for easy context.read
extension WidgetRefExtension on BuildContext {
  T read<T>(ProviderListenable<T> provider) {
    return ProviderScope.containerOf(this).read(provider);
  }
}
