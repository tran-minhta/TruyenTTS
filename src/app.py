import sys
from PyQt6.QtWidgets import QApplication
from src.main_window import MainWindow


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("Truyện TTS")
    app.setOrganizationName("truyen-tts")
    window = MainWindow()
    window.show()

    if len(sys.argv) > 1:
        path = sys.argv[1]
        if path.endswith('.txt') or path.endswith('.epub'):
            window._load_file(path)

    sys.exit(app.exec())
