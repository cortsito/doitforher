#!/usr/bin/env bash
# Installs do-it-for-her with pipx (falls back to `pip install --user`)
# and offers to enable autostart on login.
set -euo pipefail

cd "$(dirname "${BASH_SOURCE[0]}")"

if command -v pipx >/dev/null 2>&1; then
    pipx install --force .
    RUN="do-it-for-her"
elif python3 -m pip --version >/dev/null 2>&1; then
    python3 -m pip install --user .
    RUN="python3 -m doitforher"
else
    echo "No se encontró pipx ni pip. Instala Python 3 + pip e intenta de nuevo." >&2
    exit 1
fi

echo "Instalado. Prueba con: $RUN"

read -r -p "¿Activar inicio automático al iniciar sesión? [s/N] " answer
case "$answer" in
    [sS]*) $RUN --install-autostart ;;
    *) echo "Puedes activarlo luego con: $RUN --install-autostart" ;;
esac
