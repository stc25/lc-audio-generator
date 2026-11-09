"""Web UI + HTTP API (FastAPI).

The same API serves the browser UI and AI agents: every endpoint takes a
`lang` code, accepts either a file `path` on this machine or the Markdown
`text` itself, and returns JSON. Interactive docs: /api/docs
"""
from __future__ import annotations

import hashlib
import io
import threading
import traceback
import uuid
import wave
from pathlib import Path

import numpy as np
from fastapi import Body, FastAPI, File, HTTPException, UploadFile
from fastapi.responses import FileResponse, HTMLResponse, Response
from fastapi.staticfiles import StaticFiles

from . import audiolist as AL
from . import service as S
from . import voices as V
from .engines import registry_for
from .lang import spawn, use
from .languages import AVAILABLE, load
from .settings import settings_for

STATIC = Path(__file__).resolve().parent / "static"
DATA, ROOT = S.DATA, S.ROOT

app = FastAPI(title="audiogen: multilingual audio generator", docs_url="/api/docs")

# ---------------------------------------------------------------- jobs

JOBS: dict = {}
LOCK = threading.Lock()


def new_job(kind: str) -> str:
    jid = uuid.uuid4().hex[:12]
    with LOCK:
        JOBS[jid] = {"id": jid, "kind": kind, "state": "running", "pct": 0,
                     "message": "starting", "log": [], "result": None,
                     "error": None, "stop": False}
    return jid


def job_update(jid: str, **kw):
    with LOCK:
        j = JOBS.get(jid)
        if not j:
            return
        log = kw.pop("log", None)
        j.update(kw)
        if log:
            j["log"] = (j["log"] + [log])[-400:]


def run_bg(jid: str, fn):
    def wrap():
        try:
            res = fn()
            job_update(jid, state="done", pct=100, message="finished", result=res)
        except Exception as e:                           # noqa: BLE001
            job_update(jid, state="error", error=str(e), message=f"failed: {e}",
                       log=traceback.format_exc()[-1500:])
    spawn(wrap)


# ---------------------------------------------------------------- helpers

def _lang(code: str) -> str:
    try:
        return load(code).CODE
    except ValueError as e:
        raise HTTPException(400, str(e))


def _source(body: dict) -> tuple:
    try:
        return S.read_source(body.get("path") or "", body.get("text") or "")
    except FileNotFoundError as e:
        raise HTTPException(404, str(e))
    except ValueError as e:
        raise HTTPException(400, str(e))


def _out(body: dict, code: str, kind: str) -> Path:
    if body.get("out_dir"):
        return Path(body["out_dir"]).expanduser()
    return S.DEFAULT_OUT / code / kind


