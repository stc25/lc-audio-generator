"""Portuguese language pack (Brazilian and European)."""

CODE, NAME, NATIVE = "pt", "Portuguese", "Português"
SAMPLE_TEXT = "Olá! Eu me chamo Ana. Prazer em conhecê-lo! Como você está?"
SAMPLE_SCENE = "Primeiro dia de aula: Ana encontra o James no corredor."

FEMALE_NAMES = {
    "ana", "maria", "joana", "beatriz", "carolina", "mariana", "catarina",
    "inês", "ines", "sofia", "leonor", "matilde", "lara", "clara", "alice",
    "júlia", "julia", "helena", "laura", "manuela", "isabel", "teresa",
    "margarida", "rita", "sara", "diana", "cláudia", "claudia", "patrícia",
    "patricia", "sandra", "paula", "cristina", "susana", "vera", "raquel",
    "filipa", "daniela", "andreia", "mónica", "monica", "carla", "sílvia",
    "silvia", "luísa", "luisa", "rosa", "amélia", "amelia", "fernanda",
    "juliana", "camila", "gabriela", "letícia", "leticia", "larissa",
    "amanda", "bruna", "débora", "debora", "eduarda", "fabiana", "flávia",
    "flavia", "isadora", "jéssica", "jessica", "luana", "marcela", "natália",
    "natalia", "priscila", "renata", "simone", "tatiana", "thais", "vanessa",
    "viviane", "adriana", "aline", "bianca", "carmen", "cecília", "cecilia",
    "elisa", "esperança", "graça", "graca", "iara", "ivone", "lúcia", "lucia",
    "madalena", "nádia", "nadia", "olga", "regina", "rute", "solange",
    "francisca", "raquel", "thalita", "leila", "yara", "conceição",
}

MALE_NAMES = {
    "joão", "joao", "josé", "jose", "antónio", "antonio", "pedro", "manuel",
    "carlos", "paulo", "luís", "luis", "miguel", "rui", "tiago", "andré",
    "andre", "francisco", "ricardo", "fernando", "jorge", "nuno", "sérgio",
    "sergio", "vítor", "vitor", "hugo", "bruno", "diogo", "gonçalo", "goncalo",
    "rodrigo", "duarte", "afonso", "santiago", "gabriel", "guilherme",
    "leonardo", "lucas", "mateus", "matheus", "gustavo", "felipe", "rafael",
    "thiago", "vinícius", "vinicius", "eduardo", "marcelo", "márcio", "marcio",
    "roberto", "rodolfo", "júlio", "julio", "renato", "alexandre", "alberto",
    "armando", "artur", "augusto", "césar", "cesar", "cristiano", "daniel",
    "david", "délio", "domingos", "emanuel", "fábio", "fabio", "filipe",
    "flávio", "flavio", "henrique", "joaquim", "leandro", "márcio", "mário",
    "mario", "nelson", "otávio", "otavio", "raul", "ruben", "rubem", "samuel",
    "simão", "simao", "telmo", "tomás", "tomas", "vasco", "xavier", "james",
    "faber", "cadu", "jeff", "edresson", "tugão", "tugao", "diogo",
}

UNISEX_NAMES = {"alex", "ariel", "darci", "dani", "nicola", "cássio_f", "b", "l"}

FEMALE_ROLES = {
    "senhora", "sra", "senhorita", "srta", "dona", "mulher", "menina",
    "rapariga", "moça", "moca", "garota", "filha", "mãe", "mae", "mamãe",
    "irmã", "irma", "tia", "avó", "avo", "esposa", "namorada", "garçonete",
    "empregada", "vendedora", "atendente_f", "funcionária", "funcionaria",
    "professora", "doutora", "médica", "medica", "enfermeira", "farmacêutica",
    "farmaceutica", "recepcionista_f", "secretária", "secretaria", "caixa_f",
    "cliente_f", "aluna", "estudante_f", "turista_f", "amiga", "vizinha",
    "colega_f", "engenheira", "advogada", "cozinheira", "cabeleireira",
    "costureira", "comerciante_f", "compradora", "narradora", "voz feminina",
    "bot_f", "assistente_f",
}

MALE_ROLES = {
    "senhor", "sr", "seu", "homem", "menino", "rapaz", "moço", "moco",
    "garoto", "filho", "pai", "papai", "irmão", "irmao", "tio", "avô", "avo_m",
    "marido", "esposo", "namorado", "garçom", "garcom", "empregado",
    "vendedor", "funcionário", "funcionario", "professor", "doutor", "médico",
    "medico", "enfermeiro", "farmacêutico", "farmaceutico", "secretário",
    "secretario", "aluno", "amigo", "vizinho", "engenheiro", "advogado",
    "cozinheiro", "cabeleireiro", "comprador", "narrador", "voz masculina",
    "motorista_m", "porteiro", "carteiro",
}

