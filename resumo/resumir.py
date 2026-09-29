"""
Gera um resumo por artigo com a API do Gemini, classifica cada artigo
numa categoria editorial fixa (Tecnologia, Finanças, etc.), monta o
HTML do e-mail em formato de feed agrupado por categoria
(resumo/template.py) e salva em `digests`.

Importante: "tópico" (o que o usuário cadastrou pra acompanhar, ex.:
"Inteligência Artificial") e "categoria" (a classificação editorial do
conteúdo, ex.: "Tecnologia") são coisas diferentes. O tópico decide o
que é coletado; a categoria decide como o e-mail final é organizado.
"""
import os
import random
import time
from datetime import date
from typing import Literal, get_args

from google import genai
from google.genai.errors import ClientError, ServerError
from psycopg2.extras import RealDictCursor
from pydantic import BaseModel

from db import get_connection
from template import montar_email_html

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
    """Agrupa os artigos coletados por tópico.

    Protótipo: pega todos os artigos, sem filtro de data. Quando o
    agendador estiver rodando de verdade (1x/dia), trocar o SELECT por
    um filtro em `articles.collected_at > now() - interval '24 hours'`.
    """
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute(
            """
            select topics.name as topic_name,
                   articles.title, articles.url, articles.content,
                   articles.author, articles.published_at
            from articles
            join sources on sources.id = articles.source_id
            join topics on topics.id = sources.topic_id
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

    ServerError (5xx, ex.: 503 "alta demanda") e ClientError 429 (rate
    limit) são erros passageiros — vale tentar de novo, inclusive no
    tier pago (quota maior, mas ainda existe). Qualquer outro
    ClientError (400, 401, 404, ...) é erro de verdade (prompt inválido,
    chave errada, etc.) e não adianta insistir, então propaga na hora.
    """
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
        except ServerError as erro:
            motivo = f"servidor sobrecarregado ({erro.code})"
        except ClientError as erro:
            if erro.code != 429:
                raise
            motivo = "rate limit (429)"

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
            "title": artigo["title"],
            "url": artigo["url"],
            "author": artigo["author"],
            "published_at": artigo["published_at"],
            "resumo": item.resumo,
            "categoria": item.categoria,
        })
    return cards


def agrupar_por_categoria(cards):
    grupos = {categoria: [] for categoria in CATEGORIAS}
    for card in cards:
        grupos[card["categoria"]].append(card)
    return {categoria: itens for categoria, itens in grupos.items() if itens}


def salvar_digest(conn, user_id, html):
    with conn.cursor() as cur:
        cur.execute(
            """
            insert into digests (user_id, digest_date, html_content)
            values (%s, current_date, %s)
            on conflict (user_id, digest_date)
            do update set html_content = excluded.html_content
            returning id, created_at
            """,
            (user_id, html),
        )
        linha = cur.fetchone()
    conn.commit()
    return linha


def main():
    user_id = os.environ["FEED_USER_ID"]
    client = genai.Client()  # lê GEMINI_API_KEY do ambiente/.env
    conn = get_connection()
    try:
        por_topico = buscar_artigos_por_topico(conn)
        if not por_topico:
            print("Nenhum artigo encontrado no banco.")
            return

        todos_os_cards = []
        for topico, artigos in por_topico.items():
            print(f"Resumindo '{topico}' ({len(artigos)} artigo(s))...")
            try:
                resposta = resumir_artigos_do_topico(client, topico, artigos)
            except Exception as erro:
                print(f"  erro ao resumir '{topico}': {erro}")
                continue
            todos_os_cards.extend(montar_cards(topico, artigos, resposta))

        if not todos_os_cards:
            print("Nenhum resumo gerado, nada a salvar.")
            return

        cards_por_categoria = agrupar_por_categoria(todos_os_cards)
        html = montar_email_html(cards_por_categoria, date.today())

        with open("preview.html", "w", encoding="utf-8") as f:
            f.write(html)
        print("Prévia salva em resumo/preview.html — abre no navegador pra ver como ficou.")

        salvar_digest(conn, user_id, html)
        print("Digest salvo na tabela `digests`.")
    finally:
        conn.close()


if __name__ == "__main__":
    main()
