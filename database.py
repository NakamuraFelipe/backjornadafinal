import os
import psycopg
from psycopg.rows import dict_row

DB_URL = os.environ.get("DATABASE_URL")

def get_db_connection():
    return psycopg.connect(
        DB_URL,
        row_factory=dict_row,
        connect_timeout=10
    )