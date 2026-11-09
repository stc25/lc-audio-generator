"""Greek language pack.

Greek marks gender on articles (ο/η/το) and on noun endings (-ος/-ας/-ης
masculine, -α/-η/-ια feminine), so articles and `morph()` carry most of the
work after names and roles. Course files may be in Greek script or in Latin
transliteration ("Greeklish"); both are listed.
"""

CODE, NAME, NATIVE = "el", "Greek", "Ελληνικά"
SAMPLE_TEXT = "Γεια σου! Με λένε Μαρία. Τι κάνεις σήμερα;"
SAMPLE_SCENE = "Πρώτη μέρα στο μάθημα: η Ελένη συναντά τον Νίκο στο διάδρομο."

FEMALE_NAMES = {
    "μαρία", "ελένη", "κατερίνα", "σοφία", "άννα", "αναστασία", "δήμητρα",
    "γεωργία", "χριστίνα", "ειρήνη", "νίκη", "αθηνά", "ιωάννα", "παναγιώτα",
    "βασιλική", "αγγελική", "ευαγγελία", "μαρίνα", "δέσποινα", "θεοδώρα",
    "κωνσταντίνα", "ελισάβετ", "ζωή", "ευτυχία", "σταυρούλα", "φωτεινή",
    "άρτεμις", "αλεξάνδρα", "μυρτώ", "ράνια", "κλεοπάτρα", "ιουλία", "ελπίδα",
    "πηνελόπη", "ναταλία", "μελίνα", "δανάη", "φανή", "βάσω", "τζένη",
    "maria", "eleni", "katerina", "sofia", "anna", "anastasia", "dimitra",
    "georgia", "christina", "eirini", "irini", "niki", "athina", "ioanna",
    "panagiota", "vasiliki", "angeliki", "evangelia", "marina", "despina",
    "theodora", "konstantina", "zoi", "efthymia", "foteini", "artemis",
    "alexandra", "myrto", "rania", "kleopatra", "ioulia", "penelope",
    "natalia", "melina", "danai", "fani", "vaso",
}

MALE_NAMES = {
    "γιώργος", "γιάννης", "νίκος", "κώστας", "δημήτρης", "παναγιώτης",
    "νικόλαος", "βασίλης", "χρήστος", "αλέξανδρος", "μιχάλης", "θανάσης",
    "στέλιος", "πέτρος", "παύλος", "ανδρέας", "αντώνης", "μανώλης", "σπύρος",
    "τάσος", "θοδωρής", "κωνσταντίνος", "ευάγγελος", "γρηγόρης", "λευτέρης",
    "ηλίας", "δανιήλ", "στάθης", "φώτης", "μάρκος", "ορέστης", "οδυσσέας",
    "αχιλλέας", "σωκράτης", "πλάτων", "αριστοτέλης", "ιάσονας", "απόστολος",
    "διονύσης", "άρης", "λάμπρος", "μάκης", "σταύρος", "φίλιππος",
    "giorgos", "giannis", "yannis", "nikos", "kostas", "costas", "dimitris",
    "panagiotis", "nikolaos", "vasilis", "christos", "alexandros", "michalis",
    "thanasis", "stelios", "petros", "pavlos", "andreas", "antonis",
    "manolis", "spyros", "tasos", "thodoris", "konstantinos", "evangelos",
    "grigoris", "lefteris", "ilias", "stathis", "fotis", "markos", "orestis",
    "odysseas", "achilleas", "sokratis", "platon", "aristotelis", "iasonas",
    "apostolos", "dionysis", "aris", "lambros", "makis", "stavros", "filippos",
}

UNISEX_NAMES = {"dani", "andrea", "αντρέα"}

FEMALE_ROLES = {
    "κυρία", "κυρια", "δεσποινίς", "γυναίκα", "κορίτσι", "κόρη", "μητέρα",
    "μαμά", "αδελφή", "αδερφή", "θεία", "γιαγιά", "νύφη",
    "δασκάλα", "καθηγήτρια", "μαθήτρια", "φοιτήτρια", "σερβιτόρα", "πωλήτρια",
    "νοσοκόμα", 
    "φίλη", "γειτόνισσα", "πελάτισσα", "διευθύντρια", 
    "μαγείρισσα", "κομμώτρια", "τουρίστρια", "αφηγήτρια",
    "kyria", "despinis", "gynaika", "koritsi", "kori", "mitera", "mama",
    "adelfi", "theia", "giagia", "daskala", "kathigitria", "mathitria",
    "foititria", "servitora", "politria", "nosokoma", "fili", "geitonissa",
    "pelatissa", "diefthyntria", "magirissa",
}

MALE_ROLES = {
    "κύριος", "κύριε", "κος", "άνδρας", "άντρας", "αγόρι",
    "γιος", "πατέρας", "μπαμπάς", "αδελφός", "αδερφός", "θείος", "παππούς",
    "γαμπρός", "δάσκαλος", "καθηγητής", "μαθητής", "φοιτητής",
    "σερβιτόρος", "πωλητής", "νοσοκόμος", "γιατρός", "δικηγόρος", "φίλος",
    "γείτονας", "πελάτης", "διευθυντής", "ξενοδόχος", "μάγειρας", "κομμωτής",
    "τουρίστας", "αφηγητής", "αστυνομικός", "ταξιτζής",
    "kyrios", "kyrie", "andras", "antras", "agori", "gios", "pateras",
    "babas", "mpampas", "adelfos", "theios", "pappous", "daskalos",
    "kathigitis", "mathitis", "foititis", "servitoros", "politis", "giatros",
    "dikigoros", "filos", "geitonas", "pelatis", "diefthyntis", "mageiras",
}

