"""
Nomes de verdade (pessoas, organizações, lugares, obras), com o spaCy:
modelos treinados pra reconhecer entidades em textos de notícia, um pra
português e um pra inglês. No lugar do "nome é o que tem maiúscula"
(sinais.nomes), que juntava "Agricultura e Pecuária André de Paula" num
nome só e pegava "Astro da NBA" e "Reconhece" (começo de título).

Cada nome sai com:
  - nome: como aparece no texto ("Flávio Bolsonaro"), pra mostrar no hub;
  - chave: normalizado ("flavio bolsonaro"), pra comparar notícias e pro
    "seguir pessoas" (o mesmo nome em português e inglês vira a mesma
    chave quando é um lugar ou órgão conhecido: "Ukraine" e "Ucrânia"
    viram "ucrania");
  - tipo: pessoa, organização, lugar ou outro (obra, produto, evento).

Os modelos (requirements.txt): pt_core_news_md e en_core_web_md, ~40 MB
cada. Sem eles (rodando local sem instalar), volta pro sinais.nomes, com
um aviso.

O idioma vem do catálogo de fontes (feed_catalog.idioma) quando a fonte
está lá; senão, das palavras mais comuns de cada língua (idioma()).
"""
import re
import sys
from collections import Counter

from sinais import NAO_SAO_NOMES, PALAVRAS_VAZIAS, nomes as nomes_pela_maiuscula, normalizar

MODELOS = {"pt": "pt_core_news_md", "en": "en_core_web_md"}
CARACTERES_DO_TEXTO = 600
MAX_NOMES = 10
MAX_PALAVRAS_DO_NOME = 6

# Rótulos dos dois modelos -> os nossos. O de inglês também marca datas,
# valores, quantidades e nacionalidades ("Brazilian"): ficam de fora.
TIPOS = {
    "PER": "pessoa", "PERSON": "pessoa",
    "ORG": "organização",
    "LOC": "lugar", "GPE": "lugar", "FAC": "lugar",
    "MISC": "outro", "PRODUCT": "outro", "EVENT": "outro", "WORK_OF_ART": "outro", "LAW": "outro",
}

# Créditos de foto e restos de página que o modelo confunde com nome
NAO_SAO_ENTIDADES = set("""
getty images|divulgacao|reproducao|reproducao instagram|reproducao redes sociais|reproducao tv globo|
foto|fotos|arquivo|arquivo pessoal|acervo|acervo pessoal|montagem|publicado|publicado em|atualizado|
atualizado em|leia mais|veja mais|saiba mais|siga|whatsapp|afp|ap photo|reuters|efe|folhapress|
estadao conteudo|agencia brasil|shutterstock|freepik|unsplash|credito|creditos|imagem|ia|ai|
sabe|sabia|conheca|descubra|relembre|lembre|aprenda|acompanhe|ouca|clique|baixe|compre|aproveite|garanta|
assine|vote|exclusivo|urgente|ao vivo|video|videos|podcast|newsletter
""".replace("\n", "").split("|"))

# Cargo ou profissão colado no nome ("Cantor Netinho", "Senador Flávio
# Bolsonaro"): sai da frente; sozinho ("Senador"), não é nome
CARGOS = set("""
cantor cantora ator atriz senador senadora deputado deputada presidente presidenta ministro ministra governador
governadora prefeito prefeita vereador vereadora jogador jogadora tecnico tecnica treinador treinadora
apresentador apresentadora influenciador influenciadora empresario empresaria juiz juiza ex atacante goleiro
zagueiro lateral meia volante piloto diretor diretora produtor produtora rapper modelo jornalista
candidato candidata secretario secretaria general coronel delegado delegada advogado advogada medico medica
""".split())

