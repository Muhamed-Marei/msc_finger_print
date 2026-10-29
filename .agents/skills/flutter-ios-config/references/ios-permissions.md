# iOS Permissions Reference

Complete reference for all iOS permissions in Flutter applications. Each permission requires a usage description string in Info.plist, and many require additional configuration in entitlements or capabilities.

## Permission Configuration Overview

| Permission | Info.plist Key | Entitlement Required | Capability |
|------------|---------------|---------------------|------------|
| Camera | NSCameraUsageDescription | No | No |
| Photo Library (Read) | NSPhotoLibraryUsageDescription | No | No |
| Photo Library (Write) | NSPhotoLibraryAddUsageDescription | No | No |
| Location (When In Use) | NSLocationWhenInUseUsageDescription | No | No |
| Location (Always) | NSLocationAlwaysAndWhenInUseUsageDescription | No | Background Modes |
| Microphone | NSMicrophoneUsageDescription | No | No |
| Contacts | NSContactsUsageDescription | No | No |
| Calendar | NSCalendarsUsageDescription | No | No |
| Reminders | NSRemindersUsageDescription | No | No |
| Bluetooth | NSBluetoothAlwaysUsageDescription | No | No |
| Face ID | NSFaceIDUsageDescription | No | No |
| Push Notifications | N/A | aps-environment | Push Notifications |
| Health | NSHealthShareUsageDescription | com.apple.developer.healthkit | HealthKit |
| Motion | NSMotionUsageDescription | No | No |
| Speech Recognition | NSSpeechRecognitionUsageDescription | No | No |
| Tracking (iOS 14+) | NSUserTrackingUsageDescription | No | No |
| Apple Music | NSAppleMusicUsageDescription | No | No |
| Siri | NSSiriUsageDescription | com.apple.developer.siri | Siri |
| HomeKit | NSHomeKitUsageDescription | com.apple.developer.homekit | HomeKit |
| NFC | NFCReaderUsageDescription | com.apple.developer.nfc.readersession.formats | Near Field Communication |

---

## Camera Permission

**Required for:** Taking photos, recording videos, QR code scanning

### Info.plist Configuration

```xml
<key>NSCameraUsageDescription</key>
<string>This app needs camera access to take photos for your profile and scan QR codes.</string>
```

### Flutter Packages

```yaml
# pubspec.yaml
dependencies:
  camera: ^0.10.5+5
  image_picker: ^1.0.4
  mobile_scanner: ^3.5.5  # For QR codes
```

### Dart Implementation

```dart
import 'package:permission_handler/permission_handler.dart';

Future<bool> requestCameraPermission() async {
  final status = await Permission.camera.request();
  if (status.isPermanentlyDenied) {
    // Open app settings
    await openAppSettings();
    return false;
  }
  return status.isGranted;
}
```

### Best Practices

- Request permission only when needed, not at app launch
- Provide clear context before showing system dialog
- Handle permanently denied state gracefully
- Consider showing a custom pre-permission dialog

---

## Photo Library Permission

**Required for:** Selecting photos/videos, saving media

### Info.plist Configuration

```xml
<!-- Read access -->
<key>NSPhotoLibraryUsageDescription</key>
<string>This app needs access to your photo library to select images for your posts.</string>

<!-- Write access (saving photos) -->
<key>NSPhotoLibraryAddUsageDescription</key>
<string>This app needs permission to save photos to your library.</string>
```

### iOS 14+ Limited Access

Starting iOS 14, users can grant limited photo access. Handle this in your app:

```dart
import 'package:permission_handler/permission_handler.dart';

Future<PermissionStatus> requestPhotoPermission() async {
  final status = await Permission.photos.request();

  if (status == PermissionStatus.limited) {
    // User granted access to selected photos only
    // You can request access to more photos via PHPhotoLibrary
  }

  return status;
}
```

### Flutter Packages

```yaml
dependencies:
  image_picker: ^1.0.4
  photo_manager: ^2.8.1  # Advanced photo library access
```

---

## Location Permission

**Required for:** Maps, nearby places, geofencing, navigation

