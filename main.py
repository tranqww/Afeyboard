"""Afeyboard entry point."""
import sys

from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import QApplication

from app.config import APP_NAME
from app.ui.main_window import MainWindow


def main() -> int:
    app = QApplication(sys.argv)
    app.setApplicationName(APP_NAME)
    app.setQuitOnLastWindowClosed(False)
    app.setFont(QFont("Segoe UI", 9))

    window = MainWindow()
    if not window.should_start_minimized():
        window.show()

    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
