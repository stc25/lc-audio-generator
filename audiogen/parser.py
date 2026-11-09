"""Turn a Markdown file into a list of dialogues with speaker-tagged lines.

The parser is deliberately forgiving because hand-written study notes are
messy. It recognises these speaker-line shapes (with optional leading list
bullet, blockquote marker or ordinal):

    Ana: Hola, buenos dias.
    **Ana:** Hola, buenos dias.
    **Ana**: Hola, buenos dias.
    *Ana:* Hola, buenos dias.
    _Ana_: Hola, buenos dias.
    - Ana: Hola, buenos dias.
    > Ana: Hola, buenos dias.
    1. Ana: Hola, buenos dias.
    ANA: Hola, buenos dias.

Dialogue boundaries come from Markdown headings; a heading with no speaker
lines beneath it (a unit or chapter title) is skipped rather than emitted as
an empty dialogue. Files with no headings fall back to splitting on
horizontal rules, then to a single dialogue.
"""

from __future__ import annotations

import hashlib
import re
import unicodedata
from dataclasses import dataclass, field, asdict
from typing import Optional

from .gender import guess_gender_conf
from .lang import PACK

# ---------------------------------------------------------------- regexes

RE_FENCE = re.compile(r"^\s*(```|~~~)")
RE_HEADING = re.compile(r"^(#{1,6})\s+(.*?)\s*#*\s*$")
RE_SETEXT_H1 = re.compile(r"^={3,}\s*$")
RE_SETEXT_H2 = re.compile(r"^-{3,}\s*$")
RE_HRULE = re.compile(r"^\s*([-*_])(?:\s*\1){2,}\s*$")
RE_PREFIX = re.compile(r"^\s*(?:>\s*)*(?:[-*+]\s+|\d{1,3}[.)]\s+)?")
RE_TRANS_TAG = re.compile(
    r"^(?:EN|ENG|English|Translation|Trad|Traduccion|Traducci\u00f3n|ES)\s*[:\-]\s*(.+)$",
    re.IGNORECASE,
)
RE_ALL_ITALIC = re.compile(r"^[*_](?!\*)(.+?)[*_]$")
RE_ALL_PAREN = re.compile(r"^\((.+)\)$")
RE_STAGE = re.compile(r"[（(\[]([^()\[\]]{2,120})[)）\]]")
RE_INLINE_MD = re.compile(r"(\*\*|__|\*|_|`|~~)")
RE_LINK = re.compile(r"\[([^\]]*)\]\([^)]*\)")
RE_IMAGE = re.compile(r"!\[[^\]]*\]\([^)]*\)")
RE_TABLE_SEP = re.compile(r"^\s*\|?[\s:\-|]+\|[\s:\-|]+$")
# a whole line that is nothing but bold text, e.g. "**Dialogue**"
RE_BOLD_LINE = re.compile(r"^(?:\*\*|__)(?!\s)(.+?)(?:\*\*|__)$")

# "Name:" candidate -- name is 1-4 words, no terminal punctuation inside
RE_SPEAKER = re.compile(
    r"^(?P<open>\*\*|__|\*|_)?"
    r"(?P<name>[^\s:*_][^:*_\n]{0,48}?)"
    r"(?P<close>\*\*|__|\*|_)?"
    r"\s*:\s*"
    r"(?P<text>.*)$"
)

MAX_NAME_WORDS = 4

# Pulled from the active language pack so one codebase serves every language.
# Resolved lazily: the active language can change between calls.
class _LazySet:
    def __init__(self, attr, extra=()):
        self.attr, self.extra = attr, set(extra)

    def _s(self):
        return set(getattr(PACK, self.attr)) | self.extra

    def __contains__(self, x):
        return x in self._s()

    def __iter__(self):
        return iter(self._s())


def default_skip_headings() -> list:
    return list(PACK.SKIP_HEADINGS)


def _speech_transform():
    return getattr(PACK, "SPEECH_TRANSFORM", None)


CONSOLIDATION_HEADINGS = _LazySet("CONSOLIDATION_HEADINGS")
NON_SPEAKER_LABELS = _LazySet("NON_SPEAKER_LABELS")

