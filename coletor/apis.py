"""
Sites com API pública de notícias: o mesmo conteúdo do site, em JSON, que
os apps deles usam. Pra esses, o coletor não lê o RSS nem abre a página:
uma chamada traz as últimas notícias já com texto completo, foto e autor.

ESPN (espn.com.br e espn.com): o site barra as máquinas do GitHub (por
isso ela ia pro hub, na Vercel), e o RSS dela não traz nem resumo nem
foto. A API de conteúdo (content.core.api.espn.com) entrega tudo. Matéria
"premium" (paga) fica só com título e resumo, como no resto do Daily
Paper. Se a API também barrar o GitHub, o coletar.py marca a fonte pro
hub de novo (o caminho de antes).

Pra pôr outro site aqui: uma entrada em SITES, com como reconhecer o RSS
dele, a chamada da lista e a de uma notícia só.
"""
import re
from datetime import datetime

import requests

from texto import html_para_texto, limpar_texto

TEMPO_LIMITE = 20
MAX_NOTICIAS = 50

ESPN_API = "https://content.core.api.espn.com/v1/sports"
# Tags que a ESPN põe no meio do texto no lugar de vídeos, fotos e "veja
# também" (<video1>, <photo2>, <alsosee>, <inline1>)
_MARCADORES_ESPN = re.compile(r"<(video|photo|alsosee|inline|pullquote)\d*\s*/?>", re.I)


def _espn_idioma(url):
    """(lang, region) pelo site: espn.com.br em português, espn.com em inglês."""
    return ("pt", "br") if ".com.br" in url else ("en", "us")


def _espn_lista(url_do_rss):
    lang, region = _espn_idioma(url_do_rss)
    esporte = "/soccer" if "/soccer/" in url_do_rss else ""
    return f"{ESPN_API}{esporte}/news?lang={lang}&region={region}&limit={MAX_NOTICIAS}"


def _espn_noticia(url):
    """A chamada de uma notícia só, pelo id no link (.../artigo/_/id/17405082/...)."""
    achado = re.search(r"/_/id/(\d+)", url)
    if not achado:
        return None
    lang, region = _espn_idioma(url)
    return f"{ESPN_API}/news/{achado.group(1)}?lang={lang}&region={region}"


SITES = [
    {
        "nome": "ESPN",
        "rss": re.compile(r"^https?://(www\.)?espn\.com(\.br)?/(espn/)?rss", re.I),
        "pagina": re.compile(r"^https?://(www\.)?espn\.com(\.br)?/.+/_/id/\d+", re.I),
        "lista": _espn_lista,
        "noticia": _espn_noticia,
    },
]


def _site_do_rss(url):
    return next((s for s in SITES if s["rss"].match(url or "")), None)


def _site_da_pagina(url):
    return next((s for s in SITES if s["pagina"].match(url or "")), None)


def tem_api(url_do_feed):
    """O feed é de um site que o coletor lê pela API?"""
    return _site_do_rss(url_do_feed) is not None


def _baixar(url, user_agent):
    resposta = requests.get(url, headers={"User-Agent": user_agent, "Accept": "application/json"}, timeout=TEMPO_LIMITE)
    resposta.raise_for_status()
    return resposta.json()


def _data(texto):
    """'2026-10-20T18:55:10Z' -> '2026-10-20 18:55:10+00' (como o resto do coletor grava)."""
    if not texto:
        return None
    try:
        return datetime.fromisoformat(texto.replace("Z", "+00:00")).strftime("%Y-%m-%d %H:%M:%S+00")
    except ValueError:
        return None


def _imagem(item):
    imagens = item.get("images") or []
    capa = next((i for i in imagens if i.get("type") == "header"), None) or (imagens[0] if imagens else None)
    return capa.get("url") if capa else None


def _noticia(item):
    """Um item da API -> o formato que o coletor grava."""
    link = ((item.get("links") or {}).get("web") or {}).get("href")
    resumo = (item.get("description") or "").strip()
    if item.get("premium"):
        texto = resumo  # matéria paga: o texto fica no site
    else:
        texto = limpar_texto(html_para_texto(_MARCADORES_ESPN.sub("", item.get("story") or ""))) or resumo
    return {
        "title": (item.get("headline") or item.get("title") or "").strip(),
        "url": link,
        "content": texto or None,
        # "ESPN.com.br" não é autor: é o site
        "author": None if re.fullmatch(r"espn(\.com(\.br)?)?", (item.get("byline") or "").strip(), re.I) else (item.get("byline") or "").strip() or None,
        "image_url": _imagem(item),
        "published_at": _data(item.get("published")),
    }


def noticias_pela_api(url_do_feed, user_agent):
    """As últimas notícias do site pela API, no formato do coletor.
    Levanta requests.RequestException se a API falhar ou barrar."""
    site = _site_do_rss(url_do_feed)
    dados = _baixar(site["lista"](url_do_feed), user_agent)
    noticias = [_noticia(item) for item in dados.get("headlines") or []]
    return [n for n in noticias if n["url"] and n["title"]]


def tem_api_da_pagina(url):
    """A notícia (link da página) é de um site com API?"""
    return _site_da_pagina(url) is not None


def pagina_pela_api(url, user_agent):
    """Texto, imagem e autor de uma notícia pela API, no formato do
    enriquecer.extrair. None se o link não tem id que a API entenda."""
    site = _site_da_pagina(url)
    chamada = site["noticia"](url) if site else None
    if not chamada:
        return None
    itens = _baixar(chamada, user_agent).get("headlines") or []
    if not itens:
        return None
    noticia = _noticia(itens[0])
    return {"texto": noticia["content"] or "", "imagem": noticia["image_url"], "autor": noticia["author"]}
