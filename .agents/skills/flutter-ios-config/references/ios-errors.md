# Common iOS Build Errors & Solutions

## CocoaPods Errors

### "Unable to find a specification for..."
```bash
cd ios
pod repo update
pod install
```

### "The sandbox is not in sync..."
```bash
cd ios
pod deintegrate
pod setup
pod install
```

### CDN: trunk Repo update failed
```ruby
# In Podfile, add at top:
source 'https://github.com/CocoaPods/Specs.git'
```

## Code Signing Errors

### "No signing certificate iOS Distribution found"
1. Open Xcode > Preferences > Accounts
2. Download Manual Profiles
3. Or create new certificate in Apple Developer Portal

### "Provisioning profile doesn't include signing certificate"
1. Go to Apple Developer Portal
2. Edit the provisioning profile
3. Add your certificate
4. Download and double-click to install

### "The executable was signed with invalid entitlements"
- Check Runner.entitlements matches your App ID capabilities
- Regenerate provisioning profile after capability changes

## Build Errors

### "Undefined symbols for architecture arm64"
```bash
# In Podfile post_install:
config.build_settings['EXCLUDED_ARCHS[sdk=iphonesimulator*]'] = 'arm64'
```

### "Module not found"
```bash
cd ios
rm -rf Pods
rm Podfile.lock
pod install --repo-update
```

### "No such module 'Flutter'"
```bash
flutter clean
flutter pub get
cd ios && pod install
```

## Permission Errors

### "This app has crashed because it attempted to access privacy-sensitive data without a usage description"
- Add the required NSxxxUsageDescription key to Info.plist
- Clean build and reinstall

## Runtime Errors

### App crashes on launch (iOS 12)
- Check minimum deployment target matches in:
  - Podfile (`platform :ios, '12.0'`)
  - Xcode project settings
  - Info.plist MinimumOSVersion

### Push notifications not working
1. Check aps-environment in entitlements
2. Verify APNs certificate in Apple Developer Portal
3. Check bundle ID matches exactly

## Archive/Upload Errors

### "ITMS-90717: Invalid App Store Icon"
- Icon must not have transparency
- Must be exactly 1024x1024 PNG

### "Missing Compliance"
Add to Info.plist:
```xml
<key>ITSAppUsesNonExemptEncryption</key>
<false/>
```

### "Missing Push Notification Entitlement"
- If not using push: Remove from capabilities
- If using push: Add capability in Xcode and regenerate profile
