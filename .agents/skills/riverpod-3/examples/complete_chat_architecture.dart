// COMPLETE RIVERPOD 3.0 CHAT ARCHITECTURE
// Dual-stack (Firestore + WebSocket) with optimistic UI

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:riverpod_annotation/riverpod_annotation.dart';
import 'package:cloud_firestore/cloud_firestore.dart';
import 'package:socket_io_client/socket_io_client.dart' as io;
import 'package:fpdart/fpdart.dart';

part 'complete_chat_architecture.g.dart';

// ============================================================================
// DOMAIN MODELS
// ============================================================================

enum MessageStatus { sending, sent, failed }

class Message {
  final String id;
  final String text;
  final String senderId;
  final DateTime createdAt;
  final MessageStatus status;

  Message({
    required this.id,
    required this.text,
    required this.senderId,
    required this.createdAt,
    this.status = MessageStatus.sent,
  });

  Message copyWith({MessageStatus? status}) => Message(
    id: id,
    text: text,
    senderId: senderId,
    createdAt: createdAt,
    status: status ?? this.status,
  );

  factory Message.fromFirestore(DocumentSnapshot doc) {
    final data = doc.data() as Map<String, dynamic>;
    return Message(
      id: doc.id,
      text: data['text'],
      senderId: data['senderId'],
      createdAt: (data['createdAt'] as Timestamp).toDate(),
      status: MessageStatus.sent,
    );
  }

  factory Message.fromJson(Map<String, dynamic> json) => Message(
    id: json['id'],
    text: json['text'],
    senderId: json['senderId'],
    createdAt: DateTime.parse(json['createdAt']),
  );
}

// ============================================================================
// FAILURES (Functional Error Handling)
// ============================================================================

sealed class ChatFailure {
  const ChatFailure();
}

class NetworkFailure extends ChatFailure {}
class AuthenticationFailure extends ChatFailure {}
class UnknownFailure extends ChatFailure {
  final String message;
  const UnknownFailure(this.message);
}

// ============================================================================
// REPOSITORY LAYER (Returns Either)
// ============================================================================

abstract class ChatRepository {
  Future<Either<ChatFailure, Message>> sendMessage(String chatId, String text);
  Future<Either<ChatFailure, void>> deleteMessage(String chatId, String messageId);
}

@riverpod
ChatRepository chatRepository(Ref ref) => FirebaseChatRepository(
  firestore: ref.watch(firebaseFirestoreProvider),
  socket: ref.watch(socketClientProvider),
);

class FirebaseChatRepository implements ChatRepository {
  final FirebaseFirestore firestore;
  final io.Socket socket;

  FirebaseChatRepository({required this.firestore, required this.socket});

  @override
  Future<Either<ChatFailure, Message>> sendMessage(String chatId, String text) async {
    try {
      final docRef = await firestore
        .collection('chats/$chatId/messages')
        .add({
          'text': text,
          'senderId': 'current_user_id', // Get from auth
          'createdAt': FieldValue.serverTimestamp(),
        });

      final doc = await docRef.get();
      final message = Message.fromFirestore(doc);

      // Emit via WebSocket for real-time delivery
      socket.emit('send_message', {
        'chatId': chatId,
        'message': message,
      });

      return right(message);
    } on FirebaseException catch (e) {
      return left(UnknownFailure(e.message ?? 'Firestore error'));
    } catch (e) {
      return left(NetworkFailure());
    }
  }

  @override
  Future<Either<ChatFailure, void>> deleteMessage(String chatId, String messageId) async {
    try {
      await firestore
        .collection('chats/$chatId/messages')
        .doc(messageId)
        .delete();
      return right(null);
    } catch (e) {
      return left(UnknownFailure('Delete failed'));
    }
  }
}

// ============================================================================
// INFRASTRUCTURE PROVIDERS
// ============================================================================

@Riverpod(keepAlive: true)
FirebaseFirestore firebaseFirestore(Ref ref) => FirebaseFirestore.instance;

@Riverpod(keepAlive: true)
io.Socket socketClient(Ref ref) {
  final socket = io.io('wss://your-api.com', <String, dynamic>{
    'transports': ['websocket'],
    'autoConnect': false,
  });

  socket.connect();

  ref.onDispose(() {
    socket.disconnect();
    socket.dispose();
  });

  return socket;
}

// ============================================================================
// DATA LAYER: FIRESTORE STREAM
// ============================================================================

@riverpod
Stream<List<Message>> firestoreMessages(Ref ref, String chatId) {
  final firestore = ref.watch(firebaseFirestoreProvider);

  // TTL Cache: Keep stream alive 5min after leaving screen
  final link = ref.keepAlive();
  final timer = Timer(Duration(minutes: 5), link.close);
  ref.onDispose(() => timer.cancel());

  return firestore
    .collection('chats/$chatId/messages')
    .orderBy('createdAt', descending: true)
    .limit(50)
    .snapshots()
    .map((snapshot) => snapshot.docs
      .map((doc) => Message.fromFirestore(doc))
      .toList()
    );
}

// ============================================================================
// DATA LAYER: WEBSOCKET STREAM
// ============================================================================

@riverpod
Stream<Message> liveSocketMessages(Ref ref) {
  final socket = ref.watch(socketClientProvider);
  final controller = StreamController<Message>();

  void onNewMessage(dynamic data) {
    try {
      final message = Message.fromJson(data);
      controller.add(message);
    } catch (e) {
      // Log error, don't crash
      debugPrint('Socket message parse error: $e');
    }
  }

  socket.on('new_message', onNewMessage);

  ref.onDispose(() {
    socket.off('new_message', onNewMessage);
    controller.close();
  });

  return controller.stream;
}

