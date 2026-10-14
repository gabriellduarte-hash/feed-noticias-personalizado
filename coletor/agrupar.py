"""
Histórias: notícias de fontes diferentes que contam o mesmo acontecimento,
sem IA. É o que define o Trending (as histórias que mais fontes estão
cobrindo) e a relevância no e-mail.

Como decide se duas notícias são a mesma história (nota de 0 a 100):
  - texto parecido (TF-IDF do título e do começo do texto): 40%
  - nomes em comum (pessoas, empresas, lugares, siglas; sinais.nomes): 25%
  - palavras do título em comum: 20%
  - perto no tempo (até 36h): 15%
  - números diferentes no título (placar, valor, versão): -10
A partir de CORTE, e com texto parecido de verdade (ou título bem
parecido), viram a mesma história. Calibrado em 14/10 com 6.456 notícias
reais: acima de 70, sempre a mesma; de 60 a 70, quase sempre; de 50 a 60,
misturado (por isso o corte em 58).

Pra não formar "correntes" (A parece B, B parece C, mas A e C não têm
nada a ver), dois grupos só se juntam se a nota média entre eles também
for alta.

Pra não comparar tudo com tudo (milhares de notícias), primeiro o TF-IDF
separa os pares candidatos (blocking); a nota completa só pra esses.

Roda de hora em hora, depois da classificação. Recalcula a janela inteira
(36h) e mantém o id das histórias que já existiam.

Uso (de dentro de coletor/):
    python agrupar.py              # agrupa e grava
    python agrupar.py --simular    # mostra as maiores histórias, sem gravar
"""
import argparse
import time
import uuid
from collections import Counter
from urllib.parse import parse_qs, urlparse

from psycopg2.extras import RealDictCursor, execute_values
from sklearn.feature_extraction.text import TfidfVectorizer

from db import get_connection
from sinais import PALAVRAS_VAZIAS, nomes, normalizar, numeros, palavras

JANELA_HORAS = 36
CORTE = 58
FOLGA_DA_MEDIA = 18          # média entre dois grupos: pelo menos CORTE - isso
COSSENO_CANDIDATO = 0.2      # blocking: abaixo disso nem calcula a nota
COSSENO_MINIMO = 0.25        # ou o texto é parecido de verdade...
TITULO_MINIMO = 0.5          # ...ou metade das palavras do título bate
CARACTERES_DO_TEXTO = 500
TEXTO_PRA_VITRINE = 400      # notícia que representa a história no Trending
PREFIXOS_DE_HOST = ("www.", "feeds.", "feed.", "rss.", "admin.", "m.", "amp.")


def chave_da_fonte(url):
    """O site, pra contar fontes diferentes: "feeds.folha.uol.com.br" e
    "folha.uol.com.br" são o mesmo; no Google Notícias, o site da busca."""
    p = urlparse(url or "")
    host = p.netloc.lower()
    if host == "news.google.com":
        host = parse_qs(p.query).get("q", [""])[0].replace("site:", "").split("/")[0]
    for prefixo in PREFIXOS_DE_HOST:
        if host.startswith(prefixo):
            host = host[len(prefixo):]
    return host


# ------------------------------------------------------------------ dados

def carregar(conn):
    """Notícias da janela, das fontes dos usuários e do catálogo. A mesma
    URL nas duas tabelas vira uma notícia só (e as duas linhas recebem a
    mesma história)."""
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute(
            f"""
            select 'articles' as tabela, a.id, a.url, a.title, left(coalesce(a.content, ''), {CARACTERES_DO_TEXTO}) as lead,
                   length(coalesce(a.content, '')) as tamanho, a.image_url, a.category, a.palavras_chave,
                   coalesce(a.published_at, a.collected_at) as quando, f.url as fonte_url,
                   a.historia_id, a.historia_nota, a.historia_motivo
            from articles a join feeds f on f.id = a.feed_id
            where a.collected_at > now() - make_interval(hours => {JANELA_HORAS})
            union all
            select 'catalog_articles', c.id, c.url, c.title, left(coalesce(c.content, ''), {CARACTERES_DO_TEXTO}),
                   length(coalesce(c.content, '')), c.image_url, c.category, c.palavras_chave,
                   coalesce(c.published_at, c.collected_at), fc.url,
                   c.historia_id, c.historia_nota, c.historia_motivo
            from catalog_articles c join feed_catalog fc on fc.id = c.catalog_id
            where c.collected_at > now() - make_interval(hours => {JANELA_HORAS})
            """
        )
        linhas = cur.fetchall()
    conn.commit()

    por_url = {}
    for linha in linhas:
        doc = por_url.get(linha["url"])
        if doc is None:
            doc = por_url[linha["url"]] = {**linha, "linhas": []}
        doc["linhas"].append(linha)
        if linha["tabela"] == "catalog_articles":
            doc["catalogo_id"] = linha["id"]
    docs = list(por_url.values())
    for d in docs:
        d["fonte"] = chave_da_fonte(d["fonte_url"])
        d["nomes"] = set(d["palavras_chave"] or nomes(f"{d['title']}. {d['lead'][:300]}"))
        d["nums"] = numeros(d["title"])
        d["tit"] = set(palavras(d["title"], 4))
        d["ts"] = d["quando"].timestamp()
    return docs


