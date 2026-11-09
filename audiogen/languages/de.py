"""German language pack.

Two things make German different from the Romance packs:

* Gender is marked on the noun by a suffix that is nearly regular — the
  feminine `-in` (Lehrer/Lehrerin, Kellner/Kellnerin, Arzt/Ärztin) — so
  `morph()` is unusually reliable. The catch is that a pile of ordinary male
  first names also end in -in (Martin, Kevin, Robin, Konstantin), which is
  the same trap Italian sets with -a; they are listed explicitly.
* Course files address people as `Herr Schmidt` / `Frau Weber` far more often
  than they use a bare role noun, so the title rule carries most of the work.

"""

import re as _re

CODE, NAME, NATIVE = "de", "German", "Deutsch"
SAMPLE_TEXT = "Guten Tag! Ich heiße Lena. Wie geht es Ihnen heute?"
SAMPLE_SCENE = "Erster Kurstag: Lena trifft Jonas im Flur."

FEMALE_NAMES = {
    "lena", "anna", "julia", "sarah", "sara", "laura", "lisa", "marie",
    "maria", "sophie", "sofia", "sophia", "hannah", "hanna", "emma", "mia",
    "lea", "leah", "amelie", "clara", "klara", "charlotte", "johanna",
    "katharina", "katrin", "kathrin", "katja", "petra", "sabine", "susanne",
    "monika", "andrea", "claudia", "birgit", "brigitte", "ute", "ursula",
    "ulrike", "gabriele", "gaby", "heike", "ingrid", "irmgard", "renate",
    "helga", "gerda", "gisela", "erika", "elke", "elisabeth", "eva", "ella",
    "greta", "frieda", "hedwig", "hildegard", "ilse", "jutta", "karin",
    "kerstin", "leonie", "lieselotte", "lotte", "luise", "louisa", "luisa",
    "maja", "marion", "martina", "melanie", "nadine", "nicole", "nina",
    "ramona", "regina", "rita", "ruth", "silke", "silvia", "sonja", "steffi",
    "stefanie", "tanja", "tina", "vanessa", "verena", "wiebke", "annika",
    "antje", "beate", "bettina", "carla", "cornelia", "dagmar", "daniela",
    "doris", "franziska", "friederike", "heidi", "henrike", "iris", "jana",
    "janina", "jessica", "josefine", "juliane", "karla", "kira", "lara",
    "linda", "magdalena", "manuela", "margarete", "marlene", "mathilde",
    "michaela", "miriam", "paula", "pia", "rebecca", "rosa", "roswitha",
    "sandra", "saskia", "svenja", "theresa", "therese", "ulla", "waltraud",
    "amala", "klarissa", "seraphina", "leni", "vroni", "resi",
}

# German male first names ending in -in, -a or -e, which the -in feminine rule
# and the usual suffix guesses would otherwise get wrong. Listed explicitly
# for the same reason Italian lists Luca and Andrea.
MALE_NAMES = {
    # the -in trap
    "martin", "kevin", "robin", "armin", "erwin", "edwin", "konstantin",
    "valentin", "benjamin", "korbinian", "quentin", "augustin", "severin",
    "kilian", "killian", "florentin", "ruben", "alwin", "colin", "justin",
    # -a / -e endings
    "luca", "noah", "elia", "joshua", "nikita", "andrea_m", "uwe", "helge",
    "gerhardt", "ole", "arne", "kai", "eike", "sunny_m",
    # everyday German male names
    "jonas", "lukas", "leon", "paul", "felix", "maximilian", "max", "moritz",
    "tim", "tom", "thomas", "michael", "andreas", "peter", "klaus", "hans",
    "jürgen", "juergen", "wolfgang", "günter", "guenter", "günther", "helmut",
    "manfred", "dieter", "horst", "werner", "gerhard", "rolf", "rainer",
    "reiner", "bernd", "bernhard", "christian", "christoph", "stefan",
    "stephan", "matthias", "markus", "marcus", "frank", "ralf", "ralph",
    "sven", "sascha", "torsten", "thorsten", "carsten", "karsten", "jens",
    "jan", "jörg", "joerg", "kurt", "karl", "carl", "heinz", "heinrich",
    "friedrich", "fritz", "wilhelm", "ludwig", "otto", "rudolf", "walter",
    "gustav", "johann", "johannes", "josef", "joseph", "franz", "anton",
    "alexander", "sebastian", "daniel", "david", "philipp", "philip",
    "fabian", "julian", "simon", "niklas", "nico", "nick", "elias", "emil",
    "erik", "eric", "finn", "henry", "henrik", "jakob", "jacob", "joel",
    "jonathan", "leo", "levi", "linus", "louis", "luis", "marlon", "mats",
    "milan", "nils", "oskar", "oscar", "raphael", "samuel", "theo", "til",
    "till", "tobias", "vincent", "conrad", "konrad", "kasper", "kaspar",
    "florian", "dominik", "patrick", "roland", "detlef", "eberhard", "egon",
    "ernst", "gottfried", "hartmut", "herbert", "hubert", "joachim", "lothar",
    "norbert", "reinhard", "siegfried", "ulrich", "volker", "wilfried",
    # surnames that appear as bare speaker labels in these course files
    "schmidt", "müller", "mueller", "weber", "wagner", "becker", "hoffmann",
    "schulz", "koch", "richter", "klein", "wolf", "neumann", "schwarz",
    "zimmermann", "braun", "krüger", "krueger", "hofmann", "hartmann",
}

