from minio import Minio
from app.config import *
from io import BytesIO

client = Minio(
    MINIO_ENDPOINT,
    access_key=MINIO_ACCESS_KEY,
    secret_key=MINIO_SECRET_KEY,
    secure=MINIO_SECURE
)


def detect_bucket(filename: str):
    ext = filename.split(".")[-1].lower()

    if ext in ["pdf", "docx", "pptx", "xlsx"]:
        return "document"
    elif ext in ["mp4", "avi", "mov"]:
        return "video"
    elif ext in ["jpg", "jpeg", "png"]:
        return "image"
    else:
        return "document"


def upload_file(file, class_code, subject_code, topic_order, lesson_order):
    bucket = detect_bucket(file.filename)

    topic_code = f"T{str(topic_order).zfill(2)}"
    lesson_code = f"L{str(lesson_order).zfill(2)}"

    object_path = f"{class_code}/{subject_code}/{topic_code}/{lesson_code}/"

    # 🔥 Giữ nguyên tên file
    object_name = object_path + file.filename

    file_bytes = file.file.read()
    file_stream = BytesIO(file_bytes)

    client.put_object(
        bucket_name=bucket,
        object_name=object_name,
        data=file_stream,
        length=len(file_bytes),
        content_type=file.content_type
    )

    url = f"http://{MINIO_ENDPOINT}/{bucket}/{object_name}"

    return {
        "bucket": bucket,
        "file_id": file.filename,
        "object_name": object_name,
        "url": url
    }
def upload_file_from_path(file_path, file_name,
                          class_code, subject_code,
                          topic_order, lesson_order):

    bucket = detect_bucket(file_name)

    topic_code = f"T{str(topic_order).zfill(2)}"
    lesson_code = f"L{str(lesson_order).zfill(2)}"

    object_path = f"{class_code}/{subject_code}/{topic_code}/{lesson_code}/"
    object_name = object_path + file_name

    with open(file_path, "rb") as f:
        from io import BytesIO
        data = f.read()
        stream = BytesIO(data)

        client.put_object(
            bucket_name=bucket,
            object_name=object_name,
            data=stream,
            length=len(data)
        )

    url = f"http://{MINIO_ENDPOINT}/{bucket}/{object_name}"

    return {
        "bucket": bucket,
        "url": url
    }
