"""
Categoria, temas e nomes de cada notícia, sem IA (no lugar da
classificação que o resumir.py fazia com o Gemini).

Como decide a categoria:
  1. conta os termos da taxonomia (taxonomia.py) no título (peso 3) e no
     começo do texto (peso 1);
  2. soma a categoria do site como ponto de partida: forte nos sites de
     um assunto só (games, cinema, esportes...), fraca nos de notícias
     gerais;
  3. fica com a mais pontuada. Sem sinal suficiente: a do site, ou
     "Outros". A confiança (0 a 1) vai junto, pra saber o que revisar.
Temas: o tema amplo (a categoria) e os específicos que apareceram (Filmes,
Fofoca, Quadrinhos...; catálogo em temas.py, uma notícia pode ter vários).
O catálogo é copiado pro banco a cada rodada (catalogo_temas, sql/047),
pra busca do hub achar o tema pelos sinônimos.
Nomes: pessoas, organizações, lugares e obras, pelo spaCy (entidades.py).
Vão em dois lugares: `entidades` (como aparecem, com o tipo, pro hub
mostrar e a pessoa seguir) e `palavras_chave` (só as chaves
normalizadas, pro agrupamento de histórias e pra achar quem segue).

Roda de hora em hora, depois da limpeza de texto. Só as notícias ainda
não classificadas (classificado_em nulo), ou classificadas antes dos
nomes pelo spaCy (entidades nulo, sql/045): na primeira rodada depois do
045, refaz os últimos 3 dias.

Uso (de dentro de coletor/):
    python classificar.py               # as novas
    python classificar.py --dias 7      # reclassifica as dos últimos 7 dias
    python classificar.py --avaliar     # compara com as categorias que a IA dava, sem gravar
"""
import argparse
import json
import time
from collections import Counter, defaultdict

from psycopg2.extras import RealDictCursor, execute_values

from db import get_connection
from entidades import extrair
from sinais import normalizar
from taxonomia import CATEGORIAS, DA_FONTE, FONTES_ESPECIALIZADAS
from temas import detectar as detectar_temas, linhas_do_catalogo

PESO_TITULO = 3
PESO_TEXTO = 1
CARACTERES_DO_TEXTO = 600
BONUS_FONTE_ESPECIALIZADA = 4
BONUS_FONTE_GERAL = 1.5
SINAL_MINIMO = 3          # abaixo disso, vale a categoria do site
LOTE = 2000

# termo normalizado -> [(categoria, peso)]; n-gramas até 4 palavras
INDICE = defaultdict(list)
for _categoria, _dados in CATEGORIAS.items():
    for _termo, _peso in _dados["termos"].items():
        INDICE[_termo].append((_categoria, _peso))
MAIOR_TERMO = max((len(t.split()) for t in INDICE), default=1)


def termos_do_texto(texto):
    """Os termos da taxonomia que aparecem no texto (cada um conta até 2x)."""
    palavras = normalizar(texto).split()
    achados = Counter()
    for n in range(1, MAIOR_TERMO + 1):
        for i in range(len(palavras) - n + 1):
            termo = " ".join(palavras[i:i + n])
            if termo in INDICE:
                achados[termo] += 1
    return {t: min(c, 2) for t, c in achados.items()}


def categoria_da_fonte(categoria_do_site):
    if not categoria_do_site:
        return None
    if categoria_do_site in DA_FONTE:
        return DA_FONTE[categoria_do_site]
    return categoria_do_site if categoria_do_site in CATEGORIAS else None


def classificar(titulo, texto, categoria_do_site=None):
    """(categoria, temas, confiança). Os nomes saem à parte, em lote (entidades.extrair)."""
    pontos = Counter()
    termos_titulo = termos_do_texto(titulo)
    termos_texto = termos_do_texto((texto or "")[:CARACTERES_DO_TEXTO])
    for termos, peso_lugar in ((termos_titulo, PESO_TITULO), (termos_texto, PESO_TEXTO)):
        for termo, vezes in termos.items():
            for categoria, peso in INDICE[termo]:
                pontos[categoria] += peso * peso_lugar * vezes

    da_fonte = categoria_da_fonte(categoria_do_site)
    if da_fonte:
        pontos[da_fonte] += BONUS_FONTE_ESPECIALIZADA if da_fonte in FONTES_ESPECIALIZADAS else BONUS_FONTE_GERAL

    ordem = pontos.most_common(2)
    if not ordem or ordem[0][1] < SINAL_MINIMO:
        categoria = da_fonte or "Outros"
        confianca = 0.3 if da_fonte else 0.0
    else:
        categoria, melhor = ordem[0]
        segundo = ordem[1][1] if len(ordem) > 1 else 0
        confianca = round(min(1.0, (melhor - segundo) / melhor + 0.2), 2)

    return categoria, detectar_temas(titulo, texto, categoria), confianca


# ------------------------------------------------------------------ banco

CONSULTAS = {
    "articles": """
        select a.id, a.title, a.content, a.category as categoria_atual, c.category as categoria_do_site, c.idioma
        from articles a
        join feeds f on f.id = a.feed_id
        left join feed_catalog c on c.url = f.url
        where {filtro}
        order by a.collected_at desc
        limit %(lote)s
    """,
    "catalog_articles": """
        select a.id, a.title, a.content, a.category as categoria_atual, c.category as categoria_do_site, c.idioma
        from catalog_articles a
        join feed_catalog c on c.id = a.catalog_id
        where {filtro}
        order by a.collected_at desc
        limit %(lote)s
    """,
}


