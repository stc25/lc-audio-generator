"""Korean language pack.

Course files are written directly in Korean script (Hangul), not romanised —
so there is no SPEECH_TRANSFORM here. edge-tts's `ko-KR` voices read Hangul natively.
"""

CODE, NAME, NATIVE = "ko", "Korean", "한국어"
SAMPLE_TEXT = "안녕하세요! 저는 김민지입니다. 잘 부탁드립니다."
SAMPLE_SCENE = "두 학생이 캠퍼스에서 만난다."


# Korean has no grammatical gender, and most given names are not reliably
# gendered from the word alone (many syllables show up in names of either
# sex) — so, as with the Japanese and Mandarin packs, this list is
# deliberately short and everything else falls through to alternation,
# flagged as a guess. This course's named characters are stated directly in
# SPEAKER_HINTS below.
FEMALE_NAMES = {"민지", "수진", "지은", "유진", "소연", "하은", "지영", "은지"}
MALE_NAMES = {"준호", "민수", "성민", "태현", "동현", "현우", "지훈", "영수"}
UNISEX_NAMES = {"정민", "현진", "수민"}

# Only kinship terms carry real gender. Korean sibling terms are also
# speaker-gender-dependent (a woman calls her older brother 오빠, a man calls
# his 형; a man calls his older sister 누나, a woman calls hers 언니) — but as
# a *label* naming who is speaking, both members of each pair name a person
# of the same sex, so both go in the same set below. Job words like 선생님,
# 학생, 점원 do not carry gender and are left undecided.
FEMALE_ROLES = {"어머니", "엄마", "언니", "누나", "여동생", "할머니", "이모",
                "고모", "딸", "아내", "부인", "여자친구", "아가씨", "여자",
                "며느리"}
MALE_ROLES = {"아버지", "아빠", "오빠", "형", "남동생", "할아버지", "삼촌",
              "아들", "남편", "남자친구", "남자", "사위"}

# Identical whoever is speaking — the norm for job and role words in Korean.
EPICENE = {
    "선생님", "학생", "점원", "손님", "친구", "동료", "기사님",
    "경찰관", "의사", "간호사", "점장", "직원", "접수처", "관광객",
    "유학생", "이웃", "선배", "후배", "사원", "회사원",
}

# Korean has no articles.
ARTICLES: set = set()
ARTICLE_GENDER: dict = {}

# -씨/-님 are honorifics, not gender markers reliable enough to use as
# speaker-label titles (-씨 is the neutral default for anyone), so this is
# empty rather than guessing from them.
TITLE_PATTERNS: tuple = ()


def morph(word: str):
    """Korean given names are not reliably gendered by their ending — common
    syllables like -지, -민, -현 appear in names of either sex — so, like
    Japanese and Mandarin, this never guesses from a word ending."""
    return None


# The course's named characters. Their gender is stated rather than
# inferred; gender only, no voice, so your accent and engine choices still
# apply. Keyed on both the given-name-only form this course's dialogues use
# ("민지") — via FEMALE_NAMES/MALE_NAMES above — and the full surname+given
# name form, in case your own course addresses characters that way instead.
SPEAKER_HINTS = {
    "김민지": {"gender": "F", "note": "김민지 (Kim Minji) — named character"},
    "박준호": {"gender": "M", "note": "박준호 (Park Junho) — named character"},
}
SPEAKER_LABELS: dict = {}   # names are already in native script; nothing to translate

# Korean particles (은/는/이/가/도/야 and so on) attach directly to the noun
# with no space, so the space-tokenised matching self_gender() relies on
# wouldn't reliably catch inflected forms like 오빠가/누나는 — as with
# Japanese and Mandarin, this stays empty rather than half-working.
SELF_GENDER_MARKERS: dict = {}

NON_SPEAKER_LABELS = {
    "note", "notes", "language notes", "vocabulary", "key vocabulary",
    "grammar", "translation", "example", "exercise", "answer", "answers",
    "key", "tip", "objective", "objectives", "learning objectives", "topic",
    "title", "level", "summary", "table", "dialogue", "conversation",
    "romanization", "romanisation", "pronunciation", "ko", "en", "english",
    "korean", "audio", "image", "figure", "http", "https", "www",
    "문법", "단어", "어휘", "문화", "발음", "메모", "연습", "정답",
}

SKIP_HEADINGS = [
    "grammar", "문법",
    "vocabulary", "key vocabulary", "단어", "어휘", "word list",
    "language notes", "language note", "notes", "note", "메모",
    "exercise", "exercises", "연습", "연습문제",
    "answer key", "answers", "정답",
    "culture", "문화",
    "pronunciation", "발음",
    "learning objectives", "objectives", "학습목표",
]

CONSOLIDATION_HEADINGS = {
    "putting it all together", "put it all together", "putting it together",
    "all together", "consolidation", "recap", "종합", "총복습",
}

ACCENT_LONG = {"ko_KR": "Korean (Standard/Seoul)"}


# --- Voice grouping. The voice catalogue itself comes from a live edge-tts
# snapshot; the pack only says which locales belong to the language, how to
# label them, and which voices are preferred as the M/F pair of each locale.
EDGE_LOCALES = ('ko-',)
LOCALE_LABELS = {
    'ko_KR': 'South Korea (Standard/Seoul)',
}
ACCENTS = LOCALE_LABELS
DEFAULT_ACCENT = 'ko_KR'
PREFERRED_PAIRS = {
    'ko_KR': {'M': 'ko-KR-InJoonNeural', 'F': 'ko-KR-SunHiNeural'},
}
VARIANTS_NOTE = 'Standard (Seoul) Korean only; edge-tts has a single ko-KR locale.'
