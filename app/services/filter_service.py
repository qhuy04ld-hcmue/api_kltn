from sqlalchemy import text
from ..database import SessionLocal
from app.database import SessionLocal
from app.services.mongo_service import get_lesson_files


def filter_lessons(
    class_id=None,
    subject_id=None,
    topic_id=None,
    lesson_id=None,
    start_date=None,
    end_date=None,
    limit=20,
    offset=0
):
    db = SessionLocal()
    try:
        query = """
        SELECT l.lesson_id,
               l.lesson_name, 
               t.topic_id,
               s.subject_id,
               c.class_id,
               l.created_at
        FROM lessons l
        JOIN topics t ON l.topic_id = t.topic_id
        JOIN subjects s ON t.subject_id = s.subject_id
        JOIN classes c ON s.class_id = c.class_id
        WHERE l.is_deleted = FALSE
        """

        params = {}

        if class_id:
            query += " AND c.class_id = :class_id"
            params["class_id"] = class_id
        if subject_id:
            query += " AND s.subject_id = :subject_id"
            params["subject_id"] = subject_id
        if topic_id:
            query += " AND t.topic_id = :topic_id"
            params["topic_id"] = topic_id
        if lesson_id:
            query += " AND l.lesson_id = :lesson_id"
            params["lesson_id"] = lesson_id
        if start_date:
            query += " AND l.created_at >= :start_date"
            params["start_date"] = start_date
        if end_date:
            query += " AND l.created_at <= :end_date"
            params["end_date"] = end_date

        query += " ORDER BY l.created_at DESC LIMIT :limit OFFSET :offset"
        params["limit"] = limit
        params["offset"] = offset

        result = db.execute(text(query), params)
        lessons = [dict(row._mapping) for row in result]

        # Gắn file từ Mongo
        for lesson in lessons:
            lesson["files"] = get_lesson_files(lesson["lesson_id"])

        return lessons

    finally:
        db.close()


'''
from sqlalchemy import text
from ..database import SessionLocal

def filter_lessons(
    class_id=None,
    subject_id=None,
    topic_id=None,
    lesson_id=None,
    start_date=None,
    end_date=None,
    limit=20,
    offset=0
):
    db = SessionLocal()
    try:
        # Đã đổi l.lesson_title thành l.lesson_name
        query = """
        SELECT l.lesson_id,
               l.lesson_name, 
               t.topic_id,
               s.subject_id,
               c.class_id,
               l.created_at
        FROM lessons l
        JOIN topics t ON l.topic_id = t.topic_id
        JOIN subjects s ON t.subject_id = s.subject_id
        JOIN classes c ON s.class_id = c.class_id
        WHERE l.is_deleted = FALSE
        """

        params = {}

        if class_id:
            query += " AND c.class_id = :class_id"
            params["class_id"] = class_id
        if subject_id:
            query += " AND s.subject_id = :subject_id"
            params["subject_id"] = subject_id
        if topic_id:
            query += " AND t.topic_id = :topic_id"
            params["topic_id"] = topic_id
        if lesson_id:
            query += " AND l.lesson_id = :lesson_id"
            params["lesson_id"] = lesson_id
        if start_date:
            query += " AND l.created_at >= :start_date"
            params["start_date"] = start_date
        if end_date:
            query += " AND l.created_at <= :end_date"
            params["end_date"] = end_date

        query += " ORDER BY l.created_at DESC LIMIT :limit OFFSET :offset"
        params["limit"] = limit
        params["offset"] = offset

        result = db.execute(text(query), params)
        return [dict(row._mapping) for row in result]
    finally:
        db.close()
'''