# Used for either gender in German, so morphology must not decide.
UNISEX_NAMES = {
    "alex", "chris", "kim", "toni", "tony", "sasha", "eli", "noel", "mika",
    "luca_u", "andrea_u", "sam", "max_u", "nikita_u", "charlie",
}

# -in is the feminine marker; these are the words a course file actually uses.
FEMALE_ROLES = {
    "frau", "fräulein", "dame", "mädchen", "tochter", "mutter", "mama",
    "mutti", "schwester", "tante", "oma", "großmutter", "grossmutter",
    "ehefrau", "gattin", "freundin", "nachbarin", "kollegin", "chefin",
    "lehrerin", "lehrer_f", "schülerin", "studentin", "professorin",
    "dozentin", "ärztin", "aerztin", "doktorin", "krankenschwester",
    "pflegerin", "kellnerin", "bedienung", "verkäuferin", "verkaeuferin",
    "kassiererin", "verkaufsberaterin", "beraterin", "angestellte",
    "mitarbeiterin", "sekretärin", "sekretaerin", "direktorin", "leiterin",
    "managerin", "ingenieurin", "anwältin", "anwaeltin", "rechtsanwältin",
    "journalistin", "autorin", "bäckerin", "baeckerin", "köchin", "koechin",
    "friseurin", "friseuse", "apothekerin", "polizistin", "fahrerin",
    "schaffnerin", "empfangsdame", "rezeptionistin", "wirtin", "besitzerin",
    "vermieterin", "mieterin", "kundin", "besucherin", "touristin",
    "reiseleiterin", "sprecherin", "erzählerin", "erzaehlerin", "moderatorin",
    "praktikantin", "auszubildende_f", "azubine", "briefträgerin",
    "briefträgerin", "bankangestellte", "beamtin", "trainerin",
}
MALE_ROLES = {
    "herr", "mann", "junge", "bursche", "sohn", "vater", "papa", "vati",
    "bruder", "onkel", "opa", "großvater", "grossvater", "ehemann", "gatte",
    "freund", "nachbar", "kollege", "chef", "lehrer", "schüler", "schueler",
    "student", "professor", "dozent", "arzt", "doktor", "krankenpfleger",
    "pfleger", "kellner", "verkäufer", "verkaeufer", "kassierer",
    "verkaufsberater", "berater", "angestellter", "mitarbeiter", "sekretär",
    "sekretaer", "direktor", "leiter", "manager", "ingenieur", "anwalt",
    "rechtsanwalt", "journalist", "autor", "bäcker", "baecker", "koch",
    "friseur", "apotheker", "polizist", "fahrer", "schaffner", "portier",
    "rezeptionist", "wirt", "besitzer", "vermieter", "mieter", "kunde",
    "besucher", "tourist", "reiseleiter", "sprecher", "erzähler", "erzaehler",
    "moderator", "praktikant", "briefträger", "brieftraeger", "beamter",
    "trainer", "schauspieler", "verkehrspolizist", "busfahrer", "taxifahrer",
}

