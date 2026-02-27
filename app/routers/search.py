from fastapi import APIRouter, Query
from app.database.postgres import get_conn

router = APIRouter(prefix="/search")

@router.get("/")
def search(q: str = Query(...)):
    conn = get_conn()
    cur = conn.cursor()

    cur.execute("""
        SELECT lesson_id, title, content
        FROM lesson
        WHERE is_deleted = false
        AND (
            title ILIKE %s
            OR content ILIKE %s
        )
        LIMIT 100
    """, (f"%{q}%", f"%{q}%"))

    rows = cur.fetchall()
    conn.close()

    return [
        {"lesson_id": r[0], "title": r[1], "content": r[2][:200]}
        for r in rows
    ]
