# 2026 Design Patterns

## Tactile Buttons ("Squishy")
Buttons that deform with physics-based `elasticOut` curves and provide haptic feedback.
```dart
SquishyButton(
  onPressed: () => print('Tapped'),
  leadingIcon: Icons.rocket,
  child: Text('Launch'),
)
```

**Implementation Details:**
```dart
AnimatedContainer(
  duration: Duration(milliseconds: 80), // <100ms required
  curve: Curves.elasticOut, 
  transform: _isPressed ? Matrix4.identity()..scale(0.95) : Matrix4.identity(),
  // ...
)
```

## Glassmorphism 2.0
Frosted glass with border highlights, used for floating overlays.
```dart
GlassCard(
  blur: 15,
  opacity: 0.15,
  child: Text('Frosted Overlay'),
)
```

**Key Code:**
```dart
BackdropFilter(
  filter: ImageFilter.blur(sigmaX: 15, sigmaY: 15),
  child: Container(
    decoration: BoxDecoration(
      color: Colors.white.withOpacity(0.1),
      border: Border.all(color: Colors.white.withOpacity(0.2)),
    ),
    // ...
  ),
)
```

## Bento Grid Layouts
Modular, magazine-style layouts. Use `ResponsiveBentoGrid` for automatic column adjustment.
```dart
ResponsiveBentoGrid(
  children: [
    BentoCard(featured: true, child: AnalyticsWidget()), // Large
    BentoCard(child: StatWidget()),                      // Small
    BentoCard(child: AnotherWidget()),                   // Small
  ],
)
```

## Skeleton Loaders (Progressive)
**Never** use spinners. Use shimmering skeletons.
```dart
// Individual element
SkeletonLoader(width: 200, height: 20)

// Complete Card
SkeletonCard(height: 120)
```

## Intent-Driven UI (Predictive)
Cards that proactively offer solutions.
```dart
PredictiveInsightCard(
  insight: '3 tasks are at risk of missing deadlines',
  actionLabel: 'Review Tasks',
  icon: Icons.warning_amber,
  onActionTap: () => navigateToTasks(),
)
```

## Semantic Banners
Context-aware alerts using semantic tokens.
```dart
SemanticBanner(
  message: 'Operation completed successfully',
  type: SemanticType.success, // or warning, error, info
  onDismiss: () {},
)
```
