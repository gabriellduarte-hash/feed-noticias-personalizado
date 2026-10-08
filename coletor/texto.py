"""
Limpeza do texto das notícias: tudo o que não é a matéria sai antes de
gravar. Anúncio ("Publicidade", "Continua depois da publicidade"), aviso
de cookies, "siga no WhatsApp", pedido de assinatura, aviso de link de
afiliado, botões de comentário, rodapé do WordPress ("The post ...
appeared first on ...").

  - texto_do_rss(entry): o texto mais completo que o próprio feed manda
    (content:encoded ou description), já limpo. O RSS traz só a matéria;
    a página do site traz a matéria mais menus, anúncios e links pra
    outras matérias. Por isso o RSS vem sempre primeiro, e a página
    (enriquecer.py) só é aberta quando o feed manda pouco texto.
  - html_para_texto(html): HTML -> um parágrafo por linha (o hub monta
    intertítulos e listas a partir disso), sem figuras, scripts,
    formulários e blocos de anúncio.
  - texto_da_pagina(html): a matéria de uma página inteira (trafilatura
    no modo "precisão": prefere deixar um trecho de fora a trazer menu e
    anúncio junto), já limpa.
  - limpar_texto(texto, repetidos): tira os parágrafos de lixo e os
    trechos que se repetem em várias matérias da mesma fonte (o
    limpar_textos.py conta as repetições no banco e decide com
    eh_repetido()).

As regras fixas também existem no hub (src/lib/limpar-texto.ts), pras
notícias coletadas na hora de adicionar uma fonte e pro que já estava
gravado. Mudou uma, muda a outra.
"""
import html
import re

import ftfy
import trafilatura
from lxml import etree
from lxml import html as lhtml

MAX_CARACTERES = 12000

# Tags que nunca são texto da matéria
TAGS_FORA = {
    "script", "style", "noscript", "iframe", "form", "button", "svg", "figure", "figcaption",
    "aside", "nav", "footer", "header", "video", "audio", "object", "embed", "input", "select",
    "textarea", "template", "picture", "img",
}
# Tags que quebram linha (viram parágrafos separados)
TAGS_BLOCO = {
    "p", "div", "section", "article", "main", "h1", "h2", "h3", "h4", "h5", "h6", "li", "ul", "ol",
    "blockquote", "pre", "table", "tr", "dl", "dt", "dd", "hr",
}
# class/id de blocos que não são matéria (anúncio, "leia também", compartilhar...).
# Comparado por palavra da class, do começo: "ad" sozinho ou "ad-..." sim,
# "article-body-ad-free" não (senão sumiria a matéria inteira).
PREFIXOS_FORA = (
    "ad-", "ads-", "ad_", "ads_", "adsbygoogle", "advert", "publicidade", "anuncio", "banner",
    "cookie", "newsletter", "related", "relacionad", "leia-tambem", "veja-tambem", "sharedaddy",
    "share", "social-share", "compartilh", "sponsor", "patrocin", "outbrain", "taboola",
    "code-block", "jp-relatedposts", "instagram-media",
)

