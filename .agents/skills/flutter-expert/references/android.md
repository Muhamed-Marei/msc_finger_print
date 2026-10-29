# Android Quick Reference

## build.gradle (app)
```groovy
android {
    compileSdk 34
    defaultConfig {
        minSdk 21
        targetSdk 34
        multiDexEnabled true
    }
    buildTypes {
        release {
            minifyEnabled true
            shrinkResources true
            proguardFiles getDefaultProguardFile('proguard-android.txt'), 'proguard-rules.pro'
        }
    }
}
```

## Permissions (AndroidManifest.xml)
```xml
<uses-permission android:name="android.permission.INTERNET"/>
<uses-permission android:name="android.permission.CAMERA"/>
<uses-permission android:name="android.permission.ACCESS_FINE_LOCATION"/>
```

## Build
```bash
flutter build apk --release
flutter build appbundle --release
```

## Signing (key.properties)
```properties
storePassword=xxx
keyPassword=xxx
keyAlias=upload
storeFile=keystore.jks
```