### Info.plist Configuration

```xml
<!-- Basic location (when app is in use) -->
<key>NSLocationWhenInUseUsageDescription</key>
<string>This app needs your location to show nearby restaurants and provide directions.</string>

<!-- Background location (always) -->
<key>NSLocationAlwaysAndWhenInUseUsageDescription</key>
<string>This app needs continuous location access to provide turn-by-turn navigation even when the app is in the background.</string>

<!-- Legacy key (iOS 10 and earlier) -->
<key>NSLocationAlwaysUsageDescription</key>
<string>This app needs background location access for tracking your runs.</string>
```

### Background Location Configuration

For background location, also add to Info.plist:

```xml
<key>UIBackgroundModes</key>
<array>
    <string>location</string>
</array>
```

### Location Accuracy (iOS 14+)

iOS 14 introduced approximate vs. precise location:

```xml
<!-- Optional: Set default accuracy level -->
<key>NSLocationDefaultAccuracyReduced</key>
<false/>  <!-- false = request precise, true = request approximate -->
```

### Flutter Packages

```yaml
dependencies:
  geolocator: ^10.1.0
  geocoding: ^2.1.1
  location: ^5.0.3
```

### Dart Implementation

```dart
import 'package:geolocator/geolocator.dart';

Future<Position?> getCurrentLocation() async {
  // Check if location services are enabled
  bool serviceEnabled = await Geolocator.isLocationServiceEnabled();
  if (!serviceEnabled) {
    // Location services are disabled
    return null;
  }

  // Check permission
  LocationPermission permission = await Geolocator.checkPermission();
  if (permission == LocationPermission.denied) {
    permission = await Geolocator.requestPermission();
    if (permission == LocationPermission.denied) {
      return null;
    }
  }

  if (permission == LocationPermission.deniedForever) {
    // Permissions are permanently denied
    return null;
  }

  // Get current position
  return await Geolocator.getCurrentPosition(
    desiredAccuracy: LocationAccuracy.high,
  );
}
```

### App Store Review Notes

- Background location requires strong justification
- Apple may reject apps that request "Always" location without clear need
- Provide detailed explanation in App Store review notes

---

## Push Notifications

**Required for:** Remote notifications, alerts, badges, sounds

### Entitlements Configuration

```xml
<!-- Runner.entitlements -->
<key>aps-environment</key>
<string>development</string>  <!-- Use "production" for App Store builds -->
```

### Enable in Xcode

1. Select target > Signing & Capabilities
2. Click "+ Capability"
3. Add "Push Notifications"
4. Add "Background Modes" > Check "Remote notifications"

### Info.plist (Background Fetch)

```xml
<key>UIBackgroundModes</key>
<array>
    <string>remote-notification</string>
</array>
```

### AppDelegate.swift Setup

```swift
import UIKit
import Flutter
import UserNotifications

@UIApplicationMain
@objc class AppDelegate: FlutterAppDelegate {
    override func application(
        _ application: UIApplication,
        didFinishLaunchingWithOptions launchOptions: [UIApplication.LaunchOptionsKey: Any]?
    ) -> Bool {
        // Request notification permission
        UNUserNotificationCenter.current().delegate = self

        let authOptions: UNAuthorizationOptions = [.alert, .badge, .sound]
        UNUserNotificationCenter.current().requestAuthorization(
            options: authOptions,
            completionHandler: { _, _ in }
        )

        application.registerForRemoteNotifications()

        GeneratedPluginRegistrant.register(with: self)
        return super.application(application, didFinishLaunchingWithOptions: launchOptions)
    }

    override func application(
        _ application: UIApplication,
        didRegisterForRemoteNotificationsWithDeviceToken deviceToken: Data
    ) {
        // Send token to your server
        let tokenParts = deviceToken.map { data in String(format: "%02.2hhx", data) }
        let token = tokenParts.joined()
        print("Device Token: \(token)")
    }

    override func application(
        _ application: UIApplication,
        didFailToRegisterForRemoteNotificationsWithError error: Error
    ) {
        print("Failed to register: \(error)")
    }
}
```

