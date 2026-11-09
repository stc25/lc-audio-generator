"""Orchestration: parsed dialogues + voice assignment -> audio files."""

from __future__ import annotations

import hashlib
import json
import re
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable, Optional

import numpy as np

from . import audio as A
from . import textprep
from .parser import Dialogue, speaker_display, speaker_hint
from .engines import Registry, make_ref, parse_ref
from .audio import resample

Progress = Optional[Callable[[dict], None]]


@dataclass
class VoiceChoice:
    voice_key: str      # a full engine-qualified reference, e.g. edge:it-IT-ElsaNeural
    speaker_id: Optional[int] = None
    rate: float = 1.0

    def cache_key(self, text: str) -> str:
        blob = f"{self.voice_key}|{self.speaker_id}|{self.rate:.4f}|{text}"
        return hashlib.sha1(blob.encode("utf-8")).hexdigest()


@dataclass
class GenOptions:
    accent: str = "es_ES"
    speak_intro: bool = True
    narrator_voice: str = ""
    narrator_rate: float = 0.95
    intro_pause_ms: int = 900
    spell_out: bool = True
    default_rate: float = 1.0
    pause_ms: int = 650
    lead_ms: int = 300
    tail_ms: int = 700
    fmt: str = "mp3"
    bitrate: str = "128k"
    trim: bool = True
    use_cache: bool = True
    write_srt: bool = False
    write_transcript: bool = True
    engine: str = "edge"          # default engine for auto-assigned voices
    scene_pause_ms: int = 1100      # gap at a scene change inside one dialogue
    naming: str = "structured"     # "structured" -> u_01_ls_01 | "template"
    filename_template: str = "{index:02d}-{slug}"
    album: str = "Dialogues"


def resolve_assignment(
    speakers: list,
    overrides: dict,
    accent: str,
    default_rate: float,
    registry: Registry,
    engine: str = "edge",
) -> dict:
    """speaker name -> VoiceChoice. `overrides` is
    {name: {voice, speaker_id, rate}} from the UI; anything missing falls back
    to the accent's default male/female pair for the chosen engine."""
    pair = registry.default_pair(engine, accent)
    out = {}
    for s in speakers:
        name = s["name"]
        ov = overrides.get(name) or overrides.get(name.lower()) or {}
        ref = ov.get("voice")
        sid = ov.get("speaker_id")
        rate = float(ov.get("rate") or default_rate)
        if not ref:
            # a language pack may suggest a voice for a known speaker code,
            # e.g. the CULP course's "B" (bot) and "L" (learner)
            ref = hinted_ref(name, s.get("gender", "M"), accent, registry) or ""
        if not ref:
            ref = pair.get(s.get("gender", "M"), pair["M"])
        eng, voice, embedded = parse_ref(ref)
        if sid is None:
            sid = embedded
        out[name] = VoiceChoice(make_ref(eng, voice), sid, rate)
    return out


def hinted_ref(name: str, gender: str, accent: str,
               registry: Registry) -> Optional[str]:
    """Voice a language pack suggests for a known speaker code.

    A hint pinned to one variety (the CULP files' Brazilian "B" and "L") must
    not out-rank an explicit variety choice. When the selected accent differs,
    the hint still decides the gender and which engine to prefer, and the voice
    itself comes from that accent's pair.
    """
    hint = speaker_hint(name)
    ref = hint.get("voice")
    if not ref:
        return None
    want = hint.get("accent")
    if not want or want == accent:
        return ref
    engine = parse_ref(ref)[0]
    pair = registry.default_pair(engine, accent)
    return pair.get(hint.get("gender") or gender) or pair.get("M")


def resolve_narrator(opts: "GenOptions", registry: Registry):
    """Voice that reads scene-setting lines. Falls back to any ready voice so a
    stale setting never stops a render."""
    ref = (opts.narrator_voice or "").strip()
    if not ref:
        ref = registry.default_pair(opts.engine, opts.accent)["M"]
    if not registry.is_ready(ref):
        ready = registry.ready_voices()
        if not ready:
            return None
        ref = ready[0]["ref"]
    eng, voice, spk = parse_ref(ref)
    return VoiceChoice(make_ref(eng, voice), spk, float(opts.narrator_rate or 1.0))