# Parágrafo inteiro que é só rótulo de anúncio, navegação ou botão
ROTULOS = re.compile(
    r"^(publicidade|an[uú]ncio|propaganda|patrocinado( por)?|conte[uú]do (patrocinado|de marca|pago)"
    r"|continua (depois|ap[oó]s) (d?a )?publicidade|leia (mais|tamb[eé]m|a seguir|mais sobre)"
    r"|veja (tamb[eé]m|mais)|saiba mais|confira( tamb[eé]m)?|tudo sobre|mais lidas?|relacionad[ao]s?"
    r"|ver (na|no) amazon.*|ver (esse|este) post no instagram"
    r"|(excluir|editar|responder|denunciar) coment[aá]rio|confirmar a exclus[aã]o do coment[aá]rio"
    r"|compartilhe|compartilhar|imprimir|copiar link|republicar|me registro"
    r"|(rep[oó]rter|redator|redatora|colaborador|colaboradora|freelancer|editor|editora)( de [\w ,]{1,60})?"
    # crédito de imagem que sobra solto: "Reprodução", "Divulgação/Nasa", "Foto: Fulano"
    r"|(reprodu[cç][aã]o|divulga[cç][aã]o)(\s*[/|-].{0,40})?|(foto|imagem|cr[eé]dito)s?\s*[:/-].{0,60}"
    # em inglês (fontes de fora, sql/032)
    r"|advertisement|sponsored( content)?|story continues below( advertisement)?|read more|related( stories| articles| coverage)?"
    r"|recommended( stories| for you)?|more from .{1,40}|share this (article|story)|(photo|image)( credit)?\s*[:/-].{0,60}"
    r"|getty images|(sign up|subscribe)( now| today)?)[\s:.?!→»>-]*$",
    re.I,
)
# "Publicado em: 06/10/2026 14h" / "Publicado em: Modificado em:"
DATAS_DE_PUBLICACAO = re.compile(r"^((publicado|modificado|atualizado) em:?\s*(\d[\d/:h, -]{0,25})?\s*)+$", re.I)
# Data solta, de lista de outras matérias: "1 de outubro de 2026 - 17:10"
DATA_SOLTA = re.compile(r"^\d{1,2} de [a-zç]+ de \d{4}(\s*[-–,às]+\s*\d{1,2}[:h]\d{2})?$", re.I)
# Resto de template que vazou pro texto: "{% endif %}", "{{ excerpt }}"
TEMPLATE = re.compile(r"^\{[{%].*[}%]\}$")
# Post do Instagram embutido: só sobra a legenda do botão
INSTAGRAM = re.compile(r"^(ver (esse|este) post no instagram\s*)?um post compartilhado por .{1,80}\(@[\w.]+\)$", re.I)
# Chamadas e avisos. Só valem em parágrafo curto, pra não apagar uma
# notícia que fale de cookies, newsletter ou WhatsApp.
CHAMADAS = re.compile(
    r"\bcookies?\b|pol[ií]tica de privacidade"
    r"|\b(siga|acompanhe|inscreva-se)\b.{0,60}\b(whatsapp|instagram|telegram|google (news|not[ií]cias)|youtube|tiktok|facebook|twitter|threads|bluesky)\b"
    r"|(whatsapp|telegram).{0,80}\b(siga|canal|participe|grupo)\b|\b(siga|canal|participe|grupo)\b.{0,80}(whatsapp|telegram)"
    r"|participe do (nosso )?canal|inscreva-se|newsletter"
    r"|\breceba\b.{0,40}\b(not[ií]cias|newsletters?|alertas)\b"
    r"|\bassine\b|contribua com|apoie o jornalismo"
    r"|(afiliad[oa]s?|parceiros)\b.{0,120}\b(comiss|porcentagem)|\b(comiss[aã]o|porcentagem)\b.{0,120}\b(afiliad|parceiros)"
    r"|adicion\w*.{0,40}tela inicial|baixe (o|nosso) app|clique aqui|\bclique e (entre|confira|saiba|acesse)\b"
    r"|bloqueador de an[uú]ncios|\badblock"
    # em inglês
    r"|\b(sign up|subscribe)\b.{0,60}\b(newsletter|our|today|free)\b|\bfollow us on\b|privacy policy|terms of (use|service)"
    r"|\bthis (article|story) (contains|may contain) affiliate|\bwe may (earn|receive) (a )?commission",
    re.I,
)
# Aviso de cookies e de bloqueador vale mesmo em parágrafo mais longo
AVISOS = re.compile(
    r"\b(usamos|utilizamos|este site (usa|utiliza)) cookies\b|browser extensions? seems? to be blocking"
    r"|\bwe use cookies\b|\bthis (site|website) uses cookies\b",
    re.I,
)
AVISO_MAX_CARACTERES = 600
CHAMADA_MAX_CARACTERES = 280
# Emoji de chamada no começo ("➡️ Siga...", "📲 Receba...")
EMOJI_DE_CHAMADA = re.compile(r"^(➡️|➡|📲|👉|📢|🔔|📱)")
# Rodapé do WordPress no fim do texto (às vezes na mesma linha do resumo)
RODAPE_WORDPRESS = re.compile(
    r"\s*\b(The post|O post)\b.{1,400}?\b(appeared first on|apareceu primeiro em)\b[^\n]{0,120}", re.I
)

# Trecho repetido em várias matérias da mesma fonte é do site, não da
# notícia. Calibrado com os dados de 07/10: pedido de assinatura, bio de
# autor e lista de outras matérias aparecem em 8% ou mais das matérias
# da fonte; parágrafo de contexto reaproveitado em matérias da mesma
# série (apuração da eleição, elenco de uma série) fica abaixo de 8%.
# Linha curta sem pontuação pode ser intertítulo de verdade ("Design",
# "Prováveis escalações", que aparecem em toda review ou pré-jogo): só
# sai se estiver em 15% ou mais (aí é menu: "Esporte", "Temas").
MINIMO_REPETICOES = 3
PROPORCAO_MINIMA = 0.08
PROPORCAO_MINIMA_TITULO = 0.15
AMOSTRA_MINIMA = 30               # fonte com menos matérias: só as regras fixas
TAMANHO_MAXIMO_REPETIDO = 400
# Crédito se repete por natureza e não é lixo: nunca conta como repetido
CREDITO = re.compile(
    r"^\*?(com (informa[cç][oõ]es d[aoe]s?\b|afp\b|reuters\b|ag[eê]ncias?\b|estad[aã]o\b)"
    r"|conte[uú]do distribu[ií]do por\b|este texto foi publicado originalmente\b)",
    re.I,
)


def _linha(texto):
    return " ".join(texto.split())


def _fora(el):
    palavras = f"{el.get('class', '')} {el.get('id', '')}".lower().split()
    return any(p in ("ad", "ads") or p.startswith(PREFIXOS_FORA) for p in palavras)


