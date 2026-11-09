"""Turkish language pack.

Turkish has no grammatical gender (the pronoun "o" means he, she and it), so
gender comes only from first names, kinship words and the honorific titles
`Hanım` (Ms/Mrs, after the name) and `Bey` (Mr, after the name). Both Turkish
spellings and plain-ASCII forms (without ç ş ğ ı ö ü) are listed, because the
matcher folds accents but cannot fold dotless ı to i.
"""

CODE, NAME, NATIVE = "tr", "Turkish", "Türkçe"
SAMPLE_TEXT = "Merhaba! Benim adım Ayşe. Bugün nasılsınız?"
SAMPLE_SCENE = "Dersin ilk günü: Ayşe koridorda Mehmet ile tanışır."

FEMALE_NAMES = {
    "ayşe", "ayse", "fatma", "emine", "hatice", "zeynep", "elif", "merve",
    "esra", "büşra", "busra", "özge", "ozge", "selin", "derya", "gül", "gul",
    "leyla", "aylin", "burcu", "ebru", "sevgi", "seda", "sibel",
    "songül", "songul", "nur", "nihal", "melek", "meryem", "havva", "hülya",
    "hulya", "gamze", "pınar", "pinar", "yasemin", "dilara", "ceren", "ece",
    "irem", "defne", "nazlı", "nazli", "sena", "ipek", "buse", "damla",
    "gizem", "tuğba", "tugba", "aslı", "asli", "cansu", "melis", "sevil",
    "nilüfer", "nilufer", "müge", "muge", "şeyma", "seyma", "rabia", "kübra",
    "kubra", "betül", "betul", "sümeyye", "sumeyye", "ayten",
    "serap", "filiz", "figen", "nermin", "perihan", "sevim",
}

MALE_NAMES = {
    "mehmet", "mustafa", "ahmet", "ali", "hüseyin", "huseyin", "hasan",
    "ibrahim", "ismail", "yusuf", "murat", "ömer",
    "omer", "osman", "emre", "burak", "cem", "kemal", "mert", "selim",
    "serkan", "volkan", "oğuz", "oguz", "tolga", "onur",
    "fatih", "kerem", "arda", "berk", "eren", "kaan", "tuna",
    "furkan", "yasin", "enes", "hakan", "okan", "sinan", "taner", "tarık",
    "tarik", "orhan", "necati", "cengiz", "erdem", "gökhan", "gokhan",
    "levent", "metin", "recep", "süleyman", "suleyman", "ramazan", "bülent",
    "bulent", "halil", "ilker", "ibrahim", "kadir", "ufuk", "salih", "veli",
    "bora", "çağlar", "caglar", "alper", "erkan", "turgut", "yılmaz",
}

UNISEX_NAMES = {"deniz", "yağmur", "yagmur", "güneş", "gunes", "can", "umut",
                "barış", "baris", "uğur", "ugur", "ilkay",
                "ege", "evren", "gökçe", "gokce", "kıvanç",
                "kivanc", "tan", "dilek", "ay", "irmak", "aydın", "aydin"}

FEMALE_ROLES = {
    "kadın", "kadin", "hanım", "hanim", "hanımefendi", "hanimefendi", "bayan",
    "kız", "kiz", "kızım", "kizim", "anne", "annem", "abla", "ablam",
    "kız kardeş", "kiz kardes", "kızkardeş", "teyze", "hala", "yenge",
    "büyükanne", "buyukanne", "babaanne", "anneanne", "nine", "gelin",
    "kraliçe", "kralice", "karı", "kari", "kadın öğretmen",
    "kadın doktor", "kadın sesi", "anlatıcı kadın", "komşu teyze",
    "bayanlar", "kızlar", "kadın müşteri",
}

MALE_ROLES = {
    "adam", "erkek", "bey", "beyefendi", "bay", "oğul", "ogul", "oğlum",
    "oglum", "oğlan", "oglan", "baba", "babam", "abi", "abim", "ağabey",
    "agabey", "abe", "erkek kardeş", "erkek kardes", "amca", "dayı", "dayi",
    "dede", "büyükbaba", "buyukbaba", "damat", "koca", "kral", "efendi",
    "delikanlı", "delikanli", "beyler", "erkek öğretmen", "erkek doktor",
    "erkek sesi", "anlatıcı erkek", "erkek müşteri", "komşu amca",
}

