#!/usr/bin/env bash
# Removes autostart and uninstalls the do-it-for-her package.
set -euo pipefail

if command -v do-it-for-her >/dev/null 2>&1; then
    do-it-for-her --uninstall-autostart || true
fi

if command -v pipx >/dev/null 2>&1 && pipx list --short 2>/dev/null | grep -q '^do-it-for-her '; then
    pipx uninstall do-it-for-her
elif python3 -m pip show do-it-for-her >/dev/null 2>&1; then
    python3 -m pip uninstall -y do-it-for-her
else
    echo "do-it-for-her no parece estar instalado." >&2
fi

echo "Nota: tus fotos y config siguen en ~/.config/do-it-for-her/ — bórralo a mano si ya no lo quieres."
