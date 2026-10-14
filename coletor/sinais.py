"""
Sinais de texto, sem IA: o que a classificação (classificar.py) e o
agrupamento de histórias (agrupar.py) usam pra entender uma notícia.

- normalizar: minúsculas, sem acento, só letras/números/espaço;
- palavras: as que carregam sentido (sem "de", "the", "para"...);
- nomes: pessoas, empresas, lugares e siglas pelo jeito de escrever
  (palavras com maiúscula no meio da frase, "Banco Central", "STF",
  "OpenAI"). Não é um reconhecedor de entidades de verdade (spaCy), mas
  pega a maioria e não custa nada; dá pra trocar depois;
- numeros: placares, valores, versões ("2 a 1", "R$ 150 milhões",
  "iPhone 17"): notícias com números diferentes tendem a ser
  acontecimentos diferentes.
"""
import re
import unicodedata

PALAVRAS_VAZIAS = set("""
a o as os um uma uns umas de da do das dos em na no nas nos por pela pelo pelas pelos para pra pro com sem sob
sobre entre ate apos ante e ou mas que se ja nao sim mais menos muito muita muitos muitas como quando onde
qual quais quem cujo seu sua seus suas ele ela eles elas isso isto esse essa este esta aquele aquela ao aos
foi ser sao era estao esta tem ter teve vai vao pode podem deve devem fica ficam diz dizem afirma segundo
apos durante contra desde ha hoje ontem amanha agora ainda tambem so apenas novo nova novos novas
the of and to in on for with at by from as is are was were be been it its this that these those an or
but not no new after before over into out up about more than will would can could has have had says said
""".split())

# Palavras que começam frase ou título com maiúscula sem serem nomes
NAO_SAO_NOMES = set("""
o a os as um uma de do da em no na para por com e ao aos veja saiba entenda confira assista leia
the a an in on at of for to and why how what when who new
janeiro fevereiro marco abril maio junho julho agosto setembro outubro novembro dezembro
segunda terca quarta quinta sexta sabado domingo hoje ontem
""".split())

CONECTORES_DE_NOME = {"de", "da", "do", "das", "dos", "of", "van", "von", "del", "la", "le"}

_PALAVRA = re.compile(r"[A-Za-zÀ-ÖØ-öø-ÿ0-9][A-Za-zÀ-ÖØ-öø-ÿ0-9'’.-]*")
_NUMERO = re.compile(r"\d+(?:[.,]\d+)?")


def sem_acento(texto):
    return unicodedata.normalize("NFKD", texto or "").encode("ascii", "ignore").decode()


def normalizar(texto):
    return re.sub(r"\s+", " ", re.sub(r"[^a-z0-9 ]+", " ", sem_acento(texto).lower())).strip()


def palavras(texto, minimo=3):
    """Palavras com sentido, normalizadas (sem acento, minúsculas)."""
    return [p for p in normalizar(texto).split() if len(p) >= minimo and p not in PALAVRAS_VAZIAS and not p.isdigit()]


def numeros(texto):
    """Números do texto, normalizados ("1.500" -> "1500", "2,5" -> "2.5")."""
    saida = set()
    for n in _NUMERO.findall(texto or ""):
        n = n.replace(".", "") if re.fullmatch(r"\d{1,3}(\.\d{3})+", n) else n.replace(",", ".")
        saida.add(n)
    return saida


def nomes(texto):
    """Nomes próprios e siglas pelo jeito de escrever: sequências de palavras
    com inicial maiúscula (com "de", "da"... no meio), siglas (STF, NBA) e
    palavras com maiúscula no meio (OpenAI, iPhone). Normalizados."""
    achados = []
    for frase in re.split(r"(?<=[.!?:;])\s+|\n+|\s[-–—|]\s", texto or ""):
        tokens = _PALAVRA.findall(frase)
        atual = []
        for i, t in enumerate(tokens):
            limpo = t.strip(".'’-")
            if not limpo:
                continue
            maiuscula = limpo[0].isupper() or (len(limpo) > 1 and any(c.isupper() for c in limpo[1:]) and limpo[0].islower())
            sigla = len(limpo) >= 2 and limpo.isupper() and limpo.isalpha()
            if (maiuscula or sigla) and not (i == 0 and limpo.lower() in NAO_SAO_NOMES and not sigla):
                atual.append(limpo)
            elif atual and limpo.lower() in CONECTORES_DE_NOME:
                atual.append(limpo.lower())
            else:
                if atual:
                    achados.append(atual)
                atual = []
        if atual:
            achados.append(atual)
    saida = []
    for grupo in achados:
        while grupo and grupo[-1] in CONECTORES_DE_NOME:
            grupo = grupo[:-1]
        nome = normalizar(" ".join(grupo))
        if not nome or nome in NAO_SAO_NOMES or len(nome) < 2:
            continue
        # uma palavra só, começando frase, sem ser sigla: provável palavra comum
        if len(grupo) == 1 and not grupo[0].isupper() and normalizar(grupo[0]) in PALAVRAS_VAZIAS:
            continue
        if nome not in saida:
            saida.append(nome)
    return saida
