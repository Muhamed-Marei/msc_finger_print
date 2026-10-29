// MEMORY-SAFE VIDEO PLAYER MANAGEMENT
// Automatic disposal when scrolling, prevents OOM crashes

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:riverpod_annotation/riverpod_annotation.dart';
import 'package:video_player/video_player.dart';

part 'video_memory_management.g.dart';

// ============================================================================
// VIDEO CONTROLLER PROVIDER (Scoped AutoDispose)
// ============================================================================

@riverpod
Future<VideoPlayerController> videoController(
  Ref ref,
  String videoUrl,
) async {
  // 1. Create controller
  final controller = VideoPlayerController.networkUrl(Uri.parse(videoUrl));

  // 2. CRITICAL: Bind disposal to provider lifecycle
  //    When widget unmounts → ref disposed → controller.dispose() called
  ref.onDispose(() {
    debugPrint('🗑️ Disposing video controller: $videoUrl');
    controller.dispose();
  });

  // 3. Initialize
  await controller.initialize();

  // 4. Optional: Auto-play
  // controller.play();

  return controller;
}

// ============================================================================
// VIDEO WIDGET (Stateless - No Manual Cleanup)
// ============================================================================

class VideoMessage extends ConsumerWidget {
  final String videoUrl;

  const VideoMessage({required this.videoUrl});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final controllerAsync = ref.watch(videoControllerProvider(videoUrl));

    return controllerAsync.when(
      data: (controller) => _VideoPlayer(controller: controller),
      loading: () => Container(
        height: 200,
        color: Colors.black12,
        child: Center(child: CircularProgressIndicator()),
      ),
      error: (error, stackTrace) => Container(
        height: 200,
        color: Colors.red.shade50,
        child: Center(
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              Icon(Icons.error, color: Colors.red),
              SizedBox(height: 8),
              Text('Video load failed'),
            ],
          ),
        ),
      ),
    );
  }
}

class _VideoPlayer extends StatelessWidget {
  final VideoPlayerController controller;

  const _VideoPlayer({required this.controller});

  @override
  Widget build(BuildContext context) {
    return AspectRatio(
      aspectRatio: controller.value.aspectRatio,
      child: Stack(
        alignment: Alignment.center,
        children: [
          VideoPlayer(controller),

          // Play/Pause overlay
          if (!controller.value.isPlaying)
            IconButton(
              icon: Icon(Icons.play_arrow, color: Colors.white, size: 64),
              onPressed: () => controller.play(),
            ),
        ],
      ),
    );
  }
}

// ============================================================================
// CHAT SCREEN WITH VIDEO MESSAGES (Infinite Scroll)
// ============================================================================

class ChatScreenWithVideos extends StatelessWidget {
  final List<Message> messages;

  const ChatScreenWithVideos({required this.messages});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text('Chat')),
      body: ListView.builder(
        reverse: true,
        itemCount: messages.length,
        itemBuilder: (ctx, index) {
          final message = messages[index];

          return switch (message) {
            TextMessage(:final text) => ListTile(title: Text(text)),
            VideoMessageData(:final videoUrl) => VideoMessage(videoUrl: videoUrl),
          };
        },
      ),
    );
  }
}

// ============================================================================
// MESSAGE MODELS
// ============================================================================

sealed class Message {}

class TextMessage extends Message {
  final String text;
  TextMessage(this.text);
}

class VideoMessageData extends Message {
  final String videoUrl;
  VideoMessageData(this.videoUrl);
}

// ============================================================================
// ADVANCED: KEEP ALIVE FOR RECENTLY VIEWED VIDEOS
// ============================================================================

// Keep video in memory for 30s after scrolling off-screen
@riverpod
Future<VideoPlayerController> cachedVideoController(
  Ref ref,
  String videoUrl,
) async {
  final controller = VideoPlayerController.networkUrl(Uri.parse(videoUrl));

  // Keep alive for 30 seconds after widget disposal
  final link = ref.keepAlive();
  final timer = Timer(Duration(seconds: 30), () {
    debugPrint('🕐 Cache expired for: $videoUrl');
    link.close();
  });

  ref.onDispose(() {
    debugPrint('🗑️ Disposing cached video controller: $videoUrl');
    timer.cancel();
    controller.dispose();
  });

  await controller.initialize();
  return controller;
}

// ============================================================================
// ADVANCED: VIDEO STATE NOTIFIER (Playback Control)
// ============================================================================

@riverpod
class VideoPlayback extends _$VideoPlayback {
  @override
  Future<VideoPlayerController> build(String videoUrl) async {
    final controller = VideoPlayerController.networkUrl(Uri.parse(videoUrl));

    ref.onDispose(() {
      debugPrint('🗑️ VideoPlayback disposed: $videoUrl');
      controller.dispose();
    });

    await controller.initialize();
    return controller;
  }

  void play() {
    state.whenData((controller) => controller.play());
  }

  void pause() {
    state.whenData((controller) => controller.pause());
  }

  void seek(Duration position) {
    state.whenData((controller) => controller.seekTo(position));
  }
}

// ============================================================================
// WIDGET USING NOTIFIER
// ============================================================================

class InteractiveVideoPlayer extends ConsumerWidget {
  final String videoUrl;

  const InteractiveVideoPlayer({required this.videoUrl});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final controllerAsync = ref.watch(videoPlaybackProvider(videoUrl));

    return controllerAsync.when(
      data: (controller) => Column(
        children: [
          AspectRatio(
            aspectRatio: controller.value.aspectRatio,
            child: VideoPlayer(controller),
          ),
          VideoControls(videoUrl: videoUrl),
        ],
      ),
      loading: () => Center(child: CircularProgressIndicator()),
      error: (e, st) => Text('Error: $e'),
    );
  }
}

class VideoControls extends ConsumerWidget {
  final String videoUrl;

  const VideoControls({required this.videoUrl});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final controllerAsync = ref.watch(videoPlaybackProvider(videoUrl));

    return controllerAsync.whenData((controller) {
      return Row(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          IconButton(
            icon: Icon(
              controller.value.isPlaying ? Icons.pause : Icons.play_arrow,
            ),
            onPressed: () {
              if (controller.value.isPlaying) {
                ref.read(videoPlaybackProvider(videoUrl).notifier).pause();
              } else {
                ref.read(videoPlaybackProvider(videoUrl).notifier).play();
              }
            },
          ),
          Expanded(
            child: Slider(
              value: controller.value.position.inSeconds.toDouble(),
              max: controller.value.duration.inSeconds.toDouble(),
              onChanged: (value) {
                ref.read(videoPlaybackProvider(videoUrl).notifier)
                  .seek(Duration(seconds: value.toInt()));
              },
            ),
          ),
          Text(_formatDuration(controller.value.position)),
        ],
      );
    }).value ?? SizedBox.shrink();
  }

  String _formatDuration(Duration duration) {
    String twoDigits(int n) => n.toString().padLeft(2, '0');
    final minutes = twoDigits(duration.inMinutes.remainder(60));
    final seconds = twoDigits(duration.inSeconds.remainder(60));
    return '$minutes:$seconds';
  }
}

// ============================================================================
// PERFORMANCE MONITORING
// ============================================================================

class VideoMemoryMonitor extends ConsumerWidget {
  @override
  Widget build(BuildContext context, WidgetRef ref) {
    // In debug mode, you can track active video controllers
    return FloatingActionButton(
      mini: true,
      onPressed: () {
        // Log all active providers
        final container = ProviderScope.containerOf(context);
        debugPrint('📊 Active video providers: ${container.getAllProviderElements().length}');
      },
      child: Icon(Icons.memory),
    );
  }
}