# Headings that repeat throughout a workbook and so make useless titles on
# their own -- the dialogue is named after its parent unit instead.
# Headings whose contents are reference material, not dialogue. A dialogue is
# dropped if ANY heading on its path matches, so subsections under Grammar go
# too. Overridable in the UI.

# The consolidation section at the end of a unit.

RE_UNIT_NO = re.compile(
    r"\b(?:unit|unidad|lesson|lecci[o\u00f3]n|tema|chapter|cap[i\u00ed]tulo"
    r"|module|m[o\u00f3]dulo)\s*[:.\-\u2013\u2014]?\s*(\d{1,3})\b",
    re.IGNORECASE,
)
RE_SKILL_NO = re.compile(
    r"\b(?:skill|habilidad|destreza|part|parte|objective|objetivo"
    r"|topic|t[o\u00f3]pico|assunto|abilit[a\u00e0]|comp[e\u00e9]tence)"
    r"\s*[:.\-\u2013\u2014]?\s*(\d{1,3})\b",
    re.IGNORECASE,
)

GENERIC_HEADINGS = _LazySet("CONSOLIDATION_HEADINGS", {
    "putting it all together", "put it all together", "all together",
    "putting it together", "dialogue", "dialogues", "dialogo", "dialogos",
    "conversation", "conversations", "conversacion", "conversaciones",
    "practice", "practica", "practise", "role play", "roleplay",
    "in context", "en contexto", "example dialogue", "sample dialogue",
    "listening", "audio", "escucha", "juntando todo", "todo junto",
    "consolidation", "recap", "wrap up", "wrap-up", "dialogue", "dialogues",
})


@dataclass
class Line:
    speaker: str
    text: str
    translation: str = ""
    note: str = ""
    raw: str = ""
    lineno: int = 0
    kind: str = "speech"      # "speech" | "scene"

    def key(self) -> str:
        h = hashlib.sha1(f"{self.speaker}\x00{self.text}".encode("utf-8"))
        return h.hexdigest()[:16]


@dataclass
class Dialogue:
    title: str
    index: int
    lines: list = field(default_factory=list)
    heading_path: list = field(default_factory=list)
    section: str = ""     # the leaf heading when the title came from an ancestor
    unit: Optional[int] = None
    skill: Optional[int] = None
    kind: str = "dialogue"      # "dialogue" | "consolidation"
    basename: str = ""          # filename stem, set by assign_basenames()

    @property
    def slug(self) -> str:
        s = re.sub(r"[^\w\s-]", "", self.title, flags=re.UNICODE).strip()
        s = re.sub(r"[\s_]+", "-", s).strip("-").lower()
        s = _deaccent(s)
        return s[:60] or f"dialogo-{self.index:02d}"

    @property
    def speakers(self) -> list:
        seen = []
        for ln in self.lines:
            if ln.kind != "speech":
                continue
            if ln.speaker not in seen:
                seen.append(ln.speaker)
        return seen

    @property
    def speech_lines(self) -> list:
        return [l for l in self.lines if l.kind == "speech"]

    @property
    def scenes(self) -> list:
        return [l.text for l in self.lines if l.kind == "scene"]

    @property
    def intro(self) -> str:
        """Scene line that opens the dialogue, if any."""
        return (self.lines[0].text
                if self.lines and self.lines[0].kind == "scene" else "")

    def to_dict(self) -> dict:
        d = asdict(self)
        d["slug"] = self.slug
        d["speakers"] = self.speakers
        d["n_lines"] = len(self.speech_lines)
        d["n_scenes"] = len(self.scenes)
        d["intro"] = self.intro
        d["has_intro"] = bool(self.intro)
        d["basename"] = self.basename
        d["n_chars"] = sum(len(l.text) for l in self.lines)
        for raw, ln in zip(d["lines"], self.lines):
            raw["key"] = ln.key()
            raw["display"] = speaker_display(ln.speaker) if ln.speaker else ""
            raw["note_label"] = getattr(PACK, "PARENTHETICAL_LABEL", "")
            fn = _speech_transform()
            if fn:
                out = fn(ln.text)
                raw["speech"] = out[0] if isinstance(out, tuple) else out
        return d