# Identical for both genders in Portuguese.
EPICENE = {
    "cliente", "estudante", "recepcionista", "rececionista", "atendente",
    "gerente",
    "assistente", "colega", "turista", "motorista", "dentista", "jornalista",
    "artista", "pianista", "taxista", "caixa", "intérprete", "interprete",
    "guia", "agente", "gente", "pessoa", "jovem", "criança", "crianca",
    "adulto_e", "parente", "voz", "bot", "chatbot", "aprendiz", "utente",
    "a", "b", "c", "l", "1", "2", "3", "interlocutor",
}

ARTICLES = {"o", "a", "os", "as", "um", "uma", "uns", "umas", "do", "da",
            "no", "na", "de"}
ARTICLE_GENDER = {"a": "F", "uma": "F", "o": "M", "um": "M"}

TITLE_PATTERNS = (
    (r"\bsra\b|\bsra\.|\bsenhora\b|\bsrta\b|\bd\.\s*[a-z]*a\b|\bdra\b|"
     r"\bdoutora\b|\bprof\.?\s*a\b", "F"),
    (r"\bsr\b|\bsr\.|\bsenhor\b|\bdr\b|\bdr\.|\bdoutor\b|\bprof\.", "M"),
)

_F_SUFFIX = ("dora", "tora", "eira", "esa", "essa", "ina", "inha", "ica",
             "ista_f", "ana", "ada", "ega", "a")
_M_SUFFIX = ("dor", "tor", "eiro", "ão", "ao", "inho", "ico", "ano", "ado",
             "ego", "o", "os", "im", "um")


def morph(word: str):
    """Guess from a Portuguese ending. Returns 'F', 'M' or None.

    Portuguese is close to Spanish here (-o masculine, -a feminine), with -ão
    masculine and -ora/-eira feminine. Words in -e are left undecided."""
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


# --- The CULP course files label their two speakers "B" (the chatbot) and
# "L" (the learner). Both are pinned here so a fresh install is correct on the
# first render; everything stays overridable on the Cast tab.
# "accent" ties the hinted voice to one variety. Select Portugal instead and
# the hint still supplies the gender and the engine preference, but the voice
# comes from the European pair.
SPEAKER_HINTS = {
    "b": {"gender": "F", "voice": "edge:pt-BR-FranciscaNeural",
          "accent": "pt_BR",
          "note": "Bot — female, edge-tts"},
    "l": {"gender": "M", "voice": "edge:pt-BR-AntonioNeural",
          "accent": "pt_BR",
          "note": "Learner — male, edge-tts"},
}
SPEAKER_LABELS = {"b": "B — Bot", "l": "L — Learner"}

SELF_GENDER_MARKERS = {
    "F": ["obrigada", "sou portuguesa", "sou brasileira", "sou inglesa",
          "sou casada", "sou solteira", "sou filha", "filha única",
          "sou professora", "sou engenheira", "sou vendedora",
          "sou funcionária", "estou cansada", "sou aluna", "sou nascida",
          "chegámos atrasadas", "sou americana", "sou francesa"],
    "M": ["obrigado", "sou português", "sou brasileiro", "sou inglês",
          "sou casado", "sou solteiro", "sou filho", "filho único",
          "sou professor", "sou engenheiro", "sou vendedor",
          "sou funcionário", "estou cansado", "sou aluno",
          "sou americano", "sou francês"],
}

NON_SPEAKER_LABELS = {
    "nota", "notas", "observação", "vocabulário", "vocabulario", "léxico",
    "lexico", "gramática", "gramatica", "tradução", "traducao", "exemplo",
    "exemplos", "exercício", "exercicio", "exercícios", "exercicios",
    "resposta", "respostas", "solução", "solucao", "chave", "dica", "dicas",
    "objetivo", "objetivos", "tema", "título", "titulo", "nível", "nivel",
    "diálogo", "dialogo", "conversa", "conversação", "cena", "ato",
    "contexto", "situação", "situacao", "resumo", "introdução", "introducao",
    "atenção", "atencao", "importante", "fonte", "autor", "data",
    "pronúncia", "pronuncia", "cultura", "pt", "en", "inglês", "ingles",
    "português", "portugues", "áudio", "audio", "imagem", "figura", "tabela",
    "ver", "http", "https", "www",
    # these course files use English headings
    "vocabulary", "key vocabulary", "grammar", "translation", "example",
    "exercise", "answer", "answers", "key", "tip", "objective", "objectives",
    "learning objectives", "topic", "title", "level", "summary", "table",
    "note", "notes", "dialogue", "conversation", "expressions",
}

SKIP_HEADINGS = [
    "grammar", "gramática", "gramatica",
    "vocabulary", "key vocabulary", "vocabulary and useful expressions",
    "vocabulário", "vocabulario", "vocabulário e expressões úteis",
    "léxico", "lexico", "word list", "useful expressions", "expressões úteis",
    "exercise", "exercises", "exercício", "exercicio", "exercícios",
    "answer key", "answers", "respostas", "soluções", "solucoes",
    "notes", "note", "nota", "notas",
    "language notes", "language note", "notas de língua", "nota de língua",
    "culture", "cultura", "nota cultural",
    "pronunciation", "pronúncia", "pronuncia",
    "learning objectives", "objetivos", "objetivos de aprendizagem",
]

