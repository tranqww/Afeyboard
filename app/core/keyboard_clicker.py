"""Keyboard Clicker worker: spam / hold / macro modes on a background thread via pynput."""
from __future__ import annotations

import random
import threading
import time
from dataclasses import dataclass

from PyQt6.QtCore import QObject, pyqtSignal
from pynput.keyboard import Controller, Key

from app.config import ClickerStatus, KeyboardMode, TimeUnit

_SLEEP_STEP = 0.02

_SPECIAL_KEY_MAP = {
    "space": Key.space,
    "return": Key.enter,
    "enter": Key.enter,
    "tab": Key.tab,
    "esc": Key.esc,
    "escape": Key.esc,
    "backspace": Key.backspace,
    "delete": Key.delete,
    "del": Key.delete,
    "insert": Key.insert,
    "ins": Key.insert,
    "home": Key.home,
    "end": Key.end,
    "pgup": Key.page_up,
    "pageup": Key.page_up,
    "pgdown": Key.page_down,
    "pagedown": Key.page_down,
    "left": Key.left,
    "right": Key.right,
    "up": Key.up,
    "down": Key.down,
    "capslock": Key.caps_lock,
    "numlock": Key.num_lock,
    "scrolllock": Key.scroll_lock,
    "printscreen": Key.print_screen,
    "prtsc": Key.print_screen,
    "pause": Key.pause,
    "menu": Key.menu,
    "shift": Key.shift,
    "ctrl": Key.ctrl,
    "control": Key.ctrl,
    "alt": Key.alt,
    "meta": Key.cmd,
    "win": Key.cmd,
    "super": Key.cmd,
}
for _i in range(1, 25):
    _f_key = getattr(Key, f"f{_i}", None)
    if _f_key is not None:
        _SPECIAL_KEY_MAP[f"f{_i}"] = _f_key


def _parse_key_token(token: str):
    token = token.strip()
    if not token:
        return None
    lowered = token.lower()
    if lowered in _SPECIAL_KEY_MAP:
        return _SPECIAL_KEY_MAP[lowered]
    return token[0].lower()


def parse_key_sequence(text: str):
    """Parse a captured key string (e.g. 'Ctrl+Alt+P', 'F6') into (modifiers, main_key)."""
    tokens = [t for t in text.split("+") if t]
    if not tokens:
        raise ValueError("No key selected")
    *mod_tokens, main_token = tokens
    modifiers = [k for k in (_parse_key_token(t) for t in mod_tokens) if k is not None]
    main_key = _parse_key_token(main_token)
    if main_key is None:
        raise ValueError(f"Unrecognized key: {text!r}")
    return modifiers, main_key


@dataclass
class KeyboardClickSettings:
    mode: KeyboardMode = KeyboardMode.SPAM

    key_text: str = ""
    interval_value: float = 100.0
    interval_unit: TimeUnit = TimeUnit.MS
    randomize: bool = False
    random_min: float = 50.0
    random_max: float = 150.0

    hold_duration_value: float = 1000.0
    hold_duration_unit: TimeUnit = TimeUnit.MS

    macro_text: str = ""
    macro_interval_value: float = 1000.0
    macro_interval_unit: TimeUnit = TimeUnit.MS

    def next_spam_delay_seconds(self) -> float:
        if self.randomize:
            lo, hi = sorted((self.random_min, self.random_max))
            value = random.uniform(lo, hi)
        else:
            value = self.interval_value
        return max(self.interval_unit.to_seconds(value), 0.0)

    def hold_duration_seconds(self) -> float:
        return max(self.hold_duration_unit.to_seconds(self.hold_duration_value), 0.0)

    def macro_delay_seconds(self) -> float:
        return max(self.macro_interval_unit.to_seconds(self.macro_interval_value), 0.0)


class KeyboardClickerWorker(QObject):
    status_changed = pyqtSignal(object)
    count_changed = pyqtSignal(int)
    finished = pyqtSignal()
    error = pyqtSignal(str)

    def __init__(self, settings: KeyboardClickSettings) -> None:
        super().__init__()
        self._settings = settings
        self._stop_event = threading.Event()
        self._pause_event = threading.Event()
        self._count = 0

    def request_stop(self) -> None:
        self._stop_event.set()

    def set_paused(self, paused: bool) -> None:
        if paused:
            self._pause_event.set()
            self.status_changed.emit(ClickerStatus.PAUSED)
        else:
            self._pause_event.clear()
            self.status_changed.emit(ClickerStatus.RUNNING)

    def toggle_pause(self) -> None:
        self.set_paused(not self._pause_event.is_set())

    def run(self) -> None:
        kb = Controller()
        self._count = 0
        self.status_changed.emit(ClickerStatus.RUNNING)

        try:
            if self._settings.mode is KeyboardMode.SPAM:
                self._run_spam(kb)
            elif self._settings.mode is KeyboardMode.HOLD:
                self._run_hold(kb)
            else:
                self._run_macro(kb)
        except Exception as exc:  # noqa: BLE001 - surface any pynput/runtime error to the UI
            self.error.emit(str(exc))
        finally:
            self.status_changed.emit(ClickerStatus.IDLE)
            self.finished.emit()

    def _run_spam(self, kb: Controller) -> None:
        modifiers, main_key = parse_key_sequence(self._settings.key_text)
        while not self._stop_event.is_set():
            self._wait_while_paused()
            if self._stop_event.is_set():
                break
            self._press(kb, modifiers, main_key)
            self._release(kb, modifiers, main_key)
            self._count += 1
            self.count_changed.emit(self._count)
            self._interruptible_sleep(self._settings.next_spam_delay_seconds())

    def _run_hold(self, kb: Controller) -> None:
        modifiers, main_key = parse_key_sequence(self._settings.key_text)
        self._wait_while_paused()
        self._press(kb, modifiers, main_key)
        try:
            self._interruptible_sleep(self._settings.hold_duration_seconds())
        finally:
            self._release(kb, modifiers, main_key)
        self._count += 1
        self.count_changed.emit(self._count)
        self._stop_event.set()

    def _run_macro(self, kb: Controller) -> None:
        text = self._settings.macro_text
        while not self._stop_event.is_set():
            self._wait_while_paused()
            if self._stop_event.is_set():
                break
            kb.type(text)
            self._count += 1
            self.count_changed.emit(self._count)
            self._interruptible_sleep(self._settings.macro_delay_seconds())

    @staticmethod
    def _press(kb: Controller, modifiers: list, main_key) -> None:
        for mod in modifiers:
            kb.press(mod)
        kb.press(main_key)

    @staticmethod
    def _release(kb: Controller, modifiers: list, main_key) -> None:
        kb.release(main_key)
        for mod in reversed(modifiers):
            kb.release(mod)

    def _wait_while_paused(self) -> None:
        while self._pause_event.is_set() and not self._stop_event.is_set():
            time.sleep(_SLEEP_STEP)

    def _interruptible_sleep(self, duration: float) -> None:
        remaining = duration
        while remaining > 0 and not self._stop_event.is_set():
            step = min(_SLEEP_STEP, remaining)
            time.sleep(step)
            remaining -= step
