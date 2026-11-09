"""The edge-tts voice catalogue: a shipped snapshot, refreshable from Microsoft.

Voices are grouped per language through the language pack's EDGE_LOCALES (the
Latin and BSL packs point at Italian and English voices respectively). Every
voice Microsoft lists for those locales is exposed, including regional
dialect voices (zh-CN-liaoning, zh-CN-shaanxi, ar-EG ...), plus the handful of
"Multilingual" voices, which can read any language.
"""
from __future__ import annotations

import asyncio
import json
import threading
from pathlib import Path

SNAPSHOT = Path(__file__).resolve().parent / "data" / "edge_voices.json"
_lock = threading.Lock()
_cache: list | None = None


def _normalise(raw: dict) -> dict:
    short = raw["ShortName"]
    loc = raw["Locale"]
    tag = raw.get("VoiceTag") or {}
    friendly = raw.get("FriendlyName", "")
    return {
        "key": short,
        "gender": {"Female": "F", "Male": "M"}.get(raw.get("Gender", ""), "?"),
        "locale": loc.replace("-", "_"),
        "locale_name": raw.get("LocaleName") or (friendly.split(" - ")[-1] if " - " in friendly else loc),
        "name": short[len(loc) + 1:].replace("Neural", ""),
        "personalities": tag.get("VoicePersonalities", []),
        "categories": tag.get("ContentCategories", []),
        "multilingual": "Multilingual" in short,
    }


def refresh_snapshot() -> int:
    """Download the live list and overwrite the snapshot. Returns the count."""
    import edge_tts
    raw = asyncio.run(edge_tts.list_voices())
    voices = sorted((_normalise(v) for v in raw), key=lambda v: (v["locale"], v["gender"], v["name"]))
    SNAPSHOT.parent.mkdir(parents=True, exist_ok=True)
    SNAPSHOT.write_text(json.dumps(voices, ensure_ascii=False, indent=1), encoding="utf-8")
    global _cache
    with _lock:
        _cache = voices
    return len(voices)


def all_voices() -> list:
    global _cache
    with _lock:
        if _cache is None:
            try:
                _cache = json.loads(SNAPSHOT.read_text(encoding="utf-8"))
            except FileNotFoundError:
                _cache = []
        return _cache


def voices_for(pack, include_multilingual: bool = True) -> list:
    """Every voice usable for a language pack, own locales first."""
    prefixes = tuple(p.replace("-", "_") for p in pack.EDGE_LOCALES)
    own = [v for v in all_voices() if v["locale"].startswith(prefixes)]
    if include_multilingual:
        have = {v["key"] for v in own}
        own += [dict(v, borrowed=True) for v in all_voices()
                if v["multilingual"] and v["key"] not in have]
    return own


def locales_for(pack) -> list:
    """[(locale, label, n_voices)] for the language, ordered with the pack's
    default first, then by size."""
    count: dict = {}
    for v in voices_for(pack, include_multilingual=False):
        count[v["locale"]] = count.get(v["locale"], 0) + 1
    labels = getattr(pack, "ACCENTS", {}) or {}
    names = {}
    for v in voices_for(pack, include_multilingual=False):
        names.setdefault(v["locale"], v["locale_name"])
    default = getattr(pack, "DEFAULT_ACCENT", "")
    order = sorted(count, key=lambda l: (l != default, -count[l], l))
    return [(l, labels.get(l) or names.get(l, l), count[l]) for l in order]


def _score(v: dict) -> tuple:
    """Prefer plain general-purpose voices over cartoon/multilingual ones."""
    cats = v.get("categories") or []
    return (v.get("multilingual", False), "General" not in cats
            and "Conversation" not in cats, "Cartoon" in cats)


def norm_locale(pack, loc: str) -> str:
    """'es-mx' / 'ES_MX' -> 'es_MX' (the spelling the catalogue uses)."""
    want = (loc or "").replace("-", "_").lower()
    for v in voices_for(pack, include_multilingual=False):
        if v["locale"].lower() == want:
            return v["locale"]
    return loc.replace("-", "_") if loc else pack.DEFAULT_ACCENT


def default_pair(pack, locale: str) -> dict:
    """{'M': key, 'F': key, 'M2': key, 'F2': key} for a locale.

    Uses the pack's PREFERRED_PAIRS when it names a voice that exists, else the
    best voices the locale has. A gender the locale lacks is filled from the
    pack's default locale, so M and F are always two different voices."""
    locale = norm_locale(pack, locale)
    known = {v["key"] for v in all_voices()}
    pref = (getattr(pack, "PREFERRED_PAIRS", {}) or {}).get(locale, {})
    own = sorted((v for v in voices_for(pack, include_multilingual=False)
                  if v["locale"] == locale), key=_score)
    out: dict = {}
    for g in ("M", "F"):
        if pref.get(g) in known:
            out[g] = pref[g]
            continue
        pick = next((v["key"] for v in own if v["gender"] == g), None)
        if pick:
            out[g] = pick
    for g in ("M", "F"):
        if g not in out:
            fb = default_pair(pack, pack.DEFAULT_ACCENT) if locale != pack.DEFAULT_ACCENT else {}
            alt = fb.get(g) or next((v["key"] for v in voices_for(pack) if v["gender"] == g), None)
            out[g] = alt or next(iter(out.values()), "")
    for g in ("M", "F"):
        extra = [v["key"] for v in own if v["gender"] == g and v["key"] != out[g]]
        if extra:
            out[g + "2"] = extra[0]
    return out
