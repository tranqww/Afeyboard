"""Keyboard Clicker page — UI layout only; wired to worker/thread logic separately."""
from __future__ import annotations

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDoubleSpinBox,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QPlainTextEdit,
    QPushButton,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from app.config import KeyboardMode
from app.ui.widgets import KeyCaptureEdit, PageHeader, StatusIndicator


class KeyboardPage(QWidget):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)

        root = QVBoxLayout(self)
        root.setContentsMargins(28, 24, 28, 20)
        root.setSpacing(14)

        root.addWidget(
            PageHeader(
                "Keyboard Clicker",
                "Spam a key, hold it down, or loop-type a macro sequence.",
            )
        )

        mode_row = QHBoxLayout()
        mode_row.addWidget(QLabel("Mode:"))
        self.mode_combo = QComboBox()
        for mode in KeyboardMode:
            self.mode_combo.addItem(mode.value, mode)
        mode_row.addWidget(self.mode_combo, 1)
        root.addLayout(mode_row)

        self.mode_stack = QStackedWidget()
        self.mode_stack.addWidget(self._build_spam_panel())
        self.mode_stack.addWidget(self._build_hold_panel())
        self.mode_stack.addWidget(self._build_macro_panel())
        root.addWidget(self.mode_stack, 1)

        self.mode_combo.currentIndexChanged.connect(self.mode_stack.setCurrentIndex)

        root.addLayout(self._build_control_bar())

    # ---- panels -------------------------------------------------------

    def _build_spam_panel(self) -> QWidget:
        box = QGroupBox("Spam Mode — press && release repeatedly")
        form = QFormLayout(box)
        form.setSpacing(10)

        self.spam_key_edit = KeyCaptureEdit()
        form.addRow("Key:", self.spam_key_edit)

        interval_row = QHBoxLayout()
        self.spam_interval_spin = QDoubleSpinBox()
        self.spam_interval_spin.setRange(0.001, 3_600_000)
        self.spam_interval_spin.setDecimals(3)
        self.spam_interval_spin.setValue(100)
        self.spam_unit_combo = QComboBox()
        self.spam_unit_combo.addItems(["ms", "s"])
        interval_row.addWidget(self.spam_interval_spin, 1)
        interval_row.addWidget(self.spam_unit_combo)
        form.addRow("Interval:", interval_row)

        self.spam_random_check = QCheckBox("Randomize delay")
        form.addRow("", self.spam_random_check)

        random_row = QHBoxLayout()
        self.spam_random_min_spin = QDoubleSpinBox()
        self.spam_random_min_spin.setRange(0, 3_600_000)
        self.spam_random_min_spin.setValue(50)
        self.spam_random_max_spin = QDoubleSpinBox()
        self.spam_random_max_spin.setRange(0, 3_600_000)
        self.spam_random_max_spin.setValue(150)
        self.spam_random_min_spin.setEnabled(False)
        self.spam_random_max_spin.setEnabled(False)
        self.spam_random_check.toggled.connect(self.spam_random_min_spin.setEnabled)
        self.spam_random_check.toggled.connect(self.spam_random_max_spin.setEnabled)
        random_row.addWidget(QLabel("Min:"))
        random_row.addWidget(self.spam_random_min_spin)
        random_row.addWidget(QLabel("Max:"))
        random_row.addWidget(self.spam_random_max_spin)
        form.addRow("", random_row)

        return box

    def _build_hold_panel(self) -> QWidget:
        box = QGroupBox("Hold Mode — press and hold for a duration")
        form = QFormLayout(box)
        form.setSpacing(10)

        self.hold_key_edit = KeyCaptureEdit()
        form.addRow("Key:", self.hold_key_edit)

        duration_row = QHBoxLayout()
        self.hold_duration_spin = QDoubleSpinBox()
        self.hold_duration_spin.setRange(0.001, 3_600_000)
        self.hold_duration_spin.setDecimals(3)
        self.hold_duration_spin.setValue(1000)
        self.hold_unit_combo = QComboBox()
        self.hold_unit_combo.addItems(["ms", "s"])
        duration_row.addWidget(self.hold_duration_spin, 1)
        duration_row.addWidget(self.hold_unit_combo)
        form.addRow("Hold duration:", duration_row)

        return box

    def _build_macro_panel(self) -> QWidget:
        box = QGroupBox("Macro Mode — loop-type a text sequence")
        layout = QVBoxLayout(box)
        layout.setSpacing(10)

        layout.addWidget(QLabel("Macro text:"))
        self.macro_text_edit = QPlainTextEdit()
        self.macro_text_edit.setPlaceholderText("Type the text/sequence to repeat…")
        self.macro_text_edit.setMaximumHeight(110)
        layout.addWidget(self.macro_text_edit)

        interval_row = QHBoxLayout()
        interval_row.addWidget(QLabel("Repeat every:"))
        self.macro_interval_spin = QDoubleSpinBox()
        self.macro_interval_spin.setRange(0.001, 3_600_000)
        self.macro_interval_spin.setDecimals(3)
        self.macro_interval_spin.setValue(1000)
        self.macro_unit_combo = QComboBox()
        self.macro_unit_combo.addItems(["ms", "s"])
        interval_row.addWidget(self.macro_interval_spin, 1)
        interval_row.addWidget(self.macro_unit_combo)
        layout.addLayout(interval_row)

        layout.addStretch(1)
        return box

    def _build_control_bar(self) -> QHBoxLayout:
        bar = QHBoxLayout()
        self.start_btn = QPushButton("Start")
        self.start_btn.setObjectName("PrimaryButton")
        self.start_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.start_btn.setMinimumWidth(120)

        self.stop_btn = QPushButton("Stop")
        self.stop_btn.setObjectName("DangerButton")
        self.stop_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.stop_btn.setMinimumWidth(120)
        self.stop_btn.setEnabled(False)

        self.status_indicator = StatusIndicator()
        self.count_label = QLabel("Actions: 0")
        self.count_label.setStyleSheet("color: #9099a8;")

        bar.addWidget(self.start_btn)
        bar.addWidget(self.stop_btn)
        bar.addSpacing(12)
        bar.addWidget(self.status_indicator)
        bar.addStretch(1)
        bar.addWidget(self.count_label)
        return bar
