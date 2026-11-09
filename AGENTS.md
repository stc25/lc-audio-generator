# Instructions for AI agents (Codex, Claude Code, others)

This project, **audiogen**, generates spoken audio (edge-tts) for 17 languages
from Markdown. When the user gives you a Markdown file that lists audio to
produce ("generate the audio in this list"), use the CLI below. Do not write
your own TTS code, and do not edit the user's list.

Run everything from this project's root (`cd` here first; the scripts find
their own `.venv`; the first run builds it). Use `./audiogen.sh` in WSL / Linux /
macOS and `.\audiogen.bat` in Windows PowerShell. Needs `ffmpeg` and, to generate
audio, internet.

## Procedure

1. **Language.** Map the user's language to a code (`./audiogen.sh languages`):
   ar bsl zh fr de el he it ja ko la fa pt ru es sw tr. If they name a
   variety (Mexican Spanish, Egyptian Arabic, Brazilian, Cantonese, Swiss
   German…) pass it as `--locale` (`es-MX`, `ar-EG`, `pt-BR`, `zh-HK`, `de-CH`).
   List choices with `./audiogen.sh voices <lang>`. Ask the user only if the
   language or variety is genuinely ambiguous.
   - `la` (Latin) is read with Italian voices; `bsl` voices only the English
     text of BSL material (signing cannot be audio). Tell the user this.
2. **Path.** Windows paths from WSL: `wslpath -u 'C:\\x\\y.md'`;
   `\\\\wsl.localhost\\<distro>\\home\\...` is `/home/...`.
3. **Inspect first** (no audio, no network):
   `./audiogen.sh inspect FILE --lang xx [--locale yy] --json`
   Check `kind` (`audio-list` or `dialogues`), the file counts, the `voices`, and
   `problems` (must be empty; `skipped_rows` and `reuse_rows` are expected and
   are not generated). If there are problems, report them to the user instead of guessing.
4. **Generate:**
   `./audiogen.sh generate FILE --lang xx [--locale yy] -o OUTDIR --json`
   - Choose `OUTDIR` as the user says; otherwise ask or use `output/<lang>/`.
   - Long lists (hundreds of files) are fine: it runs 4 requests in parallel
     (`--jobs 8` for more), and it is resumable. If it is interrupted or some
     files fail (exit 1), run the same command again; finished files are skipped.
   - Filters: `--unit 1-3`, `--folder vocab,texts`, `--id A,B`, `--match REGEX`,
     `--force` (re-render), `--rate X` (override speeds), `--strip PREFIX`,
     `--format mp3|wav|m4a|opus|flac`.
   - Dialogue files: `--voice 'Name=es-MX-DaliaNeural'` per speaker, `--only 1-3`.
5. **Verify** an audio list: `./audiogen.sh verify FILE --lang xx -o OUTDIR --json`
   (exit 0 means every expected file exists). Report written / skipped /
   missing / errors to the user, and where the files are.
6. One phrase: `./audiogen.sh speak "text" --lang xx [--gender M|F] [--voice NAME] -o file.mp3`.

Exit codes: 0 ok; 1 some files failed/missing (re-run); 2 bad input or
unusable voice (fix the cause; do not retry blindly). `--json` result goes to
stdout, progress and warnings to stderr.

## Audio-list rules (what the app follows; see README for the full format)

Tables with **ID**, **Voice** (`M`, `F`, or `F+M` for a dialogue; `F2`/`M2` for second voices),
**Save as** (backticked path) and a text column. Output path = `<OUTDIR>/<unit Folder>/<Save as>`.
A section heading with `0.8x speed` sets the speed of its tables. Rows "no new file: uses X" are
not generated. No `male/` `female/` folders. A regional voice may be named in a row's note by code
(`LA-F1`, from the list's Voices table) or edge-tts name.

## Developing

`./.venv/bin/python -m pytest` (network is mocked). Language packs live in
`audiogen/languages/<code>.py`; the voice list is `audiogen/data/edge_voices.json`
(`./audiogen.sh voices --refresh`). Web UI: `./run.sh`; HTTP API docs at `/api/docs`.
