"""
Faxina do texto das notícias: tira o que não é matéria. Roda na coleta
de hora em hora, depois do enriquecimento e antes do resumo da IA (pra
IA ler o texto limpo). Precisa do sql/029.

Duas regras (as duas em texto.py):
  1. fixas: anúncio, cookies, "siga no WhatsApp", rodapé do WordPress...
  2. trechos repetidos: parágrafo curto que aparece em muitas matérias da
     mesma fonte é do site (pedido de assinatura, bio do autor, links pra
     outras matérias), não da notícia. As repetições são contadas no
     próprio banco (só os trechos candidatos vêm pra cá, não o texto de
     todas as matérias). Os descobertos ficam em trechos_repetidos, pra
     sair das próximas matérias logo de cara; o que passa 30 dias sem
     aparecer é esquecido.

A cada hora só as notícias novas são limpas (e as antigas que tiverem
um trecho repetido recém-descoberto). Pra limpar tudo de uma vez, use
--dias.

Uso (de dentro de coletor/):
    python limpar_textos.py               # notícias das últimas 3 horas
    python limpar_textos.py --dias 60     # faxina geral (primeira vez)
    python limpar_textos.py --fonte <id>  # só uma fonte (workflow "Fonte nova")
    python limpar_textos.py --simular     # mostra o que sairia, sem gravar
"""
import argparse
from collections import defaultdict

from psycopg2.extras import RealDictCursor, execute_values

from db import get_connection
from texto import eh_repetido, limpar_texto

# tabela -> coluna que diz de qual fonte é a notícia
TABELAS = {"articles": "source_id", "catalog_articles": "catalog_id"}
JANELA_REPETICAO = "7 days"   # onde as repetições são contadas
DIAS_PRA_ESQUECER = 30


def trechos_conhecidos(conn):
    with conn.cursor() as cur:
        cur.execute("select fonte_id::text, trecho from trechos_repetidos")
        conhecidos = defaultdict(set)
        for fonte_id, trecho in cur.fetchall():
            conhecidos[fonte_id].add(trecho)
    conn.commit()
    return conhecidos


def descobrir_repetidos(conn, tabela, coluna):
    """Conta no banco, por fonte, os parágrafos que se repetem em 3 ou
    mais matérias da janela; texto.eh_repetido decide quais são do site."""
    with conn.cursor() as cur:
        cur.execute(
            f"""
            with recentes as (
                select id, {coluna}::text as fonte, content
                from {tabela}
                where content is not null and collected_at > now() - interval '{JANELA_REPETICAO}'
            ),
            totais as (select fonte, count(*) as total from recentes group by fonte),
            paragrafos as (
                select r.fonte, r.id, btrim(regexp_replace(p, '\\s+', ' ', 'g')) as trecho
                from recentes r, unnest(string_to_array(r.content, E'\\n')) as p
            )
            select p.fonte, p.trecho, count(distinct p.id) as vezes, t.total
            from paragrafos p join totais t using (fonte)
            where length(p.trecho) between 1 and 400
            group by p.fonte, p.trecho, t.total
            having count(distinct p.id) >= 3
            """
        )
        linhas = cur.fetchall()
    conn.commit()
    achados = defaultdict(set)
    for fonte, trecho, vezes, total in linhas:
        if eh_repetido(trecho, vezes, total):
            achados[fonte].add(trecho)
    return achados


def _padrao_like(trecho):
    return "%" + trecho.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_") + "%"


