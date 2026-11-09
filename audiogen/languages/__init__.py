"""Language packs.

One module per language (`audiogen/languages/<code>.py`). A pack is plain data
plus a few helpers; it imports nothing from the rest of the app. Use
`load(code)` to get one, `AVAILABLE` for the ordered list of codes and
`summary()` for a UI-friendly description of each.
"""

import importlib

# Ordered alphabetically by English name.
AVAILABLE = ("ar", "bsl", "zh", "fr", "de", "el", "he", "it", "ja", "ko",
             "la", "fa", "pt", "ru", "es", "sw", "tr")

ALIASES = {
    "arabic": "ar", "msa": "ar",
    "bsl": "bsl", "british-sign-language": "bsl", "british sign language": "bsl",
    "british_sign_language": "bsl", "sign": "bsl", "sign-language": "bsl",
    "chinese": "zh", "mandarin": "zh", "zh-cn": "zh", "zh_cn": "zh",
    "zh-tw": "zh", "zh-hans": "zh", "zh-hant": "zh", "cantonese": "zh",
    "french": "fr", "francais": "fr", "français": "fr",
    "german": "de", "deutsch": "de",
    "greek": "el", "gr": "el", "ellinika": "el", "ελληνικά": "el",
    "hebrew": "he", "iw": "he", "ivrit": "he", "עברית": "he",
    "italian": "it", "italiano": "it",
    "japanese": "ja", "jp": "ja", "nihongo": "ja",
    "korean": "ko", "kr": "ko", "hangul": "ko",
    "latin": "la", "latina": "la", "lat": "la",
    "persian": "fa", "farsi": "fa", "fa-ir": "fa",
    "portuguese": "pt", "portugues": "pt", "português": "pt",
    "pt-br": "pt", "pt-pt": "pt",
    "russian": "ru",
    "spanish": "es", "espanol": "es", "español": "es", "castellano": "es",
    "swahili": "sw", "kiswahili": "sw",
    "turkish": "tr", "turkce": "tr", "türkçe": "tr",
}

_CACHE: dict = {}


def resolve(code: str) -> str:
    """Canonical pack code for a code, name or alias; ValueError if unknown."""
    key = (code or "").strip().lower()
    if key in AVAILABLE:
        return key
    key = ALIASES.get(key) or ALIASES.get(key.replace("_", "-"))
    if key in AVAILABLE:
        return key
    raise ValueError(
        f"Unknown language {code!r}. Available: {', '.join(AVAILABLE)}")


def load(code: str):
    """Import and return the language pack module for `code`."""
    key = resolve(code)
    if key not in _CACHE:
        _CACHE[key] = importlib.import_module(f"{__name__}.{key}")
    return _CACHE[key]


def summary() -> list:
    """One dict per language: code, name, native, rtl, note."""
    out = []
    for code in AVAILABLE:
        p = load(code)
        out.append({"code": p.CODE, "name": p.NAME, "native": p.NATIVE,
                    "rtl": bool(getattr(p, "RTL", False)),
                    "note": p.VARIANTS_NOTE})
    return out
