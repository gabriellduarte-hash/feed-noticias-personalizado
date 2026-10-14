"""
Histórias: notícias de fontes diferentes que contam o mesmo acontecimento,
sem IA. É o que define o Trending (as histórias que mais fontes estão
cobrindo) e a relevância no e-mail.

Como decide se duas notícias são a mesma história (nota de 0 a 100):
  - texto parecido: 40%. O maior entre dois jeitos de medir:
      * palavras em comum (TF-IDF do título e do começo do texto);
      * sentido parecido (vetores.py): pega a mesma história contada com
        outras palavras, e em outra língua;
  - nomes em comum (pessoas, empresas, lugares; entidades.py): 25%
  - palavras do título em comum: 20%
  - perto no tempo (até 36h): 15%
  - números diferentes no título (placar, valor, versão): -10
Entre português e inglês, o título não tem palavra em comum (só os nomes):
o peso dele vai pro texto, que aí é só o sentido.

A partir de CORTE, e com texto parecido de verdade (palavras, título ou
sentido acima do mínimo), viram a mesma história. Calibrado em 14/10 com
6.456 notícias reais: acima de 70, sempre a mesma; de 60 a 70, quase
sempre; de 50 a 60, misturado (por isso o corte em 58). A amostra
marcada à mão (abaixo) é que diz se continua valendo.

Pra não formar "correntes" (A parece B, B parece C, mas A e C não têm
nada a ver), dois grupos só se juntam se a nota média entre eles também
for alta.

Pra não comparar tudo com tudo (milhares de notícias), primeiro separa os
pares candidatos (blocking): os de palavras parecidas (TF-IDF) e os de
sentido parecido (vetores). A nota completa só pra esses.

Amostra marcada à mão (sql/045, tabela pares_avaliados): a cada rodada,
se faltarem pares pra marcar, sorteia alguns de todas as faixas de nota
(e alguns entre línguas). O Gabriel marca no hub (Relatórios > Pares) se
são a mesma história; `--medir` diz a precisão (das que juntamos, quantas
eram mesmo a mesma) e a cobertura (das que eram, quantas juntamos).

Roda de hora em hora, depois da classificação. Recalcula a janela inteira
(36h) e mantém o id das histórias que já existiam.

Uso (de dentro de coletor/):
    python agrupar.py              # agrupa e grava
    python agrupar.py --simular    # mostra as maiores histórias, sem gravar
    python agrupar.py --amostra 60 # sorteia mais 60 pares pra marcar
    python agrupar.py --medir      # precisão e cobertura pelos pares marcados
"""
import argparse
import json
import random
import time
import uuid
from collections import Counter, defaultdict
from urllib.parse import parse_qs, urlparse

import numpy as np
from psycopg2.extras import RealDictCursor, execute_values
from sklearn.feature_extraction.text import TfidfVectorizer

import vetores
from db import get_connection
from entidades import chave, idioma
from sinais import PALAVRAS_VAZIAS, nomes, normalizar, numeros, palavras

