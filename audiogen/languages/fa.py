"""Persian (Farsi) language pack.

Written for course files in Persian script, optionally with a Finglish
transliteration in parentheses after each line — the script is spoken, the
Finglish is kept on screen as a reading aid and never read aloud.

Persian marks no grammatical gender at all: adjectives never agree, and most
occupation nouns (daneshjoo "student", mohandes "engineer", raanande "driver")
are used unchanged for men and women alike. Gender therefore comes from an
explicit title (Aqaa-ye / Khanom), an inherently gendered kinship word
(baraadar "brother" vs khahar "sister"), or a known first name — never from
word shape, so there is no adjective-agreement signal to mine the way Arabic
or Romance packs do.
"""

CODE, NAME, NATIVE = "fa", "Persian", "فارسی"
RTL = True                      # the UI renders dialogue lines right-to-left
PARENTHETICAL_LABEL = "Finglish"
SAMPLE_TEXT = "سلام! صبح بخیر. حالت چطوره؟"
SAMPLE_SCENE = "سارا و آرش روز اول کلاس فارسی با هم آشنا می‌شن."

FEMALE_NAMES = {
    "سارا", "نیلوفر", "رویا", "مریم", "زهرا", "فاطمه", "لیلا", "یاسمن",
    "نگار", "شیرین", "پریسا", "آزاده", "سمیرا", "الهام", "مهسا", "نازنین",
    "ترانه", "شیدا", "ویدا", "آیدا", "بهاره", "سحر", "شبنم", "گلناز",
    "پروانه", "رها", "هستی", "کیمیا", "ستاره",
    "sara", "saraa", "niloofar", "niloufar", "roya", "ronya", "maryam",
    "zahra", "zahraa", "fatemeh", "fateme", "leila", "layla", "yasaman",
    "yasmin", "negar", "shirin", "parisa", "azadeh", "samira", "elham",
    "mahsa", "nazanin", "taraneh", "shida", "vida", "aida", "bahareh",
    "sahar", "shabnam", "golnaz", "parvaneh", "raha", "hasti", "kimia",
    "setareh",
}

MALE_NAMES = {
    "آرش", "کیان", "رضا", "علی", "محمد", "حسین", "امیر", "بابک", "دانیال",
    "سعید", "فرهاد", "کاوه", "پیمان", "بهروز", "سیاوش", "نیما", "شاهین",
    "یاشار", "کامران", "مهدی", "حمید", "جواد", "بیژن", "فرید", "سهراب",
    "arash", "kian", "reza", "ali", "mohammad", "hossein", "amir", "babak",
    "daniel", "danial", "saeed", "farhad", "kaveh", "peyman", "behrouz",
    "siavash", "nima", "shahin", "yashar", "kamran", "mehdi", "hamid",
    "javad", "bijan", "farid", "sohrab",
}

UNISEX_NAMES = {"پارسا", "parsa", "ایلیا", "ilia", "elia"}

# Persian marks almost no noun with grammatical gender; these are the
# genuinely gendered exceptions -- kinship and a handful of honorifics --
# listed as whole words rather than a shared root with two endings.
FEMALE_ROLES = {
    "خواهر", "مادر", "دختر", "زن", "عمه", "خاله", "مادربزرگ", "دوست‌دختر",
    "دوست دختر", "ملکه", "خانم", "بانو", "نامزد دختر", "همسر زن",
}
MALE_ROLES = {
    "برادر", "پدر", "پسر", "شوهر", "عمو", "دایی", "پدربزرگ", "دوست‌پسر",
    "دوست پسر", "پادشاه", "آقا",
}

FEMALE_ROLES |= {
    "khahar", "khâhar", "madar", "mâdar", "dokhtar", "zan", "ameh", "khaleh",
    "madarbozorg", "mâdarbozorg", "doost dokhtar", "malake", "khanom",
    "khanoom", "banoo", "banu",
}
MALE_ROLES |= {
    "baraadar", "baradar", "pedar", "pesar", "shohar", "amoo", "amu",
    "daei", "dayi", "pedarbozorg", "doost pesar", "padeshah", "agha",
    "aghaa",
}

