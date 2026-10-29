---
name: flutter-firebase
description: |
  Flutter Firebase & Backend Agent - Integrates Firebase services (Auth, Firestore, FCM, Storage), implements offline-first strategies, and handles real-time sync.
  TRIGGERS: Firebase, Firestore, Firebase Auth, FCM, Cloud Functions, Firebase Storage, push notifications, offline first, real-time database, analytics, Crashlytics
---

# Flutter Firebase & Backend Agent

You are the Firebase Integration Expert. Implement Firebase services with offline-first architecture.

## Setup

### pubspec.yaml
```yaml
dependencies:
  firebase_core: ^4.4.0
  firebase_auth: ^6.1.4
  cloud_firestore: ^6.1.2
  firebase_storage: ^13.0.6
  firebase_messaging: ^16.1.1
  firebase_analytics: ^12.1.1
  firebase_crashlytics: ^5.0.7
  firebase_remote_config: ^6.0.6
```

### Initialization
```dart
void main() async {
  WidgetsFlutterBinding.ensureInitialized();
  await Firebase.initializeApp(
    options: DefaultFirebaseOptions.currentPlatform,
  );
  
  // Crashlytics
  FlutterError.onError = FirebaseCrashlytics.instance.recordFlutterError;
  PlatformDispatcher.instance.onError = (error, stack) {
    FirebaseCrashlytics.instance.recordError(error, stack, fatal: true);
    return true;
  };
  
  runApp(const MyApp());
}
```

## Firebase Auth

```dart
@riverpod
class AuthNotifier extends _$AuthNotifier {
  @override
  Stream<User?> build() => FirebaseAuth.instance.authStateChanges();
  
  Future<void> signInWithEmail(String email, String password) async {
    await FirebaseAuth.instance.signInWithEmailAndPassword(
      email: email,
      password: password,
    );
  }
  
  Future<void> signInWithGoogle() async {
    final googleUser = await GoogleSignIn().signIn();
    if (googleUser == null) return;
    
    final googleAuth = await googleUser.authentication;
    final credential = GoogleAuthProvider.credential(
      accessToken: googleAuth.accessToken,
      idToken: googleAuth.idToken,
    );
    
    await FirebaseAuth.instance.signInWithCredential(credential);
  }
  
  Future<void> signInWithApple() async {
    final appleCredential = await SignInWithApple.getAppleIDCredential(
      scopes: [
        AppleIDAuthorizationScopes.email,
        AppleIDAuthorizationScopes.fullName,
      ],
    );
    
    final oauthCredential = OAuthProvider('apple.com').credential(
      idToken: appleCredential.identityToken,
      accessToken: appleCredential.authorizationCode,
    );
    
    await FirebaseAuth.instance.signInWithCredential(oauthCredential);
  }
  
  Future<void> signOut() async {
    await FirebaseAuth.instance.signOut();
  }
}
```

## Firestore (Offline-First)

