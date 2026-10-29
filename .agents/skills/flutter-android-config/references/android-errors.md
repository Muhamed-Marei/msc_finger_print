# Common Android Build Errors & Solutions

## Gradle Errors

### "Could not determine the dependencies of task ':app:compileDebugJavaWithJavac'"
```bash
flutter clean
cd android && ./gradlew clean && cd ..
flutter pub get
```

### "Execution failed for task ':app:processDebugResources'"
- Check for invalid characters in resource file names
- Resource names must be lowercase with underscores only

### "Minimum SDK version X cannot be smaller than Y"
Update `android/app/build.gradle`:
```groovy
defaultConfig {
    minSdk 21  // or required version
}
```

### "Could not resolve com.android.tools.build:gradle"
Update `android/build.gradle`:
```groovy
buildscript {
    repositories {
        google()
        mavenCentral()
    }
}
```

## Kotlin/Java Errors

### "Module was compiled with an incompatible version of Kotlin"
Update `android/build.gradle`:
```groovy
buildscript {
    ext.kotlin_version = '1.9.0'  // Match plugin requirements
}
```

### "java.lang.OutOfMemoryError: Java heap space"
In `android/gradle.properties`:
```properties
org.gradle.jvmargs=-Xmx4G -XX:+HeapDumpOnOutOfMemoryError
```

## Signing Errors

### "Keystore was tampered with, or password was incorrect"
- Verify passwords in key.properties match keystore
- Recreate keystore if forgotten

### "INSTALL_PARSE_FAILED_NO_CERTIFICATES"
- APK not signed properly
- Check signingConfigs in build.gradle

## MultiDex Errors

### "Cannot fit requested classes in a single dex file"
In `android/app/build.gradle`:
```groovy
defaultConfig {
    multiDexEnabled true
}

dependencies {
    implementation 'androidx.multidex:multidex:2.0.1'
}
```

## Resource Errors

### "Duplicate resources"
- Check for duplicate file names in res folders
- Clean and rebuild

### "AAPT: error: resource not found"
```bash
flutter clean
flutter pub get
```

## Play Store Upload Errors

### "Version code X has already been used"
- Increment `versionCode` in build.gradle or pubspec.yaml

### "Your app has an APK/AAB that targets Android API level X"
Update targetSdk in build.gradle:
```groovy
defaultConfig {
    targetSdk 34  // Latest required
}
```

### "Your app contains native code, and you've not uploaded debug symbols"
Build with:
```bash
flutter build appbundle --release --obfuscate --split-debug-info=build/symbols
```
Upload symbols folder to Play Console.

## NDK Errors

### "No version of NDK matched"
In `android/app/build.gradle`:
```groovy
android {
    ndkVersion flutter.ndkVersion
}
```
Or install specific NDK version via Android Studio SDK Manager.