EPICENE = {
    "άτομο", "ατομο", "φωνή", "παιδί", "παιδι", 
    "a", "b", "c", "1", "2", "3", "voice", "student",
    "teacher", "atomo", "fwni", "paidi", "tourist",
}

ARTICLES = {"ο", "η", "το", "οι", "τα", "ένας", "μια", "μία", "ένα", "του",
            "της", "των", "τον", "την", "τους", "τις"}
ARTICLE_GENDER = {"η": "F", "την": "F", "της": "F", "μια": "F", "μία": "F",
                  "ο": "M", "τον": "M", "του": "M", "ένας": "M"}

TITLE_PATTERNS = (
    (r"\bκα\b|\bκυρία\b|\bκυρια\b|\bδεσποινίς\b|\bkyria\b|\bkiria\b", "F"),
    (r"\bκος\b|\bκύριος\b|\bκύριε\b|\bκυριος\b|\bkyrios\b|\bkirios\b", "M"),
)

# Greek feminine nouns end in -α, -η, -ια, -ού, -ω; masculine in -ος, -ας,
# -ης. Masculine -ος words that are actually feminine (η οδός) are rare.
_F_SUFFIX = ("τρια", "ισσα", "ούσα", "α", "η", "ω")
_M_SUFFIX = ("ος", "ας", "ης", "ους")
_NOT_PERSON = {"φωνή", "πόλη", "μέρα", "ώρα"}


def morph(word: str):
    """Guess from a Greek ending. Returns 'F', 'M' or None."""
    w = (word or "").lower()
    if len(w) < 4 or w in _NOT_PERSON:
        return None
    for suf in sorted(_F_SUFFIX, key=len, reverse=True):
        if w.endswith(suf) and (len(suf) > 1):
            return "F"
    for suf in _M_SUFFIX:
        if w.endswith(suf):
            return "M"
    return None


# Greek adjectives agree with the speaker: "είμαι κουρασμένη" (F) vs
# "είμαι κουρασμένος" (M).
SELF_GENDER_MARKERS = {
    "F": ["είμαι κουρασμένη", "είμαι χαρούμενη", "είμαι έτοιμη",
          "είμαι παντρεμένη", "είμαι ελληνίδα",
          "είμαι αγγλίδα", "είμαι φοιτήτρια", "είμαι δασκάλα",
          "είμαι ευχαριστημένη", "είμαι μόνη",
          "eimai kourasmeni", "eimai xaroumeni", "eimai ellinida"],
    "M": ["είμαι κουρασμένος", "είμαι χαρούμενος", "είμαι έτοιμος",
          "είμαι παντρεμένος", "είμαι έλληνας", "είμαι άγγλος",
          "είμαι φοιτητής", "είμαι δάσκαλος", "είμαι ευχαριστημένος",
          "είμαι μόνος", "eimai kourasmenos", "eimai xaroumenos"],
}

NON_SPEAKER_LABELS = {
    "σημείωση", "σημειώσεις", "λεξιλόγιο", "γραμματική", "μετάφραση",
    "παράδειγμα", "παραδείγματα", "άσκηση", "ασκήσεις", "απάντηση",
    "απαντήσεις", "διάλογος", "συνομιλία", "σκηνή", "αφηγητής", "αφηγήτρια",
    "περίληψη", "εισαγωγή", "προσοχή", "σημαντικό", "στόχοι", "πολιτισμός",
    "προφορά", "τίτλος", "επίπεδο", "θέμα", "πλαίσιο", "πηγή", "ήχος",
    "note", "notes", "vocabulary", "key vocabulary", "grammar", "translation",
    "example", "exercise", "answer", "answers", "key", "tip", "objective",
    "objectives", "learning objectives", "topic", "title", "level", "summary",
    "table", "dialogue", "conversation", "scene", "narrator", "context",
    "transliteration", "pronunciation", "el", "en", "english", "greek",
    "audio", "http", "https", "www",
}

SKIP_HEADINGS = [
    "grammar", "γραμματική",
    "vocabulary", "key vocabulary", "word list", "λεξιλόγιο",
    "exercise", "exercises", "άσκηση", "ασκήσεις",
    "answer key", "answers", "απαντήσεις", "λύσεις",
    "notes", "note", "σημείωση", "σημειώσεις",
    "culture", "πολιτισμός", "cultural note",
    "pronunciation", "προφορά", "transliteration",
    "learning objectives", "objectives", "στόχοι",
]

CONSOLIDATION_HEADINGS = {
    "putting it all together", "put it all together", "putting it together",
    "all together", "consolidation", "recap", "επανάληψη", "ανακεφαλαίωση",
    "όλα μαζί", "σύνοψη",
}

EDGE_LOCALES = ("el-",)
LOCALE_LABELS = {"el_GR": "Greece"}
ACCENTS = LOCALE_LABELS
ACCENT_LONG = {"el_GR": "Modern Greek (Greece)"}
DEFAULT_ACCENT = "el_GR"
PREFERRED_PAIRS = {
    "el_GR": {"M": "el-GR-NestorasNeural", "F": "el-GR-AthinaNeural"},
}
VARIANTS_NOTE = ("Modern Standard Greek (Demotic) only; edge-tts has one el-GR locale with a male and a female voice, and Cypriot Greek has no voice.")
