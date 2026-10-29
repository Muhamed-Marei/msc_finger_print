# 2026 Design Patterns - Quick Reference

## Key Changes from 2020s Design

| Aspect | Old (2020-2024) | New (2026) |
|--------|-----------------|------------|
| **Color Philosophy** | Pure white/black, flat colors | Cloud Dancer/Charcoal, bio-digital balance |
| **Backgrounds** | #FFFFFF / #000000 | #F0EEE9 / #0B0D10 |
| **Theming** | Light/Dark toggle | Mood Mode (focus/energy/calm/luxury) |
| **Buttons** | Flat, minimal animation | Squishy, physics-based, deformable |
| **Design System** | Hardcoded hex values | Semantic design tokens |
| **Typography** | Static, geometric sans | Variable, kinetic, expressive |
| **Contrast** | WCAG 2.1 AA (4.5:1) | WCAG 3.0 APCA (60+) |
| **Touch Targets** | 48x48 dp | 60x60 dp |
| **Loading States** | Spinners | Skeleton screens |
| **Interaction Speed** | 200-400ms | <100ms instant feedback |
| **UX Paradigm** | User-initiated actions | Intent-driven, predictive AI |
| **Visual Style** | Flat, minimal | Tactile maximalism, glassmorphism 2.0 |

## Core 2026 Patterns

### 1. Tactile Maximalism
- Physics-based animations (bounce, deform, ripple)
- Specular highlights, subsurface scattering
- 3D appearance without heavy rendering
- Elastic curves (Curves.elasticOut, Curves.easeOutBack)

### 2. Glassmorphism 2.0
- BackdropFilter with blur (sigma 10-20)
- Semi-transparent surfaces (opacity 0.1-0.2)
- Border highlights (white 0.2 opacity)
- Subtle shadow layers

### 3. Intent-Driven UI
- Proactive insights ("3 tasks at risk")
- Predictive suggestions
- Contextual prompts
- AI-generated transient interfaces

### 4. Bento Grid Layouts
- Modular, asymmetric boxes
- Responsive storytelling
- Variable tile sizes
- Visual hierarchy through size

### 5. Mood-Based Theming
- Context-aware color shifts
- Time-of-day adaptation
- Activity-based modes
- Emotional color mapping

## Material 3 + 2026 Integration

### Color Scheme Generation
```dart
// Use seed colors from 2026 palettes
ColorScheme.fromSeed(
  seedColor: Color(0xFF2F6364), // Transformative Teal
  brightness: Brightness.light,
)
```

### Semantic Tokens
```dart
// Never use hardcoded colors
Container(
  color: Theme.of(context).colorScheme.surfaceContainerLow,
  // NOT: color: Color(0xFFF0F0F0)
)
```

### Touch Accessibility
```dart
// 2026 minimum: 60x60 dp
Container(
  constraints: BoxConstraints(minWidth: 60, minHeight: 60),
  child: IconButton(...),
)
```

## Sector-Specific Quick Patterns

### Fintech
```dart
// Deep Trust palette
primary: Color(0xFF002966)
accent: Color(0xFFFFD66B) // Ion Gold for rewards
bgLight: Color(0xFFF0EEE9) // Cloud Dancer
bgDark: Color(0xFF0B0D10) // True Charcoal

// Tabular fonts for numbers
style: GoogleFonts.jetBrainsMono(
  fontFeatures: [FontFeature.tabularFigures()],
)
```

### Healthcare
```dart
// Restorative Calm palette
primary: Color(0xFF7B8473) // Warm Eucalyptus
accent: Color(0xFFD7A3A1) // Dusty Rose
bg: Color(0xFFF7F3EE) // Warm Paper

// Pharma Serif + high x-height sans
headings: 'P22 Mackinac' or custom humanist serif
body: GoogleFonts.openSans()

// Generous touch targets
minHeight: 60, minWidth: 60
```

