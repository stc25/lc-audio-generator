"""Language-independent speaker-gender guessing, driven by a language pack.

Order of evidence, strongest first:
  1. a title pattern on the whole label   ("Prof.ssa Bianchi", "Mme Girard")
  2. an article on the whole label        ("La receptionniste", "L'employe")
  3. an explicit role word                ("Vendeuse", "Cameriere")
  4. a known first name                   ("Lea", "Marco")
  5. a morphological suffix               ("-euse" -> F, "-ore" -> M)
Names that are used for either gender (Camille, Andrea) and nouns identical in
both (receptionniste, farmacista) return unknown on purpose: alternating is
more useful than a coin-flip dressed up as a guess.
Anything in the pack's EPICENE set short-circuits to unknown, because guessing
from morphology there is worse than alternating.
"""

from __future__ import annotations

import re
import unicodedata

_WORD_SPLIT = re.compile(r"[^\w\s]+", re.UNICODE)
_WS = re.compile(r"\s+")


def deaccent(s: str) -> str:
    return "".join(c for c in unicodedata.normalize("NFD", s)
                   if unicodedata.category(c) != "Mn")


def norm(label: str) -> str:
    """Lowercased, punctuation-flattened label. Accents are preserved because
    they carry gender in French (employe vs employee stay distinct anyway, but
    e.g. 'ne' vs 'nee' does not)."""
    t = (label or "").strip().replace("İ", "i").replace("İ", "i").lower()
    t = _WORD_SPLIT.sub(" ", t)
    return _WS.sub(" ", t).strip()


def _lookup(word: str, exact: set, loose: dict, prefixes=()):
    """Exact match first, then an accent-insensitive match that is only
    consulted for words whose de-accented form is unambiguous.

    `prefixes` covers languages that attach the article to the word, as Arabic
    does with ال: النادل has to be found under نادل.
    """
    if word in exact:
        return True
    if loose.get(deaccent(word), False):
        return True
    for pre in prefixes:
        if word.startswith(pre) and len(word) > len(pre) + 1:
            stem = word[len(pre):]
            if stem in exact or loose.get(deaccent(stem), False):
                return True
    return False


def _loose_index(female: set, male: set) -> tuple:
    """De-accented lookup tables, excluding forms that would collide across
    genders. This is what keeps French 'employe' (M) apart from 'employee' (F)
    while still matching 'Lea' typed without its accent."""
    fd, md = {}, {}
    for w in female:
        fd.setdefault(deaccent(w), 0)
        fd[deaccent(w)] += 1
    for w in male:
        md.setdefault(deaccent(w), 0)
        md[deaccent(w)] += 1
    clash = set(fd) & set(md)
    return ({k: True for k in fd if k not in clash},
            {k: True for k in md if k not in clash})


_CACHE: dict = {}


def _tables(pack):
    key = id(pack)
    if key not in _CACHE:
        _CACHE[key] = {
            "names": _loose_index(pack.FEMALE_NAMES, pack.MALE_NAMES),
            "roles": _loose_index(pack.FEMALE_ROLES, pack.MALE_ROLES),
        }
    return _CACHE[key]


def guess_gender_conf(label: str, pack) -> tuple:
    """Return (gender, source) with gender in {'F','M','?'} and source in
    {'title','article','role','name','morph','none'}."""
    raw = norm(label)
    if not raw:
        return "?", "none"
    tables = _tables(pack)
    prefixes = tuple(getattr(pack, "ARTICLE_PREFIXES", ()) or ())
    words = [w for w in raw.split() if w]

    # 1. titles, matched against the original label so "Prof.ssa" survives
    low = (label or "").lower()
    for rx, g in getattr(pack, "TITLE_PATTERNS", ()):
        if re.search(rx, low):
            return g, "title"

    # short-circuit genuinely epicene labels before any guessing
    stripped = [w for w in words if w not in getattr(pack, "ARTICLES", set())]
    core = stripped[-1] if stripped else raw
    if raw in pack.EPICENE or core in pack.EPICENE:
        # an article can still settle it ("la receptionniste")
        for art, g in getattr(pack, "ARTICLE_GENDER", {}).items():
            if words and words[0] == art:
                return g, "article"
        return "?", "none"

    # 1b. names used for either gender: do not let morphology decide
    unisex = getattr(pack, "UNISEX_NAMES", set())
    if core in unisex or (words and words[0] in unisex):
        return "?", "unisex"

    # 2. articles
    for art, g in getattr(pack, "ARTICLE_GENDER", {}).items():
        if words and words[0] == art:
            # only trust the article if the noun itself gives nothing stronger
            if not (_lookup(core, pack.FEMALE_NAMES, tables["names"][0],
                            prefixes)
                    or _lookup(core, pack.MALE_NAMES, tables["names"][1],
                               prefixes)):
                fem = _lookup(core, pack.FEMALE_ROLES, tables["roles"][0],
                              prefixes)
                masc = _lookup(core, pack.MALE_ROLES, tables["roles"][1],
                               prefixes)
                if fem and not masc:
                    return "F", "role"
                if masc and not fem:
                    return "M", "role"
                return g, "article"

    # 3. role words
    for w in stripped:
        if _lookup(w, pack.FEMALE_ROLES, tables["roles"][0], prefixes):
            return "F", "role"
        if _lookup(w, pack.MALE_ROLES, tables["roles"][1], prefixes):
            return "M", "role"

    # 4. known first names
    for w in stripped:
        if _lookup(w, pack.FEMALE_NAMES, tables["names"][0], prefixes):
            return "F", "name"
        if _lookup(w, pack.MALE_NAMES, tables["names"][1], prefixes):
            return "M", "name"

    # 5. morphology, lowest confidence
    g = pack.morph(core)
    if g:
        return g, "morph"
    return "?", "none"
