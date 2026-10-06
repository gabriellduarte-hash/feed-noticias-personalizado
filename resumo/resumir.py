"""
Gera um resumo por artigo com a API do Gemini, classifica cada artigo
numa categoria editorial fixa (Tecnologia, Finanças, etc.) e grava
categoria+resumo de volta em `articles` (o hub mostra os dois).

Roda junto da coleta, de hora em hora (workflow "Coleta de notícias").
Montar e enviar o e-mail é do envio/enviar.py, no horário que cada
usuário escolheu (sql/024).

Importante: "tópico" (o que o usuário cadastrou pra acompanhar, ex.:
"Inteligência Artificial") e "categoria" (a classificação editorial do
conteúdo, ex.: "Tecnologia") são coisas diferentes. O tópico decide o
que é coletado; a categoria decide como o e-mail final é organizado.
"""
import random
import time
from typing import Literal, get_args

from google import genai
from psycopg2.extras import RealDictCursor
from pydantic import BaseModel

from db import get_connection

MODEL = "gemini-3.8-flash"  # tier pago; se der erro de "modelo não encontrado",
                            # confira o nome atual em ai.google.dev/gemini-api/docs/pricing
MAX_CARACTERES_POR_ARTIGO = 2000  # trunca artigos longos pra não gastar tokens à toa
MAX_TENTATIVAS = 5             # tentativas de chamada à API (erro de rede/503)
ESPERA_BASE_SEGUNDOS = 2
ESPERA_MAXIMA_SEGUNDOS = 60

# Volume: em 05/10, 182 artigos de uma coleção foram numa chamada só, a
# resposta passou do limite de tamanho, veio cortada e o job travou por
# 25 min. Agora vai em lotes, com teto por rodada (o resto fica pra
# próxima hora) e reserva (sql/026) pra dois jobs não pegarem o mesmo.
TAMANHO_LOTE = 20
MAX_POR_RODADA = 120
TEMPO_MAXIMO_SEGUNDOS = 12 * 60   # o workflow tem 30 min; sobra pro resto
MAX_TENTATIVAS_ARTIGO = 3         # depois disso, desiste do artigo
RESERVA_EXPIRA = "30 minutes"     # reserva de um job que caiu volta a valer

# Categorias fixas: mantém o agrupamento do feed consistente entre
# rodadas (se o modelo pudesse inventar qualquer string, "Tecnologia" e
# "Tech" virariam grupos diferentes por acidente).
Categoria = Literal[
    "Tecnologia", "Finanças", "Humor", "Política", "Ciência",
    "Saúde", "Esportes", "Entretenimento", "Mundo", "Outros",
]
CATEGORIAS = get_args(Categoria)

SYSTEM_INSTRUCTION = (
    "Você é um assistente que resume notícias para um feed diário por e-mail. "
    "Para cada artigo recebido, escreva um resumo curto (2-4 frases) em "
    "português, sem inventar informação que não esteja no texto, e classifique "
    "o artigo em UMA categoria da lista: " + ", ".join(CATEGORIAS) + ". "
    "Use 'Outros' só se nenhuma outra categoria fizer sentido."
)


class ResumoArtigo(BaseModel):
    indice: int  # 1-based, corresponde ao "Artigo N" do prompt
    resumo: str
    categoria: Categoria


class ResumoTopico(BaseModel):
    artigos: list[ResumoArtigo]


def reservar_lote(conn, limite):
    """Reserva até `limite` artigos sem resumo (os mais novos primeiro) e
    devolve agrupados por tópico.

    "for update skip locked" + marcar resumo_reservado_em: se outro job
    estiver reservando ao mesmo tempo, cada um fica com artigos
    diferentes. O commit no fim fecha a transação ANTES de chamar a IA —
    deixar a transação aberta durante a espera foi o que segurou a
    tabela e travou o sql/025 em 05/10.
    """
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute(
            f"""
            with escolhidos as (
                select id from articles
                where category is null
                  and resumo_tentativas < %(max_tentativas)s
                  and (resumo_reservado_em is null
                       or resumo_reservado_em < now() - interval '{RESERVA_EXPIRA}')
                order by collected_at desc
                limit %(limite)s
                for update skip locked
            )
            update articles a
            set resumo_reservado_em = now(), resumo_tentativas = a.resumo_tentativas + 1
            from escolhidos e
            where a.id = e.id
            returning a.id
            """,
            {"limite": limite, "max_tentativas": MAX_TENTATIVAS_ARTIGO},
        )
        ids = [linha["id"] for linha in cur.fetchall()]
        linhas = []
        if ids:
            cur.execute(
                """
                select articles.id, topics.name as topic_name,
                       articles.title, articles.url, articles.content,
                       articles.author, articles.published_at
                from articles
                join sources on sources.id = articles.source_id
                join topics on topics.id = sources.topic_id
                where articles.id = any(%s::uuid[])
                order by topics.name, articles.collected_at
                """,
                (ids,),
            )
            linhas = cur.fetchall()
    conn.commit()

    por_topico = {}
    for linha in linhas:
        por_topico.setdefault(linha["topic_name"], []).append(linha)
    return por_topico


