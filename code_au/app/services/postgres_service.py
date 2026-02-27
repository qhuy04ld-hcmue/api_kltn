from sqlalchemy import create_engine, text
from app.config import POSTGRES_URL

engine = create_engine(POSTGRES_URL)

def lesson_exists(lesson_id):
    with engine.connect() as conn:
        result = conn.execute(
            text("SELECT 1 FROM lessons WHERE lesson_id = :id"),
            {"id": lesson_id}
        ).fetchone()
        return result is not None

def upsert_class(class_code, class_name):
    with engine.begin() as conn:
        conn.execute(text("""
        INSERT INTO classes (class_code, class_name)
        VALUES (:code, :name)
        ON CONFLICT (class_code)
        DO UPDATE SET class_name = EXCLUDED.class_name
        """), {"code": class_code, "name": class_name})


def upsert_subject(class_code, subject_code, subject_name):
    with engine.begin() as conn:
        conn.execute(text("""
        INSERT INTO subjects (class_id, subject_code, subject_name)
        VALUES (:class_id, :subject_code, :subject_name)
        ON CONFLICT (class_id, subject_code)
        DO UPDATE SET subject_name = EXCLUDED.subject_name
        """), {
            "class_id": class_code,
            "subject_code": subject_code,
            "subject_name": subject_name
        })


def upsert_topic(subject_id, topic_order, topic_name):
    with engine.begin() as conn:
        conn.execute(text("""
        INSERT INTO topics (subject_id, topic_order, topic_name)
        VALUES (:subject_id, :topic_order, :topic_name)
        ON CONFLICT (subject_id, topic_order)
        DO UPDATE SET topic_name = EXCLUDED.topic_name
        """), locals())


def upsert_lesson(topic_id, lesson_order, lesson_name, description):
    with engine.begin() as conn:
        conn.execute(text("""
        INSERT INTO lessons (topic_id, lesson_order, lesson_name, description)
        VALUES (:topic_id, :lesson_order, :lesson_name, :description)
        ON CONFLICT (topic_id, lesson_order)
        DO UPDATE SET
            lesson_name = EXCLUDED.lesson_name,
            description = EXCLUDED.description
        """), locals())
def upsert_structure(
    class_code,
    class_name,
    subject_code,
    subject_name,
    topic_order,
    topic_name,
    lesson_order,
    lesson_name,
    description=""
):
    upsert_class(class_code, class_name)
    upsert_subject(class_code, subject_code, subject_name)

    subject_id = f"{class_code}-{subject_code}"
    upsert_topic(subject_id, topic_order, topic_name)

    topic_id = f"{subject_id}-T{str(topic_order).zfill(2)}"
    upsert_lesson(topic_id, lesson_order, lesson_name, description)

#support for crud 

def update_lesson_info(lesson_id, lesson_name, description):
    with engine.begin() as conn:
        conn.execute(text("""
        UPDATE lessons
        SET lesson_name = :lesson_name,
            description = :description,
            updated_at = NOW()
        WHERE lesson_id = :lesson_id
        """), locals())


def soft_delete_lesson(lesson_id):
    with engine.begin() as conn:
        conn.execute(text("""
        UPDATE lessons
        SET is_deleted = TRUE,
            updated_at = NOW()
        WHERE lesson_id = :lesson_id
        """), {"lesson_id": lesson_id})
# support for search and filter 

from sqlalchemy import text
from sqlalchemy.orm import Session

def filter_lessons_raw(db: Session, class_id: str = None, subject_id: str = None, 
                       topic_id: str = None, start_date: str = None, end_date: str = None):
    # Khởi tạo câu lệnh SQL cơ bản
    query_str = "SELECT * FROM lessons WHERE is_deleted = FALSE"
    params = {}

    # Lọc theo Class/Subject/Topic dựa trên tiền tố của lesson_id (C10-TIN-T01...)
    if class_id:
        query_str += " AND lesson_id LIKE :class_id"
        params["class_id"] = f"{class_id}%"
    if subject_id:
        query_str += " AND lesson_id LIKE :subject_id"
        params["subject_id"] = f"{subject_id}%"
    if topic_id:
        query_str += " AND topic_id = :topic_id"
        params["topic_id"] = topic_id
    
    # Lọc theo ngày tháng
    if start_date:
        query_str += " AND created_at >= :start_date"
        params["start_date"] = start_date
    if end_date:
        query_str += " AND created_at <= :end_date"
        params["end_date"] = end_date

    query_str += " ORDER BY lesson_order ASC"
    
    result = db.execute(text(query_str), params)
    # Chuyển đổi kết quả sang list of dicts
    return [dict(row._mapping) for row in result]