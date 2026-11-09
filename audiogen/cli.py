"""Command line for audiogen: made to be driven by people *and* AI agents.

  audiogen languages                       list languages (+ --json)
  audiogen voices es [--locale es-MX]      list edge-tts voices for a language
  audiogen inspect LIST.md --lang es       what is in this file? (no audio made)
  audiogen generate LIST.md --lang es -o out/   render everything it asks for
  audiogen speak "Hola" --lang es -o hola.mp3   one phrase
  audiogen verify LIST.md --lang es -o out/     which expected files are missing
  audiogen serve                           start the web UI

Every command takes --json for machine-readable output on stdout (progress and
warnings go to stderr). Exit codes: 0 ok, 1 finished with errors/missing files,
2 bad input or an unusable voice.
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

from . import service as S
from . import voices as V
from .languages import AVAILABLE, load


def _err(*a):
    print(*a, file=sys.stderr)


def _lang(a):
    if not a.lang:
        _err("error: --lang is required (try `audiogen languages`)")
        raise SystemExit(2)
    try:
        return load(a.lang).CODE
    except ValueError as e:
        _err(f"error: {e}")
        raise SystemExit(2)


def _units(spec: str) -> set:
    out = set()
    for part in filter(None, (p.strip() for p in (spec or "").split(","))):
        lo, _, hi = part.partition("-")
        out |= set(range(int(lo), int(hi or lo) + 1))
    return out


def _csv(spec: str) -> set:
    return {p.strip() for p in (spec or "").split(",") if p.strip()}


def _emit(a, data, text=""):
    if getattr(a, "json", False):
        print(json.dumps(data, ensure_ascii=False, indent=2, default=str))
    elif text:
        print(text)


# ------------------------------------------------------------------ commands

def cmd_languages(a) -> int:
    rows = S.languages()
    if a.json:
        _emit(a, rows)
        return 0
    print(f"  {'code':5} {'language':34} {'voices':>6}  locales")
    for r in rows:
        locs = ", ".join(l["locale"].replace("_", "-") for l in r["locales"][:6])
        more = f" +{len(r['locales']) - 6}" if len(r["locales"]) > 6 else ""
        print(f"  {r['code']:5} {r['name']:34} {r['n_voices']:>6}  {locs}{more}")
        if r["note"]:
            print(f"        {r['note']}")
    return 0


def cmd_voices(a) -> int:
    if a.refresh:
        try:
            n = V.refresh_snapshot()
        except Exception as e:                           # noqa: BLE001
            _err(f"could not reach the edge-tts service: {e}")
            return 2
        _err(f"voice catalogue refreshed: {n} voices")
    a.lang = a.lang or a.lang_pos
    code = _lang(a)
    cat = S.voice_table(code)
    if a.locale:
        want = a.locale.replace("-", "_").lower()
        cat = [v for v in cat if v["locale"].lower() == want]
    if a.json:
        _emit(a, cat)
        return 0
    cur = None
    for v in cat:
        if v["locale"] != cur:
            cur = v["locale"]
            print(f"\n  {cur.replace('_', '-')}  {v['accent']}")
        tags = ", ".join(v["personalities"])
        extra = "  (multilingual)" if v.get("borrowed") else ""
        print(f"    {v['gender']}  {v['key']:40} {tags}{extra}")
    return 0


def cmd_inspect(a) -> int:
    code = _lang(a)
    text, name = S.read_source(a.file)
    kind = a.kind if a.kind != "auto" else S.detect_kind(text)
    info = {"file": a.file, "language": code, "kind": kind}
    if kind == "audio-list":
        plan = S.parse_audio_list(code, text)
        r = S.build_renderer(code, plan, a.locale)
        by: dict = {}
        for it in plan.items:
            k = by.setdefault(it.kind, {"files": 0, "voices": {}})
            k["files"] += 1
            k["voices"][it.voice] = k["voices"].get(it.voice, 0) + 1
        info.update({
            "files_to_make": len(plan.items), "reuse_rows": len(plan.reused),
            "units": sorted({i.unit for i in plan.items}), "by_kind": by,
            "voices": r.refs(plan.items),
            "problems": plan.problems, "skipped_rows": plan.skipped,
            "sample": [{"id": i.id, "voice": i.voice, "save_as": str(i.path),
                        "rate": i.rate, "text": i.text[:60]} for i in plan.items[:5]],
        })
        human = (f"  {a.file}: audio list for {load(code).NAME}\n"
                 f"  {len(plan.items)} files to make, {len(plan.reused)} reuse an earlier file, "
                 f"units {info['units']}\n  by folder: "
                 + ", ".join(f"{k} {v['files']}" for k, v in by.items())
                 + "\n  voices: " + ", ".join(f"{k}={v}" for k, v in info["voices"].items())
                 + ("\n  PROBLEMS:\n   - " + "\n   - ".join(plan.problems) if plan.problems else ""))
    else:
        d = S.parse_dialogues(code, text)
        info.update({
            "dialogues": len(d["dialogues"]),
            "lines": sum(len(x.speech_lines) for x in d["dialogues"]),
            "ignored_sections": sorted({x["heading"] for x in d["skipped"]}),
            "speakers": [{"name": s["name"], "gender": s["gender"], "voice": s["voice"]}
                         for s in d["speakers"]],
            "files": [{"file": f"{x.basename}.mp3", "title": x.title} for x in d["dialogues"]],
        })
        human = (f"  {a.file}: dialogues for {load(code).NAME}\n"
                 f"  {info['dialogues']} dialogues, {info['lines']} lines, "
                 f"{len(info['speakers'])} speakers\n"
                 + "\n".join(f"    {s['name']:24} {s['gender']}  -> {s['voice']}"
                             for s in info["speakers"]))
    _emit(a, info, human)
    return 1 if info.get("problems") else 0


def _progress(a):
    state = {"last": 0.0}

    def prog(ev):
        if a.json or a.quiet:
            return
        now = time.time()
        if ev.get("status") == "error" or now - state["last"] > 0.15:
            state["last"] = now
            if "total" in ev and "id" in ev:
                print(f"\r  [{ev['n']}/{ev['total']}] {ev['id']:14} {ev['status']:8}",
                      end="", file=sys.stderr, flush=True)
            elif ev.get("type") == "dialogue":
                print(f"\n  [{ev['n']}/{ev['total']}] {ev['title']}", file=sys.stderr)
    return prog


def cmd_generate(a) -> int:
    code = _lang(a)
    text, name = S.read_source(a.file)
    kind = a.kind if a.kind != "auto" else S.detect_kind(text)
    out = Path(a.out) if a.out else S.DEFAULT_OUT / code / (
        "list" if kind == "audio-list" else "dialogues")
    if kind == "audio-list":
        plan = S.parse_audio_list(code, text)
        for p in plan.problems:
            _err(f"  ! {p}")
        if plan.problems and not a.ignore_problems:
            _err("  The list has problems (above). Fix them, or pass --ignore-problems.")
            return 2
        full = plan
        plan = S.AL.filter_plan(plan, _units(a.unit), _csv(a.folder),
                                _csv(a.id), a.match)
        r = S.build_renderer(code, plan, a.locale, a.rate)
        _err(f"  {len(plan.items)} recordings ({len(plan.reused)} reuse earlier files); "
             f"voices: " + ", ".join(f"{k}={v}" for k, v in r.refs(plan.items).items()))
        if a.dry_run:
            _emit(a, {"dry_run": True, "files": [str(S.AL.dest_for(out, i, a.format, a.strip))
                                                 for i in plan.items]})
            return 0
        try:
            rep = S.generate_list(code, plan, out, locale=a.locale, rate=a.rate,
                                  fmt=a.format, force=a.force, jobs=a.jobs,
                                  strip=a.strip, progress=_progress(a))
        except ValueError as e:
            _err(f"\n  {e}")
            return 2
        chk = S.AL.verify(plan, out, a.format, a.strip, full=full)
        res = {"kind": kind, "out": str(out), "written": rep["written"],
               "skipped": rep["skipped"], "errors": rep["errors"],
               "expected": chk["expected"], "present": chk["present"],
               "missing": chk["missing"], "extra": chk["extra"]}
        _err("")
        _emit(a, res, f"  {rep['written']} written, {rep['skipped']} already there, "
                      f"{chk['present']}/{chk['expected']} present, {len(chk['missing'])} missing\n"
                      f"  -> {out}")
        for e in rep["errors"][:10]:
            _err(f"    ! {e['id']}: {e['error']}")
        return 1 if (chk["missing"] or rep["errors"]) else 0

    # dialogues
    patch = {"fmt": a.format, "default_rate": a.rate or 1.0}
    if a.locale:
        patch["accent"] = a.locale.replace("-", "_")
    voices = {}
    for spec in a.voice or []:
        who, _, v = spec.partition("=")
        voices[who.strip()] = {"voice": v.strip()}
    if a.dry_run:
        return cmd_inspect(a)
    try:
        m = S.generate_dialogues(code, text, out, source_name=name, patch=patch,
                                 voices=voices, only=sorted(_units(a.only)) or None,
                                 progress=_progress(a), save_settings=False)
    except (ValueError, FileNotFoundError) as e:
        _err(f"\n  {e}")
        return 2
    res = {"kind": kind, "out": str(out), "results": m["results"], "errors": m["errors"],
           "speaker_voices": m["speaker_voices"], "elapsed_s": m["elapsed_s"]}
    _err("")
    _emit(a, res, "\n".join(f"  {r['file']:44} {r['duration']:6.1f}s" for r in m["results"])
          + f"\n\n  -> {out}  ({m['elapsed_s']}s)")
    for e in m["errors"]:
        _err(f"  ! dialogue {e['dialogue']}: {e['error']}")
    return 1 if m["errors"] else 0


def cmd_speak(a) -> int:
    code = _lang(a)
    text = a.text if a.text != "-" else sys.stdin.read()
    try:
        res = S.speak(code, text, Path(a.out), voice=a.voice or "", gender=a.gender,
                      locale=a.locale or "", rate=a.rate or 1.0)
    except (ValueError, RuntimeError) as e:
        _err(f"error: {e}")
        return 2
    _emit(a, res, f"  {res['file']}  ({res['seconds']}s, {res['voice']})")
    return 0


def cmd_verify(a) -> int:
    code = _lang(a)
    text, _ = S.read_source(a.file)
    plan = S.parse_audio_list(code, text)
    full = plan
    plan = S.AL.filter_plan(plan, _units(a.unit), _csv(a.folder), _csv(a.id), a.match)
    chk = S.AL.verify(plan, Path(a.out), a.format, a.strip, full=full)
    _emit(a, chk, f"  {chk['present']}/{chk['expected']} present, "
                  f"{len(chk['missing'])} missing, {len(chk['extra'])} extra")
    if chk["missing"] and not a.json:
        print("  missing: " + ", ".join(chk["missing"][:40])
              + (" ..." if len(chk["missing"]) > 40 else ""))
    return 1 if chk["missing"] else 0


def cmd_serve(a) -> int:
    from run import main as run_main        # noqa: PLC0415
    sys.argv = ["run.py"] + (["--no-browser"] if a.no_browser else []) + \
        (["--port", str(a.port)] if a.port else []) + (["--host", a.host] if a.host else [])
    run_main()
    return 0


# ------------------------------------------------------------------ parser

def build_parser() -> argparse.ArgumentParser:
    ap = argparse.ArgumentParser(prog="audiogen", description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)

    def common(p, lang=True):
        if lang:
            p.add_argument("--lang", "-l", help="language code, e.g. es, ar, zh "
                           "(see `audiogen languages`)")
        p.add_argument("--json", action="store_true", help="machine-readable output")
        p.add_argument("--quiet", "-q", action="store_true")

    def listopts(p):
        p.add_argument("--unit", default="", help="units to include, e.g. 1-3 or 2,5")
        p.add_argument("--folder", default="", help="only these kinds: vocab,texts,sentences,phrases")
        p.add_argument("--id", default="", help="only these IDs (comma separated)")
        p.add_argument("--match", default="", help="regex on the ID, e.g. '^U03-B'")
        p.add_argument("--strip", default="", metavar="PREFIX",
                       help="drop this prefix from each unit folder, e.g. site/public/audio")
        p.add_argument("--format", default="mp3",
                       choices=["mp3", "m4a", "opus", "flac", "wav"])

    p = sub.add_parser("languages", help="list languages and how many voices each has")
    common(p, lang=False)
    p.set_defaults(fn=cmd_languages)

    p = sub.add_parser("voices", help="list edge-tts voices for a language")
    common(p)
    p.add_argument("lang_pos", nargs="?", metavar="LANG", help="same as --lang")
    p.add_argument("--locale", help="only this variety, e.g. es-MX, ar-EG, zh-HK")
    p.add_argument("--refresh", action="store_true", help="update the catalogue from Microsoft first")
    p.set_defaults(fn=cmd_voices)

    p = sub.add_parser("inspect", help="parse a Markdown file and say what it would make")
    common(p)
    p.add_argument("file")
    p.add_argument("--kind", default="auto", choices=["auto", "audio-list", "dialogues"])
    p.add_argument("--locale")
    p.set_defaults(fn=cmd_inspect)

    p = sub.add_parser("generate", help="make the audio a Markdown file asks for")
    common(p)
    p.add_argument("file")
    p.add_argument("--out", "-o", help="output folder (default: output/<lang>/...)")
    p.add_argument("--kind", default="auto", choices=["auto", "audio-list", "dialogues"],
                   help="auto: tables with ID + Save as = audio-list, else dialogues")
    p.add_argument("--locale", help="variety/accent, e.g. es-MX, pt-BR, zh-TW")
    p.add_argument("--rate", type=float, help="speed multiplier; overrides the list's own speeds")
    p.add_argument("--jobs", type=int, default=4, help="parallel requests (list mode)")
    p.add_argument("--force", action="store_true", help="re-render files that already exist")
    p.add_argument("--dry-run", action="store_true")
    p.add_argument("--ignore-problems", action="store_true")
    p.add_argument("--only", default="", help="dialogue mode: dialogue numbers, e.g. 1-3")
    p.add_argument("--voice", action="append", metavar="SPEAKER=VOICE",
                   help="dialogue mode: e.g. --voice 'Ana=es-MX-DaliaNeural'")
    listopts(p)
    p.set_defaults(fn=cmd_generate)

    p = sub.add_parser("speak", help="say one phrase and save it")
    common(p)
    p.add_argument("text", help="text to say, or - to read stdin")
    p.add_argument("--out", "-o", required=True)
    p.add_argument("--voice", help="edge-tts voice name, e.g. es-MX-DaliaNeural")
    p.add_argument("--gender", default="F", choices=["F", "M"])
    p.add_argument("--locale")
    p.add_argument("--rate", type=float)
    p.set_defaults(fn=cmd_speak)

    p = sub.add_parser("verify", help="check which files from an audio list exist")
    common(p)
    p.add_argument("file")
    p.add_argument("--out", "-o", required=True)
    listopts(p)
    p.set_defaults(fn=cmd_verify)

    p = sub.add_parser("serve", help="start the web UI")
    p.add_argument("--port", type=int, default=0)
    p.add_argument("--host", default="")
    p.add_argument("--no-browser", action="store_true")
    p.set_defaults(fn=cmd_serve)
    return ap


def main(argv=None) -> int:
    a = build_parser().parse_args(argv)
    try:
        return a.fn(a)
    except (FileNotFoundError, ValueError) as e:
        _err(f"error: {e}")
        return 2
    except KeyboardInterrupt:
        _err("\ninterrupted")
        return 130


if __name__ == "__main__":
    raise SystemExit(main())
