import json
from pathlib import Path

import pytest

from audiogen import service as S
from audiogen import voices as V
from audiogen.languages import AVAILABLE, load

EX = Path(__file__).resolve().parent.parent / "examples"
OUT_FMT = "wav"          # keep tests independent of ffmpeg's mp3 encoder


def test_all_requested_languages_load():
    want = {"Arabic", "British Sign Language", "Chinese", "French", "German", "Greek",
            "Hebrew", "Italian", "Japanese", "Korean", "Latin", "Persian",
            "Portuguese", "Russian", "Spanish", "Swahili", "Turkish"}
    got = {load(c).NAME.split(" (")[0] for c in AVAILABLE}
    assert want == got


@pytest.mark.parametrize("code", AVAILABLE)
def test_every_language_has_a_usable_voice_pair(code):
    pack = load(code)
    for loc, _label, _n in V.locales_for(pack):
        pair = V.default_pair(pack, loc)
        assert pair.get("M") and pair.get("F"), (code, loc)
    assert pack.DEFAULT_ACCENT in pack.ACCENTS


def test_voice_counts_and_variants():
    assert len(V.voices_for(load("es"), False)) >= 40
    assert {"ar_EG", "ar_SA", "ar_MA"} <= {l for l, _, _ in V.locales_for(load("ar"))}
    assert {"zh_HK", "zh_TW", "zh_CN"} <= {l for l, _, _ in V.locales_for(load("zh"))}
    assert {"pt_BR", "pt_PT"} <= {l for l, _, _ in V.locales_for(load("pt"))}
    assert V.default_pair(load("la"), "it_IT")["M"].startswith("it-IT")


def test_locale_spelling_is_forgiving():
    p = load("es")
    assert V.default_pair(p, "es-mx") == V.default_pair(p, "es_MX")


def test_audio_list_parse():
    plan = S.parse_audio_list("es", (EX / "sample-audio-list.es.md").read_text())
    assert plan.problems == []
    assert len(plan.items) == 8 and len(plan.reused) == 1
    assert plan.reused[0].reuse_of == "U01-A-V01"
    by = {i.id: i for i in plan.items}
    assert by["U01-A-V01"].rate is None                 # vocabulary: normal speed
    assert by["U01-B-T1"].rate == 0.8                   # heading says 0.8x
    assert by["U01-B-T1"].tokens == ["F", "M"]
    assert by["U01-A-V01"].path.as_posix() == "lo-01-primer-contacto/vocab/U01-A-V01.mp3"
    assert plan.code_voices["LA-F1"] == "es-MX-DaliaNeural"


def test_dialogue_row_is_cast_by_gender_not_order(fake_edge):
    plan = S.parse_audio_list("es", (EX / "sample-audio-list.es.md").read_text())
    r = S.build_renderer("es", plan)
    row = next(i for i in plan.items if i.id == "U01-B-T1")
    voices = [(t[:12], r.voice_for(row, tok))
              for t, tok, _ in __import__("audiogen.audiolist", fromlist=["x"]).cast(row, load("es"))]
    assert voices[0][1] == "es-ES-ElviraNeural"         # Sra. Martínez = F
    assert voices[1][1] == "es-ES-AlvaroNeural"         # Sr. González = M


def test_generate_list_resumes_and_honours_row_voice(tmp_path, fake_edge):
    plan = S.parse_audio_list("es", (EX / "sample-audio-list.es.md").read_text())
    rep = S.generate_list("es", plan, tmp_path, fmt=OUT_FMT, jobs=2)
    assert rep["written"] == 8 and not rep["errors"]
    assert (tmp_path / "lo-01-primer-contacto/vocab/U01-A-V01.wav").is_file()
    # U01-C-S02 names LA-F1 in its note: Mexican voice, and speed 0.8
    call = next(c for c in fake_edge if c["text"].startswith("¿Cómo te llamas"))
    assert call["voice"] == "es-MX-DaliaNeural" and call["rate"] == 0.8
    n = len(fake_edge)
    rep2 = S.generate_list("es", plan, tmp_path, fmt=OUT_FMT, jobs=2)
    assert rep2["written"] == 0 and rep2["skipped"] == 8 and len(fake_edge) == n
    chk = S.AL.verify(plan, tmp_path, OUT_FMT)
    assert chk["missing"] == [] and chk["voice_dirs"] == []


def test_locale_changes_the_default_voices(tmp_path, fake_edge):
    plan = S.parse_audio_list("pt", "| ID | Voice | Save as | Text |\n|---|---|---|---|\n"
                              "| X1 | F | `vocab/X1.mp3` | Olá |\n")
    S.generate_list("pt", plan, tmp_path, locale="pt-PT", fmt=OUT_FMT)
    assert fake_edge[0]["voice"].startswith("pt-PT-")


def test_simple_id_voice_text_list():
    md = ("| id | voice | text |\n|---|---|---|\n"
          "| v-hi | edge:pt-BR-FranciscaNeural | Oi. Olá. |\n"
          "| d1 | Emily = edge:pt-BR-FranciscaNeural, Lucas = edge:pt-BR-AntonioNeural | dialogue: Meeting |\n")
    assert S.detect_kind(md) == "audio-list"
    plan = S.parse_audio_list("pt", md)
    assert [i.id for i in plan.items] == ["v-hi"] and len(plan.skipped) == 1


def test_bad_voice_is_reported():
    plan = S.parse_audio_list("es", "| ID | Voice | Save as | Text |\n|---|---|---|---|\n"
                              "| A | Q | `a.mp3` | hola |\n")
    assert any("voice" in p for p in plan.problems)


def test_dialogues_generate_and_use_locale(tmp_path, fake_edge):
    text = (EX / "sample-dialogues.es.md").read_text()
    m = S.generate_dialogues("es", text, tmp_path, patch={"fmt": OUT_FMT, "accent": "es_MX"},
                             save_settings=False)
    assert len(m["results"]) == 2 and not m["errors"]
    assert {v.split(":")[1] for v in m["speaker_voices"].values()} <= {
        "es-MX-DaliaNeural", "es-MX-JorgeNeural"}


def test_language_switching_is_isolated():
    from audiogen.lang import PACK, use
    with use("ar"):
        assert PACK.CODE == "ar"
        with use("tr"):
            assert PACK.CODE == "tr"
        assert PACK.CODE == "ar"


def test_speak_latin_strips_macrons(tmp_path, fake_edge):
    S.speak("la", "Salvē, amīce!", tmp_path / "x.wav")
    assert fake_edge[0]["text"].startswith("Salve, amice")
    assert fake_edge[0]["voice"].startswith("it-IT")


def test_cli_inspect_json(capsys):
    from audiogen.cli import main
    assert main(["inspect", str(EX / "sample-audio-list.es.md"), "--lang", "es", "--json"]) == 0
    d = json.loads(capsys.readouterr().out)
    assert d["kind"] == "audio-list" and d["files_to_make"] == 8


def test_cli_rejects_unknown_language(capsys):
    from audiogen.cli import main
    with pytest.raises(SystemExit) as e:
        main(["inspect", str(EX / "sample-audio-list.es.md"), "--lang", "klingon"])
    assert e.value.code == 2


def test_explicit_locale_beats_list_defaults():
    plan = S.parse_audio_list("es", (EX / "sample-audio-list.es.md").read_text())
    assert S.build_renderer("es", plan).refs(plan.items)["F"] == "es-ES-ElviraNeural"
    assert S.build_renderer("es", plan, "es-AR").refs(plan.items)["F"].startswith("es-AR-")
