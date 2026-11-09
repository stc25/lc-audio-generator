"""Render the recordings listed in an AUDIO_LIST.md, one file per row.

This is the file an AI agent (or you) hands to the app. The list is the
specification: each row names an ID, the voice(s) that must read it and the
path it must be saved at. The parser is table-driven rather than tied to one
course, so the Arabic, Spanish, German, Portuguese ... lists all load:

  ## Unit 3: Free time                      <- a section (unit); any ## heading
  Folder: `site/public/audio/lo-03-free/`   <- optional output sub-folder
  ### B. Texts (generate at 0.8x speed)     <- speed picked up from the heading
  | ID | Where | Voice | Save as | Voice note | Text |
  | U03-B-T1 | .. | **F+M** | `texts/U03-B-T1.mp3` | Ana = F, Luis = M | Ana: Hola. / Luis: Buenas. |

Recognised columns (case-insensitive): ID, Voice, Save as / File / Path, Voice
note / Note, and the text column (named after the language, or Text, Sentence,
Phrase, Passage ...). A "Voices" table (| Code | Voice | Use |) may map codes
such as ES-F1 to edge-tts names, and a row may name a regional voice either by
code or by edge-tts name in its voice note.

Voice cell: M, F, or several joined with + (F+M, M+F+F2). Several means a
dialogue: each speaker label ("Ana:") is cast to one of the listed voices.
"""

from __future__ import annotations

import hashlib
import json
import re
import tempfile
import threading
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable, Optional

import numpy as np

from .audio import encode, fade, normalize_peak, silence, trim_silence, write_wav
from .gender import guess_gender_conf

EDGE_LEAD = 0.5            # seconds of silence at each end
PARA_PAUSE = 0.9           # "¶"
TURN_PAUSE = 0.5           # "/" between speakers or lines
AUDIO_EXT = (".mp3", ".wav", ".m4a", ".ogg", ".opus", ".flac")

RE_SECTION = re.compile(r"^##\s+(.*?)\s*$")
RE_UNIT_NO = re.compile(r"(\d+)")
RE_FOLDER = re.compile(r"^\**Folder:?\**\s*`([^`]+)`", re.I)
RE_SPEED = re.compile(r"(\d(?:\.\d+)?)\s*[x×]\s*speed|speed\D{0,12}(\d(?:\.\d+)?)\s*[x×]", re.I)
RE_PATHCELL = re.compile(r"`([^`]+\.(?:mp3|wav|m4a|ogg|opus|flac))`", re.I)
RE_REUSE = re.compile(r"no new file[^|]*?(?:\*\*([^*|]+?)\*\*|\b([A-Za-z0-9]+(?:-[A-Za-z0-9]+)+)\b)", re.I)
RE_EDGE = re.compile(r"\b[a-z]{2,3}-[A-Z]{2}(?:-[A-Za-z]+)?-[A-Za-z]+Neural\b")
RE_VTOKEN = re.compile(r"^(?:[MF]\d?|[A-Z]{2,3}-[MF]\d)$")
RE_PARA = re.compile(r"\s*¶\s*")
RE_TURN = re.compile(r"\s+/\s+|\s*/\s*$|^\s*/\s*")
RE_LABEL = re.compile(r"^([^\W\d_][^:：.!?؟。！？¿¡,，0-9]{0,38}?)\s*[:：]\s*(\S.*)$", re.S)
RE_MD = re.compile(r"(\*\*|__|`|~~)")

TEXT_HEADERS = ("text", "say", "sentence", "phrase", "passage", "script", "dialogue",
                "word", "target", "line", "audio text")
META_HEADERS = {"id", "voice", "save as", "file", "path", "where", "exercise",
                "topic", "why", "note", "voice note", "english", "translation",
                "gloss", "notes", "unit", "tier", "section"}


@dataclass
class Item:
    id: str
    unit: int
    folder: str
    rel: str
    text: str = ""
    voice: str = "M"                  # raw cell, e.g. "F+M"
    tokens: list = field(default_factory=list)    # ["F", "M"]
    note: str = ""
    section: str = ""
    rate: Optional[float] = None
    reuse_of: Optional[str] = None
    forced: dict = field(default_factory=dict)    # token -> edge voice name

    @property
    def kind(self) -> str:
        return Path(self.rel).parent.name or "audio"

    @property
    def path(self) -> Path:
        return Path(self.folder) / self.rel


