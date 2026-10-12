import os

import psycopg2
from dotenv import load_dotenv

load_dotenv()


def get_connection():
    dsn = os.environ["DATABASE_URL"]
    conn = psycopg2.connect(dsn)
    # Rede de segurança: se um script deixar uma transação aberta parada
    # (ex.: leu do banco e foi esperar a IA ou um site), o banco derruba a
    # conexão em 5 min, em vez de segurar a tabela por meia hora e travar
    # migrações e outros jobs (aconteceu em 05/10 com o resumir.py).
    with conn.cursor() as cur:
        cur.execute("set idle_in_transaction_session_timeout = '5min'")
    conn.commit()
    return conn


def resolver_feed(conn, id_):
    """--fonte aceita o id do feed (feeds.id) ou o de quem segue
    (sources.id): desde o sql/038 a coleta é por feed, mas um disparo
    antigo do hub ainda pode mandar o da fonte."""
    if not id_:
        return None
    with conn.cursor() as cur:
        cur.execute(
            "select id from feeds where id = %(id)s::uuid "
            "union all select feed_id from sources where id = %(id)s::uuid limit 1",
            {"id": id_},
        )
        linha = cur.fetchone()
    conn.commit()
    return str(linha[0]) if linha else id_