def pendentes(conn, tabela, dias=None):
    filtro = (
        f"a.collected_at > now() - make_interval(days => {int(dias)})"
        if dias
        else "(a.classificado_em is null or a.entidades is null) and a.collected_at > now() - interval '3 days'"
    )
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute(CONSULTAS[tabela].format(filtro=filtro), {"lote": LOTE})
        linhas = cur.fetchall()
    conn.commit()
    return linhas


def gravar(conn, tabela, resultados):
    with conn.cursor() as cur:
        execute_values(
            cur,
            f"""
            update {tabela} as t
            set category = v.categoria, temas = v.temas::text[], palavras_chave = v.chaves::text[],
                entidades = v.entidades::jsonb, categoria_confianca = v.confianca, classificado_em = now()
            from (values %s) as v(id, categoria, temas, confianca, chaves, entidades)
            where t.id = v.id::uuid
            """,
            resultados,
            template="(%s, %s, %s, %s, %s, %s)",
            page_size=500,
        )
    conn.commit()


def sincronizar_catalogo(conn):
    """O catálogo de temas (temas.py) no banco, igualzinho: o hub busca
    os temas por nome e sinônimo nessa tabela."""
    linhas = linhas_do_catalogo()
    with conn.cursor() as cur:
        execute_values(
            cur,
            """
            insert into catalogo_temas (nome, grupo, sinonimos, ordem) values %s
            on conflict (nome) do update set grupo = excluded.grupo, sinonimos = excluded.sinonimos,
              ordem = excluded.ordem, atualizado_em = now()
            """,
            linhas,
            template="(%s, %s, %s::text[], %s)",
        )
        cur.execute("delete from catalogo_temas where not (nome = any(%s))", ([n for n, *_ in linhas],))
    conn.commit()


def atualizar_sugestoes(conn):
    """Os temas e nomes mais citados nos últimos 3 dias (tabela
    sugestoes_seguir, sql/045): o que o hub sugere pra seguir. Nome citado
    por menos de 3 notícias fica de fora (erro de leitura, nome de passagem)."""
    with conn.cursor() as cur:
        cur.execute("delete from sugestoes_seguir")
        cur.execute(
            """
            insert into sugestoes_seguir (tipo, chave, rotulo, detalhe, noticias)
            select 'nome', e->>'chave', mode() within group (order by e->>'nome'),
                   mode() within group (order by e->>'tipo'), count(distinct n.url)
            from (
              select url, entidades from articles
              where collected_at > now() - interval '3 days' and entidades is not null
              union all
              select url, entidades from catalog_articles
              where collected_at > now() - interval '3 days' and entidades is not null
            ) n, jsonb_array_elements(n.entidades) e
            group by e->>'chave'
            having count(distinct n.url) >= 3
            order by count(distinct n.url) desc
            limit 3000
            """
        )
        cur.execute(
            """
            insert into sugestoes_seguir (tipo, chave, rotulo, detalhe, noticias)
            select 'tema', t.nome, t.nome, ct.grupo, count(distinct n.url)
            from (
              select url, temas from articles where collected_at > now() - interval '3 days'
              union all
              select url, temas from catalog_articles where collected_at > now() - interval '3 days'
            ) n
            cross join lateral unnest(n.temas) as t(nome)
            left join catalogo_temas ct on ct.nome = t.nome
            group by t.nome, ct.grupo
            """
        )
    conn.commit()


def avaliar(conn):
    """Compara com as categorias que a IA (Gemini) tinha dado: só pra calibrar."""
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute(
            """
            select a.title, a.content, a.category as ia, c.category as site
            from articles a join feeds f on f.id = a.feed_id left join feed_catalog c on c.url = f.url
            where a.category is not null and a.classificado_em is null
              and a.collected_at > now() - interval '10 days'
            limit 3000
            """
        )
        linhas = cur.fetchall()
    acertos, confusao = 0, Counter()
    for linha in linhas:
        categoria, _, _ = classificar(linha["title"], linha["content"], linha["site"])
        if categoria == linha["ia"]:
            acertos += 1
        else:
            confusao[(linha["ia"], categoria)] += 1
    total = len(linhas) or 1
    print(f"{len(linhas)} notícias com categoria da IA; as regras concordam em {acertos / total:.0%}")
    print("maiores diferenças (IA -> regras):")
    for (ia, regra), n in confusao.most_common(12):
        print(f"  {ia:15} -> {regra:15} {n}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dias", type=int, help="reclassifica as notícias desses últimos dias")
    parser.add_argument("--avaliar", action="store_true", help="compara com a IA, sem gravar")
    args = parser.parse_args()

    conn = get_connection()
    try:
        if args.avaliar:
            avaliar(conn)
            return
        sincronizar_catalogo(conn)
        for tabela in ("articles", "catalog_articles"):
            total, inicio = 0, time.time()
            while True:
                linhas = pendentes(conn, tabela, args.dias)
                if not linhas:
                    break
                nomes = extrair([(linha["title"], linha["content"], linha["idioma"]) for linha in linhas])
                resultados = []
                for linha, achados in zip(linhas, nomes):
                    categoria, temas, confianca = classificar(linha["title"], linha["content"], linha["categoria_do_site"])
                    chaves = list(dict.fromkeys(n["chave"] for n in achados))
                    resultados.append((str(linha["id"]), categoria, temas, confianca, chaves, json.dumps(achados, ensure_ascii=False)))
                gravar(conn, tabela, resultados)
                total += len(resultados)
                if args.dias or len(linhas) < LOTE:
                    break
            print(f"{tabela}: {total} notícia(s) classificada(s) ({time.time() - inicio:.1f}s)")
        atualizar_sugestoes(conn)
    finally:
        conn.close()


if __name__ == "__main__":
    main()
