"""Application-wide constants, paths and enums."""
from __future__ import annotations

import os
from enum import Enum

APP_NAME = "Afeyboard"
ORG_NAME = "Afeyboard"

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROFILES_DIR = os.path.join(BASE_DIR, "profiles")
LAST_STATE_PATH = os.path.join(PROFILES_DIR, "_last_state.json")

os.makedirs(PROFILES_DIR, exist_ok=True)


class ClickerStatus(Enum):
    IDLE = "Idle"
    RUNNING = "Running"
    PAUSED = "Paused"


class TimeUnit(Enum):
    MS = "ms"
    SEC = "s"

    def to_seconds(self, value: float) -> float:
        return value / 1000.0 if self is TimeUnit.MS else value


class MouseButtonOption(Enum):
    LEFT = "Left"
    RIGHT = "Right"
    MIDDLE = "Middle"
    X1 = "Side 1 (Back)"
    X2 = "Side 2 (Forward)"


class ClickMode(Enum):
    SINGLE = "Single Click"
    DOUBLE = "Double Click"


class PositionMode(Enum):
    CURRENT = "Current Cursor Position"
    FIXED = "Fixed Coordinates"
    MULTI = "Multiple Points"


class LimitMode(Enum):
    INFINITE = "Infinite"
    FIXED = "Fixed Count"


class KeyboardMode(Enum):
    SPAM = "Spam Mode"
    HOLD = "Hold Mode"
    MACRO = "Macro Mode"


DEFAULT_HOTKEY_START_STOP = "F6"
DEFAULT_HOTKEY_PAUSE_RESUME = "F7"

STATUS_COLORS = {
    ClickerStatus.IDLE: "#6b7280",
    ClickerStatus.RUNNING: "#39ff9d",
    ClickerStatus.PAUSED: "#ffb020",
}