@dataclass
class Plan:
    items: list = field(default_factory=list)
    reused: list = field(default_factory=list)
    problems: list = field(default_factory=list)
    folders: dict = field(default_factory=dict)
    declared: dict = field(default_factory=dict)
    code_voices: dict = field(default_factory=dict)    # "ES-F1" -> "es-ES-ElviraNeural"
    default_voices: dict = field(default_factory=dict)  # "F" -> edge name, from the list's table
    skipped: list = field(default_factory=list)       # rows deliberately not made


# ------------------------------------------------------------------ parsing

def _all_voices():
    from . import voices as V
    return V.all_voices()


def _cells(line: str) -> list:
    return [c.strip() for c in line.strip().strip("|").split("|")]


def _plain(s: str) -> str:
    return RE_MD.sub("", s).strip()


def _tokens(cell: str) -> list:
    raw = re.sub(r"\(.*?\)", "", _plain(cell))
    return [t.strip().upper() for t in re.split(r"[+/&,]|\band\b", raw, flags=re.I)
            if t.strip()]


def _text_col(header: list, pack) -> Optional[int]:
    names = [h.lower() for h in header]
    want = [getattr(pack, "NAME", "").lower(), getattr(pack, "NATIVE", "").lower()]
    for key in want + list(TEXT_HEADERS):
        if key and key in names:
            return names.index(key)
    for n, h in enumerate(names):
        if h not in META_HEADERS and h:
            return n
    return None


def parse_list(md: str, pack=None, catalogue=None) -> Plan:
    """Turn an audio-list Markdown file into a Plan.

    `catalogue` is the set of known edge-tts voice names; it validates a
    "Voices" table and any voice named in a row's note."""
    plan = Plan()
    known = set(catalogue or [])
    if m := re.search(r"\*\*(\d+) files to produce\*\*", md):
        plan.declared["files"] = int(m[1])

    unit, folder, section, speed = 0, "", "", None
    header: Optional[list] = None
    seen: set = set()
    voices_table: list = []
    in_voices = False

    for line in md.splitlines():
        s = line.strip()
        if m := RE_SECTION.match(line) if line.startswith("## ") else None:
            section = m[1]
            n = RE_UNIT_NO.search(section)
            unit = int(n[1]) if n else 0
            folder, header, speed = "", None, None
            continue
        if line.startswith("#"):
            speed = None
            if sp := RE_SPEED.search(line):
                speed = float(sp[1] or sp[2])
            header = None
            continue
        if f := RE_FOLDER.match(s):
            folder = f[1]
            plan.folders[unit] = folder
            continue
        if not s.startswith("|"):
            if not s:
                header, in_voices = None, False
            continue
        cells = _cells(line)
        if re.fullmatch(r"[\s:|-]+", s):
            continue
        low = [c.lower() for c in cells]
        if low and low[0] == "code":              # the "Voices" table
            header, in_voices = None, True
            continue
        if low and low[0] in ("id", "unit"):
            header, in_voices = low, False
            continue
        if header is None:
            if in_voices:
                voices_table.append(cells)
            continue
        # a data row of an items table
        if "id" not in header:
            continue
        col = {h: i for i, h in enumerate(header)}
        path_i = next((col[k] for k in ("save as", "file", "path", "filename") if k in col), None)
        if path_i is None and not ("voice" in col and any(t in col for t in TEXT_HEADERS)):
            continue
        id_ = _plain(cells[0])
        if not id_ or id_.lower() == "id":
            continue
        if path_i is not None:
            pm = RE_PATHCELL.search(cells[path_i]) if path_i < len(cells) else None
        else:                                    # simple "id | voice | text" lists
            pm = re.match(r"(.+)", f"{id_}.mp3")
        reuse = RE_REUSE.search(line)
        text_i = _text_col(header, pack) if pack else None
        text = cells[text_i] if text_i is not None and text_i < len(cells) else ""
        text = _plain(text)
        vcell = cells[col["voice"]] if "voice" in col and col["voice"] < len(cells) else "M"
        note = ""
        for k in ("voice note", "note"):
            if k in col and col[k] < len(cells) and cells[col[k]]:
                note += " " + cells[col[k]]
        if id_ in seen:
            plan.problems.append(f"{id_}: duplicate ID")
            continue
        seen.add(id_)
        if reuse and not pm:
            plan.reused.append(Item(id_, unit, folder, "", text, reuse_of=(reuse[1] or reuse[2]).strip()))
            continue
        if not pm:
            if reuse:
                plan.reused.append(Item(id_, unit, folder, "", text, reuse_of=(reuse[1] or reuse[2]).strip()))
            else:
                plan.problems.append(f"{id_}: no file path in the 'Save as' cell")
            continue
        if not text:
            plan.problems.append(f"{id_}: no text to speak")
            continue
        if re.match(r"dialogue\s*:", text, re.I) and "=" in vcell:
            plan.skipped.append(f"{id_}: a dialogue title row; its lines are not in this list")
            continue
        explicit = RE_EDGE.findall(vcell)
        if explicit and "=" not in vcell:
            g = next((v["gender"] for v in _all_voices() if v["key"] == explicit[0]), "M")
            it = Item(id_, unit, folder, pm[1], text, g, [g], note.strip(), section, speed)
            it.forced[g] = explicit[0]
            plan.items.append(it)
            continue
        it = Item(id_, unit, folder, pm[1], text, _plain(vcell), _tokens(vcell),
                  note.strip(), section, speed)
        for t in it.tokens:
            if not RE_VTOKEN.match(t):
                plan.problems.append(f"{id_}: voice {t!r} is not M, F, M2, F2 or a code from the list")
        plan.items.append(it)

    # "Voices" table: | Code | Voice | Use |
    for cells in voices_table:
        if len(cells) < 2:
            continue
        code = _plain(cells[0]).upper()
        names = RE_EDGE.findall(cells[1])
        if code and names:
            plan.code_voices[code] = names[0]
            use = " ".join(cells[2:]).lower()
            if "default" in use:
                g = "F" if "female" in use else "M" if "male" in use else None
                if g:
                    plan.default_voices.setdefault(g, names[0])
            if re.search(r"second|2nd", use):
                g = "F" if "female" in use or "woman" in use else "M"
                plan.default_voices.setdefault(g + "2", names[0])

    for it in plan.items:
        _apply_forced(it, plan, known)
    ids = {i.id for i in plan.items}
    for r in plan.reused:
        if r.reuse_of not in ids:
            plan.problems.append(f"{r.id}: reuses unknown {r.reuse_of}")
    if "files" in plan.declared and plan.declared["files"] != len(plan.items):
        plan.problems.append(
            f"list says {plan.declared['files']} files, parsed {len(plan.items)}")
    return plan


