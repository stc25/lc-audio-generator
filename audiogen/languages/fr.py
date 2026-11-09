"""French language pack."""

CODE, NAME, NATIVE = "fr", "French", "Français"
SAMPLE_TEXT = "Bonjour ! Je m'appelle Camille. Comment allez-vous aujourd'hui ?"
SAMPLE_SCENE = "Premier jour de cours : Léa rencontre Nicolas dans le couloir."

FEMALE_NAMES = {
    "léa", "lea", "marie", "sophie", "julie", "emma", "chloé", "manon", "léna",
    "sarah", "laura", "clara", "jade", "louise", "alice", "lina", "rose",
    "anna", "inès", "lucie", "zoé", "juliette", "agathe", "charlotte", "eva",
    "romane", "ambre", "jeanne", "margaux", "océane", "pauline", "mathilde",
    "élise", "elise", "céline", "nathalie", "isabelle", "sylvie", "martine",
    "monique", "françoise", "catherine", "christine", "brigitte", "véronique",
    "valérie", "virginie", "aurélie", "delphine", "sandrine", "karine",
    "stéphanie", "amélie", "hélène", "denise", "vivienne", "éloïse", "eloise",
    "nicole", "michèle", "annie", "danielle", "jacqueline", "chantal",
    "corinne", "florence", "laurence", "patricia", "sabine", "solange",
    "yvette", "adèle", "capucine", "elsa", "fanny", "gabrielle", "iris",
    "maëlys", "noémie", "salomé", "victoire", "colette", "simone", "girard",
}

MALE_NAMES = {
    "nicolas", "thomas", "hugo", "lucas", "léo", "leo", "gabriel", "raphaël",
    "arthur", "louis", "jules", "adam", "maël", "tom", "sacha", "noah",
    "ethan", "mathis", "enzo", "nathan", "théo", "antoine", "pierre", "jean",
    "michel", "philippe", "alain", "patrick", "bernard", "daniel",
    "christophe", "laurent", "olivier", "sébastien", "julien", "david",
    "frédéric", "stéphane", "pascal", "éric", "eric", "franck", "gilles",
    "rémy", "remy", "henri", "guillaume", "maxime", "vincent", "benoît",
    "benoit", "damien", "cédric", "cedric", "fabien", "romain", "quentin",
    "clément", "clement", "baptiste", "mathieu", "matthieu",
    "grégoire", "jérôme", "jérémy", "loïc", "marc", "paul", "richard",
    "robert", "roger", "serge", "yves", "xavier", "bruno", "didier", "gérard",
    "joseph", "lionel", "ludovic", "victor", "aurélien", "dubois",
}

# Given names used for either gender; alternation decides and the UI flags
# them as low confidence.
UNISEX_NAMES = {
    "camille", "dominique", "claude", "alix", "ange", "sasha", "charlie",
    "lou", "andrea", "maxence", "swann", "noa", "eden", "louison", "morgan",
}

FEMALE_ROLES = {
    "madame", "mme", "mademoiselle", "mlle", "femme", "fille", "mère", "maman",
    "sœur", "soeur", "tante", "grand-mère", "épouse", "serveuse", "vendeuse",
    "employée", "cliente", "pharmacienne", "boulangère", "coiffeuse",
    "caissière", "infirmière", "professeure", "institutrice", "maîtresse",
    "étudiante", "directrice", "patronne", "voisine", "amie", "copine",
    "passante", "dame", "doctoresse", "avocate", "factrice", "hôtesse",
    "cuisinière", "marchande", "commerçante", "acheteuse", "chanteuse",
    "danseuse", "conductrice", "spectatrice", "lectrice", "gardienne",
    "policière", "voix féminine", "narratrice",
}

MALE_ROLES = {
    "monsieur", "messieurs", "homme", "garçon", "fils", "père", "papa",
    "frère", "oncle", "grand-père", "époux", "mari", "serveur", "vendeur",
    "employé", "client", "pharmacien", "boulanger", "coiffeur", "caissier",
    "infirmier", "professeur", "instituteur", "étudiant", "directeur",
    "patron", "voisin", "ami", "copain", "passant", "docteur", "avocat",
    "facteur", "cuisinier", "marchand", "commerçant", "acheteur", "chanteur",
    "danseur", "conducteur", "spectateur", "lecteur", "gardien", "policier",
    "voix masculine", "narrateur", "gars",
}

