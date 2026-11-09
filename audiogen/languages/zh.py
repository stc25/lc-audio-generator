"""Chinese (Mandarin) language pack.

The course files are written in tone-marked pinyin. Every Mandarin engine
reads characters, so each line is converted through `sda/pinyin.py` before
synthesis; the conversion is dictionary-driven and shown to you in the app.
"""

import re as _re
import unicodedata as _ud

from . import zh_lexicon as _lexicon

# --- Pinyin -> characters converter (from the original sda/pinyin.py).
WORD_RE = _re.compile(r"[^\W\d_]+(?:['’][^\W\d_]+)*", _re.UNICODE)

# Full-width punctuation reads more naturally in Mandarin TTS: it carries the
# pause and intonation that the ASCII equivalents do not.
PUNCT = {",": "，", ".": "。", "?": "？", "!": "！", ":": "：", ";": "；",
         "(": "（", ")": "）", "—": "，", "-": ""}

TONE_MARKS = {0x0304: 1, 0x0301: 2, 0x030C: 3, 0x0300: 4}


def strip_tone(word: str) -> tuple:
    """'Nǐ' -> ('ni', 3). Tone 5 (neutral) when unmarked."""
    tone = 5
    out = []
    for ch in _ud.normalize("NFD", word):
        cp = ord(ch)
        if cp in TONE_MARKS:
            tone = TONE_MARKS[cp]
        elif _ud.category(ch) != "Mn":
            out.append(ch)
    return "".join(out).lower().replace("’", "'"), tone


def _norm(word: str) -> str:
    return word.lower().replace("’", "'")


def to_hanzi(text: str, lexicon=None) -> tuple:
    """Convert a pinyin line to characters.

    Returns (converted_text, unmapped_words). Punctuation and spacing are
    preserved in place; characters are written without spaces between them,
    which is what a Mandarin engine expects.
    """
    if lexicon is None:
        lexicon = _lexicon

    phrases = getattr(lexicon, "PHRASES", {})
    words = getattr(lexicon, "WORDS", {})
    initial = getattr(lexicon, "INITIAL_WORDS", {})
    max_phrase = max((len(p.split()) for p in phrases), default=1)

    tokens = []          # (kind, text) where kind is "w" or "x"
    pos = 0
    for m in WORD_RE.finditer(text):
        if m.start() > pos:
            tokens.append(("x", text[pos:m.start()]))
        tokens.append(("w", m.group(0)))
        pos = m.end()
    if pos < len(text):
        tokens.append(("x", text[pos:]))

    out = []
    unmapped = []
    i = 0
    while i < len(tokens):
        kind, tok = tokens[i]
        if kind == "x":
            out.append("".join(PUNCT.get(c, c) for c in tok
                               if not c.isspace()) or "")
            i += 1
            continue

        # longest phrase match, skipping over the whitespace tokens between
        matched = False
        for n in range(max_phrase, 1, -1):
            seq, j, taken = [], i, 0
            while j < len(tokens) and taken < n:
                if tokens[j][0] == "w":
                    seq.append(_norm(tokens[j][1]))
                    taken += 1
                elif tokens[j][1].strip():
                    break          # real punctuation ends the phrase
                j += 1
            if taken == n and " ".join(seq) in phrases:
                out.append(phrases[" ".join(seq)])
                i = j
                matched = True
                break
        if matched:
            continue

        key = _norm(tok)
        first_word = not any(k == "w" for k, _ in tokens[:i])
        if first_word and key in initial:
            out.append(initial[key])
            i += 1
            continue
        if key in words:
            out.append(words[key])
        else:
            out.append(tok)
            unmapped.append(tok)
        i += 1

    return "".join(out), unmapped





CODE, NAME, NATIVE = "zh", "Chinese", "中文"
SAMPLE_TEXT = "Nǐ hǎo! Wǒ jiào Wáng Míng. Hěn gāoxìng rènshi nǐ."
SAMPLE_SCENE = "Liǎng ge xuésheng zài kāfēitīng jiànmiàn."

# --- Pinyin in, characters out. The app shows the converted text next to the
# original so nothing is spoken that you have not seen.
SPEECH_TRANSFORM = to_hanzi
SPEECH_LABEL = "Chinese characters"

# Mandarin has no grammatical gender: role nouns like fúwùyuán (service
# worker) or lǎoshī (teacher) say nothing about the person, and given names
# are not reliably gendered either. So the lists here are deliberately short
# and everything else falls through to alternation, flagged as a guess.
FEMALE_NAMES = {"nà", "měi", "yàn", "jìng", "xiù", "fāng", "lì", "juān",
                "yīng", "xiá", "lán", "yún", "xuě", "tíng", "wēn"}
MALE_NAMES = {"míng", "wěi", "qiáng", "jūn", "gāng", "yǒng", "bīn", "hào",
              "lěi", "tāo", "peng", "péng", "chāo", "yǔ", "fēi", "jié"}
UNISEX_NAMES = {"yǔ", "fēi", "xīn", "lè", "chén", "qí", "yì"}

FEMALE_ROLES = {"māma", "mǔqīn", "jiějie", "mèimei", "nǚ'ér", "nǎinai",
                "wàipó", "āyí", "gūgu", "nǚshì", "tàitai", "xiǎojiě",
                "nǚ", "qīzi", "sūnnǚ"}
MALE_ROLES = {"bàba", "fùqīn", "gēge", "dìdi", "érzi", "yéye", "wàigōng",
              "shūshu", "jiùjiu", "xiānsheng", "nán", "zhàngfu", "sūnzi"}