_ACCENTS = str.maketrans("áéíóúüñçÁÉÍÓÚÜÑÇ", "aeiouuncAEIOUUNC")


def _deaccent(s: str) -> str:
    return s.translate(_ACCENTS)


def _norm_heading(h: str) -> str:
    """Lowercase, de-accented, punctuation-stripped form for matching."""
    t = _deaccent(_strip_markdown(h or "")).lower()
    t = re.sub(r"[^\w\s]+", " ", t)
    return re.sub(r"\s+", " ", t).strip()


# Stripped repeatedly, because normalising "3.2 Grammar" flattens the dot and
# leaves "3 2 grammar". Roman numerals are deliberately NOT matched here: the
# letter set would swallow real words such as "Civil".
RE_LEADING_ORDINAL = re.compile(r"^(?:\d+|[a-z])[.)]?\s+", re.IGNORECASE)


def is_structural_heading(heading: str) -> bool:
    """A heading carrying a Unit / Skill / Topic number organises content; it is
    never itself a reference section, whatever words it also contains."""
    h = heading or ""
    return bool(RE_UNIT_NO.search(h) or RE_SKILL_NO.search(h))


def heading_matches(heading: str, keywords) -> bool:
    """True if the heading IS one of these reference sections.

    The keyword has to open the heading (after any "3.2 " style ordinal), not
    merely appear somewhere in it. Containment was too aggressive: a unit
    titled "Unit 10 - Geography, History, Culture: The Lusophone World" is not
    a Culture section, and "Skill 3 - Numbers and Spelling" is not a Spelling
    section. Structural headings are exempt outright as a second safety net.
    """
    if is_structural_heading(heading):
        return False
    norm = _norm_heading(heading)
    if not norm:
        return False
    core = norm
    while True:
        stripped_core = RE_LEADING_ORDINAL.sub("", core).strip()
        if stripped_core == core:
            break
        core = stripped_core
    for kw in keywords:
        k = _deaccent(str(kw)).lower().strip()
        if not k:
            continue
        if core == k or core.startswith(k + " "):
            return True
    return False


def numbers_from_path(path: list) -> tuple:
    """(unit, skill) read from the heading path; the deepest match wins."""
    unit = skill = None
    for h in path:
        mu = RE_UNIT_NO.search(h or "")
        if mu:
            unit = int(mu.group(1))
        ms = RE_SKILL_NO.search(h or "")
        if ms:
            skill = int(ms.group(1))
    return unit, skill


def _strip_markdown(s: str) -> str:
    s = RE_IMAGE.sub("", s)
    s = RE_LINK.sub(r"\1", s)
    s = RE_INLINE_MD.sub("", s)
    return s.strip()


def _looks_like_speaker(name: str) -> bool:
    n = name.strip()
    if not n or len(n) > 48:
        return False
    if _deaccent(n).strip(" .").lower() in NON_SPEAKER_LABELS:
        return False
    if n.lower() in NON_SPEAKER_LABELS:
        return False
    # Reject sentences masquerading as names
    if len(n.split()) > MAX_NAME_WORDS:
        return False
    if any(ch in n for ch in ",;!?\u00bf\u00a1\"\u201c\u201d/\\|<>{}="):
        return False
    if n.endswith((".",)) and len(n.split()) > 2:
        return False
    # must contain at least one letter
    if not re.search(r"[^\W\d_]", n, re.UNICODE):
        return False
    # reject URLs / times like "10" in "10:30"
    if n.isdigit():
        return False
    return True


def _split_stage_directions(text: str, keep: bool) -> tuple:
    """Pull parenthetical/bracketed stage directions out of the spoken text."""
    notes = []

    def _sub(m):
        inner = m.group(1).strip()
        # A short parenthetical that is plainly part of the sentence is kept.
        notes.append(inner)
        return " "

    if keep:
        return text, ""
    cleaned = RE_STAGE.sub(_sub, text)
    cleaned = re.sub(r"\s{2,}", " ", cleaned).strip()
    if not cleaned:  # the whole line was a stage direction
        return "", " / ".join(notes)
    return cleaned, " / ".join(notes)