# Identical in both genders: never guess from morphology here.
EPICENE = {
    "réceptionniste", "receptionniste", "secrétaire", "touriste", "élève",
    "eleve", "collègue", "collegue", "colocataire", "journaliste", "dentiste",
    "artiste", "pianiste", "guide", "médecin", "medecin", "interprète",
    "libraire", "fonctionnaire", "partenaire", "locataire", "stagiaire",
    "camarade", "enfant", "personne", "adulte", "automobiliste", "cycliste",
    "a", "b", "c", "1", "2", "3", "voix", "interlocuteur",
}

ARTICLES = {"le", "la", "les", "l", "un", "une", "des", "du", "de", "d"}
ARTICLE_GENDER = {"la": "F", "une": "F", "le": "M", "un": "M"}

TITLE_PATTERNS = (
    (r"\bmme\b|\bmadame\b|\bmlle\b|\bmademoiselle\b", "F"),
    (r"\bm\.\s|\bmonsieur\b|\bmr\b", "M"),
)

# Longest suffix wins, so "-euse" beats a bare "-e".
_F_SUFFIX = ("euse", "trice", "ienne", "ière", "iere", "onne", "esse", "ette",
             "elle", "ée", "ee", "ande", "aine", "ine")
_M_SUFFIX = ("teur", "eur", "ien", "ier", "ant", "and", "ard", "eau", "on",
             "in", "is", "ot", "ou")


def morph(word: str):
    """Guess from a French suffix. Returns 'F', 'M' or None."""
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
    "note", "notes", "remarque", "remarques", "vocabulaire", "lexique",
    "grammaire", "traduction", "exemple", "exemples", "exercice", "exercices",
    "réponse", "réponses", "corrigé", "astuce", "conseil", "objectif",
    "objectifs", "thème", "titre", "niveau", "dialogue", "conversation",
    "scène", "acte", "contexte", "situation", "résumé", "introduction",
    "attention", "important", "source", "auteur", "date", "clé",
    "prononciation", "culture", "en", "fr", "anglais", "français", "audio",
    "image", "figure", "tableau", "voir", "http", "https", "www",
    # these bilingual course files use English headings throughout
    "vocabulary", "key vocabulary", "grammar", "grammar focus", "translation",
    "example", "exercise", "answer", "answers", "key", "tip", "objective",
    "objectives", "learning objectives", "topic", "title", "level",
    "summary", "table", "scenario",
    "vocabulary and useful expressions",
}

SKIP_HEADINGS = [
    "grammar", "grammaire",
    "vocabulary", "key vocabulary", "vocabulaire", "lexique", "word list",
    "exercise", "exercises", "exercice", "exercices",
    "answer key", "answers", "corrigé", "corrige", "solutions",
    "notes", "note", "remarque", "remarques",
    "culture", "note culturelle", "civilisation",
    "pronunciation", "prononciation",
    "learning objectives", "objectifs", "objectifs d'apprentissage",
]

CONSOLIDATION_HEADINGS = {
    "putting it all together", "put it all together", "putting it together",
    "all together", "on recapitule", "recapitulatif", "bilan", "synthese",
    "mise en pratique", "consolidation", "recap",
}


SELF_GENDER_MARKERS: dict = {}    # no speaker-agreement clues defined for this language

# --- Voice grouping. The voice catalogue itself comes from a live edge-tts
# snapshot; the pack only says which locales belong to the language, how to
# label them, and which voices are preferred as the M/F pair of each locale.
EDGE_LOCALES = ('fr-',)
LOCALE_LABELS = {
    'fr_FR': 'France',
    'fr_CA': 'Canada (Québec)',
    'fr_BE': 'Belgium',
    'fr_CH': 'Switzerland',
}
ACCENTS = LOCALE_LABELS
DEFAULT_ACCENT = 'fr_FR'
PREFERRED_PAIRS = {
    'fr_FR': {'M': 'fr-FR-HenriNeural', 'F': 'fr-FR-DeniseNeural'},
    'fr_CA': {'M': 'fr-CA-JeanNeural', 'F': 'fr-CA-SylvieNeural'},
    'fr_BE': {'M': 'fr-BE-GerardNeural', 'F': 'fr-BE-CharlineNeural'},
    'fr_CH': {'M': 'fr-CH-FabriceNeural', 'F': 'fr-CH-ArianeNeural'},
}
VARIANTS_NOTE = 'Metropolitan French is the default, with Canadian (Québec), Belgian and Swiss accent voices available.'
