"""Arabic language pack.

Written for course files in Arabic script, optionally with a romanisation in
parentheses after each line — the script is spoken, the romanisation is kept
on screen as a reading aid and never read aloud.
"""

import re as _re

CODE, NAME, NATIVE = "ar", "Arabic", "العربية"
RTL = True                      # the UI renders dialogue lines right-to-left
PARENTHETICAL_LABEL = "romanisation"
SAMPLE_TEXT = "مرحبا! صباح الخير. كيف حالك اليوم؟"
SAMPLE_SCENE = "سمر وكريم يلتقيان في أول يوم من الدورة."

FEMALE_NAMES = {
    "سمر", "فاطمة", "مريم", "عائشة", "زينب", "خديجة", "نور", "ليلى", "سارة",
    "هدى", "رنا", "دينا", "منى", "ريم", "لينا", "ندى", "أمل", "سلمى", "ياسمين",
    "جميلة", "نادية", "سعاد", "وفاء", "هبة", "رند", "شيماء", "إيمان", "أسماء",
    "بثينة", "حنان", "رغد", "سناء", "عبير", "غادة", "لمى", "مها", "نجلاء",
    "samar", "fatima", "maryam", "aisha", "layla", "sara", "nour", "rana",
    "dina", "mona", "reem", "lina", "nada", "amal", "salma", "yasmin", "huda",
    "raanya", "rania", "raania", "hala", "haala", "jamila", "jamiila",
    "sawsan", "suha", "suhaa", "abeer", "ghada", "ghaada", "maha", "mahaa",
}

MALE_NAMES = {
    "كريم", "محمد", "أحمد", "علي", "حسن", "حسين", "عمر", "خالد", "سامي",
    "طارق", "ياسر", "زياد", "رامي", "سليم", "مروان", "نبيل", "هشام", "وليد",
    "أمين", "بشير", "جمال", "حازم", "رشيد", "سعيد", "شريف", "صلاح", "عادل",
    "عصام", "فادي", "فيصل", "ماجد", "مازن", "منير", "نادر", "يوسف", "إبراهيم",
    "kariim", "karim", "mohammed", "muhammad", "ahmad", "ahmed", "ali", "omar",
    "khalid", "sami", "tariq", "yasser", "ziad", "rami", "salim", "marwan",
    "hisham", "walid", "said", "fadi", "majid", "nader", "yousef", "ibrahim",
}

UNISEX_NAMES = {"نور", "جهاد", "إسلام", "رجاء", "أمل",
                "nour", "noor", "nuur", "jihad", "islam", "rajaa", "amal"}

# Arabic marks gender on the noun itself, usually with the ة ending.
FEMALE_ROLES = {
    "معلمة", "مدرسة", "طالبة", "أستاذة", "دكتورة", "طبيبة", "ممرضة", "نادلة",
    "بائعة", "موظفة", "سكرتيرة", "مديرة", "زبونة", "صديقة", "جارة", "أخت",
    "أم", "بنت", "ابنة", "زوجة", "خالة", "عمة", "جدة", "سيدة", "آنسة",
    "مهندسة", "محامية", "صحفية", "كاتبة", "شرطية", "طاهية", "مضيفة",
}
MALE_ROLES = {
    "معلم", "مدرس", "طالب", "أستاذ", "دكتور", "طبيب", "ممرض", "نادل",
    "بائع", "موظف", "سكرتير", "مدير", "زبون", "صديق", "جار", "أخ", "أب",
    "ابن", "ولد", "زوج", "خال", "عم", "جد", "سيد", "رجل", "شاب",
    "مهندس", "محامي", "صحفي", "كاتب", "شرطي", "طاه", "سائق", "بواب",
}

