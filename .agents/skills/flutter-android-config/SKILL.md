---
name: flutter-android-config
description: |
  Flutter Android Configuration Agent - Handles Android-specific setup, permissions, Gradle configuration, Play Store deployment, and error resolution.
  TRIGGERS: Android config, AndroidManifest.xml, build.gradle, Android permissions, ProGuard, R8, keystore, Play Store, APK, AAB, Gradle, Android build error, API level, targetSdk
---

# Flutter Android Configuration Agent

You are the Android Configuration Specialist. Handle all Android-specific setup and troubleshooting.

## Project Structure

```
android/
├── app/
│   ├── build.gradle            # App-level config
│   ├── proguard-rules.pro      # Obfuscation rules
│   └── src/
│       └── main/
│           ├── AndroidManifest.xml
│           ├── kotlin/          # Native code
│           └── res/             # Resources
├── build.gradle                # Project-level config
├── gradle.properties           # Build properties
└── key.properties              # Signing keys (gitignore!)
```

## build.gradle (app level)

```groovy
plugins {
    id "com.android.application"
    id "kotlin-android"
    id "dev.flutter.flutter-gradle-plugin"
}

def localProperties = new Properties()
def localPropertiesFile = rootProject.file('local.properties')
if (localPropertiesFile.exists()) {
    localPropertiesFile.withReader('UTF-8') { reader ->
        localProperties.load(reader)
    }
}

def flutterVersionCode = localProperties.getProperty('flutter.versionCode')
if (flutterVersionCode == null) {
    flutterVersionCode = '1'
}

def flutterVersionName = localProperties.getProperty('flutter.versionName')
if (flutterVersionName == null) {
    flutterVersionName = '1.0'
}

// Load keystore properties
def keystoreProperties = new Properties()
def keystorePropertiesFile = rootProject.file('key.properties')
if (keystorePropertiesFile.exists()) {
    keystoreProperties.load(new FileInputStream(keystorePropertiesFile))
}

android {
    namespace "com.example.app"
    compileSdk 34
    ndkVersion flutter.ndkVersion

    compileOptions {
        sourceCompatibility JavaVersion.VERSION_1_8
        targetCompatibility JavaVersion.VERSION_1_8
    }

    kotlinOptions {
        jvmTarget = '1.8'
    }

    defaultConfig {
        applicationId "com.example.app"
        minSdk 21
        targetSdk 34
        versionCode flutterVersionCode.toInteger()
        versionName flutterVersionName
        multiDexEnabled true
    }

    signingConfigs {
        release {
            keyAlias keystoreProperties['keyAlias']
            keyPassword keystoreProperties['keyPassword']
            storeFile keystoreProperties['storeFile'] ? file(keystoreProperties['storeFile']) : null
            storePassword keystoreProperties['storePassword']
        }
    }

    buildTypes {
        release {
            signingConfig signingConfigs.release
            minifyEnabled true
            shrinkResources true
            proguardFiles getDefaultProguardFile('proguard-android-optimize.txt'), 'proguard-rules.pro'
        }
        debug {
            signingConfig signingConfigs.debug
        }
    }
    
    // Flavor configuration (optional)
    flavorDimensions "environment"
    productFlavors {
        dev {
            dimension "environment"
            applicationIdSuffix ".dev"
            versionNameSuffix "-dev"
        }
        prod {
            dimension "environment"
        }
    }
}

flutter {
    source '../..'
}

dependencies {
    implementation "org.jetbrains.kotlin:kotlin-stdlib:$kotlin_version"
    implementation 'androidx.multidex:multidex:2.0.1'
}
```

## AndroidManifest.xml

