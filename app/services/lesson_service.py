from app.services import (
    postgres_service,
    mongo_service,
    neo4j_service,
    minio_service
)


def upsert_lesson(
    class_number,
    subject_code,
    topic_order,
    lesson_order,
    lesson_name,
    description="",
    file=None,
    file_path=None
):

    class_code = f"C{class_number}"
    subject_code = subject_code.upper()

    subject_id = f"{class_code}-{subject_code}"
    topic_id = f"{subject_id}-T{str(topic_order).zfill(2)}"
    lesson_id = f"{topic_id}-L{str(lesson_order).zfill(2)}"

    exists = postgres_service.lesson_exists(lesson_id)

    # =========================
    # CREATE FLOW
    # =========================
    if not exists:
        postgres_service.upsert_class(class_code, f"Lớp {class_number}")
        postgres_service.upsert_subject(class_code, subject_code, subject_code)
        postgres_service.upsert_topic(subject_id, topic_order, f"Chủ đề {topic_order}")
        postgres_service.upsert_lesson(topic_id, lesson_order, lesson_name, description)

        mongo_service.sync_class(class_code, f"Lớp {class_number}")
        mongo_service.sync_subject(subject_id, class_code, subject_code)
        mongo_service.sync_topic(topic_id, subject_id, topic_order)
        mongo_service.sync_lesson_structure(lesson_id, topic_id, lesson_order)

        neo4j_service.sync_graph(
            class_code,
            subject_code,
            topic_order,
            lesson_order
        )

    # =========================
    # UPDATE FLOW
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
    # FILE HANDLING
    # =========================
    file_info = None

    if file:
        file_info = minio_service.upload_file(
            file,
            class_code,
            subject_code,
            topic_order,
            lesson_order
        )

    elif file_path:
        file_info = minio_service.upload_file_from_path(
            file_path,
            file_path.split("/")[-1],
            class_code,
            subject_code,
            topic_order,
            lesson_order
        )

    if file_info:
        mongo_service.add_file_to_lesson(
            lesson_id,
            {
                "file_name": file_info.get("file_name", ""),
                "file_url": file_info["url"],
                "bucket": file_info["bucket"],
                "class": class_number,
                "subject": subject_code,
                "topic": topic_order,
                "lesson": lesson_order
            }
        )

    return lesson_id