JANELA_HORAS = 36
CORTE = 58
FOLGA_DA_MEDIA = 18          # média entre dois grupos: pelo menos CORTE - isso
PESOS = {"texto": 0.40, "nomes": 0.25, "titulo": 0.20, "tempo": 0.15}
PESOS_ENTRE_LINGUAS = {"texto": 0.60, "nomes": 0.25, "titulo": 0.0, "tempo": 0.15}
PENALIDADE_NUMEROS = 10
COSSENO_CHEIO = 0.6          # palavras: a partir daqui o texto vale 100%
# Sentido (vetores): onde começa a contar e onde vale 100%. Entre línguas
# a semelhança da mesma história sai mais baixa (0,80 já é quase certo).
SENTIDO = {"mesma": (0.70, 0.95), "entre": (0.65, 0.90)}
# Blocking: abaixo disso nem calcula a nota
COSSENO_CANDIDATO = 0.2
SENTIDO_CANDIDATO = 0.72
# Trava: além da nota, o texto tem que ser parecido de verdade
COSSENO_MINIMO = 0.25
TITULO_MINIMO = 0.5
SENTIDO_MINIMO = {"mesma": 0.80, "entre": 0.75}
# Duas do mesmo site só se ligam direto se forem quase a mesma matéria
# (republicada, atualizada). Sem isso, séries com título de modelo viravam
# história: "Arsenal x Lille: onde assistir" e "Feyenoord x Como: onde
# assistir", as tirinhas "Pinguins ...". Elas ainda caem na mesma história
# pelas ligações com outros sites.
MESMA_FONTE_TEXTO = 0.5
MESMA_FONTE_SENTIDO = 0.95
CARACTERES_DO_TEXTO = 500
TEXTO_PRA_VITRINE = 400      # notícia que representa a história no Trending
MAX_VETORES_POR_RODADA = 4000  # a primeira rodada calcula a janela toda; as outras, só as novas
PREFIXOS_DE_HOST = ("www.", "feeds.", "feed.", "rss.", "admin.", "m.", "amp.")
# Amostra pra marcar à mão: faixas de nota (sorteia o mesmo tanto de cada)
FAIXAS = [(0, 40), (40, 50), (50, 58), (58, 65), (65, 75), (75, 101)]
PENDENTES_MINIMO = 20        # menos que isso sem resposta: a rodada sorteia mais
AMOSTRA_POR_RODADA = 30


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
                   coalesce(a.published_at, a.collected_at) as quando, f.url as fonte_url, fc.idioma,
                   a.historia_id, a.historia_nota, a.historia_motivo
            from articles a
            join feeds f on f.id = a.feed_id
            left join feed_catalog fc on fc.url = f.url
            where a.collected_at > now() - make_interval(hours => {JANELA_HORAS})
            union all
            select 'catalog_articles', c.id, c.url, c.title, left(coalesce(c.content, ''), {CARACTERES_DO_TEXTO}),
                   length(coalesce(c.content, '')), c.image_url, c.category, c.palavras_chave,
                   coalesce(c.published_at, c.collected_at), fc.url, fc.idioma,
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
        d["lingua"] = idioma(f"{d['title']} {d['lead'][:300]}", d["idioma"])
        # palavras_chave: os nomes que o classificar.py achou (spaCy); quem
        # ainda não foi classificado usa os nomes pela maiúscula
        d["nomes"] = set(d["palavras_chave"] or (chave(n) for n in nomes(f"{d['title']}. {d['lead'][:300]}")))
        d["nums"] = numeros(d["title"])
        d["tit"] = set(palavras(d["title"], 4))
        d["ts"] = d["quando"].timestamp()
    return docs


def carregar_vetores(conn, docs):
    """Põe d["vetor"] em cada notícia: os guardados, e calcula (e guarda)
    os que faltam, das mais novas pras mais antigas."""
    guardados = vetores.carregar(conn, [d["url"] for d in docs])
    faltando = sorted((d for d in docs if d["url"] not in guardados), key=lambda d: -d["ts"])[:MAX_VETORES_POR_RODADA]
    if faltando:
        inicio = time.time()
        matriz = vetores.vetorizar([vetores.texto_da_noticia(d["title"], d["lead"]) for d in faltando])
        novos = {d["url"]: v for d, v in zip(faltando, matriz)}
        vetores.gravar(conn, novos)
        guardados.update(novos)
        print(f"{len(novos)} vetor(es) calculado(s) ({time.time() - inicio:.1f}s)")
    for d in docs:
        d["vetor"] = guardados.get(d["url"])


# ------------------------------------------------------------------ nota

def _sobreposicao(x, y):
    return len(x & y) / min(len(x), len(y)) if x and y else 0.0


def sinais_do_par(a, b, cosseno, sentido):
    """Tudo o que a nota usa, separado (vai junto pra amostra marcada à mão,
    pra dar pra testar outros pesos depois sem recalcular)."""
    return {
        "texto": round(cosseno, 3),
        "sentido": round(sentido, 3) if sentido is not None else None,
        "nomes": round(_sobreposicao(a["nomes"], b["nomes"]), 3),
        "titulo": round(_sobreposicao(a["tit"], b["tit"]), 3),
        "horas": round(abs(a["ts"] - b["ts"]) / 3600, 1),
        "numeros": bool(a["nums"] and b["nums"] and not (a["nums"] & b["nums"])),
        "linguas": "mesma" if a["lingua"] == b["lingua"] else "entre",
        "mesma_fonte": a["fonte"] == b["fonte"],
    }


