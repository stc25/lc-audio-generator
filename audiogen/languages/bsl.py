"""British Sign Language pack (English voice-over).

BSL is a signed language and has no audio form, so it cannot be synthesised.
This pack exists so BSL course material, which is usually written English
(translations, instructions, dialogue scripts, gloss notes), can be given an
English voice-over. Gloss-only material (capitalised glosses, handshape
notation) is not meaningful to read aloud and its headings are skipped.
"""

import re as _re

CODE, NAME, NATIVE = "bsl", "British Sign Language (English voice-over)", "BSL"
SAMPLE_TEXT = "Hello! My name is Emma. I am learning British Sign Language."
SAMPLE_SCENE = "First day of the BSL class: Emma meets Tom in the corridor."

FEMALE_NAMES = {
    "emma", "olivia", "amelia", "isla", "ava", "sophie", "grace", "lily",
    "ella", "chloe", "charlotte", "jessica", "megan", "hannah", "lucy",
    "holly", "emily", "poppy", "freya", "georgia", "katie", "rebecca",
    "sarah", "laura", "rachel", "claire", "helen", "joanne", "susan",
    "karen", "margaret", "elizabeth", "victoria", "alice", "ruby", "daisy",
    "imogen", "eleanor", "florence", "harriet", "zoe", "jane", "mary",
    "anna", "kate", "louise", "gemma", "nicola", "lisa", "sian", "ffion",
}

MALE_NAMES = {
    "oliver", "george", "harry", "jack", "jacob", "noah", "thomas", "oscar",
    "william", "james", "henry", "leo", "alfie", "joshua", "freddie",
    "archie", "ethan", "isaac", "alexander", "joseph", "edward", "samuel",
    "daniel", "matthew", "luke", "adam", "ryan", "liam", "callum", "connor",
    "dylan", "tom", "tim", "david", "john", "paul", "mark", "peter",
    "andrew", "simon", "richard", "michael", "stephen", "ben", "chris",
    "gareth", "rhys", "angus", "hamish",
}

UNISEX_NAMES = {"alex", "sam", "charlie", "jamie", "taylor", "jordan",
                "morgan", "robin", "ashley", "lee", "kerry", "max", "frankie",
                "billie", "sasha", "jesse", "riley", "casey", "jay", "kit"}

FEMALE_ROLES = {
    "woman", "lady", "girl", "mother", "mum", "mummy", "mom", "mam", "sister",
    "aunt", "auntie", "grandmother", "grandma", "gran", "nan", "nanna", "wife",
    "daughter", "girlfriend", "waitress", "actress", "hostess", "headmistress",
    "policewoman", "businesswoman", "chairwoman", "stewardess", "landlady",
    "housewife", "schoolgirl", "niece", "bride", "queen", "princess",
    "female voice", "narratress",
}

MALE_ROLES = {
    "man", "gentleman", "boy", "father", "dad", "daddy", "brother", "uncle",
    "grandfather", "grandpa", "grandad", "husband", "son", "boyfriend",
    "waiter", "actor", "host", "headmaster", "policeman", "businessman",
    "chairman", "steward", "landlord", "schoolboy", "nephew", "groom",
    "king", "prince", "male voice", "bloke", "lad",
}

EPICENE = {
    "teacher", "student", "pupil", "interpreter", "tutor", "doctor", "nurse",
    "customer", "friend", "colleague", "neighbour", "neighbor", "tourist",
    "guest", "visitor", "child", "baby", "person", "deaf person", "signer",
    "narrator", "voice", "presenter", "receptionist", "manager", "partner",
    "a", "b", "c", "1", "2", "3", "speaker", "participant", "parent",
}

ARTICLES = {"the", "a", "an", "my", "your", "his", "her"}
ARTICLE_GENDER: dict = {}

TITLE_PATTERNS = (
    (r"\bmrs\b|\bms\b|\bmiss\b|\bmadam\b|\blady\b", "F"),
    (r"\bmr\b|\bsir\b|\blord\b", "M"),
)


def morph(word: str):
    """English -ess nouns (waitress, actress) are feminine; nothing marks
    masculine."""
    w = (word or "").lower()
    if len(w) > 4 and w.endswith("ess") and not w.endswith(("less", "ness")):
        return "F"
    return None


SELF_GENDER_MARKERS = {
    "F": [r"re:(?i)\bI(?:'m| am) an? (?:woman|girl|mum|mother|wife|daughter)\b",
          r"re:(?i)\bmy (?:husband|boyfriend)\b"],
    "M": [r"re:(?i)\bI(?:'m| am) an? (?:man|boy|dad|father|husband|son)\b",
          r"re:(?i)\bmy (?:wife|girlfriend)\b"],
}

NON_SPEAKER_LABELS = {
    "note", "notes", "vocabulary", "key vocabulary", "grammar", "translation",
    "example", "examples", "exercise", "exercises", "answer", "answers",
    "key", "tip", "objective", "objectives", "learning objectives", "topic",
    "title", "level", "summary", "table", "dialogue", "conversation",
    "scene", "scenario", "narrator", "context", "introduction", "task",
    "instruction", "instructions", "gloss", "glosses", "sign", "signs",
    "handshape", "handshapes", "non-manual features", "non manual features",
    "nmf", "nmfs", "fingerspelling", "bsl", "en", "english", "video",
    "audio", "http", "https", "www",
}

SKIP_HEADINGS = [
    "gloss", "glosses", "sign", "signs", "handshape", "handshapes",
    "non-manual features", "non manual features", "nmf", "fingerspelling",
    "grammar", "vocabulary", "key vocabulary", "word list", "sign list",
    "exercise", "exercises", "answer key", "answers", "solutions",
    "notes", "note", "culture", "deaf culture", "cultural note",
    "learning objectives", "objectives", "pronunciation",
]

CONSOLIDATION_HEADINGS = {
    "putting it all together", "put it all together", "putting it together",
    "all together", "consolidation", "recap", "review", "summary",
}

# --- Voices: BSL has no audio, so the English text is read by English voices.
EDGE_LOCALES = ("en-",)
LOCALE_LABELS = {
    "en_GB": "United Kingdom (British English)",
    "en_IE": "Ireland (Irish English)",
    "en_US": "United States (American English)",
}
ACCENTS = LOCALE_LABELS
DEFAULT_ACCENT = "en_GB"
PREFERRED_PAIRS = {
    "en_GB": {"M": "en-GB-RyanNeural", "F": "en-GB-SoniaNeural"},
    "en_IE": {"M": "en-IE-ConnorNeural", "F": "en-IE-EmilyNeural"},
    "en_US": {"M": "en-US-GuyNeural", "F": "en-US-JennyNeural"},
}
VARIANTS_NOTE = ("British Sign Language itself has no audio; this pack voices only the English text of BSL course material (British English by default), never the signing.")
