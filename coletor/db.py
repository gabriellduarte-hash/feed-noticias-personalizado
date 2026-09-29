import os

import psycopg2
from dotenv import load_dotenv

load_dotenv()


def get_connection():
    dsn = os.environ["DATABASE_URL"]
    return psycopg2.connect(dsn)
