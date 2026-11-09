"""Text tidying applied just before synthesis."""

from __future__ import annotations

import re

# D-I-E-G-O  /  M-A-R-T-A  ->  "D, I, E, G, O" so espeak-ng says each letter
# name instead of trying to pronounce it as one word. Needs 3+ capitals so
# ordinary hyphenated words are untouched.
RE_SPELLED = re.compile(
    r"\b([A-ZÁÉÍÓÚÜÑ])"
    r"((?:[-‐‑–—][A-ZÁÉÍÓÚÜÑ]){2,})\b"
)
RE_SPLIT = re.compile(r"[-‐‑–—]")

# Collapse runs of the same punctuation and tidy whitespace.
RE_WS = re.compile(r"\s+")
RE_DOTS = re.compile(r"\.{4,}")
CJK_PUNCT = "。！？…：；，、）》」』"


def _has_cjk(t: str) -> bool:
    return any("\u4e00" <= c <= "\u9fff" for c in t)


def _has_arabic(t: str) -> bool:
    return any("\u0600" <= c <= "\u06ff" or "\u0750" <= c <= "\u077f"
               for c in t)


def _non_latin(t: str) -> bool:
    return _has_cjk(t) or _has_arabic(t)


def _ends_with_cjk_punct(t: str) -> bool:
    return bool(t) and t[-1] in CJK_PUNCT


def spell_out(text: str) -> str:
    def sub(m):
        letters = [m.group(1)] + [c for c in RE_SPLIT.split(m.group(2)) if c]
        return ", ".join(letters)
    return RE_SPELLED.sub(sub, text)


def speech_text(text: str, pack=None) -> tuple:
    """Apply a language's script conversion, if it has one.

    Chinese course files are written in pinyin but every Mandarin engine reads
    characters, so the pack supplies a transform. Returns (text, unmapped).
    """
    if pack is None:
        from .lang import PACK as pack
    fn = getattr(pack, "SPEECH_TRANSFORM", None)
    if fn is None:
        return text, []
    out = fn(text or "")
    if isinstance(out, tuple):
        return out[0], list(out[1] or [])
    return out, []


def prepare(text: str, spell: bool = True, pack=None) -> str:
    """Normalise one utterance for the TTS engine."""
    t, _ = speech_text(text, pack)
    t = (t or "").strip()
    if not t:
        return t
    t = t.replace("’", "'").replace("‘", "'")
    t = t.replace("“", '"').replace("”", '"')
    if not _non_latin(t):
        t = t.replace("–", " - ").replace("—", " - ")
    t = RE_DOTS.sub("...", t)
    if spell and not _non_latin(t):
        t = spell_out(t)
    t = RE_WS.sub(" ", t).strip()
    # give the voice a sentence to land on; scripts with their own full-width
    # punctuation are left as they are
    if t and t[-1] not in ".!?…:;،؛؟" and not _ends_with_cjk_punct(t):
        if _has_cjk(t):
            t += "\u3002"
        else:
            t += "."
    return t
