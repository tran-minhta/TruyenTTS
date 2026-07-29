from PyQt6.QtWidgets import QTreeWidget, QTreeWidgetItem, QLabel, QVBoxLayout, QWidget, QFrame
from PyQt6.QtCore import pyqtSignal, Qt


class ChapterPanel(QWidget):
    chapter_selected = pyqtSignal(int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._chapters = []
        self._setup_ui()

    def _setup_ui(self):
        self.setStyleSheet("""
            ChapterPanel {
                background: #FFFFFF; border-right: 1px solid #E5E7EB;
            }
            QLabel#title {
                color: #2563EB; font-size: 11px; font-weight: bold;
                padding: 12px 12px 4px; text-transform: uppercase;
            }
            QTreeWidget {
                background: transparent; color: #4B5563;
                font-size: 13px; border: none; padding: 4px;
            }
            QTreeWidget::item {
                padding: 8px 12px; border-radius: 6px; margin: 1px 4px;
            }
            QTreeWidget::item:selected {
                background: #EFF6FF; color: #2563EB; font-weight: bold;
            }
            QTreeWidget::item:hover {
                background: #F9FAFB; color: #2563EB;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        title = QLabel("MỤC LỤC")
        title.setObjectName("title")
        layout.addWidget(title)

        self.tree = QTreeWidget()
        self.tree.setHeaderHidden(True)
        self.tree.setRootIsDecorated(False)
        self.tree.setIndentation(12)
        self.tree.setFrameShape(QFrame.Shape.NoFrame)
        self.tree.itemClicked.connect(self._on_item_clicked)
        layout.addWidget(self.tree)

    def set_chapters(self, chapters):
        self.tree.clear()
        self._chapters = [(title, sentences) for title, sentences in chapters]
        for i, (title, sentences) in enumerate(self._chapters):
            display = title if len(title) < 45 else title[:42] + "..."
            item = QTreeWidgetItem([display])
            item.setData(0, Qt.ItemDataRole.UserRole, i)
            sc = sentences.count('.') + sentences.count('!') + sentences.count('?')
            item.setToolTip(0, f"{title}\n{sc} câu")
            self.tree.addTopLevelItem(item)

    def select_chapter(self, index):
        if 0 <= index < self.tree.topLevelItemCount():
            self.tree.setCurrentItem(self.tree.topLevelItem(index))

    def _on_item_clicked(self, item, column):
        index = item.data(0, Qt.ItemDataRole.UserRole)
        if index is not None:
            self.chapter_selected.emit(index)

    def get_chapter_count(self):
        return len(self._chapters)
