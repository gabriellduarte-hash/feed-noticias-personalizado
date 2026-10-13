"""
Enriquecimento: abre a página de cada notícia nova que chegou com pouco
texto ou sem imagem, e guarda o texto completo e a imagem (trafilatura).
Vale pras notícias das fontes dos usuários (articles) e do catálogo
(catalog_articles, aba Explorar). Precisa do sql/025.

Por que: alguns feeds mandam só um resumo curto, e sitemap não manda
texto nenhum. Com o texto inteiro, a leitura dentro do hub fica completa
e o resumo da IA (resumir.py, que roda depois) fica melhor.

O texto do RSS vale mais que o da página: a página vem com menus,
anúncios e links pra outras matérias. Então a página só substitui o
texto quando o feed mandou pouco (TEXTO_CURTO); se o feed já trouxe a
matéria e só faltou a imagem, o texto do feed fica.

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
import re
import time
import urllib.robotparser as robotparser
from urllib.parse import urlparse

import requests
import trafilatura
from psycopg2.extras import RealDictCursor

from coletar import USER_AGENT
from db import get_connection, resolver_feed
from texto import texto_da_pagina

POR_RODADA = 60          # por tabela; a coleta roda de hora em hora
TEXTO_CURTO = 600        # abaixo disso, o "texto" é só o resumo do feed
PAUSA_SEGUNDOS = 0.5
# Resumo do feed que termina chamando pro site ("Continue lendo »", da
# Nintendo Blast): cortado, mesmo passando de TEXTO_CURTO. A mesma regra
# vale no SQL de pendentes e na rota do hub.
CORTADO = r"(continue lendo|leia mais|read more|keep reading)\s*(»|›|\.\.\.|…)"
# Página de "prove que não é robô" que alguns sites devolvem com 200 pras
# máquinas de nuvem. Só pelo título (muita página normal carrega o script
# do reCAPTCHA do formulário de comentário) e pela frase do Google.
TITULO = re.compile(r"<title[^>]*>(.*?)</title>", re.I | re.S)
TITULO_DE_DESAFIO = re.compile(r"just a moment|attention required|captcha|access denied|are you a robot", re.I)
FRASE_DO_GOOGLE = "unusual traffic from your computer network"


class Barrado(Exception):
    """O site barrou a máquina do GitHub nesta página."""


def parece_cortado(texto):
    return bool(re.search(CORTADO, texto or "", re.I))

TABELAS = {"articles": "fontes dos usuários", "catalog_articles": "catálogo"}


# Sites que barram o GitHub: quem abre as páginas é o hub, na Vercel (sql/040)
FORA_DO_HUB = {
    "articles": "not exists (select 1 from feeds f where f.id = feed_id and f.coletar_pelo_hub)",
    "catalog_articles": "not exists (select 1 from feed_catalog f where f.id = catalog_id and f.coletar_pelo_hub)",
}
COLUNA_DA_FONTE = {"articles": "feed_id", "catalog_articles": "catalog_id"}


def pendentes(conn, tabela, fonte_id=None, limite=POR_RODADA):
    filtro_fonte = "and feed_id = %(fonte)s" if fonte_id and tabela == "articles" else ""
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute(
            f"""
            select id, url, content, image_url, author, {COLUNA_DA_FONTE[tabela]} as fonte
            from {tabela}
            where enriquecido_em is null
              and url not like 'https://news.google.com/%%'
              and (content is null or length(content) < %(curto)s or image_url is null
                   or content ~* %(cortado)s)
              and {FORA_DO_HUB[tabela]}
              {filtro_fonte}
            order by collected_at desc
            limit %(limite)s
            """,
            {"curto": TEXTO_CURTO, "limite": limite, "fonte": fonte_id, "cortado": CORTADO},
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
    inicio = resp.text[:30000]
    titulo = TITULO.search(inicio)
    if (titulo and TITULO_DE_DESAFIO.search(titulo.group(1))) or FRASE_DO_GOOGLE in inicio.lower():
        raise Barrado(url)
    meta = trafilatura.extract_metadata(resp.content)
    return {
        "texto": texto_da_pagina(resp.content) or "",
        "imagem": meta.image if meta and meta.image else None,
        "autor": meta.author if meta and meta.author else None,
    }


def gravar(conn, tabela, noticia, achado):
    atual = noticia["content"] or ""
    curto = len(atual) < TEXTO_CURTO or parece_cortado(atual)
    novo_texto = achado["texto"] if curto and len(achado["texto"]) > len(atual) else None
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


def remover_sumida(conn, tabela, noticia):
    """A página da notícia não existe mais (404/410: o site tirou do ar).
    Sem texto nosso pra mostrar, ela só apareceria vazia no feed: sai.
    Se alguém salvou pra ler depois, fica (com o que tiver)."""
    if len(noticia["content"] or "") >= TEXTO_CURTO:
        marcar_tentada(conn, tabela, noticia["id"])
        return
    with conn.cursor() as cur:
        if tabela == "articles":
            cur.execute(
                """delete from articles a where a.id = %s
                   and not exists (select 1 from saved_articles s where s.article_id = a.id)""",
                (noticia["id"],),
            )
        else:
            cur.execute("delete from catalog_articles where id = %s", (noticia["id"],))
    conn.commit()
    marcar_tentada(conn, tabela, noticia["id"])  # se ficou (salva), não tenta de novo


def mandar_pro_hub(conn, tabela, fonte_id):
    """O site barra as páginas pras máquinas do GitHub: daqui pra frente
    quem coleta e abre as páginas dele é o hub, na Vercel (sql/040)."""
    with conn.cursor() as cur:
        if tabela == "articles":
            cur.execute("update feeds set coletar_pelo_hub = true where id = %s returning url", (fonte_id,))
            urls = [r[0] for r in cur.fetchall()]
            cur.execute("update feed_catalog set coletar_pelo_hub = true where url = any(%s)", (urls,))
        else:
            cur.execute("update feed_catalog set coletar_pelo_hub = true where id = %s returning url", (fonte_id,))
            urls = [r[0] for r in cur.fetchall()]
            cur.execute("update feeds set coletar_pelo_hub = true where url = any(%s)", (urls,))
    conn.commit()


def marcar_tentada(conn, tabela, noticia_id):
    with conn.cursor() as cur:
        cur.execute(f"update {tabela} set enriquecido_em = now() where id = %s", (noticia_id,))
    conn.commit()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--fonte", help="só as notícias deste feed (feeds.id ou sources.id)")
    parser.add_argument("--simular", action="store_true", help="baixa e mostra, sem gravar")
    args = parser.parse_args()

    robots = Robots()
    bloqueados = set()
    conn = get_connection()
    try:
        feed = resolver_feed(conn, args.fonte)
        tabelas = ["articles"] if feed else list(TABELAS)
        for tabela in tabelas:
            noticias = pendentes(conn, tabela, feed)
            conn.commit()  # fecha a leitura antes de abrir as páginas
            print(f"{TABELAS[tabela]}: {len(noticias)} notícia(s) pra enriquecer")
            com_texto = com_imagem = 0
            for n in noticias:
                dominio = urlparse(n["url"]).netloc
                if dominio in bloqueados:
                    continue  # barrou nesta rodada: a notícia fica pra fila do hub
                if not robots.pode(n["url"]):
                    if not args.simular:
                        marcar_tentada(conn, tabela, n["id"])
                    continue
                try:
                    achado = extrair(n["url"])
                except (requests.HTTPError, Barrado) as erro:
                    resposta = getattr(erro, "response", None)
                    status = resposta.status_code if resposta is not None else ("desafio" if isinstance(erro, Barrado) else None)
                    if status in (401, 403, 429, "desafio"):
                        print(f"  {dominio} barrou o GitHub ({status}); daqui pra frente, quem abre é o hub")
                        bloqueados.add(dominio)
                        if not args.simular:
                            mandar_pro_hub(conn, tabela, n["fonte"])
                            continue  # sem marcar como tentada: fica pra fila do hub
                    if not args.simular:
                        if status in (404, 410):
                            remover_sumida(conn, tabela, n)
                        else:
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