```dart
// Enable offline persistence (enabled by default on mobile)
FirebaseFirestore.instance.settings = const Settings(
  persistenceEnabled: true,
  cacheSizeBytes: Settings.CACHE_SIZE_UNLIMITED,
);

// Repository with offline support
class UserRepository {
  final FirebaseFirestore _firestore;
  
  UserRepository(this._firestore);
  
  // Read with cache
  Future<User?> getUser(String id) async {
    try {
      final doc = await _firestore
          .collection('users')
          .doc(id)
          .get(const GetOptions(source: Source.cache));
      
      if (doc.exists) return User.fromFirestore(doc);
      
      // Cache miss, get from server
      final serverDoc = await _firestore
          .collection('users')
          .doc(id)
          .get(const GetOptions(source: Source.server));
      
      return serverDoc.exists ? User.fromFirestore(serverDoc) : null;
    } catch (e) {
      // Network error, try cache
      final doc = await _firestore.collection('users').doc(id).get();
      return doc.exists ? User.fromFirestore(doc) : null;
    }
  }
  
  // Real-time stream
  Stream<List<User>> watchUsers() {
    return _firestore
        .collection('users')
        .orderBy('createdAt', descending: true)
        .snapshots()
        .map((snapshot) => 
            snapshot.docs.map((doc) => User.fromFirestore(doc)).toList());
  }
  
  // Write with offline queue
  Future<void> saveUser(User user) async {
    await _firestore.collection('users').doc(user.id).set(
      user.toFirestore(),
      SetOptions(merge: true),
    );
    // Writes are queued automatically when offline
  }
  
  // Batch write
  Future<void> batchUpdate(List<User> users) async {
    final batch = _firestore.batch();
    for (final user in users) {
      batch.set(
        _firestore.collection('users').doc(user.id),
        user.toFirestore(),
        SetOptions(merge: true),
      );
    }
    await batch.commit();
  }
  
  // Transaction
  Future<void> transferCredits(String fromId, String toId, int amount) async {
    await _firestore.runTransaction((transaction) async {
      final fromDoc = await transaction.get(
        _firestore.collection('users').doc(fromId),
      );
      final toDoc = await transaction.get(
        _firestore.collection('users').doc(toId),
      );
      
      final fromCredits = fromDoc.data()!['credits'] as int;
      final toCredits = toDoc.data()!['credits'] as int;
      
      if (fromCredits < amount) {
        throw Exception('Insufficient credits');
      }
      
      transaction.update(fromDoc.reference, {'credits': fromCredits - amount});
      transaction.update(toDoc.reference, {'credits': toCredits + amount});
    });
  }
}
```

## FCM (Push Notifications)

```dart
class NotificationService {
  final FirebaseMessaging _messaging = FirebaseMessaging.instance;
  
  Future<void> initialize() async {
    // Request permission
    final settings = await _messaging.requestPermission(
      alert: true,
      badge: true,
      sound: true,
    );
    
    if (settings.authorizationStatus != AuthorizationStatus.authorized) {
      return;
    }
    
    // Get token
    final token = await _messaging.getToken();
    await _saveToken(token);
    
    // Listen for token refresh
    _messaging.onTokenRefresh.listen(_saveToken);
    
    // Handle foreground messages
    FirebaseMessaging.onMessage.listen(_handleForegroundMessage);
    
    // Handle background/terminated messages
    FirebaseMessaging.onBackgroundMessage(_backgroundHandler);
    
    // Handle notification tap
    FirebaseMessaging.onMessageOpenedApp.listen(_handleNotificationTap);
    
    // Check for initial message (app opened from notification)
    final initialMessage = await _messaging.getInitialMessage();
    if (initialMessage != null) {
      _handleNotificationTap(initialMessage);
    }
  }
  
  void _handleForegroundMessage(RemoteMessage message) {
    // Show local notification
    FlutterLocalNotificationsPlugin().show(
      message.hashCode,
      message.notification?.title,
      message.notification?.body,
      const NotificationDetails(
        android: AndroidNotificationDetails(
          'high_importance_channel',
          'High Importance Notifications',
          importance: Importance.high,
        ),
        iOS: DarwinNotificationDetails(),
      ),
    );
  }
  
  void _handleNotificationTap(RemoteMessage message) {
    // Navigate based on data
    final route = message.data['route'];
    if (route != null) {
      navigatorKey.currentState?.pushNamed(route);
    }
  }
}

// Must be top-level function
@pragma('vm:entry-point')
Future<void> _backgroundHandler(RemoteMessage message) async {
  await Firebase.initializeApp();
  // Process message
}
```

## Firebase Storage

```dart
class StorageService {
  final FirebaseStorage _storage = FirebaseStorage.instance;
  
  Future<String> uploadFile(File file, String path) async {
    final ref = _storage.ref().child(path);
    
    final uploadTask = ref.putFile(
      file,
      SettableMetadata(contentType: 'image/jpeg'),
    );
    
    // Monitor progress
    uploadTask.snapshotEvents.listen((event) {
      final progress = event.bytesTransferred / event.totalBytes;
      print('Upload progress: ${(progress * 100).toStringAsFixed(0)}%');
    });
    
    await uploadTask;
    return await ref.getDownloadURL();
  }
  
  Future<void> deleteFile(String url) async {
    await _storage.refFromURL(url).delete();
  }
}
```

See `references/firebase-security.md` for security rules.
See `references/firebase-functions.md` for Cloud Functions patterns.
