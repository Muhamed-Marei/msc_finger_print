# Material 3 Theme Configuration Reference

Complete code examples for implementing Material 3 theming in Flutter applications.

## Table of Contents

1. [Complete Theme Setup](#complete-theme-setup)
2. [Color Scheme Configuration](#color-scheme-configuration)
3. [Custom Color Extensions](#custom-color-extensions)
4. [Typography Configuration](#typography-configuration)
5. [Component Theme Examples](#component-theme-examples)
6. [Dynamic Theming](#dynamic-theming)
7. [Theme Mode Management](#theme-mode-management)

---

## Complete Theme Setup

### Full App Theme Implementation

```dart
// lib/theme/app_theme.dart
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';

import 'color_schemes.dart';
import 'typography.dart';
import 'component_themes.dart';
import 'custom_colors.dart';
import 'spacing.dart';

/// Main application theme configuration
///
/// Usage:
/// ```dart
/// MaterialApp(
///   theme: AppTheme.lightTheme,
///   darkTheme: AppTheme.darkTheme,
///   themeMode: ThemeMode.system,
/// )
/// ```
class AppTheme {
  // Prevent instantiation
  AppTheme._();

  // Brand seed color - change this to customize your app's color scheme
  static const Color seedColor = Color(0xFF6750A4); // Material purple

  // Alternative seed colors for different brands:
  // static const Color seedColor = Color(0xFF1976D2); // Blue
  // static const Color seedColor = Color(0xFF388E3C); // Green
  // static const Color seedColor = Color(0xFFD32F2F); // Red
  // static const Color seedColor = Color(0xFFFF6F00); // Orange

  /// Light theme configuration
  static ThemeData get lightTheme {
    final colorScheme = ColorScheme.fromSeed(
      seedColor: seedColor,
      brightness: Brightness.light,
    );
    return _buildTheme(colorScheme, Brightness.light);
  }

  /// Dark theme configuration
  static ThemeData get darkTheme {
    final colorScheme = ColorScheme.fromSeed(
      seedColor: seedColor,
      brightness: Brightness.dark,
    );
    return _buildTheme(colorScheme, Brightness.dark);
  }

  /// High contrast light theme for accessibility
  static ThemeData get highContrastLightTheme {
    final colorScheme = ColorScheme.fromSeed(
      seedColor: seedColor,
      brightness: Brightness.light,
      contrastLevel: 1.0, // Maximum contrast
    );
    return _buildTheme(colorScheme, Brightness.light);
  }

  /// High contrast dark theme for accessibility
  static ThemeData get highContrastDarkTheme {
    final colorScheme = ColorScheme.fromSeed(
      seedColor: seedColor,
      brightness: Brightness.dark,
      contrastLevel: 1.0,
    );
    return _buildTheme(colorScheme, Brightness.dark);
  }

  /// Build theme from color scheme
  static ThemeData _buildTheme(ColorScheme colorScheme, Brightness brightness) {
    final textTheme = AppTypography.buildTextTheme(colorScheme);

    return ThemeData(
      useMaterial3: true,
      colorScheme: colorScheme,
      brightness: brightness,

      // Typography
      textTheme: textTheme,
      primaryTextTheme: textTheme,

      // Scaffold
      scaffoldBackgroundColor: colorScheme.surface,

      // AppBar
      appBarTheme: ComponentThemes.appBar(colorScheme),

      // Buttons
      elevatedButtonTheme: ComponentThemes.elevatedButton(colorScheme),
      filledButtonTheme: ComponentThemes.filledButton(colorScheme),
      outlinedButtonTheme: ComponentThemes.outlinedButton(colorScheme),
      textButtonTheme: ComponentThemes.textButton(colorScheme),
      iconButtonTheme: ComponentThemes.iconButton(colorScheme),

      // FAB
      floatingActionButtonTheme: ComponentThemes.fab(colorScheme),

      // Cards
      cardTheme: ComponentThemes.card(colorScheme),

      // Inputs
      inputDecorationTheme: ComponentThemes.inputDecoration(colorScheme),

      // Navigation
      bottomNavigationBarTheme: ComponentThemes.bottomNavBar(colorScheme),
      navigationBarTheme: ComponentThemes.navigationBar(colorScheme),
      navigationRailTheme: ComponentThemes.navigationRail(colorScheme),
      navigationDrawerTheme: ComponentThemes.navigationDrawer(colorScheme),
      drawerTheme: ComponentThemes.drawer(colorScheme),

      // Dialogs & Sheets
      dialogTheme: ComponentThemes.dialog(colorScheme),
      bottomSheetTheme: ComponentThemes.bottomSheet(colorScheme),

      // Selection
      checkboxTheme: ComponentThemes.checkbox(colorScheme),
      radioTheme: ComponentThemes.radio(colorScheme),
      switchTheme: ComponentThemes.switchTheme(colorScheme),

      // Lists
      listTileTheme: ComponentThemes.listTile(colorScheme),

      // Chips
      chipTheme: ComponentThemes.chip(colorScheme),

      // Dividers
      dividerTheme: ComponentThemes.divider(colorScheme),

      // Progress indicators
      progressIndicatorTheme: ComponentThemes.progressIndicator(colorScheme),

      // Snackbar
      snackBarTheme: ComponentThemes.snackBar(colorScheme),

      // Tabs
      tabBarTheme: ComponentThemes.tabBar(colorScheme),

      // Tooltips
      tooltipTheme: ComponentThemes.tooltip(colorScheme),

      // Popup menu
      popupMenuTheme: ComponentThemes.popupMenu(colorScheme),

      // Search bar
      searchBarTheme: ComponentThemes.searchBar(colorScheme),

      // Sliders
      sliderTheme: ComponentThemes.slider(colorScheme),

      // Date/Time pickers
      datePickerTheme: ComponentThemes.datePicker(colorScheme),
      timePickerTheme: ComponentThemes.timePicker(colorScheme),

      // Extensions
      extensions: [
        CustomColors.fromBrightness(brightness),
        const AppSpacing(),
      ],
    );
  }

  /// Configure system UI overlay style based on theme
  static SystemUiOverlayStyle systemUiOverlayStyle(Brightness brightness) {
    return brightness == Brightness.light
        ? SystemUiOverlayStyle.dark.copyWith(
            statusBarColor: Colors.transparent,
            systemNavigationBarColor: Colors.transparent,
          )
        : SystemUiOverlayStyle.light.copyWith(
            statusBarColor: Colors.transparent,
            systemNavigationBarColor: Colors.transparent,
          );
  }
}
```

---

## Color Scheme Configuration

### Using ColorScheme.fromSeed

```dart
// Basic seed color generation
final lightColorScheme = ColorScheme.fromSeed(
  seedColor: const Color(0xFF6750A4),
  brightness: Brightness.light,
);

final darkColorScheme = ColorScheme.fromSeed(
  seedColor: const Color(0xFF6750A4),
  brightness: Brightness.dark,
);
```

### Custom Color Scheme with Overrides

```dart
// Override specific colors while keeping seed-based generation
final customColorScheme = ColorScheme.fromSeed(
  seedColor: const Color(0xFF6750A4),
  brightness: Brightness.light,
).copyWith(
  // Override specific colors
  primary: const Color(0xFF1976D2),
  secondary: const Color(0xFF03DAC6),
  tertiary: const Color(0xFFFFB74D),
  error: const Color(0xFFB00020),
);
```

### Fully Custom Color Scheme

```dart
// Complete manual color scheme definition
const lightColorScheme = ColorScheme(
  brightness: Brightness.light,

  // Primary
  primary: Color(0xFF6750A4),
  onPrimary: Color(0xFFFFFFFF),
  primaryContainer: Color(0xFFEADDFF),
  onPrimaryContainer: Color(0xFF21005D),

  // Secondary
  secondary: Color(0xFF625B71),
  onSecondary: Color(0xFFFFFFFF),
  secondaryContainer: Color(0xFFE8DEF8),
  onSecondaryContainer: Color(0xFF1D192B),

  // Tertiary
  tertiary: Color(0xFF7D5260),
  onTertiary: Color(0xFFFFFFFF),
  tertiaryContainer: Color(0xFFFFD8E4),
  onTertiaryContainer: Color(0xFF31111D),

  // Error
  error: Color(0xFFB3261E),
  onError: Color(0xFFFFFFFF),
  errorContainer: Color(0xFFF9DEDC),
  onErrorContainer: Color(0xFF410E0B),

  // Surface
  surface: Color(0xFFFEF7FF),
  onSurface: Color(0xFF1D1B20),
  surfaceContainerLowest: Color(0xFFFFFFFF),
  surfaceContainerLow: Color(0xFFF7F2FA),
  surfaceContainer: Color(0xFFF3EDF7),
  surfaceContainerHigh: Color(0xFFECE6F0),
  surfaceContainerHighest: Color(0xFFE6E0E9),
  onSurfaceVariant: Color(0xFF49454F),

  // Outline
  outline: Color(0xFF79747E),
  outlineVariant: Color(0xFFCAC4D0),

  // Inverse
  inverseSurface: Color(0xFF322F35),
  onInverseSurface: Color(0xFFF5EFF7),
  inversePrimary: Color(0xFFD0BCFF),

  // Misc
  shadow: Color(0xFF000000),
  scrim: Color(0xFF000000),
  surfaceTint: Color(0xFF6750A4),
);
```

### Color Role Usage Guide

```dart
/// Color usage examples following Material 3 guidelines
class ColorUsageExamples {

  Widget buildPrimaryButton(BuildContext context) {
    final colorScheme = Theme.of(context).colorScheme;

    return ElevatedButton(
      style: ElevatedButton.styleFrom(
        // Filled button uses primary colors
        backgroundColor: colorScheme.primary,
        foregroundColor: colorScheme.onPrimary,
      ),
      onPressed: () {},
      child: const Text('Primary Action'),
    );
  }

  Widget buildSecondaryButton(BuildContext context) {
    final colorScheme = Theme.of(context).colorScheme;

    return ElevatedButton(
      style: ElevatedButton.styleFrom(
        // Tonal button uses container colors
        backgroundColor: colorScheme.secondaryContainer,
        foregroundColor: colorScheme.onSecondaryContainer,
      ),
      onPressed: () {},
      child: const Text('Secondary Action'),
    );
  }

  Widget buildErrorState(BuildContext context) {
    final colorScheme = Theme.of(context).colorScheme;

    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: colorScheme.errorContainer,
        borderRadius: BorderRadius.circular(12),
      ),
      child: Row(
        children: [
          Icon(Icons.error, color: colorScheme.onErrorContainer),
          const SizedBox(width: 8),
          Text(
            'Error message',
            style: TextStyle(color: colorScheme.onErrorContainer),
          ),
        ],
      ),
    );
  }

  Widget buildSurfaceCard(BuildContext context) {
    final colorScheme = Theme.of(context).colorScheme;

    return Card(
      // Use surface container for cards
      color: colorScheme.surfaceContainerLow,
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              'Card Title',
              style: TextStyle(
                color: colorScheme.onSurface,
                fontWeight: FontWeight.w500,
              ),
            ),
            Text(
              'Card description with secondary text',
              style: TextStyle(color: colorScheme.onSurfaceVariant),
            ),
          ],
        ),
      ),
    );
  }

  Widget buildOutlinedContainer(BuildContext context) {
    final colorScheme = Theme.of(context).colorScheme;

    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        border: Border.all(color: colorScheme.outline),
        borderRadius: BorderRadius.circular(12),
      ),
      child: Text(
        'Outlined container',
        style: TextStyle(color: colorScheme.onSurface),
      ),
    );
  }

  Widget buildSubtleOutlinedContainer(BuildContext context) {
    final colorScheme = Theme.of(context).colorScheme;

    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        // Use outlineVariant for subtle borders
        border: Border.all(color: colorScheme.outlineVariant),
        borderRadius: BorderRadius.circular(12),
      ),
      child: Text(
        'Subtle outline',
        style: TextStyle(color: colorScheme.onSurface),
      ),
    );
  }
}
```

---

## Custom Color Extensions

### Complete Custom Colors Implementation

```dart
// lib/theme/custom_colors.dart
import 'package:flutter/material.dart';

