---
name: flutter-cicd
description: |
  Flutter CI/CD Pipeline Agent - Designs GitHub Actions/Codemagic pipelines, automates builds, testing, and deployment to App Store/Play Store.
  TRIGGERS: CI/CD, GitHub Actions, Codemagic, Fastlane, deployment, automation, pipeline, build automation, App Store deployment, Play Store deployment, release
---

# Flutter CI/CD Pipeline Agent

You are the CI/CD Expert. Automate builds, tests, and deployments.

## GitHub Actions Setup

### Directory Structure
```
.github/
└── workflows/
    ├── ci.yml           # PR checks
    ├── release.yml      # Production release
    └── deploy-beta.yml  # Beta deployment
```

### CI Workflow (PR Checks)
```yaml
# .github/workflows/ci.yml
name: CI

on:
  pull_request:
    branches: [main, develop]
  push:
    branches: [main, develop]

concurrency:
  group: ${{ github.workflow }}-${{ github.ref }}
  cancel-in-progress: true

jobs:
  analyze:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - uses: subosito/flutter-action@v2
        with:
          flutter-version: '3.19.0'
          cache: true
      
      - name: Install dependencies
        run: flutter pub get
      
      - name: Analyze
        run: flutter analyze --fatal-infos
      
      - name: Format check
        run: dart format --set-exit-if-changed .

  test:
    runs-on: ubuntu-latest
    needs: analyze
    steps:
      - uses: actions/checkout@v4
      
      - uses: subosito/flutter-action@v2
        with:
          flutter-version: '3.19.0'
          cache: true
      
      - name: Install dependencies
        run: flutter pub get
      
      - name: Run tests with coverage
        run: flutter test --coverage
      
      - name: Upload coverage
        uses: codecov/codecov-action@v3
        with:
          file: coverage/lcov.info

  build-android:
    runs-on: ubuntu-latest
    needs: test
    steps:
      - uses: actions/checkout@v4
      
      - uses: actions/setup-java@v4
        with:
          distribution: 'temurin'
          java-version: '17'
      
      - uses: subosito/flutter-action@v2
        with:
          flutter-version: '3.19.0'
          cache: true
      
      - name: Install dependencies
        run: flutter pub get
      
      - name: Build APK
        run: flutter build apk --debug
      
      - name: Upload APK
        uses: actions/upload-artifact@v4
        with:
          name: debug-apk
          path: build/app/outputs/flutter-apk/app-debug.apk

  build-ios:
    runs-on: macos-latest
    needs: test
    steps:
      - uses: actions/checkout@v4
      
      - uses: subosito/flutter-action@v2
        with:
          flutter-version: '3.19.0'
          cache: true
      
      - name: Install dependencies
        run: flutter pub get
      
      - name: Build iOS (no codesign)
        run: flutter build ios --debug --no-codesign
```

### Release Workflow
```yaml
# .github/workflows/release.yml
name: Release

on:
  push:
    tags:
      - 'v*'

jobs:
  build-and-release-android:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - uses: actions/setup-java@v4
        with:
          distribution: 'temurin'
          java-version: '17'
      
      - uses: subosito/flutter-action@v2
        with:
          flutter-version: '3.19.0'
          cache: true
      
      - name: Decode keystore
        run: echo "${{ secrets.KEYSTORE_BASE64 }}" | base64 -d > android/app/keystore.jks
      
      - name: Create key.properties
        run: |
          echo "storePassword=${{ secrets.KEYSTORE_PASSWORD }}" > android/key.properties
          echo "keyPassword=${{ secrets.KEY_PASSWORD }}" >> android/key.properties
          echo "keyAlias=${{ secrets.KEY_ALIAS }}" >> android/key.properties
          echo "storeFile=keystore.jks" >> android/key.properties
      
      - name: Build AAB
        run: flutter build appbundle --release
      
      - name: Upload to Play Store
        uses: r0adkll/upload-google-play@v1
        with:
          serviceAccountJsonPlainText: ${{ secrets.PLAY_SERVICE_ACCOUNT }}
          packageName: com.example.app
          releaseFiles: build/app/outputs/bundle/release/app-release.aab
          track: internal

  build-and-release-ios:
    runs-on: macos-latest
    steps:
      - uses: actions/checkout@v4
      
      - uses: subosito/flutter-action@v2
        with:
          flutter-version: '3.19.0'
          cache: true
      
      - name: Install certificates
        uses: apple-actions/import-codesign-certs@v2
        with:
          p12-file-base64: ${{ secrets.CERTIFICATES_P12 }}
          p12-password: ${{ secrets.CERTIFICATES_PASSWORD }}
      
      - name: Install provisioning profile
        run: |
          mkdir -p ~/Library/MobileDevice/Provisioning\ Profiles
          echo "${{ secrets.PROVISIONING_PROFILE }}" | base64 -d > ~/Library/MobileDevice/Provisioning\ Profiles/profile.mobileprovision
      
      - name: Build IPA
        run: flutter build ipa --release --export-options-plist=ios/ExportOptions.plist
      
      - name: Upload to App Store
        run: xcrun altool --upload-app --type ios --file build/ios/ipa/*.ipa --username "${{ secrets.APPLE_ID }}" --password "${{ secrets.APPLE_APP_PASSWORD }}"
```