def _dedupe_title(title: str, used: dict) -> str:
    base = title
    n = used.get(base, 0) + 1
    used[base] = n
    return base if n == 1 else f"{base} ({n})"


def parse_markdown(
    text: str,
    speak_stage_directions: bool = False,
    capture_translations: bool = True,
    skip_headings=None,
) -> list:
    """Parse Markdown text into a list of Dialogue objects.

    `skip_headings` is a list of keywords; any dialogue with a matching heading
    anywhere on its path is dropped. What was dropped is left on
    `parse_markdown.last_skipped` for reporting.
    """
    if skip_headings is None:
        skip_headings = default_skip_headings()
    text = text.replace("\r\n", "\n").replace("\r", "\n")

    # strip YAML front matter
    if text.startswith("---\n"):
        end = text.find("\n---", 4)
        if end != -1:
            text = text[end + 4 :]

    raw_lines = text.split("\n")

    # remove fenced code blocks
    lines, in_fence = [], False
    for i, ln in enumerate(raw_lines):
        if RE_FENCE.match(ln):
            in_fence = not in_fence
            lines.append(("", i + 1))
            continue
        lines.append(("" if in_fence else ln, i + 1))

    dialogues: list = []
    used_titles: dict = {}
    heading_stack: list = []      # (level, title, is_pseudo)
    cur_title = ""
    cur_path: list = []
    cur_lines: list = []

    def flush():
        nonlocal cur_lines
        # a section holding only scene lines and no speech is not a dialogue
        if any(l.kind == "speech" for l in cur_lines):
            # drop trailing scene lines that belong to nothing
            while cur_lines and cur_lines[-1].kind == "scene":
                cur_lines.pop()
            dialogues.append(
                Dialogue(
                    title=cur_title or (cur_path[-1] if cur_path else ""),
                    index=len(dialogues) + 1,
                    lines=cur_lines,
                    heading_path=list(cur_path),
                )
            )
        cur_lines = []

    i = 0
    while i < len(lines):
        raw, lineno = lines[i]
        stripped = raw.strip()

        # --- setext headings (Title\n=====)
        if stripped and i + 1 < len(lines):
            nxt = lines[i + 1][0].strip()
            if RE_SETEXT_H1.match(nxt) or (
                RE_SETEXT_H2.match(nxt) and not RE_HRULE.match(stripped)
            ):
                level = 1 if RE_SETEXT_H1.match(nxt) else 2
                flush()
                while heading_stack and heading_stack[-1][0] >= level:
                    heading_stack.pop()
                heading_stack.append((level, _strip_markdown(stripped), False))
                cur_path = [t for _, t, _ in heading_stack]
                cur_title = cur_path[-1]
                i += 2
                continue

        # --- ATX headings
        m = RE_HEADING.match(raw)
        if m:
            flush()
            level = len(m.group(1))
            title = _strip_markdown(m.group(2))
            while heading_stack and heading_stack[-1][0] >= level:
                heading_stack.pop()
            heading_stack.append((level, title, False))
            cur_path = [t for _, t, _ in heading_stack]
            cur_title = title
            i += 1
            continue

        # --- a stand-alone bold line behaves as a heading one level deeper
        # than the deepest real heading, so "**Vocabulary and useful
        # expressions**" ends the dialogue above it and is skippable by name.
        bm = RE_BOLD_LINE.match(stripped)
        if bm and ":" not in bm.group(1):
            flush()
            title = _strip_markdown(bm.group(1))
            base = max((lv for lv, _t, ps in heading_stack if not ps),
                       default=0)
            level = base + 1
            while heading_stack and heading_stack[-1][0] >= level:
                heading_stack.pop()
            heading_stack.append((level, title, True))
            cur_path = [t for _, t, _ in heading_stack]
            cur_title = title
            i += 1
            continue

        # --- horizontal rule: a dialogue break when there are no headings
        if RE_HRULE.match(stripped):
            flush()
            i += 1
            continue

        if not stripped or RE_TABLE_SEP.match(raw):
            i += 1
            continue

        body = RE_PREFIX.sub("", raw, count=1).strip()
        if not body:
            i += 1
            continue

        # --- markdown table row: | Ana | Hola | (English) |
        if body.startswith("|") and body.count("|") >= 2:
            # a header row is the one immediately followed by |---|---|
            if i + 1 < len(lines) and RE_TABLE_SEP.match(lines[i + 1][0]):
                i += 1
                continue
            cells = [c.strip() for c in body.strip("|").split("|")]
            cells = [_strip_markdown(c) for c in cells]
            if len(cells) >= 2 and _looks_like_speaker(cells[0].rstrip(":")):
                spk = cells[0].rstrip(":").strip()
                spoken, note = _split_stage_directions(cells[1], speak_stage_directions)
                trans = cells[2] if (capture_translations and len(cells) > 2) else ""
                if spoken:
                    cur_lines.append(
                        Line(spk, spoken, trans, note, raw=body, lineno=lineno)
                    )
                i += 1
                continue

        # --- scene-setting line: a whole-line italic or parenthesised
        # sentence, e.g. "*Nicolas rencontre sa nouvelle professeure.*" or
        # "*(Later, in the shop)*". Checked BEFORE the speaker regex so a scene
        # line containing a colon is not mistaken for a speaker name.
        #
        # These occur mid-dialogue as well as at the start: a single
        # "#### Dialogue" section often holds two scenes. A translation looks
        # the same but always follows its speech line with no blank line
        # between, so it is consumed by the continuation scan below and never
        # reaches here.
        sc = RE_ALL_ITALIC.match(body) or RE_ALL_PAREN.match(body)
        if sc:
            inner = _strip_markdown(sc.group(1)).strip()
            if inner and not RE_TRANS_TAG.match(inner):
                cur_lines.append(
                    Line("", inner, raw=body, lineno=lineno, kind="scene")
                )
                i += 1
                continue

        sm = RE_SPEAKER.match(body)
        if sm and _looks_like_speaker(sm.group("name")):
            speaker = _strip_markdown(sm.group("name")).strip().rstrip(":").strip()
            spoken_raw = _strip_markdown(sm.group("text"))
            spoken, note = _split_stage_directions(spoken_raw, speak_stage_directions)

            # continuation + translation lines that follow
            trans = ""
            j = i + 1
            while j < len(lines):
                nraw, _nl = lines[j]
                nbody = RE_PREFIX.sub("", nraw, count=1).strip()
                if not nbody:
                    break
                if RE_HEADING.match(nraw) or RE_HRULE.match(nbody):
                    break
                nsm = RE_SPEAKER.match(nbody)
                if nsm and _looks_like_speaker(nsm.group("name")):
                    break
                tm = RE_TRANS_TAG.match(nbody)
                if capture_translations and tm:
                    trans = _strip_markdown(tm.group(1))
                    j += 1
                    continue
                im = RE_ALL_ITALIC.match(nbody) or RE_ALL_PAREN.match(nbody)
                if capture_translations and im and not trans:
                    inner = _strip_markdown(im.group(1))
                    itm = RE_TRANS_TAG.match(inner)
                    trans = _strip_markdown(itm.group(1)) if itm else inner
                    j += 1
                    continue
                # plain wrapped continuation of the same utterance
                extra, extra_note = _split_stage_directions(
                    _strip_markdown(nbody), speak_stage_directions
                )
                if extra:
                    spoken = (spoken + " " + extra).strip()
                if extra_note:
                    note = (note + " / " + extra_note).strip(" /")
                j += 1

            if spoken:
                cur_lines.append(
                    Line(speaker, spoken, trans, note, raw=body, lineno=lineno)
                )
            i = j
            continue

        i += 1

    flush()

    kept, skipped = [], []
    for d in dialogues:
        hit = next((h for h in d.heading_path
                    if heading_matches(h, skip_headings)), None)
        if hit is not None:
            skipped.append({"title": d.title, "heading": hit,
                            "path": list(d.heading_path),
                            "n_lines": len(d.speech_lines)})
            continue
        kept.append(d)
    for n, d in enumerate(kept, 1):
        d.index = n
        d.unit, d.skill = numbers_from_path(d.heading_path)
        d.kind = ("consolidation"
                  if any(_norm_heading(h) in CONSOLIDATION_HEADINGS
                         for h in d.heading_path)
                  else "dialogue")

    _resolve_titles(kept)
    assign_basenames(kept)
    parse_markdown.last_skipped = skipped
    return kept


