import subprocess
import signal
from PyQt6.QtCore import QThread, pyqtSignal

class PiperEngine(QThread):
    # Tín hiệu gửi chỉ số câu đang đọc về UI để highlight và cuộn
    sentence_changed = pyqtSignal(int)
    finished_reading = pyqtSignal()

    def __init__(self, sentences, piper_path, model_path):
        super().__init__()
        self.sentences = sentences
        self.piper_path = piper_path
        self.model_path = model_path
        self.current_index = 0
        self.is_running = True
        self.process = None

    def run(self):
        while self.current_index < len(self.sentences) and self.is_running:
            sentence = self.sentences[self.current_index].strip()
            
            if not sentence:
                self.current_index += 1
                continue

            self.sentence_changed.emit(self.current_index)

            # SỬA TẠI ĐÂY: Gọi qua python3 -m piper thay vì file binary
            # Sử dụng đúng biến self.model_path dẫn tới file .onnx của bạn
            cmd = f'echo "{sentence}" | python3 -m piper --model {self.model_path} --output-raw | aplay -r 22050 -f S16_LE -t raw'
            
            self.process = subprocess.Popen(cmd, shell=True, preexec_fn=os.setsid)
            self.process.wait()
            
            self.current_index += 1

        self.finished_reading.emit()

    def stop(self):
        self.is_running = False
        if self.process:
            try:
                # Giết toàn bộ group tiến trình bao gồm cả Piper và aplay
                os.killpg(os.getpgid(self.process.pid), signal.SIGTERM)
            except Exception:
                pass
