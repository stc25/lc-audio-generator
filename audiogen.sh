#!/usr/bin/env bash
# CLI launcher for Linux / WSL / macOS: ./audiogen.sh <command> ...
# Builds the virtual environment on first use (same as run.sh).
set -euo pipefail
cd "$(dirname "$0")"
if [ ! -x .venv/bin/python ]; then
  echo "First run: creating virtual environment..." >&2
  python3 -m venv .venv
  ./.venv/bin/pip install --upgrade pip -q
  ./.venv/bin/pip install -r requirements.txt -q
fi
exec ./.venv/bin/python -m audiogen "$@"
