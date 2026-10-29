# Error Pattern Recognition

## Build Errors

| Pattern | Category | Likely Cause |
|---------|----------|--------------|
| `is not defined` | import | Missing import or wrong version |
| `isn't defined for the type` | api_change | Package API changed |
| `Could not find a generator` | codegen | Missing build_runner setup |
| `Part directive` | codegen | Missing part statement |
| `version solving failed` | dependency | Version conflict |
| `Cannot fit requested classes` | android | Needs multidex |
| `Minimum deployment target` | ios | iOS version mismatch |

## Runtime Errors

| Pattern | Category | Likely Cause |
|---------|----------|--------------|
| `was used after being disposed` | lifecycle | Widget unmounted |
| `setState() called after dispose` | lifecycle | Async callback after dispose |
| `No Firebase App` | firebase | Firebase not initialized |
| `PlatformException` | platform | Native code issue |
| `RangeError` | logic | Index out of bounds |
| `Null check operator` | null_safety | Unexpected null value |

## Dependency Errors

| Pattern | Category | Likely Cause |
|---------|----------|--------------|
| `Because X depends on Y` | conflict | Version incompatibility |
| `Could not resolve` | network | Pub.dev unreachable |
| `Incompatible` | version | SDK version mismatch |

## Platform Errors

### iOS Patterns
| Pattern | Likely Fix |
|---------|------------|
| `signing certificate` | Fix code signing |
| `Podfile` | pod install |
| `CocoaPods` | pod deintegrate && pod install |
| `provisioning profile` | Regenerate profiles |

### Android Patterns
| Pattern | Likely Fix |
|---------|------------|
| `Gradle` | ./gradlew clean |
| `minSdk` | Update minSdk in build.gradle |
| `R8` / `ProGuard` | Add keep rules |
| `NDK` | Install NDK version |