# Same form whatever the speaker's gender, or genuinely uninformative.
EPICENE = {
    "gast", "person", "leute", "kind", "baby", "publikum", "stimme",
    "jemand", "gruppe", "klasse", "kurs", "teilnehmer", "fahrgast",
    "passagier", "patient", "gegenüber", "gegenueber", "ansager",
    "durchsage", "lautsprecher", "automat", "telefonstimme",
    "a", "b", "c", "d", "1", "2", "3", "4", "sprecher a", "sprecher b",
}

# der/die/das and the case forms a speaker label can carry.
ARTICLES = {"der", "die", "das", "den", "dem", "des", "ein", "eine", "einen",
            "einem", "eines", "einer", "mein", "meine", "unser", "unsere",
            "herr", "frau"}
# "die" is also the plural article for every gender, but a speaker label is
# singular, so reading it as feminine is safe here.
ARTICLE_GENDER = {"die": "F", "eine": "F", "einer": "F",
                  "der": "M", "den": "M", "dem": "M", "ein": "M",
                  "einen": "M", "einem": "M"}

# Matched against the raw label. Herr/Frau decide outright: they are courtesy
# titles, not role nouns, and a course file uses them constantly.
TITLE_PATTERNS = (
    (r"\bfrau\b|\bfr\.\s|\bfräulein\b|\bfraeulein\b"
     r"|\bfrau\s+dr\.?|\bfrau\s+prof\.?", "F"),
    (r"\bherr\b|\bherrn\b|\bhr\.\s|\bherr\s+dr\.?|\bherr\s+prof\.?", "M"),
)

# -in is the reliable one. The rest are weak and only consulted after the
# role and name lists have had their say.
_F_SUFFIX = ("erin", "orin", "ärztin", "aerztin", "istin", "antin", "entin",
             "eurin", "ikerin", "login", "arin", "urin", "in",
             "frau", "schwester", "tochter", "dame", "mädchen", "maedchen")
_M_SUFFIX = ("mann", "vater", "sohn", "bruder", "junge", "arzt", "eur",
             "ist", "ant", "ent", "iker", "loge", "or", "ling", "er")

# Words that end in -in without being feminine, or in -er without being a
# person: the suffix rules must not fire on these.
_NOT_FEMININE_IN = {
    "berlin", "wien", "termin", "kamin", "benzin", "rosin", "min", "wein",
    "sohn", "kusin", "delfin", "gewinn", "beginn", "kinn", "sinn", "zwilling",
}
# -er, -or, -ent and -ant are also the endings of a great many ordinary
# nouns. A speaker label is a person, so the risk is small, but these are the
# words that actually turn up near dialogue and they must not be read as one.
_NOT_PERSON_ER = {
    "wetter", "zimmer", "fenster", "wasser", "zucker", "butter", "teller",
    "messer", "computer", "koffer", "kalender", "kilometer", "meter", "liter",
    "theater", "papier", "eier", "bier", "tier", "feuer", "ufer", "ober",
    "immer", "wieder", "weiter", "oder", "aber", "sehr", "mehr", "sommer",
    "winter", "morgen", "nummer", "muster", "silber", "pflaster", "pulver",
    # -or / -ent / -ant / -ist that are not people
    "motor", "tor", "humor", "korridor", "traktor", "chor", "dekor", "likör",
    "likoer", "moment", "prozent", "restaurant", "elefant", "instrument",
    "talent", "zement", "dokument", "prospekt", "abonnement", "argument",
    "parlament", "monument", "kontinent", "präsent", "praesent", "list",
    "obst", "post", "wurst", "durst", "frost", "kunst", "angst",
}


def morph(word: str):
    """Guess a German role noun's gender from its ending.

    `-in` is close to a rule rather than a tendency, so it is trusted; `-er`
    is only a hint (it is also the ending of half the neuter nouns in the
    language), and both are checked against a short exclusion list. Words
    ending in -e are left undecided: Kollege is masculine, Tante feminine.
    """
    w = (word or "").strip().lower()
    if len(w) < 4:
        return None
    if w in _NOT_FEMININE_IN or w in _NOT_PERSON_ER:
        return None
    for suf in sorted(_F_SUFFIX, key=len, reverse=True):
        if w.endswith(suf):
            # -in on a two-syllable stem is a person; on a place or an object
            # it is a coincidence, which the exclusion list covers
            return "F"
    for suf in sorted(_M_SUFFIX, key=len, reverse=True):
        if w.endswith(suf):
            return "M"
    return None