/// Custom semantic colors extending Material 3 color scheme
///
/// Usage:
/// ```dart
/// final customColors = Theme.of(context).extension<CustomColors>()!;
/// // or with extension:
/// final customColors = context.customColors;
/// ```
@immutable
class CustomColors extends ThemeExtension<CustomColors> {
  // Success colors
  final Color success;
  final Color onSuccess;
  final Color successContainer;
  final Color onSuccessContainer;

  // Warning colors
  final Color warning;
  final Color onWarning;
  final Color warningContainer;
  final Color onWarningContainer;

  // Info colors
  final Color info;
  final Color onInfo;
  final Color infoContainer;
  final Color onInfoContainer;

  // Neutral/Disabled colors
  final Color neutral;
  final Color onNeutral;
  final Color neutralContainer;
  final Color onNeutralContainer;

  const CustomColors({
    required this.success,
    required this.onSuccess,
    required this.successContainer,
    required this.onSuccessContainer,
    required this.warning,
    required this.onWarning,
    required this.warningContainer,
    required this.onWarningContainer,
    required this.info,
    required this.onInfo,
    required this.infoContainer,
    required this.onInfoContainer,
    required this.neutral,
    required this.onNeutral,
    required this.neutralContainer,
    required this.onNeutralContainer,
  });

