"""
Coleta as notícias das fontes do catálogo (feed_catalog) pra aba
"Explorar" do hub, gravando em catalog_articles (sql/020).

Diferente do coletar.py:
  - lê de feed_catalog, não de sources, e só as fontes da vitrine (sql/031):
    o resto do catálogo é só mapa, coletado quando alguém segue;
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

from urllib.parse import urlparse

from alternativas import eh_google_news, entradas_do_site, ler_sitemap, limpar_titulo_google_news, url_google_news
from coletar import USER_AGENT, extrair_imagem_rss, limpar_html
from texto import texto_do_rss
from db import get_connection

PAUSA_ENTRE_FONTES_SEGUNDOS = 1.0
MAX_POR_FONTE = 20          # as mais recentes de cada feed, por rodada
DIAS_GUARDADOS = 14


def buscar_catalogo(conn):
    """Só as fontes da vitrine (sql/031). O resto do catálogo é mapa: só é
    coletado quando alguém segue (aí vira fonte normal, no coletar.py)."""
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute("select id, name, url, kind from feed_catalog where vitrine order by name")
        return cur.fetchall()


def baixar_feed(url):
    """Baixa com o nosso User-Agent (o feedparser.parse(url) usaria o dele,
    que alguns sites bloqueiam) e entrega o conteúdo pro feedparser."""
    resposta = requests.get(url, headers={"User-Agent": USER_AGENT}, timeout=15)
    resposta.raise_for_status()
    return feedparser.parse(resposta.content)


def noticias_pelo_google_news(url_feed):
    """Plano B quando o RSS do site falha. Alguns sites (ex.: Adrenaline,
    PLACAR) respondem 403 pras máquinas do GitHub Actions, mas não pra
    uma conexão doméstica: bloqueiam servidores de nuvem. O Google
    Notícias do mesmo site não depende do site responder."""
    p = urlparse(url_feed)
    site = f"{p.scheme}://{p.netloc}"
    feed = baixar_feed(url_google_news(site))
    return extrair_noticias(entradas_do_site(feed.entries, site), google_news=True)


def coletar_fonte(fonte):
    if fonte["kind"] == "sitemap":
        return noticias_do_sitemap(fonte["url"]), None
    google_news = eh_google_news(fonte["url"])
    try:
        noticias = extrair_noticias(baixar_feed(fonte["url"]).entries, google_news)
        motivo = None if noticias else "RSS veio vazio"
    except Exception as erro:
        noticias, motivo = [], str(erro)
    if noticias or google_news:
        return noticias, motivo
    print(f"  RSS falhou ({motivo}); tentando pelo Google Notícias")
    return noticias_pelo_google_news(fonte["url"]), "via Google Notícias"


def noticias_do_sitemap(url):
    """Só o que o sitemap traz (título, data, imagem): não baixa cada
    matéria, porque aqui são dezenas de fontes por dia, pra uma vitrine."""
    return [
        {
            "title": i["title"],
            "url": i["url"],
            "content": None,
            "author": None,
            "image_url": i["image_url"],
            "published_at": i["published_at"],
        }
        for i in ler_sitemap(url, USER_AGENT, limite=MAX_POR_FONTE)
    ]


def extrair_noticias(entradas, google_news=False):
    noticias = []
    for entry in entradas[:MAX_POR_FONTE]:
        link = entry.get("link")
        if not link:
            continue
        publicado = None
        data = entry.get("published_parsed") or entry.get("updated_parsed")
        if data:
            publicado = time.strftime("%Y-%m-%d %H:%M:%S+00", data)
        titulo = limpar_html(entry.get("title", "(sem título)"))
        noticias.append({
            "title": limpar_titulo_google_news(titulo) if google_news else titulo,
            "url": link,
            # no Google Notícias o "resumo" é só um link repetindo o título
            "content": None if google_news else texto_do_rss(entry),
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
        conn.commit()  # fecha a leitura antes de baixar os feeds
        print(f"{len(catalogo)} fonte(s) no catálogo.{' (simulação: nada será gravado)' if args.simular else ''}")

        total_novos = 0
        for fonte in catalogo:
            print(f"Coletando: {fonte['name']} ({fonte['url']})")
            try:
                noticias, _ = coletar_fonte(fonte)
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
