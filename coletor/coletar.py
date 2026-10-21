"""
Lê os feeds que alguém segue (`feeds`, sql/038), busca conteúdo novo (RSS,
sitemap de notícias ou scraping bruto) e insere em `articles`. Cada feed é
coletado uma vez só, não importa quantas pessoas o sigam: quem segue vê
as notícias dele. A deduplicação é feita pelo próprio banco, via
`on conflict (feed_id, url) do nothing`.

Feed que bloqueia as máquinas do GitHub (responde 401/403/429 ou derruba a
conexão) fica marcado com coletar_pelo_hub (sql/040). Sites abertos, só
que barram servidores de nuvem. Daí em diante o feed e as páginas dele
vêm pelo Worker do Cloudflare (rede.py); sem o Worker configurado, quem
coleta é o hub, na Vercel (/api/coletar-bloqueados).

Fonte que acabou de ser seguida (ainda sem nenhum artigo): a primeira
coleta traz só as notícias das últimas 24 horas. Se não houver nenhuma
(fonte que publica pouco), traz as mais recentes, pra fonte não ficar
vazia. Daí em diante, tudo o que for novo.
"""
import argparse
import html
import re
import time
from datetime import datetime, timedelta, timezone
import urllib.robotparser as robotparser
from urllib.parse import urlparse

import feedparser
import requests
import trafilatura
from psycopg2.extras import RealDictCursor

from apis import noticias_pela_api, tem_api
from alternativas import (
    eh_google_news,
    entradas_do_site,
    eh_noticia_do_google_news,
    ler_sitemap,
    limpar_titulo_google_news,
    url_google_news,
)
from db import get_connection, resolver_feed
from manchetes import DIAS_PRA_COMPARAR, separar_repetidas
from rede import RobotsNaoDeixa, baixar, tem_worker
from texto import consertar_acentos, texto_da_pagina, texto_do_rss

USER_AGENT = "DailyPaperBot/0.1 (uso pessoal - estudo)"
PAUSA_ENTRE_FONTES_SEGUNDOS = 1.5
MAX_MATERIAS_SITEMAP = 10  # de cada sitemap, baixa o texto só das mais recentes
PRIMEIRA_COLETA_HORAS = 24
PRIMEIRA_COLETA_RESERVA = 5  # sem nada nas últimas 24h: as N mais recentes
REGEX_PRIMEIRA_IMG = re.compile(r'<img[^>]+src="([^"]+)"', re.IGNORECASE)
REGEX_TAG_HTML = re.compile(r"<[^>]+>")


def limpar_html(texto):
    """Tira tags HTML e desfaz entidades (&#8217; etc.) — alguns feeds
    (ex.: G1) mandam o resumo com HTML de verdade dentro (<img>, <br>),
    diferente de outros que já vêm em texto puro."""
    sem_tags = REGEX_TAG_HTML.sub(" ", texto or "")
    texto_limpo = consertar_acentos(html.unescape(sem_tags))
    return " ".join(texto_limpo.split())


def buscar_fontes(conn, feed_id=None, so_sem_artigos=False):
    """Os feeds que alguém segue; ou só um (--fonte); ou só os que ainda
    não têm nenhum artigo (--sem-artigos), pra acabou-de-ser-seguido.
    Feed que ninguém segue mais não é coletado. O que bloqueia o GitHub
    (coletar_pelo_hub) vem pelo Worker; sem ele, fica com o hub."""
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute(
            """
            select f.id, f.url, f.type, f.coletar_pelo_hub as pelo_worker,
                   exists (select 1 from articles a where a.feed_id = f.id) as tem_artigos
            from feeds f
            where exists (select 1 from sources s where s.feed_id = f.id)
              and (not f.coletar_pelo_hub or %(worker)s)
              and (%(feed)s::uuid is null or f.id = %(feed)s::uuid)
              and (not %(sem_artigos)s or not exists (select 1 from articles a where a.feed_id = f.id))
            """,
            {"feed": feed_id, "sem_artigos": so_sem_artigos, "worker": tem_worker()},
        )
        return cur.fetchall()


