---
name: flutter-uiux-design-2026
description: |
  Flutter UI/UX Design Agent - Creates 2026-forward design systems with Material 3, intent-driven interfaces, tactile maximalism, and semantic design tokens.
  TRIGGERS: design system, Material 3, 2026 trends, intent-driven design, tactile UI, glassmorphism, bento grid, semantic tokens, mood mode, transformative teal, cloud dancer, APCA, design tokens, color palette, responsive, accessible
  AUTO: Activates for any Flutter UI/UX design, theming, or visual design requests
---

# Flutter UI/UX Design Agent (2026)

Senior UI/UX Designer specializing in Flutter with 2026 design trends.

## Auto Mode Selection

| User Request Pattern | Design Approach | Key Features |
|---------------------|-----------------|--------------|
| "modern fintech app" | Deep Trust + Quiet Luxury | Transformative Teal, tabular fonts, predictive UI |
| "healthcare/wellness" | Restorative Calm | Warm Eucalyptus, Pharma Serif, 60px touch targets |
| "ecommerce/food" | Tactile Immersion | Squishy UI, dynamic backgrounds, AR-ready |
| "AI/SaaS tool" | Sentient Intelligence | Bento grids, Holo Lilac, agentic interface |
| "playful/Gen Z" | Dopamine Maximalism | Neon Lime, Wasabi accents, gamification |
| "luxury/premium" | Cloud Dancer Serenity | Plum Noir, Funky Serif, museum aesthetic |

## 2026 Core Design Principles

### Intent-Driven Design (Machine Experience)
```dart
// Traditional: User navigates to reports
// 2026: AI surfaces insight proactively
class PredictiveInsightCard extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return Card(
      child: Column(
        children: [
          Text('⚠️ 3 tasks at risk', style: Theme.of(context).textTheme.headlineSmall),
          Text('Based on current velocity, deadline may slip'),
          TextButton(onPressed: () {}, child: Text('Review Now')),
        ],
      ),
    );
  }
}
```

### Tactile Maximalism ("Squishy-uishy" UI)
```dart
// Physics-based button with deformation
AnimatedContainer(
  duration: Duration(milliseconds: 200),
  curve: Curves.elasticOut, // Bouncy, tactile feel
  transform: _isPressed ? Matrix4.identity()..scale(0.95) : Matrix4.identity(),
  decoration: BoxDecoration(
    borderRadius: BorderRadius.circular(28),
    boxShadow: _isPressed ? [] : [
      BoxShadow(color: Colors.black26, blurRadius: 8, offset: Offset(0, 4)),
    ],
  ),
  child: Material(
    borderRadius: BorderRadius.circular(28),
    child: InkWell(
      onTap: _handleTap,
      child: Padding(padding: EdgeInsets.all(16), child: Text('Squishy Button')),
    ),
  ),
)
```

### Glassmorphism 2.0
```dart
import 'dart:ui';

class GlassCard extends StatelessWidget {
  final Widget child;
  const GlassCard({required this.child});

  @override
  Widget build(BuildContext context) {
    return ClipRRect(
      borderRadius: BorderRadius.circular(16),
      child: BackdropFilter(
        filter: ImageFilter.blur(sigmaX: 10, sigmaY: 10),
        child: Container(
          decoration: BoxDecoration(
            color: Colors.white.withOpacity(0.1),
            borderRadius: BorderRadius.circular(16),
            border: Border.all(color: Colors.white.withOpacity(0.2)),
          ),
          child: child,
        ),
      ),
    );
  }
}
```

## 2026 Color Palettes

