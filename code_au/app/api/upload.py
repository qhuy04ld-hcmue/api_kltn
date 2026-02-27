from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from app.services import (
    minio_service,
    postgres_service,
    mongo_service,
    neo4j_service
)

router = APIRouter()


@router.post("/")
async def upload(
    file: UploadFile = File(...),
    class_number: int = Form(...),
    subject_code: str = Form(...),
    topic_order: int = Form(...),
    lesson_order: int = Form(...)
):
    try:
        # =============================
        # 1️⃣ Chuẩn hóa ID
        # =============================

        class_code = f"C{class_number}"
        subject_code = subject_code.upper()

        subject_id = f"{class_code}-{subject_code}"
        topic_id = f"{subject_id}-T{str(topic_order).zfill(2)}"
        lesson_id = f"{topic_id}-L{str(lesson_order).zfill(2)}"

        # =============================
        # 2️⃣ Postgres
        # =============================

        if not postgres_service.lesson_exists(lesson_id):
            postgres_service.upsert_class(class_code, f"Lớp {class_number}")
            postgres_service.upsert_subject(class_code, subject_code, subject_code)
            postgres_service.upsert_topic(subject_id, topic_order, f"Chủ đề {topic_order}")
            postgres_service.upsert_lesson(topic_id, lesson_order, f"Bài {lesson_order}", "")

            neo4j_service.sync_graph(
                class_code,
                subject_code,
                topic_order,
                lesson_order
            )

        # =============================
        # 3️⃣ Mongo structure sync
        # =============================

        mongo_service.sync_class(class_code, f"Lớp {class_number}")
        mongo_service.sync_subject(subject_id, class_code, subject_code)
        mongo_service.sync_topic(topic_id, subject_id, topic_order)
        mongo_service.sync_lesson_structure(lesson_id, topic_id, lesson_order)

        # =============================
        # 4️⃣ Upload MinIO
        # =============================

        file_info = minio_service.upload_file(
            file,
            class_code,
            subject_code,
            topic_order,
            lesson_order
        )

        # =============================
        # 5️⃣ Lưu file Mongo
        # =============================

        mongo_service.add_file_to_lesson(
            lesson_id,
            {
                "file_name": file.filename,
                "file_url": file_info["url"],
                "bucket": file_info["bucket"],
                "class": class_number,
                "subject": subject_code,
                "topic": topic_order,
                "lesson": lesson_order
            }
        )

        return {
            "status": "success",
            "lesson_id": lesson_id,
            "bucket": file_info["bucket"],
            "file_url": file_info["url"]
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
