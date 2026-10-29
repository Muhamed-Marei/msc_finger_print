// INFINITE SCROLL PAGINATION WITH ASYNCNOTIFIER
// Memory-efficient, error-preserving, reverse pagination for chat

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:riverpod_annotation/riverpod_annotation.dart';
import 'package:cloud_firestore/cloud_firestore.dart';

part 'pagination_pattern.g.dart';

class Message {
  final String id;
  final String text;
  final DateTime createdAt;

  Message({required this.id, required this.text, required this.createdAt});

  factory Message.fromFirestore(DocumentSnapshot doc) {
    final data = doc.data() as Map<String, dynamic>;
    return Message(
      id: doc.id,
      text: data['text'],
      createdAt: (data['createdAt'] as Timestamp).toDate(),
    );
  }
}

// ============================================================================
// PAGINATION NOTIFIER (Self-Contained State)
// ============================================================================

@riverpod
class MessagePagination extends _$MessagePagination {
  // Internal pagination state (not exposed to UI)
  DocumentSnapshot? _lastDoc;
  bool _hasMore = true;

  @override
  Future<List<Message>> build(String chatId) async {
    // Reset state on initialization
    _lastDoc = null;
    _hasMore = true;

    // Load initial page
    return _fetchPage(chatId);
  }

  Future<List<Message>> _fetchPage(String chatId) async {
    final firestore = FirebaseFirestore.instance;

    // Build query
    var query = firestore
      .collection('chats/$chatId/messages')
      .orderBy('createdAt', descending: true)
      .limit(20);

    // Apply cursor if not first page
    if (_lastDoc != null) {
      query = query.startAfterDocument(_lastDoc!);
    }

    // Execute query
    final snapshot = await query.get();

    // Update internal state
    _lastDoc = snapshot.docs.isNotEmpty ? snapshot.docs.last : null;
    _hasMore = snapshot.docs.length == 20; // If less than limit, no more data

    // Parse messages
    return snapshot.docs
      .map((doc) => Message.fromFirestore(doc))
      .toList();
  }

  Future<void> loadMore() async {
    // Guard: Don't load if already loading or no more data
    if (state.isLoading || !_hasMore) return;

    // Capture current list
    final currentList = state.value ?? [];

    // Set loading state BUT preserve previous data
    // This prevents UI from showing spinner over entire list
    state = const AsyncLoading().copyWithPrevious(state);

    // Fetch next page and update state
    state = await AsyncValue.guard(() async {
      final newMessages = await _fetchPage(arg);
      return [...currentList, ...newMessages]; // Append new to existing
    });
  }

  // Manual refresh (pull-to-refresh)
  Future<void> refresh() async {
    _lastDoc = null;
    _hasMore = true;

    state = const AsyncLoading();
    state = await AsyncValue.guard(() => _fetchPage(arg));
  }
}

// ============================================================================
// UI: SCROLL DETECTION
// ============================================================================

class PaginatedChatScreen extends ConsumerWidget {
  final String chatId;

  const PaginatedChatScreen({required this.chatId});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final messagesAsync = ref.watch(messagePaginationProvider(chatId));

    return Scaffold(
      appBar: AppBar(title: Text('Chat History')),
      body: NotificationListener<ScrollNotification>(
        onNotification: (notification) {
          // Trigger pagination when user scrolls near top (history)
          if (notification.metrics.extentAfter < 500) {
            ref.read(messagePaginationProvider(chatId).notifier).loadMore();
          }
          return false;
        },
        child: RefreshIndicator(
          onRefresh: () => ref
            .read(messagePaginationProvider(chatId).notifier)
            .refresh(),
          child: messagesAsync.when(
            data: (messages) => ListView.builder(
              reverse: true, // Chat style: newest at bottom
              itemCount: messages.length + 1, // +1 for loading indicator
              itemBuilder: (ctx, index) {
                // Loading indicator at top (for history)
                if (index == messages.length) {
                  return messagesAsync.isLoading
                    ? Center(child: Padding(
                        padding: EdgeInsets.all(16),
                        child: CircularProgressIndicator(),
                      ))
                    : SizedBox.shrink();
                }

                final message = messages[index];
                return MessageTile(message: message);
              },
            ),
            loading: () => Center(child: CircularProgressIndicator()),
            error: (error, stackTrace) => Center(
              child: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  Icon(Icons.error, color: Colors.red, size: 48),
                  SizedBox(height: 16),
                  Text('Error loading messages'),
                  SizedBox(height: 8),
                  ElevatedButton(
                    onPressed: () => ref.invalidate(messagePaginationProvider(chatId)),
                    child: Text('Retry'),
                  ),
                ],
              ),
            ),
          ),
        ),
      ),
    );
  }
}

