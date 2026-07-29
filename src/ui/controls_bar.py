from PyQt6.QtWidgets import (
    QWidget, QHBoxLayout, QPushButton, QSlider, QLabel, QStyle,
)
from PyQt6.QtCore import Qt, pyqtSignal


class ControlsBar(QWidget):
    play_pause_clicked = pyqtSignal()
    stop_clicked = pyqtSignal()
    prev_sentence_clicked = pyqtSignal()
    next_sentence_clicked = pyqtSignal()
    prev_chapter_clicked = pyqtSignal()
    next_chapter_clicked = pyqtSignal()
    speed_changed = pyqtSignal(float)
    volume_changed = pyqtSignal(float)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._is_playing = False
        self._setup_ui()

    def _setup_ui(self):
        self.setStyleSheet("""
            QWidget { background-color: #2C2C2C; }
            QPushButton {
                background-color: #3C3C3C;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 6px 12px;
                font-size: 14px;
                min-width: 36px;
            }
            QPushButton:hover { background-color: #505050; }
            QPushButton:pressed { background-color: #666; }
            QLabel { color: #CCC; font-size: 12px; }
            QSlider::groove:horizontal {
                height: 4px;
                background: #555;
                border-radius: 2px;
            }
            QSlider::handle:horizontal {
                background: #FFB300;
                width: 14px;
                height: 14px;
                margin: -5px 0;
                border-radius: 7px;
            }
            QSlider::sub-page:horizontal {
                background: #FFB300;
                border-radius: 2px;
            }
        """)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(8, 4, 8, 4)
        layout.setSpacing(4)

        self.btn_prev_chapter = QPushButton("⏮")
        self.btn_prev_chapter.setToolTip("Chapter trước")
        self.btn_prev_sentence = QPushButton("◀")
        self.btn_prev_sentence.setToolTip("Câu trước")
        self.btn_play_pause = QPushButton("▶")
        self.btn_play_pause.setToolTip("Play / Pause")
        self.btn_play_pause.setMinimumWidth(48)
        self.btn_stop = QPushButton("⏹")
        self.btn_stop.setToolTip("Dừng")
        self.btn_next_sentence = QPushButton("▶▶")
        self.btn_next_sentence.setToolTip("Câu sau")
        self.btn_next_chapter = QPushButton("⏭")
        self.btn_next_chapter.setToolTip("Chapter sau")

        layout.addWidget(self.btn_prev_chapter)
        layout.addWidget(self.btn_prev_sentence)
        layout.addWidget(self.btn_play_pause)
        layout.addWidget(self.btn_stop)
        layout.addWidget(self.btn_next_sentence)
        layout.addWidget(self.btn_next_chapter)

        layout.addSpacing(16)

        layout.addWidget(QLabel("Tốc độ:"))
        self.speed_slider = QSlider(Qt.Orientation.Horizontal)
        self.speed_slider.setRange(50, 200)
        self.speed_slider.setValue(100)
        self.speed_slider.setFixedWidth(100)
        self.speed_label = QLabel("1.0x")
        self.speed_label.setFixedWidth(36)
        layout.addWidget(self.speed_slider)
        layout.addWidget(self.speed_label)

        layout.addSpacing(8)

        layout.addWidget(QLabel("Âm lượng:"))
        self.volume_slider = QSlider(Qt.Orientation.Horizontal)
        self.volume_slider.setRange(0, 100)
        self.volume_slider.setValue(80)
        self.volume_slider.setFixedWidth(80)
        self.volume_label = QLabel("80%")
        self.volume_label.setFixedWidth(32)
        layout.addWidget(self.volume_slider)
        layout.addWidget(self.volume_label)

        layout.addStretch()

        self.pos_label = QLabel("-- / --")
        self.pos_label.setStyleSheet("color: #AAA; font-size: 12px;")
        layout.addWidget(self.pos_label)

        self.btn_prev_chapter.clicked.connect(self.prev_chapter_clicked.emit)
        self.btn_prev_sentence.clicked.connect(self.prev_sentence_clicked.emit)
        self.btn_play_pause.clicked.connect(self._on_play_pause)
        self.btn_stop.clicked.connect(self.stop_clicked.emit)
        self.btn_next_sentence.clicked.connect(self.next_sentence_clicked.emit)
        self.btn_next_chapter.clicked.connect(self.next_chapter_clicked.emit)
        self.speed_slider.valueChanged.connect(self._on_speed_changed)
        self.volume_slider.valueChanged.connect(self._on_volume_changed)

    def _on_play_pause(self):
        self.play_pause_clicked.emit()

    def set_playing(self, playing):
        self._is_playing = playing
        self.btn_play_pause.setText("⏸" if playing else "▶")

    def set_position(self, current, total):
        self.pos_label.setText(f"{current + 1} / {total}")

    def _on_speed_changed(self, value):
        speed = value / 100.0
        self.speed_label.setText(f"{speed:.1f}x")
        self.speed_changed.emit(speed)

    def _on_volume_changed(self, value):
        self.volume_label.setText(f"{value}%")
        self.volume_changed.emit(value / 100.0)

    def get_speed(self):
        return self.speed_slider.value() / 100.0

    def get_volume(self):
        return self.volume_slider.value() / 100.0