  /// Light mode semantic colors
  static const CustomColors light = CustomColors(
    // Success - Green tones
    success: Color(0xFF2E7D32),
    onSuccess: Color(0xFFFFFFFF),
    successContainer: Color(0xFFC8E6C9),
    onSuccessContainer: Color(0xFF1B5E20),

    // Warning - Orange tones
    warning: Color(0xFFF57C00),
    onWarning: Color(0xFFFFFFFF),
    warningContainer: Color(0xFFFFE0B2),
    onWarningContainer: Color(0xFFE65100),

    // Info - Blue tones
    info: Color(0xFF1976D2),
    onInfo: Color(0xFFFFFFFF),
    infoContainer: Color(0xFFBBDEFB),
    onInfoContainer: Color(0xFF0D47A1),

    // Neutral - Gray tones
    neutral: Color(0xFF757575),
    onNeutral: Color(0xFFFFFFFF),
    neutralContainer: Color(0xFFEEEEEE),
    onNeutralContainer: Color(0xFF424242),
  );

  /// Dark mode semantic colors
  static const CustomColors dark = CustomColors(
    // Success - Green tones (lighter for dark mode)
    success: Color(0xFF81C784),
    onSuccess: Color(0xFF1B5E20),
    successContainer: Color(0xFF2E7D32),
    onSuccessContainer: Color(0xFFC8E6C9),

    // Warning - Orange tones
    warning: Color(0xFFFFB74D),
    onWarning: Color(0xFFE65100),
    warningContainer: Color(0xFFF57C00),
    onWarningContainer: Color(0xFFFFE0B2),

    // Info - Blue tones
    info: Color(0xFF64B5F6),
    onInfo: Color(0xFF0D47A1),
    infoContainer: Color(0xFF1976D2),
    onInfoContainer: Color(0xFFBBDEFB),

    // Neutral - Gray tones
    neutral: Color(0xFFBDBDBD),
    onNeutral: Color(0xFF424242),
    neutralContainer: Color(0xFF616161),
    onNeutralContainer: Color(0xFFEEEEEE),
  );

  /// Factory constructor based on brightness
  factory CustomColors.fromBrightness(Brightness brightness) {
    return brightness == Brightness.light ? light : dark;
  }

  @override
  CustomColors copyWith({
    Color? success,
    Color? onSuccess,
    Color? successContainer,
    Color? onSuccessContainer,
    Color? warning,
    Color? onWarning,
    Color? warningContainer,
    Color? onWarningContainer,
    Color? info,
    Color? onInfo,
    Color? infoContainer,
    Color? onInfoContainer,
    Color? neutral,
    Color? onNeutral,
    Color? neutralContainer,
    Color? onNeutralContainer,
  }) {
    return CustomColors(
      success: success ?? this.success,
      onSuccess: onSuccess ?? this.onSuccess,
      successContainer: successContainer ?? this.successContainer,
      onSuccessContainer: onSuccessContainer ?? this.onSuccessContainer,
      warning: warning ?? this.warning,
      onWarning: onWarning ?? this.onWarning,
      warningContainer: warningContainer ?? this.warningContainer,
      onWarningContainer: onWarningContainer ?? this.onWarningContainer,
      info: info ?? this.info,
      onInfo: onInfo ?? this.onInfo,
      infoContainer: infoContainer ?? this.infoContainer,
      onInfoContainer: onInfoContainer ?? this.onInfoContainer,
      neutral: neutral ?? this.neutral,
      onNeutral: onNeutral ?? this.onNeutral,
      neutralContainer: neutralContainer ?? this.neutralContainer,
      onNeutralContainer: onNeutralContainer ?? this.onNeutralContainer,
    );
  }

  @override
  CustomColors lerp(CustomColors? other, double t) {
    if (other is! CustomColors) return this;
    return CustomColors(
      success: Color.lerp(success, other.success, t)!,
      onSuccess: Color.lerp(onSuccess, other.onSuccess, t)!,
      successContainer: Color.lerp(successContainer, other.successContainer, t)!,
      onSuccessContainer: Color.lerp(onSuccessContainer, other.onSuccessContainer, t)!,
      warning: Color.lerp(warning, other.warning, t)!,
      onWarning: Color.lerp(onWarning, other.onWarning, t)!,
      warningContainer: Color.lerp(warningContainer, other.warningContainer, t)!,
      onWarningContainer: Color.lerp(onWarningContainer, other.onWarningContainer, t)!,
      info: Color.lerp(info, other.info, t)!,
      onInfo: Color.lerp(onInfo, other.onInfo, t)!,
      infoContainer: Color.lerp(infoContainer, other.infoContainer, t)!,
      onInfoContainer: Color.lerp(onInfoContainer, other.onInfoContainer, t)!,
      neutral: Color.lerp(neutral, other.neutral, t)!,
      onNeutral: Color.lerp(onNeutral, other.onNeutral, t)!,
      neutralContainer: Color.lerp(neutralContainer, other.neutralContainer, t)!,
      onNeutralContainer: Color.lerp(onNeutralContainer, other.onNeutralContainer, t)!,
    );
  }
}

/// Extension for easy access to custom colors
extension CustomColorsExtension on BuildContext {
  CustomColors get customColors => Theme.of(this).extension<CustomColors>()!;
}
```

### Using Custom Colors

```dart
class CustomColorUsageExample extends StatelessWidget {
  const CustomColorUsageExample({super.key});

  @override
  Widget build(BuildContext context) {
    final customColors = context.customColors;

    return Column(
      children: [
        // Success banner
        Container(
          padding: const EdgeInsets.all(16),
          decoration: BoxDecoration(
            color: customColors.successContainer,
            borderRadius: BorderRadius.circular(8),
          ),
          child: Row(
            children: [
              Icon(Icons.check_circle, color: customColors.onSuccessContainer),
              const SizedBox(width: 8),
              Text(
                'Operation completed successfully!',
                style: TextStyle(color: customColors.onSuccessContainer),
              ),
            ],
          ),
        ),

        const SizedBox(height: 16),

        // Warning banner
        Container(
          padding: const EdgeInsets.all(16),
          decoration: BoxDecoration(
            color: customColors.warningContainer,
            borderRadius: BorderRadius.circular(8),
          ),
          child: Row(
            children: [
              Icon(Icons.warning, color: customColors.onWarningContainer),
              const SizedBox(width: 8),
              Text(
                'Please review before continuing',
                style: TextStyle(color: customColors.onWarningContainer),
              ),
            ],
          ),
        ),

        const SizedBox(height: 16),

        // Info banner
        Container(
          padding: const EdgeInsets.all(16),
          decoration: BoxDecoration(
            color: customColors.infoContainer,
            borderRadius: BorderRadius.circular(8),
          ),
          child: Row(
            children: [
              Icon(Icons.info, color: customColors.onInfoContainer),
              const SizedBox(width: 8),
              Text(
                'Here is some helpful information',
                style: TextStyle(color: customColors.onInfoContainer),
              ),
            ],
          ),
        ),
      ],
    );
  }
}
```

---

## Typography Configuration

### Complete Typography Implementation

```dart
// lib/theme/typography.dart
import 'package:flutter/material.dart';