# --- Gender from a speaker's own words.
#
# German participles do not agree ("ich bin gekommen" says nothing), so the
# Romance trick of reading past tenses does not transfer. What German does
# give is the predicate noun: "ich bin Lehrerin" is unambiguous, and the -in
# regex generalises it to any profession the lists do not happen to hold.
# A first-person statement of what the speaker is, anywhere in one sentence:
# "ich bin Lehrerin", "ich bin die neue Kollegin", "ich arbeite als Kellner".
# The bounded gap keeps it inside the sentence, and the lookahead drops
# negated statements ("ich bin nicht der Lehrer" says the opposite).
# The "re:" prefix is what marks a marker as a pattern rather than a phrase.
# The gap is kept short on purpose: long enough for "die neue " or "auch ",
# short enough that a second person named later in the same sentence is not
# read as the speaker.
_SELF = (r"re:\b[Ii]ch (?:bin|arbeite als)\b"
         r"(?![^.!?]{0,18}?\b(?:nicht|kein|keine|keiner)\b)"
         r"[^.!?]{0,18}?\b%s\b")


SELF_GENDER_MARKERS = {
    # Plain words, matched case-insensitively. Professions whose ending the
    # regexes below cannot generalise from are simply listed.
    "F": ["ich bin deutsche", "ich bin österreicherin", "ich bin schweizerin",
          "ich bin engländerin", "ich bin englaenderin",
          "ich bin frau", "ich bin eine frau", "als frau",
          "ich bin hausfrau", "ich bin die neue",
          # Any profession or nationality in -in. German capitalises nouns,
          # so requiring a capital is what separates "ich bin Lehrerin" from
          # the adjective in "ich bin müde" - and the long endings keep male
          # first names such as Martin and Konstantin out of it.
          _SELF % (r"[A-ZÄÖÜ][A-Za-zÄÖÜäöüß]*"
                   r"(?:erin|orin|istin|antin|entin|eurin|ikerin|rztin"
                   r"|aerztin|login|urin|arin)"),
          ],
    "M": ["ich bin deutscher", "ich bin österreicher", "ich bin oesterreicher",
          "ich bin schweizer", "ich bin engländer", "ich bin englaender",
          "ich bin herr", "ich bin ein mann", "als mann", "ich bin der neue",
          # professions with no generalisable ending
          "ich bin koch", "ich bin arzt", "ich bin anwalt", "ich bin azubi",
          "ich bin soldat", "ich bin pilot", "ich bin architekt",
          "ich bin kaufmann", "ich bin hausmann", "ich bin rentner",
          # Any profession in a masculine ending, same capitalisation rule,
          # explicitly not the -in forms.
          # the -er guard: a handful of women's names end that way too
          _SELF % (r"(?!(?:Esther|Ester|Jennifer|Heather|Walter_f)\b)"
                   r"[A-ZÄÖÜ][A-Za-zÄÖÜäöüß]*"
                   r"(?:eur|arzt|iker|loge|ist|ant|ent|or|er)"),
          ],
}

NON_SPEAKER_LABELS = {
    "notiz", "notizen", "hinweis", "hinweise", "anmerkung", "anmerkungen",
    "vokabeln", "wortschatz", "wörter", "woerter", "wortliste", "grammatik",
    "übersetzung", "uebersetzung", "beispiel", "beispiele", "übung", "uebung",
    "übungen", "uebungen", "aufgabe", "aufgaben", "antwort", "antworten",
    "lösung", "loesung", "lösungen", "loesungen", "schlüssel", "schluessel",
    "tipp", "tipps", "ziel", "ziele", "lernziele", "thema", "titel", "stufe",
    "niveau", "dialog", "gespräch", "gespraech", "szene", "akt", "kontext",
    "situation", "zusammenfassung", "einleitung", "achtung", "wichtig",
    "quelle", "autor", "datum", "aussprache", "kultur", "landeskunde",
    "redemittel", "phonetik", "merke", "info", "tabelle", "abbildung",
    "de", "en", "deutsch", "englisch", "audio", "bild", "siehe",
    "http", "https", "www",
    # these course files use English headings throughout
    "note", "notes", "vocabulary", "key vocabulary", "grammar", "translation",
    "example", "exercise", "answer", "answers", "key", "tip", "objective",
    "objectives", "learning objectives", "topic", "title", "level",
    "summary", "table", "dialogue", "conversation", "language notes",
    "pronunciation", "culture",
    # bold lead-in labels the CULP scaffold files put before each topic's
    # scenario paragraph and unit-level grammar note, and the citation line
    # at the top of the file -- "**Scenario:** ..." has the same shape as a
    # real "**Ana:** ..." speaker line, so it must be excluded by name.
    "scenario", "grammar focus", "source", "register", "context",
}

