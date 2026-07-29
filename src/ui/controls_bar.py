from PyQt6.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QPushButton, QSlider,
    QLabel, QProgressBar,
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

    BTN = """
        QPushButton {
            background: transparent; color: #A8A8C8; border: none;
            border-radius: 6px; font-size: 16px; padding: 6px 10px;
            min-width: 32px; min-height: 32px;
        }
        QPushButton:hover { background: #36365A; color: #E8A87C; }
        QPushButton:pressed { background: #48486A; }
    """
    BTN_PRIMARY = """
        QPushButton {
            background: #E8A87C; color: #1A1A2E; border: none;
            border-radius: 8px; font-size: 18px; padding: 6px 16px;
            min-width: 44px; min-height: 36px;
        }
        QPushButton:hover { background: #F0B88C; }
        QPushButton:pressed { background: #D8986C; }
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self._is_playing = False
        self._setup_ui()

    def _setup_ui(self):
        self.setStyleSheet(f"""
            ControlsBar {{
                background: #1E1E36; border-top: 1px solid #36365A;
            }}
            QLabel {{ color: #8888A8; font-size: 11px; }}
            QProgressBar {{
                background: #36365A; border: none; border-radius: 2px;
                height: 3px; text-align: center;
            }}
            QProgressBar::chunk {{ background: #E8A87C; border-radius: 2px; }}
            QSlider::groove:horizontal {{
                height: 3px; background: #36365A; border-radius: 1px;
            }}
            QSlider::handle:horizontal {{
                background: #E8A87C; width: 12px; height: 12px;
                margin: -5px 0; border-radius: 6px;
            }}
            QSlider::sub-page:horizontal {{
                background: #E8A87C; border-radius: 1px;
            }}
        """)

        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)

        self.progress = QProgressBar()
        self.progress.setRange(0, 100)
        self.progress.setValue(0)
        self.progress.setFixedHeight(3)
        self.progress.setTextVisible(False)
        outer.addWidget(self.progress)

        row = QHBoxLayout()
        row.setContentsMargins(12, 6, 12, 8)
        row.setSpacing(4)

        self.btn_prev_chapter = QPushButton("⏮")
        self.btn_prev_chapter.setToolTip("Chương trước")
        self.btn_prev_sentence = QPushButton("◀")
        self.btn_prev_sentence.setToolTip("Câu trước")
        self.btn_play_pause = QPushButton("▶")
        self.btn_play_pause.setToolTip("Phát / Tạm dừng")
        self.btn_stop = QPushButton("⏹")
        self.btn_stop.setToolTip("Dừng")
        self.btn_next_sentence = QPushButton("▶")
        self.btn_next_sentence.setToolTip("Câu sau")
        self.btn_next_chapter = QPushButton("⏭")
        self.btn_next_chapter.setToolTip("Chương sau")
        self.btn_next_sentence.setStyleSheet(self.BTN)
        self.btn_next_chapter.setStyleSheet(self.BTN)

        self.btn_prev_chapter.setStyleSheet(self.BTN)
        self.btn_prev_sentence.setStyleSheet(self.BTN)
        self.btn_play_pause.setStyleSheet(self.BTN_PRIMARY)
        self.btn_stop.setStyleSheet(self.BTN)

        row.addWidget(self.btn_prev_chapter)
        row.addWidget(self.btn_prev_sentence)
        row.addWidget(self.btn_play_pause)
        row.addWidget(self.btn_stop)
        row.addWidget(self.btn_next_sentence)
        row.addWidget(self.btn_next_chapter)
        row.addSpacing(12)

        row.addWidget(QLabel("Tốc độ"))
        self.speed_slider = QSlider(Qt.Orientation.Horizontal)
        self.speed_slider.setRange(50, 200)
        self.speed_slider.setValue(100)
        self.speed_slider.setFixedWidth(80)
        self.speed_label = QLabel("1.0x")
        self.speed_label.setFixedWidth(30)
        row.addWidget(self.speed_slider)
        row.addWidget(self.speed_label)
        row.addSpacing(8)

        row.addWidget(QLabel("Âm lượng"))
        self.volume_slider = QSlider(Qt.Orientation.Horizontal)
        self.volume_slider.setRange(0, 100)
        self.volume_slider.setValue(80)
        self.volume_slider.setFixedWidth(60)
        self.volume_label = QLabel("80%")
        self.volume_label.setFixedWidth(28)
        row.addWidget(self.volume_slider)
        row.addWidget(self.volume_label)
        row.addSpacing(8)

        self.pos_label = QLabel("-- / --")
        self.pos_label.setStyleSheet("color: #A8A8C8; font-size: 12px; padding: 0 8px;")
        row.addWidget(self.pos_label)

        row.addStretch()

        outer.addLayout(row)

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
        if total > 0:
            self.progress.setValue(int((current + 1) / total * 100))

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