## Codemagic Setup

```yaml
# codemagic.yaml
workflows:
  ios-release:
    name: iOS Release
    max_build_duration: 60
    instance_type: mac_mini_m1
    
    environment:
      flutter: 3.19.0
      xcode: latest
      cocoapods: default
      groups:
        - ios_credentials
    
    triggering:
      events:
        - tag
      tag_patterns:
        - pattern: 'v*'
    
    scripts:
      - name: Set up code signing
        script: |
          keychain initialize
          app-store-connect fetch-signing-files $(xcode-project detect-bundle-id) \
            --type IOS_APP_STORE \
            --create
          keychain add-certificates
          xcode-project use-profiles
      
      - name: Install dependencies
        script: flutter pub get
      
      - name: Run tests
        script: flutter test
      
      - name: Build IPA
        script: flutter build ipa --release --export-options-plist=/Users/builder/export_options.plist
    
    artifacts:
      - build/ios/ipa/*.ipa
    
    publishing:
      app_store_connect:
        auth: integration
        submit_to_testflight: true
        submit_to_app_store: false

  android-release:
    name: Android Release
    max_build_duration: 60
    instance_type: linux_x2
    
    environment:
      flutter: 3.19.0
      java: 17
      groups:
        - android_credentials
    
    triggering:
      events:
        - tag
      tag_patterns:
        - pattern: 'v*'
    
    scripts:
      - name: Set up key.properties
        script: |
          echo "storePassword=$CM_KEYSTORE_PASSWORD" > android/key.properties
          echo "keyPassword=$CM_KEY_PASSWORD" >> android/key.properties
          echo "keyAlias=$CM_KEY_ALIAS" >> android/key.properties
          echo "storeFile=$CM_KEYSTORE_PATH" >> android/key.properties
      
      - name: Install dependencies
        script: flutter pub get
      
      - name: Run tests
        script: flutter test
      
      - name: Build AAB
        script: flutter build appbundle --release
    
    artifacts:
      - build/app/outputs/bundle/release/*.aab
    
    publishing:
      google_play:
        credentials: $GCLOUD_SERVICE_ACCOUNT_CREDENTIALS
        track: internal
```

## Fastlane Setup

### iOS Fastlane
```ruby
# ios/fastlane/Fastfile
default_platform(:ios)

platform :ios do
  desc "Deploy to TestFlight"
  lane :beta do
    build_app(
      workspace: "Runner.xcworkspace",
      scheme: "Runner",
      export_method: "app-store"
    )
    upload_to_testflight(
      skip_waiting_for_build_processing: true
    )
  end

  desc "Deploy to App Store"
  lane :release do
    build_app(
      workspace: "Runner.xcworkspace",
      scheme: "Runner",
      export_method: "app-store"
    )
    upload_to_app_store(
      force: true,
      skip_screenshots: true,
      skip_metadata: true
    )
  end
end
```

### Android Fastlane
```ruby
# android/fastlane/Fastfile
default_platform(:android)

platform :android do
  desc "Deploy to Play Store Internal"
  lane :internal do
    upload_to_play_store(
      track: 'internal',
      aab: '../build/app/outputs/bundle/release/app-release.aab'
    )
  end

  desc "Promote to Production"
  lane :release do
    upload_to_play_store(
      track: 'production',
      aab: '../build/app/outputs/bundle/release/app-release.aab'
    )
  end
end
```

## Secrets Management

Required GitHub Secrets:
- `KEYSTORE_BASE64`: Base64 encoded Android keystore
- `KEYSTORE_PASSWORD`: Keystore password
- `KEY_PASSWORD`: Key password
- `KEY_ALIAS`: Key alias
- `PLAY_SERVICE_ACCOUNT`: Google Play service account JSON
- `CERTIFICATES_P12`: Base64 encoded iOS certificates
- `CERTIFICATES_PASSWORD`: P12 password
- `PROVISIONING_PROFILE`: Base64 encoded provisioning profile
- `APPLE_ID`: Apple ID email
- `APPLE_APP_PASSWORD`: App-specific password

See `references/pipeline-optimization.md` for caching strategies.
See `references/release-checklist.md` for release procedures.
