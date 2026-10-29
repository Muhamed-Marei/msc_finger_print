# Troubleshooting & Validation

## Performance Metrics
| Metric | Target | Status |
| :--- | :--- | :--- |
| **Button Response** | <100ms | 80ms (Physics-based) |
| **Animation Rate** | 60fps | GPU Accelerated |
| **Touch Targets** | ≥60x60 dp | Enhanced Accessibility |
| **Contrast (Body)** | ≥60 Lc | APCA Validated |
| **Contrast (Large)**| ≥45 Lc | APCA Validated |
| **Contrast (UI)** | ≥30 Lc | APCA Validated |

## Contrast Validation (APCA)
Use `APCAContrast` to ensure accessibility.
```dart
// Run full theme validation
final report = APCAContrast.validateTheme(Theme.of(context));
if (!report.isCompliant) report.printReport();
```
*   **Body Text (14-16px)** must be **≥ 60 Lc**.
*   **Large Text (24px+)** must be **≥ 45 Lc**.

## Common Issues
1.  **"Can't find CustomColors"**: Ensure you have imported `design_tokens.dart` and are using `Theme.of(context).extension<CustomColors>()`.
2.  **"Button feels sluggish"**: Verify `AnimationController` duration is **<100ms** (ideally 80ms).
3.  **"Layout breaks on mobile"**: Switch from standard `Row`/`Column` to `ResponsiveBentoGrid`.

## Migration Examples
| Pattern | Old (Pre-2026) | New (2026) |
| :--- | :--- | :--- |
| **Color** | `Colors.white` | `DesignTokens.surface.primary(context)` |
| **Card** | `Card(color: Colors.grey)` | `Card(color: DesignTokens.surface.elevated(context))` |
| **Success** | `Colors.green` | `DesignTokens.semantic.success(context)` |
