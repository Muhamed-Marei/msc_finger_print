# Android Permissions Reference

## Permission Categories

Android permissions are divided into several categories based on their protection level and the type of access they grant.

---

## 1. Normal Permissions (Auto-Granted)

These permissions are automatically granted at install time and do not require user approval.

### Network Permissions

```xml
<!-- Access to the internet -->
<uses-permission android:name="android.permission.INTERNET" />

<!-- Check network connectivity status -->
<uses-permission android:name="android.permission.ACCESS_NETWORK_STATE" />

<!-- Check WiFi connectivity status -->
<uses-permission android:name="android.permission.ACCESS_WIFI_STATE" />

<!-- Change WiFi connectivity state -->
<uses-permission android:name="android.permission.CHANGE_WIFI_STATE" />

<!-- Change network connectivity state -->
<uses-permission android:name="android.permission.CHANGE_NETWORK_STATE" />
```

### Device State Permissions

```xml
<!-- Vibrate the device -->
<uses-permission android:name="android.permission.VIBRATE" />

<!-- Prevent processor from sleeping -->
<uses-permission android:name="android.permission.WAKE_LOCK" />

<!-- Receive broadcast after boot completes -->
<uses-permission android:name="android.permission.RECEIVE_BOOT_COMPLETED" />

<!-- Set an alarm -->
<uses-permission android:name="android.permission.SET_ALARM" />

<!-- Run foreground services -->
<uses-permission android:name="android.permission.FOREGROUND_SERVICE" />

<!-- Request to ignore battery optimizations -->
<uses-permission android:name="android.permission.REQUEST_IGNORE_BATTERY_OPTIMIZATIONS" />
```

### Bluetooth (Basic)

```xml
<!-- Basic Bluetooth (Android 11 and below) -->
<uses-permission android:name="android.permission.BLUETOOTH"
    android:maxSdkVersion="30" />
<uses-permission android:name="android.permission.BLUETOOTH_ADMIN"
    android:maxSdkVersion="30" />
```

### Biometric

```xml
<!-- Use biometric authentication -->
<uses-permission android:name="android.permission.USE_BIOMETRIC" />

<!-- Deprecated fingerprint permission (still needed for some APIs) -->
<uses-permission android:name="android.permission.USE_FINGERPRINT" />
```

### NFC

```xml
<!-- NFC access -->
<uses-permission android:name="android.permission.NFC" />
```

---

## 2. Dangerous Permissions (Runtime Request Required)

These permissions require explicit user approval at runtime (Android 6.0+).

### Location Permissions

```xml
<!-- Approximate location via network -->
<uses-permission android:name="android.permission.ACCESS_COARSE_LOCATION" />

<!-- Precise location via GPS -->
<uses-permission android:name="android.permission.ACCESS_FINE_LOCATION" />

<!-- Background location access (Android 10+) - Requires separate request -->
<uses-permission android:name="android.permission.ACCESS_BACKGROUND_LOCATION" />
```

**Runtime Request Pattern (Dart):**

```dart
import 'package:permission_handler/permission_handler.dart';

Future<bool> requestLocationPermission() async {
  // First, request foreground location
  var status = await Permission.locationWhenInUse.request();
  
  if (!status.isGranted) {
    return false;
  }
  
  // For background location (must be requested separately on Android 10+)
  if (await Permission.locationAlways.isDenied) {
    // Show rationale explaining why background location is needed
    status = await Permission.locationAlways.request();
  }
  
  return status.isGranted;
}
```

### Camera & Microphone

```xml
<!-- Camera access -->
<uses-permission android:name="android.permission.CAMERA" />

<!-- Microphone access -->
<uses-permission android:name="android.permission.RECORD_AUDIO" />
```

**Runtime Request Pattern:**

```dart
Future<bool> requestCameraPermission() async {
  final status = await Permission.camera.request();
  
  if (status.isPermanentlyDenied) {
    // User permanently denied, direct to settings
    await openAppSettings();
    return false;
  }
  
  return status.isGranted;
}

Future<bool> requestMicrophonePermission() async {
  return (await Permission.microphone.request()).isGranted;
}
```

### Storage Permissions (Version-Specific)

