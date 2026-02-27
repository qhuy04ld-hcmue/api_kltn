from fastapi import APIRouter, HTTPException
from app.config import BUCKETS
from app.services.postgres_service import get_tables, get_table_data
from app.services.mongo_service import get_collections, get_collection_data
from app.services.minio_service import client
from app.services.neo4j_service import get_graph

router = APIRouter()

# ================= POSTGRES =================

@router.get("/postgres")
def postgres_tables():
    return get_tables()


@router.get("/postgres/{table_name}")
def postgres_table(table_name: str):
    return get_table_data(table_name)


# ================= MONGO =================

@router.get("/mongo")
def mongo_collections():
    return get_collections()


@router.get("/mongo/{collection}")
def mongo_collection(collection: str):
    return get_collection_data(collection)


# ================= MINIO =================

@router.get("/buckets")
def list_buckets():
    return BUCKETS


@router.get("/bucket/{bucket_name}")
def list_bucket(bucket_name: str):

    if bucket_name not in BUCKETS:
        raise HTTPException(status_code=400, detail="Invalid bucket")

    if not client.bucket_exists(bucket_name):
        raise HTTPException(status_code=404, detail="Bucket not found")

    objects = client.list_objects(bucket_name, recursive=True)

    files = []
    for obj in objects:
        files.append({
            "name": obj.object_name,
            "size": obj.size
        })

    return files


# ================= NEO4J =================

@router.get("/neo4j")
def neo4j_graph():
    return get_graph()



from fastapi.responses import StreamingResponse
from urllib.parse import unquote
import mimetypes

@router.get("/view/{bucket}/{path:path}")
def view_file(bucket: str, path: str):

    path = unquote(path)

    if bucket not in BUCKETS:
        raise HTTPException(status_code=400, detail="Invalid bucket")

    if not client.bucket_exists(bucket):
        raise HTTPException(status_code=404, detail="Bucket not found")

    try:
        response = client.get_object(bucket, path)
    except Exception:
        raise HTTPException(status_code=404, detail="File not found")

    mime_type, _ = mimetypes.guess_type(path)
    if not mime_type:
        mime_type = "application/octet-stream"

    return StreamingResponse(response, media_type=mime_type)

@router.delete("/bucket/{bucket_name}/{path:path}")
def delete_file(bucket_name: str, path: str):

    if not client.bucket_exists(bucket_name):
        raise HTTPException(status_code=404, detail="Bucket not found")

    client.remove_object(bucket_name, path)

    return {"message": "File deleted"}


'''
@router.get("/{bucket}/{object_name:path}")
async def get_file(bucket: str, object_name: str):

    if bucket not in BUCKETS:
        raise HTTPException(status_code=404, detail="Bucket not found")

    try:
        response = client.get_object(bucket, object_name)

        return StreamingResponse(
            response,
            media_type="application/octet-stream"
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
'''