#!/usr/bin/env bash
# Linux / WSL / macOS: makes a virtual environment on first run, then starts the UI.
set -euo pipefail
cd "$(dirname "$0")"
if [ ! -x .venv/bin/python ]; then
  echo "First run: creating virtual environment..."
  python3 -m venv .venv
  ./.venv/bin/pip install --upgrade pip -q
  ./.venv/bin/pip install -r requirements.txt
fi
if ! command -v ffmpeg >/dev/null 2>&1; then
  echo "note: ffmpeg not found - audio cannot be generated until it is installed"
  echo "      Linux/WSL: sudo apt install ffmpeg      macOS: brew install ffmpeg"
fi
exec ./.venv/bin/python run.py "$@"