### Flutter Packages

```yaml
dependencies:
  firebase_messaging: ^14.7.6
  flutter_local_notifications: ^16.2.0
```

---

## Microphone Permission

**Required for:** Audio recording, voice messages, video calls

### Info.plist Configuration

```xml
<key>NSMicrophoneUsageDescription</key>
<string>This app needs microphone access to record voice messages and participate in audio calls.</string>
```

### Flutter Packages

```yaml
dependencies:
  record: ^5.0.4
  audio_session: ^0.1.18
  just_audio: ^0.9.36
```

---

## Contacts Permission

**Required for:** Accessing user contacts, invite friends

### Info.plist Configuration

```xml
<key>NSContactsUsageDescription</key>
<string>This app needs access to your contacts to help you find friends who are already using the app.</string>
```

### Flutter Packages

```yaml
dependencies:
  contacts_service: ^0.6.3
  flutter_contacts: ^1.1.7+1
```

---

## Calendar Permission

**Required for:** Creating/reading calendar events

### Info.plist Configuration

```xml
<key>NSCalendarsUsageDescription</key>
<string>This app needs calendar access to add events and reminders for your scheduled activities.</string>
```

### Flutter Packages

```yaml
dependencies:
  device_calendar: ^4.3.1
```

---

## Reminders Permission

**Required for:** Creating/reading reminders

### Info.plist Configuration

```xml
<key>NSRemindersUsageDescription</key>
<string>This app needs access to your reminders to create task notifications.</string>
```

---

## Bluetooth Permission

**Required for:** Connecting to Bluetooth devices, BLE scanning

### Info.plist Configuration

```xml
<!-- Always usage (iOS 13+) -->
<key>NSBluetoothAlwaysUsageDescription</key>
<string>This app uses Bluetooth to connect to fitness trackers and heart rate monitors.</string>

<!-- Peripheral usage (iOS 6-12) -->
<key>NSBluetoothPeripheralUsageDescription</key>
<string>This app uses Bluetooth to communicate with nearby devices.</string>
```

### Background Bluetooth

```xml
<key>UIBackgroundModes</key>
<array>
    <string>bluetooth-central</string>
    <string>bluetooth-peripheral</string>
</array>
```

### Flutter Packages

```yaml
dependencies:
  flutter_blue_plus: ^1.29.6
  flutter_reactive_ble: ^5.2.0
```

---

## Face ID Permission

**Required for:** Biometric authentication using Face ID

### Info.plist Configuration

```xml
<key>NSFaceIDUsageDescription</key>
<string>This app uses Face ID for secure and quick authentication.</string>
```

### Flutter Packages

```yaml
dependencies:
  local_auth: ^2.1.7
```

### Dart Implementation

```dart
import 'package:local_auth/local_auth.dart';

final LocalAuthentication auth = LocalAuthentication();

Future<bool> authenticateWithBiometrics() async {
  try {
    // Check if biometrics are available
    final bool canAuthenticateWithBiometrics = await auth.canCheckBiometrics;
    final bool canAuthenticate = canAuthenticateWithBiometrics || await auth.isDeviceSupported();

    if (!canAuthenticate) {
      return false;
    }

    // Get available biometric types
    final List<BiometricType> availableBiometrics = await auth.getAvailableBiometrics();

    // Authenticate
    final bool didAuthenticate = await auth.authenticate(
      localizedReason: 'Please authenticate to access your account',
      options: const AuthenticationOptions(
        stickyAuth: true,
        biometricOnly: false,
      ),
    );

    return didAuthenticate;
  } catch (e) {
    return false;
  }
}
```

---

## Health Permission

**Required for:** Reading/writing HealthKit data

### Info.plist Configuration

```xml
<!-- Reading health data -->
<key>NSHealthShareUsageDescription</key>
<string>This app reads your health data to track your fitness progress and provide personalized recommendations.</string>

<!-- Writing health data -->
<key>NSHealthUpdateUsageDescription</key>
<string>This app writes workout data to Health to keep your fitness records complete.</string>
```

### Entitlements Configuration

