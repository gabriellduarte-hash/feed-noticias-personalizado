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