# Identical whoever is speaking — the norm in Chinese.
EPICENE = {
    "lǎoshī", "xuésheng", "tóngxué", "fúwùyuán", "kèrén", "qiántái", "lùrén",
    "sījī", "shòuhuòyuán", "yàoshī", "yīshēng", "gōngchéngshī", "péngyou",
    "tóngshì", "jǐngchá", "sījī", "shīfu", "lǚkè", "gùkè", "zhǔrèn",
    "jīnglǐ", "zuòjiā", "yǎnyuán", "gēshǒu", "rén", "a", "b", "c", "1", "2",
    "3", "jiǎ", "yǐ",
}

ARTICLES: set = set()
ARTICLE_GENDER: dict = {}

TITLE_PATTERNS = (
    (r"\bnǚshì\b|\bxiǎojiě\b|\btàitai\b", "F"),
    (r"\bxiānsheng\b", "M"),
)


def morph(word: str):
    """Chinese carries no gender in word endings, so never guess from one."""
    return None


# The course's named characters. Chinese given names do not reliably signal
# gender, so these are stated rather than inferred; gender only, no voice, so
# your accent and engine choices still apply.
SPEAKER_HINTS = {
    "li na": {"gender": "F", "note": "Lǐ Nà 李娜 — named character"},
    "wang ming": {"gender": "M", "note": "Wáng Míng 王明 — named character"},
    "chen yu": {"gender": "M", "note": "Chén Yǔ 陈宇 — named character"},
    "lin fei": {"gender": "F", "note": "Lín Fēi 林飞 — named character"},
    "zhang laoshi": {"gender": "F", "note": "Zhāng lǎoshī 张老师 — the teacher"},
}
SPEAKER_LABELS = {
    "li na": "Lǐ Nà 李娜",
    "wang ming": "Wáng Míng 王明",
    "chen yu": "Chén Yǔ 陈宇",
    "lin fei": "Lín Fēi 林飞",
    "zhang laoshi": "Zhāng lǎoshī 张老师",
    "fuwuyuan": "Fúwùyuán 服务员",
    "keren": "Kèrén 客人",
    "qiantai": "Qiántái 前台",
    "tongxue": "Tóngxué 同学",
    "luren": "Lùrén 路人",
    "siji": "Sījī 司机",
    "shouhuoyuan": "Shòuhuòyuán 售货员",
    "yaoshi": "Yàoshī 药师",
}

SELF_GENDER_MARKERS: dict = {}      # Mandarin gives no such agreement clues

NON_SPEAKER_LABELS = {
    "note", "notes", "language notes", "vocabulary", "key vocabulary",
    "grammar", "translation", "example", "exercise", "answer", "answers",
    "key", "tip", "objective", "objectives", "learning objectives", "topic",
    "title", "level", "summary", "table", "dialogue", "conversation",
    "pinyin", "hanzi", "characters", "tone", "tones", "pronunciation",
    "zh", "en", "english", "chinese", "audio", "image", "figure",
    "http", "https", "www",
}

SKIP_HEADINGS = [
    "grammar", "yǔfǎ",
    "vocabulary", "key vocabulary", "cíhuì", "word list",
    "language notes", "language note", "notes", "note",
    "exercise", "exercises", "liànxí",
    "answer key", "answers",
    "culture", "wénhuà",
    "pronunciation", "tones", "fāyīn",
    "learning objectives", "objectives",
]

CONSOLIDATION_HEADINGS = {
    "putting it all together", "put it all together", "putting it together",
    "all together", "zōnghé liànxí", "fùxí", "consolidation", "recap",
}

ACCENT_LONG = {"zh_CN": "Mandarin (Mainland)", "zh_TW": "Mandarin (Taiwan)",
               "zh_HK": "Cantonese (Hong Kong)"}


# --- Voice grouping. The voice catalogue itself comes from a live edge-tts
# snapshot; the pack only says which locales belong to the language, how to
# label them, and which voices are preferred as the M/F pair of each locale.
EDGE_LOCALES = ('zh-', 'yue-', 'wuu-', 'cmn-')
LOCALE_LABELS = {
    'zh_CN': 'Mainland China',
    'zh_TW': 'Taiwan',
    'zh_HK': 'Hong Kong (Cantonese)',
    'zh_CN_liaoning': 'Mainland China — Liaoning (Northeastern) dialect',
    'zh_CN_shaanxi': 'Mainland China — Shaanxi dialect',
    'yue_CN': 'Cantonese (Mainland)',
    'wuu_CN': 'Wu (Shanghainese)',
}
ACCENTS = LOCALE_LABELS
DEFAULT_ACCENT = 'zh_CN'
PREFERRED_PAIRS = {
    'zh_CN': {'M': 'zh-CN-YunxiNeural', 'F': 'zh-CN-XiaoxiaoNeural'},
    'zh_TW': {'M': 'zh-TW-YunJheNeural', 'F': 'zh-TW-HsiaoChenNeural'},
    'zh_HK': {'M': 'zh-HK-WanLungNeural', 'F': 'zh-HK-HiuMaanNeural'},
    'zh_CN_liaoning': {'F': 'zh-CN-liaoning-XiaobeiNeural'},
    'zh_CN_shaanxi': {'F': 'zh-CN-shaanxi-XiaoniNeural'},
}
VARIANTS_NOTE = 'Mandarin (Mainland zh_CN and Taiwan zh_TW) is the default; Cantonese is available via the Hong Kong voices, and there are single-voice Liaoning and Shaanxi dialect-accented Mandarin voices; pinyin input is converted to characters before synthesis.'