CONSOLIDATION_HEADINGS = {
    "putting it all together", "put it all together", "putting it together",
    "all together", "juntando tudo", "tudo junto", "revisão", "revisao",
    "recapitulação", "recapitulacao", "síntese", "sintese", "consolidation",
    "recap",
}

# fuller names, used in prose where "Portugal Portuguese" would read badly
ACCENT_LONG = {"pt_BR": "Brazilian Portuguese",
               "pt_PT": "European Portuguese"}

# --- Telling the two varieties apart from the text itself, so a European
# course file is not read out in Brazilian voices (and the reverse). Scored by
# counting distinctive words; no single hit decides anything.
import re as _re

_PT_WORDS = [
    "telemóvel", "comboio", "casa de banho", "pequeno-almoço", "autocarro",
    "apelido", "rececionista", "receção", "se faz favor", "faz favor",
    "fixe", "giro", "gira", "sumo", "rapariga", "frigorífico", "chávena",
    "talho", "ecrã", "boleia", "elétrico", "gelado", "pequeno almoço",
    "casa-de-banho", "autocarros", "comboios", "telemóveis", "divisão",
    "divisões", "arrendado", "lavandaria", "paragem", "bilheteira",
    "peço desculpa", "com licença", "estou à procura", "tomar duche",
    "anteontem", "prédio",
]
_BR_WORDS = [
    "ônibus", "trem", "banheiro", "café da manhã", "celular", "sobrenome",
    "geladeira", "suco", "garota", "garoto", "sorvete", "a gente", "legal",
    "bacana", "xícara", "açougue", "carona", "moça", "grana", "ponto com",
    "metrô", "apartamento alugado", "lanchonete", "cantina", "esporte",
    "time", "trem-bala", "café da manha",
]
# Structural giveaways: European favours "estou a fazer" and attaches the
# pronoun after the verb; Brazilian favours the gerund and "você".
_PT_PATTERNS = [
    r"\bestou a \w+r\b", r"\bestá a \w+r\b", r"\bestamos a \w+r\b",
    r"\bchamo-me\b", r"\blevanto-me\b", r"\bdeito-me\b", r"\bchama-se\b",
    r"\bfica-me\b", r"\bconhecem-se\b", r"\bcontar-te\b", r"\btu\b",
]
_BR_PATTERNS = [
    r"\bvocê\b", r"\bvocês\b", r"\bestou \w+ndo\b", r"\bestá \w+ndo\b",
    r"\bmе chamo\b", r"\beu me chamo\b", r"\bse chama\b",
]


def _count(text, words, patterns):
    low = text.lower()
    n = 0
    hits = []
    for w in words:
        c = low.count(w.lower())
        if c:
            n += c
            hits.append(w)
    for pat in patterns:
        c = len(_re.findall(pat, low))
        if c:
            n += c
    return n, hits


def detect_accent(text: str) -> dict:
    """Guess which variety a course file is written in.

    Returns {accent, confidence, scores, evidence}. `accent` is None when the
    two scores are too close to call — which is the right answer for a file
    that deliberately mixes them, like the CULP chatbot course.
    """
    pt, pt_hits = _count(text, _PT_WORDS, _PT_PATTERNS)
    br, br_hits = _count(text, _BR_WORDS, _BR_PATTERNS)
    total = pt + br
    if total < 5:
        return {"accent": None, "confidence": "none",
                "scores": {"pt_PT": pt, "pt_BR": br}, "evidence": []}
    lead = max(pt, br)
    other = min(pt, br)
    ratio = lead / max(1, total)
    winner = "pt_PT" if pt > br else "pt_BR"
    if ratio < 0.65 or lead - other < 4:
        return {"accent": None, "confidence": "mixed",
                "scores": {"pt_PT": pt, "pt_BR": br},
                "evidence": (pt_hits[:4] + br_hits[:4])}
    return {"accent": winner,
            "confidence": "high" if ratio > 0.8 else "likely",
            "scores": {"pt_PT": pt, "pt_BR": br},
            "evidence": (pt_hits if winner == "pt_PT" else br_hits)[:6]}


# --- Voice grouping. The voice catalogue itself comes from a live edge-tts
# snapshot; the pack only says which locales belong to the language, how to
# label them, and which voices are preferred as the M/F pair of each locale.
EDGE_LOCALES = ('pt-',)
LOCALE_LABELS = {
    'pt_BR': 'Brazil',
    'pt_PT': 'Portugal',
}
ACCENTS = LOCALE_LABELS
DEFAULT_ACCENT = 'pt_BR'
PREFERRED_PAIRS = {
    'pt_BR': {'M': 'pt-BR-AntonioNeural', 'F': 'pt-BR-FranciscaNeural'},
    'pt_PT': {'M': 'pt-PT-DuarteNeural', 'F': 'pt-PT-RaquelNeural'},
}
VARIANTS_NOTE = 'Brazilian (pt_BR) and European (pt_PT) Portuguese differ in pronunciation, vocabulary and some spelling, so choose the voice matching the variety of your course.'
