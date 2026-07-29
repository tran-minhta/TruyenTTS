from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGroupBox,
    QComboBox, QSlider, QLabel, QCheckBox, QSpinBox,
    QScrollArea, QFrame,
)
from PyQt6.QtCore import Qt, pyqtSignal


class SettingsPanel(QWidget):
    voice_changed = pyqtSignal(str)
    style_changed = pyqtSignal(str)
    param_changed = pyqtSignal(str, object)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()

    def _setup_ui(self):
        self.setStyleSheet("""
            QWidget { background-color: #252542; color: #C8C8E0; }
            QGroupBox {
                font-size: 12px; font-weight: bold; color: #A8A8C8;
                border: 1px solid #36365A; border-radius: 6px;
                margin-top: 12px; padding: 12px 8px 8px;
            }
            QGroupBox::title {
                subcontrol-origin: margin; subcontrol-position: top left;
                padding: 0 8px; color: #E8A87C;
            }
            QComboBox {
                background-color: #36365A; color: #E0E0F0;
                border: 1px solid #48486A; border-radius: 4px;
                padding: 4px 8px; font-size: 12px;
                min-height: 24px;
            }
            QComboBox:hover { border-color: #E8A87C; }
            QComboBox::drop-down { border: none; width: 20px; }
            QComboBox QAbstractItemView {
                background-color: #36365A; color: #E0E0F0;
                selection-background-color: #E8A87C;
                selection-color: #1A1A2E;
                border: 1px solid #48486A;
            }
            QLabel { font-size: 12px; color: #A8A8C8; }
            QSlider::groove:horizontal {
                height: 3px; background: #36365A; border-radius: 1px;
            }
            QSlider::handle:horizontal {
                background: #E8A87C; width: 12px; height: 12px;
                margin: -5px 0; border-radius: 6px;
            }
            QSlider::sub-page:horizontal {
                background: #E8A87C; border-radius: 1px;
            }
            QCheckBox {
                color: #C8C8E0; font-size: 12px; spacing: 6px;
            }
            QCheckBox::indicator {
                width: 14px; height: 14px; border-radius: 3px;
                border: 1px solid #48486A; background: #36365A;
            }
            QCheckBox::indicator:checked {
                background: #E8A87C; border-color: #E8A87C;
            }
            QSpinBox {
                background-color: #36365A; color: #E0E0F0;
                border: 1px solid #48486A; border-radius: 4px;
                padding: 2px 4px; font-size: 12px;
                min-height: 22px;
            }
        """)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")

        inner = QWidget()
        inner.setStyleSheet("background: transparent;")
        layout = QVBoxLayout(inner)
        layout.setContentsMargins(8, 4, 8, 4)
        layout.setSpacing(4)

        title = QLabel("⚙ Cài đặt")
        title.setStyleSheet("font-size: 14px; font-weight: bold; color: #E0E0F0; padding: 4px 0;")
        layout.addWidget(title)

        self._build_voice_section(layout)
        self._build_audio_section(layout)

        layout.addStretch()
        scroll.setWidget(inner)

        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.addWidget(scroll)

    def _build_voice_section(self, parent):
        gb = QGroupBox("Giọng nói")
        gl = QVBoxLayout(gb)
        gl.setSpacing(6)

        gl.addWidget(QLabel("Engine TTS"))
        self.engine_combo = QComboBox()
        self.engine_combo.addItem("VieNeu-TTS")
        self.engine_combo.setEnabled(False)
        gl.addWidget(self.engine_combo)

        gl.addWidget(QLabel("Giọng đọc"))
        self.voice_combo = QComboBox()
        self.voice_combo.setPlaceholderText("Đang tải...")
        self.voice_combo.currentIndexChanged.connect(self._on_voice_changed)
        gl.addWidget(self.voice_combo)

        gl.addWidget(QLabel("Phong cách"))
        self.style_combo = QComboBox()
        self.style_combo.addItems(["Tự nhiên", "Tin tức", "Kể chuyện"])
        self.style_combo.currentIndexChanged.connect(self._on_style_changed)
        gl.addWidget(self.style_combo)

        parent.addWidget(gb)

    def _build_audio_section(self, parent):
        gb = QGroupBox("Tinh chỉnh âm thanh")
        gl = QVBoxLayout(gb)
        gl.setSpacing(6)

        gl.addWidget(QLabel("Nhiệt độ (Temperature)"))
        h = QHBoxLayout()
        self.temp_slider = QSlider(Qt.Orientation.Horizontal)
        self.temp_slider.setRange(0, 150)
        self.temp_slider.setValue(80)
        self.temp_label = QLabel("0.8")
        self.temp_label.setFixedWidth(30)
        h.addWidget(self.temp_slider)
        h.addWidget(self.temp_label)
        gl.addLayout(h)
        self.temp_slider.valueChanged.connect(lambda v: self._on_param_int('temperature', v, 100))

        gl.addWidget(QLabel("Top K"))
        self.topk_spin = QSpinBox()
        self.topk_spin.setRange(1, 100)
        self.topk_spin.setValue(25)
        self.topk_spin.valueChanged.connect(lambda v: self._emit_param('top_k', v))
        gl.addWidget(self.topk_spin)

        gl.addWidget(QLabel("Ngăn lặp từ (Repetition Penalty)"))
        h = QHBoxLayout()
        self.rep_slider = QSlider(Qt.Orientation.Horizontal)
        self.rep_slider.setRange(100, 200)
        self.rep_slider.setValue(120)
        self.rep_label = QLabel("1.2")
        self.rep_label.setFixedWidth(30)
        h.addWidget(self.rep_slider)
        h.addWidget(self.rep_label)
        gl.addLayout(h)
        self.rep_slider.valueChanged.connect(lambda v: self._on_param_int('repetition_penalty', v, 100))

        gl.addWidget(QLabel("Im lặng (Silence)"))
        h = QHBoxLayout()
        self.silence_slider = QSlider(Qt.Orientation.Horizontal)
        self.silence_slider.setRange(0, 50)
        self.silence_slider.setValue(15)
        self.silence_label = QLabel("0.15")
        self.silence_label.setFixedWidth(30)
        h.addWidget(self.silence_slider)
        h.addWidget(self.silence_label)
        gl.addLayout(h)
        self.silence_slider.valueChanged.connect(lambda v: self._on_param_int('silence_p', v, 100))

        self.denoise_cb = QCheckBox("Khử nhiễu (Denoise)")
        self.denoise_cb.setChecked(True)
        self.denoise_cb.toggled.connect(lambda v: self._emit_param('denoise', v))
        gl.addWidget(self.denoise_cb)

        parent.addWidget(gb)

    def _on_param_int(self, key, value, divisor):
        actual = value / divisor
        label_map = {
            'temperature': self.temp_label,
            'repetition_penalty': self.rep_label,
            'silence_p': self.silence_label,
        }
        if key in label_map:
            label_map[key].setText(f"{actual:.2f}")
        self._emit_param(key, actual)

    def _emit_param(self, key, value):
        self.param_changed.emit(key, value)

    def _on_voice_changed(self, idx):
        if idx >= 0:
            voice_id = self.voice_combo.itemData(idx)
            if voice_id:
                self.voice_changed.emit(voice_id)

    def _on_style_changed(self, idx):
        styles = ['tu_nhien', 'tin_tuc', 'ke_chuyen']
        if 0 <= idx < len(styles):
            self.style_changed.emit(styles[idx])

    def populate_voices(self, voices):
        self.voice_combo.blockSignals(True)
        self.voice_combo.clear()
        for desc, vid in voices:
            self.voice_combo.addItem(desc.split('—')[0].strip(), vid)
        self.voice_combo.blockSignals(False)
        if self.voice_combo.count() > 0:
            self.voice_combo.setCurrentIndex(0)

    def set_style(self, style):
        styles = ['tu_nhien', 'tin_tuc', 'ke_chuyen']
        if style in styles:
            self.style_combo.setCurrentIndex(styles.index(style))