def noticias_pra_limpar(conn, tabela, coluna, args, trechos_novos):
    """As novas (ou as dos últimos --dias), mais as da janela que contêm
    um trecho repetido recém-descoberto."""
    if args.dias:
        filtros = [f"collected_at > now() - make_interval(days => {int(args.dias)})"]
    else:
        filtros = [f"collected_at > now() - make_interval(hours => {int(args.horas)})"]
    if trechos_novos:
        filtros.append(
            f"(collected_at > now() - interval '{JANELA_REPETICAO}' and content like any(%(padroes)s))"
        )
    filtro_fonte = f"and {coluna} = %(fonte)s" if args.fonte else ""
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute(
            f"""
            select id, {coluna}::text as fonte, content
            from {tabela}
            where content is not null and ({" or ".join(filtros)}) {filtro_fonte}
            """,
            {"fonte": args.fonte, "padroes": [_padrao_like(t) for t in trechos_novos]},
        )
        linhas = cur.fetchall()
    conn.commit()
    return linhas


def gravar(conn, tabela, mudancas, trechos_vistos):
    """trechos_vistos: os descobertos agora e os já conhecidos que saíram
    de alguma matéria nesta rodada (renova o visto_em)."""
    with conn.cursor() as cur:
        if trechos_vistos:
            execute_values(
                cur,
                "insert into trechos_repetidos (fonte_id, trecho) values %s "
                "on conflict (fonte_id, trecho) do update set visto_em = now()",
                trechos_vistos,
                template="(%s::uuid, %s)",
            )
        if mudancas:
            execute_values(
                cur,
                f"update {tabela} as t set content = v.content from (values %s) as v(id, content) where t.id = v.id",
                mudancas,
                template="(%s::uuid, %s)",
                page_size=200,
            )
    conn.commit()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--horas", type=int, default=3, help="limpa as notícias coletadas nessas últimas horas")
    parser.add_argument("--dias", type=int, help="limpa as notícias desses últimos dias (faxina geral)")
    parser.add_argument("--fonte", help="só as notícias desta fonte (sources.id)")
    parser.add_argument("--simular", action="store_true", help="mostra o que sairia, sem gravar")
    args = parser.parse_args()

    conn = get_connection()
    try:
        conhecidos = trechos_conhecidos(conn)
        tabelas = {"articles": TABELAS["articles"]} if args.fonte else TABELAS
        for tabela, coluna in tabelas.items():
            achados = descobrir_repetidos(conn, tabela, coluna)
            novos = {(f, t) for f, ts in achados.items() for t in ts - conhecidos[f]}
            noticias = noticias_pra_limpar(conn, tabela, coluna, args, {t for _, t in novos})

            mudancas, vistos, exemplos = [], set(), []
            for n in noticias:
                fonte = n["fonte"]
                fora = achados[fonte] | conhecidos[fonte]
                limpo = limpar_texto(n["content"], fora) or None
                if limpo == n["content"]:
                    continue
                mudancas.append((n["id"], limpo))
                paragrafos = {" ".join(l.split()) for l in n["content"].split("\n")}
                vistos.update((fonte, t) for t in fora if t in paragrafos)
                if len(exemplos) < 5:
                    ficou = set((limpo or "").split("\n"))
                    exemplos.append([p for p in paragrafos if p and p not in ficou])

            print(
                f"{tabela}: {len(mudancas)} de {len(noticias)} texto(s) limpo(s), "
                f"{len(novos)} trecho(s) repetido(s) novo(s)"
            )
            if args.simular:
                for _, trecho in sorted(novos)[:20]:
                    print(f"  repetido: {trecho[:110]}")
                for saiu in exemplos:
                    print(f"  saiu de uma notícia: {[s[:70] for s in saiu[:4]]}")
                continue
            gravar(conn, tabela, mudancas, sorted(vistos | novos))

        if not args.simular:
            with conn.cursor() as cur:
                cur.execute(
                    "delete from trechos_repetidos where visto_em < now() - make_interval(days => %s)",
                    (DIAS_PRA_ESQUECER,),
                )
                if cur.rowcount:
                    print(f"{cur.rowcount} trecho(s) esquecido(s) (mais de {DIAS_PRA_ESQUECER} dias sem aparecer)")
            conn.commit()
    finally:
        conn.close()


if __name__ == "__main__":
    main()