SKIP_HEADINGS = [
    "grammar", "grammatik",
    "vocabulary", "key vocabulary", "vokabeln", "wortschatz", "wortliste",
    "word list", "wörter", "woerter",
    "exercise", "exercises", "übung", "uebung", "übungen", "uebungen",
    "aufgabe", "aufgaben",
    "answer key", "answers", "lösungen", "loesungen", "antworten",
    "notes", "note", "language notes", "anmerkungen", "hinweise",
    "culture", "kultur", "landeskunde", "cultural note",
    "pronunciation", "aussprache", "phonetik",
    "learning objectives", "objectives", "lernziele", "ziele",
    "redemittel", "phrasen",
    "voices used in this unit",
]

CONSOLIDATION_HEADINGS = {
    "putting it all together", "put it all together", "putting it together",
    "all together", "alles zusammen", "alles zusammensetzen",
    "zusammenfassung des kapitels", "wiederholung", "rückblick", "rueckblick",
    "consolidation", "recap", "alles auf einmal",
}

ACCENT_LONG = {
    "de_DE": "German (Germany)",
    "de_AT": "Austrian German",
    "de_CH": "Swiss Standard German",
}

_AT_WORDS = ["grüß gott", "gruess gott", "servus", "baba", "jause", "semmel",
             "erdäpfel", "erdaepfel", "paradeiser", "sackerl", "heuer",
             "melange", "häferl", "haeferl", "topfen", "obers", "karfiol",
             "fisolen", "schlagobers", "greißler", "greissler", "trafik",
             "bankomat", "matura", "jänner", "jaenner", "feber", "spital",
             "pickerl", "häusl", "eh klar", "leiwand", "oida"]
_CH_WORDS = ["grüezi", "gruezi", "grüessech", "hoi", "velo", "znüni", "znueni",
             "zvieri", "rüebli", "rueebli", "guetzli", "parkieren", "natel",
             "kehricht", "billett", "tram", "occasion", "morgenessen",
             "zmorge", "coiffeur", "glace", "poulet", "peperoni", "cervelat",
             "estriche", "putzfrau", "kondukteur", "perron", "töff", "toeff"]
_DE_WORDS = ["guten tag", "tschüss", "tschüs", "tschuess", "brötchen",
             "broetchen", "fahrrad", "kartoffeln", "tüte", "tuete",
             "januar", "februar", "krankenhaus", "geldautomat", "abitur",
             "quark", "sahne", "blumenkohl", "grüne bohnen", "kasse",
             "moin", "hallo", "auf wiedersehen", "guten morgen",
             "straßenbahn", "strassenbahn", "handy", "fahrkarte", "bäckerei"]


def _count(text, words):
    n, hits = 0, []
    for w in words:
        c = text.count(w)
        if c:
            n += c
            hits.append(w)
    return n, hits


def detect_accent(text: str) -> dict:
    """Guess which German-speaking country a course file is written for.

    Swiss Standard German also drops ß entirely (ss everywhere), which is a
    structural signal rather than a lexical one, so a file with plenty of
    German-standard vocabulary and no ß at all still leans Swiss - but only
    enough to break a tie, never on its own.
    """
    low = (text or "").lower()
    scores, hits = {}, {}
    for key, words in (("de_AT", _AT_WORDS), ("de_CH", _CH_WORDS),
                       ("de_DE", _DE_WORDS)):
        scores[key], hits[key] = _count(low, words)

    # the ß test, as a tie-breaker only
    ss_words = len(_re.findall(r"[a-zäöü]{2,}ss[a-zäöü]", low))
    if "ß" not in low and ss_words >= 4:
        scores["de_CH"] += 1
        hits["de_CH"] = (hits["de_CH"] + ["no ß, ss throughout"])[:8]

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


