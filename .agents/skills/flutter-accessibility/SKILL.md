---
name: flutter-accessibility
description: |
  Accessibility Expert - Screen readers, semantic widgets, inclusive design, a11y compliance.
  TRIGGERS: accessibility, a11y, screen reader, semantics, inclusive, VoiceOver, TalkBack
---

# Flutter Accessibility Expert

## Semantic Widgets

### Labels & Descriptions
```dart
Semantics(
  label: 'Play video',
  hint: 'Double tap to play',
  button: true,
  child: IconButton(
    icon: Icon(Icons.play_arrow),
    onPressed: _playVideo,
  ),
)

// Or use semantic properties
IconButton(
  icon: Icon(Icons.play_arrow),
  onPressed: _playVideo,
  tooltip: 'Play video', // Auto-generates semantics
)
```

### Images
```dart
// Decorative (ignored by screen readers)
Image.asset('background.png', semanticLabel: null,
  excludeFromSemantics: true,
)

// Informative
Image.asset('chart.png',
  semanticLabel: 'Sales increased 25% in Q4',
)
```

### Custom Semantics
```dart
Semantics(
  label: 'User profile',
  value: 'John Doe',
  hint: 'Double tap to view profile',
  child: UserCard(user),
)

// Grouping
MergeSemantics(
  child: Row(
    children: [
      Icon(Icons.star),
      Text('4.5 rating'),
    ],
  ),
)

// Excluding
ExcludeSemantics(
  child: DecorativeWidget(),
)
```

## Text & Contrast

### Scalable Text
```dart
// Respect user font size settings
Text(
  'Hello',
  style: TextStyle(fontSize: 16),
  textScaler: MediaQuery.textScalerOf(context),
)

// Limit scaling for layouts
MediaQuery(
  data: MediaQuery.of(context).copyWith(
    textScaler: TextScaler.linear(
      MediaQuery.textScalerOf(context).scale(1.0).clamp(1.0, 1.5),
    ),
  ),
  child: child,
)
```

### Contrast Ratios
```dart
// WCAG Requirements:
// Normal text: 4.5:1 minimum
// Large text (18sp+): 3:1 minimum

// Good contrast pairs
const goodContrast = {
  'text': Color(0xFF1A1A1A),      // Dark gray on white
  'background': Color(0xFFFFFFFF),
};
```

## Touch Targets
```dart
// Minimum 48x48 dp touch target
SizedBox(
  width: 48,
  height: 48,
  child: IconButton(
    icon: Icon(Icons.close),
    onPressed: _close,
  ),
)

// Or use padding
Padding(
  padding: EdgeInsets.all(12),
  child: Icon(Icons.close, size: 24),
)
```

## Focus Management
```dart
// Custom focus order
FocusTraversalGroup(
  policy: OrderedTraversalPolicy(),
  child: Column(
    children: [
      FocusTraversalOrder(order: NumericFocusOrder(1), child: TextField1()),
      FocusTraversalOrder(order: NumericFocusOrder(2), child: TextField2()),
      FocusTraversalOrder(order: NumericFocusOrder(3), child: SubmitButton()),
    ],
  ),
)

// Request focus
FocusScope.of(context).requestFocus(myFocusNode);
```

## Testing Accessibility
```dart
testWidgets('has correct semantics', (tester) async {
  await tester.pumpWidget(MyApp());

  expect(
    tester.getSemantics(find.byType(PlayButton)),
    matchesSemantics(
      label: 'Play video',
      isButton: true,
      hasEnabledState: true,
      isEnabled: true,
    ),
  );
});
```

## Checklist

| Item | Check |
|------|-------|
| All images have semanticLabel | ☐ |
| Touch targets ≥ 48dp | ☐ |
| Color contrast ≥ 4.5:1 | ☐ |
| Text scales properly | ☐ |
| Focus order logical | ☐ |
| Screen reader tested | ☐ |
