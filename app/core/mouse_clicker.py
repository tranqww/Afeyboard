"""Mouse Clicker worker: runs the click loop on a background thread via pynput."""
from __future__ import annotations

import random
import threading
import time
from dataclasses import dataclass, field

from PyQt6.QtCore import QObject, pyqtSignal
from pynput import mouse
from pynput.mouse import Button, Controller

from app.config import ClickerStatus, ClickMode, LimitMode, MouseButtonOption, PositionMode, TimeUnit

_BUTTON_MAP = {
    MouseButtonOption.LEFT: Button.left,
    MouseButtonOption.RIGHT: Button.right,
    MouseButtonOption.MIDDLE: Button.middle,
    MouseButtonOption.X1: getattr(Button, "x1", Button.left),
    MouseButtonOption.X2: getattr(Button, "x2", Button.right),
}

_SLEEP_STEP = 0.02


@dataclass
class MouseClickSettings:
    button: MouseButtonOption = MouseButtonOption.LEFT
    click_mode: ClickMode = ClickMode.SINGLE
    interval_value: float = 100.0
    interval_unit: TimeUnit = TimeUnit.MS
    randomize: bool = False
    random_min: float = 50.0
    random_max: float = 150.0
    position_mode: PositionMode = PositionMode.CURRENT
    fixed_point: tuple[int, int] = (0, 0)
    points: list[tuple[int, int]] = field(default_factory=list)
    limit_mode: LimitMode = LimitMode.INFINITE
    limit_count: int = 100
    return_cursor: bool = False

    def next_delay_seconds(self) -> float:
        if self.randomize:
            lo, hi = sorted((self.random_min, self.random_max))
            value = random.uniform(lo, hi)
        else:
            value = self.interval_value
        return max(self.interval_unit.to_seconds(value), 0.0)


class MouseClickerWorker(QObject):
    status_changed = pyqtSignal(object)
    count_changed = pyqtSignal(int)
    finished = pyqtSignal()
    error = pyqtSignal(str)

    def __init__(self, settings: MouseClickSettings) -> None:
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
        mouse = Controller()
        self._count = 0
        self.status_changed.emit(ClickerStatus.RUNNING)

        try:
            targets = self._resolve_targets(self._settings)
            while not self._stop_event.is_set():
                for target in targets:
                    if self._stop_event.is_set():
                        break
                    self._wait_while_paused()
                    if self._stop_event.is_set():
                        break

                    origin = mouse.position if self._settings.return_cursor else None
                    if target is not None:
                        mouse.position = target

                    click_count = 2 if self._settings.click_mode is ClickMode.DOUBLE else 1
                    mouse.click(_BUTTON_MAP[self._settings.button], click_count)

                    if origin is not None:
                        mouse.position = origin

                    self._count += 1
                    self.count_changed.emit(self._count)

                    if (
                        self._settings.limit_mode is LimitMode.FIXED
                        and self._count >= self._settings.limit_count
                    ):
                        self._stop_event.set()
                        break

                    self._interruptible_sleep(self._settings.next_delay_seconds())
        except Exception as exc:  # noqa: BLE001 - surface any pynput/runtime error to the UI
            self.error.emit(str(exc))
        finally:
            self.status_changed.emit(ClickerStatus.IDLE)
            self.finished.emit()

    def _resolve_targets(self, settings: MouseClickSettings) -> list[tuple[int, int] | None]:
        if settings.position_mode is PositionMode.FIXED:
            return [settings.fixed_point]
        if settings.position_mode is PositionMode.MULTI:
            return list(settings.points) or [None]
        return [None]

    def _wait_while_paused(self) -> None:
        while self._pause_event.is_set() and not self._stop_event.is_set():
            time.sleep(_SLEEP_STEP)

    def _interruptible_sleep(self, duration: float) -> None:
        remaining = duration
        while remaining > 0 and not self._stop_event.is_set():
            step = min(_SLEEP_STEP, remaining)
            time.sleep(step)
            remaining -= step


class PointPicker(QObject):
    """Captures the next mouse click anywhere on screen via a pynput listener."""

    point_picked = pyqtSignal(int, int)

    def __init__(self) -> None:
        super().__init__()
        self._listener: mouse.Listener | None = None

    def start(self) -> None:
        self.stop()

        def on_click(x: float, y: float, button: Button, pressed: bool) -> bool | None:
            if pressed:
                self.point_picked.emit(int(x), int(y))
                return False
            return None

        self._listener = mouse.Listener(on_click=on_click)
        self._listener.start()

    def stop(self) -> None:
        if self._listener is not None:
            self._listener.stop()
            self._listener = None
