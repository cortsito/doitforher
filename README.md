# do-it-for-her

A tiny always-on-top desktop widget for Linux that sits quietly in a corner
of your screen — above every window and every tab — and rotates through
your own photos. A small, personal nudge while you work.

![demo placeholder](docs/demo.gif)

## Features

- Always on top, independent of whatever app or browser tab is focused
- Rotates through every image in your photo folder on a timer
- Click = next photo · right-click = menu (pause, reload, open folder, quit)
- Middle-click drag to reposition — it remembers where you left it
- Optional autostart on login (GNOME / any XDG-compliant desktop)
- Configurable size, corner, rotation interval and caption

## Requirements

- Linux with a desktop environment (tested on GNOME/Wayland via XWayland)
- Python 3.9+
- Tkinter (`python3-tkinter` on most distros; usually preinstalled)

## Install

```bash
git clone https://github.com/<your-user>/do-it-for-her.git
cd do-it-for-her
./install.sh
```

`install.sh` installs the package with [pipx](https://pypa.github.io/pipx/)
(or falls back to `pip install --user`) and offers to enable autostart.

Prefer doing it by hand?

```bash
pipx install .
do-it-for-her --install-autostart   # optional
```

## Usage

```bash
do-it-for-her
```

Drop your photos into `~/.config/do-it-for-her/images/` (created on first
run) — jpg, png, webp, gif and bmp are all picked up automatically. Right-click
the widget to pause rotation, reload the folder, jump straight to that folder,
or quit.

### CLI flags

| Flag | Effect |
|---|---|
| `--size N` | widget side in pixels |
| `--corner {top-left,top-right,bottom-left,bottom-right}` | which corner it docks to |
| `--rotate-seconds N` | seconds between automatic photo changes |
| `--caption "text"` | text shown under the photo (`""` to hide it) |
| `--install-autostart` | enable launch on login, then exit |
| `--uninstall-autostart` | disable launch on login, then exit |
| `--version` | print the version |

Flags override `config.json` for that run only. To change the defaults
permanently, edit `~/.config/do-it-for-her/config.json` (see
[`config.example.json`](config.example.json) for every field) — it's
created automatically on first run.

## Uninstall

```bash
./uninstall.sh
```

This removes the autostart entry and the installed package. Your photos and
config under `~/.config/do-it-for-her/` are left untouched — delete that
folder yourself if you want them gone too.

## How it works

- `src/doitforher/widget.py` — the Tkinter window: layout, image rotation,
  drag-to-move, right-click menu.
- `src/doitforher/config.py` — XDG-aware paths plus the `Config` dataclass
  that's loaded from / saved to `config.json`.
- `src/doitforher/autostart.py` — writes/removes the `.desktop` autostart entry.
- `src/doitforher/cli.py` — argument parsing and the `do-it-for-her` entry point.

## Known limitations

- "Always on top" relies on Tkinter's `-topmost`/`-type dock` hints; some
  window managers (particularly pure Wayland compositors without XWayland)
  may not honor it perfectly.
- No notion of multiple monitors beyond the primary one reported by Tkinter.

## License

MIT — see [LICENSE](LICENSE).