def _apply_forced(it: Item, plan: Plan, known: set) -> None:
    """A voice named in a row (by code or edge-tts name, in the voice cell or
    note) replaces the default for the first listed voice of its gender."""
    genders = {v["key"]: v["gender"] for v in _all_voices()}
    named = []
    for name in RE_EDGE.findall(it.note + " " + it.voice):
        if known and name not in known:
            plan.problems.append(f"{it.id}: voice {name} is not in the voice catalogue")
            continue
        named.append(name)
    for code, name in plan.code_voices.items():
        if re.search(rf"\b{re.escape(code)}\b", it.note, re.I):
            named.append(name)
    for name in named:
        g = genders.get(name, "?")
        tok = next((t for t in it.tokens if t[0] == g and t not in it.forced), None)
        if tok:
            it.forced[tok] = name


def filter_plan(plan: Plan, units=None, kinds=None, ids=None, pattern=None) -> Plan:
    rx = re.compile(pattern) if pattern else None

    def keep(i):
        return ((not units or i.unit in units)
                and (not kinds or i.kind in kinds)
                and (not ids or i.id in ids)
                and (not rx or rx.search(i.id)))

    out = Plan(problems=plan.problems, folders=plan.folders, declared=plan.declared,
               code_voices=plan.code_voices, default_voices=plan.default_voices,
               skipped=plan.skipped)
    out.items = [i for i in plan.items if keep(i)]
    out.reused = [i for i in plan.reused if keep(i)]
    return out


# ------------------------------------------------------------------ casting

def clean(text: str) -> str:
    """Spoken form of a cell: fill-in placeholders become a short pause."""
    text = text.replace("…", ",").replace("...", ",")
    text = re.sub(r"_{2,}", ",", text)
    return re.sub(r"\s+", " ", text).strip()


def segments(text: str) -> list:
    """Split a passage into [speaker_label|None, text, pause_after]."""
    out = []
    for para in RE_PARA.split(text):
        pieces = [p for p in RE_TURN.split(para) if p and p.strip()]
        for n, piece in enumerate(pieces):
            label = None
            if m := RE_LABEL.match(piece.strip()):
                if len(m[1].split()) <= 4:
                    label, piece = m[1].strip(), m[2]
            last = n == len(pieces) - 1
            out.append([label, clean(piece), PARA_PAUSE if last else TURN_PAUSE])
    return [tuple(s) for s in out if s[1]]


def _norm_label(lab: str) -> str:
    return re.sub(r"\W+", " ", lab).strip().lower()


