"""
Foto de capa do e-mail do resumo diário, do Unsplash (sql/028).

Uma foto por dia, igual pra todos: busca na primeira vez que precisa e
guarda em `foto_do_dia`; os outros envios do dia reaproveitam.

Regras da API do Unsplash (help.unsplash.com, "API Guidelines"):
  - usar o endereço de imagem que a API devolve (urls.*), sem copiar a foto;
  - avisar a API quando a foto for usada (links.download_location);
  - dar crédito: nome do fotógrafo + link pro perfil + link pro Unsplash,
    com ?utm_source=<app>&utm_medium=referral nos links.

Precisa de UNSPLASH_ACCESS_KEY no ambiente (secret do GitHub Actions).
Sem a chave, ou se a API falhar, devolve None e o e-mail sai sem foto.
"""
import os

import requests
from psycopg2.extras import RealDictCursor

API = "https://api.unsplash.com"
UTM = "utm_source=feed_de_noticias&utm_medium=referral"
# Um tema por dia, em rodízio: dá variedade sem depender de sorte
TEMAS = ["architecture", "city", "nature", "landscape", "ocean", "mountains", "street", "minimal", "forest", "desert"]


def _com_utm(url):
    return f"{url}{'&' if '?' in url else '?'}{UTM}"


def foto_do_dia(conn, dia):
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute("select url, fotografo, fotografo_url, unsplash_url from foto_do_dia where dia = %s", (dia,))
        guardada = cur.fetchone()
    conn.commit()
    if guardada:
        return guardada

    chave = os.environ.get("UNSPLASH_ACCESS_KEY")
    if not chave:
        print("(sem UNSPLASH_ACCESS_KEY: e-mail vai sem foto de capa)")
        return None

    cabecalhos = {"Authorization": f"Client-ID {chave}", "Accept-Version": "v1"}
    try:
        resp = requests.get(
            f"{API}/photos/random",
            params={"query": TEMAS[dia.toordinal() % len(TEMAS)], "orientation": "landscape", "content_filter": "high"},
            headers=cabecalhos,
            timeout=10,
        )
        resp.raise_for_status()
        dados = resp.json()
        # urls.raw aceita parâmetros de recorte/tamanho: capa 1200x640, leve pro e-mail
        foto = {
            "url": f"{dados['urls']['raw']}&w=1200&h=640&fit=crop&crop=entropy&q=75&fm=jpg",
            "fotografo": dados["user"]["name"],
            "fotografo_url": _com_utm(dados["user"]["links"]["html"]),
            "unsplash_url": _com_utm(dados["links"]["html"]),
        }
        # regra da API: avisar que a foto foi usada
        requests.get(dados["links"]["download_location"], headers=cabecalhos, timeout=10)
    except Exception as erro:
        print(f"(Unsplash falhou: {erro}; e-mail vai sem foto de capa)")
        return None

    with conn.cursor() as cur:
        cur.execute(
            """
            insert into foto_do_dia (dia, url, fotografo, fotografo_url, unsplash_url)
            values (%(dia)s, %(url)s, %(fotografo)s, %(fotografo_url)s, %(unsplash_url)s)
            on conflict (dia) do nothing
            """,
            {"dia": dia, **foto},
        )
    conn.commit()
    return foto