def montar_input(topico, artigos):
    partes = [
        f"Artigo {i + 1}: {a['title']}\n{(a['content'] or '')[:MAX_CARACTERES_POR_ARTIGO]}"
        for i, a in enumerate(artigos)
    ]
    corpo = "\n\n".join(partes)
    return (
        f"Tópico: {topico}\n\n"
        f"Resuma e classifique cada um dos {len(artigos)} artigos abaixo, "
        "na mesma ordem (indice 1 = Artigo 1, etc.).\n\n" + corpo
    )


def resumir_artigos_do_topico(client, topico, artigos):
    """Chama o Gemini com retry + backoff exponencial, pedindo saída
    estruturada (JSON) com um resumo + categoria por artigo.

    Antes isso pegava exceções tipadas (ServerError/ClientError) do SDK
    — na prática, um 503 "alta demanda" real não bateu com nenhuma das
    duas (motivo exato não identificado; pode ser diferença de versão
    do SDK ou da Interactions API especificamente). Trocado por uma
    checagem no texto do erro, mais grosseira mas não depende de
    acertar o tipo exato da exceção.
    """
    SINAIS_NAO_RETENTAVEIS = ("400", "401", "403", "404", "invalid", "permission", "api key")

    for tentativa in range(1, MAX_TENTATIVAS + 1):
        try:
            interaction = client.interactions.create(
                model=MODEL,
                system_instruction=SYSTEM_INSTRUCTION,
                input=montar_input(topico, artigos),
                generation_config={"maxOutputTokens": 8192},
                response_format={
                    "type": "text",
                    "mime_type": "application/json",
                    "schema": ResumoTopico.model_json_schema(),
                },
            )
            return ResumoTopico.model_validate_json(interaction.output_text)
        except Exception as erro:
            texto_erro = str(erro).lower()
            if any(sinal in texto_erro for sinal in SINAIS_NAO_RETENTAVEIS):
                raise
            motivo = str(erro)

        if tentativa == MAX_TENTATIVAS:
            raise RuntimeError(f"Gemini falhou após {MAX_TENTATIVAS} tentativas: {motivo}")

        espera = min(ESPERA_BASE_SEGUNDOS * (2 ** (tentativa - 1)), ESPERA_MAXIMA_SEGUNDOS)
        espera += random.uniform(0, 1)  # jitter, evita todo mundo tentar de novo no mesmo segundo
        print(f"  tentativa {tentativa}/{MAX_TENTATIVAS} falhou ({motivo}), esperando {espera:.1f}s...")
        time.sleep(espera)


def montar_cards(topico, artigos, resposta: ResumoTopico):
    """Junta o resumo/categoria (vindo do Gemini) com os dados reais do
    artigo (vindos do banco: título, url, autor, data). O modelo nunca
    vê nem inventa url/autor/data — isso evita alucinação nesses campos.
    """
    por_indice = {item.indice: item for item in resposta.artigos}
    cards = []
    for i, artigo in enumerate(artigos, start=1):
        item = por_indice.get(i)
        if item is None:
            print(f"  aviso: modelo não retornou resumo pro artigo {i} de '{topico}', pulando.")
            continue
        cards.append({
            "id": artigo["id"],
            "title": artigo["title"],
            "url": artigo["url"],
            "author": artigo["author"],
            "published_at": artigo["published_at"],
            "resumo": item.resumo,
            "categoria": item.categoria,
        })
    return cards


def salvar_categorizacao(conn, cards):
    """Grava categoria + resumo de volta em `articles` — vira dado
    estruturado reaproveitável (ex.: pelo hub de leitura em Next.js),
    em vez de existir só dentro do HTML do e-mail."""
    with conn.cursor() as cur:
        for card in cards:
            cur.execute(
                "update articles set category = %s, ai_summary = %s where id = %s",
                (card["categoria"], card["resumo"], card["id"]),
            )
    conn.commit()


def main():
    client = genai.Client()  # lê GEMINI_API_KEY do ambiente/.env
    conn = get_connection()
    inicio = time.monotonic()
    total = 0
    try:
        while total < MAX_POR_RODADA:
            if time.monotonic() - inicio > TEMPO_MAXIMO_SEGUNDOS:
                print("Tempo da rodada esgotado; o resto fica pra próxima.")
                break
            por_topico = reservar_lote(conn, min(TAMANHO_LOTE, MAX_POR_RODADA - total))
            if not por_topico:
                break
            for topico, artigos in por_topico.items():
                print(f"Resumindo '{topico}' ({len(artigos)} artigo(s))...")
                try:
                    resposta = resumir_artigos_do_topico(client, topico, artigos)
                except Exception as erro:
                    # a reserva expira em 30 min e o artigo volta pra fila
                    # (até MAX_TENTATIVAS_ARTIGO vezes)
                    print(f"  erro ao resumir '{topico}': {erro}")
                    continue
                cards = montar_cards(topico, artigos, resposta)
                salvar_categorizacao(conn, cards)  # grava e faz commit a cada lote
                total += len(cards)

        print(f"{total} artigo(s) resumidos e categorizados nesta rodada.")
    finally:
        conn.close()


if __name__ == "__main__":
    main()
