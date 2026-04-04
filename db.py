import psycopg2
from psycopg2.extras import RealDictCursor
from config import Config


def get_connection(dict_cursor=False):
    """
    建立 PostgreSQL 連線

    參數:
        dict_cursor (bool):
            True  -> 回傳 dict 形式資料列
            False -> 回傳 tuple 形式資料列

    回傳:
        psycopg2 connection
    """
    cursor_factory = RealDictCursor if dict_cursor else None

    conn = psycopg2.connect(
        host=Config.DB_HOST,
        dbname=Config.DB_NAME,
        user=Config.DB_USER,
        password=Config.DB_PASSWORD,
        port=Config.DB_PORT,
        cursor_factory=cursor_factory
    )
    return conn