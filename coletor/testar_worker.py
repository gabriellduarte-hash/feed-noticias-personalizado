"""
Testa o Worker do Cloudflare (worker/leitor.js) com os sites que barram o
GitHub e a Vercel: pra cada um, baixa o feed e a página de uma notícia
pelo Worker e diz se veio (e com quanto texto). Não grava nada.

Precisa no .env: WORKER_URL (https://....workers.dev) e WORKER_SECRET (a
mesma senha do SEGREDO no Worker).

Uso (de dentro de coletor/):
    python testar_worker.py                     # todos os sites marcados pro hub, mais o Adrenaline
    python testar_worker.py https://www.adrenaline.com.br/feed/   # só esse feed
"""
import os
import sys

import feedparser
import requests
from dotenv import load_dotenv

from db import get_connection
from texto import texto_da_pagina, texto_do_rss

load_dotenv()

ADRENALINE = "https://www.adrenaline.com.br/feed/"


def pelo_worker(url):
    return requests.get(
        os.environ["WORKER_URL"].rstrip("/") + "/",
        params={"url": url},
        headers={"Authorization": f"Bearer {os.environ['WORKER_SECRET']}"},
        timeout=40,
    )


def sites_barrados():
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                select distinct url from (
                  select url from feeds where coletar_pelo_hub
                  union select url from feed_catalog where coletar_pelo_hub
                ) x order by url
                """
            )
            urls = [r[0] for r in cur.fetchall()]
        conn.commit()
    finally:
        conn.close()
    return sorted(set(urls) | {ADRENALINE})


def testar(url_do_feed):
    try:
        resp = pelo_worker(url_do_feed)
    except requests.RequestException as erro:
        return f"FALHOU  feed: {type(erro).__name__}"
    if resp.status_code != 200:
        return f"BARRADO feed: {resp.status_code} {resp.text[:60]!r}"
    feed = feedparser.parse(resp.content)
    if not feed.entries:
        return f"VAZIO   feed: {len(resp.content)} bytes, nenhum item (página de desafio?)"
    item = feed.entries[0]
    texto_rss = len(texto_do_rss(item) or "")
    try:
        pagina = pelo_worker(item.get("link"))
        texto_pagina = len(texto_da_pagina(pagina.content) or "") if pagina.status_code == 200 else 0
        estado_pagina = f"página {pagina.status_code}, {texto_pagina} caracteres"
    except requests.RequestException as erro:
        estado_pagina = f"página falhou ({type(erro).__name__})"
    return f"OK      feed: {len(feed.entries)} itens, texto no RSS {texto_rss} | {estado_pagina}"


def main():
    if not os.environ.get("WORKER_URL") or not os.environ.get("WORKER_SECRET"):
        sys.exit("Falta WORKER_URL e/ou WORKER_SECRET no .env")
    urls = sys.argv[1:] or sites_barrados()
    for url in urls:
        print(f"{url[:60]:60}  {testar(url)}")


if __name__ == "__main__":
    main()
