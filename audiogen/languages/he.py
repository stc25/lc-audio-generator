"""Hebrew language pack.

Written for course files in Hebrew script (usually unvocalised, optionally
with a transliteration in parentheses, which is shown but not spoken). Hebrew
has grammatical gender on nouns, adjectives and verbs: feminine nouns often
end in -ה or -ת (and -ית for professions), masculine nouns have no marker.
The definite article is the prefix ה-.
"""

CODE, NAME, NATIVE = "he", "Hebrew", "עברית"
RTL = True
PARENTHETICAL_LABEL = "transliteration"
SAMPLE_TEXT = "שלום! קוראים לי דנה. מה שלומך היום?"
SAMPLE_SCENE = "היום הראשון בקורס: דנה פוגשת את יובל במסדרון."

FEMALE_NAMES = {
    "דנה", "נועה", "מיכל", "שרה", "רונית", "יעל", "תמר", "מירב", "רחל",
    "לאה", "רות", "אסתר", "מרים", "הדס", "שירה", "אורית", "גלית",
    "נעמי", "מאיה", "שני", "ענת", "אילנה", "דפנה", "חנה",
    "אביגיל", "יפה", "ורד", "סיגל", "קרן", "נטע", "הילה", "אלה",
    "ליאת", "אפרת", "מורן", "שושנה", "דורית", "אורנה",
    "dana", "noa", "michal", "sara", "sarah", "ronit", "yael", "tamar",
    "merav", "rachel", "leah", "ruth", "esther", "miriam", "hadas", "shira",
    "orit", "galit", "naomi", "maya", "shani", "anat", "ilana", "dafna",
    "hanna", "chana", "avigail", "yafa", "vered", "sigal", "keren", "neta",
    "hila", "ella", "liat", "efrat", "moran", "shoshana", "dorit", "orna",
}

MALE_NAMES = {
    "דוד", "יוסי", "משה", "יובל", "אבי", "דני", "רון", "אורי",
    "איתי", "נועם", "יונתן", "אברהם", "יצחק", "יעקב",
    "שמואל", "אליהו", "דניאל", "מיכאל", "אלון", "עומר", "תומר", "גדי",
    "רועי", "אסף", "ניר", "עידו", "אלי", "שלמה", "בני", "חיים", "מאיר",
    "יהונתן", "עמוס", "שמעון", "ראובן", "אהרון", "בנימין", "אילן",
    "dani", "david", "yossi", "moshe", "yuval", "avi", "ron", "uri", "itai",
    "noam", "yonatan", "avraham", "yitzhak", "yaakov", "shmuel", "eliyahu",
    "daniel", "michael", "alon", "omer", "tomer", "gadi", "roi", "assaf",
    "nir", "ido", "eli", "shlomo", "benny", "haim", "chaim", "meir",
    "amos", "shimon", "reuven", "aharon", "binyamin", "ilan",
}

UNISEX_NAMES = {"עדי", "טל", "ליאור", "גל", "שחר", "עמית", "גיל",
                "אריאל", "רותם", "זיו", "אור", "מור", "שי",
                "adi", "tal", "lior", "gal", "shachar", "amit", "gil",
                "ariel", "rotem", "ziv", "or", "mor", "shay"}

FEMALE_ROLES = {
    "גברת", "גב", "אישה", "אשה", "ילדה", "בת", "אמא", "אמה", "אחות", "סבתא",
    "דודה", "אשתי", "תלמידה", "סטודנטית", "מלצרית",
    "מוכרת", "פקידה", "רופאה", "מנהלת", "עובדת", "חברה", "שכנה", "לקוחה",
    "מזכירה", "שוטרת", "טבחית", "נהגת", "סבתא", "מתורגמנית", "ספרנית",
    "גברתי",
    "gveret", "isha", "yalda", "bat", "ima", "achot", "savta", "doda",
    "talmida", "meltzarit", "mochret", "pkida", "rofa", "rofah",
    "menahelet", "ovedet", "chavera", "shchena", "lakucha", "mazkira",
}

MALE_ROLES = {
    "אדון", "מר", "איש", "ילד", "בן", "אבא", "אב", "אח", "סבא", "דוד",
    "בעלי", "תלמיד", "סטודנט", "מלצר", "מוכר", "פקיד", "רופא", "מנהל",
    "עובד", "חבר", "שכן", "לקוח", "מזכיר", "שוטר", "טבח", "נהג", "מתורגמן",
    "ספרן", "אדוני", "נער", "גבר",
    "adon", "ish", "yeled", "ben", "aba", "av", "ach", "saba", "dod",
    "talmid", "meltzar", "mocher", "pakid", "rofe", "menahel",
    "oved", "chaver", "shachen", "lakoach", "mazkir", "shoter", "nahag",
}