# Mesmo lugar ou órgão em português e em inglês: a chave fica a de
# português, pra notícia em inglês ter nome em comum com a brasileira.
MESMA_CHAVE = {
    "united states": "estados unidos", "us": "estados unidos", "usa": "estados unidos", "eua": "estados unidos",
    "u s": "estados unidos", "america": "estados unidos", "white house": "casa branca",
    "united kingdom": "reino unido", "uk": "reino unido", "britain": "reino unido", "england": "inglaterra",
    "london": "londres", "new york": "nova york", "brazil": "brasil", "germany": "alemanha", "france": "franca",
    "spain": "espanha", "italy": "italia", "japan": "japao", "russia": "russia", "ukraine": "ucrania",
    "kyiv": "kiev", "iran": "ira", "iraq": "iraque", "syria": "siria", "lebanon": "libano", "egypt": "egito",
    "saudi arabia": "arabia saudita", "turkey": "turquia", "greece": "grecia", "poland": "polonia",
    "sweden": "suecia", "norway": "noruega", "denmark": "dinamarca", "netherlands": "holanda",
    "belgium": "belgica", "switzerland": "suica", "mexico": "mexico", "canada": "canada", "argentina": "argentina",
    "south korea": "coreia do sul", "north korea": "coreia do norte", "china": "china", "beijing": "pequim",
    "taiwan": "taiwan", "india": "india", "pakistan": "paquistao", "afghanistan": "afeganistao",
    "venezuela": "venezuela", "cuba": "cuba", "colombia": "colombia", "chile": "chile", "peru": "peru",
    "europe": "europa", "european union": "uniao europeia", "eu": "uniao europeia", "ue": "uniao europeia",
    "united nations": "onu", "un": "onu", "nato": "otan", "vatican": "vaticano", "the vatican": "vaticano",
    "gaza strip": "gaza", "faixa de gaza": "gaza", "west bank": "cisjordania", "middle east": "oriente medio",
    "pentagon": "pentagono", "congress": "congresso americano", "supreme court": "suprema corte",
    "federal reserve": "fed", "the fed": "fed",
}

# Pra decidir o idioma quando a fonte não diz: palavras que só aparecem
# (com frequência) numa das línguas
_SO_PT = set("de da do das dos que em para com uma os no na por mais ao pelo pela sobre como seu sua apos nao e é sao".split())
_SO_EN = set("the of and to in is for on with that by at from his her its are was be how why what this after will".split())

# Jogo, filme ou produto com número no título ("GTA 6", "FIFA 26",
# "Hellboy 3:"): o modelo de inglês costuma deixar passar (marca só o 6).
# Sigla + número em qualquer lugar; palavra + número só no fim do título ou
# antes de pontuação, pra não pegar "Pinguins 3 vezes".
_SIGLA_COM_NUMERO = re.compile(r"\b([A-Z]{2,5})\s(\d{1,2})\b")
_PALAVRA_COM_NUMERO = re.compile(r"\b([A-Z][a-zà-ÿ]{3,})\s(\d{1,2})(?=\s*[’'\":|?!.,]|\s*$)")
NAO_SAO_OBRAS = set("temporada episodio capitulo parte volume fase rodada dia top lei artigo numero edicao semana ano".split())

_ASPAS_E_PONTUACAO = "“”‘’\"'«»()[]{}|.,;:!?–—-*#•"
_ARTIGO_INICIAL = re.compile(r"^(o|a|os|as|the|um|uma)\s+", re.IGNORECASE)

_modelos = {}
_avisou = False


def idioma(texto, dica=None):
    """'pt' ou 'en'. `dica` (o idioma do catálogo) ganha quando existe."""
    if dica in MODELOS:
        return dica
    palavras = (texto or "").lower().split()
    pt = sum(p in _SO_PT for p in palavras)
    en = sum(p in _SO_EN for p in palavras)
    return "en" if en > pt else "pt"


def _modelo(lingua):
    """O spaCy daquela língua, carregado uma vez; None se não estiver instalado."""
    global _avisou
    if lingua not in _modelos:
        try:
            import spacy

            # só o reconhecedor de entidades: o resto (gramática, lemas) não é usado e custa tempo
            _modelos[lingua] = spacy.load(MODELOS[lingua], enable=["tok2vec", "ner"])
        except (ImportError, OSError) as erro:
            _modelos[lingua] = None
            if not _avisou:
                print(f"::warning::spaCy indisponível ({type(erro).__name__}: {erro}); nomes pela maiúscula", file=sys.stderr)
                _avisou = True
    return _modelos[lingua]


def chave(nome):
    k = normalizar(nome)
    return MESMA_CHAVE.get(k, k)


