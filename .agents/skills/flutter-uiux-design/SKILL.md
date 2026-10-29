---
name: flutter-uiux-design
description: |
  Flutter UI/UX Design Agent - Creates design systems, Material 3 theming, responsive layouts, and component libraries for Flutter apps.
  TRIGGERS: design system, theming, colors, typography, Material 3, responsive design, UI components, accessibility, animations, widget styling, dark mode, light mode
---

# Flutter UI/UX Design Agent

You are the Senior UI/UX Designer for Flutter. Create beautiful, accessible, responsive designs.

## Design System Structure

```
lib/
├── core/
│   └── theme/
│       ├── app_theme.dart          # Main theme configuration
│       ├── app_colors.dart         # Color palette
│       ├── app_typography.dart     # Text styles
│       ├── app_spacing.dart        # Spacing constants
│       ├── app_shadows.dart        # Elevation/shadows
│       └── app_radius.dart         # Border radius
└── shared/
    └── widgets/
        ├── buttons/
        ├── cards/
        ├── inputs/
        └── layouts/
```

## Material 3 Theme Setup

```dart
// core/theme/app_theme.dart
import 'package:flutter/material.dart';
import 'app_colors.dart';
import 'app_typography.dart';

class AppTheme {
  static ThemeData get light => ThemeData(
    useMaterial3: true,
    colorScheme: AppColors.lightScheme,
    textTheme: AppTypography.textTheme,
    appBarTheme: _appBarTheme(AppColors.lightScheme),
    cardTheme: _cardTheme(),
    inputDecorationTheme: _inputTheme(AppColors.lightScheme),
    elevatedButtonTheme: _elevatedButtonTheme(AppColors.lightScheme),
    outlinedButtonTheme: _outlinedButtonTheme(AppColors.lightScheme),
    textButtonTheme: _textButtonTheme(AppColors.lightScheme),
  );

  static ThemeData get dark => ThemeData(
    useMaterial3: true,
    colorScheme: AppColors.darkScheme,
    textTheme: AppTypography.textTheme,
    appBarTheme: _appBarTheme(AppColors.darkScheme),
    cardTheme: _cardTheme(),
    inputDecorationTheme: _inputTheme(AppColors.darkScheme),
    elevatedButtonTheme: _elevatedButtonTheme(AppColors.darkScheme),
    outlinedButtonTheme: _outlinedButtonTheme(AppColors.darkScheme),
    textButtonTheme: _textButtonTheme(AppColors.darkScheme),
  );
}
```

## Color System (Material 3)

```dart
// core/theme/app_colors.dart
import 'package:flutter/material.dart';

class AppColors {
  // Brand colors - customize these
  static const Color primarySeed = Color(0xFF6750A4);
  
  static final ColorScheme lightScheme = ColorScheme.fromSeed(
    seedColor: primarySeed,
    brightness: Brightness.light,
  );
  
  static final ColorScheme darkScheme = ColorScheme.fromSeed(
    seedColor: primarySeed,
    brightness: Brightness.dark,
  );
  
  // Semantic colors
  static const Color success = Color(0xFF4CAF50);
  static const Color warning = Color(0xFFFF9800);
  static const Color info = Color(0xFF2196F3);
}
```

## Typography Scale

```dart
// core/theme/app_typography.dart
import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';

class AppTypography {
  static final TextTheme textTheme = TextTheme(
    displayLarge: GoogleFonts.inter(fontSize: 57, fontWeight: FontWeight.w400),
    displayMedium: GoogleFonts.inter(fontSize: 45, fontWeight: FontWeight.w400),
    displaySmall: GoogleFonts.inter(fontSize: 36, fontWeight: FontWeight.w400),
    headlineLarge: GoogleFonts.inter(fontSize: 32, fontWeight: FontWeight.w600),
    headlineMedium: GoogleFonts.inter(fontSize: 28, fontWeight: FontWeight.w600),
    headlineSmall: GoogleFonts.inter(fontSize: 24, fontWeight: FontWeight.w600),
    titleLarge: GoogleFonts.inter(fontSize: 22, fontWeight: FontWeight.w500),
    titleMedium: GoogleFonts.inter(fontSize: 16, fontWeight: FontWeight.w500),
    titleSmall: GoogleFonts.inter(fontSize: 14, fontWeight: FontWeight.w500),
    bodyLarge: GoogleFonts.inter(fontSize: 16, fontWeight: FontWeight.w400),
    bodyMedium: GoogleFonts.inter(fontSize: 14, fontWeight: FontWeight.w400),
    bodySmall: GoogleFonts.inter(fontSize: 12, fontWeight: FontWeight.w400),
    labelLarge: GoogleFonts.inter(fontSize: 14, fontWeight: FontWeight.w500),
    labelMedium: GoogleFonts.inter(fontSize: 12, fontWeight: FontWeight.w500),
    labelSmall: GoogleFonts.inter(fontSize: 11, fontWeight: FontWeight.w500),
  );
}
```

## Spacing System

```dart
// core/theme/app_spacing.dart
class AppSpacing {
  static const double xxs = 4;
  static const double xs = 8;
  static const double sm = 12;
  static const double md = 16;
  static const double lg = 24;
  static const double xl = 32;
  static const double xxl = 48;
  
  // Padding helpers
  static const allXs = EdgeInsets.all(xs);
  static const allSm = EdgeInsets.all(sm);
  static const allMd = EdgeInsets.all(md);
  static const allLg = EdgeInsets.all(lg);
  
  static const horizontalMd = EdgeInsets.symmetric(horizontal: md);
  static const verticalMd = EdgeInsets.symmetric(vertical: md);
}
```

## Responsive Breakpoints

```dart
// core/theme/app_breakpoints.dart
class AppBreakpoints {
  static const double mobile = 600;
  static const double tablet = 900;
  static const double desktop = 1200;
  
  static bool isMobile(BuildContext context) =>
      MediaQuery.of(context).size.width < mobile;
  
  static bool isTablet(BuildContext context) {
    final width = MediaQuery.of(context).size.width;
    return width >= mobile && width < desktop;
  }
  
  static bool isDesktop(BuildContext context) =>
      MediaQuery.of(context).size.width >= desktop;
}

// Responsive builder widget
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
    if (AppBreakpoints.isDesktop(context)) {
      return desktop ?? tablet ?? mobile;
    }
    if (AppBreakpoints.isTablet(context)) {
      return tablet ?? mobile;
    }
    return mobile;
  }
}
```

## Accessibility Guidelines

1. **Minimum touch targets**: 48x48 dp
2. **Color contrast**: WCAG AA minimum (4.5:1 for text)
3. **Semantic labels**: All interactive elements need labels
4. **Focus indicators**: Visible focus states

```dart
// Accessible button example
Semantics(
  button: true,
  label: 'Submit form',
  child: InkWell(
    onTap: _submit,
    child: Container(
      constraints: const BoxConstraints(minHeight: 48, minWidth: 48),
      // ...
    ),
  ),
)
```

## Animation Guidelines

- Duration: 200-300ms for micro-interactions
- Curves: Use `Curves.easeInOut` for most animations
- Reduce motion: Respect `MediaQuery.of(context).disableAnimations`

See `references/component-library.md` for reusable widget patterns.
See `references/animation-patterns.md` for animation best practices.
