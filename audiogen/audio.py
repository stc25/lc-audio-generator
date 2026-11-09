"""Assemble synthesized lines into one audio file per dialogue."""

from __future__ import annotations

import shutil
import subprocess
import wave
from pathlib import Path
from typing import Optional

import numpy as np

TARGET_PEAK = 0.955  # about -0.4 dBFS


def silence(seconds: float, rate: int) -> np.ndarray:
    return np.zeros(max(0, int(round(seconds * rate))), dtype=np.float32)


def crossfade_free_concat(segments: list) -> np.ndarray:
    segments = [s for s in segments if s is not None and s.size]
    if not segments:
        return np.zeros(0, dtype=np.float32)
    return np.concatenate(segments).astype(np.float32)


def trim_silence(audio: np.ndarray, rate: int, threshold_db: float = -45.0,
                 keep_ms: int = 40) -> np.ndarray:
    """Trim dead air from both ends of an utterance so the pause setting is
    the only thing controlling the gap between turns."""
    if audio.size == 0:
        return audio
    thresh = 10.0 ** (threshold_db / 20.0)
    win = max(1, int(rate * 0.01))
    n_win = audio.size // win
    if n_win < 2:
        return audio
    frames = audio[: n_win * win].reshape(n_win, win)
    loud = np.max(np.abs(frames), axis=1) > thresh
    if not loud.any():
        return audio
    first, last = int(np.argmax(loud)), int(n_win - 1 - np.argmax(loud[::-1]))
    keep = int(rate * keep_ms / 1000.0)
    start = max(0, first * win - keep)
    end = min(audio.size, (last + 1) * win + keep)
    return audio[start:end]


def normalize_peak(audio: np.ndarray, target: float = TARGET_PEAK) -> np.ndarray:
    if audio.size == 0:
        return audio
    peak = float(np.max(np.abs(audio)))
    if peak <= 1e-6:
        return audio
    return (audio * (target / peak)).astype(np.float32)


def fade(audio: np.ndarray, rate: int, ms: int = 8) -> np.ndarray:
    n = min(int(rate * ms / 1000.0), audio.size // 2)
    if n <= 0:
        return audio
    ramp = np.linspace(0.0, 1.0, n, dtype=np.float32)
    audio = audio.copy()
    audio[:n] *= ramp
    audio[-n:] *= ramp[::-1]
    return audio


def write_wav(path: Path, audio: np.ndarray, rate: int) -> Path:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    pcm = np.clip(audio, -1.0, 1.0)
    pcm = (pcm * 32767.0).astype("<i2")
    with wave.open(str(path), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(int(rate))
        w.writeframes(pcm.tobytes())
    return path


def have_ffmpeg() -> bool:
    return shutil.which("ffmpeg") is not None


def encode(
    wav_path: Path,
    out_path: Path,
    fmt: str = "mp3",
    bitrate: str = "128k",
    tags: Optional[dict] = None,
) -> Path:
    """Transcode a wav to mp3/m4a/opus/flac with metadata via ffmpeg."""
    wav_path, out_path = Path(wav_path), Path(out_path)
    if fmt == "wav":
        if out_path != wav_path:
            shutil.copy2(wav_path, out_path)
        return out_path
    if not have_ffmpeg():
        raise RuntimeError(
            "ffmpeg is required for non-wav output. Install it "
            "(Ubuntu/WSL: sudo apt install ffmpeg) or choose WAV."
        )
    codec = {"mp3": ["-c:a", "libmp3lame", "-b:a", bitrate],
             "m4a": ["-c:a", "aac", "-b:a", bitrate],
             "opus": ["-c:a", "libopus", "-b:a", "64k"],
             "flac": ["-c:a", "flac"]}.get(fmt)
    if codec is None:
        raise ValueError(f"Unsupported output format: {fmt}")

    meta = []
    for k, v in (tags or {}).items():
        if v not in (None, ""):
            meta += ["-metadata", f"{k}={v}"]

    out_path.parent.mkdir(parents=True, exist_ok=True)
    cmd = ["ffmpeg", "-y", "-loglevel", "error", "-i", str(wav_path),
           "-ac", "1", *codec, *meta, str(out_path)]
    proc = subprocess.run(cmd, capture_output=True, text=True)
    if proc.returncode != 0:
        raise RuntimeError(f"ffmpeg failed: {proc.stderr.strip()[:500]}")
    return out_path


def to_srt_time(t: float) -> str:
    ms = int(round(t * 1000))
    h, ms = divmod(ms, 3600000)
    m, ms = divmod(ms, 60000)
    s, ms = divmod(ms, 1000)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


def write_srt(path: Path, cues: list) -> Path:
    """cues: [{start, end, speaker, text}]"""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    out = []
    for i, c in enumerate(cues, 1):
        out.append(str(i))
        out.append(f"{to_srt_time(c['start'])} --> {to_srt_time(c['end'])}")
        who = c.get("display") or c.get("speaker") or ""
        out.append(f"{who}: {c['text']}" if who else c["text"])
        out.append("")
    path.write_text("\n".join(out), encoding="utf-8")
    return path


# ------------------------------------------------ loudness / resampling

def match_loudness(audio, target_dbfs: float = -20.0, max_gain_db: float = 18.0):
    """Scale an utterance so its RMS sits at target_dbfs, then guard the peak."""
    if audio.size == 0:
        return audio
    rms = float(np.sqrt(np.mean(np.square(audio, dtype=np.float64))))
    if rms < 1e-6:
        return audio
    gain_db = target_dbfs - 20.0 * np.log10(rms)
    gain_db = max(-max_gain_db, min(max_gain_db, gain_db))
    out = audio * (10.0 ** (gain_db / 20.0))
    peak = float(np.max(np.abs(out)))
    if peak > 0.98:
        out = out * (0.98 / peak)
    return out.astype(np.float32)


def resample(audio, src_rate: int, dst_rate: int):
    """Linear resample (used only to bring voices to a common working rate)."""
    if src_rate == dst_rate or audio.size == 0:
        return audio
    n_out = int(round(audio.size * dst_rate / float(src_rate)))
    x_old = np.linspace(0.0, 1.0, num=audio.size, endpoint=False, dtype=np.float64)
    x_new = np.linspace(0.0, 1.0, num=n_out, endpoint=False, dtype=np.float64)
    return np.interp(x_new, x_old, audio).astype(np.float32)
