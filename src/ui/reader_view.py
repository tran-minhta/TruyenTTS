import html as html_mod
from PyQt6.QtWidgets import QTextBrowser
from PyQt6.QtCore import Qt, pyqtSignal


class ReaderView(QTextBrowser):
    sentence_clicked = pyqtSignal(int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setReadOnly(True)
        self.setOpenExternalLinks(False)
        self.sentences = []
        self.chapter_title = ""
        self._active_index = -1
        self.setStyleSheet("""
            QTextBrowser {
                background-color: #FDF5E6;
                color: #333;
                font-size: 16px;
                padding: 20px;
                border: none;
            }
        """)

    def set_content(self, chapter_title, sentences, active_index=-1):
        self.chapter_title = chapter_title
        self.sentences = sentences
        self._active_index = active_index if 0 <= active_index < len(sentences) else -1
        self._render()

    def set_active_sentence(self, index):
        if not self.sentences:
            return
        idx = max(0, min(index, len(self.sentences) - 1))
        if idx == self._active_index:
            return
        self._active_index = idx
        self._render()
        self.scrollToAnchor(f"s{idx}")

    def clear_content(self):
        self.sentences = []
        self._active_index = -1
        self.clear()

    def _render(self):
        parts = [f'<html><body style="font-family:serif;font-size:16px;line-height:1.8;color:#333;">']
        if self.chapter_title:
            parts.append(f'<h2 style="color:#8B4513;text-align:center;">{html_mod.escape(self.chapter_title)}</h2>')
        for i, sent in enumerate(self.sentences):
            escaped = html_mod.escape(sent)
            if i == self._active_index:
                parts.append(
                    f'<span id="s{i}" '
                    f'style="background-color:#FFE082;padding:2px 4px;border-radius:3px;">'
                    f'{escaped}</span> '
                )
            else:
                parts.append(
                    f'<span id="s{i}" '
                    f'style="cursor:pointer;">'
                    f'{escaped}</span> '
                )
        parts.append('</body></html>')
        self.setHtml(''.join(parts))

    def mousePressEvent(self, event):
        super().mousePressEvent(event)
        cursor = self.cursorForPosition(event.pos())
        cursor_pos = cursor.position()
        if cursor_pos < 0 or not self.sentences:
            return
        text_before = self.toPlainText()[:cursor_pos]
        approx_index = text_before.count('.') + text_before.count('!') + text_before.count('?')
        approx_index = min(approx_index, len(self.sentences) - 1)
        for i, sent in enumerate(self.sentences):
            pos_in_doc = self._find_sentence_position(i)
            if pos_in_doc is not None and abs(cursor_pos - pos_in_doc) < 200:
                self.sentence_clicked.emit(i)
                return
        self.sentence_clicked.emit(approx_index)

    def _find_sentence_position(self, index):
        text = self.toPlainText()
        pos = 0
        for i, sent in enumerate(self.sentences):
            found = text.find(sent, pos)
            if found == -1:
                return None
            if i == index:
                return found
            pos = found + len(sent)
        return None

    def get_active_sentence(self):
        return self._active_index
