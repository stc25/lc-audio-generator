"""Everything the CLI, the web UI and the HTTP API do, in one place.

Each function takes a language code and runs inside `lang.use(code)`, so the
parser, gender guesser and voice catalogue all see the right language pack.
Nothing here prints; callers pass a `progress(event_dict)` callback.
"""
from __future__ import annotations

import re
from pathlib import Path
from typing import Callable, Optional

from . import audiolist as AL
from . import voices as V
from .audio import have_ffmpeg
from .engines import parse_ref, registry_for, unavailable_reason
from .generate import GenOptions, Generator, resolve_assignment
from .lang import use
from .languages import AVAILABLE, load
from .parser import assign_alternating, collect_speakers, parse_markdown
from .settings import settings_for

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
DEFAULT_OUT = ROOT / "output"


# ------------------------------------------------------------ languages

def language_info(code: str) -> dict:
    pack = load(code)
    locs = V.locales_for(pack)
    return {
        "code": pack.CODE, "name": pack.NAME, "native": pack.NATIVE,
        "rtl": bool(getattr(pack, "RTL", False)),
        "note": getattr(pack, "VARIANTS_NOTE", ""),
        "default_locale": pack.DEFAULT_ACCENT,
        "n_voices": len(V.voices_for(pack, include_multilingual=False)),
        "locales": [{"locale": l, "label": lab, "n": n} for l, lab, n in locs],
        "sample_text": pack.SAMPLE_TEXT,
    }


def languages() -> list:
    return [language_info(c) for c in AVAILABLE]


def voice_table(code: str) -> list:
    return registry_for(code).catalogue()


# ------------------------------------------------------------ sources

def read_source(path: str = "", text: str = "") -> tuple:
    """-> (text, display name). Accepts a path or the text itself."""
    if text:
        return text, "pasted text"
    if not path:
        raise ValueError("Give a file path or the text itself.")
    p = Path(path).expanduser()
    if not p.is_file():
        raise FileNotFoundError(f"No such file: {p}")
    try:
        return p.read_text(encoding="utf-8-sig"), p.name
    except UnicodeDecodeError:
        return p.read_text(encoding="latin-1"), p.name


def detect_kind(text: str) -> str:
    """'audio-list' when the file has tables with an ID and a save-as path,
    otherwise 'dialogues'."""
    for m in re.finditer(r"^\|\s*ID\s*\|.*$", text, re.I | re.M):
        if re.search(r"save as|file|path", m[0], re.I) or \
                re.search(r"voice.*\b(text|say)\b", m[0], re.I):
            return "audio-list"
    return "dialogues"


# ------------------------------------------------------------ dialogues

def _options(s: dict) -> GenOptions:
    return GenOptions(
        accent=s["accent"], speak_intro=bool(s["speak_intro"]),
        narrator_voice=s["narrator_voice"], narrator_rate=float(s["narrator_rate"]),
        intro_pause_ms=int(s["intro_pause_ms"]), spell_out=bool(s["spell_out"]),
        default_rate=float(s["default_rate"]), pause_ms=int(s["pause_ms"]),
        lead_ms=int(s["lead_ms"]), tail_ms=int(s["tail_ms"]), fmt=s["fmt"],
        bitrate=s["bitrate"], trim=bool(s["trim"]), use_cache=bool(s["use_cache"]),
        write_srt=bool(s["write_srt"]), write_transcript=bool(s["write_transcript"]),
        engine="edge", scene_pause_ms=int(s["scene_pause_ms"]), naming=s["naming"],
        filename_template=s["filename_template"], album=s["album"])


def parse_dialogues(code: str, text: str, settings=None) -> dict:
    with use(code):
        s = settings or settings_for(DATA, code)
        reg = registry_for(code)
        dialogues = parse_markdown(
            text, speak_stage_directions=bool(s["speak_stage_directions"]),
            capture_translations=bool(s["capture_translations"]),
            skip_headings=s["skip_headings"])
        skipped = list(getattr(parse_markdown, "last_skipped", []))
        speakers = assign_alternating(collect_speakers(dialogues))
        pack = load(code)
        saved = s["voices"] or {}
        pair = reg.default_pair("edge", s["accent"])
        for sp in speakers:
            ov = saved.get(sp["name"]) or {}
            sp["voice"] = ov.get("voice") or pair.get(sp["gender"], pair.get("M"))
            sp["rate"] = ov.get("rate")
        return {
            "language": code, "accent": s["accent"], "dialogues": dialogues,
            "skipped": skipped, "speakers": speakers, "pair": pair,
            "variety": pack.detect_accent(text) if hasattr(pack, "detect_accent") else None,
        }


