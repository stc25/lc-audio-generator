"""Italian language pack."""

CODE, NAME, NATIVE = "it", "Italian", "Italiano"
SAMPLE_TEXT = "Buongiorno! Mi chiamo Giulia. Come sta oggi?"
SAMPLE_SCENE = "Primo giorno di corso: Giulia incontra Marco in corridoio."

FEMALE_NAMES = {
    "giulia", "sara", "chiara", "laura", "sofia", "francesca", "alessia",
    "martina", "giorgia", "elena", "anna", "maria", "valentina", "federica",
    "silvia", "elisa", "camilla", "beatrice", "arianna", "aurora", "ginevra",
    "emma", "greta", "alice", "benedetta", "carlotta", "gaia", "ilaria",
    "irene", "isabella", "elsa", "paola", "roberta", "simona", "cristina",
    "monica", "barbara", "daniela", "antonella", "angela", "teresa", "rosa",
    "lucia", "marta", "michela", "serena", "stefania", "veronica", "viola",
    "bianca", "caterina", "claudia", "cecilia", "diana", "eleonora", "fiamma",
    "fabiola", "gioia", "imelda", "irma", "letizia", "linda", "lorena",
    "manuela", "margherita", "matilde", "nicoletta", "noemi", "ornella",
    "palmira", "patrizia", "pierina", "rita", "sabrina", "sandra", "stella",
    "valeria", "vittoria", "giovanna", "carla", "franca", "luisa", "gabriella",
}

# Italian male names that END IN -a or -e and so defeat the usual morphology.
# These must be listed explicitly or Luca, Andrea and Nicola come out female.
MALE_NAMES = {
    "marco", "luca", "davide", "andrea", "matteo", "francesco", "alessandro",
    "lorenzo", "riccardo", "giuseppe", "antonio", "giovanni", "paolo",
    "roberto", "stefano", "mario", "luigi", "angelo", "vincenzo", "pietro",
    "salvatore", "carlo", "franco", "domenico", "bruno", "gianni", "nicola",
    "mattia", "elia", "simone", "gabriele", "daniele", "emanuele", "michele",
    "raffaele", "samuele", "tommaso", "filippo", "federico", "edoardo",
    "leonardo", "diego", "enrico", "fabio", "claudio", "massimo", "sergio",
    "dario", "alberto", "umberto", "giacomo", "cesare", "benigno", "calimero",
    "cataldo", "lisandro", "rinaldo", "aldo", "cosimo", "dante", "ettore",
    "fulvio", "gaetano", "gianluca", "gino", "guido", "ivano", "lino",
    "manuele", "nino", "oreste", "osvaldo", "pasquale", "renzo", "rocco",
    "silvio", "tiziano", "valerio", "walter", "bianchi", "rossi", "marchetti",
}

# Used for either gender in Italian.
UNISEX_NAMES = {"andrea_f", "celeste", "flavia_m", "loris", "amedeo_f"}

FEMALE_ROLES = {
    "signora", "signorina", "sig.ra", "sigra", "signore_f", "donna", "ragazza",
    "figlia", "madre", "mamma", "sorella", "zia", "nonna", "moglie", "sposa",
    "cameriera", "venditrice", "commessa", "impiegata", "infermiera",
    "professoressa", "ssa", "studentessa", "maestra", "direttrice",
    "dottoressa", "cassiera", "panettiera", "parrucchiera", "cuoca", "vicina",
    "amica", "coinquilina", "ragioniera", "operaia", "contadina", "cliente_f",
    "voce femminile", "narratrice", "insegnante_f", "impiegatta",
}

MALE_ROLES = {
    "signore", "signor", "sig", "uomo", "ragazzo", "figlio", "padre", "papà",
    "papa", "fratello", "zio", "nonno", "marito", "sposo", "cameriere",
    "venditore", "commesso", "impiegato", "infermiere", "professore", "prof",
    "studente", "maestro", "direttore", "dottore", "dott", "cassiere",
    "panettiere", "parrucchiere", "cuoco", "vicino", "amico", "coinquilino",
    "operaio", "contadino", "voce maschile", "narratore", "ingegnere",
}

