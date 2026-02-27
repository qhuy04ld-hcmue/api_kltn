from sqlalchemy import text
from ..database import SessionLocal
from neo4j import GraphDatabase
from app.config import NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD
from app.services.mongo_service import get_lesson_files


def search_by_keyword(keyword: str, limit: int = 20, offset: int = 0):
    db = SessionLocal()
    try:
        result = db.execute(text("""
            SELECT DISTINCT l.lesson_id,
                            l.lesson_name,
                            t.topic_id,
                            s.subject_id,
                            c.class_id,
                            l.created_at
            FROM lessons l
            JOIN topics t ON l.topic_id = t.topic_id
            JOIN subjects s ON t.subject_id = s.subject_id
            JOIN classes c ON s.class_id = c.class_id
            LEFT JOIN chunks ch ON ch.lesson_id = l.lesson_id
            LEFT JOIN lesson_keywords lk ON lk.lesson_id = l.lesson_id
            LEFT JOIN keywords k ON k.keyword_id = lk.keyword_id
            WHERE l.is_deleted = FALSE AND (
                l.lesson_name ILIKE :kw
                OR l.description ILIKE :kw
                OR ch.content ILIKE :kw
                OR k.keyword_name ILIKE :kw
            )
            ORDER BY l.created_at DESC
            LIMIT :limit OFFSET :offset
        """), {
            "kw": f"%{keyword}%",
            "limit": limit,
            "offset": offset
        })

        lessons = [dict(row._mapping) for row in result]

        # Gắn file từ Mongo
        for lesson in lessons:
            lesson["files"] = get_lesson_files(lesson["lesson_id"])

        return lessons

    finally:
        db.close()


def search_by_graph(class_id=None, subject_id=None, topic_id=None):
    driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))

    query = """
    MATCH (c:Class)-[:HAS_SUBJECT]->(s:Subject)
          -[:HAS_TOPIC]->(t:Topic)
          -[:HAS_LESSON]->(l:Lesson)
    WHERE
        ($class_id IS NULL OR c.id = $class_id) AND
        ($subject_id IS NULL OR s.id = $subject_id) AND
        ($topic_id IS NULL OR t.id = $topic_id)
    RETURN l.id AS lesson_id,
           l.name AS lesson_name,
           t.id AS topic_id,
           s.id AS subject_id,
           c.id AS class_id
    """

    with driver.session() as session:
        result = session.run(query, {
            "class_id": class_id,
            "subject_id": subject_id,
            "topic_id": topic_id
        })

        lessons = [record.data() for record in result]

        for lesson in lessons:
            lesson["files"] = get_lesson_files(lesson["lesson_id"])

        return lessons



'''
from sqlalchemy import text
from ..database import SessionLocal
from neo4j import GraphDatabase
from app.config import NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD # Nên dùng từ config

def search_by_keyword(keyword: str, limit: int = 20, offset: int = 0):
    db = SessionLocal()
    try:
        # Đã đổi lesson_title -> lesson_name
        result = db.execute(text("""
            SELECT DISTINCT l.lesson_id,
                            l.lesson_name,
                            t.topic_id,
                            s.subject_id,
                            c.class_id,
                            l.created_at
            FROM lessons l
            JOIN topics t ON l.topic_id = t.topic_id
            JOIN subjects s ON t.subject_id = s.subject_id
            JOIN classes c ON s.class_id = c.class_id
            LEFT JOIN chunks ch ON ch.lesson_id = l.lesson_id
            LEFT JOIN lesson_keywords lk ON lk.lesson_id = l.lesson_id
            LEFT JOIN keywords k ON k.keyword_id = lk.keyword_id
            WHERE l.is_deleted = FALSE AND (
                l.lesson_name ILIKE :kw
                OR l.description ILIKE :kw
                OR ch.content ILIKE :kw
                OR k.keyword_name ILIKE :kw
            )
            ORDER BY l.created_at DESC
            LIMIT :limit OFFSET :offset
        """), {
            "kw": f"%{keyword}%",
            "limit": limit,
            "offset": offset
        })
        return [dict(row._mapping) for row in result]
    finally:
        db.close()

def search_by_graph(class_id=None, subject_id=None, topic_id=None):
    # Sử dụng thông tin từ config thay vì viết cứng
    driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))

    query = """
    MATCH (c:Class)-[:HAS_SUBJECT]->(s:Subject)
          -[:HAS_TOPIC]->(t:Topic)
          -[:HAS_LESSON]->(l:Lesson)
    WHERE
        ($class_id IS NULL OR c.id = $class_id) AND
        ($subject_id IS NULL OR s.id = $subject_id) AND
        ($topic_id IS NULL OR t.id = $topic_id)
    RETURN l.id AS lesson_id,
           l.name AS lesson_name,
           t.id AS topic_id,
           s.id AS subject_id,
           c.id AS class_id
    """

    with driver.session() as session:
        result = session.run(query, {
            "class_id": class_id,
            "subject_id": subject_id,
            "topic_id": topic_id
        })
        return [record.data() for record in result]
'''