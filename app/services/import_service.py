import zipfile
import os
import shutil
import pandas as pd
import tempfile
from app.services.minio_service import MinioService
from app.services.postgres_service import PostgresService
from app.services.mongo_service import MongoService
from app.services.neo4j_service import Neo4jService


class ImportService:

    async def process_zip(self, zip_file, db):

        temp_dir = tempfile.mkdtemp()

        # Save zip
        zip_path = os.path.join(temp_dir, zip_file.filename)
        with open(zip_path, "wb") as f:
            f.write(await zip_file.read())

        # Extract
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(temp_dir)

        # Find metadata
        metadata_path = os.path.join(temp_dir, "metadata.xlsx")
        files_dir = os.path.join(temp_dir, "files")

        df = pd.read_excel(metadata_path)

        minio = MinioService()
        pg = PostgresService()
        mongo = MongoService()
        neo = Neo4jService()

        for _, row in df.iterrows():

            class_code = row["class_code"]
            subject_code = row["subject_code"]
            topic_order = row["topic_order"]
            lesson_order = row["lesson_order"]
            lesson_name = row["lesson_name"]
            file_name = row["file_name"]
            bucket = row["file_type"]

            file_path = os.path.join(files_dir, file_name)

            if not os.path.exists(file_path):
                continue

            # UPSERT POSTGRES
            pg.upsert_class(db, class_code, f"Lớp {class_code[1:]}")
            pg.upsert_subject(db, class_code, subject_code, subject_code)

            subject_id = f"{class_code}-{subject_code}"
            topic_id = f"{subject_id}-T{str(topic_order).zfill(2)}"
            lesson_id = f"{topic_id}-L{str(lesson_order).zfill(2)}"

            pg.upsert_topic(db, subject_id, topic_order, f"Chủ đề {topic_order}")
            pg.upsert_lesson(db, topic_id, lesson_order, lesson_name, None)

            # Upload MinIO
            with open(file_path, "rb") as f:
                minio.client.put_object(
                    bucket,
                    f"{class_code}/{subject_code}/{file_name}",
                    f,
                    os.path.getsize(file_path)
                )

            # Sync Neo4j
            neo.sync_lesson_graph({
                "class_id": class_code,
                "class_name": f"Lớp {class_code[1:]}",
                "subject_id": subject_id,
                "subject_name": subject_code,
                "topic_id": topic_id,
                "topic_name": f"Chủ đề {topic_order}",
                "lesson_id": lesson_id,
                "lesson_name": lesson_name
            })

            mongo.upsert_lesson_metadata(lesson_id, {
                "file_name": file_name,
                "bucket": bucket
            })

        shutil.rmtree(temp_dir)

        return {"status": "import completed"}
