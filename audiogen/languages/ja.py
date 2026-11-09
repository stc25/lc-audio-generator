"""Japanese language pack.

Unlike the Mandarin pack, course files are written directly in Japanese
script (hiragana, katakana and kanji), not romaji — so there is no
SPEECH_TRANSFORM here. edge-tts's ja-JP voices read kanji natively.
"""

CODE, NAME, NATIVE = "ja", "Japanese", "日本語"
SAMPLE_TEXT = "こんにちは！私は田中美咲です。よろしくお願いします。"
SAMPLE_SCENE = "二人の学生がキャンパスで会う。"

# Japanese has no grammatical gender, and most given names are not reliably
# gendered from the word alone (the same name can be read multiple ways, and
# common endings are shared by both sexes) — so these lists are deliberately
# short and everything else falls through to alternation, flagged as a guess.
# This course's named characters are stated directly in SPEAKER_HINTS below.
FEMALE_NAMES = {"美咲", "陽子", "さくら", "愛", "恵", "真由美", "由美", "花子"}
MALE_NAMES = {"健太", "大輔", "翔太", "拓也", "浩二", "誠", "直樹", "健一"}
UNISEX_NAMES = {"薫", "つかさ", "ひろ"}

# Only kinship terms carry real gender (hahha "mother" vs chichi "father");
# job words like sensei, gakusei, ten'in do not, and are left undecided.
FEMALE_ROLES = {"母", "お母さん", "おかあさん", "姉", "お姉さん", "おねえさん",
                "妹", "娘", "祖母", "おばあさん", "おばさん", "彼女", "奥さん",
                "妻", "女の子", "女性", "お嬢さん"}
MALE_ROLES = {"父", "お父さん", "おとうさん", "兄", "お兄さん", "おにいさん",
              "弟", "息子", "祖父", "おじいさん", "おじさん", "彼", "旦那さん",
              "夫", "男の子", "男性"}

# Identical whoever is speaking — the norm for job and role words in Japanese.
EPICENE = {
    "先生", "学生", "店員", "お客さん", "客", "友達", "同僚", "運転手",
    "警察官", "医者", "看護師", "店長", "スタッフ", "受付", "観光客",
    "留学生", "隣人", "先輩", "後輩", "社員", "会社員", "生徒",
}

# Japanese has no articles.
ARTICLES: set = set()
ARTICLE_GENDER: dict = {}

# -さん/-くん/-ちゃん are honorifics, not gender markers reliable enough to
# use as speaker-label titles (-さん is the neutral default for anyone; -くん
# and -ちゃん skew by age and familiarity more than by sex), so this is empty
# rather than guessing from them.
TITLE_PATTERNS: tuple = ()


def morph(word: str):
    """Japanese given names are not reliably gendered by their ending —
    common moras like -ko, -mi, -e appear in ordinary nouns too — so, like
    Mandarin, this never guesses from a word ending."""
    return None


# The course's named characters. Their gender is stated rather than
# inferred; gender only, no voice, so your accent and engine choices still
# apply.
SPEAKER_HINTS = {
    "田中美咲": {"gender": "F", "note": "田中美咲 (Tanaka Misaki) — named character"},
    "山田健太": {"gender": "M", "note": "山田健太 (Yamada Kenta) — named character"},
    "鈴木大輔": {"gender": "M", "note": "鈴木大輔 (Suzuki Daisuke) — named character"},
    "中村愛": {"gender": "F", "note": "中村愛 (Nakamura Ai) — named character"},
    "佐藤先生": {"gender": "F", "note": "佐藤先生 (Satō-sensei) — the teacher"},
    "エマ": {"gender": "F", "note": "エマ (Emma) — exchange student, named character"},
}
SPEAKER_LABELS: dict = {}   # names are already in native script; nothing to translate

# The space-tokenised matching self_gender() relies on doesn't apply to
# unsegmented Japanese text (no spaces between words), so — as with
# Mandarin — this stays empty rather than half-working.
SELF_GENDER_MARKERS: dict = {}

NON_SPEAKER_LABELS = {
    "note", "notes", "language notes", "vocabulary", "key vocabulary",
    "grammar", "translation", "example", "exercise", "answer", "answers",
    "key", "tip", "objective", "objectives", "learning objectives", "topic",
    "title", "level", "summary", "table", "dialogue", "conversation",
    "romaji", "kana", "kanji", "hiragana", "katakana", "pronunciation",
    "ja", "en", "english", "japanese", "audio", "image", "figure",
    "http", "https", "www", "文法", "単語", "語彙", "文化", "発音", "メモ",
    "練習", "解答",
}

SKIP_HEADINGS = [
    "grammar", "文法",
    "vocabulary", "key vocabulary", "単語", "語彙", "word list",
    "language notes", "language note", "notes", "note", "メモ",
    "exercise", "exercises", "練習", "練習問題",
    "answer key", "answers", "解答",
    "culture", "文化",
    "pronunciation", "発音",
    "learning objectives", "objectives", "学習目標",
]

CONSOLIDATION_HEADINGS = {
    "putting it all together", "put it all together", "putting it together",
    "all together", "consolidation", "recap", "まとめ", "総復習",
}

ACCENT_LONG = {"ja_JP": "Japanese (Standard/Tokyo)"}


# --- Voice grouping. The voice catalogue itself comes from a live edge-tts
# snapshot; the pack only says which locales belong to the language, how to
# label them, and which voices are preferred as the M/F pair of each locale.
EDGE_LOCALES = ('ja-',)
LOCALE_LABELS = {
    'ja_JP': 'Japan (Standard/Tokyo)',
}
ACCENTS = LOCALE_LABELS
DEFAULT_ACCENT = 'ja_JP'
PREFERRED_PAIRS = {
    'ja_JP': {'M': 'ja-JP-KeitaNeural', 'F': 'ja-JP-NanamiNeural'},
}
VARIANTS_NOTE = 'Standard (Tokyo) Japanese only; edge-tts has a single ja-JP locale with one male and one female voice.'
