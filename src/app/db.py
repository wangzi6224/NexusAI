import psycopg
from psycopg.rows import dict_row

from src.app.config import get_settings


def get_connection():
    settings = get_settings()

    return psycopg.connect(
        host=settings.postgres_host,
        port=settings.postgres_port,
        dbname=settings.postgres_db,
        user=settings.postgres_user,
        password=settings.postgres_password,
        row_factory=dict_row,
    )
