#!/usr/bin/env python3
"""Refresh audiogen/data/edge_voices.json from Microsoft's live voice list.

  .venv/bin/python tools/build_voice_catalogue.py

Needs internet. The app ships with a snapshot so it works without this; the UI
and `audiogen voices --refresh` call the same code to update it later.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from audiogen.voices import refresh_snapshot  # noqa: E402

if __name__ == "__main__":
    n = refresh_snapshot()
    print(f"wrote {n} voices")
