#!/usr/bin/env sh
set -eu

SCRIPT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
cd "$SCRIPT_DIR"

VENV_DIR="$SCRIPT_DIR/.venv"
PYTHON_EXE="$VENV_DIR/bin/python"
PIP_EXE="$VENV_DIR/bin/pip"

echo "[1/3] Checking Python..."
if ! command -v python3 >/dev/null 2>&1; then
  echo "python3 not found. Please install Python 3.10+ and try again."
  exit 1
fi

if ! python3 -c "import sys; raise SystemExit(0 if sys.version_info >= (3, 10) else 1)"; then
  echo "Python 3.10+ is required. Please upgrade Python and try again."
  exit 1
fi

if [ ! -x "$PYTHON_EXE" ]; then
  echo "[2/3] Creating virtual environment..."
  python3 -m venv "$VENV_DIR"
else
  echo "[2/3] Virtual environment already exists."
fi

echo "[3/3] Installing dependencies..."
"$PIP_EXE" install -r "$SCRIPT_DIR/requirements.txt"

echo
echo "Install completed successfully."