# ------------------------------------------------------------------ nota

def pontuar(a, b, cosseno):
    nomes_em_comum = a["nomes"] & b["nomes"]
    ent = len(nomes_em_comum) / min(len(a["nomes"]), len(b["nomes"])) if a["nomes"] and b["nomes"] else 0.0
    tit = len(a["tit"] & b["tit"]) / min(len(a["tit"]), len(b["tit"])) if a["tit"] and b["tit"] else 0.0
    horas = abs(a["ts"] - b["ts"]) / 3600
    tempo = max(0.0, 1 - horas / JANELA_HORAS)
    nota = 100 * (0.40 * min(1.0, cosseno / 0.6) + 0.25 * ent + 0.20 * tit + 0.15 * tempo)
    if a["nums"] and b["nums"] and not (a["nums"] & b["nums"]):
        nota -= 10
    motivo = f"texto {cosseno:.2f} · título {tit:.2f} · {horas:.0f}h"
    if nomes_em_comum:
        motivo += " · nomes: " + ", ".join(sorted(nomes_em_comum)[:4])
    aceita = nota >= CORTE and (cosseno >= COSSENO_MINIMO or tit >= TITULO_MINIMO)
    return nota, aceita, motivo


def pares_candidatos(docs):
    textos = [f"{normalizar(d['title'])} {normalizar(d['title'])} {normalizar(d['lead'])}" for d in docs]
    vetorizador = TfidfVectorizer(
        ngram_range=(1, 2), max_df=0.3, sublinear_tf=True, stop_words=sorted(PALAVRAS_VAZIAS)
    )
    matriz = vetorizador.fit_transform(textos)
    pares = []
    for inicio in range(0, matriz.shape[0], 1000):  # em blocos: a matriz inteira não cabe na memória
        parcial = (matriz[inicio:inicio + 1000] @ matriz.T).tocoo()
        for i, j, cosseno in zip(parcial.row + inicio, parcial.col, parcial.data):
            if i < j and cosseno >= COSSENO_CANDIDATO:
                pares.append((int(i), int(j), float(cosseno)))
    return pares


def agrupar(docs):
    """Grupos de índices em docs, com a melhor nota e o motivo de cada um."""
    notas, ligacoes = {}, []
    for i, j, cosseno in pares_candidatos(docs):
        nota, aceita, motivo = pontuar(docs[i], docs[j], cosseno)
        notas[(i, j)] = nota
        if aceita:
            ligacoes.append((nota, i, j, motivo))

    pai = list(range(len(docs)))
    membros = {i: [i] for i in range(len(docs))}
    melhor = {}

    def raiz(i):
        while pai[i] != i:
            pai[i] = pai[pai[i]]
            i = pai[i]
        return i

    for nota, i, j, motivo in sorted(ligacoes, reverse=True):
        a, b = raiz(i), raiz(j)
        if a == b:
            continue
        entre = [notas.get((min(x, y), max(x, y)), 0) for x in membros[a] for y in membros[b]]
        if sum(entre) / len(entre) < CORTE - FOLGA_DA_MEDIA:
            continue  # evita corrente
        if len(membros[a]) < len(membros[b]):
            a, b = b, a
        pai[b] = a
        membros[a] += membros.pop(b)
        for k in (i, j):
            if nota > melhor.get(k, (0, ""))[0]:
                melhor[k] = (nota, motivo)
    grupos = [m for m in membros.values() if len(m) > 1]
    return grupos, melhor


# ------------------------------------------------------------------ gravar