# Romanised role nouns. Transliteration is not standardised, so the common
# spellings of each word are all listed rather than guessed at.
FEMALE_ROLES |= {
    "muallima", "muʿallima", "mualima", "mudarrisa", "ustaadha", "ustadha",
    "ustaatha", "taaliba", "talibah", "taliba", "duktoora", "duktura",
    "doktora", "tabiiba", "tabiba", "mumarrida", "naadila", "nadila",
    "baayiʿa", "baayia", "baaya", "muwaZZafa", "muwazzafa", "muazzafa",
    "mudiira", "mudira", "zaboona", "zabuna", "SaaHiba", "sahiba", "saahiba",
    "ukht", "umm", "bint", "zawja", "jadda", "sayyida", "aanisa", "anisa",
    "muhandisa", "muhaamiya", "muhamiya", "Taahiya", "tahiya", "mudiifa",
    "garsoona", "jarsoona", "sitt", "madam",
}
MALE_ROLES |= {
    "muallim", "muʿallim", "mualim", "mudarris", "ustaadh", "ustadh",
    "ustaath", "ustaz", "Taalib", "talib", "duktoor", "duktur", "doktor",
    "tabiib", "tabib", "mumarrid", "naadil", "nadil", "baayiʿ", "baayi",
    "baaya3", "muwaZZaf", "muwazzaf", "muazzaf", "mudiir", "mudir",
    "zaboon", "zabun", "SaaHib", "sahib", "saahib", "akh", "abb", "ibn",
    "walad", "zawj", "jadd", "sayyid", "rajul", "shaabb", "shab",
    "muhandis", "muhaami", "muhami", "saayiq", "sayyaaq", "bawwaab",
    "garsoon", "jarsoon", "garson", "waiter", "shurTi", "shurti",
}

EPICENE = {"شخص", "ضيف", "مسافر", "زائر", "أ", "ب", "ج", "a", "b", "c",
           "1", "2", "3", "صوت",
           "shakhS", "shakhs", "Dayf", "dayf", "musaafir", "musafir",
           "zaa'ir", "zair", "Soot", "sawt", "voice", "student", "teacher",
           "passer-by", "passerby"}

ARTICLES = {"ال", "al", "el", "il", "ال"}
ARTICLE_PREFIXES = ("ال", "al-", "el-", "il-")
ARTICLE_GENDER: dict = {}

TITLE_PATTERNS = (
    (r"\bالسيدة\b|\bالآنسة\b|\bسيدة\b|\bآنسة\b|\bد\.\s*\S+ة\b", "F"),
    (r"\bالسيد\b|\bسيد\b|\bالأستاذ\b|\bالشيخ\b", "M"),
    (r"\bustaadha\b|\bustadha\b|\bustaatha\b|\bsayyida\b|\bmadam\b", "F"),
    (r"\bustaadh\b|\bustadh\b|\bustaath\b|\bustaz\b|\bsayyid\b|\bshaykh\b|\bsheikh\b", "M"),
)

_F_SUFFIX = ("ة", "اء", "ى")
_M_SUFFIX = ()


def morph(word: str):
    """The ة (taa marbuuta) ending is a reliable feminine marker on a role
    noun. There is no comparable positive marker for masculine, so masculine
    is never inferred from shape alone."""
    w = (word or "").strip()
    if w.startswith("ال") and len(w) > 4:
        w = w[2:]
    if len(w) < 3:
        return None
    for suf in _F_SUFFIX:
        if w.endswith(suf):
            return "F"
    return None


# --- Gender from a speaker's own words. Arabic agrees on adjectives, so
# "أنا منيح" and "أنا منيحة" identify the speaker directly. The regex entry
# generalises it: أنا followed by a word ending in ة.
SELF_GENDER_MARKERS = {
    "F": ["منيحة", "بخيرة", "سعيدة", "مبسوطة", "جاهزة", "متأكدة", "طالبة",
          "معلمة", "مدرسة", "متزوجة", "عزباء", "تعبانة", "مشغولة", "جديدة",
          "مصرية", "أردنية", "لبنانية", "سورية", "سعودية", "إنجليزية",
          "أمريكية", "فرنسية", "مسرورة", "موجودة", "قادمة", "ذاهبة",
          "re:\\bأنا\\s+\\S+ة\\b", "re:\\bوأنا\\s+\\S+ة\\b"],
    # The masculine adjective is also the adverb ("mniiH" = fine / well), so
    # "ma baʿrif al-Qaahira mniiH" ("I don't know Cairo well") is not a man
    # speaking. The ambiguous ones are therefore anchored to a first-person
    # pronoun; only forms that cannot double as adverbs stay as bare words.
    "M": ["أعزب", "متزوج", "مصري", "أردني", "لبناني", "سوري", "سعودي",
          "إنجليزي", "بريطاني", "أمريكي", "فرنسي", "مسرور",
          "re:\\b(?:و?أنا|وإنا)\\s+(?:منيح|سعيد|مبسوط|جاهز|متأكد|طالب|معلم"
          "|مدرس|تعبان|مشغول|جديد|موجود|قادم|ذاهب|كويس|تمام)\\b",
          "re:\\bأنا\\s+ال?(?:طالب|معلم|مدرس|أستاذ|مهندس|دكتور|موظف)\\b"],
}