def label_gender(label: str, pack, hint: str = "") -> str:
    """'F', 'M' or '?': from the row's voice note first (e.g. 'Ana = F', 'Sra.
    Martínez (female)'), then the language pack's name/role knowledge."""
    key = re.escape(label)
    if m := re.search(rf"{key}\W{{0,6}}(?:=|is|\()\s*(female|male|f\b|m\b|woman|man)", hint, re.I):
        return "F" if m[1].lower() in ("female", "f", "woman") else "M"
    if hint:
        for g, words in (("F", "female|woman|f"), ("M", "male|man|m")):
            if re.search(rf"{key}\s*\(\s*(?:{words})\s*\)", hint, re.I):
                return g
    try:
        g, _src = guess_gender_conf(label, pack)
    except Exception:                                   # noqa: BLE001
        return "?"
    return g if g in ("F", "M") else "?"


def cast(item: Item, pack) -> list:
    """Row -> [[text, voice_token, pause_after], ...]."""
    toks = item.tokens or ["M"]
    if len(toks) == 1:
        # one voice: read exactly as written (labels, if any, included)
        segs = segments(item.text)
        if not segs:
            return [[clean(item.text), toks[0], 0.0]]
        return [[clean(f"{l}: {t}" if l else t), toks[0], p] for l, t, p in segs]

    segs = segments(item.text)
    labels = list(dict.fromkeys(s[0] for s in segs if s[0]))
    if len(labels) >= 2:
        # cast each speaker to one of the listed voices: by gender where the
        # name/note says so, else in order of appearance
        genders = {l: label_gender(l, pack, item.note) for l in labels}
        free = list(toks)
        assign: dict = {}
        for l in labels:
            g = genders[l]
            if g in ("F", "M"):
                m = next((t for t in free if t[0] == g), None)
                if m:
                    assign[l] = m
                    free.remove(m)
        for l in labels:
            if l not in assign:
                assign[l] = free.pop(0) if free else toks[labels.index(l) % len(toks)]
        return [[t, assign.get(l) or assign[labels[0]], p] for l, t, p in segs]

    # several voices but no speaker labels: alternate on line breaks
    out, n = [], 0
    for _l, t, p in segs:
        out.append([t, toks[n % len(toks)], p])
        n += 1
    return out


# ------------------------------------------------------------------ render

class Renderer:
    def __init__(self, registry, locale: str, plan: Optional[Plan] = None,
                 rate: Optional[float] = None, alt_locale: Optional[str] = None,
                 pack=None, bitrate: str = "96k", explicit_locale: bool = False):
        self.reg, self.pack = registry, pack or registry.pack
        self.rate_override = rate
        self.bitrate = bitrate
        self.locale = locale
        pair = registry.default_pair("edge", locale)
        self.pair = {k: v.replace("edge:", "") for k, v in pair.items()}
        if plan and not explicit_locale:     # an explicit --locale beats the list's defaults
            for g, name in plan.default_voices.items():
                self.pair[g] = name
        if alt_locale:
            alt = registry.default_pair("edge", alt_locale)
            for k in ("M", "F"):
                self.pair.setdefault(k + "2", alt.get(k, "").replace("edge:", ""))
        for g in ("M", "F"):                       # second voice falls back
            self.pair.setdefault(g + "2", self.pair.get(g, ""))
        self.code_voices = dict(plan.code_voices) if plan else {}

    def voice_for(self, item: Item, token: str) -> str:
        if token in item.forced:
            return item.forced[token]
        if token in self.code_voices:
            return self.code_voices[token]
        return self.pair.get(token) or self.pair.get(token[0]) \
            or next(iter(self.pair.values()))

    def _gender(self, name: str) -> str:
        from . import voices as V
        return next((v["gender"] for v in V.all_voices() if v["key"] == name), "?")

    def rate_for(self, item: Item) -> float:
        if self.rate_override:
            return self.rate_override
        return item.rate or 1.0

    def refs(self, items) -> dict:
        used = {}
        for it in items:
            for t in (it.tokens or ["M"]):
                used[t] = self.code_voices.get(t) or self.pair.get(t) \
                    or self.pair.get(t[0], "")
        return used

    def render(self, item: Item) -> tuple:
        parts, sr = [], None
        rate = self.rate_for(item)
        for text, tag, pause in cast(item, self.pack):
            if not text.strip():
                continue
            audio, sr = self.reg.synth(text, "edge:" + self.voice_for(item, tag), rate=rate)
            audio = fade(trim_silence(audio, sr), sr)
            parts += [audio, silence(pause, sr)]
        if sr is None:
            raise RuntimeError("nothing to say")
        body = np.concatenate([p for p in parts if p.size])
        lead = silence(EDGE_LEAD, sr)
        return normalize_peak(np.concatenate([lead, body, lead])), sr

    def stamp(self, item: Item) -> str:
        v = "|".join(self.voice_for(item, t) for t in (item.tokens or ["M"]))
        h = hashlib.sha1(item.text.encode("utf-8")).hexdigest()[:12]
        return f"{item.voice}|{v}|{self.rate_for(item)}|{h}"


