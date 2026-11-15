#!/usr/bin/env bash
# Launch Bilibili 必剪 (Bcut) Windows desktop edition under Wine.
set -euo pipefail
export WINEPREFIX="${WINEPREFIX:-/home/box/.wine-bcut}"
export WINEARCH=win64
export DISPLAY="${DISPLAY:-:2}"
export LANG="${LANG:-zh_CN.UTF-8}"
export LC_ALL="${LC_ALL:-zh_CN.UTF-8}"
export WINEDLLOVERRIDES="${WINEDLLOVERRIDES:-mscoree,mshtml=}"
BCUT_EXE="${WINEPREFIX}/drive_c/Bcut/BCUT.exe"
if [[ ! -x "$BCUT_EXE" && ! -f "$BCUT_EXE" ]]; then
  echo "必剪 is not installed at $BCUT_EXE" >&2
  exit 1
fi
cd "${WINEPREFIX}/drive_c/Bcut"
exec wine "C:\\Bcut\\BCUT.exe" "$@"
