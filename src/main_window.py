import os
import threading
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout,
    QSplitter, QDockWidget, QFileDialog, QMessageBox,
    QMenuBar, QMenu, QStatusBar, QLabel,
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QAction, QKeySequence

from src.ui.reader_view import ReaderView
from src.ui.controls_bar import ControlsBar
from src.ui.chapter_panel import ChapterPanel
from src.ui.settings_panel import SettingsPanel
from src.tts.vieneu_engine import VieNeuEngine
from src.tts.audio_player import AudioPlayer
from src.tts.manager import TTSManager
from src.reader.text_loader import load_file
from src.reader.text_splitter import split_sentences
from src.reader.bookmark_manager import (
    load_bookmarks, add_bookmark,
    load_config, save_config,
)


APP_CSS = """
QMainWindow { background-color: #1A1A2E; }
QMenuBar {
    background: #1E1E36; color: #B0B0D0; border-bottom: 1px solid #36365A;
    padding: 2px 0; font-size: 13px;
}
QMenuBar::item { padding: 6px 12px; border-radius: 4px; }
QMenuBar::item:selected { background: #36365A; color: #E8A87C; }
QMenu {
    background: #252542; color: #C8C8E0; border: 1px solid #36365A;
    border-radius: 6px; padding: 4px;
}
QMenu::item { padding: 8px 24px; border-radius: 4px; }
QMenu::item:selected { background: #E8A87C; color: #1A1A2E; }
QMenu::separator { height: 1px; background: #36365A; margin: 4px 8px; }
QStatusBar {
    background: #1E1E36; color: #8888A8; font-size: 11px;
    border-top: 1px solid #36365A; padding: 2px 8px;
}
QStatusBar::item { border: none; }
QSplitter::handle { background: #36365A; width: 1px; }
QDockWidget {
    color: #C8C8E0; titlebar-close-icon: none;
    font-size: 12px; border: none;
}
QDockWidget::title {
    background: #1E1E36; padding: 8px; text-align: center;
    border-bottom: 1px solid #36365A;
}
"""


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Truyện TTS")
        self.setMinimumSize(1100, 750)
        self.setStyleSheet(APP_CSS)

        self.current_file = None
        self.chapters = []
        self.current_chapter = 0
        self.current_sentence = 0
        self.all_sentences_flat = []
        self.chapter_sentence_offsets = []
        self._play_state = 'stopped'

        self._init_ui()
        self._setup_shortcuts()
        self._init_engine()
        self._restore_session()

        self._loading_timer = QTimer()
        self._loading_timer.timeout.connect(self._check_engine_loaded)
        self._loading_timer.start(100)

    def _init_engine(self):
        self.engine = VieNeuEngine()
        self.player = AudioPlayer()
        self.tts_manager = TTSManager(self.engine, self.player)
        self.engine_loaded = False

        self.tts_manager.sentence_started.connect(self._on_sentence_started)
        self.tts_manager.sentence_finished.connect(self._on_sentence_finished)
        self.tts_manager.all_done.connect(self._on_all_done)
        self.tts_manager.status_message.connect(self._on_status_message)
        self.tts_manager.error_occurred.connect(self._on_error)

        self._start_engine_loading()

    def _start_engine_loading(self):
        self.status_label.setText("Đang tải model TTS...")
        thread = threading.Thread(target=self._load_engine, daemon=True)
        thread.start()

    def _load_engine(self):
        try:
            self.engine.initialize(
                status_callback=lambda msg: self.status_label.setText(msg)
            )
            self.engine_loaded = True
        except Exception as e:
            self._on_error(f"Không thể tải model TTS: {e}")

    def _check_engine_loaded(self):
        if self.engine_loaded:
            self._loading_timer.stop()
            self.status_label.setText("Sẵn sàng")
            self._populate_settings()

    def _populate_settings(self):
        voices = self.engine.get_voices()
        self.settings_panel.populate_voices(voices)

    def _init_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.setHandleWidth(1)

        self.chapter_panel = ChapterPanel()
        self.chapter_panel.setFixedWidth(220)
        self.chapter_panel.chapter_selected.connect(self._on_chapter_selected)

        self.reader_view = ReaderView()
        self.reader_view.sentence_clicked.connect(self._on_sentence_clicked)

        splitter.addWidget(self.chapter_panel)
        splitter.addWidget(self.reader_view)
        splitter.setStretchFactor(0, 0)
        splitter.setStretchFactor(1, 1)

        self.controls_bar = ControlsBar()
        self.controls_bar.play_pause_clicked.connect(self._on_play_pause)
        self.controls_bar.stop_clicked.connect(self._on_stop)
        self.controls_bar.prev_sentence_clicked.connect(self._on_prev_sentence)
        self.controls_bar.next_sentence_clicked.connect(self._on_next_sentence)
        self.controls_bar.prev_chapter_clicked.connect(self._on_prev_chapter)
        self.controls_bar.next_chapter_clicked.connect(self._on_next_chapter)

        main_layout.addWidget(splitter)
        main_layout.addWidget(self.controls_bar)

        self.settings_panel = SettingsPanel()
        self.settings_panel.voice_changed.connect(self._on_voice_changed)
        self.settings_panel.style_changed.connect(self._on_style_changed)
        self.settings_panel.param_changed.connect(self._on_param_changed)

        dock = QDockWidget("Cài đặt", self)
        dock.setWidget(self.settings_panel)
        dock.setFeatures(QDockWidget.DockWidgetFeature.NoDockWidgetFeatures)
        dock.setFixedWidth(240)
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, dock)

        self._setup_menu()

        self.status_label = QLabel("Sẵn sàng")
        self.statusBar().addWidget(self.status_label, 1)

    def _setup_menu(self):
        mb = self.menuBar()

        fm = mb.addMenu("Tập tin")
        a = QAction("📂 Mở tập tin...", self)
        a.setShortcut(QKeySequence("Ctrl+O"))
        a.triggered.connect(self._on_open_file)
        fm.addAction(a)
        a = QAction("📥 Xuất audio...", self)
        a.setShortcut(QKeySequence("Ctrl+E"))
        a.triggered.connect(self._on_export_audio)
        fm.addAction(a)
        fm.addSeparator()
        a = QAction("Thoát", self)
        a.setShortcut(QKeySequence("Ctrl+Q"))
        a.triggered.connect(self.close)
        fm.addAction(a)

        nm = mb.addMenu("Điều hướng")
        a = QAction("Câu sau", self)
        a.setShortcut(QKeySequence(Qt.Key.Key_Right))
        a.triggered.connect(self._on_next_sentence)
        nm.addAction(a)
        a = QAction("Câu trước", self)
        a.setShortcut(QKeySequence(Qt.Key.Key_Left))
        a.triggered.connect(self._on_prev_sentence)
        nm.addAction(a)

        bm = mb.addMenu("Bookmark")
        a = QAction("➕ Thêm bookmark", self)
        a.setShortcut(QKeySequence("Ctrl+B"))
        a.triggered.connect(self._on_add_bookmark)
        bm.addAction(a)
        a = QAction("📋 Danh sách", self)
        a.setShortcut(QKeySequence("Ctrl+L"))
        a.triggered.connect(self._on_list_bookmarks)
        bm.addAction(a)

    def _setup_shortcuts(self):
        a = QAction("Play/Pause", self)
        a.triggered.connect(self._on_play_pause)
        a.setShortcut(QKeySequence(Qt.Key.Key_Space))
        self.addAction(a)

    def _on_open_file(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Mở tập tin truyện", "",
            "Hỗ trợ (*.txt *.epub);;Text (*.txt);;EPUB (*.epub);;Tất cả (*)"
        )
        if not path:
            return
        self.tts_manager.stop()
        self.controls_bar.set_playing(False)
        self._play_state = 'stopped'
        self._load_file(path)

    def _load_file(self, path):
        try:
            chapters_raw = load_file(path)
        except Exception as e:
            QMessageBox.critical(self, "Lỗi", f"Không thể đọc file:\n{e}")
            return

        self.current_file = path
        self.chapters = []
        self.all_sentences_flat = []
        self.chapter_sentence_offsets = []

        for title, text in chapters_raw:
            sents = split_sentences(text)
            self.chapters.append((title, sents))
            offset = len(self.all_sentences_flat)
            self.chapter_sentence_offsets.append(offset)
            self.all_sentences_flat.extend(sents)

        chapter_titles = [(title, sents) for title, sents in chapters_raw]
        self.chapter_panel.set_chapters(chapter_titles)

        self.current_chapter = 0
        self.current_sentence = 0
        self._show_chapter(0, 0)
        self.setWindowTitle(f"Truyện TTS - {os.path.basename(path)}")
        self.status_label.setText(
            f"📖 {len(self.chapters)} chương · {len(self.all_sentences_flat)} câu"
        )

    def _show_chapter(self, chapter_index, sentence_index=0):
        if not self.chapters:
            return
        chapter_index = max(0, min(chapter_index, len(self.chapters) - 1))
        title, sents = self.chapters[chapter_index]
        sentence_index = max(0, min(sentence_index, len(sents) - 1))
        self.reader_view.set_content(title, sents, sentence_index)
        self.chapter_panel.select_chapter(chapter_index)
        self.current_chapter = chapter_index
        self.current_sentence = sentence_index
        global_idx = self.chapter_sentence_offsets[chapter_index] + sentence_index
        self.controls_bar.set_position(global_idx, len(self.all_sentences_flat))

    def _on_chapter_selected(self, index):
        self.tts_manager.stop()
        self.controls_bar.set_playing(False)
        self._play_state = 'stopped'
        self._show_chapter(index, 0)

    def _on_sentence_clicked(self, index):
        global_idx = self.chapter_sentence_offsets[self.current_chapter] + index
        self.tts_manager.skip_to(global_idx)

    def _on_play_pause(self):
        if not self.all_sentences_flat:
            return
        if not self.engine_loaded:
            self.status_label.setText("Đợi model TTS tải xong...")
            return
        if self._play_state == 'playing':
            self.tts_manager.pause()
            self.controls_bar.set_playing(False)
            self._play_state = 'paused'
        elif self._play_state == 'paused':
            self.tts_manager.resume()
            self.controls_bar.set_playing(True)
            self._play_state = 'playing'
        else:
            g = self.chapter_sentence_offsets[self.current_chapter] + self.current_sentence
            self.tts_manager.start(self.all_sentences_flat, g)
            self.controls_bar.set_playing(True)
            self._play_state = 'playing'

    def _on_stop(self):
        self.tts_manager.stop()
        self.controls_bar.set_playing(False)
        self._play_state = 'stopped'
        self.status_label.setText("Đã dừng")

    def _on_prev_sentence(self):
        if not self.chapters:
            return
        self.tts_manager.stop()
        self.controls_bar.set_playing(False)
        self._play_state = 'stopped'
        if self.current_sentence > 0:
            self._show_chapter(self.current_chapter, self.current_sentence - 1)
        elif self.current_chapter > 0:
            prev = self.chapters[self.current_chapter - 1][1]
            self._show_chapter(self.current_chapter - 1, len(prev) - 1)

    def _on_next_sentence(self):
        if not self.chapters:
            return
        self.tts_manager.stop()
        self.controls_bar.set_playing(False)
        self._play_state = 'stopped'
        title, sents = self.chapters[self.current_chapter]
        if self.current_sentence < len(sents) - 1:
            self._show_chapter(self.current_chapter, self.current_sentence + 1)
        elif self.current_chapter < len(self.chapters) - 1:
            self._show_chapter(self.current_chapter + 1, 0)

    def _on_prev_chapter(self):
        if self.current_chapter > 0:
            self.tts_manager.stop()
            self.controls_bar.set_playing(False)
            self._play_state = 'stopped'
            self._show_chapter(self.current_chapter - 1, 0)

    def _on_next_chapter(self):
        if self.current_chapter < len(self.chapters) - 1:
            self.tts_manager.stop()
            self.controls_bar.set_playing(False)
            self._play_state = 'stopped'
            self._show_chapter(self.current_chapter + 1, 0)

    def _on_voice_changed(self, voice_id):
        self.engine.set_voice(voice_id)
        self.status_label.setText(f"Giọng: {voice_id}")

    def _on_style_changed(self, style):
        self.engine.set_style(style)
        style_names = {'tu_nhien': 'tự nhiên', 'tin_tuc': 'tin tức', 'ke_chuyen': 'kể chuyện'}
        self.status_label.setText(f"Phong cách: {style_names.get(style, style)}")

    def _on_param_changed(self, key, value):
        self.engine.set_parameter(key, value)

    def _on_sentence_started(self, global_idx):
        ch, sent = self._global_to_local(global_idx)
        if ch != self.current_chapter:
            self._show_chapter(ch, sent)
        else:
            self.reader_view.set_active_sentence(sent)
            self.current_sentence = sent
            self.current_chapter = ch
            self.controls_bar.set_position(global_idx, len(self.all_sentences_flat))

    def _on_sentence_finished(self, global_idx):
        pass

    def _on_all_done(self):
        self.controls_bar.set_playing(False)
        self._play_state = 'stopped'
        self.status_label.setText("✅ Đã đọc xong!")

    def _on_status_message(self, msg):
        self.status_label.setText(msg)

    def _on_error(self, msg):
        self.status_label.setText(f"❌ {msg}")

    def _global_to_local(self, global_idx):
        for ch in range(len(self.chapter_sentence_offsets) - 1, -1, -1):
            if global_idx >= self.chapter_sentence_offsets[ch]:
                s = global_idx - self.chapter_sentence_offsets[ch]
                if ch < len(self.chapters) and s < len(self.chapters[ch][1]):
                    return ch, s
        return 0, 0

    def _on_add_bookmark(self):
        if not self.current_file or not self.chapters:
            return
        title, sents = self.chapters[self.current_chapter]
        preview = sents[self.current_sentence] if self.current_sentence < len(sents) else ""
        add_bookmark(self.current_file, self.current_chapter,
                     self.current_sentence, title, preview)
        self.status_label.setText("✅ Đã thêm bookmark")

    def _on_list_bookmarks(self):
        bookmarks = load_bookmarks()
        if not bookmarks:
            QMessageBox.information(self, "Bookmark", "Chưa có bookmark nào.")
            return
        lines = [f"{i+1}. [{os.path.basename(bm.get('file_path',''))}] {bm.get('text_preview','')}"
                 for i, bm in enumerate(bookmarks)]
        QMessageBox.information(self, "Bookmark", "\n".join(lines))

    def _on_export_audio(self):
        if not self.all_sentences_flat:
            QMessageBox.warning(self, "Xuất audio", "Chưa có nội dung.")
            return
        dir_path = QFileDialog.getExistingDirectory(self, "Chọn thư mục xuất")
        if not dir_path:
            return
        self.tts_manager.stop()
        self.controls_bar.set_playing(False)
        self._play_state = 'stopped'
        self.status_label.setText("Đang xuất audio...")
        threading.Thread(target=self._export_audio_thread,
                         args=(dir_path,), daemon=True).start()

    def _export_audio_thread(self, dir_path):
        try:
            import soundfile as sf
        except ImportError:
            self._on_error("Cần: pip install soundfile")
            return
        for ch_idx, (title, sents) in enumerate(self.chapters):
            chunks = []
            for i, sent in enumerate(sents):
                try:
                    audio, sr = self.engine.generate(sent)
                    chunks.append(audio)
                except Exception as e:
                    self._on_error(f"Lỗi câu {i} ch.{ch_idx}: {e}")
                    continue
                if i % 10 == 0:
                    self._on_status_message(
                        f"Xuất ch.{ch_idx+1}/{len(self.chapters)}: {i}/{len(sents)}")
            if chunks:
                import numpy as np
                combined = np.concatenate(chunks)
                safe = "".join(c for c in title if c.isalnum() or c in ' _-')[:40]
                sf.write(os.path.join(dir_path, f"chuong_{ch_idx+1}_{safe}.wav"),
                         combined, 24000)
        self._on_status_message(f"✅ Đã xuất {len(self.chapters)} file WAV")

    def _restore_session(self):
        try:
            cfg = load_config()
            last = cfg.get('last_file')
            if last and os.path.exists(last):
                self._load_file(last)
        except Exception:
            pass

    def _save_session(self):
        if self.current_file:
            save_config({'last_file': self.current_file})

    def closeEvent(self, event):
        self._save_session()
        self.tts_manager.stop()
        self.player.close()
        self.engine.close()
        event.accept()