NON_SPEAKER_LABELS = {
    "ملاحظة", "ملاحظات", "مفردات", "قواعد", "ترجمة", "مثال", "أمثلة", "تمرين",
    "تمارين", "إجابة", "إجابات", "الحوار", "حوار", "محادثة", "المفردات",
    "القواعد", "الأهداف", "هدف", "أهداف", "ملخص", "مقدمة", "تنبيه", "مهم",
    "note", "notes", "language notes", "vocabulary", "key vocabulary",
    "grammar", "translation", "example", "exercise", "answer", "answers",
    "key", "tip", "objective", "objectives", "learning objectives", "topic",
    "title", "level", "summary", "table", "dialogue", "conversation",
    "transliteration", "romanisation", "romanization", "pronunciation",
    "ar", "en", "english", "arabic", "audio", "http", "https", "www",
}

SKIP_HEADINGS = [
    "grammar", "قواعد", "القواعد",
    "vocabulary", "key vocabulary", "مفردات", "المفردات", "word list",
    "language notes", "language note", "notes", "note", "ملاحظات", "ملاحظة",
    "exercise", "exercises", "تمارين", "تمرين",
    "answer key", "answers", "إجابات",
    "culture", "ثقافة", "cultural note",
    "pronunciation", "النطق", "transliteration", "romanisation",
    "learning objectives", "objectives", "الأهداف", "أهداف",
]

CONSOLIDATION_HEADINGS = {
    "putting it all together", "put it all together", "putting it together",
    "all together", "consolidation", "recap", "مراجعة", "الخلاصة", "خلاصة",
    "نجمع كل شيء",
}

ACCENT_LONG = {
    "ar_SA": "Modern Standard Arabic", "ar_EG": "Egyptian Arabic",
    "ar_JO": "Levantine Arabic (Jordanian)",
    "ar_LB": "Levantine Arabic (Lebanese)",
    "ar_AE": "Gulf Arabic (Emirati)", "ar_MA": "Moroccan Arabic",
}

# --- Which variety a course file is actually written in. MSA and the spoken
# dialects differ in very common words, so this is a reliable signal and it
# matters: an MSA voice reading Levantine text sounds wrong.
_LEV_WORDS = ["منيح", "منيحة", "كمان", "إنتي", "إنته", "هلق", "شو", "ليش",
              "هيك", "كتير", "بدي", "بدك", "مبسوط", "تمام", "مرحبا",
              "بالتوفيق", "يلا", "لسا", "هون", "وين"]
_EGY_WORDS = ["إزيك", "إزيك؟", "عايز", "عايزة", "دلوقتي", "كده", "ازاي",
              "مش", "أوي", "حاجة", "بتاع", "فين", "امبارح", "النهاردة"]
_GULF_WORDS = ["شلونك", "وايد", "زين", "أبغى", "أبي", "حق", "الحين", "چذي"]
_MSA_WORDS = ["بخير", "أيضاً", "أيضا", "الآن", "ماذا", "لماذا", "هكذا",
              "كثيراً", "أريد", "تريد", "هنا", "أين", "أمس", "اليوم",
              "السلام عليكم", "وعليكم السلام", "أهلاً وسهلاً", "من فضلك",
              "شكراً جزيلاً", "كيف حالك", "حسناً", "نعم", "لا"]


def _count(text, words):
    n, hits = 0, []
    for w in words:
        c = text.count(w)
        if c:
            n += c
            hits.append(w)
    return n, hits