```xml
<!-- Android 9 and below: Full storage access -->
<uses-permission android:name="android.permission.READ_EXTERNAL_STORAGE"
    android:maxSdkVersion="32" />
<uses-permission android:name="android.permission.WRITE_EXTERNAL_STORAGE"
    android:maxSdkVersion="29"
    tools:ignore="ScopedStorage" />

<!-- Android 10: Opt-out of scoped storage (temporary) -->
<application android:requestLegacyExternalStorage="true">

<!-- Android 11+: Manage all files (requires special approval) -->
<uses-permission android:name="android.permission.MANAGE_EXTERNAL_STORAGE"
    tools:ignore="ScopedStorage" />

<!-- Android 13+: Granular media permissions -->
<uses-permission android:name="android.permission.READ_MEDIA_IMAGES" />
<uses-permission android:name="android.permission.READ_MEDIA_VIDEO" />
<uses-permission android:name="android.permission.READ_MEDIA_AUDIO" />

<!-- Android 14+: Selected photos access -->
<uses-permission android:name="android.permission.READ_MEDIA_VISUAL_USER_SELECTED" />
```

**Version-Aware Storage Request:**

```dart
import 'dart:io';
import 'package:device_info_plus/device_info_plus.dart';
import 'package:permission_handler/permission_handler.dart';

Future<bool> requestStoragePermission() async {
  if (!Platform.isAndroid) return true;
  
  final androidInfo = await DeviceInfoPlugin().androidInfo;
  final sdkInt = androidInfo.version.sdkInt;
  
  if (sdkInt >= 34) {
    // Android 14+: Request selected photos or full access
    final photos = await Permission.photos.request();
    final videos = await Permission.videos.request();
    return photos.isGranted && videos.isGranted;
    
  } else if (sdkInt >= 33) {
    // Android 13: Granular media permissions
    final statuses = await [
      Permission.photos,
      Permission.videos,
      Permission.audio,
    ].request();
    return statuses.values.every((s) => s.isGranted);
    
  } else if (sdkInt >= 30) {
    // Android 11-12: Manage external storage or media location
    if (await Permission.manageExternalStorage.isGranted) {
      return true;
    }
    
    // Try media permissions first
    final status = await Permission.storage.request();
    if (status.isGranted) return true;
    
    // Fall back to manage external storage
    return (await Permission.manageExternalStorage.request()).isGranted;
    
  } else {
    // Android 10 and below
    return (await Permission.storage.request()).isGranted;
  }
}
```

### Contacts

```xml
<uses-permission android:name="android.permission.READ_CONTACTS" />
<uses-permission android:name="android.permission.WRITE_CONTACTS" />
<uses-permission android:name="android.permission.GET_ACCOUNTS" />
```

### Calendar

```xml
<uses-permission android:name="android.permission.READ_CALENDAR" />
<uses-permission android:name="android.permission.WRITE_CALENDAR" />
```

### Phone

```xml
<uses-permission android:name="android.permission.READ_PHONE_STATE" />
<uses-permission android:name="android.permission.READ_PHONE_NUMBERS" />
<uses-permission android:name="android.permission.CALL_PHONE" />
<uses-permission android:name="android.permission.READ_CALL_LOG" />
<uses-permission android:name="android.permission.WRITE_CALL_LOG" />
<uses-permission android:name="android.permission.ADD_VOICEMAIL" />
<uses-permission android:name="android.permission.USE_SIP" />
<uses-permission android:name="android.permission.ANSWER_PHONE_CALLS" />
```

### SMS

```xml
<uses-permission android:name="android.permission.SEND_SMS" />
<uses-permission android:name="android.permission.RECEIVE_SMS" />
<uses-permission android:name="android.permission.READ_SMS" />
<uses-permission android:name="android.permission.RECEIVE_WAP_PUSH" />
<uses-permission android:name="android.permission.RECEIVE_MMS" />
```

### Body Sensors

```xml
<uses-permission android:name="android.permission.BODY_SENSORS" />

<!-- Android 13+: Background body sensors -->
<uses-permission android:name="android.permission.BODY_SENSORS_BACKGROUND" />
```

### Activity Recognition

```xml
<uses-permission android:name="android.permission.ACTIVITY_RECOGNITION" />
```

---

## 3. Special Permissions (Settings Page Required)

These require the user to navigate to settings to grant.

### Notification Permission (Android 13+)

```xml
<uses-permission android:name="android.permission.POST_NOTIFICATIONS" />
```

**Request Pattern:**

```dart
Future<bool> requestNotificationPermission() async {
  if (Platform.isAndroid) {
    final androidInfo = await DeviceInfoPlugin().androidInfo;
    
    if (androidInfo.version.sdkInt >= 33) {
      final status = await Permission.notification.request();
      return status.isGranted;
    }
  }
  
  // Auto-granted on Android 12 and below
  return true;
}
```

