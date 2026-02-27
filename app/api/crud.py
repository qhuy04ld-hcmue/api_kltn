from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from app.services import (
    postgres_service,
    mongo_service,
    neo4j_service,
    minio_service
)

router = APIRouter()


# =========================================================
# INSERT / UPSERT LESSON
# =========================================================
@router.post("/insert")
async def insert_lesson(
    file: UploadFile = File(None),  # optional
    class_number: int = Form(...),
    subject_code: str = Form(...),
    topic_order: int = Form(...),
    lesson_order: int = Form(...),
    lesson_name: str = Form(...),
    description: str = Form("")
):
    try:

        # =========================
        # 1️⃣ VALIDATE INPUT
        # =========================

        if not subject_code.strip():
            raise HTTPException(status_code=400, detail="Subject code required")

        class_code = f"C{class_number}"
        subject_code = subject_code.upper().strip()

        subject_id = f"{class_code}-{subject_code}"
        topic_id = f"{subject_id}-T{str(topic_order).zfill(2)}"
        lesson_id = f"{topic_id}-L{str(lesson_order).zfill(2)}"

        lesson_exists = postgres_service.lesson_exists(lesson_id)

        # =========================
        # 2️⃣ CREATE IF NOT EXISTS
        # =========================
        if not lesson_exists:

            postgres_service.upsert_class(
                class_code,
                f"Lớp {class_number}"
            )

            postgres_service.upsert_subject(
                class_code,
                subject_code,
                subject_code
            )

            postgres_service.upsert_topic(
                subject_id,
                topic_order,
                f"Chủ đề {topic_order}"
            )

            postgres_service.upsert_lesson(
                topic_id,
                lesson_order,
                lesson_name,
                description
            )

            # Mongo structure
            mongo_service.sync_class(class_code, f"Lớp {class_number}")
            mongo_service.sync_subject(subject_id, class_code, subject_code)
            mongo_service.sync_topic(topic_id, subject_id, topic_order)
            mongo_service.sync_lesson_structure(
                lesson_id,
                topic_id,
                lesson_order
            )

            # Neo4j
            neo4j_service.sync_graph(
                class_code,
                subject_code,
                topic_order,
                lesson_order
            )

        # =========================
        # 3️⃣ UPDATE IF EXISTS
        # =========================
        else:
            postgres_service.update_lesson_info(
                lesson_id,
                lesson_name,
                description
            )

            mongo_service.update_lesson_metadata(
                lesson_id,
                lesson_name
            )

        # =========================
        # 4️⃣ FILE HANDLING (OPTIONAL)
        # =========================
        if file and file.filename:

            file_info = minio_service.upload_file(
                file,
                class_code,
                subject_code,
                topic_order,
                lesson_order
            )

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
            "action": "created" if not lesson_exists else "updated"
        }

    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# =========================================================
# UPDATE LESSON
# =========================================================
@router.put("/update/{lesson_id}")
async def update_lesson(
    lesson_id: str,
    lesson_name: str = Form(None),
    description: str = Form(None),
    file: UploadFile = File(None)
):
    try:

        if not postgres_service.lesson_exists(lesson_id):
            raise HTTPException(status_code=404, detail="Lesson not found")

        # =========================
        # 1️⃣ UPDATE METADATA
        # =========================
        postgres_service.update_lesson_info(
            lesson_id,
            lesson_name,
            description
        )

        mongo_service.update_lesson_metadata(
            lesson_id,
            lesson_name
        )

        # =========================
        # 2️⃣ OPTIONAL FILE UPDATE
        # =========================
        if file and file.filename:

            parts = lesson_id.split("-")

            if len(parts) != 4:
                raise HTTPException(
                    status_code=400,
                    detail="Invalid lesson_id format"
                )

            class_code = parts[0]
            subject_code = parts[1]
            topic_order = int(parts[2][1:])
            lesson_order = int(parts[3][1:])

            file_info = minio_service.upload_file(
                file,
                class_code,
                subject_code,
                topic_order,
                lesson_order
            )

            mongo_service.add_file_to_lesson(
                lesson_id,
                {
                    "file_name": file.filename,
                    "file_url": file_info["url"],
                    "bucket": file_info["bucket"],
                    "class": class_code,
                    "subject": subject_code,
                    "topic": topic_order,
                    "lesson": lesson_order
                }
            )

        return {"status": "updated", "lesson_id": lesson_id}

    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# =========================================================
# SOFT DELETE LESSON
# =========================================================
@router.delete("/soft-delete/{lesson_id}")
async def soft_delete_lesson(lesson_id: str):
    try:

        if not postgres_service.lesson_exists(lesson_id):
            raise HTTPException(status_code=404, detail="Lesson not found")

        postgres_service.soft_delete_lesson(lesson_id)
        mongo_service.soft_delete_lesson(lesson_id)
        neo4j_service.soft_delete_lesson(lesson_id)

        return {
            "status": "soft_deleted",
            "lesson_id": lesson_id
        }

    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



