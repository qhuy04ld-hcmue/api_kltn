from app.database.mongo import db
from app.database.neo4j import driver

def sync_to_mongo(collection, data):
    db[collection].update_one(
        {"id": data["id"]},
        {"$set": data},
        upsert=True
    )

def sync_to_neo4j(label, data):
    with driver.session() as session:
        session.run(
            f"""
            MERGE (n:{label} {{id: $id}})
            SET n += $props
            """,
            id=data["id"],
            props=data
        )