def nota(s):
    """(nota de 0 a 100, se junta)."""
    zero, cheio = SENTIDO[s["linguas"]]
    sentido = s["sentido"] if s["sentido"] is not None else 0.0
    pelo_sentido = min(1.0, max(0.0, (sentido - zero) / (cheio - zero)))
    if s["linguas"] == "mesma":
        pesos, texto = PESOS, max(min(1.0, s["texto"] / COSSENO_CHEIO), pelo_sentido)
    else:
        pesos, texto = PESOS_ENTRE_LINGUAS, pelo_sentido
    tempo = max(0.0, 1 - s["horas"] / JANELA_HORAS)
    valor = 100 * (pesos["texto"] * texto + pesos["nomes"] * s["nomes"] + pesos["titulo"] * s["titulo"] + pesos["tempo"] * tempo)
    if s["numeros"]:
        valor -= PENALIDADE_NUMEROS
    if s.get("mesma_fonte"):
        parecido = s["texto"] >= MESMA_FONTE_TEXTO or sentido >= MESMA_FONTE_SENTIDO
    else:
        parecido = (
            s["texto"] >= COSSENO_MINIMO
            or (s["titulo"] >= TITULO_MINIMO and s["linguas"] == "mesma")
            or sentido >= SENTIDO_MINIMO[s["linguas"]]
        )
    return valor, valor >= CORTE and parecido


def motivo(a, b, s):
    texto = f"texto {s['texto']:.2f}"
    if s["sentido"] is not None:
        texto += f" · sentido {s['sentido']:.2f}"
    texto += f" · título {s['titulo']:.2f} · {s['horas']:.0f}h"
    if s["linguas"] == "entre":
        texto += f" · {a['lingua']}/{b['lingua']}"
    em_comum = a["nomes"] & b["nomes"]
    if em_comum:
        texto += " · nomes: " + ", ".join(sorted(em_comum)[:4])
    return texto


def pares_candidatos(docs):
    """{(i, j): (cosseno das palavras, semelhança do sentido ou None)}."""
    textos = [f"{normalizar(d['title'])} {normalizar(d['title'])} {normalizar(d['lead'])}" for d in docs]
    vetorizador = TfidfVectorizer(
        ngram_range=(1, 2), max_df=0.3, sublinear_tf=True, stop_words=sorted(PALAVRAS_VAZIAS)
    )
    matriz = vetorizador.fit_transform(textos)
    cossenos = {}
    for inicio in range(0, matriz.shape[0], 1000):  # em blocos: a matriz inteira não cabe na memória
        parcial = (matriz[inicio:inicio + 1000] @ matriz.T).tocoo()
        for i, j, cosseno in zip(parcial.row + inicio, parcial.col, parcial.data):
            if i < j and cosseno >= COSSENO_CANDIDATO:
                cossenos[(int(i), int(j))] = float(cosseno)

    com_vetor = [i for i, d in enumerate(docs) if d.get("vetor") is not None]
    sentidos = {}
    if com_vetor:
        V = np.stack([docs[i]["vetor"] for i in com_vetor])
        for inicio in range(0, len(com_vetor), 1000):
            parcial = V[inicio:inicio + 1000] @ V.T
            for x, y in zip(*np.nonzero(parcial >= SENTIDO_CANDIDATO)):
                i, j = com_vetor[inicio + x], com_vetor[y]
                if i < j:
                    sentidos[(i, j)] = float(parcial[x, y])

    pares = {}
    for par in cossenos.keys() | sentidos.keys():
        sentido = sentidos.get(par)
        a, b = docs[par[0]], docs[par[1]]
        if sentido is None and a.get("vetor") is not None and b.get("vetor") is not None:
            sentido = float(a["vetor"] @ b["vetor"])
        pares[par] = (cossenos.get(par, 0.0), sentido)
    return pares


def avaliar_pares(docs):
    """{(i, j): (sinais, nota, aceita)} pros pares candidatos."""
    avaliados = {}
    for (i, j), (cosseno, sentido) in pares_candidatos(docs).items():
        s = sinais_do_par(docs[i], docs[j], cosseno, sentido)
        valor, aceita = nota(s)
        avaliados[(i, j)] = (s, valor, aceita)
    return avaliados


