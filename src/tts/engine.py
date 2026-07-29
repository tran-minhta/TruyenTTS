from abc import ABC, abstractmethod
import numpy as np


class TTSEngine(ABC):
    @abstractmethod
    def generate(self, text: str) -> tuple[np.ndarray, int]:
        pass

    @abstractmethod
    def get_voices(self) -> list[tuple[str, str]]:
        pass

    @abstractmethod
    def set_voice(self, voice_id: str):
        pass

    @abstractmethod
    def close(self):
        pass
