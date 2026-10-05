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
MAX_TENTATIVAS = 5
ESPERA_BASE_SEGUNDOS = 2
ESPERA_MAXIMA_SEGUNDOS = 60

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


def buscar_artigos_por_topico(conn):
    """Agrupa por tópico os artigos ainda não categorizados.

    `category is null` faz dupla função: evita reprocessar (e pagar de
    novo) um artigo que já foi resumido, e naturalmente escopa cada
    rodada só pro que é novo — o mesmo efeito prático que um filtro de
    data traria, sem precisar de um.
    """
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute(
            """
            select articles.id, topics.name as topic_name,
                   articles.title, articles.url, articles.content,
                   articles.author, articles.published_at
            from articles
            join sources on sources.id = articles.source_id
            join topics on topics.id = sources.topic_id
            where articles.category is null
            order by topics.name, articles.collected_at
            """
        )
        linhas = cur.fetchall()

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
                generation_config={"maxOutputTokens": 4096},
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
    try:
        por_topico = buscar_artigos_por_topico(conn)
        if not por_topico:
            print("Nenhum artigo novo pra resumir.")
            return

        total = 0
        for topico, artigos in por_topico.items():
            print(f"Resumindo '{topico}' ({len(artigos)} artigo(s))...")
            try:
                resposta = resumir_artigos_do_topico(client, topico, artigos)
            except Exception as erro:
                print(f"  erro ao resumir '{topico}': {erro}")
                continue
            cards = montar_cards(topico, artigos, resposta)
            # grava por tópico: se um tópico falhar depois, os anteriores
            # já ficam salvos e não são pagos de novo na próxima rodada
            salvar_categorizacao(conn, cards)
            total += len(cards)

        print(f"{total} artigo(s) resumidos e categorizados em `articles`.")
    finally:
        conn.close()


if __name__ == "__main__":
    main()
