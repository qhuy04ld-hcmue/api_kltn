from fastapi import APIRouter
from app.database.postgres import get_conn

router = APIRouter(prefix="/filter")

@router.get("/")
def filter_data(
    class_id: str = None,
    subject_id: str = None,
    topic_id: str = None,
    lesson_id: str = None,
    from_date: str = None,
    to_date: str = None
):
    conn = get_conn()
    cur = conn.cursor()

    query = """
        SELECT lesson_id, title, created_at
        FROM lesson
        WHERE is_deleted = false
    """
    params = []

    if class_id:
        query += " AND class_id=%s"
        params.append(class_id)

    if subject_id:
        query += " AND subject_id=%s"
        params.append(subject_id)

    if topic_id:
        query += " AND topic_id=%s"
        params.append(topic_id)

    if lesson_id:
        query += " AND lesson_id=%s"
        params.append(lesson_id)

    if from_date:
        query += " AND created_at >= %s"
        params.append(from_date)

    if to_date:
        query += " AND created_at <= %s"
        params.append(to_date)

    query += " LIMIT 100"

    cur.execute(query, tuple(params))
    rows = cur.fetchall()
    conn.close()

    return [
        {"lesson_id": r[0], "title": r[1], "created_at": str(r[2])}
        for r in rows
    ]
