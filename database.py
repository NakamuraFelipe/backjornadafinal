import psycopg
from psycopg.rows import dict_row

def get_db_connection():
    conn = psycopg.connect(
        "postgresql://postgres:UTbtJ7rkB1gPYE91@db.xzzgjndcfwomumrmcumo.supabase.co:5432/postgres?sslmode=require",
        row_factory=dict_row
    )
    return conn