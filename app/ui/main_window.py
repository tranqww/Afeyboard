"""Main application window: sidebar navigation + stacked pages + status bar."""
from __future__ import annotations

from PyQt6.QtWidgets import QHBoxLayout, QMainWindow, QStackedWidget, QWidget

from app import APP_NAME
from app.config import ClickerStatus
from app.ui.pages.keyboard_page import KeyboardPage
from app.ui.pages.mouse_page import MousePage
from app.ui.pages.settings_page import SettingsPage
from app.ui.sidebar import Sidebar
from app.ui.style import STYLESHEET
from app.ui.widgets import StatusIndicator


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle(APP_NAME)
        self.resize(980, 660)
        self.setMinimumSize(860, 560)
        self.setStyleSheet(STYLESHEET)

        central = QWidget()
        central.setObjectName("Root")
        self.setCentralWidget(central)

        layout = QHBoxLayout(central)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self.sidebar = Sidebar()
        layout.addWidget(self.sidebar)

        self.mouse_page = MousePage()
        self.keyboard_page = KeyboardPage()
        self.settings_page = SettingsPage()

        self.stack = QStackedWidget()
        self.stack.addWidget(self.mouse_page)
        self.stack.addWidget(self.keyboard_page)
        self.stack.addWidget(self.settings_page)
        layout.addWidget(self.stack, 1)

        self.sidebar.page_selected.connect(self.stack.setCurrentIndex)

        self._build_status_bar()

    def _build_status_bar(self) -> None:
        bar = self.statusBar()
        self.global_status_indicator = StatusIndicator()
        self.global_status_indicator.set_status(ClickerStatus.IDLE)
        bar.addPermanentWidget(self.global_status_indicator)
        bar.showMessage(f"{APP_NAME} ready.")
