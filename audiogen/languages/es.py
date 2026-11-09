"""Spanish language pack."""

CODE, NAME, NATIVE = "es", "Spanish", "Español"
SAMPLE_TEXT = "Hola, buenos días. Me alegro mucho de verte. ¿Cómo estás?"
SAMPLE_SCENE = "Primer día de clase: Marta conoce a Diego en el pasillo."

FEMALE_NAMES = {
    "ana","maria","maría","carmen","josefa","isabel","dolores","pilar","teresa",
    "rosa","francisca","antonia","laura","cristina","marta","elena","lucia","lucía",
    "sofia","sofía","paula","raquel","beatriz","silvia","monica","mónica","patricia",
    "sara","alba","irene","claudia","natalia","andrea","julia","noelia","nuria",
    "eva","alicia","susana","yolanda","rocio","rocío","angeles","ángeles","mercedes",
    "concepcion","concepción","manuela","juana","catalina","esperanza","amparo",
    "encarnacion","encarnación","milagros","gloria","victoria","veronica","verónica",
    "sandra","tamara","lorena","vanesa","miriam","eugenia","adriana","valeria",
    "camila","daniela","gabriela","mariana","fernanda","ximena","regina","renata",
    "guadalupe","lupita","itzel","abril","emilia","martina","catalina","florencia",
    "agustina","josefina","clara","ines","inés","aurora","blanca","celia","diana",
    "elisa","estela","fatima","fátima","helena","ivana","jimena","leticia","luisa",
    "magdalena","margarita","marina","nerea","olga","pia","ramona","rebeca","rita",
    "salome","salomé","selena","tania","valentina","violeta","ximena","yolanda",
    "consuelo","dulce","estrella","itziar","maite","montse","montserrat","aitana",
}

MALE_NAMES = {
    "antonio","jose","josé","manuel","francisco","juan","david","javier","daniel",
    "carlos","miguel","rafael","pedro","angel","ángel","alejandro","fernando","luis",
    "sergio","pablo","jorge","alberto","enrique","vicente","ramon","ramón","andres",
    "andrés","raul","raúl","ruben","rubén","oscar","óscar","victor","víctor","ivan",
    "iván","adrian","adrián","diego","mario","roberto","alvaro","álvaro","joaquin",
    "joaquín","ignacio","gonzalo","hugo","martin","martín","marcos","nicolas",
    "nicolás","cesar","césar","emilio","felipe","gabriel","guillermo","hector",
    "héctor","jaime","jesus","jesús","julio","lorenzo","lucas","marcelo","mateo",
    "mauricio","octavio","omar","patricio","rodrigo","salvador","santiago","tomas",
    "tomás","gerardo","arturo","benito","bruno","cristian","damian","damián",
    "eduardo","esteban","ernesto","fabian","fabián","gustavo","isidro","leandro",
    "leonardo","matias","matías","maximiliano","norberto","pascual","ricardo",
    "sebastian","sebastián","teodoro","valentin","valentín","xavier","aitor","iker",
    "unai","gorka","paco","pepe","nacho","chema","kike","toni","alex","álex",
}

UNISEX_NAMES = {
    "alex", "cruz", "guadalupe", "trinidad", "reyes", "ariel", "yael",
}

FEMALE_ROLES = {
    "mujer","chica","señora","senora","sra","srta","señorita","senorita","madre",
    "mama","mamá","hija","abuela","hermana","tia","tía","novia","esposa","camarera",
    "profesora","maestra","doctora","medica","médica","enfermera","dependienta",
    "vendedora","secretaria","azafata","cajera","clienta","alumna",
    "empleada","jefa","directora","cocinera","panadera",
    "peluquera","farmaceutica","farmacéutica","amiga","vecina","compañera","companera","entrevistadora","locutora",
    "narradora","voz femenina","woman","female","girl","she","lady","mrs","ms",
}

MALE_ROLES = {
    "hombre","chico","señor","senor","sr","padre","papa","papá","hijo","abuelo",
    "hermano","tio","tío","novio","esposo","marido","camarero","mesero","profesor",
    "maestro","doctor","medico","médico","enfermero","dependiente","vendedor",
    "secretario","cajero","cliente","alumno","empleado",
    "jefe","director","cocinero","panadero","peluquero","farmaceutico","farmacéutico",
    "conductor","chofer","chófer","amigo","vecino","compañero","companero",
    "entrevistador","locutor","narrador","voz masculina","man","male","boy","he",
    "gentleman","mr","sir",
}

