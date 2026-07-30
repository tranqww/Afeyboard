"""Main application window: sidebar navigation + stacked pages + status bar.

Also acts as the light-weight controller wiring global hotkeys, profiles,
the auto-stop timer and tray behavior across the Mouse/Keyboard/Settings pages.
"""
from __future__ import annotations

from PyQt6.QtCore import QTimer, Qt
from PyQt6.QtGui import QCloseEvent, QColor, QIcon, QPainter, QPixmap
from PyQt6.QtWidgets import (
    QApplication,
    QHBoxLayout,
    QMainWindow,
    QMenu,
    QMessageBox,
    QStackedWidget,
    QSystemTrayIcon,
    QWidget,
)

from app import APP_NAME
from app.config import (
    DEFAULT_HOTKEY_PAUSE_RESUME,
    DEFAULT_HOTKEY_START_STOP,
    ClickerStatus,
)
from app.core import profile_manager
from app.core.hotkey_manager import HotkeyManager
from app.ui.pages.keyboard_page import KeyboardPage
from app.ui.pages.mouse_page import MousePage
from app.ui.pages.settings_page import SettingsPage
from app.ui.sidebar import Sidebar
from app.ui.style import ACCENT, STYLESHEET
from app.ui.widgets import StatusIndicator


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle(APP_NAME)
        self.resize(980, 660)
        self.setMinimumSize(860, 560)
        self.setStyleSheet(STYLESHEET)
        self.setWindowIcon(self._make_icon())

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
        self.stack.currentChanged.connect(self._on_page_changed)

        self._build_status_bar()
        self._build_tray_icon()

        self.hotkey_manager = HotkeyManager()
        self.hotkey_manager.start_stop_triggered.connect(self._on_global_start_stop)
        self.hotkey_manager.pause_resume_triggered.connect(self._on_global_pause_resume)
        self.hotkey_manager.error.connect(self._on_hotkey_error)

        self.autostop_timer = QTimer(self)
        self.autostop_timer.setSingleShot(True)
        self.autostop_timer.timeout.connect(self._on_autostop_timeout)

        self._tray_notice_shown = False

        self._load_app_settings()
        self._refresh_profile_list()
        self._wire_settings_page()
        self._wire_autostop()
        self._apply_hotkeys()

        self.mouse_page.status_changed.connect(self._on_page_status_changed)
        self.keyboard_page.status_changed.connect(self._on_page_status_changed)

    # ---- chrome ----------------------------------------------------------

    def _build_status_bar(self) -> None:
        bar = self.statusBar()
        self.global_status_indicator = StatusIndicator()
        self.global_status_indicator.set_status(ClickerStatus.IDLE)
        bar.addPermanentWidget(self.global_status_indicator)
        bar.showMessage(f"{APP_NAME} ready.")

    def _make_icon(self) -> QIcon:
        pixmap = QPixmap(64, 64)
        pixmap.fill(Qt.GlobalColor.transparent)
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QColor(ACCENT))
        painter.drawEllipse(4, 4, 56, 56)
        painter.end()
        return QIcon(pixmap)

    def _build_tray_icon(self) -> None:
        self.tray_icon = QSystemTrayIcon(self._make_icon(), self)
        self.tray_icon.setToolTip(APP_NAME)

        menu = QMenu()
        show_action = menu.addAction(f"Show {APP_NAME}")
        show_action.triggered.connect(self._show_from_tray)
        menu.addSeparator()
        quit_action = menu.addAction("Quit")
        quit_action.triggered.connect(self._quit_app)

        self.tray_icon.setContextMenu(menu)
        self.tray_icon.activated.connect(self._on_tray_activated)
        self.tray_icon.show()

    def _show_from_tray(self) -> None:
        self.showNormal()
        self.activateWindow()
        self.raise_()

    def _on_tray_activated(self, reason: QSystemTrayIcon.ActivationReason) -> None:
        if reason in (
            QSystemTrayIcon.ActivationReason.Trigger,
            QSystemTrayIcon.ActivationReason.DoubleClick,
        ):
            self._show_from_tray()

    def _quit_app(self) -> None:
        self.hotkey_manager.stop()
        self.tray_icon.hide()
        QApplication.instance().quit()

    def closeEvent(self, event: QCloseEvent) -> None:
        event.ignore()
        self.hide()
        if not self._tray_notice_shown:
            self.tray_icon.showMessage(
                APP_NAME,
                "Still running in the background. Use the tray icon to quit.",
                QSystemTrayIcon.MessageIcon.Information,
                3000,
            )
            self._tray_notice_shown = True

    def _on_page_changed(self, index: int) -> None:
        indicators = {0: self.mouse_page.status_indicator, 1: self.keyboard_page.status_indicator}
        indicator = indicators.get(index)
        self.global_status_indicator.set_status(indicator.status() if indicator else ClickerStatus.IDLE)

    def _on_page_status_changed(self, status: ClickerStatus) -> None:
        sender_page = self.sender()
        if sender_page is self._current_clicker_page():
            self.global_status_indicator.set_status(status)

    # ---- global hotkeys ---------------------------------------------------

    def _current_clicker_page(self):
        index = self.stack.currentIndex()
        if index == 0:
            return self.mouse_page
        if index == 1:
            return self.keyboard_page
        return None

    def _apply_hotkeys(self) -> None:
        self.hotkey_manager.update_hotkeys(
            self.settings_page.start_stop_edit.value(),
            self.settings_page.pause_resume_edit.value(),
        )

    def _on_global_start_stop(self) -> None:
        page = self._current_clicker_page()
        if page is None:
            return
        if page.is_running():
            page.stop_clicking()
        else:
            page.start_clicking()

    def _on_global_pause_resume(self) -> None:
        page = self._current_clicker_page()
        if page is not None:
            page.toggle_pause()

    def _on_hotkey_error(self, message: str) -> None:
        self.statusBar().showMessage(f"Hotkey error: {message}", 5000)

    # ---- settings page wiring ----------------------------------------------

    def _wire_settings_page(self) -> None:
        sp = self.settings_page

        sp.start_stop_edit.key_captured.connect(lambda _: self._on_hotkeys_changed())
        sp.pause_resume_edit.key_captured.connect(lambda _: self._on_hotkeys_changed())
        sp.start_stop_reset_btn.clicked.connect(self._reset_start_stop_hotkey)
        sp.pause_resume_reset_btn.clicked.connect(self._reset_pause_resume_hotkey)

        sp.save_profile_btn.clicked.connect(self._on_save_profile)
        sp.load_profile_btn.clicked.connect(self._on_load_profile)
        sp.delete_profile_btn.clicked.connect(self._on_delete_profile)

        sp.autostop_check.toggled.connect(self._save_app_settings)
        sp.autostop_spin.valueChanged.connect(self._save_app_settings)
        sp.autostop_unit_combo.currentIndexChanged.connect(self._save_app_settings)
        sp.start_minimized_check.toggled.connect(self._save_app_settings)

        sp.minimize_now_btn.clicked.connect(self.hide)

    def _on_hotkeys_changed(self) -> None:
        self._apply_hotkeys()
        self._save_app_settings()

    def _reset_start_stop_hotkey(self) -> None:
        self.settings_page.start_stop_edit.set_value(DEFAULT_HOTKEY_START_STOP)
        self._on_hotkeys_changed()

    def _reset_pause_resume_hotkey(self) -> None:
        self.settings_page.pause_resume_edit.set_value(DEFAULT_HOTKEY_PAUSE_RESUME)
        self._on_hotkeys_changed()

    # ---- auto-stop timer ----------------------------------------------------

    def _wire_autostop(self) -> None:
        for page in (self.mouse_page, self.keyboard_page):
            page.start_btn.clicked.connect(self._arm_autostop)
            page.stop_btn.clicked.connect(self.autostop_timer.stop)
            page.run_finished.connect(self.autostop_timer.stop)

    def _arm_autostop(self) -> None:
        sp = self.settings_page
        if not sp.autostop_check.isChecked():
            return
        seconds = sp.autostop_spin.value() * (60 if sp.autostop_unit_combo.currentText() == "Minutes" else 1)
        self.autostop_timer.start(int(seconds * 1000))

    def _on_autostop_timeout(self) -> None:
        if self.mouse_page.is_running():
            self.mouse_page.stop_clicking()
        if self.keyboard_page.is_running():
            self.keyboard_page.stop_clicking()

    # ---- profiles -----------------------------------------------------------

    def _refresh_profile_list(self) -> None:
        combo = self.settings_page.profile_combo
        current = combo.currentText()
        combo.clear()
        combo.addItems(profile_manager.list_profiles())
        index = combo.findText(current)
        if index >= 0:
            combo.setCurrentIndex(index)

    def _on_save_profile(self) -> None:
        name = self.settings_page.profile_name_edit.text().strip()
        if not name:
            QMessageBox.warning(self, "Profile name required", "Enter a name for this profile.")
            return
        data = {"mouse": self.mouse_page.to_dict(), "keyboard": self.keyboard_page.to_dict()}
        profile_manager.save_profile(name, data)
        self.settings_page.profile_name_edit.clear()
        self._refresh_profile_list()
        index = self.settings_page.profile_combo.findText(name)
        if index >= 0:
            self.settings_page.profile_combo.setCurrentIndex(index)
        self.statusBar().showMessage(f"Profile '{name}' saved.", 4000)

    def _on_load_profile(self) -> None:
        name = self.settings_page.profile_combo.currentText()
        if not name:
            return
        try:
            data = profile_manager.load_profile(name)
            if "mouse" in data:
                self.mouse_page.apply_dict(data["mouse"])
            if "keyboard" in data:
                self.keyboard_page.apply_dict(data["keyboard"])
        except (OSError, ValueError, TypeError, KeyError) as exc:
            QMessageBox.critical(self, "Failed to load profile", f"Profile '{name}' is invalid or corrupted:\n{exc}")
            return
        self.statusBar().showMessage(f"Profile '{name}' loaded.", 4000)

    def _on_delete_profile(self) -> None:
        name = self.settings_page.profile_combo.currentText()
        if not name:
            return
        confirm = QMessageBox.question(
            self, "Delete profile", f"Delete profile '{name}'? This cannot be undone."
        )
        if confirm != QMessageBox.StandardButton.Yes:
            return
        profile_manager.delete_profile(name)
        self._refresh_profile_list()
        self.statusBar().showMessage(f"Profile '{name}' deleted.", 4000)

    # ---- app settings persistence --------------------------------------------

    def _save_app_settings(self, *_args) -> None:
        sp = self.settings_page
        profile_manager.save_app_settings(
            {
                "start_stop_hotkey": sp.start_stop_edit.value(),
                "pause_resume_hotkey": sp.pause_resume_edit.value(),
                "autostop_enabled": sp.autostop_check.isChecked(),
                "autostop_value": sp.autostop_spin.value(),
                "autostop_unit": sp.autostop_unit_combo.currentText(),
                "start_minimized": sp.start_minimized_check.isChecked(),
            }
        )

    def _load_app_settings(self) -> None:
        data = profile_manager.load_app_settings()
        if not data:
            return
        sp = self.settings_page
        try:
            sp.start_stop_edit.set_value(data.get("start_stop_hotkey", DEFAULT_HOTKEY_START_STOP))
            sp.pause_resume_edit.set_value(data.get("pause_resume_hotkey", DEFAULT_HOTKEY_PAUSE_RESUME))
            sp.autostop_check.setChecked(bool(data.get("autostop_enabled", False)))
            sp.autostop_spin.setValue(int(data.get("autostop_value", 10)))
            sp.autostop_unit_combo.setCurrentText(data.get("autostop_unit", "Minutes"))
            sp.start_minimized_check.setChecked(bool(data.get("start_minimized", False)))
        except (TypeError, ValueError):
            pass  # corrupted settings file: keep UI defaults rather than crash on startup

    def should_start_minimized(self) -> bool:
        return self.settings_page.start_minimized_check.isChecked()
