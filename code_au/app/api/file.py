from fastapi import APIRouter, HTTPException
from app.services.minio_service import client
from datetime import timedelta
from urllib.parse import unquote
import mimetypes

router = APIRouter()

@router.get("/presigned")
async def get_presigned_url(bucket: str, object_name: str):

    try:
        object_name = unquote(object_name)

        # đoán content type
        content_type, _ = mimetypes.guess_type(object_name)
        if not content_type:
            content_type = "application/octet-stream"

        url = client.presigned_get_object(
            bucket_name=bucket,
            object_name=object_name,
            expires=timedelta(hours=1),
            response_headers={
                "response-content-disposition": "inline",
                "response-content-type": content_type
            }
        )

        return {"url": url}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))






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