```xml
<manifest xmlns:android="http://schemas.android.com/apk/res/android">
    
    <!-- Permissions -->
    <uses-permission android:name="android.permission.INTERNET"/>
    <uses-permission android:name="android.permission.ACCESS_NETWORK_STATE"/>
    
    <!-- Camera -->
    <uses-permission android:name="android.permission.CAMERA"/>
    <uses-feature android:name="android.hardware.camera" android:required="false"/>
    
    <!-- Location -->
    <uses-permission android:name="android.permission.ACCESS_FINE_LOCATION"/>
    <uses-permission android:name="android.permission.ACCESS_COARSE_LOCATION"/>
    
    <!-- Storage (Android 12 and below) -->
    <uses-permission android:name="android.permission.READ_EXTERNAL_STORAGE" 
                     android:maxSdkVersion="32"/>
    <uses-permission android:name="android.permission.WRITE_EXTERNAL_STORAGE" 
                     android:maxSdkVersion="32"/>
    
    <!-- Photos (Android 13+) -->
    <uses-permission android:name="android.permission.READ_MEDIA_IMAGES"/>
    <uses-permission android:name="android.permission.READ_MEDIA_VIDEO"/>
    
    <application
        android:label="@string/app_name"
        android:name="${applicationName}"
        android:icon="@mipmap/ic_launcher"
        android:usesCleartextTraffic="false"
        android:networkSecurityConfig="@xml/network_security_config">
        
        <activity
            android:name=".MainActivity"
            android:exported="true"
            android:launchMode="singleTop"
            android:theme="@style/LaunchTheme"
            android:configChanges="orientation|keyboardHidden|keyboard|screenSize|smallestScreenSize|locale|layoutDirection|fontScale|screenLayout|density|uiMode"
            android:hardwareAccelerated="true"
            android:windowSoftInputMode="adjustResize">
            
            <meta-data
                android:name="io.flutter.embedding.android.NormalTheme"
                android:resource="@style/NormalTheme"/>
            
            <intent-filter>
                <action android:name="android.intent.action.MAIN"/>
                <category android:name="android.intent.category.LAUNCHER"/>
            </intent-filter>
            
            <!-- Deep linking -->
            <intent-filter android:autoVerify="true">
                <action android:name="android.intent.action.VIEW"/>
                <category android:name="android.intent.category.DEFAULT"/>
                <category android:name="android.intent.category.BROWSABLE"/>
                <data android:scheme="https" android:host="yourdomain.com"/>
            </intent-filter>
        </activity>
        
        <!-- FCM -->
        <meta-data
            android:name="com.google.firebase.messaging.default_notification_channel_id"
            android:value="high_importance_channel"/>
    </application>
</manifest>
```

## ProGuard Rules

```proguard
# proguard-rules.pro

# Flutter
-keep class io.flutter.** { *; }
-keep class io.flutter.plugins.** { *; }

# Firebase
-keep class com.google.firebase.** { *; }
-keep class com.google.android.gms.** { *; }

# Retrofit/OkHttp (if used)
-dontwarn okhttp3.**
-dontwarn okio.**
-keep class retrofit2.** { *; }

# Gson/Serialization
-keepattributes Signature
-keepattributes *Annotation*
-keep class * extends com.google.gson.TypeAdapter
-keep class * implements com.google.gson.TypeAdapterFactory

# Prevent stripping Parcelable
-keep class * implements android.os.Parcelable {
    public static final ** CREATOR;
}
```

## Signing Setup

### Create Keystore
```bash
keytool -genkey -v -keystore ~/upload-keystore.jks -keyalg RSA -keysize 2048 -validity 10000 -alias upload
```

### key.properties (DO NOT COMMIT)
```properties
storePassword=yourpassword
keyPassword=yourpassword
keyAlias=upload
storeFile=/path/to/upload-keystore.jks
```

## Build Commands

```bash
# Build debug APK
flutter build apk --debug

# Build release APK
flutter build apk --release

# Build AAB for Play Store
flutter build appbundle --release

# Build with flavor
flutter build apk --flavor prod --release
flutter build appbundle --flavor prod --release

# Analyze APK size
flutter build apk --analyze-size
```

See `references/android-errors.md` for common error solutions.
See `references/android-permissions.md` for runtime permission handling.
