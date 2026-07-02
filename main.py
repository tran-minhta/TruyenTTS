import sys
import os
import re
import yaml
from PyQt6.QtWidgets import (QApplication, QMainWindow, QTextBrowser, 
                             QVBoxLayout, QHBoxLayout, QPushButton, QWidget, QFileDialog, QMessageBox)
from PyQt6.QtGui import QTextCursor, QTextCharFormat, QColor
from parsers import BookParser
from tts_engine import PiperEngine

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("TruyenTTS Reader")
        self.setGeometry(150, 150, 900, 700)

        # Đọc cấu hình đường dẫn model từ file config.yaml
        self.load_config()

        self.full_text = ""
        self.sentences = []
        self.sentence_map = [] 
        self.tts_worker = None

        self.init_ui()

    def load_config(self):
        config_path = "config.yaml"
        default_path = "./piper1-gpl/models/vais1000/vi_VN-vais1000-medium.onnx"
        if not os.path.exists(config_path):
            config = {"path_models": default_path}
            with open(config_path, "w", encoding="utf-8") as f:
                yaml.dump(config, f)
            self.model_path = default_path
        else:
            with open(config_path, "r", encoding="utf-8") as f:
                config = yaml.safe_load(f)
                self.model_path = config.get("path_models", default_path)

    def init_ui(self):
        layout = QVBoxLayout()

        # Thanh điều khiển file
        top_layout = QHBoxLayout()
        self.btn_open = QPushButton("Mở Truyện (.txt, .epub, .pdf)")
        self.btn_open.clicked.connect(self.handle_open_file)
        top_layout.addWidget(self.btn_open)
        layout.addLayout(top_layout)

        # Khung hiển thị nội dung truyện
        self.text_display = QTextBrowser()
        self.text_display.setStyleSheet("font-size: 19px; line-height: 160%; padding: 10px;")
        layout.addWidget(self.text_display)

        # Thanh điều khiển Đọc / Tạm dừng
        bottom_layout = QHBoxLayout()
        self.btn_play = QPushButton("Đọc")
        self.btn_play.clicked.connect(self.handle_play)
        self.btn_stop = QPushButton("Dừng")
        self.btn_stop.clicked.connect(self.handle_stop)
        self.btn_stop.setEnabled(False)
        
        bottom_layout.addWidget(self.btn_play)
        bottom_layout.addWidget(self.btn_stop)
        layout.addLayout(bottom_layout)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def handle_open_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Chọn file truyện", "", "Truyện (*.txt *.epub *.pdf);;All Files (*)"
        )
        if not file_path:
            return

        try:
            self.full_text = BookParser.get_text(file_path)
            self.text_display.setText(self.full_text)
            
            self.sentences = re.split(r'(?<=[.!?…])\s+', self.full_text)
            
            self.sentence_map = []
            search_start = 0
            for sentence in self.sentences:
                start_pos = self.full_text.find(sentence, search_start)
                end_pos = start_pos + len(sentence)
                self.sentence_map.append((start_pos, end_pos))
                search_start = end_pos

        except Exception as e:
            QMessageBox.critical(self, "Lỗi", f"Không thể đọc file: {str(e)}")

    def handle_play(self):
        if not self.sentences:
            QMessageBox.warning(self, "Thông báo", "Vui lòng tải một cuốn truyện trước!")
            return

        self.tts_worker = PiperEngine(self.sentences, self.model_path)
        self.tts_worker.sentence_changed.connect(self.update_highlight_and_scroll)
        self.tts_worker.finished_reading.connect(self.handle_stop)
        
        self.tts_worker.start()
        self.btn_play.setEnabled(False)
        self.btn_stop.setEnabled(True)

    def handle_stop(self):
        if self.tts_worker:
            self.tts_worker.stop()
            self.tts_worker = None
        
        self.clear_highlight()
        self.btn_play.setEnabled(True)
        self.btn_stop.setEnabled(False)

    def clear_highlight(self):
        cursor = self.text_display.textCursor()
        cursor.select(QTextCursor.SelectionType.Document)
        fmt = QTextCharFormat()
        fmt.setBackground(QColor("transparent"))
        cursor.setCharFormat(fmt)

    def update_highlight_and_scroll(self, index):
        if index >= len(self.sentence_map):
            return

        start, end = self.sentence_map[index]
        self.clear_highlight()

        cursor = self.text_display.textCursor()
        cursor.setPosition(start)
        cursor.setPosition(end, QTextCursor.MoveMode.KeepAnchor)

        fmt = QTextCharFormat()
        fmt.setBackground(QColor("#FFF2B2"))
        cursor.setCharFormat(fmt)

        self.text_display.setTextCursor(cursor)
        self.text_display.ensureCursorVisible()

    def closeEvent(self, event):
        self.handle_stop()
        event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