def write_item(path: Path, audio: np.ndarray, sr: int, fmt: str = "mp3",
               bitrate: str = "96k") -> int:
    """Write mono audio to path (mp3 at 44.1 kHz). Returns bytes."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as td:
        wav = write_wav(Path(td) / "x.wav", audio, sr)
        if fmt == "mp3":
            _mp3_441(wav, path, bitrate)
        else:
            encode(wav, path, fmt, bitrate)
    return path.stat().st_size


def _mp3_441(wav: Path, out: Path, bitrate: str) -> None:
    import subprocess
    proc = subprocess.run(
        ["ffmpeg", "-y", "-loglevel", "error", "-i", str(wav), "-ac", "1",
         "-ar", "44100", "-c:a", "libmp3lame", "-b:a", bitrate, str(out)],
        capture_output=True, text=True)
    if proc.returncode != 0:
        raise RuntimeError(f"ffmpeg failed: {proc.stderr.strip()[:300]}")


def dest_for(out_root: Path, item: Item, fmt: str, strip: str = "") -> Path:
    folder = item.folder
    if strip and folder.startswith(strip):
        folder = folder[len(strip):].lstrip("/")
    return (out_root / folder / item.rel).with_suffix("." + fmt)


def run(plan: Plan, renderer: Renderer, out_root: Path, fmt: str = "mp3",
        force: bool = False, jobs: int = 4, strip: str = "",
        progress: Callable[[dict], None] = lambda e: None,
        should_stop: Callable[[], bool] = lambda: False) -> dict:
    """Render every item once, at its own path under out_root. On resume a
    file is kept only if the manifest says it was made with this row's voice,
    rate and text, so editing the list re-renders exactly what changed."""
    out_root.mkdir(parents=True, exist_ok=True)
    man_path = out_root / ".manifest.json"
    try:
        manifest = json.loads(man_path.read_text(encoding="utf-8"))
    except Exception:                                   # noqa: BLE001
        manifest = {}
    report = {"written": 0, "skipped": 0, "errors": [], "files": []}
    lock = threading.Lock()
    total = len(plan.items)
    counter = {"n": 0}

    def one(it: Item):
        if should_stop():
            return
        dest = dest_for(out_root, it, fmt, strip)
        st = renderer.stamp(it)
        status = "ok"
        if (not force and dest.is_file() and dest.stat().st_size
                and manifest.get(it.id) == st):
            status = "skipped"
        else:
            try:
                audio, sr = renderer.render(it)
                write_item(dest, audio, sr, fmt, renderer.bitrate)
                with lock:
                    manifest[it.id] = st
            except Exception as e:                      # noqa: BLE001 - keep going
                status = "error"
                with lock:
                    report["errors"].append({"id": it.id, "error": str(e)})
        with lock:
            counter["n"] += 1
            if status == "ok":
                report["written"] += 1
                report["files"].append(str(dest))
            elif status == "skipped":
                report["skipped"] += 1
            if counter["n"] % 10 == 0:
                man_path.write_text(json.dumps(manifest), encoding="utf-8")
            n = counter["n"]
        progress({"n": n, "total": total, "id": it.id, "status": status})

    with ThreadPoolExecutor(max_workers=max(1, jobs)) as ex:
        list(ex.map(one, plan.items))
    man_path.write_text(json.dumps(manifest), encoding="utf-8")
    return report


def verify(plan: Plan, out_root: Path, fmt: str = "mp3", strip: str = "",
           full: Optional[Plan] = None) -> dict:
    """Compare files on disk with the list. `full` is the unfiltered plan: a
    file only counts as extra if no list row names it."""
    expected = {dest_for(out_root, i, fmt, strip) for i in plan.items}
    known = {dest_for(out_root, i, fmt, strip) for i in (full or plan).items}
    on_disk = set(out_root.rglob(f"*.{fmt}")) if out_root.is_dir() else set()
    voice_dirs = [d.name for d in out_root.rglob("*")
                  if d.is_dir() and d.name.lower() in ("male", "female")]
    return {"expected": len(expected), "present": len(expected & on_disk),
            "missing": sorted(p.stem for p in expected - on_disk),
            "extra": sorted(p.stem for p in on_disk - known),
            "voice_dirs": voice_dirs}
