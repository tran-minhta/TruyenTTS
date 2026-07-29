import numpy as np
from src.tts.engine import TTSEngine


class VieNeuEngine(TTSEngine):
    def __init__(self):
        self._voices = []
        self._current_voice = None
        self._tts = None
        self._sr = 24000

    def initialize(self, status_callback=None):
        if status_callback:
            status_callback("Đang tải model VieNeu-TTS (lần đầu có thể mất vài phút)...")
        from vieneu import Vieneu
        self._tts = Vieneu()
        self._voices = self._tts.list_preset_voices()
        if status_callback:
            status_callback(f"Sẵn sàng! {len(self._voices)} giọng đọc có sẵn.")

    def generate(self, text: str) -> tuple[np.ndarray, int]:
        if self._tts is None:
            raise RuntimeError("Engine chưa được khởi tạo")
        audio = self._tts.infer(text=text)
        return audio, self._sr

    def get_voices(self) -> list[tuple[str, str]]:
        return self._voices

    def set_voice(self, voice_id: str):
        self._current_voice = voice_id

    def close(self):
        if self._tts is not None:
            self._tts.close()
            self._tts = None
