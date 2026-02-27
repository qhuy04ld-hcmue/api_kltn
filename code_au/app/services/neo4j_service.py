from neo4j import GraphDatabase
from app.config import *

driver = GraphDatabase.driver(
    NEO4J_URI,
    auth=(NEO4J_USER, NEO4J_PASSWORD)
)


def sync_graph(class_code, subject_code, topic_order, lesson_order):
    topic_code = f"T{str(topic_order).zfill(2)}"
    lesson_code = f"L{str(lesson_order).zfill(2)}"

    subject_id = f"{class_code}-{subject_code}"
    topic_id = f"{subject_id}-{topic_code}"
    lesson_id = f"{topic_id}-{lesson_code}"

    with driver.session() as session:
        session.run("""
        MERGE (thing:Thing {id:'THING'})

        MERGE (c:Class {id:$class})
        MERGE (s:Subject {id:$subject})
        MERGE (t:Topic {id:$topic})
        MERGE (l:Lesson {id:$lesson})

        MERGE (thing)-[:HAS_CLASS]->(c)
        MERGE (c)-[:HAS_SUBJECT]->(s)
        MERGE (s)-[:HAS_TOPIC]->(t)
        MERGE (t)-[:HAS_LESSON]->(l)
        """, {
            "class": class_code,
            "subject": subject_id,
            "topic": topic_id,
            "lesson": lesson_id
        })
#support for crud
def update_lesson_topic(lesson_id, new_topic_id):
    with driver.session() as session:
        session.run("""
        MATCH (l:Lesson {id:$lesson_id})-[r:HAS_TOPIC]->()
        DELETE r
        """, {"lesson_id": lesson_id})

        session.run("""
        MATCH (t:Topic {id:$topic_id}),
              (l:Lesson {id:$lesson_id})
        MERGE (t)-[:HAS_LESSON]->(l)
        """, {
            "lesson_id": lesson_id,
            "topic_id": new_topic_id
        })


def soft_delete_lesson(lesson_id):
    with driver.session() as session:
        session.run("""
        MATCH (l:Lesson {id:$lesson_id})
        SET l.is_deleted = true
        """, {"lesson_id": lesson_id})