def detect_accent(text: str) -> dict:
    """Guess the variety a course file is written in."""
    scores, hits = {}, {}
    for key, words in (("ar_JO", _LEV_WORDS), ("ar_EG", _EGY_WORDS),
                       ("ar_AE", _GULF_WORDS), ("ar_SA", _MSA_WORDS)):
        scores[key], hits[key] = _count(text, words)
    total = sum(scores.values())
    if total < 3:
        return {"accent": None, "confidence": "none", "scores": scores,
                "evidence": []}
    winner = max(scores, key=lambda k: scores[k])
    lead = scores[winner]
    rest = total - lead
    if lead < 3 or lead <= rest:
        return {"accent": None, "confidence": "mixed", "scores": scores,
                "evidence": sum((hits[k][:2] for k in hits), [])}
    return {"accent": winner,
            "confidence": "high" if lead > 2 * rest else "likely",
            "scores": scores, "evidence": hits[winner][:6]}


# --- Voice grouping. The voice catalogue itself comes from a live edge-tts
# snapshot; the pack only says which locales belong to the language, how to
# label them, and which voices are preferred as the M/F pair of each locale.
EDGE_LOCALES = ('ar-',)
LOCALE_LABELS = {
    'ar_SA': 'Saudi Arabia (MSA-leaning)',
    'ar_EG': 'Egypt',
    'ar_JO': 'Jordan',
    'ar_LB': 'Lebanon',
    'ar_AE': 'United Arab Emirates',
    'ar_MA': 'Morocco',
    'ar_BH': 'Bahrain',
    'ar_DZ': 'Algeria',
    'ar_IQ': 'Iraq',
    'ar_KW': 'Kuwait',
    'ar_LY': 'Libya',
    'ar_OM': 'Oman',
    'ar_QA': 'Qatar',
    'ar_SY': 'Syria',
    'ar_TN': 'Tunisia',
    'ar_YE': 'Yemen',
}
ACCENTS = LOCALE_LABELS
DEFAULT_ACCENT = 'ar_SA'
PREFERRED_PAIRS = {
    'ar_SA': {'M': 'ar-SA-HamedNeural', 'F': 'ar-SA-ZariyahNeural'},
    'ar_EG': {'M': 'ar-EG-ShakirNeural', 'F': 'ar-EG-SalmaNeural'},
    'ar_JO': {'M': 'ar-JO-TaimNeural', 'F': 'ar-JO-SanaNeural'},
    'ar_LB': {'M': 'ar-LB-RamiNeural', 'F': 'ar-LB-LaylaNeural'},
    'ar_AE': {'M': 'ar-AE-HamdanNeural', 'F': 'ar-AE-FatimaNeural'},
    'ar_MA': {'M': 'ar-MA-JamalNeural', 'F': 'ar-MA-MounaNeural'},
    'ar_BH': {'M': 'ar-BH-AliNeural', 'F': 'ar-BH-LailaNeural'},
    'ar_DZ': {'M': 'ar-DZ-IsmaelNeural', 'F': 'ar-DZ-AminaNeural'},
    'ar_IQ': {'M': 'ar-IQ-BasselNeural', 'F': 'ar-IQ-RanaNeural'},
    'ar_KW': {'M': 'ar-KW-FahedNeural', 'F': 'ar-KW-NouraNeural'},
    'ar_LY': {'M': 'ar-LY-OmarNeural', 'F': 'ar-LY-ImanNeural'},
    'ar_OM': {'M': 'ar-OM-AbdullahNeural', 'F': 'ar-OM-AyshaNeural'},
    'ar_QA': {'M': 'ar-QA-MoazNeural', 'F': 'ar-QA-AmalNeural'},
    'ar_SY': {'M': 'ar-SY-LaithNeural', 'F': 'ar-SY-AmanyNeural'},
    'ar_TN': {'M': 'ar-TN-HediNeural', 'F': 'ar-TN-ReemNeural'},
    'ar_YE': {'M': 'ar-YE-SalehNeural', 'F': 'ar-YE-MaryamNeural'},
}
VARIANTS_NOTE = 'Modern Standard Arabic is the written norm, while speech is dialectal; edge-tts offers 16 country voices (Saudi, Egyptian, Levantine, Gulf, Maghrebi...) that read the same Arabic script with their local accent, so pick the voice that matches the variety your course teaches.'
