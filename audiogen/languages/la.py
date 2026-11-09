"""Latin language pack.

edge-tts has no Latin voice. The pack reads Latin with the Italian voices,
the closest available approximation of Ecclesiastical (Italianate) Latin
pronunciation. SPEECH_TRANSFORM strips macrons and breves first, because the
Italian voices stumble on them.

Latin marks gender on the noun ending: -a / -ae feminine (puella, domina),
-us / -i masculine (servus, magister is the common -er exception, listed
explicitly). First-declension masculine nouns (poeta, nauta, agricola) and
names (Seneca, Agrippa) are listed so the -a rule does not misfire.
"""

import re as _re
import unicodedata as _ud

CODE, NAME, NATIVE = "la", "Latin", "Latina"
SAMPLE_TEXT = "Salve! Mihi nomen est Iulia. Quid agis hodie?"
SAMPLE_SCENE = "Primus dies scholae: Iulia Marcum in via videt."

# --- Macrons and breves are removed before synthesis; the app shows the
# converted text so nothing is spoken that you have not seen.
SPEECH_LABEL = "without macrons"
_STRIP = {0x0304, 0x0306}          # combining macron, combining breve


def SPEECH_TRANSFORM(text: str):
    """Remove macrons and breves (ā ē ī ō ū ȳ, ă ĕ ĭ ŏ ŭ, upper case too)."""
    d = _ud.normalize("NFD", text or "")
    return _ud.normalize("NFC", "".join(c for c in d if ord(c) not in _STRIP))


FEMALE_NAMES = {
    "iulia", "julia", "cornelia", "livia", "claudia", "caecilia", "cecilia",
    "flavia", "aemilia", "octavia", "aurelia", "lucia", "marcia", "tullia",
    "valeria", "sabina", "antonia", "cassia", "fabia", "hortensia", "lesbia",
    "lydia", "maria", "paulina", "pompeia", "servilia", "sempronia",
    "terentia", "agrippina", "cynthia", "delia", "helena", "livilla",
    "poppaea", "lavinia", "camilla", "cleopatra", "dido", "penelopa",
    "vesta", "iuno", "minerva", "venus", "diana", "ceres", "lucretia",
    "porcia", "fulvia", "calpurnia", "clodia", "scribonia", "plautia",
    "rufina", "silvia", "vera", "veronica", "anna", "monica", "agatha",
}

MALE_NAMES = {
    "marcus", "lucius", "quintus", "gaius", "caius", "publius", "titus",
    "sextus", "decimus", "gnaeus", "cnaeus", "aulus", "tiberius", "iulius",
    "julius", "cornelius", "claudius", "flavius", "marcellus", "augustus",
    "cicero", "caesar", "brutus", "cato", "horatius", "vergilius", "ovidius",
    "seneca", "antonius", "octavianus", "valerius", "aurelius", "paulus",
    "petrus", "iohannes", "johannes", "iustinus", "rufus", "sulla",
    "pompeius", "crassus", "agrippa", "galba", "nero", "traianus",
    "hadrianus", "vespasianus", "domitianus", "constantinus", "hannibal",
    "romulus", "remus", "aeneas", "ulixes", "hercules", "mercurius",
    "iuppiter", "mars", "apollo", "neptunus", "vulcanus", "sallustius",
    "plinius", "tacitus", "livius", "martialis", "iuvenalis", "catullus",
    "lucretius", "horatius", "fabius", "mettius", "numerius", "servius",
}

UNISEX_NAMES = {"gaudens", "felix", "clemens", "constans", "innocens"}

FEMALE_ROLES = {
    "magistra", "discipula", "domina", "serva", "mater", "filia", "soror",
    "avia", "amita", "matertera", "uxor", "puella", "femina", "mulier",
    "regina", "dea", "ancilla", "nutrix", "coqua", "mercatrix", "medica",
    "amica", "vicina", "hospita", "matrona", "virgo", "nupta",
    "puellae", "feminae", "matres", "reginae", "ancillae", "nympha",
    "sacerdotissa", "imperatrix", "gladiatrix", "poetria",
    "cauponaria", "ostiaria", "lectrix", "narratrix", "vox muliebris",
}

MALE_ROLES = {
    "magister", "discipulus", "dominus", "servus", "pater", "filius",
    "frater", "avus", "avunculus", "vir", "puer", "rex", "deus", "miles",
    "agricola", "poeta", "nauta", "scriba", "mercator", "medicus", "amicus",
    "vicinus", "senex", "iuvenis", "imperator", "consul", "senator",
    "coquus", "caupo", "gladiator", "maritus",
    "pueri", "viri", "patres", "fratres", "servi", "discipuli", "domini",
    "pirata", "auriga", "incola", "advena", "ostiarius", "lector",
    "narrator", "nuntius", "legatus", "centurio", "tribunus",
    "vox virilis", "senatores", "milites",
}

