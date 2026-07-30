"""Placeholder main window (fleshed out in a later checklist step)."""
from PyQt6.QtWidgets import QLabel, QMainWindow

from app.config import APP_NAME


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle(APP_NAME)
        self.resize(900, 600)
        self.setCentralWidget(QLabel(f"{APP_NAME} — initializing..."))
