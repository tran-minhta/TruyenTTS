import numpy as np
from src.tts.engine import TTSEngine


STYLES = ['tu_nhien', 'tin_tuc', 'ke_chuyen']


class VieNeuEngine(TTSEngine):
    def __init__(self):
        self._voices = []
        self._voice = None
        self._style = 'tu_nhien'
        self._params = {
            'temperature': 0.8,
            'top_k': 25,
            'top_p': 0.95,
            'repetition_penalty': 1.2,
            'denoise': True,
            'silence_p': 0.15,
        }
        self._tts = None
        self._sr = 24000

    def initialize(self, status_callback=None):
        if status_callback:
            status_callback("Đang tải model VieNeu-TTS...")
        from vieneu import Vieneu
        self._tts = Vieneu()
        self._voices = self._tts.list_preset_voices()
        if status_callback:
            status_callback(f"Sẵn sàng! {len(self._voices)} giọng đọc.")

    def generate(self, text: str) -> tuple[np.ndarray, int]:
        if self._tts is None:
            raise RuntimeError("Engine chưa được khởi tạo")
        audio = self._tts.infer(
            text=text,
            voice=self._voice,
            style=self._style,
            temperature=self._params['temperature'],
            top_k=self._params['top_k'],
            top_p=self._params['top_p'],
            repetition_penalty=self._params['repetition_penalty'],
            denoise=self._params['denoise'],
            silence_p=self._params['silence_p'],
        )
        return audio, self._sr

    def get_voices(self) -> list[tuple[str, str]]:
        return self._voices

    def set_voice(self, voice_id: str):
        self._voice = voice_id if voice_id else None

    def get_voice(self) -> str | None:
        return self._voice

    def get_styles(self) -> list[str]:
        return STYLES

    def set_style(self, style: str):
        self._style = style if style in STYLES else 'tu_nhien'

    def set_parameter(self, key: str, value):
        if key in self._params:
            self._params[key] = value

    def close(self):
        if self._tts is not None:
            self._tts.close()
            self._tts = None
