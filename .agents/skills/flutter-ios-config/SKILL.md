---
name: flutter-ios-config
description: |
  Flutter iOS Configuration Agent - Handles iOS-specific setup, permissions, code signing, App Store deployment, and error resolution.
  TRIGGERS: iOS config, Info.plist, Podfile, iOS permissions, code signing, provisioning profiles, App Store, TestFlight, CocoaPods, iOS build error, Xcode, iOS version, privacy manifest
---

# Flutter iOS Configuration Agent

You are the iOS Configuration Specialist. Handle all iOS-specific setup and troubleshooting.

## Project Structure

```
ios/
├── Runner/
│   ├── Info.plist              # App configuration
│   ├── Runner.entitlements     # Capabilities
│   └── AppDelegate.swift       # Native entry point
├── Podfile                     # CocoaPods dependencies
├── Runner.xcworkspace          # Open this in Xcode
└── Runner.xcodeproj/
```

## Info.plist Configuration

### Minimum Required Keys

```xml
<key>CFBundleDisplayName</key>
<string>$(PRODUCT_NAME)</string>
<key>CFBundleIdentifier</key>
<string>$(PRODUCT_BUNDLE_IDENTIFIER)</string>
<key>CFBundleVersion</key>
<string>$(FLUTTER_BUILD_NUMBER)</string>
<key>CFBundleShortVersionString</key>
<string>$(FLUTTER_BUILD_NAME)</string>
<key>LSRequiresIPhoneOS</key>
<true/>
<key>UILaunchStoryboardName</key>
<string>LaunchScreen</string>
<key>UISupportedInterfaceOrientations</key>
<array>
    <string>UIInterfaceOrientationPortrait</string>
</array>
```

### iOS Version Support

```xml
<!-- Minimum iOS 12 -->
<key>MinimumOSVersion</key>
<string>12.0</string>
```

In Podfile:
```ruby
platform :ios, '12.0'
```

## Permissions Setup

Add to Info.plist with user-facing descriptions:

```xml
<!-- Camera -->
<key>NSCameraUsageDescription</key>
<string>We need camera access to take photos</string>

<!-- Photo Library -->
<key>NSPhotoLibraryUsageDescription</key>
<string>We need access to save photos</string>
<key>NSPhotoLibraryAddUsageDescription</key>
<string>We need access to save photos to your library</string>

<!-- Location -->
<key>NSLocationWhenInUseUsageDescription</key>
<string>We need your location to show nearby places</string>
<key>NSLocationAlwaysAndWhenInUseUsageDescription</key>
<string>We need your location for navigation</string>

<!-- Microphone -->
<key>NSMicrophoneUsageDescription</key>
<string>We need microphone access for voice messages</string>

<!-- Contacts -->
<key>NSContactsUsageDescription</key>
<string>We need access to find your friends</string>

<!-- Bluetooth -->
<key>NSBluetoothAlwaysUsageDescription</key>
<string>We need Bluetooth for device connectivity</string>

<!-- Face ID -->
<key>NSFaceIDUsageDescription</key>
<string>Use Face ID for secure authentication</string>
```

## Podfile Configuration

```ruby
platform :ios, '12.0'

# CocoaPods analytics
ENV['COCOAPODS_DISABLE_STATS'] = 'true'

project 'Runner', {
  'Debug' => :debug,
  'Profile' => :release,
  'Release' => :release,
}

def flutter_root
  generated_xcode_build_settings_path = File.expand_path(File.join('..', 'Flutter', 'Generated.xcconfig'), __FILE__)
  unless File.exist?(generated_xcode_build_settings_path)
    raise "#{generated_xcode_build_settings_path} must exist."
  end
  File.foreach(generated_xcode_build_settings_path) do |line|
    matches = line.match(/FLUTTER_ROOT\=(.*)/)
    return matches[1].strip if matches
  end
  raise "FLUTTER_ROOT not found"
end

require File.expand_path(File.join('packages', 'flutter_tools', 'bin', 'podhelper'), flutter_root)

flutter_ios_podfile_setup

target 'Runner' do
  use_frameworks!
  use_modular_headers!

  flutter_install_all_ios_pods File.dirname(File.realpath(__FILE__))
  
  # Add custom pods here
  # pod 'Firebase/Analytics'
end

post_install do |installer|
  installer.pods_project.targets.each do |target|
    flutter_additional_ios_build_settings(target)
    target.build_configurations.each do |config|
      config.build_settings['IPHONEOS_DEPLOYMENT_TARGET'] = '12.0'
    end
  end
end
```

## Code Signing Setup

1. **Development**: Automatic signing in Xcode
2. **Distribution**: Manual signing with provisioning profiles

### Xcode Settings
- Team: Select your Apple Developer Team
- Bundle Identifier: com.yourcompany.appname
- Signing Certificate: iPhone Distribution (for release)
- Provisioning Profile: App Store or Ad Hoc

### Entitlements (Runner.entitlements)
```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>aps-environment</key>
    <string>development</string>
    <key>com.apple.developer.associated-domains</key>
    <array>
        <string>applinks:yourdomain.com</string>
    </array>
</dict>
</plist>
```

## Privacy Manifest (iOS 17+)

Create `ios/Runner/PrivacyInfo.xcprivacy`:
```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>NSPrivacyAccessedAPITypes</key>
    <array>
        <dict>
            <key>NSPrivacyAccessedAPIType</key>
            <string>NSPrivacyAccessedAPICategoryUserDefaults</string>
            <key>NSPrivacyAccessedAPITypeReasons</key>
            <array>
                <string>CA92.1</string>
            </array>
        </dict>
    </array>
    <key>NSPrivacyCollectedDataTypes</key>
    <array/>
    <key>NSPrivacyTracking</key>
    <false/>
</dict>
</plist>
```

## Build Commands

```bash
# Clean build
flutter clean && cd ios && pod deintegrate && pod install && cd ..

# Build for release
flutter build ios --release

# Build IPA for App Store
flutter build ipa --release

# Build for specific device
flutter build ios --release --target-platform=ios
```

See `references/ios-errors.md` for common error solutions.
See `references/ios-permissions.md` for all permission configurations.
