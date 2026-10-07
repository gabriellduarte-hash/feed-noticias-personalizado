"""
Gera um resumo por notícia com a API do Gemini e classifica cada uma numa
categoria editorial fixa (Tecnologia, Finanças, etc.). Duas fases:

  1. artigos das fontes dos usuários (`articles`): categoria sempre, e
     resumo só se tiver texto (TEXTO_MINIMO) — sempre primeiro, é o que
     vai pro feed e pro e-mail de cada um;
  2. notícias do catálogo (`catalog_articles`, aba Explorar): só o resumo
     (a categoria vem da fonte), só das que têm texto, com teto por hora
     por causa do custo.

O resumo sai em Markdown simples (parágrafos, **negrito** nos pontos
importantes, "> citação — autor" quando houver). O hub e o e-mail
(template.py) transformam isso em texto formatado.

Roda junto da coleta, de hora em hora (workflow "Coleta de notícias").

Importante: "tópico" (o que o usuário cadastrou pra acompanhar, ex.:
"Inteligência Artificial") e "categoria" (a classificação editorial do
conteúdo, ex.: "Tecnologia") são coisas diferentes. O tópico decide o
que é coletado; a categoria decide como o feed e o e-mail se organizam.
"""
import random
import time
from typing import Literal, get_args

from google import genai
from google.genai import types
from psycopg2.extras import RealDictCursor
from pydantic import BaseModel

from db import get_connection

MODEL = "gemini-3.8-flash"  # tier pago; se der erro de "modelo não encontrado",
                            # confira o nome atual em ai.google.dev/gemini-api/docs/pricing
MAX_CARACTERES_POR_ARTIGO = 2000  # trunca artigos longos pra não gastar tokens à toa
MAX_TENTATIVAS = 3                # tentativas por chamada à API (rede, 503, resposta cortada)
ESPERA_BASE_SEGUNDOS = 2
ESPERA_MAXIMA_SEGUNDOS = 30
# Sem tempo máximo, uma requisição presa segurava o passo inteiro até o
# GitHub matar o job (06/10: só 17 resumos no dia). Com ele, a requisição
# presa falha e é tentada de novo.
TIMEOUT_REQUISICAO_MS = 90_000

# Volume (05/10: 182 artigos numa chamada só travaram o job). Lotes
# pequenos, teto por rodada (o resto fica pra próxima hora) e reserva
# (sql/026 e 027) pra dois jobs nunca pegarem a mesma notícia.
TAMANHO_LOTE = 10                 # o resumo formatado é maior que o antigo
MAX_POR_RODADA = 120              # artigos dos usuários
# Catálogo: mil ou mais notícias novas por dia. A ~US$ 0,001 por resumo,
# 40/hora dá no máximo ~US$ 29/mês. Baixe pra gastar menos.
MAX_CATALOGO_POR_RODADA = 40
# Resumo só com texto de verdade. Abaixo disso (só o título, como nas
# notícias que chegam pelo Google Notícias, ou uma frase do feed), a IA
# "resume" o título e pode inventar detalhe. A notícia dos usuários
# ainda é categorizada, mas fica sem resumo: o hub mostra título e link.
TEXTO_MINIMO = 400
TEMPO_MAXIMO_SEGUNDOS = 11 * 60   # o passo tem 15 min; conferido antes de cada chamada
MAX_TENTATIVAS_ARTIGO = 3         # depois disso, desiste da notícia
RESERVA_EXPIRA = "30 minutes"     # reserva de um job que caiu volta a valer

# Categorias fixas: mantém o agrupamento consistente entre rodadas (se o
# modelo pudesse inventar qualquer string, "Tecnologia" e "Tech" virariam
# grupos diferentes por acidente).
Categoria = Literal[
    "Tecnologia", "Finanças", "Humor", "Política", "Ciência",
    "Saúde", "Esportes", "Entretenimento", "Mundo", "Outros",
]
CATEGORIAS = get_args(Categoria)

SYSTEM_INSTRUCTION = (
    "Você resume notícias para leitores brasileiros, num app focado em leitura. "
    "Para cada artigo recebido, escreva o resumo em português, em Markdown, sem inventar "
    "nada que não esteja no texto do artigo. Formato:\n"
    "- 2 a 4 parágrafos curtos, separados por uma linha em branco. O primeiro parágrafo "
    "conta o fato principal; os seguintes, contexto e consequências.\n"
    "- Marque em **negrito** de 2 a 4 trechos curtos com o que é mais importante "
    "(números, nomes, decisões, datas). Nunca uma frase inteira.\n"
    "- Se o artigo trouxer uma declaração relevante entre aspas, inclua UMA citação em "
    "parágrafo próprio, começando com '> ', e termine com ' — Nome' só se o texto disser "
    "quem falou. Nunca invente citação nem autor.\n"
    "- Sem títulos, listas ou links.\n"
    "- Se o artigo tiver pouco texto (só título ou uma ou duas frases), escreva um único "
    "parágrafo curto, sem completar com suposições.\n"
    "Classifique cada artigo em UMA categoria da lista: " + ", ".join(CATEGORIAS) + ". "
    "Use 'Outros' só se nenhuma outra fizer sentido."
)


