"""Left navigation sidebar."""
from __future__ import annotations

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import QButtonGroup, QLabel, QPushButton, QVBoxLayout, QWidget

from app import APP_NAME, APP_VERSION

NAV_ITEMS = ("Mouse Clicker", "Keyboard Clicker", "Settings && Hotkeys")


class Sidebar(QWidget):
    page_selected = pyqtSignal(int)

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("Sidebar")
        self.setFixedWidth(220)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        logo = QLabel(APP_NAME)
        logo.setObjectName("LogoLabel")
        sub = QLabel("AUTO CLICKER SUITE")
        sub.setObjectName("LogoSubLabel")
        layout.addWidget(logo)
        layout.addWidget(sub)

        self._group = QButtonGroup(self)
        self._group.setExclusive(True)

        for index, name in enumerate(NAV_ITEMS):
            btn = QPushButton(name)
            btn.setObjectName("NavButton")
            btn.setCheckable(True)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            self._group.addButton(btn, index)
            layout.addWidget(btn)

        self._group.idClicked.connect(self.page_selected.emit)
        self._group.buttons()[0].setChecked(True)

        layout.addStretch(1)

        version = QLabel(f"v{APP_VERSION}")
        version.setObjectName("LogoSubLabel")
        version.setAlignment(Qt.AlignmentFlag.AlignLeft)
        layout.addWidget(version)

    def select_page(self, index: int) -> None:
        button = self._group.button(index)
        if button is not None:
            button.setChecked(True)
