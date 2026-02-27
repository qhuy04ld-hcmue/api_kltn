from fastapi import APIRouter, UploadFile, File, Form, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.services.minio_service import MinioService
from app.services.postgres_service import PostgresService
from app.services.mongo_service import MongoService
from app.services.neo4j_service import Neo4jService

router = APIRouter(prefix="/api/upload", tags=["Upload"])

@router.post("/")
async def upload_file(
    class_code: str = Form(...),
    class_name: str = Form(...),
    subject_code: str = Form(...),
    subject_name: str = Form(...),
    topic_order: int = Form(...),
    topic_name: str = Form(...),
    lesson_order: int = Form(...),
    lesson_name: str = Form(...),
    description: str = Form(None),
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    minio = MinioService()
    pg = PostgresService()
    mongo = MongoService()
    neo = Neo4jService()

    # 1️⃣ Determine bucket
    if file.content_type.startswith("video"):
        bucket = "video"
    elif file.content_type.startswith("image"):
        bucket = "image"
    else:
        bucket = "document"

    folder = f"{class_code.lower()}/{subject_code.lower()}"

    file_info = minio.upload_file(file, bucket, folder)

    # 2️⃣ Upsert Postgres
    pg.upsert_class(db, class_code, class_name)
    pg.upsert_subject(db, class_code, subject_code, subject_name)

    subject_id = f"{class_code}-{subject_code}"
    topic_id = f"{subject_id}-T{str(topic_order).zfill(2)}"
    lesson_id = f"{topic_id}-L{str(lesson_order).zfill(2)}"

    pg.upsert_topic(db, subject_id, topic_order, topic_name)
    pg.upsert_lesson(db, topic_id, lesson_order, lesson_name, description)

    # 3️⃣ Sync Neo4j
    neo.sync_lesson_graph({
        "class_id": class_code,
        "class_name": class_name,
        "subject_id": subject_id,
        "subject_name": subject_name,
        "topic_id": topic_id,
        "topic_name": topic_name,
        "lesson_id": lesson_id,
        "lesson_name": lesson_name
    })

    # 4️⃣ Mongo metadata
    mongo.upsert_lesson_metadata(lesson_id, file_info)

    return {"status": "success", "lesson_id": lesson_id}
