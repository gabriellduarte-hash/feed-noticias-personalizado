"""
Coleta as notícias das fontes do catálogo (feed_catalog) pra aba
"Explorar" do hub, gravando em catalog_articles (sql/020).

Diferente do coletar.py:
  - lê de feed_catalog (todas as fontes do catálogo), não de sources;
  - grava em catalog_articles, que é compartilhada entre todos os usuários;
  - não faz scraping nem resumo por IA: o catálogo só tem feeds RSS, e
    resumir dezenas de fontes todo dia custaria caro sem necessidade;
  - guarda só os últimos DIAS_GUARDADOS dias (é vitrine, não arquivo).

Uso (de dentro de coletor/):
    python coletar_catalogo.py            # coleta e grava
    python coletar_catalogo.py --simular  # só baixa e mostra, não grava nada
"""
import argparse
import time

import feedparser
import requests
from psycopg2.extras import RealDictCursor

from coletar import USER_AGENT, extrair_imagem_rss, limpar_html
from db import get_connection

PAUSA_ENTRE_FONTES_SEGUNDOS = 1.0
MAX_POR_FONTE = 20          # as mais recentes de cada feed, por rodada
MAX_CARACTERES_TEXTO = 4000  # o resumo do RSS; não precisa do texto inteiro
DIAS_GUARDADOS = 14


def buscar_catalogo(conn):
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute("select id, name, url from feed_catalog order by name")
        return cur.fetchall()


def baixar_feed(url):
    """Baixa com o nosso User-Agent (o feedparser.parse(url) usaria o dele,
    que alguns sites bloqueiam) e entrega o conteúdo pro feedparser."""
    resposta = requests.get(url, headers={"User-Agent": USER_AGENT}, timeout=15)
    resposta.raise_for_status()
    return feedparser.parse(resposta.content)


def extrair_noticias(feed):
    noticias = []
    for entry in feed.entries[:MAX_POR_FONTE]:
        link = entry.get("link")
        if not link:
            continue
        publicado = None
        data = entry.get("published_parsed") or entry.get("updated_parsed")
        if data:
            publicado = time.strftime("%Y-%m-%d %H:%M:%S+00", data)
        noticias.append({
            "title": limpar_html(entry.get("title", "(sem título)")),
            "url": link,
            "content": limpar_html(entry.get("summary", ""))[:MAX_CARACTERES_TEXTO] or None,
            "author": entry.get("author"),
            "image_url": extrair_imagem_rss(entry),
            "published_at": publicado,
        })
    return noticias


def salvar(conn, catalog_id, noticias):
    novos = 0
    with conn.cursor() as cur:
        for n in noticias:
            cur.execute(
                """
                insert into catalog_articles
                    (catalog_id, title, url, content, author, image_url, published_at)
                values (%s, %s, %s, %s, %s, %s, %s)
                on conflict (url) do nothing
                returning id
                """,
                (catalog_id, n["title"], n["url"], n["content"], n["author"], n["image_url"], n["published_at"]),
            )
            if cur.fetchone():
                novos += 1
    conn.commit()
    return novos


def apagar_antigas(conn):
    with conn.cursor() as cur:
        cur.execute(
            "delete from catalog_articles where collected_at < now() - make_interval(days => %s)",
            (DIAS_GUARDADOS,),
        )
        apagadas = cur.rowcount
    conn.commit()
    return apagadas


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--simular", action="store_true", help="baixa e mostra, sem gravar no banco")
    args = parser.parse_args()

    conn = get_connection()
    try:
        catalogo = buscar_catalogo(conn)
        print(f"{len(catalogo)} fonte(s) no catálogo.{' (simulação: nada será gravado)' if args.simular else ''}")

        total_novos = 0
        for fonte in catalogo:
            print(f"Coletando: {fonte['name']} ({fonte['url']})")
            try:
                noticias = extrair_noticias(baixar_feed(fonte["url"]))
            except Exception as erro:
                # uma fonte fora do ar não pode derrubar a coleta das outras
                print(f"  erro: {erro}")
                continue

            if args.simular:
                com_imagem = sum(1 for n in noticias if n["image_url"])
                print(f"  {len(noticias)} notícia(s), {com_imagem} com imagem")
            else:
                novos = salvar(conn, fonte["id"], noticias)
                total_novos += novos
                print(f"  {len(noticias)} notícia(s) encontradas, {novos} nova(s)")
            time.sleep(PAUSA_ENTRE_FONTES_SEGUNDOS)

        if not args.simular:
            apagadas = apagar_antigas(conn)
            print(f"\n{total_novos} notícia(s) nova(s); {apagadas} com mais de {DIAS_GUARDADOS} dias apagada(s).")
    finally:
        conn.close()


if __name__ == "__main__":
    main()
