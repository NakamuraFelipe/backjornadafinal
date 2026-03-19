import psycopg
from psycopg.rows import dict_row

def get_db_connection():
    conn = psycopg.connect(
        host="db.xzzgjndcfwomumrmcumo.supabase.co",
        user="postgres",
        password="UTbtJ7rkB1gPYE91",
        dbname="postgres",
        port=5432,
        row_factory=dict_row
    )
    return conn