def _limpar(texto):
    """'“Campus Drivers’' -> 'Campus Drivers'; 'Colin Farrell\\nCréditos' -> 'Colin Farrell';
    'Divulgação/Netflix' -> 'Divulgação', 'Netflix'."""
    pedacos = re.split(r"\n|\s\|\s|/|;|:\s", texto)
    saida = []
    for p in pedacos:
        p = p.strip().strip(_ASPAS_E_PONTUACAO).strip()
        p = re.sub(r"['’]s$", "", p)  # "Daniel Craig’s" -> "Daniel Craig"
        p = _ARTIGO_INICIAL.sub("", p) if len(p.split()) > 1 else p
        palavras = p.split()
        while len(palavras) > 1 and normalizar(palavras[0]) in CARGOS:
            palavras = palavras[1:]
        p = " ".join(palavras)
        if len(palavras) == 1 and normalizar(p) in CARGOS:
            continue
        saida.append(p)
    return saida


def _vale(nome):
    k = normalizar(nome)
    if "$" in nome or len(k) < 2 or not re.search(r"[a-z]", k) or k in NAO_SAO_ENTIDADES:
        return False
    if nome == nome.lower():  # "mercado", sem nenhuma maiúscula: não é nome próprio
        return False
    # palavra comum em caixa alta ("CONDIÇÃO"): sigla não tem acento
    if " " not in nome and nome.isupper() and any(ord(c) > 127 for c in nome):
        return False
    if " " not in k and (k in PALAVRAS_VAZIAS or k in NAO_SAO_NOMES):
        return False
    # "Temporada 2", "Capítulo 130": parte de uma série, não um nome
    if re.fullmatch(r"([a-z]+) \d+", k) and k.split()[0] in NAO_SAO_OBRAS:
        return False
    # o modelo de inglês às vezes pega o título inteiro como nome de obra
    if len(k.split()) > MAX_PALAVRAS_DO_NOME or len(nome) > 45:
        return False
    return True


def _do_doc(doc, titulo):
    """Os nomes de um texto processado: os do título primeiro, depois os
    mais citados."""
    tipos, formas, vezes = {}, {}, Counter()
    for ent in doc.ents:
        tipo = TIPOS.get(ent.label_)
        if not tipo:
            continue
        for nome in _limpar(ent.text):
            if not _vale(nome):
                continue
            k = chave(nome)
            vezes[k] += 1
            formas.setdefault(k, nome)
            tipos.setdefault(k, Counter())[tipo] += 1
    for padrao in (_SIGLA_COM_NUMERO, _PALAVRA_COM_NUMERO):
        for palavra, numero in padrao.findall(titulo or ""):
            nome = f"{palavra} {numero}"
            k = chave(nome)
            if normalizar(palavra) in NAO_SAO_OBRAS or normalizar(palavra) in PALAVRAS_VAZIAS:
                continue
            vezes[k] += 1
            formas.setdefault(k, nome)
            tipos.setdefault(k, Counter())["outro"] += 1
    titulo_normalizado = f" {normalizar(titulo)} "
    ordem = sorted(vezes, key=lambda k: (f" {normalizar(formas[k])} " not in titulo_normalizado, -vezes[k]))
    return [{"nome": formas[k], "chave": k, "tipo": tipos[k].most_common(1)[0][0]} for k in ordem[:MAX_NOMES]]


def extrair(noticias):
    """noticias: [(titulo, texto, idioma ou None)] -> [[{nome, chave, tipo}]],
    na mesma ordem. Processa em lote por língua (bem mais rápido)."""
    saida = [None] * len(noticias)
    por_lingua = {}
    for i, (titulo, texto, dica) in enumerate(noticias):
        lingua = idioma(f"{titulo} {(texto or '')[:300]}", dica)
        por_lingua.setdefault(lingua, []).append(i)
    for lingua, indices in por_lingua.items():
        nlp = _modelo(lingua)
        textos = [f"{noticias[i][0]}\n{(noticias[i][1] or '')[:CARACTERES_DO_TEXTO]}" for i in indices]
        if nlp is None:
            for i, texto in zip(indices, textos):
                saida[i] = [{"nome": n, "chave": chave(n), "tipo": "outro"} for n in nomes_pela_maiuscula(texto)[:MAX_NOMES]]
            continue
        for i, doc in zip(indices, nlp.pipe(textos, batch_size=64)):
            saida[i] = _do_doc(doc, noticias[i][0])
    return saida