def agrupar(docs, avaliados):
    """Grupos de índices em docs, com a melhor nota e o motivo de cada um."""
    notas = {par: valor for par, (_, valor, _) in avaliados.items()}
    ligacoes = [(valor, i, j, s) for (i, j), (s, valor, aceita) in avaliados.items() if aceita]

    pai = list(range(len(docs)))
    membros = {i: [i] for i in range(len(docs))}
    melhor = {}

    def raiz(i):
        while pai[i] != i:
            pai[i] = pai[pai[i]]
            i = pai[i]
        return i

    for valor, i, j, s in sorted(ligacoes, key=lambda x: x[:3], reverse=True):
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
            if valor > melhor.get(k, (0, ""))[0]:
                melhor[k] = (valor, motivo(docs[i], docs[j], s))
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
            valor, texto = melhor.get(i, (None, None))
            for linha in docs[i]["linhas"]:
                nova_nota = round(valor) if valor else None
                if str(linha["historia_id"] or "") != historia_id or linha["historia_nota"] != nova_nota:
                    mudancas.append((linha["tabela"], str(linha["id"]), historia_id, nova_nota, texto))
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


# ------------------------------------------------------------------ amostra marcada à mão

def faixa_da_nota(valor):
    for de, ate in FAIXAS:
        if de <= valor < ate:
            return f"{de}-{min(ate, 100)}"
    return f"{FAIXAS[0][0]}-{FAIXAS[0][1]}"


