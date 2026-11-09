# audiogen: multilingual dialogue and audio-list generator

One app for all of the language-course audio projects. It turns Markdown into
spoken audio with [edge-tts](https://github.com/rany2/edge-tts), in **17
languages and 100+ regional varieties**, from either

- a **web UI** (`./run.sh`), or
- a **command line and HTTP API** that an AI agent (Claude Code, Codex) can drive:
  you hand the agent a Markdown file that lists the audio you need, and it
  reads the file, runs the app and checks the result.

It replaces the separate `arabic-`, `chinese-`, `german-`, `portuguese-`,
`spanish-…-audio-generator` / `-dialogue-audio` apps. Each language is a "pack"
in `audiogen/languages/`, and you choose it with `--lang` or the UI dropdown.

> **Needs internet while generating.** edge-tts calls Microsoft's online voices
> (free, no account, no API key). Nothing else is uploaded. Parsing, listing
> voices and `--dry-run` work offline.

---

## 1. Install

You need **Python 3.10+** and **ffmpeg**. The first run creates a `.venv` and
installs the Python packages by itself.

**Linux / WSL (Ubuntu)**
```bash
sudo apt update && sudo apt install -y python3-venv ffmpeg
cd ~/projects/audio-generator
./run.sh                      # web UI at http://localhost:8765
```

**macOS (Terminal)**
```bash
brew install python ffmpeg
cd ~/projects/audio-generator
./run.sh
```

**Windows (PowerShell), without WSL**
```powershell
winget install Python.Python.3.12 Gyan.FFmpeg      # then open a new PowerShell
cd C:\path\to\audio-generator
.\run.bat
```

Check everything works (no network needed):
```bash
./audiogen.sh languages               # Windows: .\audiogen.bat languages
./audiogen.sh inspect examples/sample-audio-list.es.md --lang es
```
Run the tests with `.venv/bin/pip install -r requirements-dev.txt && .venv/bin/python -m pytest`.

---

## 2. Languages and voices

| Language | Code | Voices | Varieties (edge-tts locales) |
|---|---|---:|---|
| Arabic | `ar` | 32 | ar-SA, ar-AE, ar-BH, ar-DZ, ar-EG, ar-IQ, ar-JO, ar-KW, ar-LB, ar-LY, ar-MA, ar-OM, ar-QA, ar-SY, ar-TN, ar-YE |
| British Sign Language | `bsl` | 47 | en-GB (default), en-IE, en-US, en-AU, … see below |
| Chinese | `zh` | 14 | zh-CN, zh-TW, zh-HK (Cantonese), zh-CN-liaoning, zh-CN-shaanxi |
| French | `fr` | 13 | fr-FR, fr-CA, fr-BE, fr-CH |
| German | `de` | 10 | de-DE, de-AT, de-CH |
| Greek | `el` | 2 | el-GR |
| Hebrew | `he` | 2 | he-IL |
| Italian | `it` | 4 | it-IT |
| Japanese | `ja` | 2 | ja-JP |
| Korean | `ko` | 3 | ko-KR |
| Latin | `la` | 4 | it-IT voices, see below |
| Persian | `fa` | 2 | fa-IR |
| Portuguese | `pt` | 5 | pt-BR, pt-PT |
| Russian | `ru` | 2 | ru-RU |
| Spanish | `es` | 45 | es-ES, es-MX, es-AR, es-CO, es-CL, es-PE, es-VE, es-US, … 22 countries |
| Swahili | `sw` | 4 | sw-KE, sw-TZ |
| Turkish | `tr` | 2 | tr-TR |

The counts are what Microsoft offers today; `audiogen voices --refresh` pulls
the live list, so new voices appear without a code change. A "variety" is an
edge-tts locale: choose it with `--locale es-MX` (CLI) or the Variety dropdown
(UI). Every language also lists Microsoft's *Multilingual* voices, which can
read any language, at the end of its voice list.

**Two languages are special, and the app says so:**

- **Latin** has no edge-tts voices. It is read with **Italian voices**
  (closest to Ecclesiastical pronunciation); macrons and breves are stripped
  before speaking. This is an approximation, not Classical pronunciation.
- **British Sign Language** is signed, so it cannot be turned into audio. The
  `bsl` pack voices the *English* text of BSL course material (instructions,
  glosses, translations) with British English voices. It never voices signing.

Other limits: Greek, Hebrew, Swahili and Turkish packs were written fresh (a
native speaker should skim the name and role lists, which only drive the
male/female voice guess). Japanese, Korean and Chinese name lists are short.

```bash
./audiogen.sh voices es --locale es-MX     # every Mexican Spanish voice
./audiogen.sh voices zh                    # every Chinese voice, all varieties
./audiogen.sh speak "你好，你好吗？" --lang zh --locale zh-HK -o hello.mp3
```

---

## 3. Using the web UI

```bash
./run.sh            # opens http://localhost:8765  (use --no-browser on a server)
```
Pick the **language** and **variety** at the top, then:

- **Generate**: paste or upload a Markdown file and press *Read file*. The app
  detects whether it is an **audio list** (a table of files to make) or
  **dialogues** (`Name: line` conversations) and shows what it found. Choose
  units / folders / dialogues, adjust voices, press Generate, and play the
  results in the page. *Copy CLI command* gives the equivalent command to hand to an agent.
- **Voices**: browse and audition every voice for the language.
- **Quick speak**: type text, pick a voice, listen or save a file.

Interactive API docs are at `/api/docs`.

---

## 4. Using it from an AI agent (Claude Code or Codex)

This is the workflow for "here is a Markdown file listing the audio I need:
generate it". The agent needs only a shell. No UI, no server.

### Where to start the agent

| Where you work | Open a shell here, `cd` to the project, start the agent | Run the app with |
|---|---|---|
| **WSL** (Windows Terminal, Ubuntu) | `cd ~/projects/audio-generator && claude` (or `codex`) | `./audiogen.sh …` |
| **Windows PowerShell** with the project on Windows | `cd C:\path\to\audio-generator; claude` | `.\audiogen.bat …` |
| **PowerShell, project inside WSL** | `wsl -d Ubuntu-24.04 --cd ~/projects/audio-generator` then start the agent in that shell | `./audiogen.sh …` |
| **macOS Terminal** | `cd ~/projects/audio-generator && claude` | `./audiogen.sh …` |

The agent reads **`AGENTS.md`** (Codex) / **`CLAUDE.md`** (Claude Code) in the
project root automatically; they contain these same instructions, so it
already knows the commands. If you start it in another folder, tell it:
*"read /path/to/audio-generator/AGENTS.md first"*.

### What to say

> Read `AUDIO_LIST.md` and generate all the audio it asks for, in Spanish
> (Mexican). Put the files in `./site/public/audio`. Check nothing is missing.

or, for a Windows path from WSL: *"the list is `\\wsl.localhost\Ubuntu-24.04\home\me\course\AUDIO_LIST.md`"*
(the agent converts it with `wslpath -u`; `C:\Users\me\x.md` becomes `/mnt/c/Users/me/x.md`).

### What the agent does (the contract)

```bash
cd ~/projects/audio-generator

# 1. See what the file asks for. Makes no audio, needs no internet.
./audiogen.sh inspect /path/AUDIO_LIST.md --lang es --locale es-MX --json

# 2. Generate it. Safe to re-run: files already made with the same text,
#    voice and speed are skipped, so an interrupted run just resumes.
./audiogen.sh generate /path/AUDIO_LIST.md --lang es --locale es-MX -o ./site/public/audio --json

# 3. Confirm every expected file exists (exit code 1 if any are missing).
./audiogen.sh verify /path/AUDIO_LIST.md --lang es -o ./site/public/audio --json
```
Useful filters on `generate`/`verify`: `--unit 1-3`, `--folder vocab,texts`,
`--id U01-B-T1,U01-B-T2`, `--match '^U03-'`, `--force`, `--jobs 8`,
`--strip site/public/audio` (drop a prefix from the unit folders), `--rate 0.9`
(override every speed), `--format mp3|wav|m4a|opus|flac`. One-off phrase:
`./audiogen.sh speak "Hola" --lang es --gender M -o hola.mp3`.

Exit codes: **0** done, **1** finished but some files failed or are missing,
**2** bad input (unknown language, list problems, unusable voice). `--json`
puts the result on stdout; progress and warnings go to stderr.

Alternative: if the UI is running, an agent can use the HTTP API instead
(`POST /api/inspect`, `POST /api/generate`, `GET /api/jobs/{id}`; see `/api/docs`).

### The audio-list format

Any Markdown with tables works. The parser looks for these pieces and
ignores everything else:

```markdown
## Unit 1: Primer contacto              <- any "## " heading starts a unit (its number is used for --unit)
Folder: `lo-01-primer-contacto/`        <- optional sub-folder for that unit's files

### B. Texts (generate at 0.8x speed)    <- a heading containing "0.8x speed" sets the speed for its tables
| ID | Where | Voice | Save as | Voice note | Text |
|---|---|---|---|---|---|
| U01-B-T1 | Greeting | **F+M** | `texts/U01-B-T1.mp3` | Sra. Martínez = F, Sr. González = M | Sra. Martínez: Buenos días. / Sr. González: Hola. |
| U01-B-T2 | Reading  | F | `texts/U01-B-T2.mp3` | LA-F1 | Me llamo Marta. ¶ Vivo en México. |
| U01-A-V03 | Hello | M | no new file: uses **U01-A-V01** | | ¡Hola! |
```

- **ID**, **Voice**, **Save as** (a backticked path), and a text column named
  after the language (`Spanish`, `Arabic`…) or `Text` / `Sentence` / `Phrase` / `Say`.
- **Voice**: `M` or `F`; several joined with `+` (`F+M`, `M+F+F2`) mean a
  dialogue. Speaker labels (`Ana:`) are cast to the listed voices by gender
  (from the note, e.g. `Ana = F`, or the language pack's name knowledge), else in
  order. `F2`/`M2` are second voices. In the text, `/` separates lines or
  turns and `¶` is a longer pause.
- **Regional voices**: a `| Code | Voice | Use |` table (`ES-F1 | es-ES-ElviraNeural | Default female`)
  defines codes; a row may name a code (`LA-F1`) or an edge-tts voice
  (`es-MX-DaliaNeural`) in its note, and it replaces the default of that gender.
- Rows saying **"no new file: uses X"** are counted but not generated.
- A simpler `| id | voice | text |` table (voice may be `edge:pt-BR-AntonioNeural`) also works;
  files are then saved as `<id>.mp3`.
- Output goes to `<out>/<unit Folder>/<Save as>`. Silence of 0.5 s is added at both ends;
  MP3, mono, 44.1 kHz, 96 kbps.

### Dialogue files

A file with no such table is read as dialogues: lines like `Ana: Hola.` under
headings. Output is one file per dialogue (`u_01_ls_01.mp3`, plus a transcript).
Gender, and so the voice, is guessed from names and roles per language;
override with `--voice 'Ana=es-MX-DaliaNeural'` or in the UI. Reference sections
(Grammar, Vocabulary, Exercises…) are skipped, and `inspect` lists what was
dropped. Try `examples/sample-dialogues.es.md`.

---

## 5. Layout

```
audiogen/             Python package
  languages/          one pack per language (names, roles, skipped headings, varieties)
  data/edge_voices.json   snapshot of all edge-tts voices (refreshable)
  audiolist.py        audio-list parser, voice casting, parallel renderer
  parser.py generate.py   dialogue parser and renderer
  service.py          shared by CLI, UI and API
  cli.py server.py    command line, web UI/API
  static/             web UI
examples/             sample list and dialogues (Spanish)
tests/                pytest (network is mocked)
output/               default output (git-ignored); data/ holds settings and a line cache
run.sh run.bat run.py   start the UI        audiogen.sh audiogen.bat   the CLI
AGENTS.md CLAUDE.md   instructions for AI agents
```

## 6. Troubleshooting

- **`ffmpeg` not found**: install it (see Install) and restart the shell.
- **`edge-tts failed … Check your internet connection`**: generation needs internet; the app retries 4 times per phrase and `generate` can simply be re-run to resume.
- **A voice is "not in the catalogue"**: run `./audiogen.sh voices --refresh --lang xx`.
- **Port busy**: `./run.sh --port 8800`. To reach the UI from another machine use `--host 0.0.0.0` (there is no login; use only on a trusted network).
- **WSL and Windows paths**: use `wslpath -u 'C:\x\y.md'`, or the `\\wsl.localhost\Ubuntu-24.04\…` form for files that live in WSL.
- **Wrong gender voice in a dialogue**: add `Name = F` to the row's voice note (audio list), or set the voice for that speaker.