/// Material 3 typography configuration
///
/// Type scale:
/// - Display: Large, promotional text
/// - Headline: Section titles
/// - Title: Component headers
/// - Body: Paragraph text
/// - Label: Buttons, captions
class AppTypography {
  AppTypography._();

  // Font configuration
  static const String? fontFamily = null; // null uses system font
  // static const String? fontFamily = 'Roboto';
  // static const String? fontFamily = 'Inter';

  /// Build complete text theme
  static TextTheme buildTextTheme(ColorScheme colorScheme) {
    final Color onSurface = colorScheme.onSurface;

    return TextTheme(
      // ============ DISPLAY ============
      // Use for: Hero text, splash screens, large promotional content
      displayLarge: TextStyle(
        fontFamily: fontFamily,
        fontSize: 57,
        fontWeight: FontWeight.w400,
        letterSpacing: -0.25,
        height: 1.12, // 64px line height
        color: onSurface,
      ),
      displayMedium: TextStyle(
        fontFamily: fontFamily,
        fontSize: 45,
        fontWeight: FontWeight.w400,
        letterSpacing: 0,
        height: 1.16, // 52px line height
        color: onSurface,
      ),
      displaySmall: TextStyle(
        fontFamily: fontFamily,
        fontSize: 36,
        fontWeight: FontWeight.w400,
        letterSpacing: 0,
        height: 1.22, // 44px line height
        color: onSurface,
      ),

      // ============ HEADLINE ============
      // Use for: Page titles, section headers, primary focus areas
      headlineLarge: TextStyle(
        fontFamily: fontFamily,
        fontSize: 32,
        fontWeight: FontWeight.w400,
        letterSpacing: 0,
        height: 1.25, // 40px line height
        color: onSurface,
      ),
      headlineMedium: TextStyle(
        fontFamily: fontFamily,
        fontSize: 28,
        fontWeight: FontWeight.w400,
        letterSpacing: 0,
        height: 1.29, // 36px line height
        color: onSurface,
      ),
      headlineSmall: TextStyle(
        fontFamily: fontFamily,
        fontSize: 24,
        fontWeight: FontWeight.w400,
        letterSpacing: 0,
        height: 1.33, // 32px line height
        color: onSurface,
      ),

      // ============ TITLE ============
      // Use for: Card titles, dialog headers, list item titles
      titleLarge: TextStyle(
        fontFamily: fontFamily,
        fontSize: 22,
        fontWeight: FontWeight.w500, // Medium weight
        letterSpacing: 0,
        height: 1.27, // 28px line height
        color: onSurface,
      ),
      titleMedium: TextStyle(
        fontFamily: fontFamily,
        fontSize: 16,
        fontWeight: FontWeight.w500,
        letterSpacing: 0.15,
        height: 1.50, // 24px line height
        color: onSurface,
      ),
      titleSmall: TextStyle(
        fontFamily: fontFamily,
        fontSize: 14,
        fontWeight: FontWeight.w500,
        letterSpacing: 0.1,
        height: 1.43, // 20px line height
        color: onSurface,
      ),

      // ============ BODY ============
      // Use for: Paragraph text, descriptions, long-form content
      bodyLarge: TextStyle(
        fontFamily: fontFamily,
        fontSize: 16,
        fontWeight: FontWeight.w400,
        letterSpacing: 0.5,
        height: 1.50, // 24px line height
        color: onSurface,
      ),
      bodyMedium: TextStyle(
        fontFamily: fontFamily,
        fontSize: 14,
        fontWeight: FontWeight.w400,
        letterSpacing: 0.25,
        height: 1.43, // 20px line height
        color: onSurface,
      ),
      bodySmall: TextStyle(
        fontFamily: fontFamily,
        fontSize: 12,
        fontWeight: FontWeight.w400,
        letterSpacing: 0.4,
        height: 1.33, // 16px line height
        color: onSurface,
      ),

      // ============ LABEL ============
      // Use for: Buttons, tabs, chips, form labels, captions
      labelLarge: TextStyle(
        fontFamily: fontFamily,
        fontSize: 14,
        fontWeight: FontWeight.w500,
        letterSpacing: 0.1,
        height: 1.43, // 20px line height
        color: onSurface,
      ),
      labelMedium: TextStyle(
        fontFamily: fontFamily,
        fontSize: 12,
        fontWeight: FontWeight.w500,
        letterSpacing: 0.5,
        height: 1.33, // 16px line height
        color: onSurface,
      ),
      labelSmall: TextStyle(
        fontFamily: fontFamily,
        fontSize: 11,
        fontWeight: FontWeight.w500,
        letterSpacing: 0.5,
        height: 1.45, // 16px line height
        color: onSurface,
      ),
    );
  }
}
```

### Typography Usage Examples

```dart
class TypographyExamples extends StatelessWidget {
  const TypographyExamples({super.key});

  @override
  Widget build(BuildContext context) {
    final textTheme = Theme.of(context).textTheme;
    final colorScheme = Theme.of(context).colorScheme;

    return SingleChildScrollView(
      padding: const EdgeInsets.all(24),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Display - Hero content
          Text('Welcome', style: textTheme.displayLarge),
          const SizedBox(height: 8),
          Text('Your journey starts here', style: textTheme.displayMedium),
          const SizedBox(height: 32),

          // Headline - Section headers
          Text('Getting Started', style: textTheme.headlineMedium),
          const SizedBox(height: 16),

          // Body - Content
          Text(
            'This is body text for reading. It uses bodyLarge style for '
            'main content and paragraphs.',
            style: textTheme.bodyLarge,
          ),
          const SizedBox(height: 12),
          Text(
            'Secondary information uses bodyMedium for slightly less emphasis.',
            style: textTheme.bodyMedium?.copyWith(
              color: colorScheme.onSurfaceVariant,
            ),
          ),
          const SizedBox(height: 24),

          // Title - Card headers
          Card(
            child: Padding(
              padding: const EdgeInsets.all(16),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text('Card Title', style: textTheme.titleLarge),
                  const SizedBox(height: 8),
                  Text(
                    'Card description text',
                    style: textTheme.bodyMedium,
                  ),
                ],
              ),
            ),
          ),
          const SizedBox(height: 24),