### E-commerce
```dart
// High-conversion CTA
cta: Color(0xFFFF6A3D) // Sunset Ember

// Dynamic backgrounds (adapt to product)
Container(
  color: _getProductMoodColor(product),
)

// Massive typography
fontSize: MediaQuery.of(context).size.width * 0.5
```

### AI/SaaS
```dart
// Sentient Intelligence palette
bg: Color(0xFF07070A) // Void
primary: Color(0xFFB9A7FF) // Holo Lilac
accent: Color(0xFF00F5D4) // Plasma Teal

// Bento grid layout
GridView.custom(
  gridDelegate: SliverQuiltedGridDelegate(...),
)
```

## Animation Timing

| Interaction Type | Duration | Curve |
|------------------|----------|-------|
| Button press | 80-100ms | Curves.easeOut |
| Page transition | 250-350ms | Curves.easeInOutCubic |
| Elastic bounce | 400-600ms | Curves.elasticOut |
| Skeleton shimmer | 1500-2000ms | Curves.linear (loop) |
| Micro-interaction | <100ms | Curves.easeOutQuart |

## Performance Targets

| Metric | Target | Impact |
|--------|--------|--------|
| First Paint | <100ms | Skeleton screens, not spinners |
| Button Tap Response | <16ms (1 frame) | Haptic feedback + visual |
| Scroll FPS | 60fps | GPU-accelerated animations |
| Image Load | Progressive | Blur-up technique |
| Animation Jank | 0 dropped frames | profile mode validation |

## Accessibility Checklist

- [ ] APCA contrast ≥60 for body text
- [ ] Touch targets ≥60x60 dp
- [ ] Semantic labels on all interactive elements
- [ ] Keyboard navigation support
- [ ] Screen reader optimization
- [ ] Reduced motion alternative (respect disableAnimations)
- [ ] Color-blind safe palettes (test with sim)
- [ ] Font scaling support (up to 200%)

## Forbidden Patterns (2026)

❌ Pure white backgrounds (#FFFFFF) - use Cloud Dancer (#F0EEE9)  
❌ Pure black backgrounds (#000000) - use Charcoal (#0B0D10) or Void (#07070A)  
❌ Hardcoded color values - use semantic tokens  
❌ Circular progress spinners - use skeleton screens  
❌ Static, geometric sans for all text - add personality with variable fonts  
❌ 48x48 touch targets - minimum 60x60  
❌ WCAG 2.1 only - upgrade to APCA  
❌ Generic "Tech Blue" (#2196F3) - use sector-specific palette  

## Quick Wins Implementation Order

1. **Color Update** (1 day)
   - Replace pure white/black
   - Implement Cloud Dancer/Charcoal
   - Add Transformative Teal as seed

2. **Touch Targets** (1 day)
   - Audit all interactive elements
   - Increase to 60x60 minimum

3. **Glassmorphism** (2 days)
   - Add BackdropFilter to cards
   - Implement blur effects
   - Test performance

4. **Typography** (2 days)
   - Add Google Fonts or custom fonts
   - Implement variable font support
   - Update text theme

5. **Interactions** (3 days)
   - Replace spinners with skeletons
   - Add elastic button animations
   - Ensure <100ms feedback

6. **Mood Mode** (3 days)
   - Implement theme switching
   - Add context-aware seeds
   - Test all modes

7. **Semantic Tokens** (5 days)
   - Audit all color usage
   - Create token system
   - Replace hardcoded values

## Testing Protocol

1. **Visual Regression**
   - Screenshot tests for all themes
   - Compare against design specs

2. **Performance**
   - Profile mode: no jank
   - Memory usage: <100MB increase
   - Bundle size: optimize fonts

3. **Accessibility**
   - Contrast analyzer (APCA)
   - Touch target validator
   - Screen reader navigation

4. **Cross-Platform**
   - Android (Material You integration)
   - iOS (Cupertino harmony)
   - Web (responsive breakpoints)
   - Desktop (keyboard navigation)

## Resources

- Color Palettes: `data/color_palettes_2026.json`
- Typography: `data/typography_2026.json`
- Complete Theme: `theme-config.md`
- Components: `component-library.md`