def _safe(name: str) -> str:
    name = re.sub(r'[<>:"/\\|?*\x00-\x1f]', "", name).strip(" .")
    return re.sub(r"\s+", " ", name)[:80] or "dialogo"


class Generator:
    def __init__(self, registry: Registry, out_dir: Path, cache_dir: Path):
        self.registry = registry
        self.out_dir = Path(out_dir)
        self.cache_dir = Path(cache_dir)
        self.out_dir.mkdir(parents=True, exist_ok=True)
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    # -------------------------------------------------------------- one line
    def line_audio(self, text: str, choice: VoiceChoice, use_cache: bool = True,
                   spell: bool = True):
        text = textprep.prepare(text, spell=spell)
        cache_file = self.cache_dir / f"{choice.cache_key(text)}.npz"
        if use_cache and cache_file.is_file():
            try:
                with np.load(cache_file) as z:
                    return z["a"].astype(np.float32), int(z["sr"])
            except Exception:
                cache_file.unlink(missing_ok=True)

        a, sr = self.registry.synth(
            text, choice.voice_key, speaker_id=choice.speaker_id, rate=choice.rate
        )
        if use_cache and a.size:
            try:
                np.savez_compressed(cache_file, a=a, sr=np.int32(sr))
            except Exception:
                pass
        return a, sr

    def preview(self, text: str, choice: VoiceChoice, spell: bool = True) -> tuple:
        a, sr = self.line_audio(text, choice, use_cache=False, spell=spell)
        a = A.normalize_peak(A.fade(a, sr))
        return a, sr

    # -------------------------------------------------------------- dialogue
    def build_dialogue(
        self,
        d: Dialogue,
        assignment: dict,
        opts: GenOptions,
        progress: Progress = None,
        source_name: str = "",
    ) -> dict:
        narrator = None
        if opts.speak_intro and d.scenes:
            narrator = resolve_narrator(opts, self.registry)

        refs = {assignment[s].voice_key for s in d.speakers if s in assignment}
        if narrator:
            refs.add(narrator.voice_key)
        work_rate = max([self.registry.sample_rate(r) for r in refs] or [22050])

        segments, cues = [], []
        t = opts.lead_ms / 1000.0
        segments.append(A.silence(t, work_rate))

        speech_total = len(d.speech_lines)
        n_done = 0
        pending_gap = 0.0     # applied before the next audible segment

        for i, ln in enumerate(d.lines):
            is_scene = ln.kind == "scene"

            if is_scene:
                # A scene change inside one dialogue -- a "#### Dialogue"
                # section often holds two of them. Even when the narrator is
                # off, the gap must still separate the two scenes or they run
                # together as one conversation.
                gap = opts.scene_pause_ms / 1000.0
                if narrator is None:
                    if cues:
                        pending_gap = max(pending_gap, gap)
                    continue
                choice = narrator
                label = "(narrator)"
            else:
                choice = assignment.get(ln.speaker)
                if choice is None:
                    continue
                label = ln.speaker

            if progress:
                n_done += 0 if is_scene else 1
                progress({"type": "line", "dialogue": d.index,
                          "line": n_done, "total_lines": speech_total,
                          "speaker": label, "text": ln.text[:80]})

            a, sr = self.line_audio(ln.text, choice, opts.use_cache,
                                    opts.spell_out)
            if a.size == 0:
                continue
            if opts.trim:
                a = A.trim_silence(a, sr)
            a = resample(a, sr, work_rate)

            if cues:
                gap = pending_gap or (
                    opts.scene_pause_ms / 1000.0 if is_scene
                    else opts.pause_ms / 1000.0
                )
                segments.append(A.silence(gap, work_rate))
                t += gap
            pending_gap = 0.0

            dur = a.size / float(work_rate)
            cues.append({"start": t, "end": t + dur,
                         "speaker": "" if is_scene else ln.speaker,
                         "display": "" if is_scene
                                    else speaker_display(ln.speaker),
                         "text": ln.text,
                         "translation": ln.translation,
                         "voice": choice.voice_key, "rate": choice.rate,
                         "scene": is_scene})
            segments.append(a)
            t += dur

            if is_scene:
                pending_gap = opts.intro_pause_ms / 1000.0

        segments.append(A.silence(opts.tail_ms / 1000.0, work_rate))
        t += opts.tail_ms / 1000.0

        mix = A.crossfade_free_concat(segments)
        if mix.size == 0:
            return {"dialogue": d.index, "title": d.title, "skipped": True,
                    "reason": "no audio produced"}
        mix = A.normalize_peak(A.fade(mix, work_rate, 12))

        if opts.naming == "structured" and d.basename:
            stem = _safe(d.basename)
        else:
            stem = _safe(opts.filename_template.format(
                index=d.index, slug=d.slug, title=d.title, n=d.index,
                unit=d.unit or 0, skill=d.skill or 0, kind=d.kind))
        wav = self.out_dir / f"{stem}.wav"
        A.write_wav(wav, mix, work_rate)

        final = wav
        if opts.fmt != "wav":
            final = A.encode(
                wav, self.out_dir / f"{stem}.{opts.fmt}", opts.fmt, opts.bitrate,
                tags={"title": (f"{d.title} \u2014 {d.section}"
                                if d.section else d.title),
                      "album": opts.album, "artist": "edge-tts",
                      "track": str(d.skill or d.index),
                      "disc": str(d.unit) if d.unit else None,
                      "genre": "Speech",
                      "comment": f"Source: {source_name}"},
            )
            wav.unlink(missing_ok=True)

        extras = []
        if opts.write_srt:
            extras.append(str(A.write_srt(self.out_dir / f"{stem}.srt", cues).name))
        if opts.write_transcript:
            tp = self.out_dir / f"{stem}.txt"
            body = [d.title, "=" * len(d.title), ""]
            if d.section:
                body += [d.section, ""]
            # built from the parsed lines, not the rendered cues, so scene
            # descriptions are kept even when the narrator is switched off
            for ln in d.lines:
                if ln.kind == "scene":
                    body += ["", f"[{ln.text}]", ""]
                    continue
                body.append(f"{speaker_display(ln.speaker)}: {ln.text}")
                if ln.translation:
                    body.append(f"    ({ln.translation})")
            tp.write_text("\n".join(body) + "\n", encoding="utf-8")
            extras.append(tp.name)

        return {
            "dialogue": d.index,
            "title": d.title,
            "section": d.section,
            "unit": d.unit,
            "skill": d.skill,
            "kind": d.kind,
            "intro": d.intro,
            "scenes": d.scenes,
            "narrated": bool(narrator),
            "file": final.name,
            "path": str(final),
            "duration": round(t, 2),
            "sample_rate": work_rate,
            "bytes": final.stat().st_size,
            "n_lines": len([c for c in cues if not c.get("scene")]),
            "n_cues": len(cues),
            "speakers": d.speakers,
            "extras": extras,
            "cues": cues,
            "skipped": False,
        }

    # ----------------------------------------------------------------- batch
    def run(
        self,
        dialogues: list,
        assignment: dict,
        opts: GenOptions,
        progress: Progress = None,
        source_name: str = "",
    ) -> dict:
        started = time.time()
        results, errors = [], []
        for n, d in enumerate(dialogues, 1):
            if progress:
                progress({"type": "dialogue", "index": d.index, "title": d.title,
                          "n": n, "total": len(dialogues)})
            try:
                results.append(
                    self.build_dialogue(d, assignment, opts, progress, source_name)
                )
            except Exception as e:
                errors.append({"dialogue": d.index, "title": d.title, "error": str(e)})
                if progress:
                    progress({"type": "error", "index": d.index, "message": str(e)})

        manifest = {
            "generated_at": time.strftime("%Y-%m-%d %H:%M:%S"),
            "source": source_name,
            "elapsed_s": round(time.time() - started, 1),
            "options": {k: getattr(opts, k) for k in vars(opts)},
            "assignment": {
                k: {"voice": v.voice_key, "speaker_id": v.speaker_id, "rate": v.rate}
                for k, v in assignment.items()
            },
            "results": [{k: v for k, v in r.items() if k != "cues"} for r in results],
            "errors": errors,
        }
        (self.out_dir / "manifest.json").write_text(
            json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8"
        )
        manifest["results_full"] = results
        return manifest