def assign_basenames(dialogues: list) -> list:
    """Name files u_01_ls_01 (unit 1, skill 1) and u_01_cs (unit consolidation).

    Falls back to a numbered slug whenever the unit number can't be read from
    the headings, so a file that doesn't follow the convention still renders.
    Collisions are resolved rather than silently overwritten.
    """
    used: dict = {}
    per_unit: dict = {}
    cs_per_unit: dict = {}

    for d in dialogues:
        if d.unit is None:
            d.basename = f"{d.index:02d}-{d.slug}"
        elif d.kind == "consolidation":
            # One consolidation per unit is the norm -> plain u_NN_cs. A unit
            # with several gets an ordinal so nothing is overwritten.
            cs_per_unit[d.unit] = cs_per_unit.get(d.unit, 0) + 1
            n = cs_per_unit[d.unit]
            d.basename = (f"u_{d.unit:02d}_cs" if n == 1
                          else f"u_{d.unit:02d}_cs_{n:02d}")
        else:
            n = d.skill
            if n is None:
                # no "Skill N" heading -- number dialogues within the unit
                per_unit[d.unit] = per_unit.get(d.unit, 0) + 1
                n = per_unit[d.unit]
            d.basename = f"u_{d.unit:02d}_ls_{n:02d}"

        base = d.basename
        if base in used:
            used[base] += 1
            suffix = chr(ord("a") + used[base] - 1)   # b, c, d... last resort
            d.basename = f"{base}{suffix}"
        used.setdefault(d.basename, 1)
    return dialogues


