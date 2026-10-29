---
name: flutter-security
description: |
  Security Expert - Encryption, secure communication, authentication, data protection.
  TRIGGERS: security, encryption, SSL, certificate, authentication, secure, token, JWT, OAuth
---

# Flutter Security Expert

## Secure Storage
```dart
import 'package:flutter_secure_storage/flutter_secure_storage.dart';

final secureStorage = FlutterSecureStorage(
  aOptions: AndroidOptions(
    encryptedSharedPreferences: true,
    keyCipherAlgorithm: KeyCipherAlgorithm.RSA_ECB_PKCS1Padding,
    storageCipherAlgorithm: StorageCipherAlgorithm.AES_GCM_NoPadding,
  ),
  iOptions: IOSOptions(
    accessibility: KeychainAccessibility.first_unlock_this_device,
  ),
);

// Store tokens securely
await secureStorage.write(key: 'access_token', value: token);
await secureStorage.write(key: 'refresh_token', value: refreshToken);
```

## SSL Pinning
```dart
import 'package:dio/dio.dart';
import 'package:dio/io.dart';
import 'dart:io';

final dio = Dio();

(dio.httpClientAdapter as IOHttpClientAdapter).createHttpClient = () {
  final client = HttpClient();
  client.badCertificateCallback = (cert, host, port) {
    // Compare certificate fingerprint
    final fingerprint = sha256.convert(cert.der).toString();
    return fingerprint == 'YOUR_CERTIFICATE_FINGERPRINT';
  };
  return client;
};
```

## Authentication Patterns

### JWT Token Management
```dart
class AuthManager {
  final _secureStorage = FlutterSecureStorage();
  final _dio = Dio();

  Future<void> saveTokens(String access, String refresh) async {
    await _secureStorage.write(key: 'access_token', value: access);
    await _secureStorage.write(key: 'refresh_token', value: refresh);
  }

  Future<String?> getAccessToken() async {
    final token = await _secureStorage.read(key: 'access_token');
    if (token != null && _isTokenExpired(token)) {
      return await _refreshToken();
    }
    return token;
  }

  bool _isTokenExpired(String token) {
    final parts = token.split('.');
    if (parts.length != 3) return true;
    final payload = json.decode(
      utf8.decode(base64Url.decode(base64Url.normalize(parts[1]))),
    );
    final exp = DateTime.fromMillisecondsSinceEpoch(payload['exp'] * 1000);
    return DateTime.now().isAfter(exp);
  }

  Future<String?> _refreshToken() async {
    final refresh = await _secureStorage.read(key: 'refresh_token');
    if (refresh == null) return null;

    try {
      final response = await _dio.post('/auth/refresh', data: {
        'refresh_token': refresh,
      });
      final newAccess = response.data['access_token'];
      await _secureStorage.write(key: 'access_token', value: newAccess);
      return newAccess;
    } catch (e) {
      await logout();
      return null;
    }
  }

  Future<void> logout() async {
    await _secureStorage.deleteAll();
  }
}
```

### Biometric Authentication
```dart
import 'package:local_auth/local_auth.dart';

class BiometricAuth {
  final _localAuth = LocalAuthentication();

  Future<bool> canAuthenticate() async {
    final canCheck = await _localAuth.canCheckBiometrics;
    final isSupported = await _localAuth.isDeviceSupported();
    return canCheck && isSupported;
  }

  Future<bool> authenticate() async {
    try {
      return await _localAuth.authenticate(
        localizedReason: 'Authenticate to access the app',
        options: AuthenticationOptions(
          stickyAuth: true,
          biometricOnly: false, // Allow PIN/pattern fallback
        ),
      );
    } catch (e) {
      return false;
    }
  }
}
```

## Data Encryption
```dart
import 'package:encrypt/encrypt.dart';

class EncryptionService {
  final _key = Key.fromSecureRandom(32);
  final _iv = IV.fromSecureRandom(16);

  String encrypt(String plainText) {
    final encrypter = Encrypter(AES(_key, mode: AESMode.cbc));
    return encrypter.encrypt(plainText, iv: _iv).base64;
  }

  String decrypt(String encrypted) {
    final encrypter = Encrypter(AES(_key, mode: AESMode.cbc));
    return encrypter.decrypt64(encrypted, iv: _iv);
  }
}
```

## Network Security
```dart
// Dio interceptor for auth headers
class AuthInterceptor extends Interceptor {
  final AuthManager _authManager;

  @override
  Future<void> onRequest(options, handler) async {
    final token = await _authManager.getAccessToken();
    if (token != null) {
      options.headers['Authorization'] = 'Bearer $token';
    }
    handler.next(options);
  }

  @override
  void onError(error, handler) {
    if (error.response?.statusCode == 401) {
      // Token expired, redirect to login
      _authManager.logout();
    }
    handler.next(error);
  }
}
```

## Security Checklist

| Item | Check |
|------|-------|
| Sensitive data in secure storage | ☐ |
| SSL pinning enabled | ☐ |
| Tokens expire & refresh | ☐ |
| No sensitive data in logs | ☐ |
| Biometric option available | ☐ |
| Root/jailbreak detection | ☐ |
| Code obfuscation enabled | ☐ |
| ProGuard rules configured | ☐ |

## Build Security
```bash
# Obfuscate Dart code
flutter build apk --obfuscate --split-debug-info=build/symbols

# Android ProGuard
-keep class io.flutter.** { *; }
-keep class your.package.** { *; }
```

## Packages
```yaml
dependencies:
  flutter_secure_storage: ^9.0.0
  local_auth: ^2.1.0
  encrypt: ^5.0.1
  crypto: ^3.0.3
```