// ============================================================================
// STATE LAYER: PENDING MESSAGES (Optimistic UI)
// ============================================================================

@riverpod
class PendingMessages extends _$PendingMessages {
  @override
  List<Message> build(String chatId) => [];

  void add(Message message) {
    state = [...state, message];
  }

  void remove(String messageId) {
    state = state.where((m) => m.id != messageId).toList();
  }

  void updateStatus(String messageId, MessageStatus status) {
    state = state.map((m) =>
      m.id == messageId ? m.copyWith(status: status) : m
    ).toList();
  }
}

// ============================================================================
// STATE LAYER: MERGED TIMELINE (UI-Facing)
// ============================================================================

@riverpod
List<Message> chatTimeline(Ref ref, String chatId) {
  // Watch server messages (AsyncValue)
  final serverAsync = ref.watch(firestoreMessagesProvider(chatId));

  // Watch pending messages (optimistic)
  final pending = ref.watch(pendingMessagesProvider(chatId));

  // Merge: pending first (appear at top), then server
  final serverMessages = serverAsync.valueOrNull ?? [];

  return [...pending, ...serverMessages];
}

// ============================================================================
// CONTROLLER: MESSAGE SENDER
// ============================================================================

@riverpod
class MessageSender extends _$MessageSender {
  @override
  void build() {}

  Future<void> send(String chatId, String text) async {
    // 1. Create temporary message
    final tempMessage = Message(
      id: 'temp_${DateTime.now().millisecondsSinceEpoch}',
      text: text,
      senderId: 'current_user_id',
      createdAt: DateTime.now(),
      status: MessageStatus.sending,
    );

    // 2. Add to pending (immediate UI feedback)
    ref.read(pendingMessagesProvider(chatId).notifier).add(tempMessage);

    // 3. Send to repository
    final repository = ref.read(chatRepositoryProvider);
    final result = await repository.sendMessage(chatId, text);

    // 4. Handle result (fold Either)
    result.fold(
      (failure) {
        // Mark as failed, keep in pending for retry
        ref.read(pendingMessagesProvider(chatId).notifier)
          .updateStatus(tempMessage.id, MessageStatus.failed);
      },
      (serverMessage) {
        // Success: remove from pending (will appear in Firestore stream)
        ref.read(pendingMessagesProvider(chatId).notifier)
          .remove(tempMessage.id);
      },
    );
  }

  Future<void> retry(String chatId, Message failedMessage) async {
    // Update status to sending
    ref.read(pendingMessagesProvider(chatId).notifier)
      .updateStatus(failedMessage.id, MessageStatus.sending);

    // Retry send
    await send(chatId, failedMessage.text);
  }
}

// ============================================================================
// UI LAYER
// ============================================================================

class ChatScreen extends ConsumerWidget {
  final String chatId;

  const ChatScreen({required this.chatId});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final messages = ref.watch(chatTimelineProvider(chatId));

    return Scaffold(
      appBar: AppBar(title: Text('Chat')),
      body: Column(
        children: [
          Expanded(
            child: ListView.builder(
              reverse: true,
              itemCount: messages.length,
              itemBuilder: (ctx, index) {
                final message = messages[index];
                return MessageBubble(message: message, chatId: chatId);
              },
            ),
          ),
          ChatInput(chatId: chatId),
        ],
      ),
    );
  }
}

class MessageBubble extends ConsumerWidget {
  final Message message;
  final String chatId;

  const MessageBubble({required this.message, required this.chatId});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    return ListTile(
      title: Text(message.text),
      subtitle: Row(
        children: [
          Text(_formatTime(message.createdAt)),
          SizedBox(width: 8),
          _buildStatusIcon(message.status),
        ],
      ),
      trailing: message.status == MessageStatus.failed
        ? IconButton(
            icon: Icon(Icons.refresh),
            onPressed: () => ref
              .read(messageSenderProvider.notifier)
              .retry(chatId, message),
          )
        : null,
    );
  }

  Widget _buildStatusIcon(MessageStatus status) => switch (status) {
    MessageStatus.sending => SizedBox(
      width: 12,
      height: 12,
      child: CircularProgressIndicator(strokeWidth: 2),
    ),
    MessageStatus.sent => Icon(Icons.check, size: 16, color: Colors.grey),
    MessageStatus.failed => Icon(Icons.error, size: 16, color: Colors.red),
  };

  String _formatTime(DateTime dt) => '${dt.hour}:${dt.minute.toString().padLeft(2, '0')}';
}

class ChatInput extends ConsumerStatefulWidget {
  final String chatId;

  const ChatInput({required this.chatId});

  @override
  ConsumerState<ChatInput> createState() => _ChatInputState();
}

class _ChatInputState extends ConsumerState<ChatInput> {
  final _controller = TextEditingController();

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  void _send() {
    final text = _controller.text.trim();
    if (text.isEmpty) return;

    ref.read(messageSenderProvider.notifier).send(widget.chatId, text);
    _controller.clear();
  }

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: EdgeInsets.all(8),
      child: Row(
        children: [
          Expanded(
            child: TextField(
              controller: _controller,
              decoration: InputDecoration(hintText: 'Type a message...'),
              onSubmitted: (_) => _send(),
            ),
          ),
          IconButton(
            icon: Icon(Icons.send),
            onPressed: _send,
          ),
        ],
      ),
    );
  }
}
