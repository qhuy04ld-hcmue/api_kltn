from fastapi import APIRouter, UploadFile, File, HTTPException
import zipfile
import pandas as pd
import os
import shutil
from datetime import datetime

from app.services import (
    minio_service,
    postgres_service,
    mongo_service,
    neo4j_service
)

router = APIRouter()


REQUIRED_COLUMNS = [
    "class",
    "subject",
    "topic",
    "topic_name",
    "lesson",
    "lesson_name",
    "file_name"
]


@router.post("/")
async def import_zip(file: UploadFile = File(...)):

    temp_dir = "temp_import"

    try:
        # =============================
        # 1️⃣ Chuẩn bị thư mục
        # =============================

        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)

        os.makedirs(temp_dir, exist_ok=True)

        zip_path = os.path.join(temp_dir, "import.zip")

        with open(zip_path, "wb") as f:
            f.write(await file.read())

        # =============================
        # 2️⃣ Giải nén
        # =============================

        with zipfile.ZipFile(zip_path, "r") as zip_ref:
            zip_ref.extractall(temp_dir)

        excel_path = os.path.join(temp_dir, "structure.xlsx")

        if not os.path.exists(excel_path):
            raise Exception("Không tìm thấy file structure.xlsx")

        df = pd.read_excel(excel_path)

        # =============================
        # 3️⃣ Validate cột
        # =============================

        for col in REQUIRED_COLUMNS:
            if col not in df.columns:
                raise Exception(f"Thiếu cột: {col}")

        # =============================
        # 4️⃣ Import từng dòng
        # =============================

        for index, row in df.iterrows():

            try:
                class_number = int(row["class"])
                subject_code = str(row["subject"]).upper()
                topic_order = int(row["topic"])
                topic_name = str(row["topic_name"])
                lesson_order = int(row["lesson"])
                lesson_name = str(row["lesson_name"])
                file_name = str(row["file_name"])

                if not file_name or file_name == "nan":
                    continue

                # =============================
                # Sinh ID
                # =============================

                class_code = f"C{class_number}"
                subject_id = f"{class_code}-{subject_code}"
                topic_id = f"{subject_id}-T{str(topic_order).zfill(2)}"
                lesson_id = f"{topic_id}-L{str(lesson_order).zfill(2)}"

                # =============================
                # Postgres
                # =============================

                if not postgres_service.lesson_exists(lesson_id):
                    postgres_service.upsert_class(class_code, f"Lớp {class_number}")
                    postgres_service.upsert_subject(class_code, subject_code, subject_code)
                    postgres_service.upsert_topic(subject_id, topic_order, topic_name)
                    postgres_service.upsert_lesson(topic_id, lesson_order, lesson_name, "")

                    neo4j_service.sync_graph(
                        class_code,
                        subject_code,
                        topic_order,
                        lesson_order
                    )

                # =============================
                # Mongo structure
                # =============================

                mongo_service.sync_class(class_code, f"Lớp {class_number}")
                mongo_service.sync_subject(subject_id, class_code, subject_code)
                mongo_service.sync_topic(topic_id, subject_id, topic_order)
                mongo_service.sync_lesson_structure(lesson_id, topic_id, lesson_order)

                # =============================
                # Upload file
                # =============================

                file_path = os.path.join(temp_dir, "files", file_name)

                if not os.path.exists(file_path):
                    raise Exception(f"Không tìm thấy file: {file_name}")

                file_info = minio_service.upload_file_from_path(
                    file_path,
                    file_name,
                    class_code,
                    subject_code,
                    topic_order,
                    lesson_order
                )

                # =============================
                # Mongo file metadata
                # =============================

                mongo_service.add_file_to_lesson(
                    lesson_id,
                    {
                        "file_name": file_name,
                        "file_url": file_info["url"],
                        "bucket": file_info["bucket"],
                        "class": class_number,
                        "subject": subject_code,
                        "topic": topic_order,
                        "lesson": lesson_order
                    }
                )

            except Exception as row_error:
                print(f"Lỗi tại dòng {index+2}: {row_error}")

        return {"status": "Import completed"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    finally:
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)