def sortear_amostra(conn, docs, avaliados, quantos):
    """Sorteia `quantos` pares candidatos, o mesmo tanto de cada faixa de
    nota (e até 1/3 entre línguas em cada uma), e guarda pra marcar à mão.
    O peso de cada par é quantos pares da janela ele representa (a faixa
    tem 5 mil pares e foram sorteados 5: peso 1000), pra estimar a
    cobertura de verdade."""
    estratos = defaultdict(list)
    for par, (s, valor, _) in avaliados.items():
        estratos[(faixa_da_nota(valor), s["linguas"])].append(par)
    por_faixa = max(1, quantos // len(FAIXAS))
    escolhidos = []
    for de, _ in FAIXAS:
        faixa = faixa_da_nota(de)
        entre = estratos.get((faixa, "entre"), [])
        mesma = estratos.get((faixa, "mesma"), [])
        n_entre = min(len(entre), por_faixa // 3)
        n_mesma = min(len(mesma), por_faixa - n_entre)
        for lista, n in ((entre, n_entre), (mesma, n_mesma)):
            for par in random.sample(lista, n):
                escolhidos.append((par, len(lista) / n))
    linhas = []
    for (i, j), peso in escolhidos:
        a, b = docs[i], docs[j]
        s, valor, aceita = avaliados[(i, j)]
        linhas.append((
            a["url"], b["url"], a["title"], b["title"], a["fonte"], b["fonte"],
            a["lead"][:400], b["lead"][:400], a["quando"], b["quando"],
            round(valor, 1), aceita, json.dumps(s), faixa_da_nota(valor), round(peso, 2),
        ))
    if linhas:
        with conn.cursor() as cur:
            execute_values(
                cur,
                """
                insert into pares_avaliados (a_url, b_url, a_titulo, b_titulo, a_fonte, b_fonte, a_trecho, b_trecho,
                                             a_quando, b_quando, nota, juntou, sinais, faixa, peso)
                values %s
                on conflict (a_url, b_url) do nothing
                """,
                linhas,
                template="(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s::jsonb, %s, %s)",
            )
        conn.commit()
    return len(linhas)


def pendentes_de_marcar(conn):
    with conn.cursor() as cur:
        cur.execute("select count(*) from pares_avaliados where resposta is null")
        total = cur.fetchone()[0]
    conn.commit()
    return total


def medir(conn):
    """Precisão e cobertura com os pesos e o corte de agora, pelos pares
    marcados (a nota é recalculada pelos sinais guardados). E, com pares
    suficientes, uma regressão logística diz quanto cada sinal pesa."""
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute(
            "select sinais, peso, resposta, a_titulo, b_titulo from pares_avaliados where resposta in ('mesma', 'diferente')"
        )
        marcados = cur.fetchall()
    conn.commit()
    if not marcados:
        print("Nenhum par marcado ainda (Relatórios > Pares, no hub).")
        return

    por_faixa = defaultdict(lambda: [0, 0])
    vp = fp = fn = 0.0
    erros = []
    for m in marcados:
        valor, aceita = nota(m["sinais"])
        mesma = m["resposta"] == "mesma"
        por_faixa[faixa_da_nota(valor)][0] += 1
        por_faixa[faixa_da_nota(valor)][1] += mesma
        peso = m["peso"] or 1
        if aceita and mesma:
            vp += peso
        elif aceita:
            fp += peso
            erros.append(("juntou, mas eram diferentes", valor, m))
        elif mesma:
            fn += peso
            erros.append(("separou, mas eram a mesma", valor, m))
    print(f"{len(marcados)} par(es) marcado(s). Corte {CORTE}.")
    print("Por faixa de nota (pares marcados, quantos eram a mesma história):")
    for de, _ in FAIXAS:
        n, iguais = por_faixa.get(faixa_da_nota(de), (0, 0))
        if n:
            print(f"  {faixa_da_nota(de):>7}: {iguais}/{n} ({iguais / n:.0%})")
    if vp + fp:
        print(f"Precisão (das que juntamos, quantas eram a mesma): {vp / (vp + fp):.0%}")
    if vp + fn:
        print(f"Cobertura (das que eram a mesma, quantas juntamos): {vp / (vp + fn):.0%}")
    for tipo, valor, m in sorted(erros, key=lambda e: -abs(e[1] - CORTE))[:8]:
        print(f"  [{tipo}, nota {valor:.0f}] {m['a_titulo'][:60]} || {m['b_titulo'][:60]}")

    mesmas = sum(m["resposta"] == "mesma" for m in marcados)
    if len(marcados) >= 40 and 5 <= mesmas <= len(marcados) - 5:
        from sklearn.linear_model import LogisticRegression

        def x(s):
            zero, cheio = SENTIDO[s["linguas"]]
            sentido = min(1.0, max(0.0, ((s["sentido"] or 0) - zero) / (cheio - zero)))
            return [min(1.0, s["texto"] / COSSENO_CHEIO), sentido, s["nomes"], s["titulo"],
                    max(0.0, 1 - s["horas"] / JANELA_HORAS), float(s["numeros"]), float(s["linguas"] == "entre")]

        X = np.array([x(m["sinais"]) for m in marcados])
        y = np.array([m["resposta"] == "mesma" for m in marcados])
        modelo = LogisticRegression(class_weight="balanced", max_iter=1000).fit(X, y)
        nomes_dos_sinais = ["palavras", "sentido", "nomes", "título", "tempo", "números diferentes", "entre línguas"]
        print("Regressão logística (quanto cada sinal pesa pra ser a mesma história; negativo = contra):")
        for nome_sinal, coef in sorted(zip(nomes_dos_sinais, modelo.coef_[0]), key=lambda t: -abs(t[1])):
            print(f"  {nome_sinal:>18}: {coef:+.2f}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--simular", action="store_true", help="mostra as maiores histórias, sem gravar")
    parser.add_argument("--amostra", type=int, help="sorteia mais N pares pra marcar à mão")
    parser.add_argument("--medir", action="store_true", help="precisão e cobertura pelos pares marcados")
    args = parser.parse_args()

    conn = get_connection()
    try:
        if args.medir:
            medir(conn)
            return
        inicio = time.time()
        docs = carregar(conn)
        carregar_vetores(conn, docs)
        avaliados = avaliar_pares(docs)
        grupos, melhor = agrupar(docs, avaliados)
        entre_linguas = sum(len({docs[i]["lingua"] for i in g}) > 1 for g in grupos)
        print(f"{len(docs)} notícia(s) nas últimas {JANELA_HORAS}h; {len(avaliados)} par(es) candidato(s); "
              f"{len(grupos)} história(s) com 2+ notícias, {entre_linguas} com português e inglês "
              f"({time.time() - inicio:.1f}s)")
        maiores = sorted(grupos, key=lambda g: -len({docs[i]["fonte"] for i in g}))[:8]
        for grupo in maiores:
            r = resumo_do_grupo(docs, grupo)
            print(f"  [{r['fontes']} fontes] {r['titulo'][:90]}")
        if args.simular:
            return
        historias, mudancas = gravar(conn, docs, grupos, melhor)
        print(f"{historias} história(s) gravada(s); {mudancas} notícia(s) atualizada(s)")
        quantos = args.amostra or (AMOSTRA_POR_RODADA if pendentes_de_marcar(conn) < PENDENTES_MINIMO else 0)
        if quantos:
            print(f"{sortear_amostra(conn, docs, avaliados, quantos)} par(es) novo(s) pra marcar à mão")
    finally:
        conn.close()


if __name__ == "__main__":
    main()