def imagem_de_destaque(html_texto):
    """A primeira <img> do HTML, só se vier ANTES do texto (a imagem de
    destaque que o WordPress põe no começo). Imagem no meio do texto
    costuma ser de outra matéria citada (a CNN Brasil põe miniaturas de
    200px de "leia também"): aí é melhor ficar sem e deixar o
    enriquecimento pegar a capa da própria página (og:image)."""
    match = REGEX_PRIMEIRA_IMG.search(html_texto or "")
    if not match:
        return None
    antes = limpar_html(html_texto[: match.start()])
    return match.group(1) if len(antes) < 20 else None


def extrair_imagem_rss(entry):
    """Tenta achar uma capa pro artigo, em ordem de confiabilidade:
    media:thumbnail, media:content, enclosure e, por último, a imagem de
    destaque do começo do texto."""
    thumbs = entry.get("media_thumbnail")
    if thumbs:
        return thumbs[0].get("url")

    for media in entry.get("media_content", []) or []:
        if (media.get("medium") == "image") or (media.get("type", "").startswith("image/")):
            return media.get("url")

    for enclosure in entry.get("enclosures", []) or []:
        if enclosure.get("type", "").startswith("image/"):
            return enclosure.get("href")

    for conteudo in [*(c.get("value", "") for c in entry.get("content") or []), entry.get("summary", "")]:
        imagem = imagem_de_destaque(conteudo)
        if imagem:
            return imagem
    return None


def baixar_feed(url, pelo_worker=False):
    """Com o nosso User-Agent: o feedparser.parse(url) usaria o dele, que
    alguns sites bloqueiam. pelo_worker: site que barra o GitHub (rede.py)."""
    resposta = baixar(url, USER_AGENT, pelo_worker)
    resposta.raise_for_status()
    return feedparser.parse(resposta.content)


def bloqueou(erro):
    """O site barrou a máquina do GitHub (e não está simplesmente fora do ar)."""
    if isinstance(erro, requests.ConnectionError):
        return True
    resposta = getattr(erro, "response", None)
    return resposta is not None and resposta.status_code in (401, 403, 429)


def coletar_rss(source):
    google_news = eh_google_news(source["url"])
    try:
        entradas = baixar_feed(source["url"], source.get("pelo_worker")).entries
    except (requests.RequestException, RobotsNaoDeixa) as erro:
        if google_news:
            raise
        print(f"  RSS falhou ({erro})")
        source["bloqueado"] = bloqueou(erro)
        entradas = []
    if not entradas and not google_news:
        # Plano B: o endereço não é um feed (ex.: salvaram a página do
        # site como RSS) ou o site bloqueia o GitHub Actions. O Google
        # Notícias do mesmo site não depende do site responder.
        p = urlparse(source["url"])
        site = f"{p.scheme}://{p.netloc}"
        print("  tentando pelo Google Notícias")
        entradas = entradas_do_site(baixar_feed(url_google_news(site)).entries, site)
        google_news = True
    if google_news:
        entradas = [e for e in entradas if eh_noticia_do_google_news(e.get("title", ""))]
    artigos = []
    for entry in entradas:
        publicado = None
        if getattr(entry, "published_parsed", None):
            publicado = time.strftime("%Y-%m-%d %H:%M:%S", entry.published_parsed)
        titulo = limpar_html(entry.get("title", "(sem título)"))
        artigos.append({
            # Google Notícias: tira o " - Nome do site" do título, e o
            # "resumo" dele é só um link repetindo o título, então descarta
            "title": limpar_titulo_google_news(titulo) if google_news else titulo,
            "url": entry.get("link"),
            "content": None if google_news else texto_do_rss(entry),
            "published_at": publicado,
            "author": entry.get("author"),  # nem todo feed informa; fica None se não tiver
            "image_url": extrair_imagem_rss(entry),
        })
    return artigos