def _resolve_titles(dialogues: list) -> None:
    """Give every dialogue a distinct, useful title.

    A leaf heading that is generic ("Putting it all together") or that repeats
    in the file is replaced by the nearest meaningful ancestor heading, with the
    leaf kept in `section`. Anything still colliding gets a numeric suffix.
    """
    leaf_counts: dict = {}
    for d in dialogues:
        leaf = (d.heading_path or [d.title])[-1] if d.heading_path else d.title
        leaf_counts[leaf.strip().lower()] = leaf_counts.get(leaf.strip().lower(), 0) + 1

    for d in dialogues:
        path = list(d.heading_path)
        leaf = path[-1] if path else d.title
        low = leaf.strip().lower()
        generic = low in GENERIC_HEADINGS
        repeated = leaf_counts.get(low, 0) > 1

        if (generic or repeated) and len(path) > 1:
            ancestors = [
                a for a in path[:-1]
                if a.strip().lower() not in GENERIC_HEADINGS
            ]
            if ancestors:
                if generic:
                    d.title = ancestors[-1]
                    d.section = leaf
                else:
                    d.title = f"{ancestors[-1]} \u2014 {leaf}"
                    d.section = leaf
        if not d.title:
            d.title = f"Di\u00e1logo {d.index}"

    used: dict = {}
    for d in dialogues:
        d.title = _dedupe_title(d.title, used)


def speaker_key(name: str) -> str:
    """Stable lookup key for a speaker label.

    Uses a full Unicode de-accent rather than the language-specific table, so
    a pack can key its hints on plain ASCII ("wang ming") and have them match
    whatever diacritics the course file uses.
    """
    t = unicodedata.normalize("NFD", _strip_markdown(name or ""))
    t = "".join(c for c in t if unicodedata.category(c) != "Mn").lower()
    t = re.sub(r"[^\w\s]+", " ", t)
    return re.sub(r"\s+", " ", t).strip()