class MessageTile extends StatelessWidget {
  final Message message;

  const MessageTile({required this.message});

  @override
  Widget build(BuildContext context) {
    return ListTile(
      title: Text(message.text),
      subtitle: Text(_formatTime(message.createdAt)),
    );
  }

  String _formatTime(DateTime dt) =>
    '${dt.day}/${dt.month} ${dt.hour}:${dt.minute.toString().padLeft(2, '0')}';
}

// ============================================================================
// ALTERNATIVE: SCROLL CONTROLLER APPROACH
// ============================================================================

class PaginatedListWithController extends ConsumerStatefulWidget {
  final String chatId;

  const PaginatedListWithController({required this.chatId});

  @override
  ConsumerState<PaginatedListWithController> createState() =>
    _PaginatedListWithControllerState();
}

class _PaginatedListWithControllerState
  extends ConsumerState<PaginatedListWithController> {

  final ScrollController _scrollController = ScrollController();

  @override
  void initState() {
    super.initState();
    _scrollController.addListener(_onScroll);
  }

  @override
  void dispose() {
    _scrollController.removeListener(_onScroll);
    _scrollController.dispose();
    super.dispose();
  }

  void _onScroll() {
    // Trigger when 500px from top
    if (_scrollController.position.extentAfter < 500) {
      ref.read(messagePaginationProvider(widget.chatId).notifier).loadMore();
    }
  }

  @override
  Widget build(BuildContext context) {
    final messagesAsync = ref.watch(messagePaginationProvider(widget.chatId));

    return messagesAsync.when(
      data: (messages) => ListView.builder(
        controller: _scrollController,
        reverse: true,
        itemCount: messages.length,
        itemBuilder: (ctx, index) => MessageTile(message: messages[index]),
      ),
      loading: () => Center(child: CircularProgressIndicator()),
      error: (e, st) => Center(child: Text('Error: $e')),
    );
  }
}

// ============================================================================
// PERFORMANCE NOTE: isReloading vs. isLoading
// ============================================================================

// When using copyWithPrevious(state), check isReloading for subtle UI feedback:
class AdvancedPaginationUI extends ConsumerWidget {
  final String chatId;

  const AdvancedPaginationUI({required this.chatId});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final messagesAsync = ref.watch(messagePaginationProvider(chatId));

    return Stack(
      children: [
        // Main list (always visible even when reloading)
        messagesAsync.when(
          data: (messages) => ListView.builder(
            reverse: true,
            itemCount: messages.length,
            itemBuilder: (ctx, i) => MessageTile(message: messages[i]),
          ),
          loading: () => Center(child: CircularProgressIndicator()),
          error: (e, st) => ErrorView(error: e),
        ),

        // Overlay loading indicator (only when reloading, not initial load)
        if (messagesAsync.isRefreshing) // or messagesAsync.isReloading
          Positioned(
            top: 0,
            left: 0,
            right: 0,
            child: LinearProgressIndicator(),
          ),
      ],
    );
  }
}

class ErrorView extends StatelessWidget {
  final Object error;

  const ErrorView({required this.error});

  @override
  Widget build(BuildContext context) {
    return Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Icon(Icons.error, color: Colors.red, size: 64),
          SizedBox(height: 16),
          Text('Failed to load messages'),
        ],
      ),
    );
  }
}