def html_para_texto(conteudo):
    """HTML (ou texto puro) -> um parágrafo por linha, sem o que não é matéria."""
    if not conteudo or not conteudo.strip():
        return ""
    if "<" not in conteudo:
        linhas = (_linha(l) for l in html.unescape(conteudo).split("\n"))
        return "\n".join(l for l in linhas if l)
    try:
        raiz = lhtml.fragment_fromstring(conteudo, create_parent="div")
    except (etree.ParserError, ValueError):
        return ""

    for el in list(raiz.iter()):
        if not isinstance(el.tag, str):  # comentário de HTML
            continue
        if el.tag.lower() in TAGS_FORA or _fora(el):
            el.drop_tree()  # some com o elemento e o que tem dentro, mantém o texto depois dele

    for el in raiz.iter():
        if not isinstance(el.tag, str):
            continue
        tag = el.tag.lower()
        if tag == "br":
            el.tail = "\n" + (el.tail or "")
        elif tag in TAGS_BLOCO:
            el.text = ("\n- " if tag == "li" else "\n") + (el.text or "")
            el.tail = "\n" + (el.tail or "")

    linhas = (_linha(l) for l in raiz.text_content().split("\n"))
    return "\n".join(_juntar_quebras([l for l in linhas if l and l != "-"]))


def _juntar_quebras(linhas):
    """<br> no meio da frase ("8% do capital total e votante<br>da Azul."):
    linha que começa em minúscula continua a anterior, se a anterior não
    terminou a frase."""
    saida = []
    for linha in linhas:
        if saida and linha[0].islower() and not re.search(r"[.!?:;…\"”)]$", saida[-1]) and not saida[-1].startswith("- "):
            saida[-1] += " " + linha
        else:
            saida.append(linha)
    return saida


def eh_lixo(paragrafo):
    p = paragrafo.strip()
    if any(r.match(p) for r in (ROTULOS, DATAS_DE_PUBLICACAO, DATA_SOLTA, TEMPLATE, INSTAGRAM)):
        return True
    if len(p) <= AVISO_MAX_CARACTERES and AVISOS.search(p):
        return True
    return len(p) <= CHAMADA_MAX_CARACTERES and bool(CHAMADAS.search(p) or EMOJI_DE_CHAMADA.match(p))


def consertar_acentos(texto):
    """"simbÃ³lico" -> "simbólico": texto em UTF-8 que alguém leu como
    Latin-1 (página sem a codificação no cabeçalho, ou o próprio feed do
    site já vem assim). Não mexe em texto que já está certo."""
    return ftfy.fix_encoding(texto) if texto else texto


def limpar_texto(texto, repetidos=frozenset()):
    """Conserta acentos e tira os parágrafos de lixo, os repetidos do site
    e duplicatas."""
    if not texto:
        return texto
    texto = RODAPE_WORDPRESS.sub("", consertar_acentos(texto))
    saida, vistos = [], set()
    for linha in texto.split("\n"):
        p = _linha(linha)
        if not p or p in vistos or p in repetidos or eh_lixo(p):
            continue
        vistos.add(p)
        saida.append(p)
    return "\n".join(saida)


def texto_do_rss(entry):
    """O texto mais completo que o feed manda, limpo. Muitos feeds
    (WordPress) põem a matéria inteira no content:encoded e só uma frase
    no description; outros (G1, TechTudo) põem tudo no description."""
    candidatos = [c.get("value", "") for c in entry.get("content") or []]
    candidatos.append(entry.get("summary", ""))
    textos = [limpar_texto(html_para_texto(c)) for c in candidatos if c]
    melhor = max(textos, key=len, default="")
    return melhor[:MAX_CARACTERES] or None


def texto_da_pagina(pagina_html):
    """pagina_html: de preferência os bytes da resposta (resp.content), pro
    trafilatura descobrir a codificação pela própria página. Com resp.text,
    o requests assume Latin-1 quando o servidor não diz a codificação, e
    "simbólico" vira "simbÃ³lico"."""
    texto = trafilatura.extract(
        pagina_html, include_comments=False, include_tables=False, favor_precision=True
    )
    return limpar_texto(texto or "")[:MAX_CARACTERES] or None


def eh_repetido(trecho, vezes, total):
    """Trecho que aparece em `vezes` das `total` matérias recentes de uma
    fonte é do site (pedido de assinatura, bio do autor, links pra outras
    matérias), não da notícia?"""
    if total < AMOSTRA_MINIMA or vezes < MINIMO_REPETICOES or len(trecho) > TAMANHO_MAXIMO_REPETIDO:
        return False
    if CREDITO.match(trecho):
        return False
    titulo = len(trecho) < 40 and not re.search(r"[.!?:;…]$", trecho)
    return vezes >= (PROPORCAO_MINIMA_TITULO if titulo else PROPORCAO_MINIMA) * total