def resumo_do_grupo(docs, grupo):
    membros = [docs[i] for i in grupo]
    categorias = Counter(d["category"] for d in membros if d["category"] and d["category"] != "Outros")
    todos_os_nomes = Counter(n for d in membros for n in d["nomes"])
    # Trending: a do catálogo com foto e texto, a mais antiga (quem deu primeiro)
    vitrine = sorted(
        (d for d in membros if d.get("catalogo_id") and d["image_url"] and d["tamanho"] >= TEXTO_PRA_VITRINE),
        key=lambda d: d["ts"],
    )
    primeira = min(membros, key=lambda d: d["ts"])
    return {
        "titulo": (vitrine[0] if vitrine else primeira)["title"],
        "categoria": categorias.most_common(1)[0][0] if categorias else None,
        "fontes": len({d["fonte"] for d in membros}),
        "noticias": len(membros),
        "primeira": min(d["quando"] for d in membros),
        "ultima": max(d["quando"] for d in membros),
        "representante": str(vitrine[0]["catalogo_id"]) if vitrine else None,
        "nomes": [n for n, _ in todos_os_nomes.most_common(6)],
    }


def gravar(conn, docs, grupos, melhor):
    historias, mudancas = [], []
    usados = set()
    no_grupo = set()
    for grupo in grupos:
        # mantém o id que a maioria já tinha (a história só cresceu)
        anteriores = Counter(str(docs[i]["historia_id"]) for i in grupo if docs[i]["historia_id"])
        historia_id = next((h for h, _ in anteriores.most_common() if h not in usados), None) or str(uuid.uuid4())
        usados.add(historia_id)
        historias.append((historia_id, resumo_do_grupo(docs, grupo)))
        for i in grupo:
            no_grupo.add(i)
            nota, motivo = melhor.get(i, (None, None))
            for linha in docs[i]["linhas"]:
                nova_nota = round(nota) if nota else None
                if str(linha["historia_id"] or "") != historia_id or linha["historia_nota"] != nova_nota:
                    mudancas.append((linha["tabela"], str(linha["id"]), historia_id, nova_nota, motivo))
    # quem saiu de uma história (ficou sozinho)
    for i, d in enumerate(docs):
        if i not in no_grupo:
            for linha in d["linhas"]:
                if linha["historia_id"]:
                    mudancas.append((linha["tabela"], str(linha["id"]), None, None, None))

    with conn.cursor() as cur:
        if historias:
            execute_values(
                cur,
                """
                insert into historias (id, titulo, categoria, fontes, noticias, primeira, ultima, representante_catalogo, nomes, atualizada_em)
                values %s
                on conflict (id) do update set
                  titulo = excluded.titulo, categoria = excluded.categoria, fontes = excluded.fontes,
                  noticias = excluded.noticias, primeira = least(historias.primeira, excluded.primeira),
                  ultima = greatest(historias.ultima, excluded.ultima),
                  representante_catalogo = excluded.representante_catalogo, nomes = excluded.nomes,
                  atualizada_em = now()
                """,
                [
                    (h, r["titulo"], r["categoria"], r["fontes"], r["noticias"], r["primeira"], r["ultima"],
                     r["representante"], r["nomes"])
                    for h, r in historias
                ],
                template="(%s::uuid, %s, %s, %s, %s, %s, %s, %s::uuid, %s::text[], now())",
                page_size=500,
            )
        for tabela in ("articles", "catalog_articles"):
            linhas = [m[1:] for m in mudancas if m[0] == tabela]
            if linhas:
                execute_values(
                    cur,
                    f"""
                    update {tabela} as t
                    set historia_id = v.historia::uuid, historia_nota = v.nota::smallint, historia_motivo = v.motivo
                    from (values %s) as v(id, historia, nota, motivo)
                    where t.id = v.id::uuid
                    """,
                    linhas,
                    page_size=500,
                )
        # histórias que ficaram sem notícia nenhuma
        cur.execute(
            """
            delete from historias h
            where h.atualizada_em < now() - interval '10 minutes'
              and not exists (select 1 from articles a where a.historia_id = h.id)
              and not exists (select 1 from catalog_articles c where c.historia_id = h.id)
            """
        )
    conn.commit()
    return len(historias), len(mudancas)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--simular", action="store_true", help="mostra as maiores histórias, sem gravar")
    args = parser.parse_args()

    conn = get_connection()
    try:
        inicio = time.time()
        docs = carregar(conn)
        grupos, melhor = agrupar(docs)
        print(f"{len(docs)} notícia(s) nas últimas {JANELA_HORAS}h; {len(grupos)} história(s) com 2+ notícias "
              f"({time.time() - inicio:.1f}s)")
        maiores = sorted(grupos, key=lambda g: -len({docs[i]["fonte"] for i in g}))[:8]
        for grupo in maiores:
            r = resumo_do_grupo(docs, grupo)
            print(f"  [{r['fontes']} fontes] {r['titulo'][:90]}")
        if not args.simular:
            historias, mudancas = gravar(conn, docs, grupos, melhor)
            print(f"{historias} história(s) gravada(s); {mudancas} notícia(s) atualizada(s)")
    finally:
        conn.close()


if __name__ == "__main__":
    main()
