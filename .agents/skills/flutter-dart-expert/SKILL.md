---
name: flutter-dart-expert
description: |
  Flutter Dart & Performance Expert Agent - Writes high-performance Dart code with proper OOP/OOD, data structures, algorithms, and optimization techniques.
  TRIGGERS: performance optimization, Dart code, OOP, algorithms, data structures, memory optimization, 60 FPS, build optimization, const constructors, widget rebuilds, profiling, lazy loading
---

# Flutter Dart & Performance Expert Agent

You are the Dart & Performance Expert. Write efficient code and optimize performance.

## Performance Targets

- **Frame rate**: 60 FPS (16ms per frame)
- **App size**: Minimize APK/IPA size
- **Memory**: Efficient memory usage, no leaks
- **Startup**: Fast cold start time

## Const Everything

```dart
// GOOD: Const constructors prevent rebuilds
class MyWidget extends StatelessWidget {
  const MyWidget({super.key}); // Add const constructor
  
  @override
  Widget build(BuildContext context) {
    return const Column(  // const Column
      children: [
        Text('Hello'),    // const Text
        SizedBox(height: 8),  // const SizedBox
        Icon(Icons.star),     // const Icon
      ],
    );
  }
}

// Usage: Always use const when creating widgets
const MyWidget()  // Not: MyWidget()
```

## Efficient Lists

```dart
// BAD: Creates all items upfront
ListView(
  children: items.map((i) => ItemWidget(i)).toList(),
)

// GOOD: Lazy builds only visible items
ListView.builder(
  itemCount: items.length,
  itemBuilder: (context, index) => ItemWidget(items[index]),
)

// BETTER: With cacheExtent for smoother scrolling
ListView.builder(
  itemCount: items.length,
  cacheExtent: 100,  // Pre-build items 100 pixels away
  itemBuilder: (context, index) => ItemWidget(items[index]),
)

// Sliver for complex scrolling
CustomScrollView(
  slivers: [
    SliverAppBar(...),
    SliverList(
      delegate: SliverChildBuilderDelegate(
        (context, index) => ItemWidget(items[index]),
        childCount: items.length,
      ),
    ),
  ],
)
```

## Widget Rebuild Optimization

```dart
// BAD: Function creates new widget on every build
Widget build(BuildContext context) {
  return Column(
    children: [
      _buildHeader(),  // New instance every time
    ],
  );
}

// GOOD: Extract to separate widget class
class HeaderWidget extends StatelessWidget {
  const HeaderWidget({super.key});
  
  @override
  Widget build(BuildContext context) => ...;
}

// GOOD: Cache computed values
class MyWidget extends StatelessWidget {
  // Cache expensive computation
  static final _processedData = _computeExpensive();
}
```

## Async Best Practices

```dart
// Use async/await properly
Future<void> loadData() async {
  // Parallel execution for independent operations
  final results = await Future.wait([
    fetchUsers(),
    fetchProducts(),
    fetchSettings(),
  ]);
  
  // Sequential for dependent operations
  final user = await fetchUser();
  final orders = await fetchOrders(user.id);
}

// Cancel operations when widget disposes
class _MyState extends State<MyWidget> {
  CancelableOperation<Data>? _operation;
  
  void _load() {
    _operation?.cancel();
    _operation = CancelableOperation.fromFuture(fetchData());
    _operation!.value.then((data) {
      if (mounted) setState(() => _data = data);
    });
  }
  
  @override
  void dispose() {
    _operation?.cancel();
    super.dispose();
  }
}

// Stream subscriptions
StreamSubscription? _subscription;

@override
void initState() {
  super.initState();
  _subscription = stream.listen((data) {
    if (mounted) setState(() => _data = data);
  });
}

@override
void dispose() {
  _subscription?.cancel();
  super.dispose();
}
```

## Image Optimization

```dart
// Cache network images
CachedNetworkImage(
  imageUrl: url,
  placeholder: (context, url) => const ShimmerPlaceholder(),
  errorWidget: (context, url, error) => const Icon(Icons.error),
  memCacheWidth: 200,  // Resize in memory
)

// Precache images
@override
void didChangeDependencies() {
  super.didChangeDependencies();
  precacheImage(AssetImage('assets/large_image.png'), context);
}

// Use appropriate image formats
// - PNG for images with transparency
// - JPEG for photos
// - WebP for best compression (Android/Web)
```

## Collection Best Practices

```dart
// Use efficient collections
final Map<String, User> userMap = {};  // O(1) lookup
final Set<String> uniqueIds = {};       // O(1) contains

// Avoid repeated list searches
// BAD
for (final item in items) {
  if (otherItems.contains(item.id)) { ... }  // O(n) each time
}

// GOOD
final otherSet = otherItems.map((e) => e.id).toSet();
for (final item in items) {
  if (otherSet.contains(item.id)) { ... }  // O(1) each time
}

// Lazy iteration with Iterable
Iterable<Widget> buildItems() sync* {
  for (final item in items) {
    yield ItemWidget(item);  // Built on demand
  }
}
```

## Memory Management

```dart
// Dispose controllers
class _MyState extends State<MyWidget> {
  late final TextEditingController _controller;
  late final AnimationController _animation;
  
  @override
  void initState() {
    super.initState();
    _controller = TextEditingController();
    _animation = AnimationController(vsync: this);
  }
  
  @override
  void dispose() {
    _controller.dispose();
    _animation.dispose();
    super.dispose();
  }
}

// Avoid memory leaks with closures
// BAD: Captures entire widget
onTap: () => _handleTap(widget.item)

// GOOD: Extract method
onTap: _handleTap
void _handleTap() => doSomething(widget.item);
```

## Isolates for Heavy Work

```dart
// Move heavy computation off main thread
Future<List<ProcessedItem>> processData(List<RawItem> items) async {
  return compute(_processInBackground, items);
}

List<ProcessedItem> _processInBackground(List<RawItem> items) {
  // Heavy computation here
  return items.map((item) => ProcessedItem.from(item)).toList();
}

// For streaming results
Stream<int> heavyComputation() async* {
  for (int i = 0; i < 1000000; i++) {
    yield i;
    if (i % 10000 == 0) await Future.delayed(Duration.zero);
  }
}
```

## Profiling Commands

```bash
# Run with performance overlay
flutter run --profile

# Analyze APK size
flutter build apk --analyze-size

# Generate DevTools timeline
flutter run --profile --trace-startup
```

See `references/performance-checklist.md` for review guidelines.
See `references/dart-patterns.md` for design pattern implementations.
