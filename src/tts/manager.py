import threading
import time
from PyQt6.QtCore import QObject, pyqtSignal


class TTSManager(QObject):
    sentence_started = pyqtSignal(int)
    sentence_finished = pyqtSignal(int)
    all_done = pyqtSignal()
    status_message = pyqtSignal(str)
    error_occurred = pyqtSignal(str)

    def __init__(self, engine, player, parent=None):
        super().__init__(parent)
        self.engine = engine
        self.player = player
        self.sentences = []
        self.current_index = -1
        self._running = False
        self._paused = False
        self._stop_requested = False
        self._thread = None
        self._prefetch_count = 2

        self.player.playback_started.connect(self._on_playback_started)
        self.player.playback_finished.connect(self._on_playback_finished)

    def start(self, sentences, start_index=0):
        self.sentences = sentences
        self.current_index = start_index
        self._running = True
        self._stop_requested = False
        self._paused = False
        self.player.clear()
        self.player.start()
        if self._thread is None or not self._thread.is_alive():
            self._thread = threading.Thread(target=self._feed_loop, daemon=True)
            self._thread.start()

    def stop(self):
        self._stop_requested = True
        self._running = False
        self.player.stop()

    def pause(self):
        self._paused = True
        self.player.pause()

    def resume(self):
        self._paused = False
        self.player.resume()

    def skip_to(self, index):
        was_playing = self._running and not self._paused
        self.stop()
        self.current_index = index
        if was_playing:
            self.start(self.sentences, index)

    def _feed_loop(self):
        i = self.current_index
        while i < len(self.sentences) and self._running and not self._stop_requested:
            while self._paused and not self._stop_requested:
                time.sleep(0.05)
            if self._stop_requested:
                break

            while self.player._queue.qsize() >= self._prefetch_count and not self._stop_requested:
                time.sleep(0.1)
            if self._stop_requested:
                break

            text = self.sentences[i]
            try:
                audio, sr = self.engine.generate(text)
            except Exception as e:
                self.error_occurred.emit(f"Lỗi TTS câu {i}: {e}")
                i += 1
                continue

            if self._stop_requested:
                break

            self.player._sr = sr
            self.player.enqueue(i, audio)
            i += 1
            self.current_index = i

        if not self._stop_requested:
            while not self._queue_empty():
                time.sleep(0.1)
            self.all_done.emit()
        self._running = False

    def _queue_empty(self):
        return self.player._queue.empty()

    def _on_playback_started(self, index):
        self.sentence_started.emit(index)

    def _on_playback_finished(self, index):
        self.sentence_finished.emit(index)