EPICENE = {
    "öğretmen", "ogretmen", "öğrenci", "ogrenci", "doktor", "hemşire",
    "hemsire", "garson", "müşteri", "musteri", "satıcı", "satici", "turist",
    "misafir", "komşu", "komsu", "arkadaş", "arkadas", "çocuk", "cocuk",
    "kişi", "kisi", "ses", "anlatıcı", "anlatici", "şoför", "sofor",
    "sekreter", "müdür", "mudur", "polis", "yolcu", "eş", "es", "kardeş",
    "kardes", "a", "b", "c", "1", "2", "3", "voice", "student", "teacher",
    "tourist",
}

ARTICLES: set = set()          # no definite article; "bir" is "a/one"
ARTICLE_GENDER: dict = {}

TITLE_PATTERNS = (
    (r"\bhanım\b|\bhanim\b|\bhanımefendi\b|\bbayan\b|\bmrs\b|\bms\b|\bmiss\b", "F"),
    (r"\bbey\b|\bbeyefendi\b|\bbay\b|\bmr\b", "M"),
)


def morph(word: str):
    """Turkish word shape carries no gender. Always None."""
    return None


# Turkish adjectives do not agree, but the speaker can say it outright.
SELF_GENDER_MARKERS = {
    "F": ["ben kadınım", "ben bir kadınım", "ben kızım", "ben anneyim",
          "ben bir anneyim", "kocam var", "kocam", "eşim erkek",
          "ben bir kızım", "ben gelinim"],
    "M": ["ben erkeğim", "ben bir erkeğim", "ben oğlanım", "ben babayım",
          "ben bir babayım", "karım var", "karım", "ben damadım",
          "ben bir oğlanım"],
}

NON_SPEAKER_LABELS = {
    "not", "notlar", "kelime", "kelimeler", "sözcükler", "sozcukler",
    "kelime hazinesi", "dilbilgisi", "çeviri", "ceviri", "örnek", "ornek",
    "örnekler", "alıştırma", "alistirma", "alıştırmalar", "cevap",
    "cevaplar", "diyalog", "konuşma", "konusma", "sahne", "anlatıcı",
    "anlatici", "özet", "ozet", "giriş", "giris", "dikkat", "önemli",
    "onemli", "hedefler", "kültür", "kultur", "telaffuz", "başlık", "baslik",
    "seviye", "konu", "bağlam", "baglam", "kaynak", "ses",
    "note", "notes", "vocabulary", "key vocabulary", "grammar", "translation",
    "example", "exercise", "answer", "answers", "key", "tip", "objective",
    "objectives", "learning objectives", "topic", "title", "level", "summary",
    "table", "dialogue", "conversation", "scene", "narrator", "context",
    "pronunciation", "tr", "en", "english", "turkish", "audio", "http",
    "https", "www",
}

SKIP_HEADINGS = [
    "grammar", "dilbilgisi", "gramer",
    "vocabulary", "key vocabulary", "word list", "kelime hazinesi",
    "kelimeler", "sözcükler",
    "exercise", "exercises", "alıştırma", "alıştırmalar", "alistirma",
    "answer key", "answers", "cevaplar", "cevap anahtarı", "cevap anahtari",
    "notes", "note", "not", "notlar",
    "culture", "kültür", "kultur", "cultural note", "kültürel not",
    "pronunciation", "telaffuz",
    "learning objectives", "objectives", "hedefler", "öğrenme hedefleri",
]

CONSOLIDATION_HEADINGS = {
    "putting it all together", "put it all together", "putting it together",
    "all together", "consolidation", "recap", "tekrar", "özet", "ozet",
    "hepsi bir arada", "genel tekrar", "pekiştirme", "pekistirme",
}

EDGE_LOCALES = ("tr-",)
LOCALE_LABELS = {"tr_TR": "Turkey"}
ACCENTS = LOCALE_LABELS
ACCENT_LONG = {"tr_TR": "Istanbul Turkish (Turkey)"}
DEFAULT_ACCENT = "tr_TR"
PREFERRED_PAIRS = {
    "tr_TR": {"M": "tr-TR-AhmetNeural", "F": "tr-TR-EmelNeural"},
}
VARIANTS_NOTE = ("Standard (Istanbul) Turkish only; edge-tts has one tr-TR locale with a male and a female voice, and Cypriot, Azerbaijani and other Turkic varieties have no Turkish-pack voice.")