### System Alert Window (Overlay)

```xml
<uses-permission android:name="android.permission.SYSTEM_ALERT_WINDOW" />
```

**Request Pattern:**

```dart
Future<bool> requestOverlayPermission() async {
  if (!await Permission.systemAlertWindow.isGranted) {
    // Opens system settings for user to grant
    await Permission.systemAlertWindow.request();
  }
  return Permission.systemAlertWindow.isGranted;
}
```

### Write Settings

```xml
<uses-permission android:name="android.permission.WRITE_SETTINGS" />
```

### Access Notification Policy (Do Not Disturb)

```xml
<uses-permission android:name="android.permission.ACCESS_NOTIFICATION_POLICY" />
```

### Request Install Packages

```xml
<uses-permission android:name="android.permission.REQUEST_INSTALL_PACKAGES" />
```

### Schedule Exact Alarms (Android 12+)

```xml
<uses-permission android:name="android.permission.SCHEDULE_EXACT_ALARM" />

<!-- Android 13+: Alternative that doesn't require user permission -->
<uses-permission android:name="android.permission.USE_EXACT_ALARM" />
```

---

## 4. Bluetooth Permissions (Android 12+)

Android 12 introduced new granular Bluetooth permissions.

```xml
<!-- Discover and pair with nearby devices -->
<uses-permission android:name="android.permission.BLUETOOTH_SCAN"
    android:usesPermissionFlags="neverForLocation" />

<!-- Make device discoverable -->
<uses-permission android:name="android.permission.BLUETOOTH_ADVERTISE" />

<!-- Communicate with paired devices -->
<uses-permission android:name="android.permission.BLUETOOTH_CONNECT" />
```

**Request Pattern:**

```dart
Future<bool> requestBluetoothPermissions() async {
  if (Platform.isAndroid) {
    final androidInfo = await DeviceInfoPlugin().androidInfo;
    
    if (androidInfo.version.sdkInt >= 31) {
      // Android 12+
      final statuses = await [
        Permission.bluetoothScan,
        Permission.bluetoothConnect,
        Permission.bluetoothAdvertise,
      ].request();
      
      return statuses.values.every((s) => s.isGranted);
    } else {
      // Android 11 and below - location is required for BLE scanning
      final location = await Permission.locationWhenInUse.request();
      return location.isGranted;
    }
  }
  return true;
}
```

---

## 5. Foreground Service Types (Android 14+)

Android 14 requires specifying foreground service types.

```xml
<uses-permission android:name="android.permission.FOREGROUND_SERVICE" />

<!-- Specify the foreground service type -->
<uses-permission android:name="android.permission.FOREGROUND_SERVICE_CAMERA" />
<uses-permission android:name="android.permission.FOREGROUND_SERVICE_CONNECTED_DEVICE" />
<uses-permission android:name="android.permission.FOREGROUND_SERVICE_DATA_SYNC" />
<uses-permission android:name="android.permission.FOREGROUND_SERVICE_HEALTH" />
<uses-permission android:name="android.permission.FOREGROUND_SERVICE_LOCATION" />
<uses-permission android:name="android.permission.FOREGROUND_SERVICE_MEDIA_PLAYBACK" />
<uses-permission android:name="android.permission.FOREGROUND_SERVICE_MEDIA_PROJECTION" />
<uses-permission android:name="android.permission.FOREGROUND_SERVICE_MICROPHONE" />
<uses-permission android:name="android.permission.FOREGROUND_SERVICE_PHONE_CALL" />
<uses-permission android:name="android.permission.FOREGROUND_SERVICE_REMOTE_MESSAGING" />
<uses-permission android:name="android.permission.FOREGROUND_SERVICE_SHORT_SERVICE" />
<uses-permission android:name="android.permission.FOREGROUND_SERVICE_SPECIAL_USE" />
<uses-permission android:name="android.permission.FOREGROUND_SERVICE_SYSTEM_EXEMPTED" />
```

**Service Declaration:**

```xml
<service
    android:name=".LocationTrackingService"
    android:foregroundServiceType="location"
    android:exported="false" />

<service
    android:name=".AudioRecordingService"
    android:foregroundServiceType="microphone|mediaPlayback"
    android:exported="false" />
```

---

## 6. Hardware Feature Declarations

Declare hardware requirements for Google Play filtering.

