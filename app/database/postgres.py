import psycopg2
from urllib.parse import urlparse
from app.config import POSTGRES_URL


def get_conn():
    parsed = urlparse(POSTGRES_URL)

    return psycopg2.connect(
        dbname=parsed.path.lstrip("/"),
        user=parsed.username,
        password=parsed.password,
        host=parsed.hostname,
        port=parsed.port
    )