def _wav_bytes(a: np.ndarray, sr: int) -> bytes:
    buf = io.BytesIO()
    pcm = (np.clip(a, -1, 1) * 32767).astype("<i2")
    with wave.open(buf, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(int(sr))
        w.writeframes(pcm.tobytes())
    return buf.getvalue()


# ---------------------------------------------------------------- static

def _asset_version() -> str:
    h = hashlib.sha1()
    for n in ("app.js", "style.css", "index.html"):
        f = STATIC / n
        if f.is_file():
            h.update(f.read_bytes())
    return h.hexdigest()[:10]


@app.get("/", response_class=HTMLResponse)
def index():
    html = (STATIC / "index.html").read_text(encoding="utf-8")
    v = _asset_version()
    html = html.replace("/static/app.js", f"/static/app.js?v={v}")
    html = html.replace("/static/style.css", f"/static/style.css?v={v}")
    return HTMLResponse(html, headers={"Cache-Control": "no-store"})


class _NoCache(StaticFiles):
    def file_response(self, *a, **k):
        r = super().file_response(*a, **k)
        r.headers["Cache-Control"] = "no-cache, must-revalidate"
        return r


app.mount("/static", _NoCache(directory=str(STATIC)), name="static")


# ---------------------------------------------------------------- info

@app.get("/api/health")
def api_health():
    return {**S.health(), "languages": len(AVAILABLE), "output_root": str(S.DEFAULT_OUT)}


@app.get("/api/languages")
def api_languages():
    return {"languages": S.languages()}


@app.get("/api/voices")
def api_voices(lang: str, locale: str = ""):
    code = _lang(lang)
    cat = S.voice_table(code)
    if locale:
        cat = [v for v in cat if v["locale"].lower() == locale.replace("-", "_").lower()]
    pack = load(code)
    return {"language": S.language_info(code), "voices": cat,
            "pairs": {l["locale"]: registry_for(code).default_pair("edge", l["locale"])
                      for l in S.language_info(code)["locales"]},
            "ready": registry_for(code).available(),
            "problem": registry_for(code).unavailable_reason(),
            "default_locale": pack.DEFAULT_ACCENT}


@app.post("/api/voices/refresh")
def api_voices_refresh():
    try:
        n = V.refresh_snapshot()
    except Exception as e:                               # noqa: BLE001
        raise HTTPException(502, f"Could not reach the edge-tts service: {e}")
    return {"ok": True, "voices": n}


@app.get("/api/settings")
def api_settings(lang: str):
    return dict(settings_for(DATA, _lang(lang)))


@app.post("/api/settings")
def api_settings_post(lang: str, patch: dict = Body(...)):
    code = _lang(lang)
    s = settings_for(DATA, code)
    with use(code):
        s.apply(patch)
    return dict(s)


# ---------------------------------------------------------------- inspect

@app.post("/api/inspect")
def api_inspect(body: dict = Body(...)):
    """What does this file ask for? Auto-detects audio list vs dialogues."""
    code = _lang(body.get("lang", ""))
    text, name = _source(body)
    kind = body.get("kind") or S.detect_kind(text)
    if kind == "audio-list":
        plan = S.parse_audio_list(code, text)
        r = S.build_renderer(code, plan, body.get("locale", ""))
        return {"kind": kind, "source": name, "language": code,
                "files_to_make": len(plan.items), "reuse_rows": len(plan.reused),
                "units": sorted({i.unit for i in plan.items}),
                "problems": plan.problems, "voices": r.refs(plan.items),
                "items": [{"id": i.id, "unit": i.unit, "kind": i.kind, "voice": i.voice,
                           "save_as": str(i.path), "rate": i.rate, "text": i.text,
                           "note": i.note} for i in plan.items],
                "reused": [{"id": i.id, "reuse_of": i.reuse_of} for i in plan.reused]}
    d = S.parse_dialogues(code, text)
    return {"kind": kind, "source": name, "language": code, "accent": d["accent"],
            "variety": d["variety"], "skipped": d["skipped"], "speakers": d["speakers"],
            "pair": d["pair"],
            "dialogues": [x.to_dict() for x in d["dialogues"]]}


@app.post("/api/upload")
async def api_upload(file: UploadFile = File(...)):
    dest = DATA / "input" / Path(file.filename or "upload.md").name
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_bytes(await file.read())
    return {"ok": True, "path": str(dest), "name": dest.name}


# ---------------------------------------------------------------- generate

@app.post("/api/generate")
def api_generate(body: dict = Body(...)):
    """Start a render job. Body: lang, path|text, kind (auto|audio-list|dialogues),
    out_dir, locale, rate, plus filters (units/folders/ids/match, only) and, for
    dialogues, voices {speaker: {voice, rate}}. Poll /api/jobs/{job}."""
    code = _lang(body.get("lang", ""))
    text, name = _source(body)
    kind = body.get("kind") or S.detect_kind(text)
    out = _out(body, code, "list" if kind == "audio-list" else "dialogues")
    jid = new_job("generate")

    def stop():
        return JOBS.get(jid, {}).get("stop", False)

    if kind == "audio-list":
        plan = S.parse_audio_list(code, text)
        if plan.problems and not body.get("ignore_problems"):
            raise HTTPException(422, {"message": "The audio list has problems.",
                                      "problems": plan.problems})
        plan = AL.filter_plan(plan, set(body.get("units") or []),
                              set(body.get("folders") or []), set(body.get("ids") or []),
                              body.get("match") or None)
        if not plan.items:
            raise HTTPException(400, "Nothing matches those filters.")

        def prog(ev):
            job_update(jid, pct=int(ev["n"] * 100 / max(1, ev["total"])),
                       message=f"{ev['id']} {ev['status']}",
                       log=f"{ev['id']}: {ev['status']}" if ev["status"] == "error" else None)

        def work():
            rep = S.generate_list(code, plan, out, locale=body.get("locale", ""),
                                  rate=body.get("rate"), fmt=body.get("format", "mp3"),
                                  force=bool(body.get("force")), jobs=int(body.get("jobs") or 4),
                                  strip=body.get("strip", ""), progress=prog, should_stop=stop)
            chk = AL.verify(plan, out, body.get("format", "mp3"), body.get("strip", ""))
            return {"kind": kind, "out": str(out), **{k: rep[k] for k in ("written", "skipped", "errors")},
                    "expected": chk["expected"], "present": chk["present"], "missing": chk["missing"]}

        run_bg(jid, work)
        return {"job": jid, "kind": kind, "files": len(plan.items), "out": str(out)}

    n_lines = {"n": 0}

    def prog2(ev):
        if ev.get("type") == "line":
            n_lines["n"] += 1
            job_update(jid, message=f"[{ev['dialogue']}] {ev['speaker']}: {ev['text']}",
                       pct=min(99, ev.get("line", 0) * 100 // max(1, ev.get("total_lines", 1))))
        elif ev.get("type") == "dialogue":
            job_update(jid, log=f"Dialogue {ev['index']}: {ev['title']}")
        elif ev.get("type") == "error":
            job_update(jid, log=f"ERROR in dialogue {ev['index']}: {ev['message']}")

    patch = dict(body.get("options") or {})
    if body.get("locale"):
        patch["accent"] = body["locale"].replace("-", "_")
    if body.get("rate"):
        patch["default_rate"] = float(body["rate"])

    def work2():
        res = S.generate_dialogues(code, text, out, source_name=name, patch=patch,
                                   voices=body.get("voices") or {}, only=body.get("only"),
                                   progress=prog2)
        res["out"] = str(out)
        return res

    # fail fast on bad input before starting the thread
    try:
        with use(code):
            from .parser import parse_markdown
            if not parse_markdown(text):
                raise HTTPException(400, "No dialogues found. Dialogue lines need a 'Name:' prefix.")
    except HTTPException:
        raise
    run_bg(jid, work2)
    return {"job": jid, "kind": kind, "out": str(out)}


@app.get("/api/jobs/{jid}")
def api_job(jid: str):
    with LOCK:
        j = JOBS.get(jid)
    if not j:
        raise HTTPException(404, "Unknown job")
    return j


@app.post("/api/jobs/{jid}/stop")
def api_job_stop(jid: str):
    job_update(jid, stop=True, message="stopping after the current files")
    return {"ok": True}


# ---------------------------------------------------------------- speak / preview

@app.post("/api/preview")
def api_preview(body: dict = Body(...)):
    """Short WAV for the browser. Body: lang, voice (edge name), text, rate."""
    code = _lang(body.get("lang", ""))
    voice = body.get("voice") or ""
    if not voice:
        raise HTTPException(400, "Pick a voice first.")
    reg = registry_for(code)
    if not reg.is_ready("edge:" + voice):
        raise HTTPException(409, reg.why_not_ready("edge:" + voice))
    text = (body.get("text") or load(code).SAMPLE_TEXT)[:600]
    try:
        with use(code):
            from .textprep import prepare
            a, sr = reg.synth(prepare(text, spell=False), "edge:" + voice,
                              rate=float(body.get("rate") or 1.0))
    except Exception as e:                               # noqa: BLE001
        raise HTTPException(502, str(e))
    return Response(_wav_bytes(a, sr), media_type="audio/wav")


@app.post("/api/speak")
def api_speak(body: dict = Body(...)):
    """Say one phrase and save it. Body: lang, text, out (file path), voice|gender, locale, rate."""
    code = _lang(body.get("lang", ""))
    out = body.get("out") or str(S.DEFAULT_OUT / code / "speak" / "phrase.mp3")
    try:
        return S.speak(code, body.get("text", ""), Path(out).expanduser(),
                       voice=body.get("voice", ""), gender=body.get("gender", "F"),
                       locale=body.get("locale", ""), rate=float(body.get("rate") or 1.0))
    except (ValueError, RuntimeError) as e:
        raise HTTPException(400, str(e))


# ---------------------------------------------------------------- output

@app.get("/api/output")
def api_output(lang: str = "", kind: str = "", dir: str = ""):
    root = Path(dir).expanduser() if dir else S.DEFAULT_OUT / (lang or "") / kind
    files = []
    if root.is_dir():
        for p in sorted(root.rglob("*")):
            if p.is_file() and p.suffix in (".mp3", ".wav", ".m4a", ".opus", ".flac", ".txt", ".srt"):
                files.append({"name": str(p.relative_to(root)), "bytes": p.stat().st_size,
                              "mtime": p.stat().st_mtime})
    return {"dir": str(root), "files": files[:2000], "truncated": len(files) > 2000}


@app.get("/api/file")
def api_file(path: str):
    """Serve a generated file for in-browser playback/download (output tree only)."""
    p = Path(path).expanduser().resolve()
    allowed = [S.DEFAULT_OUT.resolve()]
    for k, v in list(JOBS.items()):
        r = (v.get("result") or {}).get("out")
        if r:
            allowed.append(Path(r).resolve())
    if not p.is_file() or not any(str(p).startswith(str(a)) for a in allowed):
        raise HTTPException(404, "Not found")
    return FileResponse(str(p), filename=p.name)