# --- Abbreviations. Course files are full of "z. B." and "usw.", and no
# engine reads them as words: some engines spell the letters out and the neural
# voices are inconsistent. Expanded before synthesis and shown in the UI so
# what will be spoken is visible.
SPEECH_LABEL = "as spoken"

_ABBREV = [
    (r"\bz\.\s*B\.", "zum Beispiel"),
    (r"\bz\.\s*T\.", "zum Teil"),
    (r"\bu\.\s*a\.", "unter anderem"),
    (r"\bu\.\s*s\.\s*w\.", "und so weiter"),
    (r"\busw\.", "und so weiter"),
    (r"\bbzw\.", "beziehungsweise"),
    (r"\bggf\.", "gegebenenfalls"),
    (r"\bevtl\.", "eventuell"),
    (r"\bca\.", "circa"),
    (r"\bd\.\s*h\.", "das heißt"),
    (r"\bo\.\s*ä\.", "oder ähnliches"),
    (r"\binkl\.", "inklusive"),
    (r"\bexkl\.", "exklusive"),
    (r"\bNr\.", "Nummer"),
    (r"\bnr\.", "Nummer"),
    (r"\bAbb\.", "Abbildung"),
    (r"\bTel\.", "Telefon"),
    # German writes the street suffix onto the compound ("Hauptstr."), where
    # a leading word boundary never matches, as well as standing alone
    (r"([A-Za-zÄÖÜäöüß]{2,})str\.", r"\1straße"),
    (r"\bStr\.", "Straße"),
    (r"\bMio\.", "Millionen"),
    (r"\bMrd\.", "Milliarden"),
    (r"\bJhd\.", "Jahrhundert"),
    (r"\bmind\.", "mindestens"),
    (r"\bmax\.", "maximal"),
    (r"\bvgl\.", "vergleiche"),
    (r"\bHr\.\s", "Herr "),
    (r"\bFr\.\s", "Frau "),
    (r"\bDr\.\s", "Doktor "),
    (r"\bProf\.\s", "Professor "),
    (r"\bEUR\b", "Euro"),
    (r"€", " Euro"),
    (r"%", " Prozent"),
    (r"&", " und "),
    (r"\bkm/h\b", "Kilometer pro Stunde"),
]
_ABBREV = [(_re.compile(rx), rep) for rx, rep in _ABBREV]
_WS = _re.compile(r"\s+")


def SPEECH_TRANSFORM(text: str):
    """Expand the abbreviations a German course file uses in writing.

    Returns (spoken_text, unmapped). Nothing is ever guessed at, so the second
    element is always empty - it exists because the Chinese pack needs it.
    """
    t = text or ""
    for rx, rep in _ABBREV:
        t = rx.sub(rep, t)
    return _WS.sub(" ", t).strip(), []


# --- Voice grouping. The voice catalogue itself comes from a live edge-tts
# snapshot; the pack only says which locales belong to the language, how to
# label them, and which voices are preferred as the M/F pair of each locale.
EDGE_LOCALES = ('de-',)
LOCALE_LABELS = {
    'de_DE': 'Germany',
    'de_AT': 'Austria',
    'de_CH': 'Switzerland',
}
ACCENTS = LOCALE_LABELS
DEFAULT_ACCENT = 'de_DE'
PREFERRED_PAIRS = {
    'de_DE': {'M': 'de-DE-ConradNeural', 'F': 'de-DE-KatjaNeural'},
    'de_AT': {'M': 'de-AT-JonasNeural', 'F': 'de-AT-IngridNeural'},
    'de_CH': {'M': 'de-CH-JanNeural', 'F': 'de-CH-LeniNeural'},
}
VARIANTS_NOTE = 'Standard German is offered with Germany, Austria and Switzerland voices; the Swiss voice speaks Standard German with a Swiss accent, not Swiss German dialect.'
