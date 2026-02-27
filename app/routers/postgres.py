from fastapi import APIRouter, Body
from app.database.postgres import get_conn
from app.services.sync_service import sync_to_mongo, sync_to_neo4j

router = APIRouter(prefix="/postgres")


@router.get("/tables")
def list_tables():
    conn = get_conn()
    cur = conn.cursor()

    cur.execute("""
        SELECT table_name
        FROM information_schema.tables
        WHERE table_schema='public'
    """)

    tables = [r[0] for r in cur.fetchall()]
    conn.close()
    return tables


@router.get("/data/{table}")
def get_data(table: str):
    conn = get_conn()
    cur = conn.cursor()

    cur.execute(f"SELECT * FROM {table} WHERE is_deleted=false LIMIT 200")
    rows = cur.fetchall()
    columns = [desc[0] for desc in cur.description]

    conn.close()

    return {
        "columns": columns,
        "rows": rows
    }


@router.post("/insert/{table}")
def insert_row(table: str, data: dict = Body(...)):
    conn = get_conn()
    cur = conn.cursor()

    keys = data.keys()
    values = data.values()

    query = f"""
        INSERT INTO {table} ({','.join(keys)})
        VALUES ({','.join(['%s']*len(keys))})
    """

    cur.execute(query, tuple(values))
    conn.commit()
    conn.close()

    sync_to_mongo(table, data)
    sync_to_neo4j(table.capitalize(), data)

    return {"status": "inserted"}


@router.put("/update/{table}")
def update_row(table: str, data: dict = Body(...)):
    conn = get_conn()
    cur = conn.cursor()

    row_id = data["id"]
    updates = {k: v for k, v in data.items() if k != "id"}

    query = f"""
        UPDATE {table}
        SET {','.join([f"{k}=%s" for k in updates])}
        WHERE id=%s
    """

    cur.execute(query, (*updates.values(), row_id))
    conn.commit()
    conn.close()

    sync_to_mongo(table, data)
    sync_to_neo4j(table.capitalize(), data)

    return {"status": "updated"}


@router.put("/soft_delete/{table}/{id}")
def soft_delete(table: str, id: str):
    conn = get_conn()
    cur = conn.cursor()

    cur.execute(
        f"UPDATE {table} SET is_deleted=true WHERE id=%s",
        (id,)
    )

    conn.commit()
    conn.close()

    return {"status": "deleted"}
