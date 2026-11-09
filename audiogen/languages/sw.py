"""Swahili language pack.

Swahili has no grammatical gender (a single pronoun "yeye" covers he and she)
and its noun classes say nothing about the sex of a person, so gender comes
from first names, kinship words and titles only. Everything else falls
through to alternation, flagged as a guess.
"""

CODE, NAME, NATIVE = "sw", "Swahili", "Kiswahili"
SAMPLE_TEXT = "Habari! Jina langu ni Amina. Unaendeleaje leo?"
SAMPLE_SCENE = "Siku ya kwanza ya darasa: Amina anakutana na Juma barabarani."

FEMALE_NAMES = {
    "amina", "fatuma", "halima", "zawadi", "neema", "asha", "mariam",
    "mariamu", "rehema", "zuhura", "salma", "aisha", "khadija", "hadija",
    "zainab", "zaituni", "rose", "grace", "esther", "upendo", "furaha",
    "tumaini", "witness", "mwajuma", "mwanaidi", "mwanaisha",
    "saida", "sofia", "janeth", "joyce", "happiness", "pendo", "nuru",
    "latifa", "subira", "faraja", "imani", "veronica", "agnes", "lucy",
    "mwanahawa", "rukia", "ruqayya", "sharifa", "dorcas", "naomi", "jamila",
    "wanjiru", "akinyi", "atieno", "wambui", "njeri", "nyambura", "chebet",
    "adhiambo", "wairimu",
}

MALE_NAMES = {
    "juma", "hamisi", "ali", "omari", "omar", "abdallah", "abdullah",
    "mohamed", "mohammed", "athumani", "salim", "said", "saidi", "rashidi",
    "rashid", "bakari", "yusuf", "yusufu", "ibrahimu", "ibrahim", "hassani",
    "hassan", "jabali", "kassim", "kasimu", "mussa", "musa", "issa", "isa",
    "daudi", "david", "john", "yohana", "petro", "peter", "paulo", "paul",
    "joseph", "yusuph", "emmanuel", "elias", "baraka", "jabir",
    "kamau", "otieno", "odhiambo", "kipchoge", "mwangi", "kariuki", "njoroge",
    "ochieng", "kibet", "mwinyi", "shabani", "selemani", "suleiman", "tabu",
    "haji", "iddi", "jumanne", "samweli", "mathayo",
}

UNISEX_NAMES = {"amani", "bahati", "heri", "wema", "salama", "mosi"}

FEMALE_ROLES = {
    "mwanamke", "mama", "mamangu", "mke", "bibi", "dada", "binti", "msichana",
    "nyanya", "shangazi", "bi",
    "mama mdogo", "mama mkubwa", "mwanamama", "mwari", "malkia", "kijakazi",
    "sauti ya kike", "msimulizi mwanamke", "mhudumu wa kike",
}

MALE_ROLES = {
    "mwanamume", "mwanaume", "mwanamme", "baba", "babu", "mume", "bwana",
    "kaka", "kijana", "mvulana", "mjomba",
    "baba mdogo", "baba mkubwa", "mzee", "mfalme", "askari",
    "bw", "sauti ya kiume", "msimulizi mwanamume", "mhudumu wa kiume",
    "mtoto wa kiume", "mwana wa kiume",
}

EPICENE = {
    "mtu", "mgeni", "mwanafunzi", "mwalimu", "mhudumu", "daktari", "muuguzi",
    "mpishi", "mwandishi", "msimulizi", "dereva", "mteja", "mfanyakazi",
    "mtalii", "jirani", "rafiki", "mtoto", "mzazi", "mkurugenzi", "sauti",
    "mpita njia", "a", "b", "c", "1", "2", "3", "voice", "student",
    "teacher", "tourist",
}

ARTICLES: set = set()          # Swahili has no articles
ARTICLE_GENDER: dict = {}

TITLE_PATTERNS = (
    (r"\bbibi\b|\bbi\b|\bmama\b|\bmrs\b|\bms\b|\bmiss\b|\bdada\b|\bmwanamke\b", "F"),
    (r"\bbwana\b|\bbw\b|\bmzee\b|\bbaba\b|\bmr\b|\bkaka\b|\bmwanamume\b", "M"),
)


def morph(word: str):
    """Swahili shape says nothing about the speaker's sex. Always None."""
    return None


# No agreement on adjectives, but a speaker's own words about themselves can
# still settle it ("mimi ni mama", "mimi ni baba").
SELF_GENDER_MARKERS = {
    "F": ["mimi ni mama", "mimi ni msichana", "mimi ni mwanamke",
          "mimi ni dada", "mimi ni bibi", "nina mume", "mume wangu",
          "mimi ni binti", "nimeolewa", "mimi ni mjamzito",
          "mimi ni nyanya"],
    "M": ["mimi ni baba", "mimi ni mvulana", "mimi ni mwanamume",
          "mimi ni kaka", "mimi ni bwana", "nina mke", "mke wangu",
          "nimeoa", "mimi ni babu", "mimi ni kijana"],
}

NON_SPEAKER_LABELS = {
    "dokezo", "maelezo", "maelezo ya lugha", "msamiati", "sarufi", "tafsiri",
    "mfano", "mifano", "zoezi", "mazoezi", "jibu", "majibu", "mazungumzo",
    "mazungumzo ya kwanza", "tukio", "muhtasari", "utangulizi",
    "angalia", "muhimu", "malengo", "utamaduni", "matamshi", "kichwa", "ngazi",
    "mada", "muktadha", "chanzo",
    "note", "notes", "vocabulary", "key vocabulary", "grammar", "translation",
    "example", "exercise", "answer", "answers", "key", "tip", "objective",
    "objectives", "learning objectives", "topic", "title", "level", "summary",
    "table", "dialogue", "conversation", "scene", "narrator", "context",
    "pronunciation", "sw", "en", "english", "swahili", "audio", "http",
    "https", "www",
}

SKIP_HEADINGS = [
    "grammar", "sarufi",
    "vocabulary", "key vocabulary", "word list", "msamiati",
    "exercise", "exercises", "zoezi", "mazoezi",
    "answer key", "answers", "majibu",
    "notes", "note", "dokezo", "maelezo", "maelezo ya lugha",
    "culture", "utamaduni", "cultural note",
    "pronunciation", "matamshi",
    "learning objectives", "objectives", "malengo",
]

CONSOLIDATION_HEADINGS = {
    "putting it all together", "put it all together", "putting it together",
    "all together", "consolidation", "recap", "marudio", "muhtasari",
    "kwa pamoja", "yote kwa pamoja",
}

EDGE_LOCALES = ("sw-",)
LOCALE_LABELS = {"sw_KE": "Kenya", "sw_TZ": "Tanzania"}
ACCENTS = LOCALE_LABELS
ACCENT_LONG = {"sw_KE": "Kenyan Swahili",
               "sw_TZ": "Tanzanian Swahili (Kiunguja-based standard)"}
DEFAULT_ACCENT = "sw_TZ"
PREFERRED_PAIRS = {
    "sw_KE": {"M": "sw-KE-RafikiNeural", "F": "sw-KE-ZuriNeural"},
    "sw_TZ": {"M": "sw-TZ-DaudiNeural", "F": "sw-TZ-RehemaNeural"},
}
VARIANTS_NOTE = ("Standard Swahili is taught on the Tanzanian (Kiunguja) model; edge-tts has a Kenyan (sw-KE) and a Tanzanian (sw-TZ) voice pair, and coastal dialects such as Kimvita or Sheng have no voices.")