# Occupation and generic nouns that carry no gender of their own in Persian --
# guessing from these would be worse than alternating.
EPICENE = {
    "دوست", "همکار", "همسایه", "مشتری", "مهمان", "مسافر", "راننده", "مدیر",
    "مهندس", "دکتر", "معلم", "استاد", "دانشجو", "دانش‌آموز", "دانش آموز",
    "پرستار", "منشی", "گارسون", "فروشنده", "غریبه", "شخص", "صدا",
    "الف", "ب", "ج", "a", "b", "c", "1", "2", "3",
    "doost", "hamkar", "hamsaye", "moshtari", "mehman", "mosafer",
    "ranande", "modir", "mohandes", "doktor", "moallem", "ostad",
    "daneshjoo", "daneshamooz", "parastar", "monshi", "garson",
    "forooshandeh", "gharibeh", "shakhs", "sedaa", "seda", "voice",
    "student", "teacher", "waiter", "customer",
}

# Persian has no definite article to strip, and nothing in the script marks
# gender by itself -- both left empty on purpose.
ARTICLES: set = set()
ARTICLE_PREFIXES: tuple = ()
ARTICLE_GENDER: dict = {}

TITLE_PATTERNS = (
    (r"\bخانم\b|\bسرکار خانم\b|\bبانو\b", "F"),
    (r"\bآقای\b|\bجناب آقای\b|\bجناب\b", "M"),
    (r"\bkhanom\b|\bkhanoom\b|\bbanoo\b|\bbanu\b", "F"),
    (r"\bagh?a-?ye\b|\baqa-?ye\b|\baghaye\b|\baqaye\b", "M"),
)

_F_SUFFIX = ("ه",)      # weak signal only -- many Arabic-origin female names
_M_SUFFIX = ()          # (fatemeh, zahreh...) keep the Arabic ة as Persian ه


def morph(word: str):
    """The ه ending is a weak feminine hint, carried over from Arabic-origin
    names whose ة became ه in Persian spelling (fatima -> fatemeh). There is
    no positive masculine marker, so masculine is never inferred from shape."""
    w = (word or "").strip()
    if len(w) < 3:
        return None
    for suf in _F_SUFFIX:
        if w.endswith(suf):
            return "F"
    return None


NON_SPEAKER_LABELS = {
    "نکته", "نکات", "واژگان", "واژگان کلیدی", "دستور", "دستور زبان", "ترجمه",
    "مثال", "مثال‌ها", "تمرین", "تمرین‌ها", "پاسخ", "پاسخ‌ها", "گفتگو",
    "مکالمه", "اهداف", "هدف", "خلاصه", "مقدمه", "تذکر", "مهم",
    "note", "notes", "language notes", "vocabulary", "key vocabulary",
    "grammar", "translation", "example", "exercise", "answer", "answers",
    "key", "tip", "objective", "objectives", "learning objectives", "topic",
    "title", "level", "summary", "table", "dialogue", "conversation",
    "transliteration", "romanisation", "romanization", "pronunciation",
    "finglish", "fa", "en", "english", "persian", "farsi",
    "audio", "http", "https", "www",
}

SKIP_HEADINGS = [
    "grammar", "دستور", "دستور زبان",
    "vocabulary", "key vocabulary", "واژگان", "واژگان کلیدی", "word list",
    "language notes", "language note", "notes", "note", "نکات", "نکته",
    "exercise", "exercises", "تمرین", "تمرین‌ها",
    "answer key", "answers", "پاسخ‌ها",
    "culture", "فرهنگ", "cultural note",
    "pronunciation", "تلفظ", "transliteration", "finglish",
    "learning objectives", "objectives", "اهداف", "هدف",
]

CONSOLIDATION_HEADINGS = {
    "putting it all together", "put it all together", "putting it together",
    "all together", "consolidation", "recap",
    "مرور", "جمع‌بندی", "جمع بندی",
}

ACCENT_LONG = {"fa_IR": "Modern Persian (Iran)"}


SELF_GENDER_MARKERS: dict = {}    # no speaker-agreement clues defined for this language

# --- Voice grouping. The voice catalogue itself comes from a live edge-tts
# snapshot; the pack only says which locales belong to the language, how to
# label them, and which voices are preferred as the M/F pair of each locale.
EDGE_LOCALES = ('fa-',)
LOCALE_LABELS = {
    'fa_IR': 'Iran',
}
ACCENTS = LOCALE_LABELS
DEFAULT_ACCENT = 'fa_IR'
PREFERRED_PAIRS = {
    'fa_IR': {'M': 'fa-IR-FaridNeural', 'F': 'fa-IR-DilaraNeural'},
}
VARIANTS_NOTE = 'Iranian (Tehran) Persian only; edge-tts offers fa-IR, and spoken colloquial forms will be read as written, with no Dari or Tajik voices.'
