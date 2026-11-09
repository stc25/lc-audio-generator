"""Persisted app settings (JSON on disk next to the data folder)."""

from __future__ import annotations

import json
from pathlib import Path

from .lang import PACK
from .parser import default_skip_headings

def defaults() -> dict:
    return {
        "source_path": "",
        "engine": "edge",
        "accent": PACK.DEFAULT_ACCENT,
        "speak_intro": False,
        "narrator_voice": "",
        "narrator_rate": 0.95,
        "intro_pause_ms": 900,
        "scene_pause_ms": 1100,
        "spell_out": True,
        "default_rate": 1.0,
        "pause_ms": 650,
        "lead_ms": 300,
        "tail_ms": 700,
        "fmt": "mp3",
        "bitrate": "128k",
        "trim": True,
        "use_cache": True,
        "write_srt": False,
        "write_transcript": True,
        "speak_stage_directions": False,
        "capture_translations": True,
        "naming": "structured",
        "skip_headings": default_skip_headings(),
        "filename_template": "{index:02d}-{slug}",
        "album": f"{PACK.NAME} dialogues",
        "output_dir": "",
        "voices": {},          # speaker name -> {voice, speaker_id, rate}
    }


class Settings(dict):
    def __init__(self, path: Path):
        super().__init__()
        self.path = Path(path)
        self.defaults = defaults()
        self.update(self.defaults)
        self.load()

    def load(self):
        if self.path.is_file():
            try:
                data = json.loads(self.path.read_text(encoding="utf-8"))
                if isinstance(data, dict):
                    for k, v in data.items():
                        if k in self.defaults:
                            self[k] = v
            except Exception:
                pass
        self.repair()
        return self

    def save(self):
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(
            json.dumps(dict(self), ensure_ascii=False, indent=2), encoding="utf-8"
        )
        return self

    def apply(self, patch: dict):
        for k, v in (patch or {}).items():
            if k in self.defaults:
                self[k] = v
        self.repair()
        return self.save()

    def repair(self) -> list:
        """Put back the default for any value that cannot survive a round trip.

        A NaN or infinity reaching the browser makes the whole settings
        response unparseable, which leaves the page with no state at all — a
        failure that shows up much later and nowhere near its cause. Names the
        keys it reset so the caller can say so."""
        fixed = []
        for k, default in self.defaults.items():
            v = self.get(k)
            if isinstance(v, float) and (v != v or v in (float("inf"),
                                                         float("-inf"))):
                self[k] = default
                fixed.append(k)
            elif isinstance(default, (int, float)) \
                    and not isinstance(default, bool) \
                    and isinstance(v, str):
                try:
                    self[k] = type(default)(v)
                except (TypeError, ValueError):
                    self[k] = default
                    fixed.append(k)
        return fixed


def settings_for(data_dir, code: str) -> "Settings":
    """Per-language settings file: data/settings/<code>.json"""
    from .lang import use
    with use(code):
        return Settings(Path(data_dir) / "settings" / f"{code}.json")
