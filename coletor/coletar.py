"""
Lê as fontes cadastradas em `sources`, busca conteúdo novo (RSS ou
scraping bruto) e insere em `articles`. A deduplicação é feita pelo
próprio banco, via `on conflict (url) do nothing` (a constraint unique
que já existe em articles.url).
"""
import time
import urllib.robotparser as robotparser
from urllib.parse import urlparse

import feedparser
import requests
import trafilatura
from psycopg2.extras import RealDictCursor

from db import get_connection

USER_AGENT = "FeedNoticiasBot/0.1 (uso pessoal - estudo)"
PAUSA_ENTRE_FONTES_SEGUNDOS = 1.5


def buscar_fontes(conn):
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute("select id, topic_id, url, type from sources")
        return cur.fetchall()


def coletar_rss(source):
    feed = feedparser.parse(source["url"])
    artigos = []
    for entry in feed.entries:
        publicado = None
        if getattr(entry, "published_parsed", None):
            publicado = time.strftime("%Y-%m-%d %H:%M:%S", entry.published_parsed)
        artigos.append({
            "title": entry.get("title", "(sem título)"),
            "url": entry.get("link"),
            "content": entry.get("summary", ""),
            "published_at": publicado,
            "author": entry.get("author"),  # nem todo feed informa; fica None se não tiver
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

    return [{
        "title": titulo,
        "url": url,
        "content": texto,
        "published_at": None,
        "author": autor,
    }]


def salvar_artigos(conn, source_id, artigos):
    novos = 0
    with conn.cursor() as cur:
        for artigo in artigos:
            if not artigo.get("url"):
                continue
            cur.execute(
                """
                insert into articles (source_id, title, url, content, published_at, author)
                values (%s, %s, %s, %s, %s, %s)
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
