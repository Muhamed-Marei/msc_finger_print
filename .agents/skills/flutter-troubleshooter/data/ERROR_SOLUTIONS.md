# Flutter Error Solutions Database

> **Auto-learning system**: When you encounter an error and find a solution, add it here!

---

## How to Use This File

1. **Search** for your error message (Cmd+F / Ctrl+F)
2. **Find** the solution
3. **Add new errors** when you solve them (helps future you!)

---

## Table of Contents

- [Build Errors](#build-errors)
- [Riverpod Errors](#riverpod-errors)
- [go_router Errors](#go_router-errors)
- [Freezed Errors](#freezed-errors)
- [Firebase Errors](#firebase-errors)
- [iOS Errors](#ios-errors)
- [Android Errors](#android-errors)
- [Dependency Conflicts](#dependency-conflicts)

---

## Build Errors

### Error: "The getter 'xxx' isn't defined for the type 'Ref'"

**Cause**: Riverpod 3.x changed how Ref works

**Solution**:
```dart
// OLD (Riverpod 2.x)
@riverpod
Future<User> user(UserRef ref) async { ... }

// NEW (Riverpod 3.x)
@riverpod
Future<User> user(Ref ref) async { ... }
```

---

### Error: "StateNotifierProvider is not defined"

**Cause**: Riverpod 3.0 moved legacy providers to separate import

**Solution**:
```dart
// Add this import for StateNotifierProvider
import 'package:flutter_riverpod/legacy.dart';

// Or migrate to new Notifier pattern (recommended)
@riverpod
class Counter extends _$Counter {
  @override
  int build() => 0;
  
  void increment() => state++;
}
```

---

### Error: "Part directive not found" after build_runner

**Cause**: Missing part directive or wrong filename

**Solution**:
```dart
// For freezed files, add:
part 'user_model.freezed.dart';
part 'user_model.g.dart';

// For riverpod files, add:
part 'user_provider.g.dart';

// Then run:
dart run build_runner build --delete-conflicting-outputs
```

---

## Riverpod Errors

### Error: "A provider was used after being disposed"

**Cause**: Accessing provider after widget unmounted

**Solution**:
```dart
// Check if mounted before using ref
@override
void initState() {
  super.initState();
  Future.microtask(() {
    if (mounted) {
      ref.read(someProvider);
    }
  });
}

// Or use ref.listen with proper lifecycle
ref.listen(someProvider, (prev, next) {
  if (!mounted) return;
  // handle state
});
```

---

### Error: "AsyncValue.value returns null during error"

**Cause**: Riverpod 3.0 changed AsyncValue.value behavior

**Solution**:
```dart
// OLD way (Riverpod 2.x)
final value = asyncValue.valueOrNull;

// NEW way (Riverpod 3.x)
final value = asyncValue.value;  // Returns null during loading/error

// Or handle all states explicitly
asyncValue.when(
  data: (value) => Text(value),
  loading: () => CircularProgressIndicator(),
  error: (e, st) => Text('Error: $e'),
);
```

---

### Error: "Notifier was used after being disposed"

**Cause**: Riverpod 3.0 recreates Notifier on rebuild

**Solution**:
```dart
// Use ref.mounted to check if still valid
class MyNotifier extends _$MyNotifier {
  @override
  Future<Data> build() async {
    final data = await fetchData();
    if (!ref.mounted) return data;  // Check before updating
    return data;
  }
}
```

---

## go_router Errors

### Error: "GoRouter redirect loop detected"

**Cause**: Redirect logic creates infinite loop

**Solution**:
```dart
GoRouter(
  redirect: (context, state) {
    final isLoggedIn = authState.isLoggedIn;
    final isOnLogin = state.matchedLocation == '/login';
    
    // IMPORTANT: Return null when no redirect needed
    if (!isLoggedIn && !isOnLogin) return '/login';
    if (isLoggedIn && isOnLogin) return '/';
    return null;  // <-- Must return null, not current path
  },
)
```

---

### Error: "Could not find a generator for route"

**Cause**: Route not defined or typo in path

**Solution**:
```dart
// Make sure route exists
GoRoute(
  path: '/user/:id',  // Note the colon for parameters
  builder: (context, state) {
    final id = state.pathParameters['id']!;
    return UserPage(id: id);
  },
)

// Navigate correctly
context.go('/user/123');  // Not '/user?id=123'
```

---

## Freezed Errors

### Error: "Could not generate fromJson for class"

**Cause**: Missing json_serializable annotation or import

**Solution**:
```dart
import 'package:freezed_annotation/freezed_annotation.dart';

part 'user.freezed.dart';
part 'user.g.dart';  // <-- Required for fromJson

@freezed
class User with _$User {
  const factory User({
    required String id,
    required String name,
  }) = _User;

  factory User.fromJson(Map<String, dynamic> json) => _$UserFromJson(json);
}
```

---

### Error: "The name '_$ClassName' is already defined"

**Cause**: Old generated files conflict

**Solution**:
```bash
# Delete all generated files and regenerate
flutter clean
find . -name "*.g.dart" -delete
find . -name "*.freezed.dart" -delete
dart run build_runner build --delete-conflicting-outputs
```

---

## Firebase Errors

### Error: "No Firebase App '[DEFAULT]' has been created"

**Cause**: Firebase not initialized before use

**Solution**:
```dart
void main() async {
  WidgetsFlutterBinding.ensureInitialized();  // Must be first!
  await Firebase.initializeApp(
    options: DefaultFirebaseOptions.currentPlatform,
  );
  runApp(MyApp());
}
```

---

### Error: "PlatformException: channel-error"

**Cause**: Firebase plugins not properly configured

**Solution**:
```bash
# iOS
cd ios && pod deintegrate && pod install && cd ..

# Android - Check google-services.json is in android/app/

# Then rebuild
flutter clean && flutter pub get
```

---

## iOS Errors

### Error: "No signing certificate iOS Distribution found"

**Cause**: Missing distribution certificate

**Solution**:
1. Open Xcode > Preferences > Accounts
2. Select your team
3. Click "Download Manual Profiles"
4. Or create certificate at developer.apple.com

---

### Error: "Minimum deployment target is X, but target is Y"

**Cause**: iOS version mismatch

**Solution**:
```ruby
# In ios/Podfile
platform :ios, '14.0'  # Set to required minimum

# Also in ios/Runner.xcodeproj/project.pbxproj
# IPHONEOS_DEPLOYMENT_TARGET = 14.0;

# Then:
cd ios && pod update && cd ..
```

---

## Android Errors

### Error: "Execution failed for task ':app:minifyReleaseWithR8'"

**Cause**: ProGuard/R8 removing needed classes

**Solution**:
```proguard
# In android/app/proguard-rules.pro
-keep class io.flutter.** { *; }
-keep class com.google.firebase.** { *; }

# For retrofit
-keepattributes Signature
-keepclassmembers,allowshrinking,allowobfuscation interface * {
    @retrofit2.http.* <methods>;
}
```

---

### Error: "Cannot fit requested classes in a single dex file"

**Cause**: Too many methods (>65k)

**Solution**:
```groovy
// In android/app/build.gradle
android {
    defaultConfig {
        multiDexEnabled true
    }
}

dependencies {
    implementation 'androidx.multidex:multidex:2.0.1'
}
```

---

## Dependency Conflicts

### Error: "version solving failed"

**Cause**: Package versions incompatible

**Solution**:
```bash
# Check what's conflicting
flutter pub deps

# Try upgrading all
flutter pub upgrade --major-versions

# Or override specific version (last resort)
# In pubspec.yaml:
dependency_overrides:
  collection: ^1.18.0
```

---

### Error: "collection package version conflict"

**Cause**: Riverpod requires collection ^1.18.0, Flutter pins 1.17.x

**Solution**:
```yaml
# Upgrade Flutter SDK to 3.16+ or add override:
dependency_overrides:
  collection: ^1.18.0
```

---

## Add Your Own Errors

### Error: "[YOUR ERROR MESSAGE]"

**Date**: YYYY-MM-DD
**Cause**: [What caused it]

**Solution**:
```
[Your solution here]
```

---

## Quick Reference Commands

```bash
# Clean everything
flutter clean && flutter pub get

# Regenerate code
dart run build_runner build --delete-conflicting-outputs

# iOS clean
cd ios && pod deintegrate && pod install && cd ..

# Android clean  
cd android && ./gradlew clean && cd ..

# Check dependencies
flutter pub outdated
flutter pub deps
```
