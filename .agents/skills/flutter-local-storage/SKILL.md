---
name: flutter-local-storage
description: |
  Local Storage Expert - SQLite, Hive, SharedPreferences, secure storage, caching.
  TRIGGERS: local storage, SQLite, Hive, SharedPreferences, cache, database, persist, offline
---

# Flutter Local Storage Expert

## Quick Selection Guide

| Use Case | Solution |
|----------|----------|
| Simple key-value | SharedPreferences |
| Structured data (fast) | Hive |
| Complex queries | SQLite (drift/sqflite) |
| Sensitive data | flutter_secure_storage |
| Large files/images | File system + path_provider |

## SharedPreferences
```dart
// Simple key-value storage
final prefs = await SharedPreferences.getInstance();

// Write
await prefs.setString('username', 'john');
await prefs.setInt('age', 25);
await prefs.setBool('darkMode', true);
await prefs.setStringList('tags', ['flutter', 'dart']);

// Read
final username = prefs.getString('username') ?? '';
final age = prefs.getInt('age') ?? 0;
final darkMode = prefs.getBool('darkMode') ?? false;

// Remove
await prefs.remove('username');
await prefs.clear(); // Remove all
```

## Hive (NoSQL - Fast)
```dart
// Setup
await Hive.initFlutter();
Hive.registerAdapter(UserAdapter());
final box = await Hive.openBox<User>('users');

// CRUD
box.put('user1', User(name: 'John', age: 25));
final user = box.get('user1');
box.delete('user1');

// Type adapters (generate with build_runner)
@HiveType(typeId: 0)
class User extends HiveObject {
  @HiveField(0)
  String name;

  @HiveField(1)
  int age;
}
```

## SQLite with Drift
```dart
// Define tables
class Users extends Table {
  IntColumn get id => integer().autoIncrement()();
  TextColumn get name => text().withLength(min: 1, max: 50)();
  IntColumn get age => integer().nullable()();
  DateTimeColumn get createdAt => dateTime().withDefault(currentDateAndTime)();
}

// Database class
@DriftDatabase(tables: [Users])
class AppDatabase extends _$AppDatabase {
  AppDatabase() : super(_openConnection());

  @override
  int get schemaVersion => 1;

  // Queries
  Future<List<User>> getAllUsers() => select(users).get();
  Future<User?> getUserById(int id) =>
    (select(users)..where((u) => u.id.equals(id))).getSingleOrNull();
  Future<int> insertUser(UsersCompanion user) => into(users).insert(user);
  Future<bool> updateUser(User user) => update(users).replace(user);
  Future<int> deleteUser(int id) =>
    (delete(users)..where((u) => u.id.equals(id))).go();
}
```

## Secure Storage
```dart
import 'package:flutter_secure_storage/flutter_secure_storage.dart';

final storage = FlutterSecureStorage(
  aOptions: AndroidOptions(encryptedSharedPreferences: true),
  iOptions: IOSOptions(accessibility: KeychainAccessibility.first_unlock),
);

// Store sensitive data
await storage.write(key: 'token', value: 'jwt_token_here');
await storage.write(key: 'pin', value: '1234');

// Read
final token = await storage.read(key: 'token');

// Delete
await storage.delete(key: 'token');
await storage.deleteAll();
```

## File Storage
```dart
import 'package:path_provider/path_provider.dart';
import 'dart:io';

// Get directories
final appDir = await getApplicationDocumentsDirectory();
final cacheDir = await getTemporaryDirectory();
final downloadsDir = await getDownloadsDirectory(); // Desktop only

// Write file
final file = File('${appDir.path}/data.json');
await file.writeAsString(jsonEncode(data));

// Read file
final contents = await file.readAsString();
final data = jsonDecode(contents);

// Check exists
if (await file.exists()) { ... }
```

## Caching Strategy
```dart
class CacheManager {
  final box = Hive.box('cache');
  final Duration maxAge;

  Future<T?> get<T>(String key) async {
    final cached = box.get(key);
    if (cached == null) return null;

    final timestamp = DateTime.parse(cached['timestamp']);
    if (DateTime.now().difference(timestamp) > maxAge) {
      await box.delete(key);
      return null;
    }
    return cached['data'] as T;
  }

  Future<void> set(String key, dynamic data) async {
    await box.put(key, {
      'data': data,
      'timestamp': DateTime.now().toIso8601String(),
    });
  }
}
```

## Packages
```yaml
dependencies:
  shared_preferences: ^2.2.0
  hive: ^2.2.3
  hive_flutter: ^1.1.0
  drift: ^2.12.0
  flutter_secure_storage: ^9.0.0
  path_provider: ^2.1.0

dev_dependencies:
  hive_generator: ^2.0.0
  drift_dev: ^2.12.0
  build_runner: ^2.4.0
```
