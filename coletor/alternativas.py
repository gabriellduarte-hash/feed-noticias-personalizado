"""
Leitura de fontes que não têm RSS, usada pelo coletar.py, pelo
coletar_catalogo.py e pelo catalogo/catalogar.py.

1. Sitemap de notícias: o XML que os sites publicam pro Google Notícias
   (<news:title>, <news:publication_date>, <image:loc>). Pode vir direto
   (<urlset>) ou como índice que aponta pra outros sitemaps
   (<sitemapindex>, ex.: BBC).
   Quando o sitemap é do site inteiro e só interessa uma seção, o
   filtro vai no próprio endereço salvo, como fragmento:
       https://www.bbc.com/sitemaps/https-index-com-news.xml#caminho=/portuguese
   O fragmento (#...) nunca é enviado ao servidor; só este código lê.

2. RSS de busca do Google Notícias (news.google.com/rss/search?q=site:...):
   é RSS comum, mas o título vem com " - Nome do site" no fim, o link
   passa por um redirecionamento do Google, e o "resumo" é só um link
   repetindo o título. As funções abaixo limpam isso.
"""
import re
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from urllib.parse import parse_qs, quote, urldefrag, urlparse

import requests

NS = {
    "sm": "http://www.sitemaps.org/schemas/sitemap/0.9",
    "news": "http://www.google.com/schemas/sitemap-news/0.9",
    "image": "http://www.google.com/schemas/sitemap-image/1.1",
}
MAX_SITEMAPS_FILHOS = 3            # de um índice, lê só os mais recentes
MAX_BYTES_SITEMAP = 15 * 1024 * 1024  # sitemaps podem ser enormes; acima disso, ignora


# ---------------------------------------------------------------- sitemap

def _texto(no, caminho):
    achado = no.find(caminho, NS)
    return achado.text.strip() if achado is not None and achado.text else None


def _data(texto):
    if not texto:
        return None
    try:
        data = datetime.fromisoformat(texto.replace("Z", "+00:00"))
    except ValueError:
        return None
    # sem fuso: assume UTC, pra poder comparar com datas que têm fuso
    return data if data.tzinfo else data.replace(tzinfo=timezone.utc)


def separar_filtro(url):
    """'...xml#caminho=/portuguese' -> ('...xml', '/portuguese')."""
    endereco, fragmento = urldefrag(url)
    return endereco, parse_qs(fragmento).get("caminho", [None])[0]


def _baixar_xml(url, user_agent):
    resposta = requests.get(url, headers={"User-Agent": user_agent}, timeout=15)
    resposta.raise_for_status()
    if len(resposta.content) > MAX_BYTES_SITEMAP:
        raise ValueError("sitemap grande demais")
    return ET.fromstring(resposta.content)


def _ler(url, user_agent, profundidade=0):
    raiz = _baixar_xml(url, user_agent)
    if raiz.tag.endswith("sitemapindex"):
        if profundidade >= 1:  # índice dentro de índice: não segue
            return []
        filhos = [
            (_texto(s, "sm:loc"), _texto(s, "sm:lastmod") or "")
            for s in raiz.findall("sm:sitemap", NS)
        ]
        filhos = sorted((f for f in filhos if f[0]), key=lambda f: f[1], reverse=True)
        itens = []
        for endereco, _ in filhos[:MAX_SITEMAPS_FILHOS]:
            try:
                itens += _ler(endereco, user_agent, profundidade + 1)
            except Exception:
                continue  # um filho quebrado não invalida os outros
        return itens

    itens = []
    for u in raiz.findall("sm:url", NS):
        link = _texto(u, "sm:loc")
        titulo = _texto(u, "news:news/news:title")
        if not link or not titulo:  # sitemap comum (sem news:) não serve
            continue
        itens.append({
            "url": link,
            "title": titulo,
            "published_at": _data(_texto(u, "news:news/news:publication_date") or _texto(u, "sm:lastmod")),
            "image_url": _texto(u, "image:image/image:loc"),
        })
    return itens


def ler_sitemap(url, user_agent, limite=30):
    """Notícias de um sitemap, da mais nova pra mais antiga."""
    endereco, caminho = separar_filtro(url)
    itens = _ler(endereco, user_agent)
    if caminho:
        itens = [i for i in itens if urlparse(i["url"]).path.startswith(caminho)]
    vistos = set()
    unicos = [i for i in itens if not (i["url"] in vistos or vistos.add(i["url"]))]
    unicos.sort(key=lambda i: i["published_at"].timestamp() if i["published_at"] else 0, reverse=True)
    return unicos[:limite]


def sitemaps_do_robots(url_site, user_agent):
    """Sitemaps declarados no robots.txt, com os de notícia primeiro."""
    p = urlparse(url_site)
    resposta = requests.get(f"{p.scheme}://{p.netloc}/robots.txt", headers={"User-Agent": user_agent}, timeout=10)
    resposta.raise_for_status()
    declarados = [
        linha.split(":", 1)[1].strip()
        for linha in resposta.text.splitlines()
        if linha.lower().startswith("sitemap:")
    ]
    de_noticia = [s for s in declarados if re.search(r"news|noticia", s, re.IGNORECASE)]
    comuns = [f"{p.scheme}://{p.netloc}{c}" for c in ("/news-sitemap.xml", "/sitemap-news.xml", "/sitemap_news.xml")]
    return list(dict.fromkeys(de_noticia + comuns))


# ---------------------------------------------------------- Google Notícias

# Edição do Google Notícias por idioma: a de português do Brasil acha
# pouco de sites em inglês, e vice-versa
EDICOES_GOOGLE_NEWS = {"pt": "hl=pt-BR&gl=BR&ceid=BR:pt-419", "en": "hl=en-US&gl=US&ceid=US:en"}


def url_google_news(url_site, idioma="pt"):
    """RSS de busca do Google Notícias restrito a um site (e seção, se houver)."""
    p = urlparse(url_site)
    alvo = p.netloc.removeprefix("www.") + p.path.rstrip("/")
    edicao = EDICOES_GOOGLE_NEWS.get(idioma, EDICOES_GOOGLE_NEWS["pt"])
    return f"https://news.google.com/rss/search?q={quote('site:' + alvo)}&{edicao}"


def eh_google_news(url):
    return urlparse(url).netloc == "news.google.com"


def entradas_do_site(entradas, url_site):
    """Do RSS do Google Notícias, só as notícias que são mesmo do site
    pedido (pelo <source href> de cada item). A busca "site:" às vezes
    traz notícias de outros sites que citam o domínio, e de subdomínios."""
    site = urlparse(url_site).netloc.lower().removeprefix("www.")
    # domínio igual (ignorando "www."): a busca "site:" também traz
    # subdomínios, como o fórum forum.adrenaline.com.br
    return [
        e for e in entradas
        if urlparse(e.get("source", {}).get("href", "")).netloc.lower().removeprefix("www.") == site
    ]


def limpar_titulo_google_news(titulo):
    """'Manchete qualquer - ge' -> 'Manchete qualquer'."""
    return re.sub(r"\s+-\s+[^-]{1,60}$", "", titulo or "").strip() or titulo
