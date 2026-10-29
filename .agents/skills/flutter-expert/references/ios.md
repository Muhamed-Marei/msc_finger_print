# iOS Quick Reference

## Permissions (Info.plist)
```xml
<key>NSCameraUsageDescription</key><string>Camera access</string>
<key>NSPhotoLibraryUsageDescription</key><string>Photo access</string>
<key>NSLocationWhenInUseUsageDescription</key><string>Location access</string>
<key>NSMicrophoneUsageDescription</key><string>Microphone access</string>
```

## Podfile
```ruby
platform :ios, '14.0'
post_install do |installer|
  installer.pods_project.targets.each do |target|
    target.build_configurations.each do |config|
      config.build_settings['IPHONEOS_DEPLOYMENT_TARGET'] = '14.0'
    end
  end
end
```

## Build
```bash
flutter build ios --release
flutter build ipa --release
```

## Signing
1. Xcode > Signing & Capabilities
2. Select Team
3. Enable Automatic signing OR set provisioning profile