          // Label - Buttons, chips
          Row(
            children: [
              ElevatedButton(
                onPressed: () {},
                child: Text('Primary Button', style: textTheme.labelLarge),
              ),
              const SizedBox(width: 12),
              Chip(
                label: Text('Label', style: textTheme.labelMedium),
              ),
            ],
          ),
          const SizedBox(height: 16),

          // Label small - Captions
          Text(
            'Caption: Last updated 2 hours ago',
            style: textTheme.labelSmall?.copyWith(
              color: colorScheme.onSurfaceVariant,
            ),
          ),
        ],
      ),
    );
  }
}
```

---

## Component Theme Examples

### Complete Component Themes

```dart
// lib/theme/component_themes.dart
import 'package:flutter/material.dart';

/// Material 3 component theme configurations
class ComponentThemes {
  ComponentThemes._();

  // ============ APP BAR ============
  static AppBarTheme appBar(ColorScheme colorScheme) {
    return AppBarTheme(
      elevation: 0,
      scrolledUnderElevation: 3,
      backgroundColor: colorScheme.surface,
      foregroundColor: colorScheme.onSurface,
      surfaceTintColor: colorScheme.surfaceTint,
      centerTitle: false,
      titleTextStyle: TextStyle(
        fontSize: 22,
        fontWeight: FontWeight.w400,
        color: colorScheme.onSurface,
      ),
      iconTheme: IconThemeData(
        color: colorScheme.onSurface,
        size: 24,
      ),
      actionsIconTheme: IconThemeData(
        color: colorScheme.onSurfaceVariant,
        size: 24,
      ),
    );
  }