```xml
<!-- Camera -->
<uses-feature android:name="android.hardware.camera" android:required="false" />
<uses-feature android:name="android.hardware.camera.autofocus" android:required="false" />
<uses-feature android:name="android.hardware.camera.flash" android:required="false" />
<uses-feature android:name="android.hardware.camera.front" android:required="false" />

<!-- Location -->
<uses-feature android:name="android.hardware.location" android:required="false" />
<uses-feature android:name="android.hardware.location.gps" android:required="false" />
<uses-feature android:name="android.hardware.location.network" android:required="false" />

<!-- Sensors -->
<uses-feature android:name="android.hardware.sensor.accelerometer" android:required="false" />
<uses-feature android:name="android.hardware.sensor.compass" android:required="false" />
<uses-feature android:name="android.hardware.sensor.gyroscope" android:required="false" />
<uses-feature android:name="android.hardware.sensor.proximity" android:required="false" />
<uses-feature android:name="android.hardware.sensor.barometer" android:required="false" />
<uses-feature android:name="android.hardware.sensor.stepcounter" android:required="false" />
<uses-feature android:name="android.hardware.sensor.heartrate" android:required="false" />

<!-- Connectivity -->
<uses-feature android:name="android.hardware.bluetooth" android:required="false" />
<uses-feature android:name="android.hardware.bluetooth_le" android:required="false" />
<uses-feature android:name="android.hardware.nfc" android:required="false" />
<uses-feature android:name="android.hardware.wifi" android:required="false" />
<uses-feature android:name="android.hardware.telephony" android:required="false" />

<!-- Biometric -->
<uses-feature android:name="android.hardware.fingerprint" android:required="false" />
<uses-feature android:name="android.hardware.biometrics" android:required="false" />

<!-- Display -->
<uses-feature android:name="android.hardware.screen.portrait" android:required="false" />
<uses-feature android:name="android.hardware.screen.landscape" android:required="false" />

<!-- Audio -->
<uses-feature android:name="android.hardware.microphone" android:required="false" />
<uses-feature android:name="android.hardware.audio.output" android:required="false" />
```

---

## 7. Package Visibility (Android 11+)

Android 11+ restricts package visibility. Declare which apps your app needs to interact with.

```xml
<queries>
    <!-- Web browsers -->
    <intent>
        <action android:name="android.intent.action.VIEW" />
        <data android:scheme="https" />
    </intent>
    
    <!-- Email apps -->
    <intent>
        <action android:name="android.intent.action.SENDTO" />
        <data android:scheme="mailto" />
    </intent>
    
    <!-- Phone dialers -->
    <intent>
        <action android:name="android.intent.action.DIAL" />
        <data android:scheme="tel" />
    </intent>
    
    <!-- SMS apps -->
    <intent>
        <action android:name="android.intent.action.SENDTO" />
        <data android:scheme="smsto" />
    </intent>
    
    <!-- File managers / Document providers -->
    <intent>
        <action android:name="android.intent.action.OPEN_DOCUMENT" />
        <data android:mimeType="*/*" />
    </intent>
    
    <!-- Share targets -->
    <intent>
        <action android:name="android.intent.action.SEND" />
        <data android:mimeType="*/*" />
    </intent>
    
    <!-- Specific packages -->
    <package android:name="com.google.android.apps.maps" />
    <package android:name="com.google.android.youtube" />
    
    <!-- Google Play -->
    <intent>
        <action android:name="android.intent.action.VIEW" />
        <data android:scheme="market" />
    </intent>
</queries>
```

---

## 8. Permission Groups Reference

| Permission Group | Permissions |
|-----------------|-------------|
| CALENDAR | READ_CALENDAR, WRITE_CALENDAR |
| CALL_LOG | READ_CALL_LOG, WRITE_CALL_LOG, PROCESS_OUTGOING_CALLS |
| CAMERA | CAMERA |
| CONTACTS | READ_CONTACTS, WRITE_CONTACTS, GET_ACCOUNTS |
| LOCATION | ACCESS_FINE_LOCATION, ACCESS_COARSE_LOCATION, ACCESS_BACKGROUND_LOCATION |
| MICROPHONE | RECORD_AUDIO |
| NEARBY_DEVICES | BLUETOOTH_ADVERTISE, BLUETOOTH_CONNECT, BLUETOOTH_SCAN, NEARBY_WIFI_DEVICES |
| NOTIFICATIONS | POST_NOTIFICATIONS |
| PHONE | READ_PHONE_STATE, READ_PHONE_NUMBERS, CALL_PHONE, READ_CALL_LOG, WRITE_CALL_LOG, ADD_VOICEMAIL, USE_SIP, ANSWER_PHONE_CALLS |
| READ_MEDIA_AURAL | READ_MEDIA_AUDIO |
| READ_MEDIA_VISUAL | READ_MEDIA_IMAGES, READ_MEDIA_VIDEO, READ_MEDIA_VISUAL_USER_SELECTED |
| SENSORS | BODY_SENSORS, BODY_SENSORS_BACKGROUND |
| SMS | SEND_SMS, RECEIVE_SMS, READ_SMS, RECEIVE_WAP_PUSH, RECEIVE_MMS |
| STORAGE | READ_EXTERNAL_STORAGE, WRITE_EXTERNAL_STORAGE |