EPICENE = {
    "civis", "hospes", "sacerdos", "homo", "infans", "parens", "comes",
    "conviva", "iudex", "testis", "vox", "persona", "tiro", "auctor",
    "cliens", "dux", "princeps", "a", "b", "c", "1", "2", "3", "voice",
    "student", "teacher",
}

ARTICLES: set = set()           # Latin has no articles
ARTICLE_GENDER: dict = {}

TITLE_PATTERNS = (
    (r"\bdomina\b|\bmatrona\b|\bdomna\b|\bsoror\b", "F"),
    (r"\bdominus\b|\bdomnus\b|\bfrater\b|\bpater\b", "M"),
)

_F_SUFFIX = ("a", "ae", "trix", "issa")
_M_SUFFIX = ("us", "orum")


def morph(word: str):
    """Guess from a Latin ending: -a/-ae feminine, -us masculine. Weak signal;
    masculine first-declension nouns are caught earlier by the role list."""
    w = _SPEECH(word or "").lower()
    if len(w) < 4:
        return None
    for suf in sorted(_F_SUFFIX, key=len, reverse=True):
        if w.endswith(suf):
            return "F"
    for suf in _M_SUFFIX:
        if w.endswith(suf):
            return "M"
    return None


_SPEECH = SPEECH_TRANSFORM

# Latin predicates agree with the speaker (laeta sum / laetus sum). Macron-free
# spellings only.
SELF_GENDER_MARKERS = {
    "F": ["sum puella", "ego sum puella", "sum femina", "sum mater",
          "sum filia", "sum magistra", "sum discipula", "sum domina",
          "sum romana", "laeta sum", "fessa sum", "parata sum",
          "contenta sum", "sola sum", "nupta sum"],
    "M": ["sum puer", "ego sum puer", "sum vir", "sum pater", "sum filius",
          "sum magister", "sum discipulus", "sum dominus", "sum romanus",
          "laetus sum", "fessus sum", "paratus sum", "contentus sum",
          "solus sum", "nuptus sum"],
}

NON_SPEAKER_LABELS = {
    "nota", "notae", "vocabularium", "lexicon", "grammatica", "translatio",
    "exemplum", "exempla", "exercitium", "exercitia", "responsum",
    "responsa", "colloquium", "dialogus", "scaena", "scena", "narrator",
    "narratrix", "argumentum", "summa", "praefatio", "index", "fons",
    "titulus", "cultura", "pronuntiatio", "propositum", "contextus",
    "note", "notes", "vocabulary", "key vocabulary", "grammar", "translation",
    "example", "exercise", "answer", "answers", "key", "tip", "objective",
    "objectives", "learning objectives", "topic", "title", "level",
    "summary", "table", "dialogue", "conversation", "scene", "context",
    "pronunciation", "la", "lat", "en", "english", "latin", "audio",
    "http", "https", "www",
}

SKIP_HEADINGS = [
    "grammar", "grammatica",
    "vocabulary", "key vocabulary", "word list", "vocabularium", "lexicon",
    "exercise", "exercises", "exercitium", "exercitia",
    "answer key", "answers", "responsa", "solutiones",
    "notes", "note", "notae", "nota",
    "culture", "cultura", "cultural note",
    "pronunciation", "pronuntiatio",
    "learning objectives", "objectives", "propositum",
]

CONSOLIDATION_HEADINGS = {
    "putting it all together", "put it all together", "putting it together",
    "all together", "consolidation", "recap", "repetitio", "recapitulatio",
    "summa", "omnia simul",
}

# --- Voices: Latin is read by the Italian voices.
EDGE_LOCALES = ("it-",)
LOCALE_LABELS = {"it_IT": "Italian voice (Ecclesiastical-style approximation)"}
ACCENTS = LOCALE_LABELS
DEFAULT_ACCENT = "it_IT"
PREFERRED_PAIRS = {
    "it_IT": {"M": "it-IT-DiegoNeural", "F": "it-IT-ElsaNeural"},
}
VARIANTS_NOTE = ("edge-tts has no Latin voices, so Latin is read with Italian voices as an approximation of Ecclesiastical pronunciation; macrons and breves are stripped, and Classical (Restored) pronunciation is not available.")