  // ============ BUTTONS ============
  static ElevatedButtonThemeData elevatedButton(ColorScheme colorScheme) {
    return ElevatedButtonThemeData(
      style: ElevatedButton.styleFrom(
        foregroundColor: colorScheme.onPrimary,
        backgroundColor: colorScheme.primary,
        disabledForegroundColor: colorScheme.onSurface.withOpacity(0.38),
        disabledBackgroundColor: colorScheme.onSurface.withOpacity(0.12),
        elevation: 1,
        shadowColor: colorScheme.shadow,
        padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 10),
        minimumSize: const Size(64, 40),
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(20), // Full stadium
        ),
        textStyle: const TextStyle(
          fontSize: 14,
          fontWeight: FontWeight.w500,
          letterSpacing: 0.1,
        ),
      ).copyWith(
        elevation: WidgetStateProperty.resolveWith((states) {
          if (states.contains(WidgetState.hovered)) return 3;
          if (states.contains(WidgetState.pressed)) return 1;
          return 1;
        }),
      ),
    );
  }

  static FilledButtonThemeData filledButton(ColorScheme colorScheme) {
    return FilledButtonThemeData(
      style: FilledButton.styleFrom(
        foregroundColor: colorScheme.onPrimary,
        backgroundColor: colorScheme.primary,
        disabledForegroundColor: colorScheme.onSurface.withOpacity(0.38),
        disabledBackgroundColor: colorScheme.onSurface.withOpacity(0.12),
        padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 10),
        minimumSize: const Size(64, 40),
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(20),
        ),
      ),
    );
  }

  static OutlinedButtonThemeData outlinedButton(ColorScheme colorScheme) {
    return OutlinedButtonThemeData(
      style: OutlinedButton.styleFrom(
        foregroundColor: colorScheme.primary,
        disabledForegroundColor: colorScheme.onSurface.withOpacity(0.38),
        padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 10),
        minimumSize: const Size(64, 40),
        side: BorderSide(color: colorScheme.outline),
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(20),
        ),
      ).copyWith(
        side: WidgetStateProperty.resolveWith((states) {
          if (states.contains(WidgetState.pressed)) {
            return BorderSide(color: colorScheme.primary);
          }
          return BorderSide(color: colorScheme.outline);
        }),
      ),
    );
  }

  static TextButtonThemeData textButton(ColorScheme colorScheme) {
    return TextButtonThemeData(
      style: TextButton.styleFrom(
        foregroundColor: colorScheme.primary,
        disabledForegroundColor: colorScheme.onSurface.withOpacity(0.38),
        padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 10),
        minimumSize: const Size(48, 40),
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(20),
        ),
      ),
    );
  }

  static IconButtonThemeData iconButton(ColorScheme colorScheme) {
    return IconButtonThemeData(
      style: IconButton.styleFrom(
        foregroundColor: colorScheme.onSurfaceVariant,
        disabledForegroundColor: colorScheme.onSurface.withOpacity(0.38),
        minimumSize: const Size(48, 48), // Accessibility
        shape: const CircleBorder(),
      ),
    );
  }

  // ============ FAB ============
  static FloatingActionButtonThemeData fab(ColorScheme colorScheme) {
    return FloatingActionButtonThemeData(
      backgroundColor: colorScheme.primaryContainer,
      foregroundColor: colorScheme.onPrimaryContainer,
      elevation: 3,
      focusElevation: 3,
      hoverElevation: 4,
      highlightElevation: 3,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(16),
      ),
      extendedPadding: const EdgeInsets.symmetric(horizontal: 16),
      extendedTextStyle: const TextStyle(
        fontSize: 14,
        fontWeight: FontWeight.w500,
        letterSpacing: 0.1,
      ),
    );
  }

  // ============ CARD ============
  static CardTheme card(ColorScheme colorScheme) {
    return CardTheme(
      elevation: 0,
      color: colorScheme.surfaceContainerLow,
      surfaceTintColor: Colors.transparent,
      shadowColor: colorScheme.shadow,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(12),
      ),
      clipBehavior: Clip.antiAlias,
      margin: const EdgeInsets.all(4),
    );
  }

  // ============ INPUT ============
  static InputDecorationTheme inputDecoration(ColorScheme colorScheme) {
    final border = OutlineInputBorder(
      borderRadius: BorderRadius.circular(4),
      borderSide: BorderSide(color: colorScheme.outline),
    );

    return InputDecorationTheme(
      filled: true,
      fillColor: Colors.transparent,
      contentPadding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),

      // Borders
      border: border,
      enabledBorder: border,
      focusedBorder: OutlineInputBorder(
        borderRadius: BorderRadius.circular(4),
        borderSide: BorderSide(color: colorScheme.primary, width: 2),
      ),
      errorBorder: OutlineInputBorder(
        borderRadius: BorderRadius.circular(4),
        borderSide: BorderSide(color: colorScheme.error),
      ),
      focusedErrorBorder: OutlineInputBorder(
        borderRadius: BorderRadius.circular(4),
        borderSide: BorderSide(color: colorScheme.error, width: 2),
      ),
      disabledBorder: OutlineInputBorder(
        borderRadius: BorderRadius.circular(4),
        borderSide: BorderSide(color: colorScheme.onSurface.withOpacity(0.12)),
      ),

      // Text styles
      labelStyle: TextStyle(color: colorScheme.onSurfaceVariant),
      floatingLabelStyle: TextStyle(color: colorScheme.primary),
      hintStyle: TextStyle(color: colorScheme.onSurfaceVariant),
      helperStyle: TextStyle(color: colorScheme.onSurfaceVariant),
      errorStyle: TextStyle(color: colorScheme.error),
      prefixStyle: TextStyle(color: colorScheme.onSurface),
      suffixStyle: TextStyle(color: colorScheme.onSurface),
      counterStyle: TextStyle(color: colorScheme.onSurfaceVariant),

      // Icons
      prefixIconColor: colorScheme.onSurfaceVariant,
      suffixIconColor: colorScheme.onSurfaceVariant,
    );
  }

  // ============ NAVIGATION ============
  static BottomNavigationBarThemeData bottomNavBar(ColorScheme colorScheme) {
    return BottomNavigationBarThemeData(
      type: BottomNavigationBarType.fixed,
      backgroundColor: colorScheme.surfaceContainer,
      selectedItemColor: colorScheme.onSurface,
      unselectedItemColor: colorScheme.onSurfaceVariant,
      elevation: 0,
      selectedLabelStyle: const TextStyle(
        fontSize: 12,
        fontWeight: FontWeight.w500,
      ),
      unselectedLabelStyle: const TextStyle(
        fontSize: 12,
        fontWeight: FontWeight.w500,
      ),
    );
  }

  static NavigationBarThemeData navigationBar(ColorScheme colorScheme) {
    return NavigationBarThemeData(
      backgroundColor: colorScheme.surfaceContainer,
      indicatorColor: colorScheme.secondaryContainer,
      elevation: 0,
      height: 80,
      labelBehavior: NavigationDestinationLabelBehavior.alwaysShow,
      iconTheme: WidgetStateProperty.resolveWith((states) {
        if (states.contains(WidgetState.selected)) {
          return IconThemeData(color: colorScheme.onSecondaryContainer);
        }
        return IconThemeData(color: colorScheme.onSurfaceVariant);
      }),
      labelTextStyle: WidgetStateProperty.resolveWith((states) {
        if (states.contains(WidgetState.selected)) {
          return TextStyle(
            color: colorScheme.onSurface,
            fontSize: 12,
            fontWeight: FontWeight.w500,
          );
        }
        return TextStyle(
          color: colorScheme.onSurfaceVariant,
          fontSize: 12,
          fontWeight: FontWeight.w500,
        );
      }),
    );
  }

  static NavigationRailThemeData navigationRail(ColorScheme colorScheme) {
    return NavigationRailThemeData(
      backgroundColor: colorScheme.surface,
      indicatorColor: colorScheme.secondaryContainer,
      elevation: 0,
      selectedIconTheme: IconThemeData(color: colorScheme.onSecondaryContainer),
      unselectedIconTheme: IconThemeData(color: colorScheme.onSurfaceVariant),
      selectedLabelTextStyle: TextStyle(
        color: colorScheme.onSurface,
        fontSize: 12,
        fontWeight: FontWeight.w500,
      ),
      unselectedLabelTextStyle: TextStyle(
        color: colorScheme.onSurfaceVariant,
        fontSize: 12,
        fontWeight: FontWeight.w500,
      ),
    );
  }

  static NavigationDrawerThemeData navigationDrawer(ColorScheme colorScheme) {
    return NavigationDrawerThemeData(
      backgroundColor: colorScheme.surfaceContainerLow,
      indicatorColor: colorScheme.secondaryContainer,
      indicatorShape: const StadiumBorder(),
      tileHeight: 56,
    );
  }

  static DrawerThemeData drawer(ColorScheme colorScheme) {
    return DrawerThemeData(
      backgroundColor: colorScheme.surfaceContainerLow,
      elevation: 1,
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.only(
          topRight: Radius.circular(16),
          bottomRight: Radius.circular(16),
        ),
      ),
    );
  }

  // ============ DIALOGS ============
  static DialogTheme dialog(ColorScheme colorScheme) {
    return DialogTheme(
      backgroundColor: colorScheme.surfaceContainerHigh,
      elevation: 6,
      shadowColor: colorScheme.shadow,
      surfaceTintColor: Colors.transparent,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(28),
      ),
      titleTextStyle: TextStyle(
        color: colorScheme.onSurface,
        fontSize: 24,
        fontWeight: FontWeight.w400,
      ),
      contentTextStyle: TextStyle(
        color: colorScheme.onSurfaceVariant,
        fontSize: 14,
        fontWeight: FontWeight.w400,
      ),
    );
  }

  static BottomSheetThemeData bottomSheet(ColorScheme colorScheme) {
    return BottomSheetThemeData(
      backgroundColor: colorScheme.surfaceContainerLow,
      elevation: 1,
      modalElevation: 1,
      surfaceTintColor: Colors.transparent,
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(28)),
      ),
      dragHandleColor: colorScheme.onSurfaceVariant.withOpacity(0.4),
      dragHandleSize: const Size(32, 4),
      showDragHandle: true,
    );
  }

  // ============ SELECTION CONTROLS ============
  static CheckboxThemeData checkbox(ColorScheme colorScheme) {
    return CheckboxThemeData(
      fillColor: WidgetStateProperty.resolveWith((states) {
        if (states.contains(WidgetState.selected)) {
          return colorScheme.primary;
        }
        return Colors.transparent;
      }),
      checkColor: WidgetStateProperty.all(colorScheme.onPrimary),
      side: BorderSide(color: colorScheme.onSurfaceVariant, width: 2),
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(2),
      ),
    );
  }

  static RadioThemeData radio(ColorScheme colorScheme) {
    return RadioThemeData(
      fillColor: WidgetStateProperty.resolveWith((states) {
        if (states.contains(WidgetState.selected)) {
          return colorScheme.primary;
        }
        return colorScheme.onSurfaceVariant;
      }),
    );
  }

  static SwitchThemeData switchTheme(ColorScheme colorScheme) {
    return SwitchThemeData(
      thumbColor: WidgetStateProperty.resolveWith((states) {
        if (states.contains(WidgetState.selected)) {
          return colorScheme.onPrimary;
        }
        return colorScheme.outline;
      }),
      trackColor: WidgetStateProperty.resolveWith((states) {
        if (states.contains(WidgetState.selected)) {
          return colorScheme.primary;
        }
        return colorScheme.surfaceContainerHighest;
      }),
      trackOutlineColor: WidgetStateProperty.resolveWith((states) {
        if (states.contains(WidgetState.selected)) {
          return Colors.transparent;
        }
        return colorScheme.outline;
      }),
    );
  }

  // ============ LISTS ============
  static ListTileThemeData listTile(ColorScheme colorScheme) {
    return ListTileThemeData(
      tileColor: Colors.transparent,
      selectedTileColor: colorScheme.secondaryContainer,
      iconColor: colorScheme.onSurfaceVariant,
      selectedColor: colorScheme.onSecondaryContainer,
      textColor: colorScheme.onSurface,
      contentPadding: const EdgeInsets.symmetric(horizontal: 16),
      minVerticalPadding: 8,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(0),
      ),
      titleTextStyle: TextStyle(
        color: colorScheme.onSurface,
        fontSize: 16,
        fontWeight: FontWeight.w400,
      ),
      subtitleTextStyle: TextStyle(
        color: colorScheme.onSurfaceVariant,
        fontSize: 14,
        fontWeight: FontWeight.w400,
      ),
    );
  }

  // ============ CHIPS ============
  static ChipThemeData chip(ColorScheme colorScheme) {
    return ChipThemeData(
      backgroundColor: colorScheme.surfaceContainerLow,
      selectedColor: colorScheme.secondaryContainer,
      disabledColor: colorScheme.onSurface.withOpacity(0.12),
      labelStyle: TextStyle(color: colorScheme.onSurface),
      secondaryLabelStyle: TextStyle(color: colorScheme.onSecondaryContainer),
      padding: const EdgeInsets.symmetric(horizontal: 8),
      side: BorderSide(color: colorScheme.outline),
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(8),
      ),
    );
  }

  // ============ DIVIDER ============
  static DividerThemeData divider(ColorScheme colorScheme) {
    return DividerThemeData(
      color: colorScheme.outlineVariant,
      thickness: 1,
      space: 1,
    );
  }

  // ============ PROGRESS INDICATORS ============
  static ProgressIndicatorThemeData progressIndicator(ColorScheme colorScheme) {
    return ProgressIndicatorThemeData(
      color: colorScheme.primary,
      linearTrackColor: colorScheme.surfaceContainerHighest,
      circularTrackColor: colorScheme.surfaceContainerHighest,
    );
  }

  // ============ SNACKBAR ============
  static SnackBarThemeData snackBar(ColorScheme colorScheme) {
    return SnackBarThemeData(
      backgroundColor: colorScheme.inverseSurface,
      contentTextStyle: TextStyle(color: colorScheme.onInverseSurface),
      actionTextColor: colorScheme.inversePrimary,
      elevation: 6,
      behavior: SnackBarBehavior.floating,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(4),
      ),
    );
  }

  // ============ TABS ============
  static TabBarTheme tabBar(ColorScheme colorScheme) {
    return TabBarTheme(
      labelColor: colorScheme.primary,
      unselectedLabelColor: colorScheme.onSurfaceVariant,
      indicatorColor: colorScheme.primary,
      indicatorSize: TabBarIndicatorSize.label,
      dividerColor: colorScheme.surfaceContainerHighest,
      labelStyle: const TextStyle(
        fontSize: 14,
        fontWeight: FontWeight.w500,
      ),
      unselectedLabelStyle: const TextStyle(
        fontSize: 14,
        fontWeight: FontWeight.w500,
      ),
    );
  }

  // ============ TOOLTIP ============
  static TooltipThemeData tooltip(ColorScheme colorScheme) {
    return TooltipThemeData(
      textStyle: TextStyle(
        color: colorScheme.onInverseSurface,
        fontSize: 12,
      ),
      decoration: BoxDecoration(
        color: colorScheme.inverseSurface,
        borderRadius: BorderRadius.circular(4),
      ),
    );
  }

  // ============ POPUP MENU ============
  static PopupMenuThemeData popupMenu(ColorScheme colorScheme) {
    return PopupMenuThemeData(
      color: colorScheme.surfaceContainer,
      elevation: 3,
      surfaceTintColor: Colors.transparent,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(4),
      ),
      textStyle: TextStyle(color: colorScheme.onSurface),
    );
  }

  // ============ SEARCH BAR ============
  static SearchBarThemeData searchBar(ColorScheme colorScheme) {
    return SearchBarThemeData(
      backgroundColor: WidgetStateProperty.all(colorScheme.surfaceContainerHigh),
      elevation: WidgetStateProperty.all(0),
      shadowColor: WidgetStateProperty.all(Colors.transparent),
      surfaceTintColor: WidgetStateProperty.all(Colors.transparent),
      padding: WidgetStateProperty.all(
        const EdgeInsets.symmetric(horizontal: 16),
      ),
      textStyle: WidgetStateProperty.all(
        TextStyle(color: colorScheme.onSurface),
      ),
      hintStyle: WidgetStateProperty.all(
        TextStyle(color: colorScheme.onSurfaceVariant),
      ),
      shape: WidgetStateProperty.all(
        RoundedRectangleBorder(borderRadius: BorderRadius.circular(28)),
      ),
    );
  }

  // ============ SLIDER ============
  static SliderThemeData slider(ColorScheme colorScheme) {
    return SliderThemeData(
      activeTrackColor: colorScheme.primary,
      inactiveTrackColor: colorScheme.surfaceContainerHighest,
      thumbColor: colorScheme.primary,
      overlayColor: colorScheme.primary.withOpacity(0.12),
      valueIndicatorColor: colorScheme.primary,
      valueIndicatorTextStyle: TextStyle(color: colorScheme.onPrimary),
    );
  }

  // ============ DATE PICKER ============
  static DatePickerThemeData datePicker(ColorScheme colorScheme) {
    return DatePickerThemeData(
      backgroundColor: colorScheme.surfaceContainerHigh,
      headerBackgroundColor: colorScheme.surfaceContainerHigh,
      headerForegroundColor: colorScheme.onSurfaceVariant,
      dayForegroundColor: WidgetStateProperty.resolveWith((states) {
        if (states.contains(WidgetState.selected)) {
          return colorScheme.onPrimary;
        }
        return colorScheme.onSurface;
      }),
      dayBackgroundColor: WidgetStateProperty.resolveWith((states) {
        if (states.contains(WidgetState.selected)) {
          return colorScheme.primary;
        }
        return Colors.transparent;
      }),
      todayForegroundColor: WidgetStateProperty.all(colorScheme.primary),
      todayBorder: BorderSide(color: colorScheme.primary),
    );
  }

  // ============ TIME PICKER ============
  static TimePickerThemeData timePicker(ColorScheme colorScheme) {
    return TimePickerThemeData(
      backgroundColor: colorScheme.surfaceContainerHigh,
      hourMinuteTextColor: colorScheme.onSurface,
      dialHandColor: colorScheme.primary,
      dialBackgroundColor: colorScheme.surfaceContainerHighest,
      dialTextColor: colorScheme.onSurface,
      entryModeIconColor: colorScheme.onSurfaceVariant,
    );
  }
}
```

---

## Dynamic Theming

### Theme from Image/Wallpaper Colors

```dart
import 'package:dynamic_color/dynamic_color.dart';

