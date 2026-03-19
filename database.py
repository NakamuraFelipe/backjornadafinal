import psycopg
from psycopg.rows import dict_row
import socket
import time

DB_URL = "postgresql://postgres:UTbtJ7rkB1gPYE91@db.xzzgjndcfwomumrmcumo.supabase.co:5432/postgres?sslmode=require"

def get_db_connection(retries=3, delay=2):
    """
    Conecta ao banco Supabase forçando IPv4 e com retry automático.
    
    :param retries: número de tentativas caso falhe a conexão
    :param delay: tempo (em segundos) entre tentativas
    :return: conexão psycopg
    """
    last_exception = None

    # Resolver hostname para IPv4
    host = DB_URL.split("@")[1].split(":")[0]
    port = int(DB_URL.split(":")[-1].split("/")[0])
    try:
        ipv4 = socket.gethostbyname(host)
        # Substitui host pelo IPv4
        db_url_ipv4 = DB_URL.replace(host, ipv4)
    except Exception as e:
        print("Erro ao resolver IPv4:", e)
        db_url_ipv4 = DB_URL  # fallback para tentar sem IPv4

    for attempt in range(1, retries + 1):
        try:
            conn = psycopg.connect(
                db_url_ipv4,
                row_factory=dict_row,
                connect_timeout=10
            )
            return conn
        except Exception as e:
            print(f"Tentativa {attempt} falhou: {e}")
            last_exception = e
            time.sleep(delay)

    # Se todas as tentativas falharem, lança a última exceção
    raise last_exception