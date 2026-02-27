from fastapi import APIRouter
from app.database.neo4j import driver
from fastapi import APIRouter
from app.database import neo4j_driver

router = APIRouter(prefix="/neo4j", tags=["Neo4j"])

#router = APIRouter(prefix="/neo4j")

@router.get("/nodes")
def get_nodes():
    with driver.session() as session:
        result = session.run("MATCH (n) RETURN labels(n), properties(n) LIMIT 200")
        data = []
        for r in result:
            data.append({
                "labels": r[0],
                "properties": r[1]
            })
        return data


@router.get("/relations")
def get_relations():
    with driver.session() as session:
        result = session.run("""
            MATCH (a)-[r]->(b)
            RETURN labels(a), type(r), labels(b) LIMIT 200
        """)
        data = []
        for r in result:
            data.append({
                "from": r[0],
                "relation": r[1],
                "to": r[2]
            })
        return data



@router.get("/graph")
def get_graph():

    query = """
    MATCH (n)
    OPTIONAL MATCH (n)-[r]->(m)
    RETURN n, r, m
    """

    with neo4j_driver.session() as session:
        result = session.run(query)

        nodes = {}
        edges = []

        for record in result:
            n = record["n"]
            m = record["m"]
            r = record["r"]

            # ---- NODE N ----
            n_props = dict(n)
            n_label = list(n.labels)[0]

            # Business id phải tồn tại
            n_business_id = n_props.get("id")

            if n_business_id and n_business_id not in nodes:
                nodes[n_business_id] = {
                    "id": n_business_id,          # dùng business id
                    "label": n_label,
                    "properties": n_props
                }

            # ---- NODE M ----
            if m:
                m_props = dict(m)
                m_label = list(m.labels)[0]
                m_business_id = m_props.get("id")

                if m_business_id and m_business_id not in nodes:
                    nodes[m_business_id] = {
                        "id": m_business_id,
                        "label": m_label,
                        "properties": m_props
                    }

            # ---- EDGE ----
            if r:
                edges.append({
                    "from": dict(r.start_node).get("id"),
                    "to": dict(r.end_node).get("id"),
                    "label": r.type
                })

        return {
            "nodes": list(nodes.values()),
            "edges": edges
        }


'''
@router.get("/graph")
def get_graph():

    query = """
    MATCH (n)
    OPTIONAL MATCH (n)-[r]->(m)
    RETURN n, r, m
    """

    with neo4j_driver.session() as session:
        result = session.run(query)

        nodes = {}
        edges = []

        for record in result:

            n = record["n"]
            m = record["m"]
            r = record["r"]

            # Add node n
            if n.id not in nodes:
                nodes[n.id] = {
                    "id": n.id,
                    "label": n.get("name", list(n.labels)[0]),
                    "type": list(n.labels)[0],
                    "properties": dict(n)
                }

            # Add node m
            if m and m.id not in nodes:
                nodes[m.id] = {
                    "id": m.id,
                    "label": m.get("name", list(m.labels)[0]),
                    "type": list(m.labels)[0],
                    "properties": dict(m)
                }

            # Add edge
            if r:
                edges.append({
                    "from": r.start_node.id,
                    "to": r.end_node.id,
                    "label": r.type
                })

        return {
            "nodes": list(nodes.values()),
            "edges": edges
        }
'''