EPICENE = {
    "מורה", "אדם", "תייר", "קול", "אורח", "אורחת",
    "עוזר", "דובר", "a", "b", "c", "1", "2", "3", "voice",
    "student", "teacher", "tourist", "adam", "more", "kol",
}

# The article ה- is a prefix, not a word: it is stripped before lookup.
ARTICLES = {"ה", "ha"}
ARTICLE_PREFIXES = ("ה", "ha-")
ARTICLE_GENDER: dict = {}

TITLE_PATTERNS = (
    (r"\bגברת\b|\bגב['׳]|\bגברתי\b|\bgveret\b|\bmrs\b|\bms\b", "F"),
    (r"\bאדון\b|\bאדוני\b|\bמר\b|\badon\b|\bmr\b", "M"),
)

# -ית (profession/nationality), -ה and -ת are feminine markers. Masculine has
# no positive ending, so it is never inferred from shape.
_F_SUFFIX = ("ית", "ה", "ת")
_NOT_FEMININE = {"אבא", "לילה", "משה", "נח", "יהודה"}


def morph(word: str):
    """Guess feminine from -ית / -ה / -ת. Returns 'F' or None."""
    w = (word or "").strip()
    if w.startswith("ה") and len(w) > 4:
        w = w[1:]
    if len(w) < 3 or w in _NOT_FEMININE:
        return None
    for suf in _F_SUFFIX:
        if w.endswith(suf):
            return "F"
    return None


# Hebrew first-person predicates agree with the speaker.
SELF_GENDER_MARKERS = {
    "F": ["אני עייפה", "אני שמחה", "אני מוכנה", "אני נשואה", "אני רווקה",
          "אני תלמידה", "אני רעבה", "אני מצטערת",
          "אני אוהבת", "אני גרה", "אני עובדת",
          "אני ישראלית", "אני אמריקאית", "אני בריטית", "אני סטודנטית",
          "ani ayefa", "ani smecha", "ani muchana", "ani talmida"],
    "M": ["אני עייף", "אני שמח", "אני מוכן", "אני נשוי", "אני רווק",
          "אני תלמיד", "אני רעב", "אני מצטער", "אני אוהב", "אני עובד",
          "אני ישראלי", "אני אמריקאי", "אני בריטי", "אני סטודנט",
          "ani ayef", "ani sameach", "ani muchan", "ani talmid"],
}

NON_SPEAKER_LABELS = {
    "הערה", "הערות", "אוצר מילים", "מילים", "דקדוק", "תרגום", "דוגמה",
    "דוגמאות", "תרגיל", "תרגילים", "תשובה", "תשובות", "דיאלוג", "שיחה",
    "סצנה", "קריין", "מספר", "הקשר", "סיכום", "מבוא", "שימו לב", "חשוב",
    "מטרות", "תרבות", "הגייה", "כותרת", "רמה", "נושא", "מקור", "שמע",
    "note", "notes", "vocabulary", "key vocabulary", "grammar", "translation",
    "example", "exercise", "answer", "answers", "key", "tip", "objective",
    "objectives", "learning objectives", "topic", "title", "level", "summary",
    "table", "dialogue", "conversation", "scene", "narrator", "context",
    "transliteration", "pronunciation", "he", "en", "english", "hebrew",
    "audio", "http", "https", "www",
}

SKIP_HEADINGS = [
    "grammar", "דקדוק",
    "vocabulary", "key vocabulary", "word list", "אוצר מילים", "מילון",
    "exercise", "exercises", "תרגיל", "תרגילים",
    "answer key", "answers", "תשובות", "פתרונות",
    "notes", "note", "הערה", "הערות",
    "culture", "תרבות", "cultural note",
    "pronunciation", "הגייה", "transliteration", "תעתיק",
    "learning objectives", "objectives", "מטרות",
]

CONSOLIDATION_HEADINGS = {
    "putting it all together", "put it all together", "putting it together",
    "all together", "consolidation", "recap", "חזרה", "סיכום", "הכול ביחד",
    "הכל ביחד",
}

EDGE_LOCALES = ("he-",)
LOCALE_LABELS = {"he_IL": "Israel"}
ACCENTS = LOCALE_LABELS
ACCENT_LONG = {"he_IL": "Modern Hebrew (Israel)"}
DEFAULT_ACCENT = "he_IL"
PREFERRED_PAIRS = {
    "he_IL": {"M": "he-IL-AvriNeural", "F": "he-IL-HilaNeural"},
}
VARIANTS_NOTE = ("Modern Israeli Hebrew only; edge-tts has one he-IL locale (a male and a female voice), unvocalised text is read with the voice's own vowel guesses, and Biblical or Yiddish text is not supported.")
