import threading
import time
from queue import Queue, Empty
import pyaudio
import numpy as np
from PyQt6.QtCore import QObject, pyqtSignal


class AudioPlayer(QObject):
    playback_started = pyqtSignal(int)
    playback_finished = pyqtSignal(int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._p = pyaudio.PyAudio()
        self._queue = Queue()
        self._running = False
        self._paused = False
        self._stop = False
        self._thread = None
        self._current_index = -1
        self._sr = 24000

    def enqueue(self, index: int, audio: np.ndarray):
        self._queue.put((index, audio))

    def start(self):
        self._running = True
        self._stop = False
        self._paused = False
        if self._thread is None or not self._thread.is_alive():
            self._thread = threading.Thread(target=self._play_loop, daemon=True)
            self._thread.start()

    def stop(self):
        self._stop = True
        self._paused = False
        while not self._queue.empty():
            try:
                self._queue.get_nowait()
            except Empty:
                break

    def pause(self):
        self._paused = True

    def resume(self):
        self._paused = False

    def skip(self):
        """Skip current sentence - clear current playback"""
        self.stop()
        self._stop = False
        self.start()

    def clear(self):
        while not self._queue.empty():
            try:
                self._queue.get_nowait()
            except Empty:
                break

    @property
    def is_playing(self):
        return self._running and not self._paused and not self._stop

    @property
    def current_index(self):
        return self._current_index

    def close(self):
        self.stop()
        self._running = False
        if self._p is not None:
            self._p.terminate()
            self._p = None

    def _play_loop(self):
        chunk_duration = 0.1
        while self._running and not self._stop:
            if self._paused:
                time.sleep(0.05)
                continue

            try:
                index, audio = self._queue.get(timeout=0.5)
            except Empty:
                continue

            self._current_index = index
            self.playback_started.emit(index)

            dtype = audio.dtype
            pa_format = pyaudio.paFloat32 if dtype == np.float32 else pyaudio.paInt16
            channels = 1 if audio.ndim == 1 else audio.shape[1]

            try:
                stream = self._p.open(
                    format=pa_format,
                    channels=channels,
                    rate=self._sr,
                    output=True,
                    frames_per_buffer=1024,
                )
            except Exception as e:
                print(f"AudioPlayer: cannot open stream: {e}")
                self.playback_finished.emit(index)
                continue

            audio_bytes = audio.tobytes()
            frame_size = channels * audio.dtype.itemsize
            chunk_frames = int(self._sr * chunk_duration)
            chunk_bytes = chunk_frames * frame_size

            offset = 0
            while offset < len(audio_bytes):
                if self._paused:
                    self._pause_wait()
                if self._stop:
                    break
                chunk = audio_bytes[offset:offset + chunk_bytes]
                if not chunk:
                    break
                try:
                    stream.write(chunk)
                except Exception:
                    break
                offset += len(chunk)

            stream.close()

            if not self._stop:
                self.playback_finished.emit(index)

    def _pause_wait(self):
        while self._paused and not self._stop:
            time.sleep(0.05)
