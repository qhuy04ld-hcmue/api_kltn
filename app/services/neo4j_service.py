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

from neo4j import GraphDatabase
from app.config import NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD


driver = GraphDatabase.driver(
    NEO4J_URI,
    auth=(NEO4J_USER, NEO4J_PASSWORD)
)


def get_graph():
    """
    Trả về danh sách node và relationship
    cho admin dashboard hiển thị graph.
    """

    with driver.session() as session:

        # Lấy node
        nodes_result = session.run("""
            MATCH (n)
            RETURN id(n) as id, labels(n) as labels, properties(n) as props
            LIMIT 300
        """)

        nodes = []
        for record in nodes_result:
            nodes.append({
                "id": record["id"],
                "label": record["labels"][0] if record["labels"] else "Node",
                "title": str(record["props"])
            })

        # Lấy relationship
        rels_result = session.run("""
            MATCH (a)-[r]->(b)
            RETURN id(a) as source,
                   id(b) as target,
                   type(r) as type
            LIMIT 500
        """)

        edges = []
        for record in rels_result:
            edges.append({
                "from": record["source"],
                "to": record["target"],
                "label": record["type"]
            })

    return {
        "nodes": nodes,
        "edges": edges
    }
