#!/usr/bin/env sh
set -eu

SCRIPT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
cd "$SCRIPT_DIR"

VENV_DIR="$SCRIPT_DIR/.venv"
PYTHON_EXE="$VENV_DIR/bin/python"
PIP_EXE="$VENV_DIR/bin/pip"
NEED_INSTALL=0

if [ "${1:-}" = "install" ]; then
  NEED_INSTALL=1
fi

if ! command -v python3 >/dev/null 2>&1; then
  echo "python3 not found. Please install Python 3.10+ and try again."
  exit 1
fi

if [ ! -x "$PYTHON_EXE" ]; then
  echo "[1/3] Creating virtual environment..."
  python3 -m venv "$VENV_DIR"
  NEED_INSTALL=1
fi

if [ "$NEED_INSTALL" -eq 1 ]; then
  echo "[2/3] Installing dependencies..."
  "$PIP_EXE" install -r "$SCRIPT_DIR/requirements.txt"
else
  echo "[2/3] Skip dependency install. (run: ./start.sh install)"
fi

echo "[3/3] Starting desktop hotkey app..."
exec "$PYTHON_EXE" "$SCRIPT_DIR/desktop_hotkey.py"
