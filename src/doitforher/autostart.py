"""Install/remove a freedesktop .desktop entry so the widget starts on login."""
from __future__ import annotations

import shutil
import sys
from pathlib import Path

from .config import APP_NAME, _xdg_dir

DESKTOP_ENTRY_NAME = f"{APP_NAME}.desktop"


def autostart_dir() -> Path:
    return _xdg_dir("XDG_CONFIG_HOME", ".config") / "autostart"


def autostart_path() -> Path:
    return autostart_dir() / DESKTOP_ENTRY_NAME


def _resolve_exec() -> str:
    exe = shutil.which(APP_NAME)
    if exe:
        return exe
    return f"{sys.executable} -m doitforher"


def install() -> Path:
    path = autostart_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "[Desktop Entry]\n"
        "Type=Application\n"
        "Name=Do It For Her\n"
        f"Exec={_resolve_exec()}\n"
        "X-GNOME-Autostart-enabled=true\n"
        "Terminal=false\n"
    )
    return path


def uninstall() -> bool:
    path = autostart_path()
    if path.exists():
        path.unlink()
        return True
    return False


def is_installed() -> bool:
    return autostart_path().exists()
