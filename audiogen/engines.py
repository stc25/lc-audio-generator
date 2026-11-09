"""edge-tts engine and the voice registry.

A voice is addressed by a reference string "edge:<ShortName>", e.g.
"edge:es-MX-DaliaNeural". A bare ShortName is accepted too.
"""
from __future__ import annotations

import asyncio
import shutil
import subprocess
from typing import Optional

import numpy as np

from . import voices as V
from .audio import match_loudness

EDGE_RATE = 24000
DEFAULT_ENGINE = "edge"


def parse_ref(ref: str) -> tuple:
    """'edge:fr-FR-HenriNeural' -> ('edge', 'fr-FR-HenriNeural', None)."""
    ref = (ref or "").strip()
    if ref.startswith("edge:"):
        ref = ref[5:]
    voice, _, spk = ref.partition("#")
    return "edge", voice, (int(spk) if spk.isdigit() else None)


def make_ref(engine: str, voice: str, speaker_id: Optional[int] = None) -> str:
    return f"edge:{voice}"


def module():
    try:
        import edge_tts
        return edge_tts
    except Exception:
        return None


def unavailable_reason() -> str:
    if module() is None:
        return "edge-tts is not installed. Run:  pip install edge-tts"
    if shutil.which("ffmpeg") is None:
        return "ffmpeg is required to decode edge-tts audio (see README)."
    return ""


def available() -> bool:
    return not unavailable_reason()


def _decode_mp3(data: bytes, rate: int) -> np.ndarray:
    proc = subprocess.run(
        ["ffmpeg", "-loglevel", "error", "-i", "pipe:0",
         "-f", "f32le", "-ac", "1", "-ar", str(rate), "pipe:1"],
        input=data, capture_output=True)
    if proc.returncode != 0 or not proc.stdout:
        raise RuntimeError(f"Could not decode audio: {proc.stderr.decode()[:300]}")
    return np.frombuffer(proc.stdout, dtype="<f4").astype(np.float32)


def synth_voice(text: str, voice: str, rate: float = 1.0, pitch_hz: int = 0,
                target_dbfs: Optional[float] = -20.0) -> tuple:
    edge_tts = module()
    if edge_tts is None:
        raise RuntimeError(unavailable_reason())
    text = (text or "").strip()
    if not text:
        return np.zeros(0, dtype=np.float32), EDGE_RATE
    pct = int(round((float(rate or 1.0) - 1.0) * 100))
    kw = {"rate": f"{pct:+d}%"}
    if pitch_hz:
        kw["pitch"] = f"{int(pitch_hz):+d}Hz"

    async def pull():
        comm = edge_tts.Communicate(text, voice, **kw)
        buf = bytearray()
        async for chunk in comm.stream():
            if chunk.get("type") == "audio" and chunk.get("data"):
                buf += chunk["data"]
        return bytes(buf)

    last, mp3 = None, b""
    for attempt in range(4):                 # transient 403s/timeouts happen
        try:
            mp3 = asyncio.run(pull())
            if mp3:
                break
            last = RuntimeError("edge-tts returned no audio")
        except Exception as e:               # noqa: BLE001
            last = e
        import time
        time.sleep(0.6 * (attempt + 1))
    if not mp3:
        raise RuntimeError(f"edge-tts failed for {voice}: {last}. "
                           "Check your internet connection.")
    audio = _decode_mp3(mp3, EDGE_RATE)
    if target_dbfs is not None:
        audio = match_loudness(audio, target_dbfs)
    return audio, EDGE_RATE


class Registry:
    """The voices for one language, behind the interface generate.py expects."""

    def __init__(self, pack):
        self.pack = pack
        self.edge = self

    # availability -------------------------------------------------------
    def available(self) -> bool:
        return available()

    def unavailable_reason(self) -> str:
        return unavailable_reason()

    # catalogue ----------------------------------------------------------
    def catalogue(self) -> list:
        ready = self.available()
        out = []
        labels = getattr(self.pack, "ACCENTS", {}) or {}
        for v in V.voices_for(self.pack):
            out.append({**v, "engine": "edge", "ref": f"edge:{v['key']}",
                        "accent": labels.get(v["locale"], v["locale_name"]),
                        "lang": v["locale"], "quality": "neural",
                        "installed": ready, "ready": ready, "speakers": [],
                        "sample_rate": EDGE_RATE, "size_mb": None,
                        "note": ", ".join(v["personalities"])})
        return out

    def ready_voices(self) -> list:
        return [c for c in self.catalogue() if c["ready"]]

    def known(self, voice: str) -> bool:
        return any(v["key"] == voice for v in V.all_voices())

    def is_ready(self, ref: str) -> bool:
        _, voice, _ = parse_ref(ref)
        return self.available() and self.known(voice)

    def why_not_ready(self, ref: str) -> str:
        _, voice, _ = parse_ref(ref)
        if not self.known(voice):
            return (f"{voice!r} is not an edge-tts voice in the catalogue "
                    "(run `audiogen voices --refresh` to update it).")
        return self.unavailable_reason()

    def sample_rate(self, ref: str) -> int:
        return EDGE_RATE

    def speakers(self, ref: str) -> list:
        return [{"id": 0, "label": "default"}]

    # synthesis ----------------------------------------------------------
    def synth(self, text, ref, speaker_id=None, rate=1.0) -> tuple:
        _, voice, _ = parse_ref(ref)
        return synth_voice(text, voice, rate=rate)

    def default_pair(self, engine_or_accent: str, accent: str = None) -> dict:
        """Accepts (engine, accent) for compatibility, or just (accent)."""
        loc = accent if accent is not None else engine_or_accent
        pair = V.default_pair(self.pack, loc)
        return {k: f"edge:{v}" for k, v in pair.items() if v}

    def unload(self):
        pass


_registries: dict = {}


def registry_for(code: str) -> Registry:
    from .languages import load
    pack = load(code)
    if pack.CODE not in _registries:
        _registries[pack.CODE] = Registry(pack)
    return _registries[pack.CODE]
