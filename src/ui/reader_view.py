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
        self._last_html = ""

    def set_content(self, chapter_title, sentences, active_index=-1):
        self.chapter_title = chapter_title
        self.sentences = sentences
        self._active_index = active_index if 0 <= active_index < len(sentences) else -1
        self._active_index = -1
        self._render()
        if active_index >= 0:
            self._active_index = active_index
            self._render()
            self.scrollToAnchor(f"s{active_index}")

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
        parts = ['<html><body style="font-family:Georgia,serif;font-size:17px;line-height:1.9;color:#2D2424;">']
        if self.chapter_title:
            parts.append(
                f'<h2 style="color:#8B6914;text-align:center;font-weight:normal;'
                f'font-size:22px;margin-bottom:20px;border-bottom:1px solid #E8D5B5;'
                f'padding-bottom:12px;">{html_mod.escape(self.chapter_title)}</h2>'
            )
        for i, sent in enumerate(self.sentences):
            escaped = html_mod.escape(sent)
            if i == self._active_index:
                parts.append(
                    f'<span id="s{i}" style="background-color:#FFE082;'
                    f'padding:2px 6px;border-radius:4px;'
                    f'transition:background-color 0.3s;">{escaped}</span> '
                )
            else:
                parts.append(
                    f'<span id="s{i}" style="cursor:pointer;">{escaped}</span> '
                )
        parts.append('</body></html>')
        html = ''.join(parts)
        if html != self._last_html:
            self._last_html = html
            self.setHtml(html)

    def mousePressEvent(self, event):
        super().mousePressEvent(event)
        cursor = self.cursorForPosition(event.pos())
        cursor_pos = cursor.position()
        if cursor_pos < 0 or not self.sentences:
            return
        text_before = self.toPlainText()[:cursor_pos]
        approx = (text_before.count('.') + text_before.count('!') +
                  text_before.count('?'))
        approx = min(approx, len(self.sentences) - 1)
        for i in range(len(self.sentences)):
            pos = self._sentence_pos(i)
            if pos is not None and abs(cursor_pos - pos) < 200:
                self.sentence_clicked.emit(i)
                return
        self.sentence_clicked.emit(approx)

    def _sentence_pos(self, index):
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