# Same form for both genders: never guess from morphology.
EPICENE = {
    "cliente", "farmacista", "insegnante", "receptionist", "collega",
    "giornalista", "dentista", "artista", "pianista", "turista", "autista",
    "barista", "regista", "musicista", "nipote", "parente", "cantante",
    "studente_e", "custode", "consorte", "agente", "presidente", "cliente",
    "persona", "gente", "giovane", "abitante", "passante", "guida", "voce",
    "a", "b", "c", "1", "2", "3", "interlocutore",
}

ARTICLES = {"il", "lo", "la", "l", "i", "gli", "le", "un", "uno", "una",
            "del", "della", "di"}
ARTICLE_GENDER = {"la": "F", "una": "F", "il": "M", "lo": "M", "un": "M",
                  "uno": "M"}

# Checked against the raw label, so "Prof.ssa" is caught before the bare
# token "prof" can be read as masculine.
TITLE_PATTERNS = (
    (r"prof\.?\s*ssa|dott\.?\s*ssa|sig\.?\s*ra|sig\.?\s*na|signorina", "F"),
    (r"\bprof\.|\bdott\.|\bsig\.|\bsignor\b(?!a)", "M"),
)

_F_SUFFIX = ("essa", "trice", "ina", "ella", "etta", "ssa", "zione", "a")
_M_SUFFIX = ("ore", "iere", "aio", "one", "tore", "ino", "etto", "o")


def morph(word: str):
    """Guess from an Italian suffix. Returns 'F', 'M' or None.

    Words ending in -e are deliberately left undecided: cameriere is male,
    insegnante is either, and there is no reliable rule."""
    w = (word or "").lower()
    if len(w) < 4:
        return None
    for suf in sorted(_F_SUFFIX, key=len, reverse=True):
        if w.endswith(suf):
            return "F"
    for suf in sorted(_M_SUFFIX, key=len, reverse=True):
        if w.endswith(suf):
            return "M"
    return None


NON_SPEAKER_LABELS = {
    "nota", "note", "vocabolario", "lessico", "grammatica", "traduzione",
    "esempio", "esempi", "esercizio", "esercizi", "risposta", "risposte",
    "soluzioni", "chiave", "consiglio", "obiettivo", "obiettivi", "tema",
    "titolo", "livello", "dialogo", "conversazione", "scena", "atto",
    "contesto", "situazione", "riassunto", "introduzione", "attenzione",
    "importante", "fonte", "source", "autore", "data", "pronuncia", "cultura",
    "it", "en", "inglese", "italiano", "audio", "immagine", "figura",
    "tabella", "vedi", "http", "https", "www",
    # these bilingual course files use English headings throughout
    "vocabulary", "key vocabulary", "grammar", "translation", "example",
    "exercise", "answer", "answers", "key", "tip", "objective", "objectives",
    "learning objectives", "topic", "title", "level", "summary", "table",
    "note", "notes", "dialogue", "conversation", "grammar focus",
}

SKIP_HEADINGS = [
    "grammar", "grammatica",
    "vocabulary", "key vocabulary", "vocabolario", "lessico", "word list",
    "exercise", "exercises", "esercizio", "esercizi",
    "answer key", "answers", "risposte", "soluzioni",
    "notes", "note", "nota",
    # Do not skip the broad word "culture": it is also used in legitimate
    # course topics such as "Italian culture and national identity".
    "nota culturale",
    "pronunciation", "pronuncia",
    "learning objectives", "obiettivi", "obiettivi di apprendimento",
]

CONSOLIDATION_HEADINGS = {
    "putting it all together", "put it all together", "putting it together",
    "all together", "mettiamo tutto insieme", "tutto insieme", "riepilogo",
    "ricapitoliamo", "sintesi", "consolidation", "recap",
}


SELF_GENDER_MARKERS: dict = {}    # no speaker-agreement clues defined for this language

# --- Voice grouping. The voice catalogue itself comes from a live edge-tts
# snapshot; the pack only says which locales belong to the language, how to
# label them, and which voices are preferred as the M/F pair of each locale.
EDGE_LOCALES = ('it-',)
LOCALE_LABELS = {
    'it_IT': 'Italy',
}
ACCENTS = LOCALE_LABELS
DEFAULT_ACCENT = 'it_IT'
PREFERRED_PAIRS = {
    'it_IT': {'M': 'it-IT-DiegoNeural', 'F': 'it-IT-ElsaNeural'},
}
VARIANTS_NOTE = 'Standard Italian only; edge-tts has one Italian locale (it-IT) with male and female voices, no regional accents.'
