from fastapi import APIRouter, UploadFile, File
from app.database.minio_client import client

router = APIRouter(prefix="/minio")

BUCKETS = ["video", "document", "image"]


@router.get("/buckets")
def list_buckets():
    return BUCKETS


@router.get("/objects/{bucket}")
def list_objects(bucket: str):
    objects = client.list_objects(bucket, recursive=True)
    return [obj.object_name for obj in objects]


@router.post("/upload/{bucket}")
def upload(bucket: str, file: UploadFile = File(...)):
    client.put_object(
        bucket,
        file.filename,
        file.file,
        length=-1,
        part_size=10*1024*1024
    )
    return {"status": "uploaded"}
