"""Russian language pack.

Unlike Chinese, Russian is written in the script it is spoken in, so there is
no SPEECH_TRANSFORM here — the course file's Cyrillic text goes straight to
the engine. Russian does carry real grammatical gender (nouns, adjectives and
past-tense verbs all agree with the speaker), so the gender-guessing tables
below are much richer than Mandarin's: most first names and many role nouns
are reliable evidence, and self-reported gender ("я сказал" vs "я сказала")
is available too.
"""

CODE, NAME, NATIVE = "ru", "Russian", "Русский"
SAMPLE_TEXT = "Привет! Меня зовут Анна. Очень приятно познакомиться."
SAMPLE_SCENE = "Два студента встречаются в кафе."

# No script conversion needed — course files are already in Cyrillic.
SPEECH_TRANSFORM = None
SPEECH_LABEL = ""

# --- Gender evidence -------------------------------------------------------
# Most Russian first names carry their gender in the ending (-а/-я usually
# feminine), but there are well-known exceptions (Никита, Илья are male), so
# names are still listed explicitly rather than left to morph() alone.
FEMALE_NAMES = {
    "анна", "мария", "елена", "ольга", "наталья", "наталия", "ирина",
    "екатерина", "татьяна", "светлана", "юлия", "дарья", "александра",
    "виктория", "полина", "ксения", "анастасия", "марина", "вера",
    "надежда", "любовь", "валентина", "людмила", "нина", "галина",
    "аня", "маша", "лена", "оля", "катя", "таня",
}
MALE_NAMES = {
    "александр", "дмитрий", "максим", "сергей", "андрей", "алексей",
    "иван", "михаил", "николай", "владимир", "павел", "артём", "артем",
    "кирилл", "егор", "денис", "виктор", "игорь", "роман", "юрий",
    "борис", "никита", "илья", "лёва", "лева", "олег", "антон",
}
# Short forms shared by a masculine and a feminine given name — do not let
# morphology decide these.
UNISEX_NAMES = {"женя", "саша", "валя", "шура"}

FEMALE_ROLES = {
    "официантка", "продавщица", "учительница", "студентка", "подруга",
    "соседка", "туристка", "гостья", "актриса", "писательница",
    "спортсменка", "горничная", "стюардесса", "журналистка", "клиентка",
    "медсестра", "хозяйка", "девушка", "женщина", "иностранка",
}
MALE_ROLES = {
    "официант", "продавец", "учитель", "студент", "друг", "сосед",
    "турист", "гость", "актёр", "актер", "писатель", "спортсмен",
    "стюард", "журналист", "клиент", "хозяин", "мужчина", "молодой человек",
    "иностранец",
}

# Kinship terms — always gendered.
FEMALE_ROLES |= {"мама", "мать", "сестра", "дочь", "бабушка", "тётя", "тетя",
                 "жена", "внучка"}
MALE_ROLES |= {"папа", "отец", "брат", "сын", "дедушка", "дядя", "муж",
               "внук"}

# Job words Russian uses in the same (grammatically masculine) form for
# anyone doing the job — guessing a gender from these would be worse than
# alternating.
EPICENE = {
    "врач", "доктор", "директор", "менеджер", "гид", "водитель",
    "полицейский", "таксист", "повар", "пилот", "инженер", "программист",
    "тренер", "юрист", "администратор", "человек", "коллега", "ребёнок",
    "ребенок",
}

# Russian has no articles.
ARTICLES: set = set()
ARTICLE_GENDER: dict = {}

TITLE_PATTERNS = (
    (r"\bгоспожа\b|\bг-жа\b", "F"),
    (r"\bгосподин\b|\bг-н\b", "M"),
)


def morph(word: str):
    """Rough Russian morphology, consulted only when nothing stronger
    matched. Nouns/adjectives ending in -а/-я are usually feminine
    (nominative singular); a consonant or -й ending is usually masculine.
    The soft sign -ь is genuinely ambiguous in Russian (дверь is feminine,
    день is masculine) and is deliberately left unguessed."""
    w = (word or "").strip().lower()
    if not w:
        return None
    if w.endswith(("ая", "яя")):
        return "F"
    if w.endswith("ь"):
        return None
    if w.endswith(("а", "я")):
        return "F"
    if w and w[-1] not in "аеёиоуыэюя":
        return "M"
    return None


# A speaker's own words settle it: Russian past-tense verbs and short
# adjectives agree with the speaker's gender ("я сказал" vs "я сказала").
SELF_GENDER_MARKERS = {
    "F": {"сказала", "была", "рада", "училась", "работала", "жила",
          "родилась", "хотела", "думала", "знала", "уверена", "готова",
          "согласна", "приехала"},
    "M": {"сказал", "был", "рад", "учился", "работал", "жил", "родился",
          "хотел", "думал", "знал", "уверен", "готов", "согласен",
          "приехал"},
}

# The course's named characters. Most Russian names would already guess
# correctly from their ending, but Никита is a well-known exception (a male
# name ending in -a), so hints are stated for the whole named cast rather
# than relying on morph() for some and not others.
SPEAKER_HINTS = {
    "анна": {"gender": "F", "note": "named character — a student"},
    "максим": {"gender": "M", "note": "named character — a student"},
    "никита": {"gender": "M", "note": "named character — a male name ending "
                                      "in -а, the opposite of the usual "
                                      "pattern"},
    "елена": {"gender": "F", "note": "named character — Maxim's friend"},
    "мария ивановна": {"gender": "F", "note": "named character — the "
                                              "teacher"},
}
SPEAKER_LABELS: dict = {}

NON_SPEAKER_LABELS = {
    "note", "notes", "language notes", "vocabulary", "key vocabulary",
    "grammar", "translation", "example", "exercise", "answer", "answers",
    "key", "tip", "objective", "objectives", "learning objectives", "topic",
    "title", "level", "summary", "table", "dialogue", "conversation",
    "ru", "en", "english", "russian", "audio", "image", "figure",
    "http", "https", "www",
    "словарь", "ключевые слова", "грамматика", "перевод", "пример",
    "упражнение", "упражнения", "ответ", "ответы", "тема", "заголовок",
    "уровень", "диалог", "разговор", "русский", "английский",
}

SKIP_HEADINGS = [
    "grammar", "грамматика",
    "vocabulary", "key vocabulary", "словарь", "ключевые слова",
    "language notes", "language note", "notes", "note",
    "exercise", "exercises", "упражнения",
    "answer key", "answers", "ответы",
    "culture", "культура",
    "pronunciation", "произношение",
    "learning objectives", "objectives", "цели",
]

CONSOLIDATION_HEADINGS = {
    "putting it all together", "put it all together", "putting it together",
    "all together", "consolidation", "recap",
    "повторение", "закрепление материала", "обобщение",
}

ACCENT_LONG = {"ru_RU": "Russian (Russia)"}




# --- Voice grouping. The voice catalogue itself comes from a live edge-tts
# snapshot; the pack only says which locales belong to the language, how to
# label them, and which voices are preferred as the M/F pair of each locale.
EDGE_LOCALES = ('ru-',)
LOCALE_LABELS = {
    'ru_RU': 'Russia',
}
ACCENTS = LOCALE_LABELS
DEFAULT_ACCENT = 'ru_RU'
PREFERRED_PAIRS = {
    'ru_RU': {'M': 'ru-RU-DmitryNeural', 'F': 'ru-RU-SvetlanaNeural'},
}
VARIANTS_NOTE = 'Standard Russian only; edge-tts has one ru-RU locale with a male and a female voice.'