class DynamicThemeApp extends StatelessWidget {
  const DynamicThemeApp({super.key});

  // Fallback colors if dynamic colors unavailable
  static const _defaultSeedColor = Color(0xFF6750A4);

  @override
  Widget build(BuildContext context) {
    return DynamicColorBuilder(
      builder: (lightDynamic, darkDynamic) {
        ColorScheme lightColorScheme;
        ColorScheme darkColorScheme;

        if (lightDynamic != null && darkDynamic != null) {
          // Use device's dynamic colors (Android 12+)
          lightColorScheme = lightDynamic.harmonized();
          darkColorScheme = darkDynamic.harmonized();
        } else {
          // Fallback to seed color
          lightColorScheme = ColorScheme.fromSeed(
            seedColor: _defaultSeedColor,
            brightness: Brightness.light,
          );
          darkColorScheme = ColorScheme.fromSeed(
            seedColor: _defaultSeedColor,
            brightness: Brightness.dark,
          );
        }

        return MaterialApp(
          theme: _buildTheme(lightColorScheme),
          darkTheme: _buildTheme(darkColorScheme),
          themeMode: ThemeMode.system,
          home: const HomeScreen(),
        );
      },
    );
  }

  ThemeData _buildTheme(ColorScheme colorScheme) {
    return ThemeData(
      useMaterial3: true,
      colorScheme: colorScheme,
      // ... other theme configuration
    );
  }
}
```

### Theme from Custom Brand Color

```dart
class BrandThemedApp extends StatefulWidget {
  const BrandThemedApp({super.key});

