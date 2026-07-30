"""Settings & Hotkeys page — UI layout only; wired to hotkey/profile managers separately."""
from __future__ import annotations

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)

from app.config import DEFAULT_HOTKEY_PAUSE_RESUME, DEFAULT_HOTKEY_START_STOP
from app.ui.widgets import KeyCaptureEdit, PageHeader


class SettingsPage(QWidget):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)

        root = QVBoxLayout(self)
        root.setContentsMargins(28, 24, 28, 20)
        root.setSpacing(14)

        root.addWidget(
            PageHeader(
                "Settings & Hotkeys",
                "Global shortcuts, profiles, auto-stop timer and tray behavior.",
            )
        )

        root.addWidget(self._build_hotkeys_group())
        root.addWidget(self._build_profiles_group())

        row = QHBoxLayout()
        row.addWidget(self._build_autostop_group(), 1)
        row.addWidget(self._build_tray_group(), 1)
        root.addLayout(row)

        root.addStretch(1)

    # ---- groups -----------------------------------------------------

    def _build_hotkeys_group(self) -> QGroupBox:
        box = QGroupBox("Global Hotkeys")
        form = QFormLayout(box)
        form.setSpacing(10)

        self.start_stop_edit = KeyCaptureEdit(default=DEFAULT_HOTKEY_START_STOP)
        self.start_stop_reset_btn = QPushButton("Reset")
        start_stop_row = QHBoxLayout()
        start_stop_row.addWidget(self.start_stop_edit, 1)
        start_stop_row.addWidget(self.start_stop_reset_btn)
        form.addRow("Start / Stop:", start_stop_row)

        self.pause_resume_edit = KeyCaptureEdit(default=DEFAULT_HOTKEY_PAUSE_RESUME)
        self.pause_resume_reset_btn = QPushButton("Reset")
        pause_resume_row = QHBoxLayout()
        pause_resume_row.addWidget(self.pause_resume_edit, 1)
        pause_resume_row.addWidget(self.pause_resume_reset_btn)
        form.addRow("Pause / Resume:", pause_resume_row)

        hint = QLabel(
            "Hotkeys work globally — even while Afeyboard is minimized or unfocused."
        )
        hint.setStyleSheet("color: #9099a8;")
        hint.setWordWrap(True)
        form.addRow("", hint)

        return box

    def _build_profiles_group(self) -> QGroupBox:
        box = QGroupBox("Profiles")
        layout = QVBoxLayout(box)
        layout.setSpacing(10)

        load_row = QHBoxLayout()
        self.profile_combo = QComboBox()
        self.profile_combo.setMinimumWidth(200)
        self.load_profile_btn = QPushButton("Load")
        self.delete_profile_btn = QPushButton("Delete")
        self.delete_profile_btn.setObjectName("DangerButton")
        load_row.addWidget(QLabel("Saved profiles:"))
        load_row.addWidget(self.profile_combo, 1)
        load_row.addWidget(self.load_profile_btn)
        load_row.addWidget(self.delete_profile_btn)
        layout.addLayout(load_row)

        save_row = QHBoxLayout()
        self.profile_name_edit = QLineEdit()
        self.profile_name_edit.setPlaceholderText("New profile name…")
        self.save_profile_btn = QPushButton("Save Current Settings As…")
        self.save_profile_btn.setObjectName("PrimaryButton")
        save_row.addWidget(self.profile_name_edit, 1)
        save_row.addWidget(self.save_profile_btn)
        layout.addLayout(save_row)

        return box

    def _build_autostop_group(self) -> QGroupBox:
        box = QGroupBox("Auto-Stop Timer")
        form = QFormLayout(box)
        form.setSpacing(10)

        self.autostop_check = QCheckBox("Stop automatically after")
        form.addRow(self.autostop_check)

        value_row = QHBoxLayout()
        self.autostop_spin = QSpinBox()
        self.autostop_spin.setRange(1, 100_000)
        self.autostop_spin.setValue(10)
        self.autostop_spin.setEnabled(False)
        self.autostop_unit_combo = QComboBox()
        self.autostop_unit_combo.addItems(["Minutes", "Seconds"])
        self.autostop_unit_combo.setEnabled(False)
        self.autostop_check.toggled.connect(self.autostop_spin.setEnabled)
        self.autostop_check.toggled.connect(self.autostop_unit_combo.setEnabled)
        value_row.addWidget(self.autostop_spin)
        value_row.addWidget(self.autostop_unit_combo)
        form.addRow("Duration:", value_row)

        return box

    def _build_tray_group(self) -> QGroupBox:
        box = QGroupBox("System Tray")
        layout = QVBoxLayout(box)
        layout.setSpacing(10)

        self.start_minimized_check = QCheckBox("Launch minimized to tray")
        layout.addWidget(self.start_minimized_check)

        self.minimize_now_btn = QPushButton("Minimize to Tray Now")
        self.minimize_now_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        layout.addWidget(self.minimize_now_btn)

        layout.addStretch(1)
        return box
