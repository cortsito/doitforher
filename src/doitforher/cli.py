"""Command-line entry point: `do-it-for-her` / `python -m doitforher`."""
from __future__ import annotations

import argparse
import sys
from dataclasses import replace

from . import __version__
from . import autostart
from .config import VALID_CORNERS, images_dir, load_config
from .widget import DoItForHer


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="do-it-for-her",
        description="A tiny always-on-top widget that rotates through your own photos.",
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    parser.add_argument("--size", type=int, help="widget side in px (overrides config.json)")
    parser.add_argument("--corner", choices=sorted(VALID_CORNERS), help="screen corner")
    parser.add_argument("--rotate-seconds", type=int, help="seconds between automatic photo changes")
    parser.add_argument("--caption", help="text under the photo (pass \"\" to hide it)")

    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        "--install-autostart", action="store_true",
        help="launch automatically on login (GNOME/XDG autostart) and exit",
    )
    group.add_argument(
        "--uninstall-autostart", action="store_true",
        help="stop launching automatically on login and exit",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)

    if args.install_autostart:
        path = autostart.install()
        print(f"Autostart instalado: {path}")
        return 0
    if args.uninstall_autostart:
        removed = autostart.uninstall()
        print("Autostart eliminado." if removed else "No había autostart instalado.")
        return 0

    cfg = load_config()
    overrides = {
        k: v
        for k, v in dict(
            size=args.size,
            corner=args.corner,
            rotate_seconds=args.rotate_seconds,
            caption=args.caption,
        ).items()
        if v is not None
    }
    if overrides:
        cfg = replace(cfg, **overrides)
    cfg = cfg.validated()

    print(f"Fotos en: {images_dir()}  (click derecho sobre el widget para el menú)")
    DoItForHer(cfg).run()
    return 0


if __name__ == "__main__":
    sys.exit(main())
