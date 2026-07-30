"""Global Start/Stop and Pause/Resume hotkeys, active even while the app is unfocused."""
from __future__ import annotations

from PyQt6.QtCore import QObject, pyqtSignal
from pynput import keyboard

_NAME_FIXUPS = {
    "return": "enter",
    "control": "ctrl",
    "meta": "cmd",
    "win": "cmd",
    "super": "cmd",
    "esc": "esc",
    "pageup": "page_up",
    "pagedown": "page_down",
    "capslock": "caps_lock",
    "numlock": "num_lock",
    "scrolllock": "scroll_lock",
    "printscreen": "print_screen",
}


def _to_pynput_hotkey(text: str) -> str:
    """Convert a captured hotkey string (e.g. 'Ctrl+Alt+P', 'F6') to pynput's grammar."""
    tokens = [t for t in text.split("+") if t]
    if not tokens:
        raise ValueError("Empty hotkey")
    parts = []
    for token in tokens:
        name = _NAME_FIXUPS.get(token.lower(), token.lower())
        parts.append(f"<{name}>" if len(name) > 1 else name)
    return "+".join(parts)


class HotkeyManager(QObject):
    start_stop_triggered = pyqtSignal()
    pause_resume_triggered = pyqtSignal()
    error = pyqtSignal(str)

    def __init__(self) -> None:
        super().__init__()
        self._listener: keyboard.GlobalHotKeys | None = None
        self._start_stop_text = ""
        self._pause_resume_text = ""

    def update_hotkeys(self, start_stop_text: str, pause_resume_text: str) -> None:
        self._start_stop_text = start_stop_text
        self._pause_resume_text = pause_resume_text
        self._restart_listener()

    def stop(self) -> None:
        if self._listener is not None:
            self._listener.stop()
            self._listener = None

    def _restart_listener(self) -> None:
        self.stop()
        mapping = {}
        try:
            if self._start_stop_text:
                mapping[_to_pynput_hotkey(self._start_stop_text)] = self.start_stop_triggered.emit
            if self._pause_resume_text:
                mapping[_to_pynput_hotkey(self._pause_resume_text)] = self.pause_resume_triggered.emit
        except ValueError as exc:
            self.error.emit(str(exc))
            return

        if not mapping:
            return

        try:
            self._listener = keyboard.GlobalHotKeys(mapping)
            self._listener.start()
        except Exception as exc:  # noqa: BLE001 - invalid/duplicate combo shouldn't crash the app
            self._listener = None
            self.error.emit(str(exc))
