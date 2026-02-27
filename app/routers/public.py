from fastapi import APIRouter
from app.database.postgres import get_conn
from app.database.mongo import db
from app.database.minio_client import client

router = APIRouter(prefix="/public")


@router.get("/overview")
def public_overview():
    result = {}

    # 1️⃣ POSTGRES
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT class_id, class_name FROM classes WHERE is_deleted=false")
    rows = cur.fetchall()
    conn.close()

    result["postgres"] = [
        {"id": r[0], "name": r[1]} for r in rows
    ]

    # 2️⃣ MONGO
    collections = db.list_collection_names()
    result["mongo"] = collections

    # 3️⃣ MINIO
    buckets = [b.name for b in client.list_buckets()]
    result["minio"] = buckets

    return result
