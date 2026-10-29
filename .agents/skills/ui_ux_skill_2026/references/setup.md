# Quick Start & Setup

## 5-Minute Setup

To get up and running immediately with the 2026 Design System:

1.  **Copy Core Files**:
    Place these three files into `lib/core/theme/`:
    *   `design_tokens.dart` (Semantic colors)
    *   `mood_theme.dart` (Mood logic)
    *   `apca_contrast.dart` (Contrast validation)

2.  **Initialize in `main.dart`**:
    ```dart
    void main() {
      final moodProvider = MoodModeProvider();
      
      runApp(
        AnimatedBuilder(
          animation: moodProvider,
          builder: (context, _) {
            return MaterialApp(
              theme: moodProvider.theme, // Applies 2026 themes
              home: MyHomePage(moodProvider: moodProvider),
            );
          },
        ),
      );
    }
    ```

3.  **Start Using Tokens**:
    Stop using `Colors.blue` or hex codes.
    ```dart
    // ✅ 2026 Way
    Container(
      color: DesignTokens.surface.primary(context),
      child: Text(
        'Hello',
        style: TextStyle(color: DesignTokens.text.emphasis(context)),
      ),
    )
    ```

## Implementation Checklist

**Phase 1: Core Setup**
- [ ] Implement `design_tokens.dart`, `mood_theme.dart`, `apca_contrast.dart`.
- [ ] Replace hardcoded `Color` usages with `DesignTokens`.
- [ ] Verify background is Cloud Dancer (`#F0EEE9`) / True Charcoal (`#0B0D10`).

**Phase 2: Theming**
- [ ] Initialize `MoodModeProvider`.
- [ ] Test all 4 Mood Modes (Focus, Energy, Calm, Luxury).
- [ ] Implement Time-of-Day or Activity-based switching.

**Phase 3: Components**
- [ ] Replace buttons with `SquishyButton` (<100ms response).
- [ ] Replace spinners with `SkeletonLoader`.
- [ ] Use `GlassCard` for overlays and `GlassAppBar`.
- [ ] Use `SemanticBanner` for user feedback.

**Phase 4: Layout & Polish**
- [ ] Implement `BentoGrid` for dashboards.
- [ ] Add `PredictiveInsightCard` for AI features.
- [ ] Audit for APCA contrast compliance (≥60 Lc for body).
- [ ] Verify 60x60dp touch targets.