'''
from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from app.services import (
    postgres_service,
    mongo_service,
    neo4j_service,
    minio_service
)

router = APIRouter()
@router.post("/insert")
async def insert_lesson(
    file: UploadFile = File(...),
    class_number: int = Form(...),
    subject_code: str = Form(...),
    topic_order: int = Form(...),
    lesson_order: int = Form(...),
    lesson_name: str = Form(...),
    description: str = Form("")
):
    try:
        # =========================
        # 1️⃣ TẠO MÃ DỮ LIỆU (Postgres trước)
        # =========================

        class_code = f"C{class_number}"
        subject_code = subject_code.upper()
        subject_id = f"{class_code}-{subject_code}"
        topic_id = f"{subject_id}-T{str(topic_order).zfill(2)}"

        postgres_service.upsert_class(class_code, f"Lớp {class_number}")
        postgres_service.upsert_subject(class_code, subject_code, subject_code)
        postgres_service.upsert_topic(subject_id, topic_order, f"Chủ đề {topic_order}")
        postgres_service.upsert_lesson(topic_id, lesson_order, lesson_name, description)

        lesson_id = f"{topic_id}-L{str(lesson_order).zfill(2)}"

        # =========================
        # 2️⃣ OBJECT STORAGE
        # =========================

        file_info = minio_service.upload_file(
            file, class_code, subject_code,
            topic_order, lesson_order
        )

        # =========================
        # 3️⃣ MongoDB (Data Source)
        # =========================

        mongo_service.sync_class(class_code, f"Lớp {class_number}")
        mongo_service.sync_subject(subject_id, class_code, subject_code)
        mongo_service.sync_topic(topic_id, subject_id, topic_order)
        mongo_service.sync_lesson_structure(lesson_id, topic_id, lesson_order)

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

        # =========================
        # 4️⃣ Neo4j (Struct DB)
        # =========================

        neo4j_service.sync_graph(
            class_code,
            subject_code,
            topic_order,
            lesson_order
        )

        # =========================
        # 5️⃣ Middleware / DWH Hook
        # =========================

        # middleware_service.publish_event("lesson_inserted", lesson_id)

        return {"status": "Inserted", "lesson_id": lesson_id}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/update/{lesson_id}")
async def update_lesson(
    lesson_id: str,
    lesson_name: str = Form(None),
    description: str = Form(None),
    file: UploadFile = File(None)
):
    try:
        if not postgres_service.lesson_exists(lesson_id):
            raise HTTPException(status_code=404, detail="Lesson not found")

        # 1️⃣ Postgres
        postgres_service.update_lesson_info(
            lesson_id,
            lesson_name,
            description
        )

        mongo_service.update_lesson_metadata(
            lesson_id,
            lesson_name
        )

        # 2️⃣ File update
        if file:
            parts = lesson_id.split("-")
            class_code = parts[0]
            subject_code = parts[1]
            topic_order = int(parts[2][1:])
            lesson_order = int(parts[3][1:])

            file_info = minio_service.upload_file(
                file,
                class_code,
                subject_code,
                topic_order,
                lesson_order
            )

            mongo_service.add_file_to_lesson(
                lesson_id,
                {
                    "file_name": file.filename,
                    "file_url": file_info["url"],
                    "bucket": file_info["bucket"],
                    "class": class_code,
                    "subject": subject_code,
                    "topic": topic_order,
                    "lesson": lesson_order
                }
            )

        # middleware_service.publish_event("lesson_updated", lesson_id)

        return {"status": "Updated"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/soft-delete/{lesson_id}")
async def soft_delete_lesson(lesson_id: str):
    try:
        postgres_service.soft_delete_lesson(lesson_id)
        mongo_service.soft_delete_lesson(lesson_id)
        neo4j_service.soft_delete_lesson(lesson_id)

        # middleware_service.publish_event("lesson_deleted", lesson_id)

        return {"status": "Soft Deleted"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
'''











'''
def create_or_update(data: dict):

    upsert_structure(
        data["class_name"],
        data["subject_name"],
        data["topic_name"],
        data["lesson_title"]
    )

    sync_graph(
        data["class_name"],
        data["subject_name"],
        data["topic_name"],
        data["lesson_title"]
    )

    return {"message": "Saved"}

@router.delete("/lesson/{lesson_title}")
def soft_delete(lesson_title: str):

    mongo_db.documents.update_many(
        {"lesson_title": lesson_title},
        {"$set": {"is_deleted": True}}
    )

    return {"message": "Soft deleted"}
'''