  @override
  State<BrandThemedApp> createState() => _BrandThemedAppState();
}

class _BrandThemedAppState extends State<BrandThemedApp> {
  Color _brandColor = const Color(0xFF6750A4);

  void _updateBrandColor(Color color) {
    setState(() {
      _brandColor = color;
    });
  }

  @override
  Widget build(BuildContext context) {
    final lightColorScheme = ColorScheme.fromSeed(
      seedColor: _brandColor,
      brightness: Brightness.light,
    );
    final darkColorScheme = ColorScheme.fromSeed(
      seedColor: _brandColor,
      brightness: Brightness.dark,
    );

    return MaterialApp(
      theme: ThemeData(
        useMaterial3: true,
        colorScheme: lightColorScheme,
      ),
      darkTheme: ThemeData(
        useMaterial3: true,
        colorScheme: darkColorScheme,
      ),
      home: BrandColorPicker(onColorChanged: _updateBrandColor),
    );
  }
}
```

---

## Theme Mode Management

### Complete Theme Mode Controller

```dart
import 'package:flutter/material.dart';
import 'package:shared_preferences/shared_preferences.dart';

/// Manages theme mode (light/dark/system) with persistence
class ThemeModeController extends ChangeNotifier {
  static const _themeModeKey = 'theme_mode';

  ThemeMode _themeMode = ThemeMode.system;

  ThemeMode get themeMode => _themeMode;

  ThemeModeController() {
    _loadThemeMode();
  }

  Future<void> _loadThemeMode() async {
    final prefs = await SharedPreferences.getInstance();
    final savedMode = prefs.getString(_themeModeKey);

    if (savedMode != null) {
      _themeMode = ThemeMode.values.firstWhere(
        (mode) => mode.name == savedMode,
        orElse: () => ThemeMode.system,
      );
      notifyListeners();
    }
  }

  Future<void> setThemeMode(ThemeMode mode) async {
    if (_themeMode != mode) {
      _themeMode = mode;
      notifyListeners();

      final prefs = await SharedPreferences.getInstance();
      await prefs.setString(_themeModeKey, mode.name);
    }
  }

  void toggleTheme() {
    switch (_themeMode) {
      case ThemeMode.system:
        setThemeMode(ThemeMode.light);
        break;
      case ThemeMode.light:
        setThemeMode(ThemeMode.dark);
        break;
      case ThemeMode.dark:
        setThemeMode(ThemeMode.system);
        break;
    }
  }
}

// Usage with Provider
class MyApp extends StatelessWidget {
  const MyApp({super.key});

  @override
  Widget build(BuildContext context) {
    return ChangeNotifierProvider(
      create: (_) => ThemeModeController(),
      child: Consumer<ThemeModeController>(
        builder: (context, themeController, _) {
          return MaterialApp(
            theme: AppTheme.lightTheme,
            darkTheme: AppTheme.darkTheme,
            themeMode: themeController.themeMode,
            home: const HomeScreen(),
          );
        },
      ),
    );
  }
}

// Theme mode selector widget
class ThemeModeSelector extends StatelessWidget {
  const ThemeModeSelector({super.key});

  @override
  Widget build(BuildContext context) {
    final controller = context.watch<ThemeModeController>();

    return SegmentedButton<ThemeMode>(
      segments: const [
        ButtonSegment(
          value: ThemeMode.system,
          icon: Icon(Icons.settings_suggest),
          label: Text('System'),
        ),
        ButtonSegment(
          value: ThemeMode.light,
          icon: Icon(Icons.light_mode),
          label: Text('Light'),
        ),
        ButtonSegment(
          value: ThemeMode.dark,
          icon: Icon(Icons.dark_mode),
          label: Text('Dark'),
        ),
      ],
      selected: {controller.themeMode},
      onSelectionChanged: (selected) {
        controller.setThemeMode(selected.first);
      },
    );
  }
}
```

---

## Best Practices Summary

1. **Always use `useMaterial3: true`** for Material 3 theming
2. **Use `ColorScheme.fromSeed()`** for automatic color harmony
3. **Access colors via context**: `Theme.of(context).colorScheme`
4. **Use semantic color roles** instead of hardcoded colors
5. **Implement ThemeExtensions** for custom semantic colors
6. **Support both light and dark themes** from the start
7. **Respect system preferences** with `ThemeMode.system`
8. **Consider high contrast themes** for accessibility
9. **Test animations** with `MediaQuery.disableAnimations`
10. **Use component themes** for consistent styling across the app