```xml
<!-- Runner.entitlements -->
<key>com.apple.developer.healthkit</key>
<true/>
<key>com.apple.developer.healthkit.access</key>
<array/>

<!-- For background delivery -->
<key>com.apple.developer.healthkit.background-delivery</key>
<true/>
```

### Enable in Xcode

1. Select target > Signing & Capabilities
2. Click "+ Capability"
3. Add "HealthKit"
4. Check specific data types if needed

### Flutter Packages

```yaml
dependencies:
  health: ^8.0.0
```

### App Store Requirements

- Health apps must provide a privacy policy
- Must explain how health data is used
- Cannot share health data with third parties without explicit consent

---

## Motion Permission

**Required for:** Fitness tracking, step counting, activity recognition

### Info.plist Configuration

```xml
<key>NSMotionUsageDescription</key>
<string>This app uses motion data to count your steps and track physical activity.</string>
```

### Flutter Packages

```yaml
dependencies:
  pedometer: ^4.0.1
  sensors_plus: ^4.0.2
```

---

## Speech Recognition Permission

**Required for:** Voice commands, dictation, transcription

### Info.plist Configuration

```xml
<key>NSSpeechRecognitionUsageDescription</key>
<string>This app uses speech recognition to convert your voice messages to text.</string>
```

### Also Requires Microphone

```xml
<key>NSMicrophoneUsageDescription</key>
<string>This app needs microphone access for speech recognition.</string>
```

### Flutter Packages

```yaml
dependencies:
  speech_to_text: ^6.5.1
```

---

## App Tracking Transparency (iOS 14+)

**Required for:** IDFA access, cross-app tracking, personalized ads

### Info.plist Configuration

```xml
<key>NSUserTrackingUsageDescription</key>
<string>This app uses tracking to provide personalized advertisements and improve your experience.</string>
```

### Flutter Packages

```yaml
dependencies:
  app_tracking_transparency: ^2.0.4
```

### Dart Implementation

```dart
import 'package:app_tracking_transparency/app_tracking_transparency.dart';

Future<void> requestTrackingPermission() async {
  // Wait for app to be ready
  await Future.delayed(const Duration(milliseconds: 200));

  // Check current status
  final status = await AppTrackingTransparency.trackingAuthorizationStatus;

  if (status == TrackingStatus.notDetermined) {
    // Request permission
    final result = await AppTrackingTransparency.requestTrackingAuthorization();

    switch (result) {
      case TrackingStatus.authorized:
        // User allowed tracking - get IDFA
        final idfa = await AppTrackingTransparency.getAdvertisingIdentifier();
        print('IDFA: $idfa');
        break;
      case TrackingStatus.denied:
        // User denied tracking
        break;
      case TrackingStatus.restricted:
        // Tracking is restricted (e.g., parental controls)
        break;
      case TrackingStatus.notDetermined:
        // Still not determined
        break;
      default:
        break;
    }
  }
}
```

### Best Practices

- Request after onboarding, not immediately at launch
- Explain benefits before showing system prompt
- Handle denied state gracefully (app should work without tracking)

---

## Apple Music Permission

**Required for:** Accessing Apple Music library, playing Apple Music content

### Info.plist Configuration

```xml
<key>NSAppleMusicUsageDescription</key>
<string>This app needs access to your Apple Music library to play your favorite songs during workouts.</string>
```

### Flutter Packages

```yaml
dependencies:
  just_audio: ^0.9.36
```

---

## Siri Permission

**Required for:** Siri Shortcuts, voice commands

### Info.plist Configuration

```xml
<key>NSSiriUsageDescription</key>
<string>This app uses Siri to let you quickly start workouts with voice commands.</string>
```

### Entitlements Configuration

```xml
<key>com.apple.developer.siri</key>
<true/>
```

---

## HomeKit Permission

**Required for:** Controlling smart home devices

### Info.plist Configuration

```xml
<key>NSHomeKitUsageDescription</key>
<string>This app needs HomeKit access to control your smart home devices.</string>
```

### Entitlements Configuration