EPICENE = {
    "recepcionista","estudiante","turista","taxista","guia","gu\u00eda","policia",
    "polic\u00eda","periodista","dentista","artista","cantante","joven","persona",
    "hablante","voz","interlocutor","interlocutora","a","b","c","1","2","3",
}

ARTICLES = {"el", "la", "los", "las", "un", "una", "unos", "unas", "del", "de"}
ARTICLE_GENDER = {"la": "F", "una": "F", "el": "M", "un": "M"}

TITLE_PATTERNS = (
    (r"\bsra\b|\bsra\.|\bse\u00f1ora\b|\bsrta\b|\bse\u00f1orita\b|\bdra\b", "F"),
    (r"\bsr\b|\bsr\.|\bse\u00f1or\b|\bdon\b|\bdr\b", "M"),
)

_F_SUFFIX = ("dora", "tora", "esa", "ina", "illa", "ita", "ana", "era", "a")
_M_SUFFIX = ("dor", "tor", "ero", "ista_m", "ano", "illo", "ito", "o", "os")


def morph(word: str):
    """Guess from a Spanish ending. Returns 'F', 'M' or None."""
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


SELF_GENDER_MARKERS = {
    "F": ["soy española", "soy inglesa", "soy casada", "estoy casada",
          "soy soltera", "estoy soltera", "soy estudiante", "soy profesora",
          "soy enfermera", "nací", "estoy cansada", "estoy lista",
          "soy americana", "soy mexicana"],
    "M": ["soy español", "soy inglés", "soy casado", "estoy casado",
          "soy soltero", "estoy soltero", "soy profesor", "soy enfermero",
          "estoy cansado", "estoy listo", "soy americano", "soy mexicano"],
}

NON_SPEAKER_LABELS = {
    "nota","notas","note","notes","vocabulario","vocabulary","vocab","gramatica",
    "gramática","grammar","traduccion","traducción","translation","traducciones",
    "ejemplo","ejemplos","example","examples","ejercicio","ejercicios","exercise",
    "exercises","respuesta","respuestas","answer","answers","clave","key","tip",
    "tips","consejo","consejos","objetivo","objetivos","objective","objectives",
    "tema","topic","titulo","título","title","nivel","level","dialogo","diálogo",
    "dialogue","dialog","conversacion","conversación","conversation","escena",
    "scene","acto","act","contexto","context","situacion","situación","situation",
    "resumen","summary","introduccion","introducción","introduction","warning",
    "aviso","atencion","atención","importante","important","source","fuente",
    "author","autor","date","fecha","tags","etiquetas","http","https","ftp","www",
    "en","es","eng","spa","english","espanol","español","spanish","audio","image",
    "figura","figure","table","tabla","see","vease","véase","todo","fixme","idea",
}

SKIP_HEADINGS = [
    "grammar", "gram\u00e1tica", "gramatica",
    "vocabulary", "key vocabulary", "vocabulario", "vocab", "lista de palabras",
    "exercise", "exercises", "ejercicio", "ejercicios",
    "answer key", "answers", "respuestas", "soluciones", "clave de respuestas",
    "notes", "note", "nota", "notas",
    "culture", "cultura", "nota cultural",
    "pronunciation", "pronunciaci\u00f3n", "pronunciacion",
    "learning objectives", "objetivos", "objetivos de aprendizaje",
]

CONSOLIDATION_HEADINGS = {
    "putting it all together", "put it all together", "putting it together",
    "all together", "juntando todo", "todo junto", "repaso", "recapitulaci\u00f3n",
    "consolidation", "recap", "s\u00edntesis", "sintesis",
}