def speaker_hint(name: str) -> dict:
    return (getattr(PACK, "SPEAKER_HINTS", {}) or {}).get(speaker_key(name), {})


def speaker_display(name: str) -> str:
    """Friendly label for terse speaker codes; audio is unaffected because
    speaker names are never spoken."""
    return (getattr(PACK, "SPEAKER_LABELS", {}) or {}).get(
        speaker_key(name), name)


def self_gender(lines: list) -> tuple:
    """Gender a speaker reveals in their own speech.

    Portuguese "obrigada"/"obrigado", French "je suis anglaise", Italian "sono
    italiana" and so on agree with the person speaking, which beats guessing
    from a role noun or a word ending. Returns (gender, conflict) where
    conflict means the same label is used by both a man and a woman — usually
    a generic label like "Cliente" covering two different characters.
    """
    markers = getattr(PACK, "SELF_GENDER_MARKERS", {}) or {}
    if not markers:
        return None, False
    text = " ".join(l.text for l in lines).lower()
    text = " " + re.sub(r"[^\w\s\u00c0-\u017f]+", " ", text) + " "
    raw = " ".join(l.text for l in lines)
    found = set()
    for g, words in markers.items():
        for w in words:
            w = str(w)
            if w.startswith("re:"):
                if re.search(w[3:], raw):
                    found.add(g)
                    break
            elif f" {w.lower()} " in text:
                found.add(g)
                break
    if len(found) == 1:
        return found.pop(), False
    if len(found) > 1:
        return None, True
    return None, False


def collect_speakers(dialogues: list) -> list:
    """Unique speakers across all dialogues with a gender guess and counts."""
    order: list = []
    stats: dict = {}
    for d in dialogues:
        for ln in d.lines:
            if ln.kind != "speech":
                continue
            k = ln.speaker
            if k not in stats:
                hint = speaker_hint(k)
                if hint.get("gender"):
                    g, src = hint["gender"], "hint"
                else:
                    g, src = guess_gender_conf(k, PACK)
                stats[k] = {
                    "name": k,
                    "display": speaker_display(k),
                    "hint": hint.get("note", ""),
                    "gender": g,
                    "source": src,
                    "lines": 0,
                    "chars": 0,
                    "dialogues": set(),
                }
                order.append(k)
            stats[k]["lines"] += 1
            stats[k]["chars"] += len(ln.text)
            stats[k]["dialogues"].add(d.index)

    # a speaker's own words outrank a role noun or a word ending
    by_speaker: dict = {}
    for d in dialogues:
        for ln in d.lines:
            if ln.kind == "speech":
                by_speaker.setdefault(ln.speaker, []).append(ln)

    out = []
    for k in order:
        s = stats[k]
        s["dialogues"] = sorted(s["dialogues"])
        if s["source"] != "hint":
            g, conflict = self_gender(by_speaker.get(k, []))
            if conflict:
                s["conflict"] = True
                s["hint"] = (s.get("hint") or "") or (
                    "this label is used by both a man and a woman in the "
                    "file — probably two different characters")
            elif g and g != s["gender"]:
                s["gender"], s["source"] = g, "speech"
            elif g:
                s["source"] = "speech"
        out.append(s)
    return out


def assign_alternating(speakers: list) -> list:
    """Fill in '?' genders by alternating F/M, biased so the first unknown
    speaker takes whichever gender is not already dominant."""
    known = [
        s["gender"] for s in speakers
        if s["gender"] in ("F", "M")
        and s.get("source") in ("role", "name", "title", "article", "hint",
                                "speech")
    ]
    nxt = "F" if known.count("F") <= known.count("M") else "M"
    for s in speakers:
        if s["gender"] == "?":
            s["gender"] = nxt
            s["confident"] = False
            nxt = "M" if nxt == "F" else "F"
        else:
            s["confident"] = (s.get("source") in ("role", "name", "title",
                                              "article", "hint", "speech")
                          and not s.get("conflict"))
    return speakers
