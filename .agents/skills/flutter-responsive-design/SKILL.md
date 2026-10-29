---
name: flutter-responsive-design
description: |
  Responsive & Adaptive Design Expert - Multi-platform layouts for mobile, tablet, web, desktop.
  TRIGGERS: responsive, adaptive, layout, screen size, breakpoint, mobile, tablet, web, desktop
---

# Flutter Responsive Design Expert

## Breakpoints
```dart
class Breakpoints {
  static const double mobile = 600;
  static const double tablet = 900;
  static const double desktop = 1200;

  static bool isMobile(BuildContext context) =>
    MediaQuery.sizeOf(context).width < mobile;
  static bool isTablet(BuildContext context) =>
    MediaQuery.sizeOf(context).width >= mobile &&
    MediaQuery.sizeOf(context).width < desktop;
  static bool isDesktop(BuildContext context) =>
    MediaQuery.sizeOf(context).width >= desktop;
}
```

## Responsive Builder
```dart
class ResponsiveBuilder extends StatelessWidget {
  final Widget mobile;
  final Widget? tablet;
  final Widget? desktop;

  const ResponsiveBuilder({
    required this.mobile,
    this.tablet,
    this.desktop,
  });

  @override
  Widget build(BuildContext context) {
    return LayoutBuilder(
      builder: (context, constraints) {
        if (constraints.maxWidth >= Breakpoints.desktop) {
          return desktop ?? tablet ?? mobile;
        } else if (constraints.maxWidth >= Breakpoints.mobile) {
          return tablet ?? mobile;
        }
        return mobile;
      },
    );
  }
}
```

## Adaptive Layouts

### Navigation
```dart
// Mobile: BottomNavigationBar
// Tablet: NavigationRail
// Desktop: NavigationDrawer (permanent)

class AdaptiveScaffold extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return ResponsiveBuilder(
      mobile: Scaffold(
        body: content,
        bottomNavigationBar: BottomNavigationBar(...),
      ),
      tablet: Scaffold(
        body: Row(
          children: [
            NavigationRail(...),
            Expanded(child: content),
          ],
        ),
      ),
      desktop: Scaffold(
        body: Row(
          children: [
            NavigationDrawer(...),
            Expanded(child: content),
          ],
        ),
      ),
    );
  }
}
```

### Grid Systems
```dart
// Responsive grid
GridView.builder(
  gridDelegate: SliverGridDelegateWithFixedCrossAxisCount(
    crossAxisCount: Breakpoints.isMobile(context) ? 2 :
                   Breakpoints.isTablet(context) ? 3 : 4,
    childAspectRatio: 1.0,
  ),
  itemBuilder: (context, index) => ItemCard(),
)
```

## Platform Detection
```dart
import 'dart:io' show Platform;
import 'package:flutter/foundation.dart' show kIsWeb;

bool get isMobileDevice => !kIsWeb && (Platform.isIOS || Platform.isAndroid);
bool get isDesktopDevice => !kIsWeb && (Platform.isMacOS || Platform.isWindows || Platform.isLinux);
bool get isWebPlatform => kIsWeb;
```

## Best Practices

| Aspect | Mobile | Tablet | Desktop |
|--------|--------|--------|---------|
| Navigation | Bottom bar | Rail | Drawer |
| Grid columns | 1-2 | 2-3 | 4+ |
| Touch targets | 48dp min | 44dp | 36dp |
| Font scaling | 1.0x | 1.0x | 0.9-1.0x |
