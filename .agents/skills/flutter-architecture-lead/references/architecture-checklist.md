# Architecture Review Checklist

## Pre-Review Setup
- [ ] Understand feature requirements
- [ ] Review existing related features
- [ ] Check for shared components

## Domain Layer Review
- [ ] Entities are pure Dart (no Flutter imports)
- [ ] Entities use Freezed for immutability
- [ ] Repository interfaces defined (not implementations)
- [ ] Usecases follow single responsibility
- [ ] Failure types properly defined
- [ ] No business logic leaking to other layers

## Data Layer Review
- [ ] Models have toEntity() and fromJson()
- [ ] Repository implementations handle all error cases
- [ ] DataSources properly separated (remote/local)
- [ ] Caching strategy implemented where needed
- [ ] Network connectivity handled

## Presentation Layer Review
- [ ] ViewModels use Riverpod providers
- [ ] UI state properly managed
- [ ] Loading/Error/Success states handled
- [ ] Widgets are as stateless as possible
- [ ] No business logic in widgets

## Dependency Injection Review
- [ ] All dependencies registered in GetIt
- [ ] Proper scoping (singleton/factory)
- [ ] Feature dependencies isolated
- [ ] Easy to mock for testing

## Common Violations to Watch

### Layer Violation Examples
```dart
// BAD: Domain importing Flutter
import 'package:flutter/material.dart'; // VIOLATION
class User { ... }

// BAD: Domain importing Data layer
import '../data/models/user_model.dart'; // VIOLATION
class GetUser { ... }

// BAD: Business logic in Widget
class UserPage extends StatelessWidget {
  // VIOLATION: Logic should be in ViewModel
  String formatName(User u) => '${u.first} ${u.last}';
}
```

### Correct Patterns
```dart
// GOOD: Pure Dart entity
class User {
  final String id;
  final String name;
  const User({required this.id, required this.name});
}

// GOOD: Logic in ViewModel
final userNameProvider = Provider<String>((ref) {
  final user = ref.watch(userProvider);
  return '${user.first} ${user.last}';
});
```
