from PyQt6.QtWidgets import QTreeWidget, QTreeWidgetItem
from PyQt6.QtCore import pyqtSignal, Qt


class ChapterPanel(QTreeWidget):
    chapter_selected = pyqtSignal(int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setHeaderHidden(True)
        self.setRootIsDecorated(False)
        self.setIndentation(12)
        self._chapters = []
        self.setStyleSheet("""
            QTreeWidget {
                background-color: #2C2C2C;
                color: #DDD;
                font-size: 13px;
                border: none;
                padding: 4px;
            }
            QTreeWidget::item {
                padding: 6px 8px;
                border-radius: 4px;
            }
            QTreeWidget::item:selected {
                background-color: #FFB300;
                color: #1A1A1A;
            }
            QTreeWidget::item:hover {
                background-color: #3A3A3A;
            }
        """)
        self.itemClicked.connect(self._on_item_clicked)

    def set_chapters(self, chapters):
        self.clear()
        self._chapters = [(title, sentences) for title, sentences in chapters]
        for i, (title, sentences) in enumerate(self._chapters):
            display = title if len(title) < 50 else title[:47] + "..."
            item = QTreeWidgetItem([display])
            item.setData(0, Qt.ItemDataRole.UserRole, i)
            item.setToolTip(0, f"{title}\n{sentences.count('.') + sentences.count('!') + sentences.count('?')} câu")
            self.addTopLevelItem(item)

    def select_chapter(self, index):
        if 0 <= index < self.topLevelItemCount():
            self.setCurrentItem(self.topLevelItem(index))

    def _on_item_clicked(self, item, column):
        index = item.data(0, Qt.ItemDataRole.UserRole)
        if index is not None:
            self.chapter_selected.emit(index)

    def get_chapter_count(self):
        return len(self._chapters)
