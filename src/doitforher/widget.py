"""The floating, always-on-top photo widget."""
from __future__ import annotations

import subprocess
import tkinter as tk
from pathlib import Path

from PIL import Image, ImageTk

from .config import Config, images_dir, load_state, save_state

IMG_EXTS = {".png", ".jpg", ".jpeg", ".webp", ".gif", ".bmp"}


def list_images(directory: Path) -> list[Path]:
    if not directory.exists():
        return []
    return sorted(p for p in directory.iterdir() if p.suffix.lower() in IMG_EXTS)


def make_square_photo(path: Path, size: int) -> ImageTk.PhotoImage:
    img = Image.open(path).convert("RGB")
    w, h = img.size
    side = min(w, h)
    left, top = (w - side) // 2, (h - side) // 2
    img = img.crop((left, top, left + side, top + side)).resize((size, size), Image.LANCZOS)
    return ImageTk.PhotoImage(img)


class DoItForHer(tk.Tk):
    def __init__(self, cfg: Config):
        super().__init__()
        self.cfg = cfg
        self.images_dir = images_dir()
        self.images_dir.mkdir(parents=True, exist_ok=True)
        self.state = load_state()
        self.paused = False
        self.photos: list[ImageTk.PhotoImage] = []  # keep refs alive
        self.paths = list_images(self.images_dir)
        self.idx = 0

        self.overrideredirect(True)
        self.attributes("-topmost", True)
        try:
            self.wm_attributes("-type", "dock")
        except tk.TclError:
            pass  # not every window manager supports this hint
        self.configure(bg="black")

        self.label = tk.Label(self, bg="black", bd=0, highlightthickness=0)
        self.label.pack()
        self.caption = tk.Label(
            self, text=cfg.caption, fg="white", bg="black",
            font=("Sans", 7, "bold"), bd=0, highlightthickness=0,
        )
        if cfg.caption:
            self.caption.pack(pady=(0, 1))

        self._place_window()
        self._bind_events()
        self._refresh_image()
        self._keep_on_top()
        self.after(cfg.rotate_seconds * 1000, self._tick)

    # -- placement ---------------------------------------------------
    def _place_window(self):
        self.update_idletasks()
        sw, sh = self.winfo_screenwidth(), self.winfo_screenheight()
        w, h = self.cfg.size, self.cfg.size + 16
        x, y = self.state.get("x"), self.state.get("y")
        if x is None or y is None:
            x = self.cfg.margin if "left" in self.cfg.corner else sw - w - self.cfg.margin
            y = (
                self.cfg.margin
                if "top" in self.cfg.corner
                else sh - h - self.cfg.margin - self.cfg.taskbar_clearance
            )
        self.geometry(f"{w}x{h}+{x}+{y}")

    def _save_position(self):
        self.state["x"] = self.winfo_x()
        self.state["y"] = self.winfo_y()
        save_state(self.state)

    # -- events --------------------------------------------------------
    def _bind_events(self):
        self.label.bind("<Button-1>", lambda e: self.next_image())
        self.caption.bind("<Button-1>", lambda e: self.next_image())

        for widget in (self, self.label, self.caption):
            widget.bind("<ButtonPress-2>", self._start_drag)
            widget.bind("<B2-Motion>", self._do_drag)
            widget.bind("<ButtonRelease-2>", lambda e: self._save_position())
            widget.bind("<Button-3>", self._show_menu)

        self.menu = tk.Menu(self, tearoff=0)
        self.menu.add_command(label="Siguiente foto", command=self.next_image)
        self.menu.add_command(label="Pausar / reanudar rotación", command=self.toggle_pause)
        self.menu.add_command(label="Abrir carpeta de imágenes", command=self._open_folder)
        self.menu.add_command(label="Recargar fotos", command=self._reload_images)
        self.menu.add_separator()
        self.menu.add_command(label="Salir", command=self.destroy)

    def _start_drag(self, event):
        self._drag_x, self._drag_y = event.x, event.y

    def _do_drag(self, event):
        x = self.winfo_x() + (event.x - self._drag_x)
        y = self.winfo_y() + (event.y - self._drag_y)
        self.geometry(f"+{x}+{y}")

    def _show_menu(self, event):
        self.menu.tk_popup(event.x_root, event.y_root)

    def _open_folder(self):
        subprocess.Popen(["xdg-open", str(self.images_dir)])

    def toggle_pause(self):
        self.paused = not self.paused

    def _reload_images(self):
        self.paths = list_images(self.images_dir)
        self.idx = 0
        self._refresh_image()

    # -- images ----------------------------------------------------
    def _refresh_image(self):
        if not self.paths:
            self.label.configure(
                text=f"Pon fotos en:\n{self.images_dir}",
                image="", fg="white", font=("Sans", 9),
                width=self.cfg.size // 7, height=self.cfg.size // 14,
            )
            return
        path = self.paths[self.idx % len(self.paths)]
        try:
            photo = make_square_photo(path, self.cfg.size)
        except Exception:
            self.paths.pop(self.idx % len(self.paths))
            if self.paths:
                self._refresh_image()
            return
        self.photos = [photo]
        self.label.configure(image=photo, text="")

    def next_image(self):
        if not self.paths:
            self._reload_images()
            return
        self.idx = (self.idx + 1) % len(self.paths)
        self._refresh_image()

    def _tick(self):
        if not self.paused:
            self.next_image()
        self.after(self.cfg.rotate_seconds * 1000, self._tick)

    def _keep_on_top(self):
        self.attributes("-topmost", True)
        self.lift()
        self.after(2000, self._keep_on_top)

    def run(self):
        self.protocol("WM_DELETE_WINDOW", self.destroy)
        try:
            self.mainloop()
        finally:
            self._save_position()