class ResumoArtigo(BaseModel):
    indice: int  # 1-based, corresponde ao "Artigo N" do prompt
    resumo: str
    categoria: Categoria


class ResumoTopico(BaseModel):
    artigos: list[ResumoArtigo]


# ------------------------------------------------------------------ reserva

# Uma consulta de reserva por tabela. "for update skip locked" + marcar
# resumo_reservado_em: se outro job reservar ao mesmo tempo, cada um fica
# com notícias diferentes.
FILTRO_PENDENTES = {
    "articles": "category is null",
    "catalog_articles": f"ai_summary is null and length(content) >= {TEXTO_MINIMO}",
}

# Detalhes pra montar o pedido à IA. "grupo" é o contexto do lote: o
# tópico do usuário, ou a categoria da fonte no catálogo.
DETALHES = {
    "articles": """
        select a.id, t.name as grupo, a.title, a.url, a.content, a.author, a.published_at
        from articles a
        join sources s on s.id = a.source_id
        join topics t on t.id = s.topic_id
        where a.id = any(%s::uuid[])
        order by t.name, a.collected_at
    """,
    "catalog_articles": """
        select c.id, f.category as grupo, c.title, c.url, c.content, c.author, c.published_at
        from catalog_articles c
        join feed_catalog f on f.id = c.catalog_id
        where c.id = any(%s::uuid[])
        order by f.category, c.collected_at
    """,
}


def reservar_lote(conn, tabela, limite):
    """Reserva até `limite` notícias pendentes (as mais novas primeiro) e
    devolve agrupadas por tópico/categoria.

    O commit no fim fecha a transação ANTES de chamar a IA: deixar a
    transação aberta durante a espera segurou a tabela e travou o sql/025
    em 05/10.
    """
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute(
            f"""
            with escolhidos as (
                select id from {tabela}
                where {FILTRO_PENDENTES[tabela]}
                  and resumo_tentativas < %(max_tentativas)s
                  and (resumo_reservado_em is null
                       or resumo_reservado_em < now() - interval '{RESERVA_EXPIRA}')
                order by collected_at desc
                limit %(limite)s
                for update skip locked
            )
            update {tabela} t
            set resumo_reservado_em = now(), resumo_tentativas = t.resumo_tentativas + 1
            from escolhidos e
            where t.id = e.id
            returning t.id
            """,
            {"limite": limite, "max_tentativas": MAX_TENTATIVAS_ARTIGO},
        )
        ids = [linha["id"] for linha in cur.fetchall()]
        linhas = []
        if ids:
            cur.execute(DETALHES[tabela], (ids,))
            linhas = cur.fetchall()
    conn.commit()

    por_grupo = {}
    for linha in linhas:
        por_grupo.setdefault(linha["grupo"], []).append(linha)
    return por_grupo


# ------------------------------------------------------------------ IA

def tem_texto(artigo):
    return len(artigo["content"] or "") >= TEXTO_MINIMO


def montar_input(grupo, artigos):
    partes = [
        f"Artigo {i + 1}: {a['title']}\n{(a['content'] or '')[:MAX_CARACTERES_POR_ARTIGO]}"
        if tem_texto(a)
        else f"Artigo {i + 1}: {a['title']}\n(sem texto: só classifique, com o resumo vazio)"
        for i, a in enumerate(artigos)
    ]
    corpo = "\n\n".join(partes)
    return (
        f"Tópico: {grupo}\n\n"
        f"Resuma e classifique cada um dos {len(artigos)} artigos abaixo, "
        "na mesma ordem (indice 1 = Artigo 1, etc.).\n\n" + corpo
    )