def coletar_pela_api(source):
    """Site com API pública (apis.py, ex.: ESPN): lista, texto e foto numa
    chamada. Se a API falhar, cai no RSS (e no Google Notícias); se ela
    barrar o GitHub, a fonte vai pro hub como as outras."""
    try:
        return noticias_pela_api(source["url"], USER_AGENT)
    except (requests.RequestException, ValueError) as erro:
        print(f"  API falhou ({erro}); tentando o RSS")
        if bloqueou(erro):
            source["bloqueado"] = True
        return coletar_rss(source)


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
        resp = baixar(robots_url, USER_AGENT, timeout=10)
        resp.raise_for_status()
        rp.parse(resp.text.splitlines())
        return rp.can_fetch(USER_AGENT, url)
    except Exception:
        # robots.txt inacessível: para um projeto pessoal de baixo volume,
        # seguimos em frente em vez de bloquear a coleta.
        return True


def coletar_scrape(source):
    url = source["url"]
    # pelo Worker, quem confere o robots.txt é ele (RobotsNaoDeixa)
    if not source.get("pelo_worker") and not pode_coletar(url):
        print(f"  robots.txt bloqueia coleta de {url}, pulando.")
        return []

    resp = baixar(url, USER_AGENT, source.get("pelo_worker"), timeout=10)
    resp.raise_for_status()

    texto = texto_da_pagina(resp.content)
    if not texto:
        return []

    metadata = trafilatura.extract_metadata(resp.content)
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
    pelo_worker = source.get("pelo_worker")
    itens = ler_sitemap(source["url"], USER_AGENT, limite=MAX_MATERIAS_SITEMAP, pelo_worker=pelo_worker)
    with conn.cursor() as cur:
        cur.execute(
            "select url from articles where feed_id = %s and url = any(%s)",
            (source["id"], [i["url"] for i in itens]),
        )
        ja_salvas = {linha[0] for linha in cur.fetchall()}
    conn.commit()  # não segura a transação enquanto baixa as matérias

    artigos = []
    for item in itens:
        if item["url"] in ja_salvas:
            continue
        texto, imagem, autor = None, item["image_url"], None
        if pelo_worker or pode_coletar(item["url"]):
            try:
                resp = baixar(item["url"], USER_AGENT, pelo_worker, timeout=10)
                resp.raise_for_status()
                texto = texto_da_pagina(resp.content)
                metadata = trafilatura.extract_metadata(resp.content)
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


def _data_do_artigo(artigo):
    valor = artigo.get("published_at")
    if isinstance(valor, datetime):
        return valor if valor.tzinfo else valor.replace(tzinfo=timezone.utc)
    if isinstance(valor, str):
        try:  # "2026-10-07 18:25:00", do published_parsed do RSS (em UTC)
            return datetime.strptime(valor[:19], "%Y-%m-%d %H:%M:%S").replace(tzinfo=timezone.utc)
        except ValueError:
            return None
    return None


def so_recentes(artigos):
    """Primeira coleta de uma fonte: as das últimas 24h (e as sem data, que
    não dá pra saber); sem nenhuma, as PRIMEIRA_COLETA_RESERVA mais recentes."""
    limite = datetime.now(timezone.utc) - timedelta(hours=PRIMEIRA_COLETA_HORAS)
    recentes = [a for a in artigos if (_data_do_artigo(a) or limite) >= limite]
    if recentes:
        return recentes
    com_data = sorted(artigos, key=lambda a: _data_do_artigo(a) or limite, reverse=True)
    return com_data[:PRIMEIRA_COLETA_RESERVA]


def recentes_do_feed(conn, tabela, coluna, feed_id):
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute(
            f"select id, url, title from {tabela} where {coluna} = %s "
            f"and collected_at > now() - make_interval(days => {DIAS_PRA_COMPARAR})",
            (feed_id,),
        )
        return cur.fetchall()