# --- Voice grouping. The voice catalogue itself comes from a live edge-tts
# snapshot; the pack only says which locales belong to the language, how to
# label them, and which voices are preferred as the M/F pair of each locale.
EDGE_LOCALES = ('es-',)
LOCALE_LABELS = {
    'es_ES': 'Spain (Castilian)',
    'es_MX': 'Mexico',
    'es_AR': 'Argentina (Rioplatense)',
    'es_UY': 'Uruguay (Rioplatense)',
    'es_CU': 'Cuba (Caribbean)',
    'es_PR': 'Puerto Rico (Caribbean)',
    'es_DO': 'Dominican Republic (Caribbean)',
    'es_VE': 'Venezuela (Caribbean)',
    'es_PE': 'Peru (Andean)',
    'es_BO': 'Bolivia (Andean)',
    'es_EC': 'Ecuador (Andean)',
    'es_CO': 'Colombia (Andean)',
    'es_CL': 'Chile',
    'es_PY': 'Paraguay',
    'es_CR': 'Costa Rica',
    'es_PA': 'Panama',
    'es_GT': 'Guatemala',
    'es_HN': 'Honduras',
    'es_NI': 'Nicaragua',
    'es_SV': 'El Salvador',
    'es_US': 'United States',
    'es_GQ': 'Equatorial Guinea',
}
ACCENTS = LOCALE_LABELS
DEFAULT_ACCENT = 'es_ES'
PREFERRED_PAIRS = {
    'es_ES': {'M': 'es-ES-AlvaroNeural', 'F': 'es-ES-ElviraNeural'},
    'es_MX': {'M': 'es-MX-JorgeNeural', 'F': 'es-MX-DaliaNeural'},
    'es_AR': {'M': 'es-AR-TomasNeural', 'F': 'es-AR-ElenaNeural'},
    'es_BO': {'M': 'es-BO-MarceloNeural', 'F': 'es-BO-SofiaNeural'},
    'es_CL': {'M': 'es-CL-LorenzoNeural', 'F': 'es-CL-CatalinaNeural'},
    'es_CO': {'M': 'es-CO-GonzaloNeural', 'F': 'es-CO-SalomeNeural'},
    'es_CR': {'M': 'es-CR-JuanNeural', 'F': 'es-CR-MariaNeural'},
    'es_CU': {'M': 'es-CU-ManuelNeural', 'F': 'es-CU-BelkysNeural'},
    'es_DO': {'M': 'es-DO-EmilioNeural', 'F': 'es-DO-RamonaNeural'},
    'es_EC': {'M': 'es-EC-LuisNeural', 'F': 'es-EC-AndreaNeural'},
    'es_GQ': {'M': 'es-GQ-JavierNeural', 'F': 'es-GQ-TeresaNeural'},
    'es_GT': {'M': 'es-GT-AndresNeural', 'F': 'es-GT-MartaNeural'},
    'es_HN': {'M': 'es-HN-CarlosNeural', 'F': 'es-HN-KarlaNeural'},
    'es_NI': {'M': 'es-NI-FedericoNeural', 'F': 'es-NI-YolandaNeural'},
    'es_PA': {'M': 'es-PA-RobertoNeural', 'F': 'es-PA-MargaritaNeural'},
    'es_PE': {'M': 'es-PE-AlexNeural', 'F': 'es-PE-CamilaNeural'},
    'es_PR': {'M': 'es-PR-VictorNeural', 'F': 'es-PR-KarinaNeural'},
    'es_PY': {'M': 'es-PY-MarioNeural', 'F': 'es-PY-TaniaNeural'},
    'es_SV': {'M': 'es-SV-RodrigoNeural', 'F': 'es-SV-LorenaNeural'},
    'es_US': {'M': 'es-US-AlonsoNeural', 'F': 'es-US-PalomaNeural'},
    'es_UY': {'M': 'es-UY-MateoNeural', 'F': 'es-UY-ValentinaNeural'},
    'es_VE': {'M': 'es-VE-SebastianNeural', 'F': 'es-VE-PaolaNeural'},
}
VARIANTS_NOTE = 'Spanish varies by country; edge-tts has 22 national locales (Castilian, Mexican, Rioplatense, Caribbean, Andean and more) and the pack labels each so you can match the variety of your course.'

# Optional grouping of national locales into broader varieties.
VARIETY_GROUPS = {'es_CARIBE': ['es_CU', 'es_DO', 'es_PR', 'es_VE'], 'es_ANDES': ['es_PE', 'es_EC', 'es_BO', 'es_CO'], 'es_RIOPLATENSE': ['es_AR', 'es_UY']}
