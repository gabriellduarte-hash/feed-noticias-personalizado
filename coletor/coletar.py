"""
Lê as fontes cadastradas em `sources`, busca conteúdo novo (RSS, sitemap
de notícias ou scraping bruto) e insere em `articles`. A deduplicação é feita pelo
próprio banco, via `on conflict (url) do nothing` (a constraint unique
que já existe em articles.url).
"""
import html
import re
import time
import urllib.robotparser as robotparser
from urllib.parse import urlparse

import feedparser
import requests
import trafilatura
from psycopg2.extras import RealDictCursor

from alternativas import eh_google_news, ler_sitemap, limpar_titulo_google_news
from db import get_connection

USER_AGENT = "FeedNoticiasBot/0.1 (uso pessoal - estudo)"
PAUSA_ENTRE_FONTES_SEGUNDOS = 1.5
MAX_MATERIAS_SITEMAP = 10  # de cada sitemap, baixa o texto só das mais recentes
REGEX_PRIMEIRA_IMG = re.compile(r'<img[^>]+src="([^"]+)"', re.IGNORECASE)
REGEX_TAG_HTML = re.compile(r"<[^>]+>")


def limpar_html(texto):
    """Tira tags HTML e desfaz entidades (&#8217; etc.) — alguns feeds
    (ex.: G1) mandam o resumo com HTML de verdade dentro (<img>, <br>),
    diferente de outros que já vêm em texto puro."""
    sem_tags = REGEX_TAG_HTML.sub(" ", texto or "")
    texto_limpo = html.unescape(sem_tags)
    return " ".join(texto_limpo.split())


def buscar_fontes(conn):
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute("select id, topic_id, url, type from sources")
        return cur.fetchall()


def extrair_imagem_rss(entry):
    """Tenta achar uma capa pro artigo, em ordem de confiabilidade.

    Nem todo feed expõe isso da mesma forma — testado na prática com
    nossas próprias fontes, media_thumbnail/media_content/enclosures
    vieram vazios no feed que já usamos, por isso o fallback final
    (primeira <img> dentro do HTML do resumo).
    """
    thumbs = entry.get("media_thumbnail")
    if thumbs:
        return thumbs[0].get("url")

    for media in entry.get("media_content", []) or []:
        if (media.get("medium") == "image") or (media.get("type", "").startswith("image/")):
            return media.get("url")

    for enclosure in entry.get("enclosures", []) or []:
        if enclosure.get("type", "").startswith("image/"):
            return enclosure.get("href")

    match = REGEX_PRIMEIRA_IMG.search(entry.get("summary", "") or "")
    return match.group(1) if match else None


def coletar_rss(source):
    feed = feedparser.parse(source["url"])
    google_news = eh_google_news(source["url"])
    artigos = []
    for entry in feed.entries:
        publicado = None
        if getattr(entry, "published_parsed", None):
            publicado = time.strftime("%Y-%m-%d %H:%M:%S", entry.published_parsed)
        titulo = limpar_html(entry.get("title", "(sem título)"))
        artigos.append({
            # Google Notícias: tira o " - Nome do site" do título, e o
            # "resumo" dele é só um link repetindo o título, então descarta
            "title": limpar_titulo_google_news(titulo) if google_news else titulo,
            "url": entry.get("link"),
            "content": None if google_news else limpar_html(entry.get("summary", "")),
            "published_at": publicado,
            "author": entry.get("author"),  # nem todo feed informa; fica None se não tiver
            "image_url": extrair_imagem_rss(entry),
        })
    return artigos


def pode_coletar(url):
    """Confere o robots.txt do domínio antes de fazer scraping bruto.

    Não usamos rp.read() porque ele busca o robots.txt com o user-agent
    padrão do urllib ("Python-urllib/x.y"), que alguns sites (ex.: a
    Wikipédia) bloqueiam com 403 — e o RobotFileParser reage a isso
    assumindo "tudo bloqueado", mesmo sem ter lido nenhuma regra real.
    Buscamos o texto nós mesmos, com o nosso USER_AGENT de verdade, e
    entregamos pro parser via rp.parse().
    """
    parsed = urlparse(url)
    robots_url = f"{parsed.scheme}://{parsed.netloc}/robots.txt"
    rp = robotparser.RobotFileParser()
    try:
        resp = requests.get(robots_url, headers={"User-Agent": USER_AGENT}, timeout=10)
        resp.raise_for_status()
        rp.parse(resp.text.splitlines())
        return rp.can_fetch(USER_AGENT, url)
    except Exception:
        # robots.txt inacessível: para um projeto pessoal de baixo volume,
        # seguimos em frente em vez de bloquear a coleta.
        return True