```xml
<key>com.apple.developer.homekit</key>
<true/>
```

---

## NFC Permission

**Required for:** Reading NFC tags, Apple Pay

### Info.plist Configuration

```xml
<key>NFCReaderUsageDescription</key>
<string>This app uses NFC to scan product tags and verify authenticity.</string>

<!-- Specify supported NFC tag types -->
<key>com.apple.developer.nfc.readersession.iso7816.select-identifiers</key>
<array>
    <string>A000000004101001</string>  <!-- Example AID -->
</array>
```

### Entitlements Configuration

```xml
<key>com.apple.developer.nfc.readersession.formats</key>
<array>
    <string>NDEF</string>
    <string>TAG</string>
</array>
```

### Flutter Packages

```yaml
dependencies:
  nfc_manager: ^3.3.0
```

---

## Local Network Permission (iOS 14+)

**Required for:** Discovering devices on local network, Bonjour services

### Info.plist Configuration

```xml
<key>NSLocalNetworkUsageDescription</key>
<string>This app needs local network access to discover and connect to smart TVs and speakers.</string>

<!-- Bonjour services to browse -->
<key>NSBonjourServices</key>
<array>
    <string>_airplay._tcp</string>
    <string>_googlecast._tcp</string>
    <string>_http._tcp</string>
</array>
```

---

## Wi-Fi Information (iOS 13+)

**Required for:** Getting current Wi-Fi SSID/BSSID

### Entitlements Configuration

```xml
<key>com.apple.developer.networking.wifi-info</key>
<true/>
```

### Enable in Xcode

1. Select target > Signing & Capabilities
2. Click "+ Capability"
3. Add "Access WiFi Information"

---

## Permission Handler Package

The `permission_handler` package provides a unified API for all permissions:

```yaml
dependencies:
  permission_handler: ^11.1.0
```

### iOS-Specific Setup

Add to Podfile:

```ruby
post_install do |installer|
  installer.pods_project.targets.each do |target|
    flutter_additional_ios_build_settings(target)

    target.build_configurations.each do |config|
      # Enable permissions
      config.build_settings['GCC_PREPROCESSOR_DEFINITIONS'] ||= [
        '$(inherited)',
        'PERMISSION_CAMERA=1',
        'PERMISSION_PHOTOS=1',
        'PERMISSION_LOCATION=1',
        'PERMISSION_MICROPHONE=1',
        'PERMISSION_CONTACTS=1',
        'PERMISSION_BLUETOOTH=1',
        'PERMISSION_APP_TRACKING_TRANSPARENCY=1',
        'PERMISSION_NOTIFICATIONS=1',
      ]
    end
  end
end
```

### Unified Permission Request

```dart
import 'package:permission_handler/permission_handler.dart';

class PermissionService {
  Future<bool> requestPermission(Permission permission) async {
    final status = await permission.status;

    if (status.isGranted) {
      return true;
    }

    if (status.isDenied) {
      final result = await permission.request();
      return result.isGranted;
    }

    if (status.isPermanentlyDenied) {
      // Open app settings
      await openAppSettings();
      return false;
    }

    return false;
  }

  Future<Map<Permission, bool>> requestMultiplePermissions(
    List<Permission> permissions,
  ) async {
    final results = <Permission, bool>{};

    for (final permission in permissions) {
      results[permission] = await requestPermission(permission);
    }

    return results;
  }
}
```

---

## Best Practices Summary

1. **Request at the right time** - Only when the feature is about to be used
2. **Explain before asking** - Use a custom dialog to explain why permission is needed
3. **Handle denial gracefully** - App should work (with reduced functionality) if denied
4. **Provide alternatives** - Offer manual input options when possible
5. **Check before requesting** - Use `permission.status` before calling `request()`
6. **Handle permanently denied** - Direct users to Settings with clear instructions
7. **Be specific in descriptions** - Clearly state exactly why and how the permission will be used
8. **Minimize permissions** - Only request what you actually need
9. **Test all scenarios** - Test granted, denied, and permanently denied states
10. **Update for new iOS versions** - New iOS versions often add new privacy requirements