---

## 9. Best Practices

### 1. Request Permissions Just-In-Time

```dart
// Good: Request when feature is about to be used
Future<void> openCamera() async {
  if (await Permission.camera.request().isGranted) {
    // Open camera
    Navigator.push(context, MaterialPageRoute(builder: (_) => CameraScreen()));
  } else {
    // Show explanation
    showPermissionDeniedDialog();
  }
}

// Bad: Request all permissions at app start
Future<void> main() async {
  await [Permission.camera, Permission.location, Permission.storage].request();
  runApp(MyApp());
}
```

### 2. Show Rationale Before Requesting

```dart
Future<bool> requestLocationWithRationale() async {
  final status = await Permission.location.status;
  
  if (status.isDenied) {
    // Show rationale dialog first
    final shouldRequest = await showDialog<bool>(
      context: context,
      builder: (context) => AlertDialog(
        title: Text('Location Permission'),
        content: Text('We need location access to show nearby stores. Your location is never shared.'),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context, false),
            child: Text('Cancel'),
          ),
          TextButton(
            onPressed: () => Navigator.pop(context, true),
            child: Text('Continue'),
          ),
        ],
      ),
    );
    
    if (shouldRequest == true) {
      return (await Permission.location.request()).isGranted;
    }
    return false;
  }
  
  return status.isGranted;
}
```

### 3. Handle Permanently Denied State

```dart
Future<void> handlePermanentlyDenied(Permission permission, String featureName) async {
  final shouldOpenSettings = await showDialog<bool>(
    context: context,
    builder: (context) => AlertDialog(
      title: Text('Permission Required'),
      content: Text(
        '$featureName requires ${permission.toString()} permission. '
        'Please enable it in Settings.',
      ),
      actions: [
        TextButton(
          onPressed: () => Navigator.pop(context, false),
          child: Text('Cancel'),
        ),
        TextButton(
          onPressed: () => Navigator.pop(context, true),
          child: Text('Open Settings'),
        ),
      ],
    ),
  );
  
  if (shouldOpenSettings == true) {
    await openAppSettings();
  }
}
```

### 4. Use Minimal Permissions

```xml
<!-- Don't request more than needed -->

<!-- Bad: Requesting fine location when coarse is sufficient -->
<uses-permission android:name="android.permission.ACCESS_FINE_LOCATION" />

<!-- Good: Request minimum required -->
<uses-permission android:name="android.permission.ACCESS_COARSE_LOCATION" />
```

### 5. Remove Permissions Added by Libraries

```xml
<!-- Some libraries add permissions you don't need -->
<uses-permission android:name="android.permission.READ_PHONE_STATE"
    tools:node="remove" />

<uses-permission android:name="android.permission.WRITE_EXTERNAL_STORAGE"
    tools:node="remove" />
```

---

## 10. Permission Compatibility Matrix

| Permission | API 21-22 | API 23-28 | API 29 | API 30-32 | API 33+ |
|-----------|-----------|-----------|---------|-----------|---------|
| WRITE_EXTERNAL_STORAGE | Install | Runtime | Runtime (limited) | N/A | N/A |
| READ_EXTERNAL_STORAGE | Install | Runtime | Runtime | Runtime | N/A |
| READ_MEDIA_IMAGES | N/A | N/A | N/A | N/A | Runtime |
| POST_NOTIFICATIONS | N/A | N/A | N/A | N/A | Runtime |
| BLUETOOTH_SCAN | N/A | N/A | N/A | N/A (API 31+) | Runtime |
| ACCESS_BACKGROUND_LOCATION | N/A | N/A | Separate | Separate | Separate |
| SCHEDULE_EXACT_ALARM | N/A | N/A | N/A | N/A (API 31+) | Special |

