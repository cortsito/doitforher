"""App paths and persisted configuration (XDG-aware)."""
from __future__ import annotations

import json
from dataclasses import asdict, dataclass, replace
from pathlib import Path

APP_NAME = "do-it-for-her"

VALID_CORNERS = {"top-left", "top-right", "bottom-left", "bottom-right"}


def _xdg_dir(env_var: str, fallback: str) -> Path:
    import os

    base = os.environ.get(env_var)
    return Path(base) if base else Path.home() / fallback


def config_dir() -> Path:
    return _xdg_dir("XDG_CONFIG_HOME", ".config") / APP_NAME


def state_dir() -> Path:
    return _xdg_dir("XDG_STATE_HOME", ".local/state") / APP_NAME


def images_dir() -> Path:
    return config_dir() / "images"


def config_path() -> Path:
    return config_dir() / "config.json"


def state_path() -> Path:
    return state_dir() / "state.json"


@dataclass
class Config:
    size: int = 110
    corner: str = "bottom-right"
    rotate_seconds: int = 8
    margin: int = 20
    taskbar_clearance: int = 40
    caption: str = "Do it for her"

    def validated(self) -> "Config":
        cfg = replace(self)
        if cfg.corner not in VALID_CORNERS:
            raise ValueError(f"corner must be one of {sorted(VALID_CORNERS)}, got {cfg.corner!r}")
        if cfg.size < 40 or cfg.size > 600:
            raise ValueError("size must be between 40 and 600 px")
        if cfg.rotate_seconds < 1:
            raise ValueError("rotate_seconds must be >= 1")
        return cfg


def load_config() -> Config:
    path = config_path()
    if not path.exists():
        cfg = Config()
        save_config(cfg)
        return cfg
    try:
        data = json.loads(path.read_text())
    except (json.JSONDecodeError, OSError):
        return Config()
    known = {f: data[f] for f in Config.__dataclass_fields__ if f in data}
    return Config(**known).validated()


def save_config(cfg: Config) -> None:
    config_dir().mkdir(parents=True, exist_ok=True)
    config_path().write_text(json.dumps(asdict(cfg), indent=2) + "\n")


def load_state() -> dict:
    path = state_path()
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text())
    except (json.JSONDecodeError, OSError):
        return {}


def save_state(data: dict) -> None:
    state_dir().mkdir(parents=True, exist_ok=True)
    state_path().write_text(json.dumps(data, indent=2) + "\n")
