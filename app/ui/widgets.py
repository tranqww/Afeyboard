"""Small reusable widgets shared across pages."""
from __future__ import annotations

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QKeySequence
from PyQt6.QtWidgets import QHBoxLayout, QLabel, QLineEdit, QVBoxLayout, QWidget

from app.config import STATUS_COLORS, ClickerStatus

_MODIFIER_ONLY_KEYS = {
    Qt.Key.Key_Control,
    Qt.Key.Key_Shift,
    Qt.Key.Key_Alt,
    Qt.Key.Key_Meta,
    Qt.Key.Key_AltGr,
}


class KeyCaptureEdit(QLineEdit):
    """Read-only field that captures the next key press (with modifiers) as text."""

    key_captured = pyqtSignal(str)

    def __init__(self, default: str = "", parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setReadOnly(True)
        self.setPlaceholderText("Click here, then press a key…")
        self._value = ""
        if default:
            self.set_value(default)

    def set_value(self, text: str) -> None:
        self._value = text
        self.setText(text)

    def value(self) -> str:
        return self._value

    def keyPressEvent(self, event) -> None:  # noqa: N802 (Qt override)
        key = event.key()
        if key in _MODIFIER_ONLY_KEYS:
            return
        if key == Qt.Key.Key_Escape:
            return
        combo = event.keyCombination()
        text = QKeySequence(combo).toString(QKeySequence.SequenceFormat.PortableText)
        if not text:
            return
        self.set_value(text)
        self.key_captured.emit(text)


class StatusIndicator(QWidget):
    """Colored dot + text label showing Idle / Running / Paused."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(6, 0, 10, 0)
        layout.setSpacing(8)

        self._dot = QLabel()
        self._dot.setFixedSize(10, 10)

        self._label = QLabel()
        self._label.setStyleSheet("font-weight: 600;")

        layout.addWidget(self._dot)
        layout.addWidget(self._label)

        self._status = ClickerStatus.IDLE
        self.set_status(ClickerStatus.IDLE)

    def set_status(self, status: ClickerStatus) -> None:
        self._status = status
        color = STATUS_COLORS[status]
        self._dot.setStyleSheet(
            f"background-color: {color}; border-radius: 5px;"
        )
        self._label.setText(status.value)
        self._label.setStyleSheet(f"font-weight: 600; color: {color};")

    def status(self) -> ClickerStatus:
        return self._status


class PageHeader(QWidget):
    """Title + subtitle shown at the top of each page."""

    def __init__(self, title: str, subtitle: str, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("PageHeader")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 4)
        layout.setSpacing(2)

        title_label = QLabel(title)
        title_label.setObjectName("PageTitle")
        subtitle_label = QLabel(subtitle)
        subtitle_label.setObjectName("PageSubtitle")

        layout.addWidget(title_label)
        layout.addWidget(subtitle_label)
