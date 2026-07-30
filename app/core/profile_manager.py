"""Save/load Mouse + Keyboard settings profiles, and persist misc app settings, as JSON."""
from __future__ import annotations

import json
import os
import re

from app.config import LAST_STATE_PATH, PROFILES_DIR

_SAFE_NAME_RE = re.compile(r"[^A-Za-z0-9 _\-]+")


def _sanitize(name: str) -> str:
    return _SAFE_NAME_RE.sub("_", name).strip() or "profile"


def _profile_path(name: str) -> str:
    return os.path.join(PROFILES_DIR, f"{_sanitize(name)}.json")


def list_profiles() -> list[str]:
    if not os.path.isdir(PROFILES_DIR):
        return []
    names = []
    for filename in os.listdir(PROFILES_DIR):
        if filename.endswith(".json") and not filename.startswith("_"):
            names.append(filename[: -len(".json")])
    return sorted(names)


def save_profile(name: str, data: dict) -> None:
    with open(_profile_path(name), "w", encoding="utf-8") as fh:
        json.dump(data, fh, indent=2)


def load_profile(name: str) -> dict:
    with open(_profile_path(name), "r", encoding="utf-8") as fh:
        return json.load(fh)


def delete_profile(name: str) -> None:
    path = _profile_path(name)
    if os.path.exists(path):
        os.remove(path)


def save_app_settings(data: dict) -> None:
    with open(LAST_STATE_PATH, "w", encoding="utf-8") as fh:
        json.dump(data, fh, indent=2)


def load_app_settings() -> dict:
    if not os.path.exists(LAST_STATE_PATH):
        return {}
    try:
        with open(LAST_STATE_PATH, "r", encoding="utf-8") as fh:
            return json.load(fh)
    except (json.JSONDecodeError, OSError):
        return {}