def generate_dialogues(code: str, text: str, out_dir: Path, *, source_name: str = "",
                       patch: Optional[dict] = None, voices: Optional[dict] = None,
                       only=None, progress: Callable = lambda e: None,
                       save_settings: bool = True) -> dict:
    with use(code):
        s = settings_for(DATA, code)
        if patch:
            s.update({k: v for k, v in patch.items() if k in s.defaults})
        reg = registry_for(code)
        dialogues = parse_markdown(
            text, speak_stage_directions=bool(s["speak_stage_directions"]),
            capture_translations=bool(s["capture_translations"]),
            skip_headings=s["skip_headings"])
        if only:
            keep = {int(i) for i in only}
            dialogues = [d for d in dialogues if d.index in keep]
        if not dialogues:
            raise ValueError("No dialogues found. Dialogue lines need a 'Name:' prefix.")
        if voices:
            s["voices"] = {**(s["voices"] or {}), **voices}
        if save_settings:
            s.save()
        speakers = assign_alternating(collect_speakers(dialogues))
        opts = _options(s)
        assignment = resolve_assignment(speakers, s["voices"] or {}, opts.accent,
                                        opts.default_rate, reg, "edge")
        bad = sorted({c.voice_key for c in assignment.values() if not reg.is_ready(c.voice_key)})
        if bad:
            raise ValueError("Voices not usable: " + "; ".join(
                f"{r} ({reg.why_not_ready(r)})" for r in bad))
        gen = Generator(reg, Path(out_dir), DATA / "cache")
        manifest = gen.run(dialogues, assignment, opts, progress, source_name)
        manifest["speaker_voices"] = {k: v.voice_key for k, v in assignment.items()}
        return manifest


# ------------------------------------------------------------ audio lists

def parse_audio_list(code: str, text: str) -> AL.Plan:
    with use(code):
        pack = load(code)
        return AL.parse_list(text, pack, {v["key"] for v in V.all_voices()})


def build_renderer(code: str, plan: AL.Plan, locale: str = "", rate=None,
                   bitrate: str = "96k") -> AL.Renderer:
    with use(code):
        pack = load(code)
        return AL.Renderer(registry_for(code), locale or pack.DEFAULT_ACCENT,
                           plan, rate=rate, pack=pack, bitrate=bitrate,
                           explicit_locale=bool(locale))


def generate_list(code: str, plan: AL.Plan, out_dir: Path, *, locale: str = "",
                  rate=None, fmt: str = "mp3", force: bool = False, jobs: int = 4,
                  strip: str = "", progress: Callable = lambda e: None,
                  should_stop: Callable = lambda: False) -> dict:
    with use(code):
        r = build_renderer(code, plan, locale, rate)
        reg = registry_for(code)
        for who, name in r.refs(plan.items).items():
            if not reg.is_ready("edge:" + name):
                raise ValueError(f"Voice {name} ({who}) is not usable: "
                                 f"{reg.why_not_ready('edge:' + name)}")
        return AL.run(plan, r, Path(out_dir), fmt=fmt, force=force, jobs=jobs,
                      strip=strip, progress=progress, should_stop=should_stop)


# ------------------------------------------------------------ one phrase

def speak(code: str, text: str, out: Path, *, voice: str = "", gender: str = "F",
          locale: str = "", rate: float = 1.0, fmt: str = "") -> dict:
    """Say one piece of text and save it. `voice` is an edge-tts name; without
    it the locale's default male/female voice is used."""
    with use(code):
        pack = load(code)
        reg = registry_for(code)
        if not voice:
            pair = reg.default_pair("edge", locale or pack.DEFAULT_ACCENT)
            voice = parse_ref(pair.get(gender.upper()[:1] or "F", pair.get("F", "")))[1]
        if not reg.is_ready("edge:" + voice):
            raise ValueError(reg.why_not_ready("edge:" + voice))
        from .textprep import prepare
        audio, sr = reg.synth(prepare(text, spell=False), "edge:" + voice, rate=rate)
        if audio.size == 0:
            raise ValueError("Nothing to say (empty text).")
        out = Path(out)
        fmt = fmt or out.suffix.lstrip(".") or "mp3"
        out = out.with_suffix("." + fmt)
        size = AL.write_item(out, audio, sr, fmt)
        return {"file": str(out), "voice": voice, "bytes": size,
                "seconds": round(audio.size / sr, 2)}


def health() -> dict:
    return {"ffmpeg": have_ffmpeg(), "edge_tts": unavailable_reason() == "" or
            "ffmpeg" in unavailable_reason(), "problem": unavailable_reason(),
            "voices": len(V.all_voices())}