def promover(conn, tabela, coluna, feed_id, promovidas):
    """A notícia que tinha vindo pelo Google ganha o link direto, o texto e
    a foto (sql/040: e volta pra fila do enriquecimento e da IA)."""
    feitas = 0
    with conn.cursor() as cur:
        for id_existente, n in promovidas:
            reabrir_ia = ", category = null, ai_summary = null" if tabela == "articles" else ", ai_summary = null"
            cur.execute(
                f"""
                update {tabela}
                set url = %(url)s, title = %(title)s,
                    content = coalesce(%(content)s, content),
                    image_url = coalesce(%(image_url)s, image_url),
                    author = coalesce(%(author)s, author),
                    published_at = coalesce(%(published_at)s, published_at),
                    enriquecido_em = null {reabrir_ia}
                where id = %(id)s
                  and not exists (select 1 from {tabela} where {coluna} = %(feed)s and url = %(url)s)
                """,
                {**n, "author": n.get("author"), "image_url": n.get("image_url"), "id": id_existente, "feed": feed_id},
            )
            feitas += cur.rowcount
    return feitas


def salvar_artigos(conn, feed_id, artigos):
    """Grava as novas sem repetir a mesma notícia que já veio pelo outro
    caminho (link direto x Google Notícias, ver manchetes.py)."""
    artigos = [a for a in artigos if a.get("url")]
    inserir, promovidas = separar_repetidas(recentes_do_feed(conn, "articles", "feed_id", feed_id), artigos)
    novos = 0
    with conn.cursor() as cur:
        for artigo in inserir:
            cur.execute(
                """
                insert into articles (feed_id, title, url, content, published_at, author, image_url)
                values (%s, %s, %s, %s, %s, %s, %s)
                on conflict (feed_id, url) do nothing
                returning id
                """,
                (
                    feed_id,
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
    novos += promover(conn, "articles", "feed_id", feed_id, promovidas)
    conn.commit()
    return novos


def marcar_pelo_hub(conn, feed_id, url):
    """sql/040: o feed (e a mesma fonte no catálogo) passa a vir pelo Worker
    (rede.py) ou, sem ele, pelo hub."""
    with conn.cursor() as cur:
        cur.execute("update feeds set coletar_pelo_hub = true where id = %s", (feed_id,))
        cur.execute("update feed_catalog set coletar_pelo_hub = true where url = %s", (url,))
    conn.commit()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--fonte", help="coleta só este feed (feeds.id ou sources.id)")
    parser.add_argument("--sem-artigos", action="store_true", help="só fontes que ainda não têm nenhum artigo")
    args = parser.parse_args()

    conn = get_connection()
    try:
        fontes = buscar_fontes(conn, resolver_feed(conn, args.fonte), args.sem_artigos)
        conn.commit()  # fecha a transação da leitura antes de sair baixando feeds
        print(f"{len(fontes)} feed(s) seguido(s).")

        for source in fontes:
            print(f"Coletando: {source['url']} ({source['type']}{', pelo Worker' if source['pelo_worker'] else ''})")
            try:
                if tem_api(source["url"]):
                    artigos = coletar_pela_api(source)
                elif source["type"] == "rss":
                    artigos = coletar_rss(source)
                elif source["type"] == "sitemap":
                    artigos = coletar_sitemap(source, conn)
                else:
                    artigos = coletar_scrape(source)
            except Exception as erro:
                print(f"  erro ao coletar {source['url']}: {erro}")
                continue

            if source.get("bloqueado") and source["pelo_worker"]:
                print("  o site barrou também o Worker: ficou com o Google Notícias")
            elif source.get("bloqueado"):
                marcar_pelo_hub(conn, source["id"], source["url"])
                quem = "o Worker (Cloudflare)" if tem_worker() else "o hub (Vercel)"
                print(f"  o site barrou o GitHub: daqui pra frente quem coleta é {quem}")

            if not source["tem_artigos"]:
                total = len(artigos)
                artigos = so_recentes(artigos)
                print(f"  primeira coleta: {len(artigos)} de {total} (últimas {PRIMEIRA_COLETA_HORAS}h)")

            novos = salvar_artigos(conn, source["id"], artigos)
            print(f"  {len(artigos)} artigo(s) encontrados, {novos} novo(s) salvos.")

            time.sleep(PAUSA_ENTRE_FONTES_SEGUNDOS)
    finally:
        conn.close()


if __name__ == "__main__":
    main()