def coletar_scrape(source):
    url = source["url"]
    if not pode_coletar(url):
        print(f"  robots.txt bloqueia coleta de {url}, pulando.")
        return []

    resp = requests.get(url, headers={"User-Agent": USER_AGENT}, timeout=10)
    resp.raise_for_status()

    texto = trafilatura.extract(resp.text)
    if not texto:
        return []

    metadata = trafilatura.extract_metadata(resp.text)
    titulo = metadata.title if metadata and metadata.title else url
    autor = metadata.author if metadata and metadata.author else None
    imagem = metadata.image if metadata and metadata.image else None

    return [{
        "title": titulo,
        "url": url,
        "content": texto,
        "published_at": None,
        "author": autor,
        "image_url": imagem,
    }]


def coletar_sitemap(source, conn):
    """Fonte sem RSS, lida pelo sitemap de notícias (ver alternativas.py).
    O sitemap só dá link, título, data e às vezes a imagem; o texto vem
    de baixar cada matéria nova com o trafilatura, como no scrape."""
    itens = ler_sitemap(source["url"], USER_AGENT, limite=MAX_MATERIAS_SITEMAP)
    with conn.cursor() as cur:
        cur.execute("select url from articles where url = any(%s)", ([i["url"] for i in itens],))
        ja_salvas = {linha[0] for linha in cur.fetchall()}

    artigos = []
    for item in itens:
        if item["url"] in ja_salvas:
            continue
        texto, imagem, autor = None, item["image_url"], None
        if pode_coletar(item["url"]):
            try:
                resp = requests.get(item["url"], headers={"User-Agent": USER_AGENT}, timeout=10)
                resp.raise_for_status()
                texto = trafilatura.extract(resp.text)
                metadata = trafilatura.extract_metadata(resp.text)
                if metadata:
                    imagem = imagem or metadata.image
                    autor = metadata.author
            except Exception as erro:
                print(f"  não deu pra baixar {item['url']}: {erro}")
            time.sleep(1)
        artigos.append({
            "title": item["title"],
            "url": item["url"],
            "content": texto,
            "published_at": item["published_at"],
            "author": autor,
            "image_url": imagem,
        })
    return artigos


def salvar_artigos(conn, source_id, artigos):
    novos = 0
    with conn.cursor() as cur:
        for artigo in artigos:
            if not artigo.get("url"):
                continue
            cur.execute(
                """
                insert into articles (source_id, title, url, content, published_at, author, image_url)
                values (%s, %s, %s, %s, %s, %s, %s)
                on conflict (url) do nothing
                returning id
                """,
                (
                    source_id,
                    artigo["title"],
                    artigo["url"],
                    artigo["content"],
                    artigo["published_at"],
                    artigo.get("author"),
                    artigo.get("image_url"),
                ),
            )
            if cur.fetchone():
                novos += 1
    conn.commit()
    return novos


def main():
    conn = get_connection()
    try:
        fontes = buscar_fontes(conn)
        print(f"{len(fontes)} fonte(s) cadastrada(s).")

        for source in fontes:
            print(f"Coletando: {source['url']} ({source['type']})")
            try:
                if source["type"] == "rss":
                    artigos = coletar_rss(source)
                elif source["type"] == "sitemap":
                    artigos = coletar_sitemap(source, conn)
                else:
                    artigos = coletar_scrape(source)
            except Exception as erro:
                print(f"  erro ao coletar {source['url']}: {erro}")
                continue

            novos = salvar_artigos(conn, source["id"], artigos)
            print(f"  {len(artigos)} artigo(s) encontrados, {novos} novo(s) salvos.")

            time.sleep(PAUSA_ENTRE_FONTES_SEGUNDOS)
    finally:
        conn.close()


if __name__ == "__main__":
    main()
