"""
Enriquecimento: abre a página de cada notícia nova que chegou com pouco
texto ou sem imagem, e guarda o texto completo e a imagem (trafilatura).
Vale pras notícias das fontes dos usuários (articles) e do catálogo
(catalog_articles, aba Explorar). Precisa do sql/025.

Por que: a maioria dos feeds manda só um resumo curto, e sitemap não
manda texto nenhum. Com o texto inteiro, a leitura dentro do hub fica
completa e o resumo da IA (resumir.py, que roda depois) fica melhor.

Regras:
  - cada notícia é tentada uma vez só (enriquecido_em), com ou sem sucesso;
  - respeita o robots.txt de cada site (lido uma vez por rodada);
  - se um site bloquear (403/429), desiste dele no resto da rodada;
  - notícias do Google Notícias ficam de fora: o link passa por um
    redirecionamento do Google que não dá pra resolver de forma confiável.

Uso (de dentro de coletor/):
    python enriquecer.py               # até 60 de cada tabela, das mais novas
    python enriquecer.py --fonte <id>  # só as notícias de uma fonte (workflow "Fonte nova")
    python enriquecer.py --simular     # baixa e mostra, sem gravar
"""
import argparse
import time
import urllib.robotparser as robotparser
from urllib.parse import urlparse

import requests
import trafilatura
from psycopg2.extras import RealDictCursor

from coletar import USER_AGENT
from db import get_connection

POR_RODADA = 60          # por tabela; a coleta roda de hora em hora
TEXTO_CURTO = 600        # abaixo disso, o "texto" é só o resumo do feed
MAX_CARACTERES = 12000
PAUSA_SEGUNDOS = 0.5

TABELAS = {"articles": "fontes dos usuários", "catalog_articles": "catálogo"}


def pendentes(conn, tabela, fonte_id=None, limite=POR_RODADA):
    filtro_fonte = "and source_id = %(fonte)s" if fonte_id and tabela == "articles" else ""
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute(
            f"""
            select id, url, content, image_url, author
            from {tabela}
            where enriquecido_em is null
              and url not like 'https://news.google.com/%%'
              and (content is null or length(content) < %(curto)s or image_url is null)
              {filtro_fonte}
            order by collected_at desc
            limit %(limite)s
            """,
            {"curto": TEXTO_CURTO, "limite": limite, "fonte": fonte_id},
        )
        return cur.fetchall()


class Robots:
    """robots.txt por domínio, lido uma vez (mesma estratégia do coletar.py:
    baixa com o nosso User-Agent em vez de rp.read())."""

    def __init__(self):
        self.cache = {}

    def pode(self, url):
        p = urlparse(url)
        dominio = f"{p.scheme}://{p.netloc}"
        if dominio not in self.cache:
            rp = robotparser.RobotFileParser()
            try:
                resp = requests.get(f"{dominio}/robots.txt", headers={"User-Agent": USER_AGENT}, timeout=10)
                rp.parse(resp.text.splitlines() if resp.ok else [])
            except requests.RequestException:
                rp.parse([])  # sem robots.txt acessível: liberado (projeto pessoal, baixo volume)
            self.cache[dominio] = rp
        return self.cache[dominio].can_fetch(USER_AGENT, url)


def extrair(url):
    resp = requests.get(url, headers={"User-Agent": USER_AGENT}, timeout=12)
    resp.raise_for_status()
    texto = trafilatura.extract(resp.text, include_comments=False, include_tables=False) or ""
    meta = trafilatura.extract_metadata(resp.text)
    return {
        "texto": texto[:MAX_CARACTERES],
        "imagem": meta.image if meta and meta.image else None,
        "autor": meta.author if meta and meta.author else None,
    }


def gravar(conn, tabela, noticia, achado):
    novo_texto = achado["texto"] if len(achado["texto"]) > len(noticia["content"] or "") else None
    with conn.cursor() as cur:
        cur.execute(
            f"""
            update {tabela}
            set content = coalesce(%s, content),
                image_url = coalesce(image_url, %s),
                author = coalesce(author, %s),
                enriquecido_em = now()
            where id = %s
            """,
            (novo_texto, achado["imagem"], achado["autor"], noticia["id"]),
        )


def marcar_tentada(conn, tabela, noticia_id):
    with conn.cursor() as cur:
        cur.execute(f"update {tabela} set enriquecido_em = now() where id = %s", (noticia_id,))
    conn.commit()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--fonte", help="só as notícias desta fonte (sources.id)")
    parser.add_argument("--simular", action="store_true", help="baixa e mostra, sem gravar")
    args = parser.parse_args()

    robots = Robots()
    bloqueados = set()
    conn = get_connection()
    try:
        tabelas = ["articles"] if args.fonte else list(TABELAS)
        for tabela in tabelas:
            noticias = pendentes(conn, tabela, args.fonte)
            conn.commit()  # fecha a leitura antes de abrir as páginas
            print(f"{TABELAS[tabela]}: {len(noticias)} notícia(s) pra enriquecer")
            com_texto = com_imagem = 0
            for n in noticias:
                dominio = urlparse(n["url"]).netloc
                if dominio in bloqueados or not robots.pode(n["url"]):
                    if not args.simular:
                        marcar_tentada(conn, tabela, n["id"])
                    continue
                try:
                    achado = extrair(n["url"])
                except requests.HTTPError as erro:
                    status = erro.response.status_code if erro.response is not None else None
                    if status in (401, 403, 429):
                        print(f"  {dominio} bloqueou (HTTP {status}); pulando esse site nesta rodada")
                        bloqueados.add(dominio)
                    if not args.simular:
                        marcar_tentada(conn, tabela, n["id"])
                    continue
                except Exception as erro:
                    print(f"  erro em {n['url'][:70]}: {type(erro).__name__}")
                    if not args.simular:
                        marcar_tentada(conn, tabela, n["id"])
                    continue

                com_texto += len(achado["texto"]) > len(n["content"] or "")
                com_imagem += bool(achado["imagem"] and not n["image_url"])
                if args.simular:
                    print(f"  {dominio}: {len(n['content'] or '')} -> {len(achado['texto'])} caracteres, imagem: {bool(achado['imagem'])}")
                else:
                    gravar(conn, tabela, n, achado)
                    conn.commit()
                time.sleep(PAUSA_SEGUNDOS)
            print(f"  {com_texto} ganharam texto, {com_imagem} ganharam imagem")
        if not args.simular:
            conn.commit()
    finally:
        conn.close()


if __name__ == "__main__":
    main()