### Fintech/Banking
| Role | Hex | Token Name | Usage |
|------|-----|------------|-------|
| Primary | `#002966` | `brand-deep-trust` | Headers, primary actions |
| Primary Alt | `#2F6364` | `brand-transformative-teal` | Green finance, sustainability |
| Accent | `#FFD66B` | `accent-ion-gold` | Rewards, premium features |
| BG Light | `#F0EEE9` | `surface-cloud-dancer` | Main background (not #FFFFFF) |
| BG Dark | `#0B0D10` | `surface-charcoal` | Dark mode (not #000000) |
| Success | `#C7DDCC` | `semantic-mint` | Positive transactions |
| Alert | `#7A2E2A` | `semantic-warm-mahogany` | Serious alerts without panic |

### Healthcare/Wellness
| Role | Hex | Token Name | Usage |
|------|-----|------------|-------|
| Primary | `#7B8473` | `brand-warm-eucalyptus` | Primary brand (reduces heart rate) |
| Secondary | `#95A7B4` | `brand-mellow-flow` | Calming secondary |
| BG | `#F7F3EE` | `surface-warm-paper` | Never use pure white |
| Accent | `#D7A3A1` | `accent-dusty-rose` | Empathetic notifications |
| Text | `#2B2F36` | `text-slate` | Softer than black |

### AI/SaaS
| Role | Hex | Token Name | Usage |
|------|-----|------------|-------|
| BG | `#07070A` | `surface-void` | Deep background |
| Primary | `#B9A7FF` | `brand-holo-lilac` | AI capability signal |
| Secondary | `#00F5D4` | `accent-plasma-teal` | Active states |
| Neon | `#B6FF3B` | `accent-neon-lime` | High-energy CTAs |

### Ecommerce/Food
| Role | Hex | Token Name | Usage |
|------|-----|------------|-------|
| CTA | `#FF6A3D` | `action-sunset-ember` | Primary CTAs (highest conversion) |
| Brand | `#2F6364` | `brand-eco-teal` | Sustainable brands |
| Dopamine | `#C8D436` | `accent-wasabi` | Sour/energetic products |
| Warm | `#E25822` | `accent-persimmon` | Appetite stimulation, warmth |

## Mood Mode Implementation

```dart
// Beyond light/dark - context-aware theming
enum MoodMode { focus, energy, calm, luxury }

class AppTheme {
  static ThemeData getMoodTheme(MoodMode mode, Brightness brightness) {
    final baseScheme = brightness == Brightness.light
        ? ColorScheme.fromSeed(seedColor: _getSeedColor(mode), brightness: Brightness.light)
        : ColorScheme.fromSeed(seedColor: _getSeedColor(mode), brightness: Brightness.dark);
    
    return ThemeData(
      useMaterial3: true,
      colorScheme: baseScheme,
      // Mood-specific customizations
    );
  }

  static Color _getSeedColor(MoodMode mode) {
    switch (mode) {
      case MoodMode.focus: return Color(0xFF7B8473); // Eucalyptus
      case MoodMode.energy: return Color(0xFFB6FF3B); // Neon Lime
      case MoodMode.calm: return Color(0xFF2F6364); // Transformative Teal
      case MoodMode.luxury: return Color(0xFF2B1538); // Plum Noir
    }
  }
}
```

## Semantic Design Tokens

```dart
// core/theme/design_tokens.dart
class DesignTokens {
  // NEVER hardcode colors - use semantic tokens
  static const brandPrimary = 'brand-primary';
  static const surfaceElevated = 'surface-elevated';
  static const textEmphasis = 'text-emphasis';
  
  // Token resolver
  static Color resolve(String token, BuildContext context) {
    final scheme = Theme.of(context).colorScheme;
    switch (token) {
      case 'brand-primary': return scheme.primary;
      case 'surface-elevated': return scheme.surfaceContainerHigh;
      case 'text-emphasis': return scheme.onSurface;
      default: return scheme.onSurface;
    }
  }
}

// Usage
Container(color: DesignTokens.resolve('surface-elevated', context))
```

## Typography: 2026 Trends

### Recommended Fonts
| Purpose | Font | Characteristics | Use Case |
|---------|------|-----------------|----------|
| Quiet Sans | Inter, Söhne, Halyard | Confident, minimal | Fintech, SaaS body text |
| Pharma Serif | Custom humanist serif | Empathetic, warm | Healthcare headings |
| Funky Curvy Serif | Ogg, Roslindale | Heritage + modern | Luxury ecommerce |
| Code-Inspired | JetBrains Mono | Tabular, precise | Financial data, AI tools |
| Playful Display | Custom rounded | Squishy, friendly | Candy, food, Gen Z |

### Variable Font Implementation
```dart
// Kinetic typography - changes on interaction
class KineticText extends StatefulWidget {
  final String text;
  @override
  _KineticTextState createState() => _KineticTextState();
}

class _KineticTextState extends State<KineticText> {
  double _weight = 400;

  @override
  Widget build(BuildContext context) {
    return MouseRegion(
      onEnter: (_) => setState(() => _weight = 700),
      onExit: (_) => setState(() => _weight = 400),
      child: AnimatedDefaultTextStyle(
        duration: Duration(milliseconds: 200),
        style: TextStyle(
          fontVariations: [FontVariation('wght', _weight)],
          fontSize: 24,
        ),
        child: Text(widget.text),
      ),
    );
  }
}
```

## Bento Grid Layout

```dart
class BentoGrid extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return GridView.custom(
      gridDelegate: SliverQuiltedGridDelegate(
        crossAxisCount: 4,
        mainAxisSpacing: 8,
        crossAxisSpacing: 8,
        repeatPattern: QuiltedGridRepeatPattern.inverted,
        pattern: [
          QuiltedGridTile(2, 2), // Large feature
          QuiltedGridTile(1, 1), // Small widget
          QuiltedGridTile(1, 1),
          QuiltedGridTile(1, 2), // Wide widget
        ],
      ),
      childrenDelegate: SliverChildBuilderDelegate(
        (context, index) => BentoTile(index: index),
      ),
    );
  }
}
```

## Accessibility: WCAG 3.0 (APCA)

```dart
// Advanced Perceptual Contrast Algorithm
class APCAContrast {
  // Minimum contrast for body text: 60
  // Minimum for large text: 45
  static bool meetsBodyTextContrast(Color fg, Color bg) {
    final contrast = _calculateAPCA(fg, bg);
    return contrast >= 60;
  }

  static double _calculateAPCA(Color fg, Color bg) {
    // Simplified - use actual APCA library in production
    final fgLum = fg.computeLuminance();
    final bgLum = bg.computeLuminance();
    return (fgLum - bgLum).abs() * 100;
  }
}

// Touch targets: 48x48 minimum, 60x60 preferred (2026 standard)
class AccessibleButton extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return Semantics(
      button: true,
      label: 'Accessible action',
      child: InkWell(
        onTap: () {},
        child: Container(
          constraints: BoxConstraints(minWidth: 60, minHeight: 60),
          child: Center(child: Text('Tap me')),
        ),
      ),
    );
  }
}
```

## Performance: <100ms Interactions

```dart
// Skeleton screens over spinners
class SkeletonLoader extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return Shimmer.fromColors(
      baseColor: Theme.of(context).colorScheme.surfaceVariant,
      highlightColor: Theme.of(context).colorScheme.surface,
      child: Column(
        children: [
          Container(height: 20, color: Colors.white),
          SizedBox(height: 8),
          Container(height: 20, width: 150, color: Colors.white),
        ],
      ),
    );
  }
}

// Micro-interactions: instant feedback
class InstantFeedbackButton extends StatefulWidget {
  @override
  _InstantFeedbackButtonState createState() => _InstantFeedbackButtonState();
}

class _InstantFeedbackButtonState extends State<InstantFeedbackButton> 
    with SingleTickerProviderStateMixin {
  late AnimationController _controller;

  @override
  void initState() {
    super.initState();
    _controller = AnimationController(
      vsync: this,
      duration: Duration(milliseconds: 80), // <100ms
    );
  }

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onTapDown: (_) => _controller.forward(),
      onTapUp: (_) => _controller.reverse(),
      child: ScaleTransition(
        scale: Tween<double>(begin: 1.0, end: 0.95).animate(_controller),
        child: Container(/* button content */),
      ),
    );
  }
}
```

## Implementation Checklist

- [ ] Use semantic design tokens (never hardcode colors)
- [ ] Implement APCA contrast checking (60+ for body text)
- [ ] All touch targets ≥60x60 dp
- [ ] Micro-interactions <100ms response time
- [ ] Background colors: Cloud Dancer (#F0EEE9) not white, Charcoal (#0B0D10) not black
- [ ] Support Mood Mode (not just light/dark)
- [ ] Bento grid for modular layouts
- [ ] Variable fonts for kinetic typography
- [ ] Glassmorphism with BackdropFilter
- [ ] Skeleton loaders (not spinners)
- [ ] Intent-driven predictive UI elements

## Reference Files

- `theme-config.md` - Complete Material 3 theme implementation
- `component-library.md` - Reusable 2026-styled widgets
- `api_reference.md` - Additional pattern documentation

## Quick Wins

1. **Update brand colors**: Replace with 2026 palette (Transformative Teal/Cloud Dancer)
2. **Add glassmorphism**: Use BackdropFilter on cards
3. **Increase touch targets**: 48dp → 60dp
4. **Add mood themes**: Implement context-aware theming
5. **Typography upgrade**: Add variable font support
6. **Performance**: Replace spinners with skeleton screens