def resumir_artigos(client, grupo, artigos):
    """Chama o Gemini (generate_content, saída estruturada em JSON) com
    retry e backoff exponencial.

    generate_content em vez da Interactions API: no teste de 06/10 foi
    mais rápida (2,6s contra 8,4s) e é a forma padrão do SDK.

    Erros "não adianta tentar de novo" (chave, permissão, pedido inválido)
    sobem direto; o resto (rede, 503, timeout, JSON cortado) tenta de novo.
    """
    SINAIS_NAO_RETENTAVEIS = ("400", "401", "403", "404", "invalid", "permission", "api key")
    config = types.GenerateContentConfig(
        system_instruction=SYSTEM_INSTRUCTION,
        response_mime_type="application/json",
        response_schema=ResumoTopico,
        max_output_tokens=8192,
    )

    for tentativa in range(1, MAX_TENTATIVAS + 1):
        try:
            resposta = client.models.generate_content(
                model=MODEL, contents=montar_input(grupo, artigos), config=config
            )
            return ResumoTopico.model_validate_json(resposta.text)
        except Exception as erro:
            texto_erro = str(erro).lower()
            if any(sinal in texto_erro for sinal in SINAIS_NAO_RETENTAVEIS):
                raise
            motivo = f"{type(erro).__name__}: {str(erro)[:200]}"

        if tentativa == MAX_TENTATIVAS:
            raise RuntimeError(f"Gemini falhou após {MAX_TENTATIVAS} tentativas: {motivo}")

        espera = min(ESPERA_BASE_SEGUNDOS * (2 ** (tentativa - 1)), ESPERA_MAXIMA_SEGUNDOS)
        espera += random.uniform(0, 1)  # jitter, evita todo mundo tentar de novo no mesmo segundo
        print(f"  tentativa {tentativa}/{MAX_TENTATIVAS} falhou ({motivo}), esperando {espera:.1f}s...")
        time.sleep(espera)


def casar_resumos(artigos, resposta: ResumoTopico):
    """Junta cada resumo (vindo do Gemini) com o id real da notícia. O
    modelo nunca vê nem inventa url/autor/data: isso evita alucinação
    nesses campos. Notícia sem resumo na resposta fica pendente (volta pra
    fila quando a reserva vencer, até MAX_TENTATIVAS_ARTIGO vezes)."""
    por_indice = {item.indice: item for item in resposta.artigos}
    casados = []
    for i, artigo in enumerate(artigos, start=1):
        item = por_indice.get(i)
        if item is None:
            print(f"  aviso: o modelo não devolveu resumo pro artigo {i}, fica pra depois.")
            continue
        # sem texto suficiente, o que a IA escrever é paráfrase do título: descarta
        resumo = item.resumo.strip() if tem_texto(artigo) else None
        casados.append({"id": artigo["id"], "resumo": resumo or None, "categoria": item.categoria})
    return casados


def salvar(conn, tabela, casados):
    """articles: resumo + categoria. catalog_articles: só o resumo (a
    categoria do catálogo vem da fonte, em feed_catalog)."""
    with conn.cursor() as cur:
        for c in casados:
            if tabela == "articles":
                cur.execute(
                    "update articles set category = %s, ai_summary = %s where id = %s",
                    (c["categoria"], c["resumo"], c["id"]),
                )
            else:
                cur.execute("update catalog_articles set ai_summary = %s where id = %s", (c["resumo"], c["id"]))
    conn.commit()


# ------------------------------------------------------------------ rodada

def processar(client, conn, tabela, teto, inicio):
    total = 0
    while total < teto:
        if time.monotonic() - inicio > TEMPO_MAXIMO_SEGUNDOS:
            print("  tempo da rodada esgotado; o resto fica pra próxima hora.")
            return total, True
        por_grupo = reservar_lote(conn, tabela, min(TAMANHO_LOTE, teto - total))
        if not por_grupo:
            break
        for grupo, artigos in por_grupo.items():
            if time.monotonic() - inicio > TEMPO_MAXIMO_SEGUNDOS:
                # as reservadas e não processadas voltam pra fila em 30 min
                print("  tempo da rodada esgotado; o resto fica pra próxima hora.")
                return total, True
            print(f"  '{grupo}': {len(artigos)} notícia(s)...")
            try:
                resposta = resumir_artigos(client, grupo, artigos)
            except Exception as erro:
                print(f"  erro ao resumir '{grupo}': {erro}")
                continue
            casados = casar_resumos(artigos, resposta)
            salvar(conn, tabela, casados)  # grava e faz commit a cada lote
            total += len(casados)
    return total, False


def main():
    client = genai.Client(http_options={"timeout": TIMEOUT_REQUISICAO_MS})
    conn = get_connection()
    inicio = time.monotonic()
    try:
        print("Artigos das fontes dos usuários:")
        feitos, esgotou = processar(client, conn, "articles", MAX_POR_RODADA, inicio)
        print(f"  {feitos} resumido(s) e categorizado(s).")

        if not esgotou:
            print("Notícias do catálogo (aba Explorar):")
            feitos, _ = processar(client, conn, "catalog_articles", MAX_CATALOGO_POR_RODADA, inicio)
            print(f"  {feitos} resumida(s).")
    finally:
        conn.close()


if __name__ == "__main__":
    main()
